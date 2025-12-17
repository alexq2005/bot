"""
Paper IOL Client
Cliente de paper trading: usa precios reales pero simula ejecución
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class PaperIOLClient:
    """
    Cliente de Paper Trading
    
    Combina lo mejor de ambos mundos:
    - Precios REALES de IOL
    - Ejecución SIMULADA (sin riesgo)
    """
    
    def __init__(self, username: str, password: str, base_url: str, initial_capital: float = 1000000):
        """
        Inicializa el cliente de paper trading
        
        Args:
            username: Usuario de IOL (para obtener precios reales)
            password: Contraseña de IOL
            base_url: URL base de la API
            initial_capital: Capital inicial simulado
        """
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        
        # Estado simulado
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, int] = {}
        self.avg_prices: Dict[str, float] = {}
        
        # Tracking de slippage realista
        self.slippage_pct = 0.0005  # 0.05% slippage promedio
        
        # Token de autenticación
        self.token = None
        self.token_expiry = None
        self.session = requests.Session()
        
        self.authenticated = False
        
        # Usar mensajes sin emojis para evitar problemas de codificación en Windows
        print("[PAPER TRADING] Modo activado")
        print(f"   - Precios: REALES (IOL API)")
        print(f"   - Ejecucion: SIMULADA")
        print(f"   - Capital: ${initial_capital:,.2f}")
    
    def authenticate(self) -> bool:
        """Autentica con la API de IOL para obtener precios reales"""
        try:
            url = f"{self.base_url}/token"
            payload = {
                "username": self.username,
                "password": self.password,
                "grant_type": "password"
            }
            
            response = self.session.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                self.authenticated = True
                print("[OK] Paper Trading: Autenticado con IOL (solo lectura)")
                return True
            else:
                # Si falla la autenticación, usar modo mock
                print("[WARNING] Paper Trading: No se pudo autenticar con IOL, usando precios simulados")
                self.authenticated = False
                return False
                
        except Exception as e:
            print(f"[ERROR] Paper Trading: Error de autenticacion: {e}")
            print("[WARNING] Usando precios simulados")
            self.authenticated = False
            return False
    
    def _ensure_authenticated(self):
        """Verifica autenticación"""
        if not self.authenticated or (self.token_expiry and datetime.now() >= self.token_expiry):
            self.authenticate()
    
    def get_current_price(self, symbol: str, market: str = "bCBA") -> Optional[float]:
        """
        Obtiene precio REAL de IOL (o simulado si no hay conexión)
        
        Args:
            symbol: Símbolo del activo
            market: Mercado
        
        Returns:
            float: Precio actual
        """
        self._ensure_authenticated()
        
        if self.authenticated:
            try:
                url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    price = data.get("ultimoPrecio") or data.get("puntas", {}).get("precioCompra")
                    
                    if price:
                        return float(price)
            except Exception as e:
                print(f"[WARNING] Error obteniendo precio real de {symbol}: {e}")
        
        # Fallback: precio simulado
        return self._get_simulated_price(symbol)
    
    def get_last_price(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Obtiene quote completo del símbolo (compatible con IOLClient)
        
        Args:
            symbol: Símbolo del activo
            market: Mercado
        
        Returns:
            Dict con: price, settlementPrice, variationRate, amount, opening, maxDay, minDay
        """
        self._ensure_authenticated()
        
        if self.authenticated:
            try:
                url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extraer precio
                    price = float(
                        data.get("ultimoPrecio")
                        or data.get("precio")
                        or data.get("puntas", {}).get("precioCompra")
                        or 0
                    )
                    
                    if price > 0:
                        # Precio de cierre anterior
                        settlement = float(
                            data.get("precioAnterior")
                            or data.get("cierre")
                            or price * 0.99
                        )
                        
                        # Calcular variación
                        variation_rate = 0
                        if settlement > 0:
                            variation_rate = ((price - settlement) / settlement) * 100
                        
                        # Apertura
                        opening = float(
                            data.get("apertura")
                            or settlement
                            or price
                        )
                        
                        # Máximo y mínimo del día
                        max_day = float(
                            data.get("maximo")
                            or price * 1.01
                        )
                        min_day = float(
                            data.get("minimo")
                            or price * 0.99
                        )
                        
                        # Volumen
                        amount = int(
                            data.get("volumen")
                            or data.get("cantidadOperada")
                            or 100000
                        )
                        
                        return {
                            'price': price,
                            'settlementPrice': settlement,
                            'variationRate': variation_rate,
                            'amount': amount,
                            'opening': opening,
                            'maxDay': max_day,
                            'minDay': min_day
                        }
            except Exception as e:
                print(f"[WARNING] Error obteniendo quote de {symbol}: {e}")
        
        # Fallback: precio simulado
        simulated_price = self._get_simulated_price(symbol)
        return {
            'price': simulated_price,
            'settlementPrice': simulated_price * 0.99,
            'variationRate': 1.0,
            'amount': 100000,
            'opening': simulated_price,
            'maxDay': simulated_price * 1.01,
            'minDay': simulated_price * 0.99
        }
    
    def _get_simulated_price(self, symbol: str) -> float:
        """Genera precio simulado si no hay conexión a IOL"""
        # Precios base simulados
        base_prices = {
            "GGAL": 3500.0,
            "YPFD": 25000.0,
            "PAMP": 8500.0,
            "ALUA": 1200.0,
            "BMA": 5800.0
        }
        
        base = base_prices.get(symbol, 1000.0)
        # Agregar variación aleatoria
        variation = np.random.normal(0, 0.02)  # 2% volatilidad
        return base * (1 + variation)
    
    def get_historical_data(
        self, 
        symbol: str, 
        from_date: datetime, 
        to_date: datetime,
        market: str = "bCBA"
    ) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos REALES de IOL (o simulados)
        
        Args:
            symbol: Símbolo
            from_date: Fecha inicial
            to_date: Fecha final
            market: Mercado
        
        Returns:
            DataFrame con OHLCV
        """
        self._ensure_authenticated()
        
        if self.authenticated:
            try:
                url = f"{self.base_url}/api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica"
                params = {
                    "fechaDesde": from_date.strftime("%Y-%m-%d"),
                    "fechaHasta": to_date.strftime("%Y-%m-%d"),
                    "ajustada": "true"
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
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
                print(f"[WARNING] Error obteniendo datos historicos de {symbol}: {e}")
        
        # Fallback: datos simulados
        return self._get_simulated_historical_data(symbol, from_date, to_date)
    
    def _get_simulated_historical_data(self, symbol: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
        """Genera datos históricos simulados"""
        days = (to_date - from_date).days
        dates = pd.date_range(start=from_date, end=to_date, freq='D')
        
        base_price = self._get_simulated_price(symbol)
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = base_price * np.exp(np.cumsum(returns))
        
        data = []
        for i, date in enumerate(dates):
            close = prices[i]
            open_price = close * (1 + np.random.normal(0, 0.005))
            high = max(open_price, close) * (1 + abs(np.random.normal(0, 0.01)))
            low = min(open_price, close) * (1 - abs(np.random.normal(0, 0.01)))
            volume = int(np.random.lognormal(15, 1))
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def get_portfolio(self) -> Optional[Dict]:
        """Obtiene portafolio SIMULADO"""
        activos = []
        for symbol, quantity in self.positions.items():
            if quantity > 0:
                current_price = self.get_current_price(symbol)
                avg_price = self.avg_prices.get(symbol, current_price)
                
                activos.append({
                    "titulo": {"simbolo": symbol},
                    "cantidad": quantity,
                    "precioPromedio": avg_price,
                    "valorActual": current_price * quantity,
                    "gananciaPerdida": (current_price - avg_price) * quantity
                })
        
        total_invertido = sum(a["valorActual"] for a in activos)
        
        return {
            "activos": activos,
            "totalInvertido": total_invertido,
            "efectivo": self.cash,
            "valorTotal": total_invertido + self.cash
        }
    
    def get_account_balance(self) -> Optional[float]:
        """Obtiene saldo SIMULADO"""
        return self.cash
    
    def place_market_order(
        self, 
        symbol: str, 
        quantity: int, 
        side: str,
        market: str = "bCBA"
    ) -> Optional[Dict]:
        """
        Simula colocación de orden con precio REAL y slippage realista
        
        Args:
            symbol: Símbolo
            quantity: Cantidad
            side: 'compra' o 'venta'
            market: Mercado
        
        Returns:
            Dict con información de la orden simulada
        """
        # Obtener precio REAL
        price = self.get_current_price(symbol)
        if not price:
            return None
        
        # Aplicar slippage realista
        if side == "compra":
            execution_price = price * (1 + self.slippage_pct)
        else:
            execution_price = price * (1 - self.slippage_pct)
        
        total_value = quantity * execution_price
        
        if side == "compra":
            if total_value > self.cash:
                print(f"✗ Paper Trading: Fondos insuficientes")
                return None
            
            self.cash -= total_value
            current_qty = self.positions.get(symbol, 0)
            current_avg = self.avg_prices.get(symbol, 0)
            
            new_avg = ((current_avg * current_qty) + (execution_price * quantity)) / (current_qty + quantity)
            
            self.positions[symbol] = current_qty + quantity
            self.avg_prices[symbol] = new_avg
            
            print(f"[OK] Paper Trading: COMPRA {quantity} {symbol} @ ${execution_price:,.2f} (precio real + slippage)")
            
        elif side == "venta":
            current_qty = self.positions.get(symbol, 0)
            if quantity > current_qty:
                print(f"[ERROR] Paper Trading: Posicion insuficiente")
                return None
            
            self.cash += total_value
            self.positions[symbol] = current_qty - quantity
            
            if self.positions[symbol] == 0:
                del self.positions[symbol]
                if symbol in self.avg_prices:
                    del self.avg_prices[symbol]
            
            print(f"[OK] Paper Trading: VENTA {quantity} {symbol} @ ${execution_price:,.2f} (precio real - slippage)")
        
        return {
            "numero": np.random.randint(100000, 999999),
            "estado": "terminada",
            "simbolo": symbol,
            "cantidad": quantity,
            "precio": execution_price,
            "monto": total_value,
            "mode": "PAPER"
        }
    
    def buy(self, symbol: str, quantity: int) -> Optional[Dict]:
        """Compra simulada con precio real"""
        return self.place_market_order(symbol, quantity, "compra")
    
    def sell(self, symbol: str, quantity: int) -> Optional[Dict]:
        """Venta simulada con precio real"""
        return self.place_market_order(symbol, quantity, "venta")
    
    def get_position(self, symbol: str) -> Optional[int]:
        """Obtiene posición simulada"""
        return self.positions.get(symbol, 0)
    
    def get_total_portfolio_value(self) -> float:
        """Calcula valor total del portafolio"""
        portfolio = self.get_portfolio()
        if portfolio:
            return portfolio["valorTotal"]
        return self.cash
    
    def get_performance(self) -> Dict:
        """Obtiene métricas de rendimiento"""
        current_value = self.get_total_portfolio_value()
        total_return = current_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        return {
            "initial_capital": self.initial_capital,
            "current_value": current_value,
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "cash": self.cash,
            "positions": len(self.positions),
            "mode": "PAPER"
        }
