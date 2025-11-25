# project_root/src/binance_client.py

import os
from binance.client import Client

def get_client(testnet=True):

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError(
            "API keys not found. Set BINANCE_API_KEY and BINANCE_API_SECRET "
            "as environment variables before running the bot."
        )
    client = Client(api_key, api_secret, testnet=testnet)
    
    if testnet:
        client.FUTURES_URL = "https://testnet.binancefuture.com/fapi/"

    return client
