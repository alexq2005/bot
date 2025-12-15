import pandas as pd
import pandas_ta as ta
import logging
from typing import Dict, List, Any
from .config import settings

logger = logging.getLogger(__name__)

class TechnicalStrategy:
    """
    Implements a transparent Technical Analysis strategy.

    Indicators:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    """

    def analyze(self, symbol: str, data: List[Dict]) -> Dict[str, Any]:
        """
        Analyzes historical data and returns a trading signal.

        Signal Logic:
        - STRONG_BUY: RSI < 30 AND MACD Cross Up
        - BUY: RSI < 30 OR MACD Cross Up
        - STRONG_SELL: RSI > 70 AND MACD Cross Down
        - SELL: RSI > 70 OR MACD Cross Down
        - HOLD: No clear signal
        """
        if not data:
            return {"signal": "HOLD", "reason": "No data"}

        df = pd.DataFrame(data)

        # Ensure sufficient data
        if len(df) < 50:
            return {"signal": "HOLD", "reason": "Insufficient data length"}

        # Calculate Indicators using pandas-ta
        # RSI
        df.ta.rsi(length=settings.RSI_PERIOD, append=True)
        # MACD
        df.ta.macd(fast=settings.MACD_FAST, slow=settings.MACD_SLOW, signal=settings.MACD_SIGNAL, append=True)
        # Bollinger Bands
        df.ta.bbands(length=20, std=2, append=True)

        # Get latest values
        current = df.iloc[-1]

        rsi = current[f'RSI_{settings.RSI_PERIOD}']
        macd_line = current[f'MACD_{settings.MACD_FAST}_{settings.MACD_SLOW}_{settings.MACD_SIGNAL}']
        macd_signal = current[f'MACDs_{settings.MACD_FAST}_{settings.MACD_SLOW}_{settings.MACD_SIGNAL}']

        # Determine Signal
        signal = "HOLD"
        reasons = []

        # RSI Logic
        is_oversold = rsi < settings.RSI_OVERSOLD
        is_overbought = rsi > settings.RSI_OVERBOUGHT

        if is_oversold:
            reasons.append(f"RSI Oversold ({rsi:.2f})")
        if is_overbought:
            reasons.append(f"RSI Overbought ({rsi:.2f})")

        # MACD Logic
        # Check for crossover in the last 2 periods
        prev_macd = df.iloc[-2][f'MACD_{settings.MACD_FAST}_{settings.MACD_SLOW}_{settings.MACD_SIGNAL}']
        prev_signal = df.iloc[-2][f'MACDs_{settings.MACD_FAST}_{settings.MACD_SLOW}_{settings.MACD_SIGNAL}']

        macd_cross_up = (prev_macd < prev_signal) and (macd_line > macd_signal)
        macd_cross_down = (prev_macd > prev_signal) and (macd_line < macd_signal)

        if macd_cross_up:
            reasons.append("MACD Cross Up")
        if macd_cross_down:
            reasons.append("MACD Cross Down")

        # Combine Signals
        score = 0
        if is_oversold: score += 1
        if macd_cross_up: score += 1

        if is_overbought: score -= 1
        if macd_cross_down: score -= 1

        if score >= 2:
            signal = "STRONG_BUY"
        elif score == 1:
            signal = "BUY"
        elif score <= -2:
            signal = "STRONG_SELL"
        elif score == -1:
            signal = "SELL"

        result = {
            "symbol": symbol,
            "signal": signal,
            "price": current['close'],
            "indicators": {
                "rsi": round(rsi, 2),
                "macd": round(macd_line, 4)
            },
            "reason": ", ".join(reasons)
        }

        logger.info(f"Analysis for {symbol}: {signal} | RSI: {rsi:.2f}")
        return result
