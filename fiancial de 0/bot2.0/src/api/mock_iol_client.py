"""
Mock IOL Client
Cliente simulado para testing seguro sin dinero real
VERSIÓN ROBUSTA
"""

import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class MockIOLClient:
    """Cliente simulado de IOL para testing"""
    
    def __init__(self, username: str, password: str, base_url: str, initial_capital: float = 1000000):
        self.username = username
        self.password = password
        self.base_url = base_url
        
        # Estado simulado
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, int] = {}
        self.avg_prices: Dict[str, float] = {}
        
        # Precios Base
        self.current_prices = {
            "GGAL": 1250.0,
            "YPFD": 2750.0,
            "PAMP": 950.0,
            "ALUA": 1100.0,
            "BMA": 4200.0,
            "TXAR": 7800.0,
            "COME": 850.0,
            "EDN": 520.0,
            "LOMA": 610.0,
            "AAPL": 235.0,
            "MSFT": 410.0,
            "GOOGL": 165.0,
            "AMZN": 200.0,
            "TSLA": 310.0,
            "AL30": 55.5,
            "AL35": 48.2
        }
        
        self.authenticated = False
    
    def authenticate(self) -> bool:
        self.authenticated = True
        return True
    
    def _ensure_authenticated(self):
        if not self.authenticated:
            self.authenticate()
    
    def _update_price(self, symbol: str):
        """Asegura que el precio existe y es válido"""
        if symbol not in self.current_prices:
            # Auto-inicializar nuevo símbolo
            price = random.uniform(500, 5000)
            self.current_prices[symbol] = price
            
        # Random walk
        curr = self.current_prices[symbol]
        curr *= (1 + random.normalvariate(0.0005, 0.02))
        
        # FORCE VALIDITY
        if curr < 0.1:
            curr = 10.0
        
        self.current_prices[symbol] = round(curr, 2)
    
    def get_current_price(self, symbol: str, market: str = "bCBA") -> Optional[float]:
        self._ensure_authenticated()
        self._update_price(symbol)
        return self.current_prices.get(symbol)
    
    def get_last_price(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """Obtiene última cotización con todos los campos requeridos"""
        self._ensure_authenticated()
        self._update_price(symbol)
        
        price = self.current_prices.get(symbol)
        
        if price:
            return {
                'price': price,
                'settlementPrice': price * 0.99,
                'variationRate': 1.0,
                'amount': 100000,
                'opening': price,
                'maxDay': price * 1.01,
                'minDay': price * 0.99
            }
        return None

    def place_market_order(self, symbol: str, quantity: int, side: str, market: str = "bCBA") -> Dict:
        """Colocar orden de mercado (compra/venta)"""
        self._ensure_authenticated()
        
        price = self.get_current_price(symbol)
        if not price or price <= 0:
            return {"success": False, "message": f"Precio inválido: {price}"}
        
        total = price * quantity
        
        # Normalizar side
        side = side.lower()
        if side in ["buy", "compra"]:
            if total > self.cash:
                return {"success": False, "message": f"Fondos insuficientes ({self.cash} vs {total})"}
            
            self.cash -= total
            old_q = self.positions.get(symbol, 0)
            self.positions[symbol] = old_q + quantity
            
            return {"success": True, "price": price, "message": "Compra exitosa"}
            
        elif side in ["sell", "venta", "vender"]:
            curr_q = self.positions.get(symbol, 0)
            if quantity > curr_q:
                return {"success": False, "message": f"Posición insuficiente ({curr_q})"}
            
            self.cash += total
            self.positions[symbol] = curr_q - quantity
            return {"success": True, "price": price, "message": "Venta exitosa"}
            
        return {"success": False, "message": f"Operación desconocida: {side}"}

    def get_portfolio(self) -> Dict:
        """Retorna portafolio simple"""
        assets = []
        for s, q in self.positions.items():
            if q > 0:
                p = self.current_prices.get(s, 0)
                assets.append({
                    "titulo": {"simbolo": s},
                    "cantidad": q,
                    "valorActual": p * q,
                    "gananciaPerdida": 0
                })
        return {"activos": assets}
    
    def get_account_balance(self) -> float:
        """Returns the current cash balance"""
        return self.cash
    
    def get_position(self, symbol: str) -> int:
        """Returns the current position quantity for a symbol"""
        return self.positions.get(symbol, 0)
    
    def buy(self, symbol: str, quantity: int) -> bool:
        """Execute a buy order"""
        result = self.place_market_order(symbol, quantity, "buy")
        return result.get("success", False)
    
    def sell(self, symbol: str, quantity: int) -> bool:
        """Execute a sell order"""
        result = self.place_market_order(symbol, quantity, "sell")
        return result.get("success", False)
    
    def get_historical_data(self, symbol: str, from_date, to_date) -> pd.DataFrame:
        """Generate synthetic historical data for backtesting"""
        self._ensure_authenticated()
        
        days = (to_date - from_date).days
        if days <= 0:
            days = 100
        
        dates = pd.date_range(start=from_date, periods=days, freq='D')
        
        # Get or initialize base price
        if symbol not in self.current_prices:
            self.current_prices[symbol] = random.uniform(500, 5000)
        
        base_price = self.current_prices[symbol]
        
        # Generate realistic price series using random walk
        prices = [base_price]
        for _ in range(days - 1):
            change = np.random.normal(0.0005, 0.02)
            new_price = prices[-1] * (1 + change)
            new_price = max(new_price, 1.0)  # Ensure positive price
            prices.append(new_price)
        
        # Generate OHLCV data
        df = pd.DataFrame({
            'date': dates,
            'open': [p * (1 + np.random.uniform(-0.005, 0.005)) for p in prices],
            'high': [p * (1 + np.random.uniform(0.005, 0.02)) for p in prices],
            'low': [p * (1 - np.random.uniform(0.005, 0.02)) for p in prices],
            'close': prices,
            'volume': [random.randint(100000, 1000000) for _ in prices]
        })
        
        # Set date as index
        df.set_index('date', inplace=True)
        
        return df
    
    def get_performance(self) -> dict:
        """Get portfolio performance metrics"""
        self._ensure_authenticated()
        
        # Calculate total invested value (only for non-zero positions)
        invested = sum(
            qty * self.current_prices.get(symbol, 0) 
            for symbol, qty in self.positions.items()
            if qty > 0
        )
        
        current_value = self.cash + invested
        initial_capital = getattr(self, 'initial_capital', 1000000)
        
        return {
            'initial_capital': initial_capital,
            'current_value': current_value,
            'total_return': current_value - initial_capital,
            'total_return_pct': ((current_value - initial_capital) / initial_capital) * 100,
            'cash': self.cash,
            'invested': invested,
            'positions': len([s for s, q in self.positions.items() if q > 0])
        }
