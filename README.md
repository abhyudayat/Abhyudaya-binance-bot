# Abhyudaya-binance-bot
Guided CLI binance bot which validates the input commmand and executes different type of orders using Binance api.
## Binance Futures AI Trading Bot (CLI binance trading bot using Python, LangGraph and HuggingFace)

This repository contains a modular, AI-powered Binance Futures trading bot built using:

- Python 3.x  
- HuggingFace Transformers (for natural-language order parsing)  
- LangGraph (workflow routing engine)  
- Binance Futures API  
- Advanced trading strategies (OCO, Stop-Limit, TWAP)  

The bot supports **natural language commands**, validates them, and executes orders safely on Binance USDT-M Futures.

---

## Project Structure
```
project_root/
│
├── bot.py # Main CLI entry point
├── graph.py # LangGraph workflow
├── llm_parser.py # HuggingFace LLM command parser
│
├── /src/
│ ├── binance_client.py # Binance client loader (env-based)
│ ├── validators.py # Input validation layer
│ ├── logger.py # Logging module
│ ├── market_orders.py # MARKET order logic
│ ├── limit_orders.py # LIMIT order logic
│ ├── stop_limit.py # STOP-LIMIT order logic
│ ├── /advanced/
│ │ ├── oco.py # OCO (Take-profit + Stop-loss)
│ │ ├── twap.py # TWAP strategy
│ │ ├── grid_strategy.py # Optional grid trading strategy
│
├── bot.log # Structured JSON logs
├── report.pdf # Submission report (architecture, screenshots, examples)
└── README.md # This documentation
```
## API Setup (Required)

Before running the bot, set your Binance Futures API keys as environment variables.

**Linux / Mac:**  
export BINANCE_API_KEY="your_key"  
export BINANCE_API_SECRET="your_secret"  

**Windows PowerShell:**
setx BINANCE_API_KEY "your_key"  
setx BINANCE_API_SECRET "your_secret"  

**Windows CMD:**  
set BINANCE_API_KEY=your_key  
set BINANCE_API_SECRET=your_secret  

**Verify:**  
echo $BINANCE_API_KEY        # Linux/Mac  
echo %BINANCE_API_KEY%       # Windows  

## Installation

Clone the repository:  

git clone https://github.com/abhyudayat/Abhyudaya-binance-bot.git  
cd Abhyudaya-binance-bot  
  

Install dependencies:  
pip install -r requirements.txt  

  
### Required Dependencies
The bot uses the following Python libraries:

- `transformers` — HuggingFace model for natural-language parsing  
- `torch` — Required backend for Transformers  
- `accelerate` — Efficient HuggingFace model loading  
- `langgraph` — Routing workflow engine  
- `python-binance` — Binance USDT-M Futures API client  
- `requests` — Network utilities  
- `tqdm` — Progress bars  
- `numpy` — Numeric utilities  

These are automatically installed via `pip install -r requirements.txt`.

## Running the Bot

The bot accepts **free-form natural language commands**.  
  
**MARKET ORDER**  
python bot.py "buy btcusdt 0.01"  
  
**LIMIT ORDER**   
python bot.py "place a limit buy on btcusdt at 86000 quantity 0.01"  
  
**STOP-LIMIT ORDER**  
python bot.py "buy 0.01 btc if price hits 86000 with limit 85950"  
  
**OCO ORDER (Take-Profit + Stop-Loss)**  
python bot.py "set oco sell btcusdt 0.01 take profit 88000 stop 84000"  
  
**TWAP ORDER**  
python bot.py "twap buy btcusdt 1 over 10 intervals"  
  
---

## How the Bot Works (Architecture)

### **1. LLM Parser**
The HuggingFace llm model converts user input into structured JSON:  
"buy btc 0.01 if price hits 86000"  
  
becomes:
```
json
{
  "order_type": "stop_limit",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.01,
  "stop_price": 86000,
  "price": 85950
}
```

### **2. Validation Layer**

The validator ensures:  
- Correct symbol format
- Side is BUY/SELL
- Quantity is numeric & positive
- Price rules follow Binance filters
- Mandatory fields exist for each order type
    
Invalid commands cause the bot to print:  
- error reason
- suggested corrected CLI command
    
### **3. LangGraph Workflow**
  
The router node directs the order to  
the respective Order Module:-
- market	market_orders.py
- limit	limit_orders.py
- stop_limit	stop_limit.py
- oco	advanced/oco.py
- twap	advanced/twap.py

### **4. Execution Layer**
Each module sends a well-formed order to:  
POST /fapi/v1/order  
or grouped logic (TP/SL for OCO, repeated orders for TWAP).  

### **5. Logging**
Every order and error is logged to bot.log as structured JSON:
```
{
  "timestamp": "2025-11-25T14:12:01",
  "level": "INFO",
  "message": "LIMIT order executed",
  "data": {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "price": 86000,
    "quantity": 0.01
  }
}
```
