# project_root/bot.py

import sys
from llm_parser import LLMParser
from graph import build_bot_graph
from src.logger import log_error
from src.binance_client import get_client

parser_llm = LLMParser()
graph = build_bot_graph()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('python bot.py "your trading command"')
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])

    # Load API keys from environment variables
    try:
        client = get_client(testnet=True)
    except Exception as e:
        print(" API setup error:", str(e))
        sys.exit(1)

    try:
        parsed = parser_llm.parse(user_text)
        parsed['client']=client
        result = graph.invoke(parsed)
        print("\nORDER EXECUTION RESULT:")
        print(result)

    except Exception as e:
        error_message = str(e)
        log_error("Bot failed", {"error": error_message, "input": user_text})

        print("\nERROR:", error_message)
        print("Trying to suggest a correction...")

        suggestion = parser_llm.suggest_correction(user_text, error_message)
        print(suggestion)
