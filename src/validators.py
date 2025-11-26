# src/validators.py

import math
from typing import Optional, Dict, Any
from src.logger import log_info, log_error


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


def _required_fields_for_order_type(order_type: str):
    order_type = (order_type or "").strip().lower()
    mapping = {
        "market": ["symbol", "side", "quantity"],
        "limit": ["symbol", "side", "quantity", "price"],
        "stop_limit": ["symbol", "side", "quantity", "stop_price", "price"],
        "oco": ["symbol", "side", "quantity", "price", "stop_price"],
        "twap": ["symbol", "side", "quantity"],
        "grid": ["symbol", "side", "quantity"],
    }
    return mapping.get(order_type, ["symbol", "side", "quantity"])


def validate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize user input state.
    Converts values to correct types and ensures required fields exist.
    """

    if not isinstance(state, dict):
        raise ValueError("State must be a dictionary")

    cleaned = {}

    # Determine order type
    order_type = state.get("order_type") or state.get("type") or "market"
    order_type = order_type.strip().lower()
    cleaned["order_type"] = order_type

    # Required fields
    required = _required_fields_for_order_type(order_type)

    for field in required:
        if field not in state:
            raise ValueError(f"Missing required field for {order_type}: {field}")

    # Symbol
    symbol = _normalize_symbol(state["symbol"])
    cleaned["symbol"] = symbol

    # Side
    side = _normalize_side(state["side"])
    cleaned["side"] = side

    # Quantity
    qty = _to_float(state["quantity"], "quantity")
    if qty <= 0:
        raise ValueError("quantity must be > 0")
    cleaned["quantity"] = qty

    # Price (optional)
    if "price" in state:
        price = _to_float(state["price"], "price")
        if price <= 0:
            raise ValueError("price must be > 0")
        cleaned["price"] = price

    # Stop price (optional)
    if "stop_price" in state:
        stop = _to_float(state["stop_price"], "stop_price")
        if stop <= 0:
            raise ValueError("stop_price must be > 0")
        cleaned["stop_price"] = stop

    # Pass through other fields
    for k, v in state.items():
        if k not in cleaned:
            cleaned[k] = v

    log_info("Validation successful", {
        "symbol": symbol,
        "order_type": order_type,
        "quantity": cleaned.get("quantity"),
    })

    return cleaned
