import logging
import torch
from transformers import pipeline
from typing import List, Dict

logger = logging.getLogger(__name__)

class AIEngine:
    """
    Artificial Intelligence Engine for Sentiment Analysis.
    Uses FinBERT (Financial BERT) to process news titles and determine market sentiment.
    """

    _pipeline = None

    def __init__(self):
        if AIEngine._pipeline is None:
            logger.info("🧠 Loading FinBERT Model... (This may take a moment)")
            try:
                # Use ProsusAI/finbert for specialized financial sentiment
                AIEngine._pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
                logger.info("✅ FinBERT Model Loaded Successfully")
            except Exception as e:
                logger.error(f"Failed to load FinBERT: {e}")
                # Fallback handled in analyze_sentiment logic if _pipeline is None

    def analyze_sentiment(self, articles: List[Dict]) -> float:
        """
        Analyzes a list of articles and returns a sentiment score between -1.0 and 1.0.
        -1.0: Extremely Negative
         0.0: Neutral
         1.0: Extremely Positive
        """
        if not articles:
            return 0.0

        if AIEngine._pipeline is None:
            logger.warning("FinBERT not available, returning neutral.")
            return 0.0

        total_score = 0.0
        count = 0

        for article in articles:
            title = article.get('title', '')
            if not title:
                continue

            try:
                # Truncate to 512 tokens max (handled by pipeline usually, but good to be safe with short headlines)
                result = AIEngine._pipeline(title[:512])[0]
                label = result['label'] # 'positive', 'negative', 'neutral'
                score = result['score'] # Confidence

                # Map FinBERT labels to -1..1 scale
                # Weight by confidence score
                val = 0.0
                if label == 'positive':
                    val = 1.0 * score
                elif label == 'negative':
                    val = -1.0 * score
                else: # neutral
                    val = 0.0

                total_score += val
                count += 1
                logger.debug(f"Analyzed: '{title[:30]}...' -> {label} ({score:.2f})")

            except Exception as e:
                logger.error(f"Error processing article '{title[:20]}...': {e}")

        if count == 0:
            return 0.0

        avg_sentiment = total_score / count
        logger.info(f"🧠 FinBERT Sentiment Score: {avg_sentiment:.2f} (based on {count} articles)")

        return avg_sentiment

    def get_recommendation(self, sentiment_score: float) -> str:
        """Translates numerical score to text recommendation"""
        if sentiment_score > 0.15:
            return "BULLISH"
        elif sentiment_score < -0.15:
            return "BEARISH"
        else:
            return "NEUTRAL"
