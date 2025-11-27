# /src/market_orders.py

from src.logger import (
    log_info,
    log_error,
    log_api_request,
    log_api_response,
    log_order
)

def execute_market_order(client, symbol, side, quantity):
    order_payload = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity
    }

    try:
        log_info("Placing MARKET order", order_payload)
        log_api_request("futures_create_order", order_payload)

        response = client.futures_create_order(**order_payload)

        log_api_response("futures_create_order", response)
        log_order("MARKET", {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "response": response
        })

        return response

    except Exception as e:
        error_info = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "error": str(e)
        }

        log_error("Market order FAILED", error_info)
        raise
