"""
Base Strategy Interface
Interfaz abstracta para todas las estrategias de trading
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from ..domain.signal import Signal


class BaseStrategy(ABC):
    """
    Interfaz base para todas las estrategias de trading
    
    Todas las estrategias deben heredar de esta clase e implementar
    los métodos abstractos. Esto permite:
    - Plug & play de estrategias
    - Backtesting limpio
    - Múltiples estrategias en paralelo
    - Fácil integración de ML
    """
    
    def __init__(self, name: str = None):
        """
        Inicializa la estrategia
        
        Args:
            name: Nombre de la estrategia (opcional)
        """
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def generate_signal(self, market_data: pd.DataFrame) -> Optional[Signal]:
        """
        Genera una señal de trading basada en los datos de mercado
        
        Args:
            market_data: DataFrame con datos de mercado e indicadores calculados
                        Debe contener al menos: open, high, low, close, volume
        
        Returns:
            Signal si hay una oportunidad de trading, None si no hay señal
        
        Raises:
            ValueError: Si market_data no tiene las columnas requeridas
        """
        pass
    
    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """
        Retorna la lista de indicadores técnicos requeridos por la estrategia
        
        Returns:
            Lista de nombres de indicadores (ej: ['rsi', 'macd', 'bb_upper'])
        
        Example:
            >>> strategy.get_required_indicators()
            ['rsi_14', 'sma_50', 'sma_200', 'atr_14']
        """
        pass
    
    def get_name(self) -> str:
        """
        Retorna el nombre de la estrategia
        
        Returns:
            Nombre de la estrategia
        """
        return self.name
    
    def validate_market_data(self, market_data: pd.DataFrame) -> bool:
        """
        Valida que market_data tenga las columnas mínimas requeridas
        
        Args:
            market_data: DataFrame a validar
        
        Returns:
            True si es válido, False si no
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in market_data.columns for col in required_columns)
    
    def validate_indicators(self, market_data: pd.DataFrame) -> bool:
        """
        Valida que market_data tenga todos los indicadores requeridos
        
        Args:
            market_data: DataFrame a validar
        
        Returns:
            True si tiene todos los indicadores, False si falta alguno
        """
        required_indicators = self.get_required_indicators()
        return all(ind in market_data.columns for ind in required_indicators)
    
    def __str__(self) -> str:
        """Representación en string de la estrategia"""
        return f"{self.name} Strategy"
    
    def __repr__(self) -> str:
        """Representación técnica de la estrategia"""
        return f"<{self.__class__.__name__}(name='{self.name}')>"
