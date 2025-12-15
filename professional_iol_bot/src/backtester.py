import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class Backtester:
    """
    Professional Backtesting Engine.
    Replays historical data to evaluate strategy performance.
    """

    def __init__(self, strategy, initial_capital=100000.0):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.portfolio = {} # {symbol: quantity}
        self.trades = []
        self.equity_curve = []

    def run(self, symbol: str, data: List[Dict]):
        """Runs the backtest for a single symbol over the provided data"""
        df = pd.DataFrame(data)

        # Pre-calculate indicators for speed
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.atr(length=14, append=True)

        logger.info(f"🔙 Starting Backtest for {symbol} ({len(df)} candles)...")

        for i in range(50, len(df)):
            # Slice history up to current point
            # In a real engine, we'd pass the full DF and current index to avoid copying
            # But our strategy expects a list of dicts for 'history' (legacy) or we adapt

            # Optimization: Pass window of data
            window = df.iloc[:i+1]
            current_bar = df.iloc[i]
            price = current_bar['close']
            date = current_bar.get('date', i)

            # Reconstruct history list for strategy (shim)
            # A better way would be to make strategy accept DF directly
            history_shim = window.to_dict('records')

            # Mock Sentiment (Neutral for backtest unless we have historical sentiment data)
            sentiment_score = current_bar.get('sentiment', 0.0)
            atr = current_bar.get('ATR_14', 0.0)

            current_pos = self.portfolio.get(symbol, 0)

            # Get Signal
            analysis = self.strategy.analyze(symbol, history_shim, sentiment_score, atr, current_pos)
            signal = analysis['signal']

            # Execute Logic (Simplified)
            if "BUY" in signal and current_pos == 0:
                quantity = int((self.capital * 0.1) / price) # Fixed 10% allocation for backtest sim
                cost = quantity * price
                if self.capital >= cost:
                    self.capital -= cost
                    self.portfolio[symbol] = quantity
                    self._record_trade(date, symbol, "BUY", quantity, price)

            elif "SELL" in signal and current_pos > 0:
                revenue = current_pos * price
                self.capital += revenue
                self.portfolio[symbol] = 0
                self._record_trade(date, symbol, "SELL", current_pos, price)

            # Update Equity
            portfolio_val = sum([q * price for s, q in self.portfolio.items()]) # Approx using current symbol price for all
            self.equity_curve.append({"date": date, "equity": self.capital + portfolio_val})

        self._generate_report()

    def _record_trade(self, date, symbol, side, qty, price):
        self.trades.append({
            "date": date, "symbol": symbol, "side": side, "qty": qty, "price": price
        })

    def _generate_report(self):
        if not self.equity_curve:
            print("No data to report.")
            return

        final_equity = self.equity_curve[-1]['equity']
        total_return = (final_equity - self.initial_capital) / self.initial_capital

        # Calculate Drawdown
        equity_series = pd.Series([x['equity'] for x in self.equity_curve])
        rolling_max = equity_series.cummax()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        print("\n📊 === BACKTEST REPORT ===")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Equity:    ${final_equity:,.2f}")
        print(f"Total Return:    {total_return:.2%}")
        print(f"Max Drawdown:    {max_drawdown:.2%}")
        print(f"Total Trades:    {len(self.trades)}")
        print("=========================\n")
