# /src/limit_orders.py

from src.logger import log_info, log_error, log_api_request, log_api_response, log_order

def execute_limit_order(client, symbol, side, quantity, price, time_in_force="GTC"):
    """
    Execute a LIMIT order on Binance Futures Testnet.
    """

    if client is None:
        log_error("Binance client not initialized")
        raise RuntimeError("Binance client not available")

    request_payload = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": time_in_force
    }

    try:
        log_api_request("Placing LIMIT order", request_payload)

        response = client.futures_create_order(**request_payload)

        log_api_response("LIMIT order executed", response)
        log_order("LIMIT", response)

        return response

    except Exception as e:
        log_error("Limit order failed", {"error": str(e)})
        raise
