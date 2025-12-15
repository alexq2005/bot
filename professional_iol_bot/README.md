# IOL Professional Trading Bot

**Version:** 1.0.0 (Clean Architecture)

A robust, transparent, and tested Algorithmic Trading Bot designed for the Argentine market (IOL). Unlike previous iterations, this bot prioritizes stability, verifyability, and honest technical analysis over "black box" promises.

## 🌟 Key Features

*   **Transparent Strategy**: Uses standard indicators (RSI, MACD, Bollinger Bands) via `pandas-ta`. No magic numbers.
*   **Robust Architecture**: Modular design separating Client, Strategy, and Database.
*   **Data Persistence**: Trades are saved to a local SQLite database (`trades.db`) to prevent data loss.
*   **Mock Mode**: Built-in simulation mode for safe testing without real money.
*   **Tested**: Includes a test suite (`pytest`) to ensure reliability.

## 🚀 Quick Start

### 1. Installation

```bash
cd professional_iol_bot
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file (optional, defaults provided):

```env
IOL_USERNAME=your_user
IOL_PASSWORD=your_password
TRADING_SYMBOL=GGAL
MOCK_MODE=True
```

### 3. Running the Bot

**Simulation Mode (Default):**
Uses fake data and simulates orders. Safe for testing.
```bash
# In .env: MOCK_MODE=True
python -m src.bot
```

**Live Trading Mode (REAL MONEY):**
Connects to IOL API and executes real orders.
1. Set `MOCK_MODE=False` in your `.env` file.
2. Ensure `IOL_USERNAME` and `IOL_PASSWORD` are correct.
3. Run the bot:
```bash
python -m src.bot
```
⚠️ **WARNING**: Live mode involves financial risk. The developers are not responsible for any losses incurred.

### 4. Running Tests

```bash
pytest tests/
```

## 🏗 Architecture

*   `src/bot.py`: Main orchestration loop.
*   `src/iol_client.py`: IOL API wrapper (with Mock support).
*   `src/strategy.py`: Technical Analysis logic.
*   `src/database.py`: SQLite persistence layer.
*   `tests/`: Unit and integration tests.

## ⚠️ Disclaimer

This software is for educational purposes. Trading involves risk. Always test in Mock Mode first.
