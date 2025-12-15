import pandas as pd
import pandas_ta as ta
import logging
from typing import Dict, List, Any
from .config import settings

logger = logging.getLogger(__name__)

class EvolutionaryStrategy:
    """
    SOTA Strategy: Technicals + AI Sentiment + ML Probability Validation.
    The ultimate decision maker.
    """

    def __init__(self, ml_engine):
        self.ml = ml_engine

    def analyze(self, symbol: str, data: List[Dict], sentiment_score: float = 0.0, atr: float = 0.0) -> Dict[str, Any]:
        """
        Returns a trading signal verified by the ML Brain.
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

        # 4. ML Validation (The Gatekeeper)
        # Ask the Brain: "Is this a winning setup?"
        win_probability = self.ml.predict_profitability(rsi, macd_line, sentiment_score, atr)

        signal = "HOLD"

        # Only trade if Score is high AND ML confirms probability > 60%
        if final_score >= 0.5:
            if win_probability > 0.60:
                signal = "STRONG_BUY" if final_score >= 1.5 else "BUY"
                reasons.append(f"ML Confirmed (Prob {win_probability:.0%})")
            else:
                reasons.append(f"ML Rejected (Prob {win_probability:.0%})")

        elif final_score <= -0.5:
            signal = "STRONG_SELL" if final_score <= -1.5 else "SELL"

        result = {
            "symbol": symbol,
            "signal": signal,
            "price": current['close'],
            "indicators": {
                "rsi": round(rsi, 2),
                "macd": round(macd_line, 4),
                "tech_score": tech_score,
                "sentiment_score": sentiment_score,
                "ml_probability": win_probability
            },
            "reason": ", ".join(reasons)
        }

        logger.info(f"🧬 Evolutionary Analysis {symbol}: {signal} | Score: {final_score} | ML Prob: {win_probability:.2f}")
        return result
