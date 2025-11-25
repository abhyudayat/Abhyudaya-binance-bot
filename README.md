# Abhyudaya-binance-bot
Guided CLI binance bot which validates the input commmand and executes different type of orders on binance.

## API Setup (Required)

Before running the bot, set your Binance Futures API keys as environment variables.

### Linux / Mac:
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"

### Windows PowerShell:
setx BINANCE_API_KEY "your_key"
setx BINANCE_API_SECRET "your_secret"

### Windows CMD:
set BINANCE_API_KEY=your_key
set BINANCE_API_SECRET=your_secret

### Verify:
echo $BINANCE_API_KEY        # Linux/Mac
echo %BINANCE_API_KEY%       # Windows
