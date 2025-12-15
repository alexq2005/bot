import pytest
from src.ai_engine import AIEngine

from unittest.mock import MagicMock, patch

def test_ai_sentiment_neutral():
    with patch('src.ai_engine.pipeline') as mock_pipeline:
        # Mock pipeline not initialized
        ai = AIEngine()
        # Force pipeline to be None to test fallback (or simulate behavior)
        AIEngine._pipeline = None
        score = ai.analyze_sentiment([])
        assert score == 0.0

def test_ai_sentiment_positive():
    # Mock FinBERT Output
    mock_result = [{'label': 'positive', 'score': 0.9}]

    with patch('src.ai_engine.pipeline') as mock_pipeline:
        mock_pipeline.return_value = MagicMock(return_value=mock_result)

        # We need to manually inject the mock pipeline into the class for this test
        # because singleton might be already initialized or failed
        AIEngine._pipeline = MagicMock(return_value=mock_result)

        ai = AIEngine()
        articles = [{"title": "Profit Growth"}]
        score = ai.analyze_sentiment(articles)
        assert score > 0 # Should be positive

def test_ai_sentiment_negative():
    mock_result = [{'label': 'negative', 'score': 0.9}]

    with patch('src.ai_engine.pipeline') as mock_pipeline:
        AIEngine._pipeline = MagicMock(return_value=mock_result)

        ai = AIEngine()
        articles = [{"title": "Market Crash"}]
        score = ai.analyze_sentiment(articles)
        assert score < 0 # Should be negative

# Removed legacy hybrid strategy test as we now use EvolutionaryStrategy with ML Brain
