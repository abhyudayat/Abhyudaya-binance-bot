# src/logger.py

import json
from datetime import datetime

LOG_FILE = "bot.log"   # correct relative path


def _write_log(entry: dict):
    """
    Write a single log entry in JSON format.
    """
    try:
        entry["timestamp"] = datetime.utcnow().isoformat()
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print("Failed to write log:", e)


def log_info(message: str, data: dict = None):
    _write_log({
        "type": "INFO",
        "message": message,
        "data": data or {}
    })


def log_error(message: str, data: dict = None):
    _write_log({
        "type": "ERROR",
        "message": message,
        "data": data or {}
    })


def log_api_request(endpoint: str, payload: dict):
    """
    Log outgoing API requests.
    """
    _write_log({
        "type": "API_REQUEST",
        "endpoint": endpoint,
        "payload": payload
    })


def log_api_response(endpoint: str, response: dict):
    """
    Log incoming API responses.
    """
    _write_log({
        "type": "API_RESPONSE",
        "endpoint": endpoint,
        "response": response
    })


def log_order(order_type: str, details: dict):
    """
    Log order execution events.
    """
    _write_log({
        "type": "ORDER_EXECUTION",
        "order_type": order_type,
        "details": details
    })
