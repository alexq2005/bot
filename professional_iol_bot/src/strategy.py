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

    def analyze(self, symbol: str, data: List[Dict], sentiment_score: float = 0.0, atr: float = 0.0, current_position_size: int = 0) -> Dict[str, Any]:
        """
        Returns a trading signal verified by the Deep RL Agent.
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

        # 2. Deep RL Decision (The Confirmation)
        # The RL Agent sees [Price, RSI, MACD, Sentiment, PositionStatus] and decides the best move.
        pos_status = 1 if current_position_size > 0 else 0
        rl_action = self.ml.predict_action(rsi, macd_line, sentiment_score, pos_status)

        # 3. Hybrid Consensus Logic (Safety First)
        # Instead of blindly trusting RL (which might be young), we require a "Quorum".
        # Tech Signal + RL Signal must align for High Conviction.

        tech_signal = "HOLD"
        if rsi < settings.RSI_OVERSOLD and macd_line > 0: tech_signal = "BUY"
        elif rsi > settings.RSI_OVERBOUGHT: tech_signal = "SELL"

        signal = "HOLD"
        reasons = []

        # Action Map: 0=Hold, 1=Buy, 2=Sell
        if rl_action == 1: # RL Says Buy
            if tech_signal == "BUY" or sentiment_score > 0.5:
                signal = "BUY"
                reasons.append("Hybrid Consensus: BUY (RL + Tech/Sentiment)")
            else:
                reasons.append("RL suggests BUY (Vetoed by weak Tech)")

        elif rl_action == 2: # RL Says Sell
            signal = "SELL" # Safety: If RL says sell, we respect it to protect capital
            reasons.append("RL Agent Decision: SELL (Safety Trigger)")

        else: # RL Says Hold
            if tech_signal == "BUY" and sentiment_score > 0.7:
                signal = "BUY"
                reasons.append("Strong Fundamentals override RL Neutrality")
            else:
                reasons.append("Market Hold")

        result = {
            "symbol": symbol,
            "signal": signal,
            "price": current['close'],
            "indicators": {
                "rsi": round(rsi, 2),
                "macd": round(macd_line, 4),
                "sentiment_score": sentiment_score,
                "rl_action": rl_action
            },
            "reason": ", ".join(reasons)
        }

        logger.info(f"🧬 Evolutionary Analysis {symbol}: {signal} | RL Action: {rl_action}")
        return result
