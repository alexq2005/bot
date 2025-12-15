import pandas as pd
import pandas_ta as ta
import logging
from typing import Dict, List, Any
from .config import settings

logger = logging.getLogger(__name__)

class HybridStrategy:
    """
    Implements an AI-Enhanced Hybrid Strategy.
    Combines Technical Analysis (60%) with AI Sentiment Analysis (40%).
    """

    def analyze(self, symbol: str, data: List[Dict], sentiment_score: float = 0.0) -> Dict[str, Any]:
        """
        Returns a trading signal based on Tech + AI.

        Sentiment Logic:
        - > 0.15: Bullish Bias (+1 to score)
        - < -0.15: Bearish Bias (-1 to score)
        """
        if not data:
            return {"signal": "HOLD", "reason": "No data"}

        df = pd.DataFrame(data)

        # Ensure sufficient data
        if len(df) < 50:
            return {"signal": "HOLD", "reason": "Insufficient data length"}

        # 1. Technical Analysis (Base)
        # RSI
        df.ta.rsi(length=settings.RSI_PERIOD, append=True)
        # MACD
        df.ta.macd(fast=settings.MACD_FAST, slow=settings.MACD_SLOW, signal=settings.MACD_SIGNAL, append=True)

        current = df.iloc[-1]
        rsi = current[f'RSI_{settings.RSI_PERIOD}']
        macd_line = current[f'MACD_{settings.MACD_FAST}_{settings.MACD_SLOW}_{settings.MACD_SIGNAL}']
        macd_signal = current[f'MACDs_{settings.MACD_FAST}_{settings.MACD_SLOW}_{settings.MACD_SIGNAL}']

        tech_score = 0
        reasons = []

        # Technical Scoring
        if rsi < settings.RSI_OVERSOLD:
            tech_score += 1
            reasons.append(f"RSI Oversold ({rsi:.2f})")
        elif rsi > settings.RSI_OVERBOUGHT:
            tech_score -= 1
            reasons.append(f"RSI Overbought ({rsi:.2f})")

        if macd_line > macd_signal:
            tech_score += 0.5 # MACD is trend following, less weight than extreme RSI
            reasons.append("MACD Bullish")
        elif macd_line < macd_signal:
            tech_score -= 0.5
            reasons.append("MACD Bearish")

        # 2. AI Sentiment Integration
        sentiment_adjustment = 0
        if sentiment_score > 0.15:
            sentiment_adjustment = 1
            reasons.append(f"AI Sentiment Bullish ({sentiment_score:.2f})")
        elif sentiment_score < -0.15:
            sentiment_adjustment = -1
            reasons.append(f"AI Sentiment Bearish ({sentiment_score:.2f})")

        # 3. Final Fusion (Weighted)
        # We give Tech slightly more weight, but Sentiment can tip the scales
        # Tech Range: -1.5 to 1.5
        # Sentiment Range: -1 to 1

        final_score = tech_score + sentiment_adjustment

        signal = "HOLD"
        if final_score >= 1.5:
            signal = "STRONG_BUY"
        elif final_score >= 0.5:
            signal = "BUY"
        elif final_score <= -1.5:
            signal = "STRONG_SELL"
        elif final_score <= -0.5:
            signal = "SELL"

        result = {
            "symbol": symbol,
            "signal": signal,
            "price": current['close'],
            "indicators": {
                "rsi": round(rsi, 2),
                "macd": round(macd_line, 4),
                "tech_score": tech_score,
                "sentiment_score": sentiment_score
            },
            "reason": ", ".join(reasons)
        }

        logger.info(f"🧠 Hybrid Analysis {symbol}: {signal} (Tech:{tech_score} + AI:{sentiment_adjustment} = {final_score})")
        return result
