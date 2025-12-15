import pytest
from src.ai_engine import AIEngine
from src.strategy import HybridStrategy

def test_ai_sentiment_neutral():
    ai = AIEngine()
    score = ai.analyze_sentiment([])
    assert score == 0.0

def test_ai_sentiment_positive():
    ai = AIEngine()
    # Use clearly positive words for TextBlob
    articles = [{"title": "Company reports great profit and excellent growth"}]
    score = ai.analyze_sentiment(articles)
    assert score > 0 # Should be positive

def test_ai_sentiment_negative():
    ai = AIEngine()
    articles = [{"title": "Market Crash: Worst recession in history"}]
    score = ai.analyze_sentiment(articles)
    assert score < 0 # Should be negative

def test_hybrid_strategy_boost():
    # Scenario: Technical signals SELL (-1), but Sentiment is Super Bullish (+1) -> Neutral (0) -> HOLD
    # OR: Technical is Neutral (0), Sentiment is Super Bullish (+1) -> BUY
    strategy = HybridStrategy()
    data = []
    price = 100
    for _ in range(60):
        data.append({"close": price, "open": price, "high": price, "low": price, "volume": 1000})
        price *= 1.001 # Flat/Slight up

    # Test with Neutral Sentiment
    result_neutral = strategy.analyze("TEST", data, sentiment_score=0.0)

    # Test with Bullish Sentiment
    result_bullish = strategy.analyze("TEST", data, sentiment_score=0.5)

    assert result_bullish['indicators']['tech_score'] == result_neutral['indicators']['tech_score']
    assert result_bullish['indicators']['sentiment_score'] == 0.5
