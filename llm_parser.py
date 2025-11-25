# project_root/llm_parser.py

from transformers import pipeline
import json
from src.logger import log_error

class LLMParser:
    """
    Uses a HuggingFace model to convert natural language
    commands into structured JSON for the trading bot.
    """

    def __init__(self, model="HuggingFaceH4/zephyr-7b-beta"):
        try:
            self.pipe = pipeline(
                "text-generation",
                model=model,
                max_new_tokens=150
            )
        except Exception as e:
            print("Warning: Failed to load model:", e)
            self.pipe = None

    def parse(self, text: str):
        """
        Convert natural language into JSON fields:
        - order_type
        - symbol
        - side
        - quantity
        - price (optional)
        - stop_price (optional)
        """
        if self.pipe is None:
            raise RuntimeError("LLM pipeline not initialized.")

        prompt = f"""
Extract a structured JSON command for a Binance futures order.
Required keys:
- order_type
- symbol
- side
- quantity
Optional:
- price
- stop_price

Command: {text}

Return ONLY valid JSON:
"""
        try:
            result = self.pipe(prompt)[0]["generated_text"]
            # Take the JSON part
            json_str = result[result.find("{") : result.rfind("}") + 1]
            data = json.loads(json_str)
            return data

        except Exception as e:
            log_error("LLM parsing failed", {"error": str(e), "input": text})
            raise RuntimeError("Failed to parse trading command.") from e
