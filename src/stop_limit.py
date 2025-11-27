# /src/stop_limit.py

from src.logger import (
    log_info,
    log_error,
    log_api_request,
    log_api_response,
    log_order,
)

def execute_stop_limit_order(client, symbol, side, quantity, stop_price, limit_price):

    if client is None:
        log_error("Binance client not initialized")
        raise RuntimeError("Binance client not available")

    request_payload = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "quantity": quantity,
        "price": limit_price,   # LIMIT price
        "stopPrice": stop_price,
        "timeInForce": "GTC"
    }

    try:
        log_api_request("Placing STOP-LIMIT order", request_payload)

        response = client.futures_create_order(**request_payload)

        log_api_response("STOP-LIMIT order executed", response)
        log_order("STOP-LIMIT", response)

        return response

    except Exception as e:
        log_error("Stop-limit order failed", {"error": str(e)})
        raise
