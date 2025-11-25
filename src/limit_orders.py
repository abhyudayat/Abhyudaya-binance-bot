# project_root/src/limit_orders.py

from src.binance_client import client
from src.logger import log, log_error

def execute_limit(state):
    """
    Executes a LIMIT order on Binance Futures.
    state contains:
        - symbol
        - side
        - quantity
        - price
        - time_in_force (optional, default GTC)
    """

    symbol = state["symbol"]
    side = state["side"]
    quantity = state["quantity"]
    price = state["price"]
    tif = state.get("time_in_force", "GTC")   # default: Good-Till-Cancelled

    if client is None:
        log_error("Binance client not initialized", state)
        raise RuntimeError("Binance client not available. Set API keys first.")

    try:
        log("Placing LIMIT order", state)

        response = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce=tif
        )

        log("LIMIT order executed", {"response": response})
        return response

    except Exception as e:
        log_error("Limit order failed", {"error": str(e), "state": state})
        raise e
