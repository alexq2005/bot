"""
XGBoost Model
Gradient Boosting para clasificación de señales de trading
"""

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
import pickle
import os
from typing import Dict


class XGBoostTradingModel:
    """
    Modelo XGBoost para predicción de señales de trading
    
    Ventajas:
    - Excelente para datos tabulares
    - Rápido y eficiente
    - Maneja bien features no lineales
    """
    
    def __init__(self, model_path: str = "./models/xgboost_model.pkl"):
        """
        Inicializa el modelo XGBoost
        
        Args:
            model_path: Ruta para guardar/cargar modelo
        """
        self.model_path = model_path
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='multi:softmax',
            num_class=3,  # HOLD, BUY, SELL
            random_state=42
        )
        self.is_trained = False
        
        if os.path.exists(model_path):
            self.load_model()
    
    def prepare_features(self, state: np.ndarray) -> np.ndarray:
        """
        Prepara features para XGBoost
        
        Args:
            state: Estado del mercado
        
        Returns:
            Features preparadas
        """
        # Si state es 1D, expandir a 2D
        if len(state.shape) == 1:
            state = state.reshape(1, -1)
        
        return state
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Entrena el modelo
        
        Args:
            X: Features (estados del mercado)
            y: Labels (acciones: 0=HOLD, 1=BUY, 2=SELL)
        """
        print("🎓 Entrenando modelo XGBoost...")
        self.model.fit(X, y)
        self.is_trained = True
        print("✓ Entrenamiento completado")
    
    def predict(self, state: np.ndarray) -> Dict:
        """
        Predice acción
        
        Args:
            state: Estado actual
        
        Returns:
            Dict con acción y confianza
        """
        if not self.is_trained:
            return {'action': 'HOLD', 'confidence': 0.0}
        
        features = self.prepare_features(state)
        
        # Predicción
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        # Mapear a acción
        action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
        action = action_map.get(int(prediction), 'HOLD')
        
        # Confianza = probabilidad de la clase predicha
        confidence = float(probabilities[int(prediction)])
        
        return {
            'action': action,
            'confidence': confidence,
            'probabilities': {
                'HOLD': float(probabilities[0]),
                'BUY': float(probabilities[1]),
                'SELL': float(probabilities[2])
            }
        }
    
    def save_model(self, path: str = None):
        """Guarda el modelo"""
        save_path = path or self.model_path
        with open(save_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"✓ Modelo XGBoost guardado en {save_path}")
    
    def load_model(self, path: str = None):
        """Carga el modelo"""
        load_path = path or self.model_path
        try:
            with open(load_path, 'rb') as f:
                self.model = pickle.load(f)
            self.is_trained = True
            print(f"✓ Modelo XGBoost cargado desde {load_path}")
        except Exception as e:
            print(f"⚠ No se pudo cargar modelo XGBoost: {e}")
            self.is_trained = False
