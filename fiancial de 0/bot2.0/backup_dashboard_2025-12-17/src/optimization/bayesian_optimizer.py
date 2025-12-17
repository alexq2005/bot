"""
Bayesian Optimizer
Optimización Bayesiana de hiperparámetros usando Optuna
"""

import optuna
from typing import Dict, List, Callable
import numpy as np
from datetime import datetime
import json
import os


class BayesianOptimizer:
    """
    Optimizador Bayesiano para hiperparámetros del bot
    
    Optimiza automáticamente:
    - Umbrales de RSI
    - Períodos de MACD
    - Niveles de riesgo
    - Pesos del ensemble
    - Thresholds de consenso
    """
    
    def __init__(
        self,
        objective_metric: str = 'sharpe_ratio',
        n_trials: int = 100,
        study_name: str = 'trading_bot_optimization'
    ):
        """
        Inicializa el optimizador
        
        Args:
            objective_metric: Métrica a optimizar
            n_trials: Número de pruebas
            study_name: Nombre del estudio
        """
        self.objective_metric = objective_metric
        self.n_trials = n_trials
        self.study_name = study_name
        
        # Crear directorio para estudios
        os.makedirs('./optimization_studies', exist_ok=True)
        
        # Crear estudio
        self.study = optuna.create_study(
            study_name=study_name,
            direction='maximize',  # Maximizar Sharpe Ratio
            storage=f'sqlite:///./optimization_studies/{study_name}.db',
            load_if_exists=True
        )
        
        print(f"🔧 Bayesian Optimizer inicializado")
        print(f"   Métrica objetivo: {objective_metric}")
        print(f"   Trials: {n_trials}")
    
    def define_search_space(self, trial: optuna.Trial) -> Dict:
        """
        Define el espacio de búsqueda de hiperparámetros
        
        Args:
            trial: Trial de Optuna
        
        Returns:
            Dict con parámetros sugeridos
        """
        params = {
            # Indicadores técnicos
            'rsi_period': trial.suggest_int('rsi_period', 10, 20),
            'rsi_oversold': trial.suggest_int('rsi_oversold', 20, 35),
            'rsi_overbought': trial.suggest_int('rsi_overbought', 65, 80),
            
            'macd_fast': trial.suggest_int('macd_fast', 8, 15),
            'macd_slow': trial.suggest_int('macd_slow', 20, 30),
            'macd_signal': trial.suggest_int('macd_signal', 7, 12),
            
            'atr_period': trial.suggest_int('atr_period', 10, 20),
            
            # Gestión de riesgo
            'risk_per_trade': trial.suggest_float('risk_per_trade', 0.5, 5.0),
            'max_position_size': trial.suggest_float('max_position_size', 10.0, 30.0),
            'stop_loss_multiplier': trial.suggest_float('stop_loss_multiplier', 1.5, 3.0),
            
            # Pesos del ensemble
            'weight_technical': trial.suggest_float('weight_technical', 0.1, 0.5),
            'weight_rl': trial.suggest_float('weight_rl', 0.1, 0.5),
            'weight_sentiment': trial.suggest_float('weight_sentiment', 0.1, 0.4),
            'weight_alt_data': trial.suggest_float('weight_alt_data', 0.05, 0.3),
            
            # Thresholds
            'consensus_threshold': trial.suggest_float('consensus_threshold', 0.5, 0.8),
            'min_confidence': trial.suggest_float('min_confidence', 0.5, 0.8),
        }
        
        # Normalizar pesos del ensemble
        total_weight = (
            params['weight_technical'] +
            params['weight_rl'] +
            params['weight_sentiment'] +
            params['weight_alt_data']
        )
        
        params['weight_technical'] /= total_weight
        params['weight_rl'] /= total_weight
        params['weight_sentiment'] /= total_weight
        params['weight_alt_data'] /= total_weight
        
        return params
    
    def optimize(
        self,
        objective_function: Callable,
        n_trials: int = None
    ) -> Dict:
        """
        Ejecuta optimización
        
        Args:
            objective_function: Función objetivo que retorna métrica
            n_trials: Número de trials (usa default si None)
        
        Returns:
            Dict con mejores parámetros
        """
        trials = n_trials or self.n_trials
        
        print(f"🔬 Iniciando optimización Bayesiana ({trials} trials)...")
        print(f"   Esto puede tomar varios minutos...")
        
        # Wrapper para la función objetivo
        def wrapped_objective(trial):
            params = self.define_search_space(trial)
            return objective_function(params)
        
        # Optimizar
        self.study.optimize(
            wrapped_objective,
            n_trials=trials,
            show_progress_bar=True
        )
        
        # Mejores parámetros
        best_params = self.study.best_params
        best_value = self.study.best_value
        
        print(f"\n✓ Optimización completada!")
        print(f"   Mejor {self.objective_metric}: {best_value:.4f}")
        print(f"\n📊 Mejores parámetros:")
        for param, value in best_params.items():
            print(f"   {param}: {value}")
        
        # Guardar resultados
        self._save_results(best_params, best_value)
        
        return {
            'best_params': best_params,
            'best_value': best_value,
            'n_trials': len(self.study.trials),
            'timestamp': datetime.now()
        }
    
    def _save_results(self, params: Dict, value: float):
        """Guarda resultados de optimización"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'objective_metric': self.objective_metric,
            'best_value': value,
            'best_params': params,
            'n_trials': len(self.study.trials)
        }
        
        filepath = f'./optimization_studies/{self.study_name}_best.json'
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: {filepath}")
    
    def load_best_params(self) -> Dict:
        """Carga los mejores parámetros guardados"""
        
        filepath = f'./optimization_studies/{self.study_name}_best.json'
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                results = json.load(f)
            
            print(f"✓ Parámetros cargados desde: {filepath}")
            print(f"   {self.objective_metric}: {results['best_value']:.4f}")
            
            return results['best_params']
        else:
            print(f"⚠ No se encontraron parámetros guardados")
            return {}
    
    def get_optimization_history(self) -> List[Dict]:
        """Obtiene historial de optimización"""
        
        history = []
        
        for trial in self.study.trials:
            history.append({
                'trial_number': trial.number,
                'value': trial.value,
                'params': trial.params,
                'state': trial.state.name
            })
        
        return history
    
    def plot_optimization_history(self):
        """Genera gráficos de optimización"""
        
        try:
            import plotly
            
            # Gráfico de historia de optimización
            fig1 = optuna.visualization.plot_optimization_history(self.study)
            fig1.write_html(f'./optimization_studies/{self.study_name}_history.html')
            
            # Gráfico de importancia de parámetros
            fig2 = optuna.visualization.plot_param_importances(self.study)
            fig2.write_html(f'./optimization_studies/{self.study_name}_importance.html')
            
            print(f"\n📊 Gráficos guardados en ./optimization_studies/")
            
        except ImportError:
            print("⚠ plotly no instalado. Ejecuta: pip install plotly")
    
    def suggest_next_trial(self) -> Dict:
        """Sugiere próximos parámetros a probar"""
        
        trial = self.study.ask()
        params = self.define_search_space(trial)
        
        return params
