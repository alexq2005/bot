import pytest
from src.ai_engine import AIEngine

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

# Removed legacy hybrid strategy test as we now use EvolutionaryStrategy with ML Brain
