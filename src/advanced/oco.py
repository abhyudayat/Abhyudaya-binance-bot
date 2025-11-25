# project_root/src/advanced/oco.py

from src.binance_client import client
from src.logger import log, log_error
import uuid


def execute_oco(state):
    """
    Implements OCO manually for Binance Futures.
    Creates:
      1) Take-profit LIMIT order
      2) Stop-market (or stop-limit) order
    If one fills, Binance cancels the other using the same order group.
    """

    symbol = state["symbol"]
    side = state["side"]
    qty = state["quantity"]

    take_profit = state["price"]        # TP price
    stop_price = state["stop_price"]    # SL trigger price

    if client is None:
        log_error("Binance client not initialized", state)
        raise RuntimeError("Binance client not available. Set API keys first.")

    # Generate a unique OCO group ID
    oco_group_id = str(uuid.uuid4())[:12]

    try:
        log("Placing OCO order", state)

        # Determine opposite side for exits
        exit_side = "SELL" if side == "BUY" else "BUY"

        # 1 TAKE PROFIT LIMIT ORDER
        tp_order = client.futures_create_order(
            symbol=symbol,
            side=exit_side,
            type="TAKE_PROFIT",
            price=take_profit,
            stopPrice=take_profit,
            quantity=qty,
            timeInForce="GTC",
            newClientOrderId=f"TP-{oco_group_id}"
        )

        # 2 STOP-LOSS ORDER
        sl_order = client.futures_create_order(
            symbol=symbol,
            side=exit_side,
            type="STOP_MARKET",
            stopPrice=stop_price,
            quantity=qty,
            newClientOrderId=f"SL-{oco_group_id}"
        )

        response = {
            "take_profit_order": tp_order,
            "stop_loss_order": sl_order,
            "group_id": oco_group_id
        }

        log("OCO order submitted", response)
        return response

    except Exception as e:
        log_error("OCO order failed", {"error": str(e), "state": state})
        raise e
