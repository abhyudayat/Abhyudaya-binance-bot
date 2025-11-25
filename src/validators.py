# project_root/src/validators.py

import math
from typing import Optional, Dict, Any
from src.logger import log_error, log
import os

# Try to import global client if available (binance_client sets `client` or None)
try:
    from src.binance_client import client as binance_client
except Exception:
    binance_client = None


def _to_float(x, name="value"):
    try:
        return float(x)
    except Exception:
        raise ValueError(f"Invalid {name}: must be numeric")


def _normalize_side(side: str) -> str:
    if not side:
        raise ValueError("Missing side (BUY or SELL)")
    s = side.strip().upper()
    if s not in ("BUY", "SELL"):
        raise ValueError("side must be 'BUY' or 'SELL'")
    return s


def _normalize_symbol(symbol: str) -> str:
    if not symbol:
        raise ValueError("Missing symbol")
    return symbol.strip().upper()


def _get_exchange_symbol_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    If binance_client is available, fetch symbol info from exchange to validate
    quantity/price filters (e.g., minQty, stepSize, tickSize). Returns None if not available.
    """
    if not binance_client:
        return None
    try:
        info = binance_client.futures_exchange_info()
        for s in info.get("symbols", []):
            if s.get("symbol", "").upper() == symbol:
                return s
    except Exception as e:
        log("Failed to fetch exchange info", data={"error": str(e)}, level="WARNING")
    return None


def _apply_lot_size_filters(qty: float, filters: Dict[str, Any]) -> float:
    """
    Adjust (round down) quantity to conform with stepSize and minQty.
    """
    if not filters:
        return qty
    step_size = None
    min_qty = None
    for f in filters:
        if f.get("filterType") == "LOT_SIZE":
            step_size = float(f.get("stepSize", 0))
            min_qty = float(f.get("minQty", 0))
            break

    if min_qty is not None and qty < min_qty:
        raise ValueError(f"Quantity {qty} is below exchange minQty {min_qty}")

    if step_size and step_size > 0:
        # Round down to the nearest step_size increment
        precision = int(round(-math.log10(step_size))) if step_size < 1 else 0
        qty = math.floor(qty / step_size) * step_size
        qty = round(qty, precision)
    return qty


def _apply_price_filters(price: float, filters: Dict[str, Any]) -> float:
    """
    Adjust (round) price to conform to tickSize if available.
    """
    if not filters:
        return price
    tick_size = None
    for f in filters:
        if f.get("filterType") == "PRICE_FILTER":
            tick_size = float(f.get("tickSize", 0))
            min_price = float(f.get("minPrice", 0))
            if price < min_price:
                raise ValueError(f"Price {price} is below exchange minPrice {min_price}")
            break

    if tick_size and tick_size > 0:
        precision = int(round(-math.log10(tick_size))) if tick_size < 1 else 0
        price = round(round(price / tick_size) * tick_size, precision)
    return price


def _required_fields_for_order_type(order_type: str):
    order_type = (order_type or "").strip().lower()
    mapping = {
        "market": ["symbol", "side", "quantity"],
        "limit": ["symbol", "side", "quantity", "price"],
        "stop_limit": ["symbol", "side", "quantity", "stop_price", "price"],
        "oco": ["symbol", "side", "quantity", "price", "stop_price"],  # simplified
        "twap": ["symbol", "side", "quantity"],  # twap has params but base required
        "grid": ["symbol", "side", "quantity"],  # grid specifics handled by strategy
    }
    return mapping.get(order_type, ["symbol", "side", "quantity"])


def validate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and normalizes the incoming `state` dictionary.
    Returns a cleaned dict with numeric types for "quantity", "price", "stop_price" etc.
    Raises ValueError if validation fails.
    """
    if not isinstance(state, dict):
        raise ValueError("State must be a dictionary")

    cleaned = {}

    # Basic normalization
    order_type = state.get("order_type") or state.get("type") or "market"
    order_type = order_type.strip().lower()
    cleaned["order_type"] = order_type

    # Required fields check
    required = _required_fields_for_order_type(order_type)
    missing = [f for f in required if f not in state and f not in state.keys()]
    if missing:
        # For clarity, check presence in original state (different keys like 'price' vs 'limit_price' sometimes used)
        # We'll attempt to map common alternate keys
        alt_map = {
            "stop_price": ["stopPrice", "stop"],
            "price": ["limit_price", "limitPrice", "limit"],
            "quantity": ["qty", "amount", "quantity"],
            "symbol": ["pair"],
            "side": ["action"]
        }
        for req in required:
            if req in state:
                continue
            found = False
            for alt in alt_map.get(req, []):
                if alt in state:
                    state[req] = state[alt]
                    found = True
                    break
            if found:
                continue
            if req not in state:
                raise ValueError(f"Missing required field for {order_type}: {req}")

    # Symbol and side
    symbol = _normalize_symbol(state.get("symbol") or state.get("pair"))
    cleaned["symbol"] = symbol

    side = _normalize_side(state.get("side") or state.get("action"))
    cleaned["side"] = side

    # Exchange info (optional)
    exch_info = _get_exchange_symbol_info(symbol)
    filters = exch_info.get("filters") if exch_info else None

    # Quantity
    if "quantity" in state or "qty" in state or "amount" in state:
        raw_qty = state.get("quantity") or state.get("qty") or state.get("amount")
        qty = _to_float(raw_qty, "quantity")
        if qty <= 0:
            raise ValueError("quantity must be > 0")
        # Apply lot size rules if exchange info present
        try:
            qty = _apply_lot_size_filters(qty, filters)
        except Exception as e:
            log_error("Quantity validation failed", data={"error": str(e), "state": state})
            raise
        cleaned["quantity"] = qty
    else:
        raise ValueError("Missing quantity")

    # Price (limit)
    if "price" in state or "limit_price" in state:
        raw_p = state.get("price") or state.get("limit_price") or state.get("limitPrice")
        price = _to_float(raw_p, "price")
        if price <= 0:
            raise ValueError("price must be > 0")
        try:
            price = _apply_price_filters(price, filters)
        except Exception as e:
            log_error("Price validation failed", data={"error": str(e), "state": state})
            raise
        cleaned["price"] = price

    # Stop price
    if "stop_price" in state or "stopPrice" in state or "stop" in state:
        raw_sp = state.get("stop_price") or state.get("stopPrice") or state.get("stop")
        stop_price = _to_float(raw_sp, "stop_price")
        if stop_price <= 0:
            raise ValueError("stop_price must be > 0")
        try:
            stop_price = _apply_price_filters(stop_price, filters)
        except Exception as e:
            log_error("Stop price validation failed", data={"error": str(e), "state": state})
            raise
        cleaned["stop_price"] = stop_price

    # Optional: time-in-force, reduceOnly, clientOrderId, etc.
    if "time_in_force" in state:
        cleaned["time_in_force"] = state["time_in_force"]

    if "reduce_only" in state:
        cleaned["reduce_only"] = bool(state["reduce_only"])

    # Pass through any extra params the strategies may need
    for key, val in state.items():
        if key not in cleaned:
            cleaned[key] = val

    log("Validation successful", data={"symbol": symbol, "order_type": order_type, "qty": cleaned.get("quantity")})
    return cleaned
