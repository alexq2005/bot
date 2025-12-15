import logging
from textblob import TextBlob
from typing import List, Dict

logger = logging.getLogger(__name__)

class AIEngine:
    """
    Artificial Intelligence Engine for Sentiment Analysis.
    Uses NLP to process news titles and determine market sentiment.
    """

    def analyze_sentiment(self, articles: List[Dict]) -> float:
        """
        Analyzes a list of articles and returns a sentiment score between -1.0 and 1.0.
        -1.0: Extremely Negative
         0.0: Neutral
         1.0: Extremely Positive
        """
        if not articles:
            return 0.0

        total_polarity = 0.0
        count = 0

        for article in articles:
            title = article.get('title', '')
            if not title:
                continue

            # Use TextBlob for Sentiment Analysis
            blob = TextBlob(title)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Weight: Give more weight to objective news?
            # For now, raw polarity is fine.
            total_polarity += polarity
            count += 1

            logger.debug(f"Analyzed: '{title[:30]}...' -> Score: {polarity:.2f}")

        if count == 0:
            return 0.0

        avg_sentiment = total_polarity / count
        logger.info(f"🧠 AI Sentiment Score: {avg_sentiment:.2f} (based on {count} articles)")

        return avg_sentiment

    def get_recommendation(self, sentiment_score: float) -> str:
        """Translates numerical score to text recommendation"""
        if sentiment_score > 0.15:
            return "BULLISH"
        elif sentiment_score < -0.15:
            return "BEARISH"
        else:
            return "NEUTRAL"
