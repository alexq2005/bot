import requests
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .config import settings

logger = logging.getLogger(__name__)

class IOLClient:
    """
    Client for interacting with Invertir Online API.
    Supports a robust MOCK_MODE for safe testing.
    """
    BASE_URL = "https://api.invertironline.com"

    def __init__(self):
        self.mock_mode = settings.MOCK_MODE or not (settings.IOL_USERNAME and settings.IOL_PASSWORD)
        self.token = None
        self.token_expiry = None

        if self.mock_mode:
            logger.info("⚠️ IOLClient starting in MOCK MODE")
        else:
            logger.info("🔐 IOLClient starting in LIVE MODE")

    def authenticate(self) -> bool:
        """Authenticates with IOL API."""
        if self.mock_mode:
            self.token = "MOCK_TOKEN"
            self.token_expiry = datetime.now() + timedelta(hours=1)
            return True

        # Implementation for real auth would go here
        # (Simplified for this exercise as we don't have real creds)
        logger.warning("Real authentication not implemented in this demo (No credentials).")
        return False

    def get_market_data(self, symbol: str) -> Optional[float]:
        """Fetches current price for a symbol."""
        if self.mock_mode:
            # Random walk simulation
            base_price = 100.0
            return round(base_price * (1 + random.uniform(-0.05, 0.05)), 2)

        # Real implementation
        # endpoint = f"{self.BASE_URL}/..."
        return None

    def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Fetches historical OHLCV data for analysis."""
        if self.mock_mode:
            data = []
            price = 100.0
            today = datetime.now()
            for i in range(days):
                date = today - timedelta(days=days-i)
                open_p = price
                close_p = price * (1 + random.uniform(-0.02, 0.02))
                high_p = max(open_p, close_p) * 1.01
                low_p = min(open_p, close_p) * 0.99
                volume = random.randint(1000, 10000)

                data.append({
                    "date": date,
                    "open": open_p,
                    "high": high_p,
                    "low": low_p,
                    "close": close_p,
                    "volume": volume
                })
                price = close_p
            return data

        return []

    def place_order(self, symbol: str, side: str, quantity: int, price: float) -> bool:
        """Places a buy/sell order."""
        if self.mock_mode:
            logger.info(f"📝 [MOCK ORDER] {side.upper()} {quantity} {symbol} @ {price}")
            return True

        # Real implementation
        return False
