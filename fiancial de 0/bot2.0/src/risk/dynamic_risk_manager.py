"""
Advanced Risk Management
Stop Loss and Take Profit dinámicos basados en ATR
"""

from typing import Dict, Optional

class DynamicRiskManager:
    """Gestión de riesgo con Stop Loss/Take Profit dinámicos"""
    
    def __init__(self, 
                 sl_atr_multiplier: float = 2.0,
                 tp_atr_multiplier: float = 3.0,
                 trailing_stop: bool = True):
        """
        Args:
            sl_atr_multiplier: Multiplicador de ATR para Stop Loss (ej: 2.0 = 2 ATRs)
            tp_atr_multiplier: Multiplicador de ATR para Take Profit (ej: 3.0 = 3 ATRs)
            trailing_stop: Si True, el SL se mueve a favor cuando hay ganancias
        """
        self.sl_multiplier = sl_atr_multiplier
        self.tp_multiplier = tp_atr_multiplier
        self.trailing_stop = trailing_stop
        
    def calculate_levels(self, 
                        entry_price: float, 
                        atr: float, 
                        direction: str = "LONG") -> Dict[str, float]:
        """
        Calcula niveles de Stop Loss y Take Profit
        
        Args:
            entry_price: Precio de entrada
            atr: ATR actual (Average True Range)
            direction: "LONG" o "SHORT"
            
        Returns:
            Dict con 'stop_loss' y 'take_profit'
        """
        if direction == "LONG":
            stop_loss = entry_price - (atr * self.sl_multiplier)
            take_profit = entry_price + (atr * self.tp_multiplier)
        else:  # SHORT
            stop_loss = entry_price + (atr * self.sl_multiplier)
            take_profit = entry_price - (atr * self.tp_multiplier)
            
        return {
            'stop_loss': max(0, stop_loss),  # Evitar negativos
            'take_profit': take_profit,
            'risk_reward_ratio': self.tp_multiplier / self.sl_multiplier
        }
    
    def should_exit(self, 
                   current_price: float, 
                   entry_price: float,
                   stop_loss: float, 
                   take_profit: float,
                   direction: str = "LONG") -> Dict[str, any]:
        """
        Determina si hay que salir de la posición
        
        Returns:
            Dict con 'exit': bool, 'reason': str, 'pnl_pct': float
        """
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        if direction == "LONG":
            if current_price <= stop_loss:
                return {'exit': True, 'reason': 'STOP_LOSS', 'pnl_pct': pnl_pct}
            elif current_price >= take_profit:
                return {'exit': True, 'reason': 'TAKE_PROFIT', 'pnl_pct': pnl_pct}
        else:  # SHORT
            if current_price >= stop_loss:
                return {'exit': True, 'reason': 'STOP_LOSS', 'pnl_pct': pnl_pct}
            elif current_price <= take_profit:
                return {'exit': True, 'reason': 'TAKE_PROFIT', 'pnl_pct': pnl_pct}
                
        return {'exit': False, 'reason': None, 'pnl_pct': pnl_pct}
    
    def update_trailing_stop(self, 
                            entry_price: float,
                            current_price: float, 
                            current_sl: float, 
                            atr: float,
                            direction: str = "LONG") -> float:
        """
        Actualiza el Stop Loss con trailing (lo mueve a favor si hay ganancia)
        
        Returns:
            Nuevo nivel de Stop Loss
        """
        if not self.trailing_stop:
            return current_sl
            
        if direction == "LONG":
            # Solo mover SL hacia arriba si estamos en ganancias
            if current_price > entry_price:
                new_sl = current_price - (atr * self.sl_multiplier)
                return max(current_sl, new_sl)
        else:  # SHORT
            if current_price < entry_price:
                new_sl = current_price + (atr * self.sl_multiplier)
                return min(current_sl, new_sl)
                
        return current_sl
