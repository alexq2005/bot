import pytest
from src.iol_client import IOLClient
from src.config import settings

def test_client_mock_init():
    # Ensure Mock Mode is default without creds
    client = IOLClient()
    assert client.mock_mode is True

def test_client_auth_mock():
    client = IOLClient()
    assert client.authenticate() is True
    assert client.token == "MOCK_TOKEN"

def test_client_market_data_mock():
    client = IOLClient()
    price = client.get_market_data("GGAL")
    assert isinstance(price, float)
    assert price > 0

def test_client_historical_data_mock():
    client = IOLClient()
    data = client.get_historical_data("GGAL", days=10)
    assert len(data) == 10
    assert "close" in data[0]
