# /src/advanced/oco.py

import uuid
from src.logger import (
    log_info,
    log_error,
    log_api_request,
    log_api_response,
    log_order,
)

def execute_oco_order(client, symbol, side, quantity, take_profit_price, stop_price):
    """
    Executes a manual OCO (One-Cancels-the-Other) order on Binance Futures Testnet.

    Creates:
        1) TAKE-PROFIT limit order
        2) STOP-MARKET order
    """

    if client is None:
        log_error("Binance client not initialized")
        raise RuntimeError("Binance client not available")

    # Unique OCO group ID
    oco_group_id = str(uuid.uuid4())[:12]

    exit_side = "SELL" if side == "BUY" else "BUY"

    try:
        # ------------------------------
        # TAKE-PROFIT ORDER
        # ------------------------------
        tp_payload = {
            "symbol": symbol,
            "side": exit_side,
            "type": "TAKE_PROFIT",
            "price": take_profit_price,
            "stopPrice": take_profit_price,
            "quantity": quantity,
            "timeInForce": "GTC",
            "newClientOrderId": f"TP-{oco_group_id}"
        }

        log_api_request("Placing OCO TAKE-PROFIT order", tp_payload)
        tp_response = client.futures_create_order(**tp_payload)
        log_api_response("TP order response", tp_response)
        log_order("OCO-TAKE-PROFIT", tp_response)

        # ------------------------------
        # STOP-LOSS ORDER
        # ------------------------------
        sl_payload = {
            "symbol": symbol,
            "side": exit_side,
            "type": "STOP_MARKET",
            "stopPrice": stop_price,
            "quantity": quantity,
            "newClientOrderId": f"SL-{oco_group_id}"
        }

        log_api_request("Placing OCO STOP-MARKET order", sl_payload)
        sl_response = client.futures_create_order(**sl_payload)
        log_api_response("SL order response", sl_response)
        log_order("OCO-STOP", sl_response)

        return {
            "group_id": oco_group_id,
            "take_profit_order": tp_response,
            "stop_loss_order": sl_response,
        }

    except Exception as e:
        log_error("OCO order failed", {"error": str(e)})
        raise
