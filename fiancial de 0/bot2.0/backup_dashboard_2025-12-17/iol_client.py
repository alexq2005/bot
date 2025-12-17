"""
IOL API Client
Cliente para interactuar con la API de Invertir Online
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd


class IOLClient:
    """Cliente para la API de Invertir Online (IOL)"""
    
    def __init__(self, username: str, password: str, base_url: str):
        """
        Inicializa el cliente de IOL
        
        Args:
            username: Usuario de IOL
            password: Contraseña de IOL
            base_url: URL base de la API
        """
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.token_expiry = None
        self.session = requests.Session()
    
    def authenticate(self) -> bool:
        """
        Autentica con la API de IOL y obtiene token
        
        Returns:
            bool: True si la autenticación fue exitosa
        """
        try:
            url = f"{self.base_url}/token"
            payload = {
                "username": self.username,
                "password": self.password,
                "grant_type": "password"
            }
            
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # Default 1 hora
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Configurar headers para futuras requests
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            
            return True
            
        except Exception as e:
            print(f"Error en autenticación IOL: {e}")
            return False
    
    def _ensure_authenticated(self):
        """Verifica que el token esté vigente, si no, re-autentica"""
        if not self.token or datetime.now() >= self.token_expiry:
            self.authenticate()
    
    def get_current_price(self, symbol: str, market: str = "bCBA") -> Optional[float]:
        """
        Obtiene el precio actual de un símbolo
        
        Args:
            symbol: Símbolo del activo (ej: GGAL)
            market: Mercado (default: bCBA - Bolsa de Comercio de Buenos Aires)
        
        Returns:
            float: Precio actual o None si hay error
        """
        self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            # IOL devuelve último precio en 'ultimoPrecio' o 'puntas'
            price = data.get("ultimoPrecio") or data.get("puntas", {}).get("precioCompra")
            
            return float(price) if price else None
            
        except Exception as e:
            print(f"Error obteniendo precio de {symbol}: {e}")
            return None
    
    def get_last_price(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Obtiene quote completo del símbolo desde IOL
        
        Args:
            symbol: Símbolo del activo (ej: GGAL)
            market: Mercado (default: bCBA)
        
        Returns:
            Dict con: price, settlementPrice, variationRate, amount, opening, maxDay, minDay
        """
        self._ensure_authenticated()
        
        try:
            # Obtener datos de la cotización
            url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer valores del response de IOL con múltiples fallbacks
            price = float(
                data.get("ultimoPrecio")
                or data.get("precio")
                or data.get("puntas", {}).get("precioCompra")
                or data.get("puntas", {}).get("precio")
                or 0
            )

            settlement = float(
                data.get("precioAnterior")
                or data.get("settlementPrice")
                or data.get("cierre")
                or data.get("precioUltimoOperado")
                or 0
            )

            # Calcular variación
            variation_rate = 0
            if settlement > 0:
                variation_rate = ((price - settlement) / settlement) * 100

            opening = float(
                data.get("apertura")
                or data.get("aperturaOperacion")
                or settlement
                or 0
            )

            max_day = float(
                data.get("maximo")
                or data.get("maxDay")
                or data.get("maximoDia")
                or price
            )

            min_day = float(
                data.get("minimo")
                or data.get("minDay")
                or data.get("minimoDia")
                or price
            )

            return {
                'price': price,
                'settlementPrice': settlement,
                'variationRate': round(variation_rate, 2),
                'amount': float(data.get("volumen") or data.get("amount") or 0),
                'opening': opening,
                'maxDay': max_day,
                'minDay': min_day
            }
            
        except Exception as e:
            print(f"Error obteniendo quote de {symbol}: {e}")
            return None
    
    def get_historical_data(
        self, 
        symbol: str, 
        from_date: datetime, 
        to_date: datetime,
        market: str = "bCBA"
    ) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos OHLCV
        
        Args:
            symbol: Símbolo del activo
            from_date: Fecha inicial
            to_date: Fecha final
            market: Mercado
        
        Returns:
            DataFrame con columnas: date, open, high, low, close, volume
        """
        self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica"
            params = {
                "fechaDesde": from_date.strftime("%Y-%m-%d"),
                "fechaHasta": to_date.strftime("%Y-%m-%d"),
                "ajustada": "true"  # Ajustada por splits/dividendos
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Convertir a DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['fechaHora'])
            df = df.rename(columns={
                'apertura': 'open',
                'maximo': 'high',
                'minimo': 'low',
                'cierre': 'close',
                'volumen': 'volume'
            })
            
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error obteniendo datos históricos de {symbol}: {e}")
            
            # FALLBACK A YAHOO FINANCE
            try:
                print(f"🔄 Intentando obtener datos de Yahoo Finance para {symbol}...")
                from src.api.yahoo_client import yahoo_client
                
                # Market mapping
                y_market = "BCBA" if market == "bCBA" else "USA"
                
                df = yahoo_client.get_historical_data(
                    symbol=symbol,
                    start_date=from_date,
                    end_date=to_date,
                    market=y_market
                )
                
                if not df.empty:
                    print(f"✅ Datos recuperados exitosamente desde Yahoo Finance para {symbol}")
                    return df
                else:
                    return None
                    
            except Exception as e2:
                print(f"❌ Falló fallback Yahoo: {e2}")
                return None
    
    def get_portfolio(self) -> Optional[Dict]:
        """
        Obtiene el portafolio actual
        
        Returns:
            Dict con información del portafolio
        """
        self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/api/v2/portafolio/argentina"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error obteniendo portafolio: {e}")
            return None
    
    def get_account_balance(self) -> Optional[float]:
        """
        Obtiene el saldo disponible en cuenta.
        Intenta múltiples rutas en el JSON de respuesta.
        """
        self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/api/v2/estadocuenta"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            # print(f"DEBUG IOL DATA: {data}") # Descomentar para debug extremo
            
            # Opción 1: cuentas[0].disponible (La estructura más común observada)
            if "cuentas" in data and isinstance(data["cuentas"], list):
                for cuenta in data["cuentas"]:
                    # Match exacto o parcial
                    moneda = str(cuenta.get("moneda", "")).lower()
                    if "peso" in moneda and "argentino" in moneda:
                        return float(cuenta.get("disponible", 0))
                
                # Fallback: primera cuenta
                if len(data["cuentas"]) > 0:
                     return float(data["cuentas"][0].get("disponible", 0))

            # Opción 2: saldos.disponible (Antigua estructura?)
            if "saldos" in data:
                return float(data["saldos"].get("disponible", 0))
            
            # Opción 3: disponible directo
            if "disponible" in data:
                return float(data["disponible"])
            
            return 0.0
            
        except Exception as e:
            print(f"Error obteniendo saldo: {e}")
            return None
    
    def place_market_order(
        self, 
        symbol: str, 
        quantity: int, 
        side: str,
        market: str = "bCBA"
    ) -> Optional[Dict]:
        """
        Coloca una orden de mercado
        
        Args:
            symbol: Símbolo del activo
            quantity: Cantidad de acciones
            side: 'compra' o 'venta'
            market: Mercado
        
        Returns:
            Dict con información de la orden o None si falla
        """
        self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/api/v2/operar/Comprar" if side == "compra" else \
                  f"{self.base_url}/api/v2/operar/Vender"
            
            payload = {
                "mercado": market,
                "simbolo": symbol,
                "cantidad": quantity,
                "precio": None,  # Orden de mercado
                "plazo": "t2",  # Plazo de liquidación
                "validez": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error colocando orden {side} de {symbol}: {e}")
            return None
    
    def buy(self, symbol: str, quantity: int) -> Optional[Dict]:
        """Compra acciones"""
        return self.place_market_order(symbol, quantity, "compra")
    
    def sell(self, symbol: str, quantity: int) -> Optional[Dict]:
        """Vende acciones"""
        return self.place_market_order(symbol, quantity, "venta")
    
    def get_position(self, symbol: str) -> Optional[int]:
        """
        Obtiene la cantidad de acciones que se poseen de un símbolo
        
        Returns:
            int: Cantidad de acciones o 0 si no se posee
        """
        portfolio = self.get_portfolio()
        if not portfolio:
            return 0
        
        activos = portfolio.get("activos", [])
        for activo in activos:
            if activo.get("titulo", {}).get("simbolo") == symbol:
                return int(activo.get("cantidad", 0))
        
        return 0
