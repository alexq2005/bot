"""
Order Executor
Componente responsable de ejecutar órdenes en el broker
"""

from typing import Optional
from datetime import datetime
import uuid

from ..domain.decision import OrderDecision
from ..domain.order import Order, OrderStatus


class OrderExecutor:
    """
    Ejecutor de órdenes que abstrae la comunicación con el broker
    
    Responsabilidades:
    - Enviar órdenes al broker
    - Tracking de órdenes activas
    - Actualización de estado de órdenes
    - Cálculo de comisiones
    """
    
    def __init__(self, broker_client, commission_rate: float = 0.0004):
        """
        Inicializa el executor
        
        Args:
            broker_client: Cliente del broker (IOLClient, MockIOLClient, etc.)
            commission_rate: Tasa de comisión (0.0004 = 0.04%)
        """
        self.broker = broker_client
        self.commission_rate = commission_rate
        self.active_orders = {}
        self.completed_orders = {}
    
    def execute(self, decision: OrderDecision) -> Optional[Order]:
        """
        Ejecuta una decisión de trading
        
        Args:
            decision: OrderDecision aprobada por el risk manager
        
        Returns:
            Order si se ejecutó exitosamente, None si falló
        """
        if not decision.approved:
            print(f"❌ No se puede ejecutar decisión rechazada: {decision.reason}")
            return None
        
        try:
            # Generar ID único para la orden
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Crear orden
            order = Order(
                id=order_id,
                symbol=decision.symbol,
                side=decision.side,
                size=decision.size,
                entry_price=decision.entry_price or 0.0,
                timestamp=datetime.now(),
                status=OrderStatus.PENDING,
                stop_loss=decision.stop_loss,
                take_profit=decision.take_profit
            )
            
            # Enviar al broker
            result = self.broker.place_market_order(
                symbol=decision.symbol,
                quantity=int(decision.size),
                side=decision.side.lower(),
                market="bCBA"
            )
            
            if result and isinstance(result, dict):
                if result.get("success"):
                    # Orden ejecutada exitosamente
                    filled_price = result.get("price", decision.entry_price)
                    commission = filled_price * decision.size * self.commission_rate
                    
                    order.update_fill(
                        filled_size=decision.size,
                        filled_price=filled_price,
                        commission=commission
                    )
                    
                    # Guardar orden
                    self.completed_orders[order_id] = order
                    
                    print(f"✅ Orden ejecutada: {order.symbol} {order.side} {order.size} @ ${filled_price:.2f}")
                    
                    return order
                else:
                    # Orden rechazada por el broker
                    order.status = OrderStatus.REJECTED
                    self.completed_orders[order_id] = order
                    
                    print(f"❌ Orden rechazada por broker: {result.get('error', 'Unknown')}")
                    return None
            else:
                # Error en la respuesta
                order.status = OrderStatus.REJECTED
                self.completed_orders[order_id] = order
                
                print(f"❌ Error ejecutando orden: respuesta inválida del broker")
                return None
                
        except Exception as e:
            print(f"❌ Error ejecutando orden: {e}")
            return None
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Obtiene una orden por su ID
        
        Args:
            order_id: ID de la orden
        
        Returns:
            Order si existe, None si no
        """
        if order_id in self.active_orders:
            return self.active_orders[order_id]
        if order_id in self.completed_orders:
            return self.completed_orders[order_id]
        return None
    
    def get_active_orders(self) -> list:
        """
        Obtiene todas las órdenes activas
        
        Returns:
            Lista de órdenes activas
        """
        return list(self.active_orders.values())
    
    def get_completed_orders(self) -> list:
        """
        Obtiene todas las órdenes completadas
        
        Returns:
            Lista de órdenes completadas
        """
        return list(self.completed_orders.values())
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancela una orden activa
        
        Args:
            order_id: ID de la orden a cancelar
        
        Returns:
            True si se canceló, False si no
        """
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order.cancel()
            
            # Mover a completadas
            self.completed_orders[order_id] = order
            del self.active_orders[order_id]
            
            print(f"🚫 Orden cancelada: {order_id}")
            return True
        
        return False
    
    def get_total_exposure(self) -> float:
        """
        Calcula la exposición total de órdenes activas
        
        Returns:
            Valor total de posiciones abiertas
        """
        total = 0.0
        for order in self.active_orders.values():
            total += order.entry_price * order.size
        return total
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del executor
        
        Returns:
            Diccionario con estadísticas
        """
        total_orders = len(self.active_orders) + len(self.completed_orders)
        filled_orders = len([o for o in self.completed_orders.values() if o.is_filled])
        rejected_orders = len([o for o in self.completed_orders.values() if o.status == OrderStatus.REJECTED])
        
        return {
            "total_orders": total_orders,
            "active_orders": len(self.active_orders),
            "completed_orders": len(self.completed_orders),
            "filled_orders": filled_orders,
            "rejected_orders": rejected_orders,
            "total_exposure": self.get_total_exposure()
        }


class BacktestExecutor(OrderExecutor):
    """
    Executor para backtesting con fills realistas
    """
    
    def __init__(self, broker_client, commission_rate: float = 0.0004, slippage: float = 0.0005):
        """
        Inicializa el executor de backtest
        
        Args:
            broker_client: Cliente del broker
            commission_rate: Tasa de comisión
            slippage: Slippage a simular (0.0005 = 0.05%)
        """
        super().__init__(broker_client, commission_rate)
        self.slippage = slippage
    
    def execute(self, decision: OrderDecision) -> Optional[Order]:
        """
        Ejecuta con slippage simulado
        
        Args:
            decision: OrderDecision aprobada
        
        Returns:
            Order con fill realista
        """
        if not decision.approved:
            return None
        
        # Aplicar slippage al precio
        if decision.entry_price:
            if decision.side == "BUY":
                filled_price = decision.entry_price * (1 + self.slippage)
            else:  # SELL
                filled_price = decision.entry_price * (1 - self.slippage)
        else:
            filled_price = 0.0
        
        # Crear orden con precio ajustado
        order_id = f"BT-{uuid.uuid4().hex[:8].upper()}"
        
        commission = filled_price * decision.size * self.commission_rate
        
        order = Order(
            id=order_id,
            symbol=decision.symbol,
            side=decision.side,
            size=decision.size,
            entry_price=filled_price,
            timestamp=datetime.now(),
            status=OrderStatus.FILLED,
            filled_size=decision.size,
            filled_price=filled_price,
            stop_loss=decision.stop_loss,
            take_profit=decision.take_profit,
            commission=commission
        )
        
        self.completed_orders[order_id] = order
        
        return order
