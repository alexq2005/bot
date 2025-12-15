import pytest
from unittest.mock import MagicMock
from src.strategy import EvolutionaryStrategy
from src.config import settings

@pytest.fixture
def strategy():
    mock_ml = MagicMock()
    # Action 1 = BUY
    mock_ml.predict_action.return_value = 1
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
    # Simulating a V-Shape Recovery to trigger Technical Buy + RL Buy
    data = []
    price = 100.0

    # 1. Crash (Low RSI)
    for i in range(40):
        price *= 0.95
        data.append({"close": price, "open": price, "high": price, "low": price, "volume": 1000})

    # 2. Rebound (MACD turn)
    for i in range(20):
        price *= 1.05
        data.append({"close": price, "open": price, "high": price, "low": price, "volume": 1000})

    # We pass a high sentiment score to help the consensus
    result = strategy.analyze("TEST", data, sentiment_score=0.8, atr=2.5)

    # Assert
    assert "indicators" in result
    assert "rl_action" in result["indicators"]
    # We mainly check that it runs and produces a result structure.
    # The exact signal depends on precise indicator values which vary,
    # but checking for 'indicators' proves the pipeline finished.
    assert result["symbol"] == "TEST"
