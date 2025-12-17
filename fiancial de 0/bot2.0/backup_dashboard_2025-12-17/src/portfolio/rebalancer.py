"""
Portfolio Rebalancer
Rebalanceo automático del portafolio para mantener diversificación
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


class PortfolioRebalancer:
    """Rebalanceador de portafolio"""
    
    def __init__(
        self,
        target_allocations: Dict[str, float] = None,
        rebalance_threshold: float = 5.0,
        rebalance_frequency_days: int = 7
    ):
        """
        Inicializa el rebalanceador
        
        Args:
            target_allocations: Dict {symbol: target_pct} (ej: {"GGAL": 20.0, "YPFD": 20.0})
            rebalance_threshold: Umbral de desviación para rebalancear (%)
            rebalance_frequency_days: Frecuencia mínima de rebalanceo (días)
        """
        self.target_allocations = target_allocations or {}
        self.rebalance_threshold = rebalance_threshold
        self.rebalance_frequency_days = rebalance_frequency_days
        self.last_rebalance = None
    
    def set_target_allocations(self, allocations: Dict[str, float]):
        """
        Establece asignaciones objetivo
        
        Args:
            allocations: Dict {symbol: target_pct}
        """
        # Normalizar a 100%
        total = sum(allocations.values())
        self.target_allocations = {
            symbol: (pct / total) * 100 
            for symbol, pct in allocations.items()
        }
    
    def calculate_current_allocations(
        self,
        positions: Dict[str, float],
        total_value: float
    ) -> Dict[str, float]:
        """
        Calcula asignaciones actuales
        
        Args:
            positions: Dict {symbol: position_value}
            total_value: Valor total del portafolio
        
        Returns:
            Dict {symbol: current_pct}
        """
        if total_value == 0:
            return {}
        
        return {
            symbol: (value / total_value) * 100
            for symbol, value in positions.items()
        }
    
    def calculate_deviations(
        self,
        current_allocations: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calcula desviaciones de las asignaciones objetivo
        
        Args:
            current_allocations: Asignaciones actuales
        
        Returns:
            Dict {symbol: deviation_pct}
        """
        deviations = {}
        
        for symbol, target_pct in self.target_allocations.items():
            current_pct = current_allocations.get(symbol, 0)
            deviations[symbol] = current_pct - target_pct
        
        return deviations
    
    def needs_rebalancing(
        self,
        current_allocations: Dict[str, float],
        force: bool = False
    ) -> bool:
        """
        Determina si se necesita rebalancear
        
        Args:
            current_allocations: Asignaciones actuales
            force: Forzar rebalanceo ignorando frecuencia
        
        Returns:
            bool: True si se necesita rebalancear
        """
        # Verificar frecuencia
        if not force and self.last_rebalance:
            days_since_last = (datetime.now() - self.last_rebalance).days
            if days_since_last < self.rebalance_frequency_days:
                return False
        
        # Calcular desviaciones
        deviations = self.calculate_deviations(current_allocations)
        
        # Verificar si alguna desviación excede el umbral
        max_deviation = max(abs(d) for d in deviations.values()) if deviations else 0
        
        return max_deviation > self.rebalance_threshold
    
    def generate_rebalance_orders(
        self,
        positions: Dict[str, float],
        prices: Dict[str, float],
        total_value: float,
        cash: float
    ) -> List[Dict]:
        """
        Genera órdenes de rebalanceo
        
        Args:
            positions: Dict {symbol: current_value}
            prices: Dict {symbol: current_price}
            total_value: Valor total del portafolio
            cash: Efectivo disponible
        
        Returns:
            List de órdenes [{symbol, action, quantity, reason}]
        """
        orders = []
        
        # Calcular asignaciones actuales
        current_allocations = self.calculate_current_allocations(positions, total_value)
        
        # Calcular valores objetivo
        target_values = {
            symbol: (target_pct / 100) * total_value
            for symbol, target_pct in self.target_allocations.items()
        }
        
        # Generar órdenes
        for symbol, target_value in target_values.items():
            current_value = positions.get(symbol, 0)
            difference = target_value - current_value
            
            # Solo rebalancear si la diferencia es significativa
            if abs(difference) < total_value * 0.01:  # 1% del portafolio
                continue
            
            price = prices.get(symbol)
            if not price:
                continue
            
            if difference > 0:
                # Necesitamos comprar
                quantity = int(difference / price)
                if quantity > 0:
                    orders.append({
                        "symbol": symbol,
                        "action": "BUY",
                        "quantity": quantity,
                        "price": price,
                        "reason": f"Rebalanceo: {current_allocations.get(symbol, 0):.1f}% → {self.target_allocations[symbol]:.1f}%"
                    })
            else:
                # Necesitamos vender
                quantity = int(abs(difference) / price)
                current_qty = int(current_value / price)
                quantity = min(quantity, current_qty)  # No vender más de lo que tenemos
                
                if quantity > 0:
                    orders.append({
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": quantity,
                        "price": price,
                        "reason": f"Rebalanceo: {current_allocations.get(symbol, 0):.1f}% → {self.target_allocations[symbol]:.1f}%"
                    })
        
        return orders
    
    def execute_rebalance(
        self,
        positions: Dict[str, float],
        prices: Dict[str, float],
        total_value: float,
        cash: float
    ) -> Dict:
        """
        Ejecuta rebalanceo completo
        
        Args:
            positions: Posiciones actuales
            prices: Precios actuales
            total_value: Valor total
            cash: Efectivo
        
        Returns:
            Dict con órdenes y estadísticas
        """
        # Generar órdenes
        orders = self.generate_rebalance_orders(positions, prices, total_value, cash)
        
        # Actualizar última fecha de rebalanceo
        self.last_rebalance = datetime.now()
        
        # Calcular estadísticas
        current_allocations = self.calculate_current_allocations(positions, total_value)
        deviations = self.calculate_deviations(current_allocations)
        
        return {
            "orders": orders,
            "num_orders": len(orders),
            "current_allocations": current_allocations,
            "target_allocations": self.target_allocations,
            "deviations": deviations,
            "timestamp": self.last_rebalance
        }
    
    def get_rebalance_summary(
        self,
        positions: Dict[str, float],
        total_value: float
    ) -> Dict:
        """
        Obtiene resumen del estado de rebalanceo
        
        Args:
            positions: Posiciones actuales
            total_value: Valor total
        
        Returns:
            Dict con resumen
        """
        current_allocations = self.calculate_current_allocations(positions, total_value)
        deviations = self.calculate_deviations(current_allocations)
        needs_rebalancing = self.needs_rebalancing(current_allocations)
        
        max_deviation = max(abs(d) for d in deviations.values()) if deviations else 0
        
        return {
            "needs_rebalancing": needs_rebalancing,
            "max_deviation": max_deviation,
            "current_allocations": current_allocations,
            "target_allocations": self.target_allocations,
            "deviations": deviations,
            "last_rebalance": self.last_rebalance,
            "days_since_last": (datetime.now() - self.last_rebalance).days if self.last_rebalance else None
        }
