"""
Generate sample visualization to show in PR
Creates a sample technical analysis chart
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.indicator_visualizer import IndicatorVisualizer


def generate_sample_chart():
    """Generate and save a sample technical analysis chart"""
    
    # Generate realistic sample data
    symbol = "GGAL"
    days = 90
    
    np.random.seed(42)
    base_price = 500
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Create price trend with some volatility
    returns = np.random.randn(days) * 0.02
    prices = base_price * np.exp(np.cumsum(returns))
    
    historical_data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.randn(days) * 0.005),
        'high': prices + np.abs(np.random.randn(days) * prices * 0.01),
        'low': prices - np.abs(np.random.randn(days) * prices * 0.01),
        'close': prices,
        'volume': np.random.randint(100000, 10000000, days)
    })
    
    # Calculate indicators
    print("📊 Calculating technical indicators...")
    indicators_calc = TechnicalIndicators()
    indicators_df = indicators_calc.calculate_all_indicators(historical_data)
    
    # Get signals
    signals = indicators_calc.get_trading_signals(historical_data)
    latest = indicators_calc.get_latest_indicators(historical_data)
    
    print(f"\n📈 Technical Analysis for {symbol}")
    print(f"   Price: ${latest['price']:.2f}")
    print(f"   RSI: {latest['rsi']:.2f}")
    print(f"   MACD: {latest['macd']:.4f}")
    print(f"\n🎯 Signals:")
    print(f"   RSI: {signals['rsi_signal']}")
    print(f"   MACD: {signals['macd_signal']}")
    print(f"   Bollinger: {signals['bb_signal']}")
    
    # Create visualization
    print("\n📊 Creating comprehensive chart...")
    visualizer = IndicatorVisualizer()
    fig = visualizer.create_comprehensive_chart(historical_data, indicators_df)
    
    # Save chart
    output_file = "technical_analysis_demo.html"
    fig.write_html(output_file)
    print(f"\n✅ Chart saved to: {output_file}")
    print("   Open this file in a browser to see the interactive chart")
    
    return fig, signals, latest


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GENERATING SAMPLE TECHNICAL ANALYSIS VISUALIZATION")
    print("=" * 70 + "\n")
    
    fig, signals, latest = generate_sample_chart()
    
    print("\n" + "=" * 70)
    print("✅ VISUALIZATION GENERATED SUCCESSFULLY")
    print("=" * 70 + "\n")
