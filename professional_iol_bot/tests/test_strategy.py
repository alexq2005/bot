import pytest
from unittest.mock import MagicMock
from src.strategy import EvolutionaryStrategy
from src.config import settings

@pytest.fixture
def strategy():
    mock_ml = MagicMock()
    mock_ml.predict_profitability.return_value = 0.8 # High win prob
    return EvolutionaryStrategy(mock_ml)

def test_strategy_empty_data(strategy):
    result = strategy.analyze("TEST", [])
    assert result["signal"] == "HOLD"
    assert result["reason"] == "No data"

def test_strategy_insufficient_data(strategy):
    data = [{"close": 100}] * 10
    result = strategy.analyze("TEST", data)
    assert result["signal"] == "HOLD"
    assert "Insufficient data" in result["reason"]

def test_strategy_integration_mock(strategy):
    # Create fake data that should trigger a signal (or at least run without error)
    data = []
    price = 100.0
    # Generate 60 points
    for i in range(60):
        data.append({
            "close": price,
            "open": price,
            "high": price,
            "low": price,
            "volume": 1000
        })
        price *= 1.01 # Uptrend

    result = strategy.analyze("TEST", data, atr=2.5)

    # We expect indicators to be calculated
    assert "indicators" in result
    assert result["indicators"]["rsi"] is not None
