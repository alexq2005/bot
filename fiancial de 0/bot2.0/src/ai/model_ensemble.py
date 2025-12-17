"""
Model Ensemble
Sistema de ensemble que combina múltiples modelos ML
"""

from typing import Dict, List, Tuple
import numpy as np
from collections import defaultdict


class ModelEnsemble:
    """
    Ensemble de modelos ML con votación ponderada
    
    Combina predicciones de:
    - PPO (Reinforcement Learning)
    - SAC (Soft Actor-Critic)
    - XGBoost (Gradient Boosting)
    - LSTM (Deep Learning)
    - Random Forest (Ensemble tradicional)
    """
    
    def __init__(self):
        """Inicializa el ensemble"""
        self.models = {}
        self.weights = {}
        self.performance_history = defaultdict(list)
        
        # Pesos iniciales (iguales)
        self.default_weight = 0.2  # 5 modelos = 20% cada uno
    
    def register_model(self, name: str, model, initial_weight: float = None):
        """
        Registra un modelo en el ensemble
        
        Args:
            name: Nombre del modelo
            model: Instancia del modelo
            initial_weight: Peso inicial (default: 0.2)
        """
        self.models[name] = model
        self.weights[name] = initial_weight or self.default_weight
        print(f"✓ Modelo '{name}' registrado en ensemble (peso: {self.weights[name]:.2f})")
    
    def predict(self, state: np.ndarray) -> Dict:
        """
        Obtiene predicción del ensemble
        
        Args:
            state: Estado actual del mercado
        
        Returns:
            Dict con acción, confianza y votos individuales
        """
        if not self.models:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'votes': {},
                'reasoning': 'No hay modelos en el ensemble'
            }
        
        # Recolectar votos de cada modelo
        votes = {}
        confidences = {}
        
        for name, model in self.models.items():
            try:
                prediction = model.predict(state)
                
                # Normalizar formato de predicción
                if isinstance(prediction, dict):
                    action = prediction.get('action', 'HOLD')
                    confidence = prediction.get('confidence', 0.5)
                elif isinstance(prediction, (int, np.integer)):
                    # Mapear acción numérica
                    action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
                    action = action_map.get(prediction, 'HOLD')
                    confidence = 0.7  # Confianza por defecto
                else:
                    action = str(prediction)
                    confidence = 0.5
                
                votes[name] = action
                confidences[name] = confidence
                
            except Exception as e:
                print(f"⚠ Error en modelo {name}: {e}")
                votes[name] = 'HOLD'
                confidences[name] = 0.0
        
        # Votación ponderada
        weighted_votes = defaultdict(float)
        
        for name, action in votes.items():
            weight = self.weights.get(name, self.default_weight)
            confidence = confidences.get(name, 0.5)
            
            # Voto ponderado = peso × confianza
            weighted_votes[action] += weight * confidence
        
        # Acción ganadora
        if not weighted_votes:
            final_action = 'HOLD'
            final_confidence = 0.0
        else:
            final_action = max(weighted_votes, key=weighted_votes.get)
            total_weight = sum(weighted_votes.values())
            final_confidence = weighted_votes[final_action] / total_weight if total_weight > 0 else 0.0
        
        # Generar razonamiento
        vote_summary = ", ".join([f"{name}: {action}" for name, action in votes.items()])
        reasoning = f"Ensemble: {vote_summary} → {final_action} ({final_confidence:.1%})"
        
        return {
            'action': final_action,
            'confidence': final_confidence,
            'votes': votes,
            'confidences': confidences,
            'weighted_votes': dict(weighted_votes),
            'reasoning': reasoning
        }
    
    def update_performance(self, model_name: str, performance: float):
        """
        Actualiza el rendimiento de un modelo
        
        Args:
            model_name: Nombre del modelo
            performance: Métrica de rendimiento (ej: accuracy, sharpe)
        """
        self.performance_history[model_name].append(performance)
    
    def adjust_weights(self, method: str = 'performance'):
        """
        Ajusta pesos de los modelos según rendimiento
        
        Args:
            method: Método de ajuste ('performance', 'equal', 'sharpe')
        """
        if method == 'equal':
            # Pesos iguales
            n_models = len(self.models)
            for name in self.models:
                self.weights[name] = 1.0 / n_models
        
        elif method == 'performance':
            # Pesos basados en rendimiento histórico
            performances = {}
            
            for name in self.models:
                history = self.performance_history.get(name, [])
                if history:
                    # Promedio de últimas 10 métricas
                    recent = history[-10:]
                    performances[name] = np.mean(recent)
                else:
                    performances[name] = 0.5  # Neutral
            
            # Normalizar a suma = 1.0
            total = sum(performances.values())
            if total > 0:
                for name in self.models:
                    self.weights[name] = performances[name] / total
            
            print("🔧 Pesos ajustados según rendimiento:")
            for name, weight in self.weights.items():
                print(f"   {name}: {weight:.3f}")
    
    def get_model_stats(self) -> Dict:
        """
        Obtiene estadísticas de cada modelo
        
        Returns:
            Dict con stats por modelo
        """
        stats = {}
        
        for name in self.models:
            history = self.performance_history.get(name, [])
            
            if history:
                stats[name] = {
                    'weight': self.weights.get(name, 0.0),
                    'avg_performance': np.mean(history),
                    'recent_performance': np.mean(history[-10:]) if len(history) >= 10 else np.mean(history),
                    'total_predictions': len(history)
                }
            else:
                stats[name] = {
                    'weight': self.weights.get(name, 0.0),
                    'avg_performance': 0.0,
                    'recent_performance': 0.0,
                    'total_predictions': 0
                }
        
        return stats
    
    def get_consensus_strength(self, votes: Dict) -> float:
        """
        Calcula la fuerza del consenso
        
        Args:
            votes: Dict de votos {model: action}
        
        Returns:
            float: Fuerza del consenso (0-1)
        """
        if not votes:
            return 0.0
        
        # Contar votos por acción
        vote_counts = defaultdict(int)
        for action in votes.values():
            vote_counts[action] += 1
        
        # Consenso = % de modelos que votaron por la acción mayoritaria
        max_votes = max(vote_counts.values())
        consensus = max_votes / len(votes)
        
        return consensus
    
    def should_trade(self, prediction: Dict, min_consensus: float = 0.6) -> bool:
        """
        Determina si se debe ejecutar el trade basado en consenso
        
        Args:
            prediction: Predicción del ensemble
            min_consensus: Consenso mínimo requerido
        
        Returns:
            bool: True si hay suficiente consenso
        """
        votes = prediction.get('votes', {})
        consensus = self.get_consensus_strength(votes)
        confidence = prediction.get('confidence', 0.0)
        
        # Requiere consenso Y confianza
        return consensus >= min_consensus and confidence >= 0.6
