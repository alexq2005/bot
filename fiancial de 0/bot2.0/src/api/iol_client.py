"""
IOL API Client
Cliente para interactuar con la API de Invertir Online
Versión Corregida con Manejo Robusto de Errores
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import time

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
        self.session.headers.update({
            "User-Agent": "IOL-Trading-Bot/1.0",
            "Accept": "application/json"
        })
    
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
            
            print(f"Autenticando con IOL en {url}...")
            response = self.session.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Configurar headers para futuras requests
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            
            print(f"✅ Autenticación exitosa. Token válido hasta: {self.token_expiry}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión en autenticación IOL: {e}")
            return False
        except Exception as e:
            print(f"❌ Error en autenticación IOL: {e}")
            return False
    
    def _ensure_authenticated(self):
        """Verifica que el token esté vigente, si no, re-autentica"""
        if not self.token or datetime.now() >= self.token_expiry:
            print("Token expirado o no disponible, reautenticando...")
            if not self.authenticate():
                raise Exception("No se pudo autenticar con IOL")
    
    def get_last_price(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Obtiene quote completo del símbolo desde IOL
        
        Args:
            symbol: Símbolo del activo (ej: GGAL)
            market: Mercado (default: bCBA)
        
        Returns:
            Dict con: price, settlementPrice, variationRate, amount, opening, maxDay, minDay
            Retorna dict con valores por defecto si hay error
        """
        try:
            self._ensure_authenticated()
            
            # Obtener datos de la cotización
            url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion"
            
            print(f"Obteniendo quote para {symbol} desde {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Crear estructura base con valores por defecto
            result = {
                'price': 0.0,
                'settlementPrice': 0.0,
                'variationRate': 0.0,
                'amount': 0.0,
                'opening': 0.0,
                'maxDay': 0.0,
                'minDay': 0.0,
                'symbol': symbol,
                'market': market,
                'timestamp': datetime.now().isoformat()
            }
            
            # Debug: mostrar estructura de datos
            # print(f"DEBUG - Estructura de datos para {symbol}: {list(data.keys())}")
            # print(f"DEBUG - Datos completos: {data}")
            
            # Extraer precio con múltiples fallbacks
            price = 0.0
            
            # Intento 1: ultimoPrecio
            if 'ultimoPrecio' in data and data['ultimoPrecio'] is not None:
                price = float(data['ultimoPrecio'])
            
            # Intento 2: punta de compra
            if price == 0 and 'puntas' in data:
                puntas = data['puntas']
                if isinstance(puntas, dict):
                    if 'precioCompra' in puntas and puntas['precioCompra'] is not None:
                        price = float(puntas['precioCompra'])
                    elif 'precioVenta' in puntas and puntas['precioVenta'] is not None:
                        price = float(puntas['precioVenta'])
            
            # Intento 3: precio directo
            if price == 0 and 'precio' in data and data['precio'] is not None:
                price = float(data['precio'])
            
            result['price'] = price
            
            # Obtener settlement price (precio anterior)
            settlement = 0.0
            if 'precioAnterior' in data and data['precioAnterior'] is not None:
                settlement = float(data['precioAnterior'])
            elif 'cierre' in data and data['cierre'] is not None:
                settlement = float(data['cierre'])
            elif 'settlementPrice' in data and data['settlementPrice'] is not None:
                settlement = float(data['settlementPrice'])
            
            result['settlementPrice'] = settlement
            
            # Calcular variación porcentual
            if settlement > 0 and price > 0:
                variation = ((price - settlement) / settlement) * 100
                result['variationRate'] = round(variation, 2)
            
            # Obtener apertura
            if 'apertura' in data and data['apertura'] is not None:
                result['opening'] = float(data['apertura'])
            elif 'aperturaOperacion' in data and data['aperturaOperacion'] is not None:
                result['opening'] = float(data['aperturaOperacion'])
            
            # Obtener máximo del día
            if 'maximo' in data and data['maximo'] is not None:
                result['maxDay'] = float(data['maximo'])
            elif 'maxDay' in data and data['maxDay'] is not None:
                result['maxDay'] = float(data['maxDay'])
            
            # Obtener mínimo del día
            if 'minimo' in data and data['minimo'] is not None:
                result['minDay'] = float(data['minimo'])
            elif 'minDay' in data and data['minDay'] is not None:
                result['minDay'] = float(data['minDay'])
            
            # Obtener volumen
            if 'volumen' in data and data['volumen'] is not None:
                result['amount'] = float(data['volumen'])
            elif 'montoOperado' in data and data['montoOperado'] is not None:
                result['amount'] = float(data['montoOperado'])
            
            print(f"✅ Quote obtenido para {symbol}: ${price:,.2f}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión obteniendo quote de {symbol}: {e}")
            return {
                'price': 0.0,
                'settlementPrice': 0.0,
                'variationRate': 0.0,
                'amount': 0.0,
                'opening': 0.0,
                'maxDay': 0.0,
                'minDay': 0.0,
                'symbol': symbol,
                'error': f"Connection error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error obteniendo quote de {symbol}: {e}")
            return {
                'price': 0.0,
                'settlementPrice': 0.0,
                'variationRate': 0.0,
                'amount': 0.0,
                'opening': 0.0,
                'maxDay': 0.0,
                'minDay': 0.0,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_current_price(self, symbol: str, market: str = "bCBA") -> Optional[float]:
        """
        Obtiene el precio actual de un símbolo
        
        Args:
            symbol: Símbolo del activo (ej: GGAL)
            market: Mercado (default: bCBA - Bolsa de Comercio de Buenos Aires)
        
        Returns:
            float: Precio actual o None si hay error
        """
        quote = self.get_last_price(symbol, market)
        if quote and 'price' in quote:
            return quote['price']
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
        try:
            self._ensure_authenticated()
            
            url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica"
            params = {
                "fechaDesde": from_date.strftime("%Y-%m-%d"),
                "fechaHasta": to_date.strftime("%Y-%m-%d"),
                "ajustada": "true"
            }
            
            print(f"Obteniendo datos históricos para {symbol} desde {url}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convertir a DataFrame
            df = pd.DataFrame(data)
            
            if df.empty:
                print(f"⚠️ No hay datos históricos para {symbol}")
                return None
            
            # Mapear columnas
            if 'fechaHora' in df.columns:
                df['date'] = pd.to_datetime(df['fechaHora'])
            elif 'fecha' in df.columns:
                df['date'] = pd.to_datetime(df['fecha'])
            
            # Renombrar columnas
            column_mapping = {
                'apertura': 'open',
                'maximo': 'high',
                'minimo': 'low',
                'cierre': 'close',
                'volumen': 'volume'
            }
            
            for esp, eng in column_mapping.items():
                if esp in df.columns:
                    df[eng] = df[esp]
            
            # Seleccionar columnas necesarias
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            available_cols = [col for col in required_cols if col in df.columns]
            
            if not available_cols:
                print(f"⚠️ No se encontraron columnas válidas en datos históricos de {symbol}")
                return None
            
            df = df[available_cols]
            df = df.sort_values('date').reset_index(drop=True)
            
            print(f"✅ Datos históricos obtenidos para {symbol}: {len(df)} registros")
            return df
            
        except Exception as e:
            print(f"❌ Error obteniendo datos históricos de {symbol}: {e}")
            return None
    
    def get_portfolio(self) -> Optional[Dict]:
        """
        Obtiene el portafolio actual
        
        Returns:
            Dict con información del portafolio
        """
        try:
            self._ensure_authenticated()
            
            url = f"{self.base_url}/api/v2/portafolio/argentina"
            print(f"Obteniendo portafolio desde {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Portafolio obtenido exitosamente")
            return data
            
        except Exception as e:
            print(f"❌ Error obteniendo portafolio: {e}")
            return None
    
    def get_account_balance(self) -> Optional[float]:
        """
        Obtiene el saldo disponible en cuenta.
        """
        try:
            self._ensure_authenticated()
            
            url = f"{self.base_url}/api/v2/estadocuenta"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Intentar múltiples rutas
            if "cuentas" in data and isinstance(data["cuentas"], list):
                for cuenta in data["cuentas"]:
                    moneda = str(cuenta.get("moneda", "")).lower()
                    if "peso" in moneda or "ars" in moneda:
                        saldo = float(cuenta.get("disponible", 0))
                        if saldo > 0:
                            return saldo
                
                # Fallback: primera cuenta
                if len(data["cuentas"]) > 0:
                    return float(data["cuentas"][0].get("disponible", 0))
            
            if "saldos" in data:
                return float(data["saldos"].get("disponible", 0))
            
            if "disponible" in data:
                return float(data["disponible"])
            
            return 0.0
            
        except Exception as e:
            print(f"❌ Error obteniendo saldo: {e}")
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
            Dict con información de la orden
        """
        try:
            self._ensure_authenticated()
            
            # Obtener precio actual para validación
            current_price = self.get_current_price(symbol, market)
            if not current_price or current_price <= 0:
                return {
                    "success": False,
                    "error": f"Precio actual inválido para {symbol}: {current_price}"
                }
            
            # Construir URL según tipo de orden
            if side.lower() in ["compra", "buy"]:
                url = f"{self.base_url}/api/v2/operar/Comprar"
                operation_type = "compra"
            elif side.lower() in ["venta", "sell", "vender"]:
                url = f"{self.base_url}/api/v2/operar/Vender"
                operation_type = "venta"
            else:
                return {
                    "success": False,
                    "error": f"Tipo de operación inválido: {side}"
                }
            
            payload = {
                "mercado": market,
                "simbolo": symbol,
                "cantidad": quantity,
                "precio": None,  # Orden de mercado
                "plazo": "t2",  # Plazo de liquidación
                "validez": datetime.now().strftime("%Y-%m-%d")
            }
            
            print(f"Enviando orden de {operation_type} para {symbol}...")
            response = self.session.post(url, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            result["success"] = True
            result["operation"] = operation_type
            result["symbol"] = symbol
            result["quantity"] = quantity
            result["price"] = current_price
            
            print(f"✅ Orden de {operation_type} para {symbol} enviada exitosamente")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión en orden {side} de {symbol}: {e}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error colocando orden {side} de {symbol}: {e}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
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
