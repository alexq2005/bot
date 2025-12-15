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

        # 2. Deep RL Decision (The General)
        # The RL Agent sees [Price, RSI, MACD, Sentiment, PositionStatus] and decides the best move.
        # Position Status: 0=None, 1=Long
        pos_status = 1 if current_position_size > 0 else 0

        rl_action = self.ml.predict_action(rsi, macd_line, sentiment_score, pos_status)
        # Action Map: 0=Hold, 1=Buy, 2=Sell

        signal = "HOLD"
        reasons = []

        if rl_action == 1:
            signal = "BUY"
            reasons.append("RL Agent Decision: BUY")
        elif rl_action == 2:
            signal = "SELL"
            reasons.append("RL Agent Decision: SELL")
        else:
            reasons.append("RL Agent Decision: HOLD")

        # Fallback/Confirmation logic (Optional):
        # We could override the RL agent if risk is extreme (e.g. RSI > 90), but for SOTA, we trust the agent.

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
