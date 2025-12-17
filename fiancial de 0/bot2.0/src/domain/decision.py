"""
Order Decision Domain Object
Decisión de riesgo sobre una señal de trading
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OrderDecision:
    """
    Decisión del Risk Manager sobre una señal de trading
    
    Attributes:
        approved: Si la orden fue aprobada o rechazada
        symbol: Símbolo del activo
        side: Lado de la operación ("BUY" o "SELL")
        size: Tamaño de la posición (cantidad de acciones/contratos)
        reason: Razón de la decisión (aprobación o rechazo)
        risk_amount: Monto de capital en riesgo
        entry_price: Precio de entrada (opcional)
        stop_loss: Stop loss calculado (opcional)
        take_profit: Take profit calculado (opcional)
    """
    approved: bool
    symbol: str
    side: str
    size: float
    reason: str
    risk_amount: float = 0.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    def __post_init__(self):
        """Validaciones de la decisión"""
        # Si está aprobada, el size debe ser positivo
        if self.approved and self.size <= 0:
            raise ValueError(f"Decisión aprobada debe tener size > 0, recibido: {self.size}")
        
        # Si está rechazada, el size debe ser 0
        if not self.approved and self.size != 0:
            raise ValueError(f"Decisión rechazada debe tener size = 0, recibido: {self.size}")
        
        # Risk amount debe ser no negativo
        if self.risk_amount < 0:
            raise ValueError(f"Risk amount no puede ser negativo, recibido: {self.risk_amount}")
    
    @property
    def is_approved(self) -> bool:
        """Alias para approved"""
        return self.approved
    
    @property
    def is_rejected(self) -> bool:
        """Indica si la decisión fue rechazada"""
        return not self.approved
    
    def to_dict(self) -> dict:
        """Convierte la decisión a diccionario para logging/serialización"""
        return {
            "approved": self.approved,
            "symbol": self.symbol,
            "side": self.side,
            "size": self.size,
            "reason": self.reason,
            "risk_amount": self.risk_amount,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit
        }
