"""
Reinforcement Learning Agent
Agente PPO para tomar decisiones de trading
"""

import os
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from typing import Optional
import pandas as pd

from .trading_env import TradingEnv


class TrainingCallback(BaseCallback):
    """Callback para logging durante entrenamiento"""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        return True
    
    def _on_rollout_end(self) -> None:
        """Llamado al final de cada rollout"""
        if len(self.model.ep_info_buffer) > 0:
            mean_reward = np.mean([ep_info["r"] for ep_info in self.model.ep_info_buffer])
            mean_length = np.mean([ep_info["l"] for ep_info in self.model.ep_info_buffer])
            
            print(f"Rollout - Mean Reward: {mean_reward:.2f}, Mean Length: {mean_length:.0f}")


class RLAgent:
    """Agente de Reinforcement Learning usando PPO"""
    
    def __init__(
        self,
        model_path: str = "./models/ppo_trading_agent",
        learning_rate: float = 0.0003,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10
    ):
        """
        Inicializa el agente RL
        
        Args:
            model_path: Ruta para guardar/cargar el modelo
            learning_rate: Tasa de aprendizaje
            n_steps: Pasos por actualización
            batch_size: Tamaño del batch
            n_epochs: Épocas de entrenamiento
        """
        self.model_path = model_path
        self.learning_rate = learning_rate
        self.n_steps = n_steps
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.model: Optional[PPO] = None
        self.env: Optional[DummyVecEnv] = None
        
        # Crear directorio de modelos si no existe
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    def create_model(self, env: TradingEnv):
        """
        Crea un nuevo modelo PPO
        
        Args:
            env: Entorno de trading
        """
        # Vectorizar el entorno
        self.env = DummyVecEnv([lambda: env])
        
        # Crear modelo PPO
        self.model = PPO(
            "MlpPolicy",  # Política de red neuronal multi-capa
            self.env,
            learning_rate=self.learning_rate,
            n_steps=self.n_steps,
            batch_size=self.batch_size,
            n_epochs=self.n_epochs,
            gamma=0.99,  # Factor de descuento
            gae_lambda=0.95,  # GAE lambda
            clip_range=0.2,  # Clip range para PPO
            verbose=1,
            tensorboard_log="./logs/tensorboard/"
        )
        
        print(f"✓ Modelo PPO creado con éxito")
    
    def train(
        self, 
        df: pd.DataFrame, 
        total_timesteps: int = 100000,
        initial_balance: float = 100000
    ):
        """
        Entrena el agente en datos históricos
        
        Args:
            df: DataFrame con datos históricos e indicadores
            total_timesteps: Pasos totales de entrenamiento
            initial_balance: Balance inicial para entrenamiento
        """
        # Crear entorno
        env = TradingEnv(df, initial_balance=initial_balance)
        
        # Crear o cargar modelo
        if self.model is None:
            self.create_model(env)
        
        # Callback para logging
        callback = TrainingCallback()
        
        print(f"🚀 Iniciando entrenamiento por {total_timesteps} timesteps...")
        
        # Entrenar
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True
        )
        
        print(f"✓ Entrenamiento completado")
        
        # Guardar modelo
        self.save()
    
    def save(self):
        """Guarda el modelo entrenado"""
        if self.model:
            self.model.save(self.model_path)
            print(f"✓ Modelo guardado en {self.model_path}")
    
    def load(self):
        """Carga un modelo previamente entrenado"""
        if os.path.exists(f"{self.model_path}.zip"):
            self.model = PPO.load(self.model_path)
            print(f"✓ Modelo cargado desde {self.model_path}")
            return True
        else:
            print(f"⚠ No se encontró modelo en {self.model_path}")
            return False
    
    def predict(self, observation: np.ndarray) -> str:
        """
        Predice la acción a tomar
        
        Args:
            observation: Estado actual del entorno
        
        Returns:
            str: "BUY", "SELL", o "HOLD"
        """
        if self.model is None:
            # Si no hay modelo, retornar HOLD por defecto
            return "HOLD"
        
        # Predecir acción
        action, _states = self.model.predict(observation, deterministic=True)
        
        # Mapear acción a string
        action_map = {0: "HOLD", 1: "BUY", 2: "SELL"}
        return action_map.get(int(action), "HOLD")
    
    def predict_from_state(
        self,
        price: float,
        rsi: float,
        macd: float,
        sentiment: float,
        position_ratio: float,
        cash_ratio: float,
        price_min: float,
        price_max: float,
        macd_min: float,
        macd_max: float
    ) -> str:
        """
        Predice acción desde valores de estado individuales
        
        Args:
            price: Precio actual
            rsi: RSI actual
            macd: MACD actual
            sentiment: Sentimiento actual (-1 a 1)
            position_ratio: Ratio de posición
            cash_ratio: Ratio de efectivo
            price_min: Precio mínimo para normalización
            price_max: Precio máximo para normalización
            macd_min: MACD mínimo para normalización
            macd_max: MACD máximo para normalización
        
        Returns:
            str: "BUY", "SELL", o "HOLD"
        """
        # Normalizar estado
        price_norm = (price - price_min) / (price_max - price_min + 1e-8)
        rsi_norm = rsi / 100.0
        macd_norm = (macd - macd_min) / (macd_max - macd_min + 1e-8)
        macd_norm = macd_norm * 2 - 1
        
        observation = np.array([
            price_norm,
            rsi_norm,
            macd_norm,
            sentiment,
            position_ratio,
            cash_ratio
        ], dtype=np.float32)
        
        return self.predict(observation)
    
    def evaluate(self, df: pd.DataFrame, initial_balance: float = 100000) -> dict:
        """
        Evalúa el rendimiento del agente en datos de prueba
        
        Args:
            df: DataFrame con datos de prueba
            initial_balance: Balance inicial
        
        Returns:
            dict: Métricas de rendimiento
        """
        if self.model is None:
            print("⚠ No hay modelo cargado para evaluar")
            return {}
        
        env = TradingEnv(df, initial_balance=initial_balance)
        obs, _ = env.reset()
        
        total_reward = 0
        done = False
        steps = 0
        
        while not done:
            action, _states = self.model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
            total_reward += reward
            steps += 1
        
        final_value = info['total_value']
        total_return = ((final_value - initial_balance) / initial_balance) * 100
        
        return {
            "total_reward": total_reward,
            "final_value": final_value,
            "total_return_pct": total_return,
            "steps": steps
        }
