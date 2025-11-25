

# project_root/bot.py

import sys
from llm_parser import LLMParser
from graph import build_bot_graph
from src.logger import log_error
from src.binance_client import get_client

parser_llm = LLMParser()
graph = build_bot_graph()

def suggest_correction(user_text, error_message):
    """
    Use LLM to suggest a corrected CLI command based on the error.
    """
    try:
        correction_prompt = f"""
You are an assistant that helps correct CLI trading commands.

The user typed:
"{user_text}"

The system error was:
"{error_message}"

Return ONLY a corrected CLI command in this format:
python bot.py "<corrected command>"

If you cannot correct it, return:
python bot.py "<help>"
"""
        suggestion = parser_llm.pipe(correction_prompt)[0]["generated_text"]
        return suggestion.strip()
    except Exception:
        return "python bot.py "help""


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("export BINANCE_API_KEY=xxx")
        print("export BINANCE_API_SECRET=yyy")
        print('python bot.py "your trading command"')
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])

    # Load API keys from environment variables
    try:
        client = get_client(testnet=True)
    except Exception as e:
        print(" API setup error:", str(e))
        sys.exit(1)

    # Inject client globally into modules
    import src.binance_client
    src.binance_client.client = client

    try:
        parsed = parser_llm.parse(user_text)
        result = graph.invoke(parsed)
        print("
 ORDER EXECUTION RESULT:")
        print(result)

    except Exception as e:
        error_message = str(e)
        log_error("Bot failed", {"error": error_message, "input": user_text})

        print("
 ERROR:", error_message)
        print("Trying to suggest a correction...")

        suggestion = suggest_correction(user_text, error_message)
        print(" Suggested CLI:")
        print(suggestion)
