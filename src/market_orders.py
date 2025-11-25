# project_root/src/market_orders.py

from src.binance_client import client
from src.logger import log, log_error

def execute_market(state):
    """
    Executes a market order on Binance Futures.
    state contains:
        - symbol
        - side (BUY/SELL)
        - quantity
    """
    symbol = state["symbol"]
    side = state["side"]
    quantity = state["quantity"]

    # Safety check: if client is not available
    if client is None:
        log_error("Binance client not initialized", state)
        raise RuntimeError("Binance client not available. Set API keys before running the bot.")

    try:
        log("Placing MARKET order", state)

        response = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )

        log("MARKET order executed", {"response": response})
        return response

    except Exception as e:
        log_error("Market order failed", {"error": str(e), "state": state})
        raise e
