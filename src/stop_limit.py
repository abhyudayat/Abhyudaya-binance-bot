# project_root/src/stop_limit.py

from src.binance_client import client
from src.logger import log, log_error

def execute_stop_limit(state):
    """
    Executes a STOP-LIMIT order on Binance Futures.
    state contains:
        - symbol
        - side
        - quantity
        - stop_price
        - price
    """

    symbol = state["symbol"]
    side = state["side"]
    quantity = state["quantity"]
    stop_price = state["stop_price"]
    limit_price = state["price"]   # state["price"] is the LIMIT price

    if client is None:
        log_error("Binance client not initialized", state)
        raise RuntimeError("Binance client not available. Set API keys first.")

    try:
        log("Placing STOP-LIMIT order", state)

        response = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="STOP",
            quantity=quantity,
            price=limit_price,
            stopPrice=stop_price,
            timeInForce="GTC"
        )

        log("STOP-LIMIT order executed", {"response": response})
        return response

    except Exception as e:
        log_error("Stop-limit order failed", {"error": str(e), "state": state})
        raise e
