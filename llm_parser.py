import json
import requests
import os
from src.logger import log_error


class LLMParser:
    """
    Uses HuggingFace Chat Completions API (remote inference).
    Works with supported chat models like Mistral-Nemo.
    """

    def __init__(self, model="mistralai/Mistral-Nemo-Instruct-2407"):
        self.model = model
        self.api_key = os.getenv("HF_API_KEY")
        if not self.api_key:
            raise RuntimeError("HF_API_KEY not set.")

        self.url = "https://api-inference.huggingface.co/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

#     def parse(self, text: str):

#         system_prompt = """
# You are a trading command parser.
# Convert the user's command into a STRICT JSON object.

# REQUIRED FIELDS:
# - order_type
# - symbol
# - side
# - quantity

# OPTIONAL FIELDS:
# - price
# - stop_price

# RULES:
# - Return ONLY JSON.
# - No explanations.
# - No extra text.
# """

#         user_prompt = f"Command: {text}\nReturn ONLY JSON."

#         payload = {
#             "model": self.model,
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ],
#             "temperature": 0,
#             "max_tokens": 150
#         }

#         try:
#             response = requests.post(self.url, headers=self.headers, json=payload)
#             data = response.json()

#             # HF chat API → choices[0].message.content
#             content = data["choices"][0]["message"]["content"]

#             # Extract JSON
#             start = content.find("{")
#             end = content.rfind("}") + 1
#             json_str = content[start:end]

#             return json.loads(json_str)

#         except Exception as e:
#             log_error("LLM parsing failed", {"error": str(e), "input": text})
#             raise RuntimeError("Failed to parse trading command.") from e
    def parse(self, text: str):
        """
        TEMP: return raw LLM output (no JSON parsing)
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": text}
            ],
            "temperature": 0.2,
            "max_tokens": 100
        }

        response = requests.post(self.url, headers=self.headers, json=payload)

        data = response.json()

        # Return raw model output for debugging
        return data
