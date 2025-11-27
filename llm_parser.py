# /llm_parser.py 
# Establishes the HuggingFace API connection and initializes a chat model
# Initializes prompt for command parsing
# Initializes prompt for command suggestion in case of error

import json
import requests
import os
from src.logger import log_error

class LLMParser:
    """
    Uses HuggingFace Chat Completions API (router endpoint)
    with a supported chat model.
    """

    def __init__(self, model="meta-llama/Llama-2-13b-chat-hf"):
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
You have to parse the user input CLI into a JSON.
JSON ouput keys for different type of orders are:
1) "market" (A market order is used to buy or sell at the current market price. It doesn't require a price parameter, only the quantity and side (buy/sell).)
{
  "order_type": ,
  "symbol": ,
  "side": ,
  "quantity": ,
}
2) "limit" (A limit order allows you to specify a price at which you want to buy or sell. You need to specify the price, along with the quantity and side.)
{
  "order_type": ,
  "symbol": ,
  "side": ,
  "quantity": ,
  "price": ,
}
3) "stop_limit" (A stop-limit order is an order to buy or sell once a specified stop price is reached. It also requires a price (limit price) and a stop_price (the trigger price).)
{
  "order_type": ,
  "symbol": ,
  "side": ,
  "quantity": ,
  "stop_price": ,
  "price": ,
}
4) "oco" (One Cancels Other, An OCO (One Cancels Other) order is used to place two orders simultaneously. If one of them is filled, the other is canceled automatically. It involves two orders: a take-profit (limit) order and a stop-loss (market) order.)
{
  "order_type": "oco",
  "symbol": "ETHUSDT",
  "side": "SELL",
  "quantity": 0.5,
  "price": 2700,
  "stop_price": 3200
}
5) "twap" (Time Weighted Average Price, A TWAP order splits a large order into smaller market orders that are executed at regular intervals over a specified period of time. It requires twap_intervals (the number of time periods) and twap_delay (the time between orders).)
{
  "order_type": "twap",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.5,
  "twap_intervals": 5,
  "twap_delay": 60
}

Look at the user input, brainstorm and logically assing the following: 
Required keys:
1)  "order_type" which will be only among th following (market,limit, stop_limit, oco or twap) nothing else.
2)  "symbol" will be the coin symbol used in binance future trade
3)  "side" i.e. SELL or BUY. extract the keyword "buy" or "sell" from the usertext. buy means side is BUY and sell means side is SELL.
4)  "quantity" which means the number of coins to buy or sell which acan be fractional.
5)  "price" which would the prices for LIMIT and STOP_LIMIT type orders. it will be an integer or real number. Do mention Price for limit.
6)  "stop_price" is used for Stop_limit orders and oco orders. it is linked to stop price in user text. You must extract side first from user input (buy or sell) and then(If the side is SELL then the "stop_price" must be lower than the "price" else if the side is BUY then "stop_price" must be higher than the "price".)
    *Interchange them as necessary (It cannot not be same a price)
7)  "twap_interval" the no. of intervals of time unit mentioned for twap order duration.
8)  "twap_delay" the time unit mentioned for the twap order


RULES:
- Always convert symbols to their Binance USDT futures pair (BTC→BTCUSDT, ETH→ETHUSDT, SOL→SOLUSDT, etc.)
- If user writes only base asset (e.g. btc), assume USDT pair.
- Only return valid JSON.
- No explanations, no text outside JSON.

Example:
$ python bot.py "buy 2 btc"
- order_type = market       
- symbol    = BTCUSDT
- side      = BUY
- quantity  = 2

$ python bot.py "sell 1 eth limit at 3200"
{'order_type': 'limit', 'symbol': 'ETHUSDT', 'side': 'SELL', 'quantity': 1, 'price': 3200}

$ python bot.py "twap buy btc amount 0.3"
{'order_type': 'twap', 'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.3}

$ python bot.py "sell 0.5 eth oco for 2700 stop_price 3200"
{'order_type': 'oco', 'symbol': 'ETHUSDT', 'side': 'SELL', 'quantity': 0.5, 'price': 2700, 'stop_price': 3200}

order can only be among: 'market', 'limit', 'stop_limit', 'oco, 'twap'
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


    def suggest_correction(self, user_text, error_message):
        """
        Use LLM to suggest a corrected CLI command based on the error and explain the issue.
        """
        # Provide context to the model for suggesting corrections and explaining the error.
        system_prompt = """
You are an assistant that helps correct CLI trading commands.
The user typed:
"{user_text}"
The system error was:
"{error_message}"

Your task is to:
1. Identify the possible mistake in the user's command.
2. Suggest a corrected CLI command that would work for the trading bot.
3. Provide an explanation of the error and how the correction fixes it.

Return only the corrected command and the explanation in this format:

Corrected command:
python bot.py "<corrected command>"

Explanation:
<error explanation here>
If you cannot correct it, return:
python bot.py "<help>"
Explanation:
Provide a detailed explanation of the issue.
"""

        user_prompt = f"Command: {user_text}\nError: {error_message}"

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
            return content

        except Exception as e:
            log_error("LLM suggestion failed", {"error": str(e), "input": user_text})
            return 'The command could not be parsed due to an error. Please check your input and try again.'

