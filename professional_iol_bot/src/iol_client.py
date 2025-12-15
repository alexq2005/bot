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

        logger.info("🔐 Authenticating with IOL...")
        endpoint = f"{self.BASE_URL}/token"
        data = {
            "username": settings.IOL_USERNAME,
            "password": settings.IOL_PASSWORD,
            "grant_type": "password"
        }

        try:
            response = requests.post(endpoint, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 300)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

            logger.info("✅ Authentication successful")
            return True
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_market_data(self, symbol: str) -> Optional[float]:
        """Fetches current price for a symbol."""
        if self.mock_mode:
            # Random walk simulation
            base_price = 100.0
            return round(base_price * (1 + random.uniform(-0.05, 0.05)), 2)

        # Real implementation
        # Market defaults to bCBA (Buenos Aires)
        market = "bCBA"
        endpoint = f"{self.BASE_URL}/api/v2/{market}/Titulos/{symbol}/Cotizacion"

        try:
            if not self.token: self.authenticate()

            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("ultimoPrecio") # or lastPrice depending on API version
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
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

        # Real implementation
        market = "bCBA"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Format dates as YYYY-MM-DD
        from_str = start_date.strftime("%Y-%m-%d")
        to_str = end_date.strftime("%Y-%m-%d")

        endpoint = f"{self.BASE_URL}/api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{from_str}/{to_str}/ajustada"

        try:
            if not self.token: self.authenticate()

            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            raw_data = response.json()

            # Map IOL format to our internal format
            clean_data = []
            for item in raw_data:
                clean_data.append({
                    "date": item.get("fechaHora"),
                    "open": item.get("apertura"),
                    "high": item.get("maximo"),
                    "low": item.get("minimo"),
                    "close": item.get("ultimoPrecio"),
                    "volume": item.get("volumenNominal")
                })
            return clean_data

        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return []

    def place_order(self, symbol: str, side: str, quantity: int, price: float) -> bool:
        """Places a buy/sell order."""
        if self.mock_mode:
            logger.info(f"📝 [MOCK ORDER] {side.upper()} {quantity} {symbol} @ {price}")
            return True

        # Real implementation
        # side must be 'Comprar' or 'Vender'
        iol_side = "Comprar" if side.upper() == "BUY" else "Vender"
        endpoint = f"{self.BASE_URL}/api/v2/operar/{iol_side}"

        payload = {
            "simbolo": symbol,
            "cantidad": quantity,
            "precio": price,
            "plazo": "t0", # Contado Inmediato by default
            "mercado": "bCBA"
        }

        try:
            if not self.token: self.authenticate()

            logger.info(f"🚀 Sending REAL order: {iol_side} {quantity} {symbol} @ {price}")
            response = requests.post(endpoint, json=payload, headers=self._get_headers())
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Order placed successfully. ID: {result.get('numeroOperacion')}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            if response is not None:
                logger.error(f"API Response: {response.text}")
            return False
