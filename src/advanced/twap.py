# project_root/src/advanced/twap.py

import time
from src.logger import (
    log_info,
    log_error,
    log_api_request,
    log_api_response,
    log_order,
)

def execute_twap_order(client, symbol, side, total_quantity, intervals=5, delay=60):
    """
    TWAP Strategy (Time-Weighted Average Price)
    Splits a large MARKET order into smaller chunks executed over time.
    """

    if client is None:
        log_error("Binance client not initialized")
        raise RuntimeError("Binance client not available")

    intervals = int(intervals)
    delay = float(delay)

    if intervals <= 0:
        raise ValueError("twap_intervals must be > 0")

    qty_per_order = total_quantity / intervals

    log_info("Starting TWAP execution", {
        "symbol": symbol,
        "side": side,
        "total_qty": total_quantity,
        "intervals": intervals,
        "delay": delay,
        "chunk_qty": qty_per_order
    })

    responses = []

    try:
        for i in range(intervals):

            request_payload = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": qty_per_order
            }

            log_api_request(f"TWAP chunk {i+1}/{intervals}", request_payload)
            order = client.futures_create_order(**request_payload)
            log_api_response("TWAP MARKET order executed", order)
            log_order("TWAP", order)

            responses.append(order)

            if i < intervals - 1:
                time.sleep(delay)

        return responses

    except Exception as e:
        log_error("TWAP execution failed", {"error": str(e)})
        raise
