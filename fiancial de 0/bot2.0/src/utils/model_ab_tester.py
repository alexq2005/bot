"""
Model A/B Tester
Nivel 6: Testing A/B de Modelos
Sistema de comparación automática entre modelos
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np

from ..ai.rl_agent import RLAgent
from ..utils.logger import log


class ModelABTester:
    """
    Sistema de A/B Testing para modelos
    
    Funcionalidades:
    - Compara modelo actual vs nuevo modelo
    - Evalúa en datos de validación
    - Decide automáticamente cuál es mejor
    - Mantiene histórico de comparaciones
    """
    
    def __init__(
        self,
        validation_episodes: int = 10,
        significance_threshold: float = 0.05,
        min_improvement: float = 0.02  # 2% mínimo de mejora
    ):
        """
        Args:
            validation_episodes: Número de episodios para validación
            significance_threshold: Threshold de significancia estadística
            min_improvement: Mejora mínima requerida para aceptar nuevo modelo
        """
        self.validation_episodes = validation_episodes
        self.significance_threshold = significance_threshold
        self.min_improvement = min_improvement
        
        # Histórico de tests
        self.test_history = []
        
        # Archivo de resultados
        self.results_file = Path("data/ab_test_results.json")
        self._load_history()
        
        log.info("[A/B TESTER] Inicializado")
        log.info(f"  Episodios de validación: {validation_episodes}")
        log.info(f"  Mejora mínima requerida: {min_improvement*100:.1f}%")
    
    def _load_history(self):
        """Cargar histórico de tests"""
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r') as f:
                    self.test_history = json.load(f)
                log.info(f"[A/B TESTER] Histórico cargado: {len(self.test_history)} tests")
            except Exception as e:
                log.warning(f"[A/B TESTER] Error cargando histórico: {e}")
    
    def _save_history(self):
        """Guardar histórico de tests"""
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.results_file, 'w') as f:
            json.dump(self.test_history[-50:], f, indent=2, default=str)
    
    def evaluate_model(
        self,
        model: RLAgent,
        validation_data,
        model_name: str = "Model"
    ) -> Dict:
        """
        Evaluar un modelo en datos de validación
        
        Args:
            model: Modelo a evaluar
            validation_data: DataFrame con datos de validación
            model_name: Nombre del modelo
        
        Returns:
            dict con métricas de evaluación
        """
        log.info(f"[A/B TESTER] Evaluando {model_name}...")
        
        results = []
        
        for episode in range(self.validation_episodes):
            metrics = model.evaluate(validation_data)
            results.append(metrics)
        
        # Agregar métricas
        returns = [r.get('total_return_pct', 0) for r in results]
        final_values = [r.get('final_value', 0) for r in results]
        
        evaluation = {
            'model_name': model_name,
            'episodes': self.validation_episodes,
            'mean_return': float(np.mean(returns)),
            'std_return': float(np.std(returns)),
            'min_return': float(np.min(returns)),
            'max_return': float(np.max(returns)),
            'mean_final_value': float(np.mean(final_values)),
            'sharpe_ratio': float(np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0,
            'consistency': 1.0 - (float(np.std(returns)) / 100.0)  # Normalizado
        }
        
        log.info(f"  ✓ {model_name}:")
        log.info(f"    Mean Return: {evaluation['mean_return']:.2f}%")
        log.info(f"    Std Return: {evaluation['std_return']:.2f}%")
        log.info(f"    Sharpe: {evaluation['sharpe_ratio']:.3f}")
        
        return evaluation
    
    def compare_models(
        self,
        model_a: RLAgent,
        model_b: RLAgent,
        validation_data,
        model_a_name: str = "Current Model",
        model_b_name: str = "New Model"
    ) -> Dict:
        """
        Comparar dos modelos
        
        Args:
            model_a: Modelo actual (baseline)
            model_b: Modelo nuevo (candidato)
            validation_data: Datos de validación
            model_a_name: Nombre del modelo A
            model_b_name: Nombre del modelo B
        
        Returns:
            dict con resultado de comparación
        """
        log.info("=" * 60)
        log.info("[A/B TESTER] Iniciando comparación de modelos")
        log.info("=" * 60)
        
        start_time = time.time()
        
        # Evaluar ambos modelos
        eval_a = self.evaluate_model(model_a, validation_data, model_a_name)
        eval_b = self.evaluate_model(model_b, validation_data, model_b_name)
        
        # Comparar métricas clave
        improvement_return = eval_b['mean_return'] - eval_a['mean_return']
        improvement_sharpe = eval_b['sharpe_ratio'] - eval_a['sharpe_ratio']
        improvement_consistency = eval_b['consistency'] - eval_a['consistency']
        
        # Realizar test estadístico (t-test simplificado)
        # Comparar medias con significancia estadística
        mean_diff = improvement_return
        std_combined = np.sqrt(eval_a['std_return']**2 + eval_b['std_return']**2)
        
        # Z-score aproximado
        z_score = mean_diff / std_combined if std_combined > 0 else 0
        is_significant = abs(z_score) > 1.96  # ~95% de confianza
        
        # Decisión
        is_better = (
            improvement_return > self.min_improvement * 100 and  # Mejora mínima
            is_significant and  # Estadísticamente significativo
            eval_b['sharpe_ratio'] >= eval_a['sharpe_ratio'] * 0.95  # No empeora mucho Sharpe
        )
        
        # Calcular score de mejora (0-100)
        improvement_score = (
            (improvement_return / 100.0) * 40 +  # 40% peso al retorno
            improvement_sharpe * 30 +  # 30% peso a Sharpe
            improvement_consistency * 100 * 30  # 30% peso a consistencia
        )
        improvement_score = max(0, min(100, improvement_score))
        
        duration = time.time() - start_time
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'model_a': eval_a,
            'model_b': eval_b,
            'comparison': {
                'improvement_return_pct': improvement_return,
                'improvement_sharpe': improvement_sharpe,
                'improvement_consistency': improvement_consistency,
                'z_score': float(z_score),
                'is_significant': is_significant,
                'improvement_score': float(improvement_score)
            },
            'decision': {
                'use_new_model': is_better,
                'reason': self._get_decision_reason(
                    is_better,
                    improvement_return,
                    is_significant,
                    improvement_sharpe
                )
            }
        }
        
        # Guardar en histórico
        self.test_history.append(result)
        self._save_history()
        
        # Log resultado
        log.info("")
        log.info("=" * 60)
        log.info("[A/B TESTER] RESULTADO DE COMPARACIÓN")
        log.info("=" * 60)
        log.info(f"Mejora en Retorno: {improvement_return:+.2f}%")
        log.info(f"Mejora en Sharpe: {improvement_sharpe:+.3f}")
        log.info(f"Z-Score: {z_score:.2f}")
        log.info(f"Significativo: {is_significant}")
        log.info(f"Score de Mejora: {improvement_score:.1f}/100")
        log.info("")
        log.info(f"DECISIÓN: {'✅ USAR NUEVO MODELO' if is_better else '❌ MANTENER MODELO ACTUAL'}")
        log.info(f"Razón: {result['decision']['reason']}")
        log.info("=" * 60)
        
        return result
    
    def _get_decision_reason(
        self,
        is_better: bool,
        improvement_return: float,
        is_significant: bool,
        improvement_sharpe: float
    ) -> str:
        """Generar razón de la decisión"""
        if is_better:
            return (
                f"Nuevo modelo muestra mejora significativa: "
                f"{improvement_return:+.2f}% retorno, "
                f"{improvement_sharpe:+.3f} Sharpe"
            )
        else:
            reasons = []
            if improvement_return < self.min_improvement * 100:
                reasons.append(f"mejora insuficiente ({improvement_return:.2f}% < {self.min_improvement*100:.1f}%)")
            if not is_significant:
                reasons.append("no es estadísticamente significativo")
            if improvement_sharpe < 0:
                reasons.append(f"Sharpe empeora ({improvement_sharpe:.3f})")
            
            return "Nuevo modelo " + " y ".join(reasons)
    
    def auto_replace_if_better(
        self,
        current_model_path: str,
        new_model_path: str,
        validation_data,
        backup: bool = True
    ) -> Dict:
        """
        Comparar y reemplazar automáticamente si el nuevo es mejor
        
        Args:
            current_model_path: Path al modelo actual
            new_model_path: Path al modelo nuevo
            validation_data: Datos de validación
            backup: Si crear backup del modelo actual
        
        Returns:
            dict con resultado
        """
        log.info("[A/B TESTER] Iniciando comparación automática")
        
        # Cargar modelos
        model_current = RLAgent(model_path=current_model_path)
        model_new = RLAgent(model_path=new_model_path)
        
        if not model_current.load():
            log.error("❌ No se pudo cargar modelo actual")
            return {'success': False, 'error': 'Failed to load current model'}
        
        if not model_new.load():
            log.error("❌ No se pudo cargar modelo nuevo")
            return {'success': False, 'error': 'Failed to load new model'}
        
        # Comparar
        comparison = self.compare_models(
            model_current,
            model_new,
            validation_data,
            "Current Model",
            "New Model"
        )
        
        # Si el nuevo es mejor, reemplazar
        if comparison['decision']['use_new_model']:
            log.info("[A/B TESTER] Reemplazando modelo actual...")
            
            try:
                # Backup del modelo actual
                if backup:
                    backup_path = f"{current_model_path}_backup_{int(time.time())}.zip"
                    import shutil
                    if os.path.exists(f"{current_model_path}.zip"):
                        shutil.copy(f"{current_model_path}.zip", backup_path)
                        log.info(f"  ✓ Backup creado: {backup_path}")
                
                # Copiar nuevo modelo sobre el actual
                import shutil
                shutil.copy(f"{new_model_path}.zip", f"{current_model_path}.zip")
                log.info("  ✓ Modelo reemplazado exitosamente")
                
                return {
                    'success': True,
                    'replaced': True,
                    'comparison': comparison,
                    'backup_path': backup_path if backup else None
                }
                
            except Exception as e:
                log.error(f"❌ Error reemplazando modelo: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'comparison': comparison
                }
        else:
            log.info("[A/B TESTER] Manteniendo modelo actual")
            return {
                'success': True,
                'replaced': False,
                'comparison': comparison,
                'reason': comparison['decision']['reason']
            }
    
    def get_test_history_summary(self) -> Dict:
        """Obtener resumen del histórico de tests"""
        if not self.test_history:
            return {
                'total_tests': 0,
                'models_replaced': 0,
                'average_improvement': 0
            }
        
        replaced_count = sum(
            1 for test in self.test_history
            if test['decision']['use_new_model']
        )
        
        improvements = [
            test['comparison']['improvement_return_pct']
            for test in self.test_history
        ]
        
        return {
            'total_tests': len(self.test_history),
            'models_replaced': replaced_count,
            'models_kept': len(self.test_history) - replaced_count,
            'replacement_rate': replaced_count / len(self.test_history) if self.test_history else 0,
            'average_improvement': float(np.mean(improvements)),
            'best_improvement': float(np.max(improvements)) if improvements else 0,
            'worst_improvement': float(np.min(improvements)) if improvements else 0
        }
    
    def get_recommendation(self) -> str:
        """Obtener recomendación basada en histórico"""
        summary = self.get_test_history_summary()
        
        if summary['total_tests'] == 0:
            return "No hay histórico de tests. Ejecutar primer test A/B."
        
        if summary['replacement_rate'] > 0.7:
            return "Alta tasa de reemplazos. Los nuevos modelos mejoran consistentemente."
        elif summary['replacement_rate'] > 0.3:
            return "Tasa moderada de reemplazos. Sistema funcionando correctamente."
        else:
            return "Baja tasa de reemplazos. Considerar ajustar hiperparámetros o estrategia de entrenamiento."
