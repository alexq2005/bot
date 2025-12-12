"""
Cliente IOL (Invertir Online)

Integración con la API de IOL para:
- Autenticación
- Obtención de datos de mercado
- Ejecución de órdenes
- Consulta de portafolio

Documentación IOL API: https://api.invertironline.com/
"""

import logging
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class IOLClient:
    """Cliente para integración con API de Invertir Online"""

    BASE_URL = "https://api.invertironline.com"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Inicializa el cliente IOL.
        
        Args:
            username: Usuario de IOL
            password: Contraseña de IOL
        """
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

        # Modo Mock si no hay credenciales
        self.mock_mode = not (username and password)
        if self.mock_mode:
            logger.warning("⚠️ Credenciales no proporcionadas. Iniciando en MOCK MODE.")

    def _is_token_valid(self) -> bool:
        """Verifica si el token actual es válido"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry

    def authenticate(self) -> bool:
        """
        Autentica con IOL y obtiene el Bearer Token.
        """
        if self.mock_mode:
            logger.info("🔐 [MOCK] Autenticación simulada exitosa")
            return True

        logger.info("🔐 Autenticando con IOL...")
        endpoint = f"{self.BASE_URL}/token"
        data = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password"
        }
        
        try:
            # Nota: La implementación real puede variar según endpoints específicos de IOL
            # Se asume flujo OAuth2 estándar
            response = requests.post(endpoint, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 300)

            # Calcular expiración (con margen de seguridad de 60s)
            self.token_expiry = datetime.now().timestamp() + expires_in - 60

            logger.info("✅ Autenticación exitosa")
            return True

        except Exception as e:
            logger.error(f"❌ Error de autenticación: {str(e)}")
            return False

    def _get_headers(self) -> Dict:
        """Obtiene headers para requests"""
        if not self._is_token_valid() and not self.mock_mode:
             self.authenticate()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_market_data(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Obtiene datos de mercado en tiempo real (Cotización).
        """
        if self.mock_mode:
            # Generar datos simulados
            import random
            base_price = 1000.0 if symbol == "GGAL" else 500.0
            variation = random.uniform(-0.02, 0.02)
            price = base_price * (1 + variation)
            
            return {
                "symbol": symbol,
                "last_price": round(price, 2),
                "bid": round(price * 0.99, 2),
                "ask": round(price * 1.01, 2),
                "volume": random.randint(1000, 50000),
                "timestamp": datetime.now().isoformat()
            }

        endpoint = f"{self.BASE_URL}/api/v2/{market}/Titulos/{symbol}/Cotizacion"
        try:
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo cotización de {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, start_date: str, end_date: str, market: str = "bCBA") -> List[Dict]:
        """
        Obtiene datos históricos para análisis técnico.
        """
        if self.mock_mode:
            # Simular una lista de velas históricas
            # Esto es necesario para que pandas-ta funcione en la demo
            data = []
            import random
            current_price = 1000.0
            
            # Generar 100 velas
            for i in range(100):
                change = random.uniform(-0.02, 0.02)
                open_p = current_price
                close_p = open_p * (1 + change)
                high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
                low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
                vol = random.randint(1000, 10000)

                data.append({
                    "fecha": f"2024-01-{i+1:02d}", # Fecha simulada
                    "apertura": open_p,
                    "cierre": close_p,
                    "maximo": high_p,
                    "minimo": low_p,
                    "volumen": vol
                })
                current_price = close_p
            return data

        endpoint = f"{self.BASE_URL}/api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{start_date}/{end_date}/ajustada"
        try:
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo histórico de {symbol}: {e}")
            return []

    def place_order(self, symbol: str, side: str, quantity: int, price: float, order_type: str = "Limit") -> Optional[Dict]:
        """
        Coloca una orden de compra o venta.
        side: 'Comprar' o 'Vender'
        """
        if self.mock_mode:
            logger.info(f"📝 [MOCK] Orden enviada: {side} {quantity} {symbol} @ {price}")
            return {"orderId": 12345, "status": "pending", "message": "Orden simulada exitosa"}

        endpoint = f"{self.BASE_URL}/api/v2/operar/{side}"
        payload = {
            "simbolo": symbol,
            "cantidad": quantity,
            "precio": price,
            "plazo": "t0", # Contado Inmediato
            "mercado": "bCBA"
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self._get_headers())
            response.raise_for_status()
            logger.info(f"✅ Orden enviada exitosamente: {symbol}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error al enviar orden: {e}")
            return None

    def get_portfolio(self) -> Dict:
        """Obtiene el estado del portafolio"""
        if self.mock_mode:
            return {
                "total_value": 1000000.0,
                "available_cash": 250000.0,
                "assets": [
                    {"symbol": "GGAL", "quantity": 100, "last_price": 2500.0},
                    {"symbol": "YPFD", "quantity": 50, "last_price": 18000.0}
                ]
            }

        endpoint = f"{self.BASE_URL}/api/v2/estadocuenta"
        try:
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo portafolio: {e}")
            return {}

__all__ = ['IOLClient']
