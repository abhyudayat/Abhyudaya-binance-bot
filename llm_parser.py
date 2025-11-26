import json
import requests
import os
from src.logger import log_error

class LLMParser:
    """
    Uses HuggingFace Chat Completions API (router endpoint)
    with a supported chat model.
    """

    def __init__(self, model="meta-llama/Llama-3.2-1B-Instruct"):
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
You are a trading command parser for a Binance Futures bot.

Convert the user's message into a STRICT JSON object with keys:

REQUIRED:
- order_type         (market, limit, stop_limit, oco, twap)
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
"""


        user_prompt = f"Command: {text}\nReturn ONLY JSON."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "max_tokens": 200,
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

