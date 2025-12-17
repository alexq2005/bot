"""
Order Domain Object
Orden ejecutada en el broker
"""

from dataclasses import dataclass
from typing import Literal, Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Estados posibles de una orden"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass
class Order:
    """
    Orden ejecutada o en proceso de ejecución
    
    Attributes:
        id: ID único de la orden
        symbol: Símbolo del activo
        side: Lado de la operación ("BUY" o "SELL")
        size: Tamaño de la orden
        entry_price: Precio de entrada
        timestamp: Momento de creación de la orden
        status: Estado actual de la orden
        filled_size: Cantidad ejecutada
        filled_price: Precio promedio de ejecución
        stop_loss: Stop loss asociado (opcional)
        take_profit: Take profit asociado (opcional)
        commission: Comisión pagada
        strategy_name: Estrategia que generó la orden
    """
    id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    size: float
    entry_price: float
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    filled_size: float = 0.0
    filled_price: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    commission: float = 0.0
    strategy_name: str = "Unknown"
    
    def __post_init__(self):
        """Validaciones de la orden"""
        if self.size <= 0:
            raise ValueError(f"Size debe ser positivo, recibido: {self.size}")
        if self.entry_price <= 0:
            raise ValueError(f"Entry price debe ser positivo, recibido: {self.entry_price}")
        if self.filled_size < 0:
            raise ValueError(f"Filled size no puede ser negativo, recibido: {self.filled_size}")
        if self.filled_size > self.size:
            raise ValueError(f"Filled size no puede ser mayor que size. Filled: {self.filled_size}, Size: {self.size}")
        if self.commission < 0:
            raise ValueError(f"Commission no puede ser negativa, recibido: {self.commission}")
    
    @property
    def is_filled(self) -> bool:
        """Indica si la orden está completamente ejecutada"""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_pending(self) -> bool:
        """Indica si la orden está pendiente"""
        return self.status == OrderStatus.PENDING
    
    @property
    def is_active(self) -> bool:
        """Indica si la orden está activa (pending o partially filled)"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
    
    @property
    def fill_percentage(self) -> float:
        """Porcentaje de la orden ejecutado"""
        return (self.filled_size / self.size * 100) if self.size > 0 else 0.0
    
    @property
    def total_cost(self) -> float:
        """Costo total de la orden (precio * tamaño + comisión)"""
        return (self.filled_price * self.filled_size) + self.commission
    
    def update_fill(self, filled_size: float, filled_price: float, commission: float = 0.0):
        """
        Actualiza el estado de ejecución de la orden
        
        Args:
            filled_size: Cantidad ejecutada
            filled_price: Precio de ejecución
            commission: Comisión de la ejecución
        """
        self.filled_size = filled_size
        self.filled_price = filled_price
        self.commission += commission
        
        # Actualizar estado
        if self.filled_size >= self.size:
            self.status = OrderStatus.FILLED
        elif self.filled_size > 0:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self):
        """Cancela la orden"""
        if self.is_active:
            self.status = OrderStatus.CANCELLED
    
    def to_dict(self) -> dict:
        """Convierte la orden a diccionario para logging/serialización"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "size": self.size,
            "entry_price": self.entry_price,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "filled_size": self.filled_size,
            "filled_price": self.filled_price,
            "fill_percentage": self.fill_percentage,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "commission": self.commission,
            "total_cost": self.total_cost,
            "strategy_name": self.strategy_name
        }
