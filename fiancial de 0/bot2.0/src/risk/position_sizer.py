"""
Position Sizer
Calcula el tamaño óptimo de posición basado en volatilidad (ATR)
"""

import pandas as pd
from typing import Dict


class PositionSizer:
    """Calculador de tamaño de posición dinámico"""
    
    def __init__(
        self,
        risk_per_trade: float = 2.0,
        max_position_size: float = 20.0,
        min_position_size: float = 1.0
    ):
        """
        Inicializa el position sizer
        
        Args:
            risk_per_trade: Porcentaje de riesgo por operación (default: 2%)
            max_position_size: Máximo porcentaje del portafolio por activo (default: 20%)
            min_position_size: Mínimo porcentaje del portafolio (default: 1%)
        """
        self.risk_per_trade = risk_per_trade / 100.0  # Convertir a decimal
        self.max_position_size = max_position_size / 100.0
        self.min_position_size = min_position_size / 100.0
    
    def calculate_position_size_atr(
        self,
        account_balance: float,
        current_price: float,
        atr: float,
        atr_multiplier: float = 2.0
    ) -> Dict:
        """
        Calcula el tamaño de posición basado en ATR (Average True Range)
        
        Método: Position Size = (Account Balance * Risk%) / (ATR * Multiplier)
        
        Args:
            account_balance: Saldo disponible en cuenta
            current_price: Precio actual del activo
            atr: Average True Range (medida de volatilidad)
            atr_multiplier: Multiplicador del ATR para stop loss (default: 2.0)
        
        Returns:
            Dict con: quantity (acciones), position_value, position_pct, stop_loss
        """
        # Calcular riesgo en dinero
        risk_amount = account_balance * self.risk_per_trade
        
        # Stop loss basado en ATR
        stop_loss_distance = atr * atr_multiplier
        stop_loss_price = current_price - stop_loss_distance
        
        # Cantidad de acciones basada en riesgo
        # Si el precio cae stop_loss_distance, perdemos risk_amount
        if stop_loss_distance > 0:
            quantity = int(risk_amount / stop_loss_distance)
        else:
            quantity = 0
        
        # Valor de la posición
        position_value = quantity * current_price
        
        # Porcentaje del portafolio
        position_pct = (position_value / account_balance) * 100 if account_balance > 0 else 0
        
        # Aplicar límites
        max_value = account_balance * self.max_position_size
        min_value = account_balance * self.min_position_size
        
        if position_value > max_value:
            quantity = int(max_value / current_price)
            position_value = quantity * current_price
            position_pct = (position_value / account_balance) * 100
        
        if position_value < min_value and position_value > 0:
            quantity = int(min_value / current_price)
            position_value = quantity * current_price
            position_pct = (position_value / account_balance) * 100
        
        return {
            "quantity": quantity,
            "position_value": position_value,
            "position_pct": position_pct,
            "stop_loss": stop_loss_price,
            "atr": atr,
            "risk_amount": risk_amount
        }
    
    def calculate_position_size_fixed(
        self,
        account_balance: float,
        current_price: float,
        position_pct: float = None
    ) -> Dict:
        """
        Calcula el tamaño de posición con porcentaje fijo
        
        Args:
            account_balance: Saldo disponible
            current_price: Precio actual
            position_pct: Porcentaje del portafolio (si None, usa max_position_size)
        
        Returns:
            Dict con: quantity, position_value, position_pct
        """
        if position_pct is None:
            position_pct = self.max_position_size * 100
        
        # Convertir a decimal
        pct_decimal = position_pct / 100.0
        
        # Aplicar límites
        pct_decimal = max(self.min_position_size, min(pct_decimal, self.max_position_size))
        
        # Calcular valor y cantidad
        position_value = account_balance * pct_decimal
        quantity = int(position_value / current_price)
        actual_value = quantity * current_price
        actual_pct = (actual_value / account_balance) * 100 if account_balance > 0 else 0
        
        return {
            "quantity": quantity,
            "position_value": actual_value,
            "position_pct": actual_pct
        }
    
    def calculate_take_profit_stop_loss(
        self,
        entry_price: float,
        take_profit_pct: float = 10.0,
        stop_loss_pct: float = 5.0
    ) -> Dict:
        """
        Calcula niveles de take profit y stop loss
        
        Args:
            entry_price: Precio de entrada
            take_profit_pct: Porcentaje de ganancia objetivo (default: 10%)
            stop_loss_pct: Porcentaje de pérdida máxima (default: 5%)
        
        Returns:
            Dict con: take_profit, stop_loss, risk_reward_ratio
        """
        take_profit = entry_price * (1 + take_profit_pct / 100.0)
        stop_loss = entry_price * (1 - stop_loss_pct / 100.0)
        
        # Risk/Reward ratio
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "risk_reward_ratio": risk_reward_ratio
        }
