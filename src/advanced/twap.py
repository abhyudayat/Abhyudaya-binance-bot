# project_root/src/advanced/twap.py

import time
from src.binance_client import client
from src.logger import log, log_error


def execute_twap(state):
    """
    Executes a TWAP strategy: splits a large order into smaller MARKET orders
    executed evenly over a time period.

    Expected fields:
        - symbol
        - side
        - quantity        : total amount
        - twap_intervals  : into how many chunks (default = 5)
        - twap_delay      : seconds between chunks (default = 60)
    """

    symbol = state["symbol"]
    side = state["side"]
    total_qty = state["quantity"]

    # Defaults if not provided by the LLM or user
    intervals = int(state.get("twap_intervals", 5))   # number of chunks
    delay = float(state.get("twap_delay", 60))        # time between chunks in seconds

    if intervals <= 0:
        raise ValueError("twap_intervals must be > 0")

    if client is None:
        log_error("Binance client not initialized", state)
        raise RuntimeError("Binance client not available. Set API keys first.")

    # Calculate per-order chunk
    qty_per_order = total_qty / intervals

    log("Starting TWAP execution", {
        "symbol": symbol,
        "side": side,
        "total_qty": total_qty,
        "intervals": intervals,
        "delay": delay,
        "chunk_qty": qty_per_order
    })

    responses = []

    try:
        for i in range(intervals):
            log(f"TWAP chunk {i+1}/{intervals}: submitting order", {"qty": qty_per_order})

            # Place MARKET order for each chunk
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=qty_per_order
            )

            responses.append(order)

            # Wait before next order unless it's the last one
            if i < intervals - 1:
                time.sleep(delay)

        log("TWAP strategy complete", {"responses": responses})
        return responses

    except Exception as e:
        log_error("TWAP execution failed", {"error": str(e), "state": state})
        raise e
