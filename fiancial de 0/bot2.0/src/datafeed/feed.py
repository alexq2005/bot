"""
Data Feed Interface
Abstracción para obtener datos de mercado
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
from datetime import datetime


class DataFeed(ABC):
    """
    Interfaz abstracta para feeds de datos de mercado
    
    Permite intercambiar entre:
    - Datos históricos (backtesting)
    - Datos en vivo (live trading)
    - Datos simulados (testing)
    """
    
    @abstractmethod
    def get_latest(self, symbol: str, lookback: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene los datos más recientes para un símbolo
        
        Args:
            symbol: Símbolo del activo
            lookback: Cantidad de períodos a retornar
        
        Returns:
            DataFrame con columnas: open, high, low, close, volume, timestamp
            None si no hay datos disponibles
        """
        pass
    
    @abstractmethod
    def is_market_open(self) -> bool:
        """
        Verifica si el mercado está abierto
        
        Returns:
            True si el mercado está abierto, False si está cerrado
        """
        pass
    
    def get_current_time(self) -> datetime:
        """
        Obtiene el tiempo actual del feed
        
        Returns:
            Timestamp actual
        """
        return datetime.now()


class LiveDataFeed(DataFeed):
    """
    Data feed para trading en vivo usando IOL Client
    """
    
    def __init__(self, iol_client):
        """
        Inicializa el feed con un cliente IOL
        
        Args:
            iol_client: Instancia de IOLClient
        """
        self.client = iol_client
    
    def get_latest(self, symbol: str, lookback: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos recientes del símbolo
        
        Args:
            symbol: Símbolo del activo
            lookback: Días de historia a obtener
        
        Returns:
            DataFrame con datos OHLCV
        """
        try:
            from datetime import timedelta
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=lookback)
            
            data = self.client.get_historical_data(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                market="bCBA"
            )
            
            if data is not None and len(data) > 0:
                # Asegurar que tenga las columnas requeridas
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                if all(col in data.columns for col in required_cols):
                    return data
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo datos para {symbol}: {e}")
            return None
    
    def is_market_open(self) -> bool:
        """
        Verifica si el mercado argentino está abierto
        
        Returns:
            True si está abierto (11:00-17:00 días hábiles)
        """
        from src.utils.market_manager import MarketManager
        
        market_manager = MarketManager()
        status = market_manager.get_market_status()
        
        return status.get('is_open', False)


class HistoricalDataFeed(DataFeed):
    """
    Data feed para backtesting con datos históricos
    """
    
    def __init__(self, historical_data: dict):
        """
        Inicializa con datos históricos pre-cargados
        
        Args:
            historical_data: Dict {symbol: DataFrame} con datos históricos
        """
        self.data = historical_data
        self.current_index = {}
    
    def get_latest(self, symbol: str, lookback: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos hasta el índice actual
        
        Args:
            symbol: Símbolo del activo
            lookback: Cantidad de barras a retornar
        
        Returns:
            DataFrame con datos hasta current_index
        """
        if symbol not in self.data:
            return None
        
        current_idx = self.current_index.get(symbol, len(self.data[symbol]) - 1)
        start_idx = max(0, current_idx - lookback + 1)
        
        return self.data[symbol].iloc[start_idx:current_idx + 1].copy()
    
    def advance(self, symbol: str, steps: int = 1):
        """
        Avanza el índice actual (para backtesting)
        
        Args:
            symbol: Símbolo a avanzar
            steps: Cantidad de pasos a avanzar
        """
        if symbol not in self.data:
            return
        
        current = self.current_index.get(symbol, 0)
        max_idx = len(self.data[symbol]) - 1
        self.current_index[symbol] = min(current + steps, max_idx)
    
    def is_market_open(self) -> bool:
        """
        En backtesting, siempre consideramos el mercado abierto
        
        Returns:
            True
        """
        return True
    
    def reset(self, symbol: str):
        """
        Reinicia el índice para un símbolo
        
        Args:
            symbol: Símbolo a reiniciar
        """
        self.current_index[symbol] = 0
