# IOL Broker Integration - Documentation

## Overview

Complete integration with IOL Invertir Online broker API for automated trading.

## Features

### IOLBrokerClient
- **Authentication**: Secure OAuth2 authentication
- **Market Data**: Real-time prices, OHLCV data
- **Account Info**: Balance, positions, order history
- **Order Execution**: Buy/sell orders with market/limit types
- **Order Management**: Status tracking, cancellation

### IOLTradingBot
- **Automated Analysis**: Technical indicators + signals
- **Order Validation**: Pre-execution checks
- **Risk Management**: Automatic stop loss/take profit
- **Position Monitoring**: Real-time position tracking
- **Telegram Alerts**: Real-time notifications
- **Semi-Automatic Mode**: Manual confirmation before execution

## Setup

### 1. Get IOL API Credentials

1. Go to [IOL Invertir Online](https://www.invertironline.com/)
2. Login to your account
3. Navigate to API settings
4. Generate API credentials (username/password)

### 2. Configure Environment

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```bash
IOL_USERNAME=your_username_here
IOL_PASSWORD=your_password_here
```

Optional - Configure Telegram:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ENABLE_TELEGRAM_ALERTS=true
```

### 3. Install Dependencies

```bash
pip install requests python-dotenv
```

## Usage

### Basic Example - IOL Client

```python
from src.brokers.iol_client import IOLBrokerClient

# Initialize and authenticate
client = IOLBrokerClient()
client.authenticate()

# Get account balance
balance = client.get_account_balance()
print(f"Available: ${balance['saldo_disponible']:,.2f}")

# Get market price
price_data = client.get_market_price('GGAL')
print(f"GGAL: ${price_data['ultimoPrecio']:.2f}")

# Get positions
positions = client.get_positions()
for pos in positions:
    print(f"{pos['titulo']['simbolo']}: {pos['cantidad']} shares")
```

### Trading Bot Example

```python
from src.brokers.iol_client import IOLBrokerClient
from src.brokers.iol_trading_bot import IOLTradingBot
import pandas as pd

# Setup
client = IOLBrokerClient()
client.authenticate()

bot = IOLTradingBot(
    iol_client=client,
    auto_execute=False,  # Requires manual confirmation
    telegram_enabled=True
)

# Analyze symbol
historical_data = pd.DataFrame(...)  # Your OHLCV data
analysis = bot.analyze_symbol('GGAL', historical_data)

print(f"Recommendation: {analysis['recommendation']}")
print(f"Signals: {analysis['signals']}")
print(f"Stop Loss: ${analysis['stop_loss']:.2f}")
print(f"Take Profit: ${analysis['take_profit']:.2f}")

# Execute trade (with confirmation required)
if analysis['recommendation'] == 'COMPRA':
    success, message = bot.execute_trade(
        symbol='GGAL',
        signal='COMPRA',
        quantity=10,
        stop_loss=analysis['stop_loss'],
        take_profit=analysis['take_profit']
    )
    print(message)

# Monitor positions
bot.monitor_positions()  # Checks SL/TP continuously

# Get portfolio summary
summary = bot.get_portfolio_summary()
print(f"Total value: ${summary['total_value']:,.2f}")
```

## Complete Workflow

### 1. Market Analysis
```python
# Analyze multiple symbols
symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA']
analyses = {}

for symbol in symbols:
    df = get_historical_data(symbol)  # Your data source
    analyses[symbol] = bot.analyze_symbol(symbol, df)

# Find best opportunities
buy_signals = [
    (symbol, data) for symbol, data in analyses.items()
    if data['recommendation'] == 'COMPRA'
]
```

### 2. Order Execution
```python
# Execute on best signal
for symbol, analysis in buy_signals[:3]:  # Top 3
    success, msg = bot.execute_trade(
        symbol=symbol,
        signal='COMPRA',
        quantity=calculate_position_size(symbol),
        stop_loss=analysis['stop_loss'],
        take_profit=analysis['take_profit']
    )
    print(f"{symbol}: {msg}")
```

### 3. Position Management
```python
# Continuous monitoring loop
import time

while True:
    bot.monitor_positions()  # Check SL/TP
    time.sleep(60)  # Check every minute
```

## Safety Features

### Order Validation
- Balance check before order
- Position size limits
- Market hours validation
- Price deviation detection
- Exposure limits per asset

### Risk Management
- Automatic stop loss (ATR-based)
- Automatic take profit
- Position monitoring
- Maximum drawdown protection

### Operational Safety
- **Semi-automatic mode by default**: Requires manual confirmation
- **Comprehensive logging**: All actions logged
- **Error handling**: Graceful degradation
- **Telegram alerts**: Real-time notifications

## Demo Script

Run the complete demo:
```bash
cd "fiancial de 0/bot2.0"
python demo_iol_broker.py
```

This demonstrates:
1. IOL client authentication
2. Account balance retrieval
3. Position querying
4. Market data fetching
5. Technical analysis
6. Trade execution (simulation)
7. Portfolio summary

## API Methods

### IOLBrokerClient

| Method | Description | Returns |
|--------|-------------|---------|
| `authenticate()` | Login to IOL API | bool |
| `get_account_balance()` | Get account balance | dict |
| `get_positions()` | Get current positions | list |
| `get_market_price(symbol)` | Get real-time price | dict |
| `place_order(...)` | Execute order | tuple(bool, dict) |
| `get_order_status(order_id)` | Check order status | dict |
| `get_order_history(days)` | Get order history | list |
| `cancel_order(order_id)` | Cancel pending order | bool |

### IOLTradingBot

| Method | Description | Returns |
|--------|-------------|---------|
| `analyze_symbol(symbol, df)` | Analyze with indicators | dict |
| `execute_trade(...)` | Execute validated trade | tuple(bool, str) |
| `monitor_positions()` | Check SL/TP | None |
| `get_portfolio_summary()` | Get portfolio info | dict |

## Configuration Options

### Trading Bot

```python
bot = IOLTradingBot(
    iol_client=client,              # Authenticated IOL client
    auto_execute=False,             # Auto-execute without confirmation
    telegram_enabled=True           # Send Telegram alerts
)
```

### Environment Variables

- `IOL_USERNAME`: IOL API username
- `IOL_PASSWORD`: IOL API password
- `TELEGRAM_BOT_TOKEN`: Telegram bot token (optional)
- `TELEGRAM_CHAT_ID`: Telegram chat ID (optional)
- `AUTO_EXECUTE`: Enable automatic execution (default: false)
- `ENABLE_TELEGRAM_ALERTS`: Enable Telegram notifications (default: true)

## Integration with Existing System

The IOL broker integration works seamlessly with all existing features:

✅ **16 Technical Indicators** → Used for signal generation  
✅ **Order Validator** → Pre-execution validation  
✅ **Alert System** → Real-time notifications  
✅ **Risk Analytics** → Risk assessment  
✅ **Portfolio Optimizer** → Portfolio allocation  
✅ **Backtesting Engine** → Strategy validation  
✅ **Pattern Recognition** → Entry/exit signals  
✅ **Multi-Timeframe Analysis** → Signal confirmation

## Production Deployment

### Recommended Setup

1. **Start with Paper Trading**:
   - Set `auto_execute=False`
   - Monitor signals manually
   - Validate system behavior

2. **Enable Semi-Automatic Mode**:
   - Review each signal
   - Confirm manually before execution
   - Monitor risk metrics

3. **Full Automation** (Advanced):
   - Set `auto_execute=True`
   - Implement additional safeguards
   - Monitor 24/7

### Monitoring

```python
# Setup monitoring
import schedule

def check_positions():
    bot.monitor_positions()
    summary = bot.get_portfolio_summary()
    log_portfolio_state(summary)

# Run every minute
schedule.every(1).minutes.do(check_positions)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## Troubleshooting

### Authentication Issues
- Verify IOL credentials
- Check API endpoint availability
- Review token expiration

### Order Execution Failures
- Check account balance
- Verify market hours
- Review order validation results

### Connection Issues
- Check internet connectivity
- Verify IOL API status
- Review firewall settings

## Security Best Practices

1. **Never commit credentials**: Use `.env` file (in `.gitignore`)
2. **Use environment variables**: Don't hardcode credentials
3. **Enable 2FA on IOL**: Additional account security
4. **Monitor regularly**: Review transactions daily
5. **Set position limits**: Limit maximum exposure
6. **Test thoroughly**: Use paper trading first

## Support

For issues or questions:
1. Check the demo script: `demo_iol_broker.py`
2. Review existing tests
3. Check IOL API documentation
4. Review system logs

## Next Steps

1. ✅ Configure credentials in `.env`
2. ✅ Run demo script
3. ✅ Test with paper trading
4. ✅ Monitor positions
5. ✅ Enable gradual automation

---

**Status**: ✅ Production-ready  
**Version**: 1.0.0  
**Integration**: Complete with all Phase 1-5 features
