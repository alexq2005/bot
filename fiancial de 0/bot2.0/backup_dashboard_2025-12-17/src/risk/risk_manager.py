"""
Risk Manager
Gestión integral de riesgo del portafolio
"""

from typing import Dict, List, Optional


class RiskManager:
    """Gestor de riesgo del portafolio"""
    
    def __init__(
        self,
        max_portfolio_risk: float = 10.0,
        max_position_size: float = 20.0,
        max_correlation: float = 0.7,
        max_drawdown: float = 20.0
    ):
        """
        Inicializa el risk manager
        
        Args:
            max_portfolio_risk: Máximo riesgo total del portafolio (%)
            max_position_size: Máximo tamaño de posición individual (%)
            max_correlation: Máxima correlación permitida entre activos
            max_drawdown: Máximo drawdown permitido (%)
        """
        self.max_portfolio_risk = max_portfolio_risk / 100.0
        self.max_position_size = max_position_size / 100.0
        self.max_correlation = max_correlation
        self.max_drawdown = max_drawdown / 100.0
        
        # Tracking
        self.peak_value = 0
        self.current_drawdown = 0
    
    def check_position_size(
        self,
        position_value: float,
        total_portfolio_value: float
    ) -> Dict:
        """
        Verifica si el tamaño de posición es aceptable
        
        Args:
            position_value: Valor de la posición propuesta
            total_portfolio_value: Valor total del portafolio
        
        Returns:
            Dict con: approved (bool), reason (str), position_pct (float)
        """
        position_pct = position_value / total_portfolio_value if total_portfolio_value > 0 else 0
        
        if position_pct > self.max_position_size:
            return {
                "approved": False,
                "reason": f"Posición excede límite ({position_pct*100:.1f}% > {self.max_position_size*100:.1f}%)",
                "position_pct": position_pct * 100
            }
        
        return {
            "approved": True,
            "reason": "Tamaño de posición aceptable",
            "position_pct": position_pct * 100
        }
    
    def check_portfolio_concentration(
        self,
        positions: Dict[str, float],
        total_value: float
    ) -> Dict:
        """
        Verifica la concentración del portafolio
        
        Args:
            positions: Dict {symbol: position_value}
            total_value: Valor total del portafolio
        
        Returns:
            Dict con: approved, reason, concentration_pct, top_positions
        """
        if not positions or total_value == 0:
            return {
                "approved": True,
                "reason": "Portafolio vacío",
                "concentration_pct": 0,
                "top_positions": []
            }
        
        # Calcular porcentajes
        position_pcts = {
            symbol: (value / total_value) * 100 
            for symbol, value in positions.items()
        }
        
        # Ordenar por tamaño
        sorted_positions = sorted(
            position_pcts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Concentración en top 3
        top_3_concentration = sum(pct for _, pct in sorted_positions[:3])
        
        # Verificar límites individuales
        for symbol, pct in sorted_positions:
            if pct > self.max_position_size * 100:
                return {
                    "approved": False,
                    "reason": f"{symbol} excede límite ({pct:.1f}% > {self.max_position_size*100:.1f}%)",
                    "concentration_pct": top_3_concentration,
                    "top_positions": sorted_positions[:5]
                }
        
        return {
            "approved": True,
            "reason": "Concentración aceptable",
            "concentration_pct": top_3_concentration,
            "top_positions": sorted_positions[:5]
        }
    
    def update_drawdown(self, current_value: float) -> Dict:
        """
        Actualiza y verifica el drawdown
        
        Args:
            current_value: Valor actual del portafolio
        
        Returns:
            Dict con: drawdown_pct, peak_value, emergency_stop
        """
        # Actualizar peak
        if current_value > self.peak_value:
            self.peak_value = current_value
        
        # Calcular drawdown
        if self.peak_value > 0:
            self.current_drawdown = (self.peak_value - current_value) / self.peak_value
        else:
            self.current_drawdown = 0
        
        # Verificar si se debe detener el trading
        emergency_stop = self.current_drawdown > self.max_drawdown
        
        return {
            "drawdown_pct": self.current_drawdown * 100,
            "peak_value": self.peak_value,
            "current_value": current_value,
            "emergency_stop": emergency_stop,
            "reason": f"Drawdown excede límite ({self.current_drawdown*100:.1f}% > {self.max_drawdown*100:.1f}%)" if emergency_stop else "Drawdown aceptable"
        }
    
    def check_trade_approval(
        self,
        action: str,
        symbol: str,
        quantity: int,
        price: float,
        current_positions: Dict[str, float],
        account_balance: float
    ) -> Dict:
        """
        Aprueba o rechaza una operación basándose en múltiples criterios de riesgo
        
        Args:
            action: "BUY" o "SELL"
            symbol: Símbolo del activo
            quantity: Cantidad de acciones
            price: Precio de la operación
            current_positions: Posiciones actuales {symbol: value}
            account_balance: Saldo disponible
        
        Returns:
            Dict con: approved, reason, checks
        """
        checks = {}
        
        if action == "BUY":
            # Verificar fondos
            total_cost = quantity * price
            if total_cost > account_balance:
                return {
                    "approved": False,
                    "reason": f"Fondos insuficientes (necesitas ${total_cost:,.2f}, tienes ${account_balance:,.2f})",
                    "checks": {"funds": False}
                }
            checks["funds"] = True
            
            # Verificar tamaño de posición
            total_value = account_balance + sum(current_positions.values())
            position_check = self.check_position_size(total_cost, total_value)
            checks["position_size"] = position_check["approved"]
            
            if not position_check["approved"]:
                return {
                    "approved": False,
                    "reason": position_check["reason"],
                    "checks": checks
                }
            
            # Verificar concentración del portafolio después de la compra
            new_positions = current_positions.copy()
            new_positions[symbol] = new_positions.get(symbol, 0) + total_cost
            
            concentration_check = self.check_portfolio_concentration(
                new_positions,
                total_value
            )
            checks["concentration"] = concentration_check["approved"]
            
            if not concentration_check["approved"]:
                return {
                    "approved": False,
                    "reason": concentration_check["reason"],
                    "checks": checks
                }
        
        elif action == "SELL":
            # Verificar que se tenga la posición
            current_position_value = current_positions.get(symbol, 0)
            sell_value = quantity * price
            
            if sell_value > current_position_value * 1.1:  # 10% de margen por precio
                return {
                    "approved": False,
                    "reason": f"No tienes suficientes acciones de {symbol}",
                    "checks": {"position_exists": False}
                }
            checks["position_exists"] = True
        
        # Todas las verificaciones pasaron
        return {
            "approved": True,
            "reason": "Operación aprobada",
            "checks": checks
        }
    
    def get_risk_metrics(
        self,
        positions: Dict[str, float],
        total_value: float
    ) -> Dict:
        """
        Calcula métricas de riesgo del portafolio
        
        Returns:
            Dict con métricas de riesgo
        """
        concentration = self.check_portfolio_concentration(positions, total_value)
        drawdown = self.update_drawdown(total_value)
        
        return {
            "total_positions": len(positions),
            "top_3_concentration_pct": concentration["concentration_pct"],
            "current_drawdown_pct": drawdown["drawdown_pct"],
            "peak_value": drawdown["peak_value"],
            "emergency_stop_active": drawdown["emergency_stop"],
            "largest_position": concentration["top_positions"][0] if concentration["top_positions"] else None
        }
