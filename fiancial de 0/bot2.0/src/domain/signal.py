"""
Domain Objects - Trading System
Objetos de dominio con tipado fuerte para eliminar uso de dict
"""

from dataclasses import dataclass
from typing import Literal
from datetime import datetime


@dataclass(frozen=True)
class Signal:
    """
    Señal de trading generada por una estrategia
    
    Attributes:
        symbol: Símbolo del activo (ej: "GGAL", "YPFD")
        side: Lado de la operación ("BUY" o "SELL")
        entry: Precio de entrada sugerido
        stop_loss: Precio de stop loss
        take_profit: Precio de take profit
        confidence: Nivel de confianza de la señal (0.0 a 1.0)
        timestamp: Momento de generación de la señal
        strategy_name: Nombre de la estrategia que generó la señal
    """
    symbol: str
    side: Literal["BUY", "SELL"]
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float
    timestamp: datetime
    strategy_name: str = "Unknown"
    
    def __post_init__(self):
        """Validaciones de la señal"""
        # Validar confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence debe estar entre 0.0 y 1.0, recibido: {self.confidence}")
        
        # Validar precios positivos
        if self.entry <= 0:
            raise ValueError(f"Entry price debe ser positivo, recibido: {self.entry}")
        if self.stop_loss <= 0:
            raise ValueError(f"Stop loss debe ser positivo, recibido: {self.stop_loss}")
        if self.take_profit <= 0:
            raise ValueError(f"Take profit debe ser positivo, recibido: {self.take_profit}")
        
        # Validar lógica de stop loss y take profit
        if self.side == "BUY":
            if self.stop_loss >= self.entry:
                raise ValueError(f"Para BUY, stop_loss debe ser < entry. Stop: {self.stop_loss}, Entry: {self.entry}")
            if self.take_profit <= self.entry:
                raise ValueError(f"Para BUY, take_profit debe ser > entry. TP: {self.take_profit}, Entry: {self.entry}")
        else:  # SELL
            if self.stop_loss <= self.entry:
                raise ValueError(f"Para SELL, stop_loss debe ser > entry. Stop: {self.stop_loss}, Entry: {self.entry}")
            if self.take_profit >= self.entry:
                raise ValueError(f"Para SELL, take_profit debe ser < entry. TP: {self.take_profit}, Entry: {self.entry}")
    
    @property
    def stop_distance(self) -> float:
        """Distancia al stop loss en valor absoluto"""
        return abs(self.entry - self.stop_loss)
    
    @property
    def profit_distance(self) -> float:
        """Distancia al take profit en valor absoluto"""
        return abs(self.take_profit - self.entry)
    
    @property
    def risk_reward_ratio(self) -> float:
        """Ratio riesgo/recompensa"""
        return self.profit_distance / self.stop_distance if self.stop_distance > 0 else 0.0
    
    def to_dict(self) -> dict:
        """Convierte la señal a diccionario para logging/serialización"""
        return {
            "symbol": self.symbol,
            "side": self.side,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "strategy_name": self.strategy_name,
            "stop_distance": self.stop_distance,
            "profit_distance": self.profit_distance,
            "risk_reward_ratio": self.risk_reward_ratio
        }
