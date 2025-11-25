# project_root/src/logger.py

import datetime
import json

LOG_PATH = "project_root/bot.log"

def log(message, data=None, level="INFO"):
    """
    Append structured logs to bot.log
    message: Short description
    data: dict of details (optional)
    level: INFO / ERROR / WARNING
    """

    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "data": data
    }

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "
")


def log_error(message, data=None):
    """Helper for logging errors."""
    log(message, data, level="ERROR")


def log_order(order_type, state):
    """
    Logs any order execution with state details.
    """
    log(f"Executed {order_type} order", data=state, level="INFO")
