"""
Demo script for IOL Broker integration.

This script demonstrates how to use the IOL broker client and trading bot
to interact with the IOL Invertir Online API.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brokers.iol_client import IOLBrokerClient
from src.brokers.iol_trading_bot import IOLTradingBot


def generate_sample_data(symbol: str, days: int = 100) -> pd.DataFrame:
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate random walk price data
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, days)
    prices = 100 * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.02, days)),
        'low': prices * (1 + np.random.uniform(-0.02, 0, days)),
        'close': prices,
        'volume': np.random.randint(100000, 1000000, days)
    })
    
    df.set_index('date', inplace=True)
    return df


def demo_iol_client():
    """Demonstrate IOL client functionality."""
    print("=" * 80)
    print("IOL BROKER CLIENT DEMO")
    print("=" * 80)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    print("1. Initializing IOL client...")
    try:
        client = IOLBrokerClient()
        print("✅ Client initialized")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure to:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your IOL credentials")
        return
    
    print()
    
    # Authenticate
    print("2. Authenticating with IOL API...")
    if client.authenticate():
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return
    
    print()
    
    # Get account balance
    print("3. Getting account balance...")
    balance = client.get_account_balance()
    if balance:
        print(f"   💰 Available balance: ${balance.get('saldo_disponible', 0):,.2f}")
        print(f"   💼 Total balance: ${balance.get('saldo_total', 0):,.2f}")
    else:
        print("   ❌ Could not retrieve balance")
    
    print()
    
    # Get positions
    print("4. Getting current positions...")
    positions = client.get_positions()
    if positions:
        print(f"   📊 You have {len(positions)} active positions:")
        for pos in positions[:5]:  # Show first 5
            symbol = pos.get('titulo', {}).get('simbolo', 'N/A')
            qty = pos.get('cantidad', 0)
            price = pos.get('ultimoPrecio', 0)
            print(f"      • {symbol}: {qty} shares @ ${price:.2f}")
    else:
        print("   📊 No active positions")
    
    print()
    
    # Get market price
    print("5. Getting market price for GGAL...")
    price_data = client.get_market_price('GGAL')
    if price_data:
        print(f"   💵 Last price: ${price_data.get('ultimoPrecio', 0):.2f}")
        print(f"   📈 Change: {price_data.get('variacion', 0):.2f}%")
        print(f"   📊 Volume: {price_data.get('volumen', 0):,}")
    else:
        print("   ❌ Could not retrieve price")
    
    print()
    print("=" * 80)
    print("IOL CLIENT DEMO COMPLETE")
    print("=" * 80)


def demo_trading_bot():
    """Demonstrate trading bot functionality."""
    print()
    print("=" * 80)
    print("IOL TRADING BOT DEMO")
    print("=" * 80)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize IOL client
    print("1. Initializing IOL client and trading bot...")
    try:
        client = IOLBrokerClient()
        client.authenticate()
        
        # Create trading bot (with auto_execute=False for safety)
        bot = IOLTradingBot(
            iol_client=client,
            auto_execute=False,  # Requires manual confirmation
            telegram_enabled=os.getenv('ENABLE_TELEGRAM_ALERTS', 'false').lower() == 'true'
        )
        print("✅ Trading bot initialized")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print()
    
    # Analyze a symbol
    print("2. Analyzing GGAL with technical indicators...")
    sample_data = generate_sample_data('GGAL', days=100)
    
    analysis = bot.analyze_symbol('GGAL', sample_data)
    
    print(f"\n   📊 ANALYSIS RESULTS FOR {analysis['symbol']}:")
    print(f"   {'=' * 60}")
    print(f"   Recommendation: {analysis['recommendation']}")
    print()
    print("   Signals:")
    for signal_name, signal_value in analysis['signals'].items():
        emoji = "🟢" if signal_value == "COMPRA" else "🔴" if signal_value == "VENTA" else "🔵"
        print(f"      {emoji} {signal_name}: {signal_value}")
    
    print()
    print("   Key Indicators:")
    indicators = analysis['indicators']
    print(f"      RSI: {indicators.get('rsi', 0):.2f}")
    print(f"      MACD: {indicators.get('macd', 0):.4f}")
    print(f"      ADX: {indicators.get('adx', 0):.2f}")
    
    print()
    print("   Risk Management:")
    print(f"      Stop Loss: ${analysis.get('stop_loss', 0):.2f}")
    print(f"      Take Profit: ${analysis.get('take_profit', 0):.2f}")
    
    print()
    
    # Get portfolio summary
    print("3. Getting portfolio summary...")
    summary = bot.get_portfolio_summary()
    if summary:
        print(f"   💼 Total portfolio value: ${summary.get('total_value', 0):,.2f}")
        print(f"   💰 Available cash: ${summary.get('available_cash', 0):,.2f}")
        print(f"   📊 Number of positions: {summary.get('num_positions', 0)}")
    
    print()
    
    # Demo trade execution (won't actually execute since auto_execute=False)
    print("4. Demonstrating trade execution (simulation mode)...")
    if analysis['recommendation'] == 'COMPRA':
        success, message = bot.execute_trade(
            symbol='GGAL',
            signal='COMPRA',
            quantity=10,
            stop_loss=analysis.get('stop_loss'),
            take_profit=analysis.get('take_profit')
        )
        print(f"   {'✅' if success else '⚠️'} {message}")
    else:
        print(f"   ⚠️  No buy signal detected. Recommendation: {analysis['recommendation']}")
    
    print()
    print("=" * 80)
    print("TRADING BOT DEMO COMPLETE")
    print("=" * 80)
    print()
    print("💡 NEXT STEPS:")
    print("   1. Review the analysis results above")
    print("   2. Set AUTO_EXECUTE=true in .env to enable automatic trading")
    print("   3. Configure Telegram for real-time alerts")
    print("   4. Monitor positions with bot.monitor_positions()")
    print()


if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        print("📝 Please create a .env file based on .env.example")
        print()
        print("Steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your IOL credentials")
        print("3. Run this script again")
        sys.exit(1)
    
    # Run demos
    demo_iol_client()
    demo_trading_bot()
