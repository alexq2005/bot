"""
Trading Environment for Reinforcement Learning
Entorno Gym personalizado para entrenar el agente PPO
"""

import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Tuple, Optional


class TradingEnv(gym.Env):
    """
    Entorno de trading para Reinforcement Learning
    
    State Space: [Price, RSI, MACD, Sentiment, Position, Cash_Ratio]
    Action Space: [0=HOLD, 1=BUY, 2=SELL]
    Reward: Portfolio value change + risk-adjusted returns
    """
    
    metadata = {'render_modes': ['human']}
    
    def __init__(
        self,
        df: pd.DataFrame,
        initial_balance: float = 100000,
        commission: float = 0.001,  # 0.1% comisión
        max_position_size: float = 0.5  # Máximo 50% del capital
    ):
        """
        Inicializa el entorno de trading
        
        Args:
            df: DataFrame con datos históricos y indicadores
            initial_balance: Balance inicial
            commission: Comisión por operación
            max_position_size: Tamaño máximo de posición (% del capital)
        """
        super().__init__()
        
        self.df = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.commission = commission
        self.max_position_size = max_position_size
        
        # State space: [price_norm, rsi_norm, macd_norm, sentiment, position_ratio, cash_ratio]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -1, -1, 0, 0], dtype=np.float32),
            high=np.array([1, 1, 1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32
        )
        
        # Action space: 0=HOLD, 1=BUY, 2=SELL
        self.action_space = spaces.Discrete(3)
        
        # Estado del episodio
        self.current_step = 0
        self.balance = initial_balance
        self.shares_held = 0
        self.total_value = initial_balance
        self.max_value = initial_balance
        
        # Para normalización
        self.price_min = df['close'].min()
        self.price_max = df['close'].max()
        self.macd_min = df['macd'].min() if 'macd' in df.columns else -1
        self.macd_max = df['macd'].max() if 'macd' in df.columns else 1
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Reinicia el entorno"""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.total_value = self.initial_balance
        self.max_value = self.initial_balance
        
        return self._get_observation(), {}
    
    def _get_observation(self) -> np.ndarray:
        """Obtiene el estado actual normalizado"""
        row = self.df.iloc[self.current_step]
        
        # Normalizar precio (0-1)
        price_norm = (row['close'] - self.price_min) / (self.price_max - self.price_min + 1e-8)
        
        # RSI ya está en 0-100, normalizar a 0-1
        rsi_norm = row.get('rsi', 50) / 100.0
        
        # MACD normalizado a -1 a 1
        macd_norm = (row.get('macd', 0) - self.macd_min) / (self.macd_max - self.macd_min + 1e-8)
        macd_norm = macd_norm * 2 - 1  # Escalar a -1, 1
        
        # Sentimiento (ya está en -1 a 1)
        sentiment = row.get('sentiment', 0)
        
        # Ratio de posición (cuánto del capital está invertido)
        current_price = row['close']
        position_value = self.shares_held * current_price
        total_value = self.balance + position_value
        position_ratio = position_value / (total_value + 1e-8)
        
        # Ratio de efectivo
        cash_ratio = self.balance / (total_value + 1e-8)
        
        return np.array([
            price_norm,
            rsi_norm,
            macd_norm,
            sentiment,
            position_ratio,
            cash_ratio
        ], dtype=np.float32)
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Ejecuta una acción en el entorno
        
        Args:
            action: 0=HOLD, 1=BUY, 2=SELL
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        current_price = self.df.iloc[self.current_step]['close']
        
        # Ejecutar acción
        if action == 1:  # BUY
            # Comprar con máximo max_position_size del capital total
            max_invest = self.balance * self.max_position_size
            shares_to_buy = int(max_invest / (current_price * (1 + self.commission)))
            
            if shares_to_buy > 0:
                cost = shares_to_buy * current_price * (1 + self.commission)
                if cost <= self.balance:
                    self.balance -= cost
                    self.shares_held += shares_to_buy
        
        elif action == 2:  # SELL
            # Vender todas las acciones
            if self.shares_held > 0:
                revenue = self.shares_held * current_price * (1 - self.commission)
                self.balance += revenue
                self.shares_held = 0
        
        # Calcular valor total del portafolio
        position_value = self.shares_held * current_price
        self.total_value = self.balance + position_value
        
        # Actualizar máximo valor alcanzado
        if self.total_value > self.max_value:
            self.max_value = self.total_value
        
        # Calcular reward
        reward = self._calculate_reward()
        
        # Avanzar al siguiente paso
        self.current_step += 1
        
        # Verificar si el episodio terminó
        terminated = self.current_step >= len(self.df) - 1
        truncated = False
        
        # Info adicional
        info = {
            'total_value': self.total_value,
            'balance': self.balance,
            'shares_held': self.shares_held,
            'current_price': current_price
        }
        
        return self._get_observation(), reward, terminated, truncated, info
    
    def _calculate_reward(self) -> float:
        """
        Calcula el reward para el agente
        
        Combina:
        - Cambio en valor del portafolio
        - Penalización por drawdown
        - Bonus por mantener posiciones ganadoras
        """
        # Retorno porcentual
        portfolio_return = (self.total_value - self.initial_balance) / self.initial_balance
        
        # Drawdown desde máximo
        drawdown = (self.max_value - self.total_value) / self.max_value if self.max_value > 0 else 0
        
        # Reward = retorno - penalización por drawdown
        reward = portfolio_return - (drawdown * 0.5)
        
        return reward
    
    def render(self):
        """Renderiza el estado actual (para debugging)"""
        print(f"Step: {self.current_step}")
        print(f"Balance: ${self.balance:,.2f}")
        print(f"Shares: {self.shares_held}")
        print(f"Total Value: ${self.total_value:,.2f}")
        print(f"Return: {((self.total_value - self.initial_balance) / self.initial_balance * 100):.2f}%")
        print("-" * 50)
