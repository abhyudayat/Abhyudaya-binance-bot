import json
import requests
import os
from src.logger import log_error

class LLMParser:
    """
    Uses HuggingFace Chat Completions API (router endpoint)
    with a supported chat model.
    """

    def __init__(self, model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"):
        self.model = model
        self.api_key = os.getenv("HF_API_KEY")
        if not self.api_key:
            raise RuntimeError("HF_API_KEY not set.")

        self.url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def parse(self, text: str):
        """
        Parse trading commands into STRICT JSON using a supported chat model.
        """

        system_prompt = """
You are a Trader who knows the trading keywords for a Binance Futures bot.
You have to parse the user input into a JSON.
Convert the user's message into a STRICT JSON object by:
1)  Extracting order type which could be only among th following:
    market, limit, stop_limit, oco or twap
2)  Extracting the coin symbol like BTCUSDT for bitcoin, etc
3)  Extracting the side i.e. SELL or BUY
4)  Extracting quantity like 0.1, 0.3, 3, 10, etc.
5)  Extracting price which would be an integer or real number like 3200, 1000.15, etc.
6)  EXtracting the stop price which would a integer linked to Stop price and mentioned after it in the user input.
    *(It cannot not be same a price)
7)  Extracting the no. of intervals of time unit mentioned for twap order duration.
8)  Extracting the time unit mentioned for the twap order (like )
REQUIRED:
- order_type         (Strictly: market, limit, stop_limit, oco or twap)
- symbol             (convert to UPPERCASE Binance format, e.g. btc→BTCUSDT)
- side               (BUY or SELL)
- quantity

OPTIONAL:
- price
- stop_price
- twap_intervals
- twap_delay

RULES:
- Always convert symbols to their Binance USDT futures pair (BTC→BTCUSDT, ETH→ETHUSDT, SOL→SOLUSDT, etc.)
- If user writes only base asset (e.g. btc), assume USDT pair.
- Only return valid JSON.
- No explanations, no text outside JSON.
Example:
$ python bot.py "sell 1 eth limit at 3200"
-order_type = limit       
- symbol    = ETHUSDT         BTCUSDT)
- side      = SELL
- quantity  = 1
- price     = 3200

$ python bot.py "twap buy btc amount 0.3"
- order_type = twap      
- symbol    = BTCUSDT        BTCUSDT)
- side      = BUY
- quantity  = 0.3

$ python bot.py "sell 0.5 eth oco for 2700 stop_price 3200"
- order type = oco
- symbol     = ETHUSDT
- side       = SELL
- Quantity   = 0.5
- Price      = 2700
- stop_price = 3200
"""


        user_prompt = f"Command: {text}\nReturn ONLY JSON."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 1000,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            data = response.json()

            content = data["choices"][0]["message"]["content"]

            # Extract JSON block
            start = content.find("{")
            end = content.rfind("}") + 1

            if start == -1 or end == -1:
                raise ValueError("No JSON detected in model output.")

            json_str = content[start:end]
            return json.loads(json_str)

        except Exception as e:
            log_error("LLM parsing failed", {"error": str(e), "input": text})
            raise RuntimeError("Failed to parse trading command.") from e

