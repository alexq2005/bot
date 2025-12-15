import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReasoningEngine:
    """
    Logic Processor that explains the 'WHY' behind the trading decisions.
    Generates structured natural language explanations based on Technicals, AI, and RL inputs.
    """

    def explain_decision(self, symbol: str, rsi: float, sentiment: float, rl_action: int, tech_signal: str, atr: float, final_signal: str) -> str:
        """
        Constructs a narrative explanation.
        """
        narrative = []

        # 1. Context (Volatility)
        volatility_desc = "Low"
        if atr > 2.0: volatility_desc = "High"
        elif atr > 1.0: volatility_desc = "Moderate"

        narrative.append(f"Market context for {symbol} shows {volatility_desc} volatility (ATR: {atr:.2f}).")

        # 2. Technical Analysis
        tech_view = "Neutral"
        if rsi < 30: tech_view = "Oversold (Bullish)"
        elif rsi > 70: tech_view = "Overbought (Bearish)"

        narrative.append(f"Technical indicators suggest the asset is {tech_view} (RSI: {rsi:.1f}).")

        # 3. Sentiment
        sentiment_view = "Neutral"
        if sentiment > 0.15: sentiment_view = "Positive"
        elif sentiment < -0.15: sentiment_view = "Negative"

        narrative.append(f"News sentiment analysis is {sentiment_view} ({sentiment:.2f}).")

        # 4. Neural Network (RL)
        rl_view = "HOLD"
        if rl_action == 1: rl_view = "BUY"
        elif rl_action == 2: rl_view = "SELL"

        narrative.append(f"The Recurrent Neural Network (LSTM) advises to {rl_view} based on pattern recognition.")

        # 5. Synthesis / Conclusion
        if final_signal == "BUY":
            reason = "strong alignment between Technicals and AI models"
            if tech_signal == "HOLD" and rl_action == 1:
                reason = "AI conviction overriding neutral technicals"
            narrative.append(f"CONCLUSION: Executing BUY order due to {reason}.")

        elif final_signal == "SELL":
            reason = "deteriorating conditions"
            if rl_action == 2:
                reason = "AI safety trigger"
            narrative.append(f"CONCLUSION: Executing SELL order triggered by {reason}.")

        else:
            narrative.append("CONCLUSION: Holding position. Waiting for clearer signal alignment.")

        full_text = " ".join(narrative)
        logger.info(f"🗣️ REASONING: {full_text}")
        return full_text
