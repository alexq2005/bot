"""
SAC Agent (Soft Actor-Critic)
Algoritmo de RL más avanzado que PPO para trading continuo
"""

import numpy as np
import torch
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
import os


class SACAgent:
    """
    Agente SAC (Soft Actor-Critic)
    
    Ventajas sobre PPO:
    - Mejor para espacios de acción continuos
    - Más sample-efficient
    - Explora mejor el espacio de acciones
    """
    
    def __init__(self, env=None, model_path: str = "./models/sac_trading_agent"):
        """
        Inicializa el agente SAC
        
        Args:
            env: Entorno de trading
            model_path: Ruta para guardar/cargar modelo
        """
        self.env = env
        self.model_path = model_path
        self.model = None
        
        if os.path.exists(f"{model_path}.zip"):
            self.load_model(model_path)
        elif env is not None:
            self._create_model()
    
    def _create_model(self):
        """Crea un nuevo modelo SAC"""
        self.model = SAC(
            "MlpPolicy",
            self.env,
            learning_rate=3e-4,
            buffer_size=100000,
            learning_starts=1000,
            batch_size=256,
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            ent_coef='auto',
            verbose=0
        )
    
    def train(self, total_timesteps: int = 50000):
        """
        Entrena el agente
        
        Args:
            total_timesteps: Número de pasos de entrenamiento
        """
        if self.model is None:
            raise ValueError("Modelo no inicializado")
        
        print(f"🎓 Entrenando agente SAC ({total_timesteps} timesteps)...")
        self.model.learn(total_timesteps=total_timesteps)
        print("✓ Entrenamiento completado")
    
    def predict(self, state: np.ndarray) -> Dict:
        """
        Predice acción dado un estado
        
        Args:
            state: Estado actual
        
        Returns:
            Dict con acción y confianza
        """
        if self.model is None:
            return {'action': 'HOLD', 'confidence': 0.0}
        
        action, _states = self.model.predict(state, deterministic=True)
        
        # Mapear acción continua a discreta
        if isinstance(action, (int, np.integer)):
            action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
            action_str = action_map.get(int(action), 'HOLD')
        else:
            # Si es continua, usar umbral
            if action > 0.5:
                action_str = 'BUY'
            elif action < -0.5:
                action_str = 'SELL'
            else:
                action_str = 'HOLD'
        
        # Confianza basada en magnitud de la acción
        confidence = min(abs(float(action)) / 1.0, 1.0) if not isinstance(action, int) else 0.7
        
        return {
            'action': action_str,
            'confidence': confidence
        }
    
    def save_model(self, path: str = None):
        """Guarda el modelo"""
        save_path = path or self.model_path
        if self.model:
            self.model.save(save_path)
            print(f"✓ Modelo SAC guardado en {save_path}")
    
    def load_model(self, path: str = None):
        """Carga el modelo"""
        load_path = path or self.model_path
        try:
            self.model = SAC.load(load_path)
            print(f"✓ Modelo SAC cargado desde {load_path}")
        except Exception as e:
            print(f"⚠ No se pudo cargar modelo SAC: {e}")
