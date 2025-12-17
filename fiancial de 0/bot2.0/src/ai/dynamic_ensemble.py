"""
Dynamic Ensemble with Auto-Calibration
Ensemble que se adapta automáticamente a cambios de régimen
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json


class DynamicEnsemble:
    """
    Ensemble dinámico que:
    1. Monitorea performance de cada modelo
    2. Ajusta pesos automáticamente
    3. Detecta model drift
    4. Recommenda reentrenamiento
    """
    
    def __init__(
        self,
        models: Dict,
        window_size: int = 50,
        drift_threshold: float = 0.3,
        min_correlation: float = 0.3
    ):
        """
        Args:
            models: Dict con nombre -> instancia del modelo
            window_size: Tamaño de ventana móvil para cálculo de R²
            drift_threshold: Threshold de R² para detectar drift
            min_correlation: Mínima correlación entre modelos
        """
        self.models = models
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.min_correlation = min_correlation
        
        # Histórico de predicciones y actuals
        self.prediction_history = {name: deque(maxlen=window_size) for name in models}
        self.actual_history = deque(maxlen=window_size)
        
        # Pesos iniciales (iguales)
        n_models = len(models)
        self.weights = {name: 1.0 / n_models for name in models}
        self.weight_history = []
        
        # Performance metrics
        self.performance = {name: {} for name in models}
        self.model_status = {name: 'ACTIVE' for name in models}
        
        # Detección de drift
        self.drift_history = {name: deque(maxlen=20) for name in models}
        
        print(f"[DYNAMIC ENSEMBLE] Inicializado con {n_models} modelos")
        print(f"Pesos iniciales: {self.weights}")
    
    def update(
        self,
        model_predictions: Dict[str, float],
        actual_value: float
    ) -> None:
        """
        Actualizar ensemble con nueva predicción y valor actual
        
        Args:
            model_predictions: Dict con nombre -> predicción del modelo
            actual_value: Valor real observado
        """
        # Guardar histórico
        for name, pred in model_predictions.items():
            self.prediction_history[name].append(pred)
        self.actual_history.append(actual_value)
        
        # Recalcular pesos si tenemos suficientes datos
        if len(self.actual_history) >= 10:
            self._recalculate_weights()
            self._detect_drift()
    
    def _recalculate_weights(self) -> None:
        """Recalcular pesos basado en performance reciente"""
        
        actuals = np.array(list(self.actual_history))
        
        # Calcular R² para cada modelo en ventana móvil
        r2_scores = {}
        
        for name in self.models:
            preds = np.array(list(self.prediction_history[name]))
            
            # Asegurar misma longitud
            if len(preds) == len(actuals):
                # Calcular R²
                ss_res = np.sum((actuals - preds) ** 2)
                ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
                
                r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                r2_scores[name] = max(0, r2)  # Asegurar positivo
            else:
                r2_scores[name] = 0.0
        
        # Guardar scores
        for name, score in r2_scores.items():
            self.performance[name]['r2_score'] = score
            self.drift_history[name].append(score)
        
        # Convertir R² a pesos (softmax)
        scores = np.array([r2_scores[name] for name in self.models])
        
        # Si todos los scores son bajos, usar pesos iguales
        if np.max(scores) < 0.1:
            new_weights = {name: 1.0 / len(self.models) for name in self.models}
        else:
            # Softmax con temperatura
            scores_normalized = np.clip(scores, 0, None)
            weights_array = np.exp(scores_normalized * 2) / np.sum(np.exp(scores_normalized * 2))
            new_weights = {name: float(w) for name, w in zip(self.models.keys(), weights_array)}
        
        # Suavizar cambios de peso (evitar cambios bruscos)
        old_weights = self.weights.copy()
        alpha = 0.3  # Factor de suavizado
        
        self.weights = {
            name: alpha * new_weights[name] + (1 - alpha) * old_weights[name]
            for name in self.models
        }
        
        # Normalizar para que sumen 1
        weight_sum = sum(self.weights.values())
        self.weights = {name: w / weight_sum for name, w in self.weights.items()}
        
        # Guardar en histórico
        self.weight_history.append({
            'timestamp': datetime.now().isoformat(),
            'weights': self.weights.copy(),
            'r2_scores': r2_scores.copy()
        })
    
    def _detect_drift(self) -> None:
        """Detectar model drift y cambios de régimen"""
        
        for name in self.models:
            recent_scores = list(self.drift_history[name])[-5:]
            
            if len(recent_scores) >= 5:
                # Trend: ¿el performance está bajando?
                trend = recent_scores[-1] - recent_scores[0]
                
                # Media reciente
                mean_recent = np.mean(recent_scores[-3:])
                
                # Detección de drift
                if mean_recent < self.drift_threshold:
                    self.model_status[name] = 'DRIFTED'
                    
                    if trend < -0.1:
                        print(f"[DRIFT ALERT] {name} detectado drift negativo")
                        print(f"  Scores recientes: {recent_scores}")
                        print(f"  Trend: {trend:.3f}")
                
                elif mean_recent > 0.5:
                    self.model_status[name] = 'ACTIVE'
                else:
                    self.model_status[name] = 'STRUGGLING'
    
    def predict(self, model_predictions: Dict[str, float]) -> Dict:
        """
        Realizar predicción ponderada del ensemble
        
        Args:
            model_predictions: Dict con nombre -> predicción
        
        Returns:
            Dict con acción, confianza y detalles
        """
        
        # Weighted average
        weighted_pred = sum(
            self.weights[name] * model_predictions[name]
            for name in self.models
            if name in model_predictions
        )
        
        # Calcular confianza como correlación de acuerdo entre modelos
        predictions_array = np.array(list(model_predictions.values()))
        if len(predictions_array) > 1:
            # Si todos predicen lo mismo, confianza alta
            std_dev = np.std(predictions_array)
            confidence = max(0, 1 - std_dev)  # Normalizado 0-1
        else:
            confidence = 0.5
        
        return {
            'prediction': float(weighted_pred),
            'confidence': float(confidence),
            'weights': self.weights.copy(),
            'status': self.model_status.copy(),
            'model_predictions': model_predictions.copy()
        }
    
    def get_health_report(self) -> Dict:
        """Reporte de salud del ensemble"""
        
        active_models = sum(1 for s in self.model_status.values() if s == 'ACTIVE')
        drifted_models = sum(1 for s in self.model_status.values() if s == 'DRIFTED')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'active_models': active_models,
            'drifted_models': drifted_models,
            'struggling_models': len(self.models) - active_models - drifted_models,
            'weights': self.weights.copy(),
            'performance': self.performance.copy(),
            'status': self.model_status.copy(),
            'recommendations': []
        }
        
        # Generar recomendaciones
        if drifted_models > 0:
            report['recommendations'].append(
                f"ALERT: {drifted_models} modelos tienen drift detectado. Considera reentrenamiento."
            )
        
        if active_models < len(self.models) * 0.6:
            report['recommendations'].append(
                f"WARNING: Solo {active_models}/{len(self.models)} modelos activos. "
                "Performance del ensemble puede estar comprometido."
            )
        
        # Mejor y peor modelo
        best_model = max(
            self.performance.items(),
            key=lambda x: x[1].get('r2_score', -1)
        )
        worst_model = min(
            self.performance.items(),
            key=lambda x: x[1].get('r2_score', 1)
        )
        
        report['best_model'] = {
            'name': best_model[0],
            'r2': best_model[1].get('r2_score', 0)
        }
        report['worst_model'] = {
            'name': worst_model[0],
            'r2': worst_model[1].get('r2_score', 0)
        }
        
        return report
    
    def should_retrain(self) -> bool:
        """¿Se recomienda reentrenamiento?"""
        drifted = sum(1 for s in self.model_status.values() if s == 'DRIFTED')
        return drifted >= 2 or sum(
            1 for s in self.model_status.values() if s == 'ACTIVE'
        ) < len(self.models) * 0.5
    
    def save_state(self, filepath: str) -> None:
        """Guardar estado del ensemble"""
        state = {
            'weights': self.weights,
            'weight_history': self.weight_history[-10:],  # Últimos 10
            'performance': self.performance,
            'model_status': self.model_status,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self, filepath: str) -> None:
        """Cargar estado del ensemble"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.weights = state['weights']
        self.performance = state['performance']
        self.model_status = state['model_status']
        
        print(f"[DYNAMIC ENSEMBLE] Estado cargado desde {filepath}")
        print(f"Pesos: {self.weights}")


if __name__ == "__main__":
    # Test
    print("Testing Dynamic Ensemble...")
    
    # Simular 4 modelos
    models = {
        'ppo': None,
        'sac': None,
        'xgboost': None,
        'lstm': None
    }
    
    ensemble = DynamicEnsemble(models, window_size=50)
    
    # Simular 100 predicciones
    np.random.seed(42)
    
    for i in range(100):
        # Generar valor actual
        actual = np.sin(i / 10) + np.random.randn() * 0.1
        
        # Generar predicciones (algunos buenos, otros malos)
        preds = {
            'ppo': actual + np.random.randn() * 0.05,      # Bueno
            'sac': actual + np.random.randn() * 0.08,      # Medio
            'xgboost': actual + np.random.randn() * 0.15,  # Peor
            'lstm': actual + np.random.randn() * 0.06      # Bueno
        }
        
        ensemble.update(preds, actual)
    
    # Mostrar reporte final
    report = ensemble.get_health_report()
    
    print("\n" + "="*60)
    print("DYNAMIC ENSEMBLE HEALTH REPORT")
    print("="*60)
    print(f"Active models: {report['active_models']}/{len(models)}")
    print(f"Drifted models: {report['drifted_models']}")
    print(f"\nWeights:")
    for name, weight in report['weights'].items():
        print(f"  {name}: {weight:.4f}")
    print(f"\nPerformance (R²):")
    for name, perf in report['performance'].items():
        print(f"  {name}: {perf.get('r2_score', 0):.4f}")
    print(f"\nBest model: {report['best_model']['name']} (R²={report['best_model']['r2']:.4f})")
    print(f"Worst model: {report['worst_model']['name']} (R²={report['worst_model']['r2']:.4f})")
    print(f"\nShould retrain: {ensemble.should_retrain()}")
    print("="*60)
