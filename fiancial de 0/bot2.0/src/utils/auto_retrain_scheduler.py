"""
Auto-Retrain Scheduler
Nivel 5: Reentrenamiento Automático
Scheduler que monitorea performance y reentrena modelos automáticamente
"""

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable
import json
from pathlib import Path

from ..ai.rl_agent import RLAgent
from ..ai.dynamic_ensemble import DynamicEnsemble
from ..database.db_manager import db_manager
from ..database.models import Trade, PerformanceMetric
from ..utils.logger import log


class AutoRetrainScheduler:
    """
    Scheduler automático de reentrenamiento
    
    Funcionalidades:
    - Monitorea performance del modelo
    - Detecta degradación de rendimiento
    - Reentrena automáticamente cuando es necesario
    - Mantiene histórico de modelos
    """
    
    def __init__(
        self,
        check_interval_hours: int = 24,
        min_trades_for_retrain: int = 100,
        performance_threshold: float = 0.6,
        drift_threshold: float = 0.3,
        auto_mode: bool = False
    ):
        """
        Args:
            check_interval_hours: Cada cuántas horas verificar si reentrenar
            min_trades_for_retrain: Mínimo de trades para considerar reentrenamiento
            performance_threshold: Threshold de Sharpe ratio para reentrenar
            drift_threshold: Threshold de drift para forzar reentrenamiento
            auto_mode: Si True, reentrena automáticamente. Si False, solo recomienda
        """
        self.check_interval_hours = check_interval_hours
        self.min_trades_for_retrain = min_trades_for_retrain
        self.performance_threshold = performance_threshold
        self.drift_threshold = drift_threshold
        self.auto_mode = auto_mode
        
        self.last_check = datetime.now()
        self.last_retrain = datetime.now()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Estadísticas
        self.retrain_history = []
        self.recommendations = []
        
        # Archivo de configuración
        self.config_file = Path("data/auto_retrain_config.json")
        self._load_config()
        
        log.info("[AUTO-RETRAIN] Scheduler inicializado")
        log.info(f"  Intervalo de chequeo: {check_interval_hours}h")
        log.info(f"  Modo automático: {auto_mode}")
    
    def _load_config(self):
        """Cargar configuración guardada"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                if 'last_retrain' in config:
                    self.last_retrain = datetime.fromisoformat(config['last_retrain'])
                
                if 'retrain_history' in config:
                    self.retrain_history = config['retrain_history']
                
                log.info("[AUTO-RETRAIN] Configuración cargada")
            except Exception as e:
                log.warning(f"[AUTO-RETRAIN] Error cargando config: {e}")
    
    def _save_config(self):
        """Guardar configuración"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'last_retrain': self.last_retrain.isoformat(),
            'retrain_history': self.retrain_history[-10:],  # Últimos 10
            'auto_mode': self.auto_mode
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def should_retrain(self, ensemble: Optional[DynamicEnsemble] = None) -> dict:
        """
        Evalúa si se debe reentrenar
        
        Args:
            ensemble: Ensemble dinámico (opcional)
        
        Returns:
            dict con 'should_retrain', 'reason', 'confidence'
        """
        reasons = []
        confidence = 0.0
        
        # 1. Verificar tiempo desde último reentrenamiento
        days_since_retrain = (datetime.now() - self.last_retrain).days
        if days_since_retrain >= 7:  # Más de 1 semana
            reasons.append(f"Han pasado {days_since_retrain} días desde último retrain")
            confidence += 0.2
        
        # 2. Verificar ensemble drift
        if ensemble and ensemble.should_retrain():
            reasons.append("Ensemble detectó drift en múltiples modelos")
            confidence += 0.4
        
        # 3. Verificar performance reciente
        try:
            recent_metrics = self._get_recent_performance()
            if recent_metrics:
                sharpe = recent_metrics.get('sharpe_ratio', 0)
                win_rate = recent_metrics.get('win_rate', 0)
                
                if sharpe < self.performance_threshold:
                    reasons.append(f"Sharpe ratio bajo: {sharpe:.2f}")
                    confidence += 0.3
                
                if win_rate < 0.45:  # Menos de 45% de victorias
                    reasons.append(f"Win rate bajo: {win_rate:.1%}")
                    confidence += 0.2
        except Exception as e:
            log.warning(f"Error verificando performance: {e}")
        
        # 4. Verificar cantidad de trades para reentrenamiento
        trade_count = self._get_trade_count_since_last_retrain()
        if trade_count < self.min_trades_for_retrain:
            reasons.append(f"Insuficientes trades: {trade_count}/{self.min_trades_for_retrain}")
            confidence = max(0, confidence - 0.3)
        
        should = confidence >= 0.5 and len(reasons) > 0
        
        result = {
            'should_retrain': should,
            'confidence': confidence,
            'reasons': reasons,
            'trade_count': trade_count,
            'days_since_retrain': days_since_retrain
        }
        
        return result
    
    def _get_recent_performance(self) -> dict:
        """Obtener métricas de performance reciente"""
        try:
            # Obtener trades recientes
            with db_manager.get_session() as session:
                # Últimos 30 días
                cutoff = datetime.utcnow() - timedelta(days=30)
                trades = session.query(Trade).filter(
                    Trade.timestamp >= cutoff,
                    Trade.is_closed == True
                ).all()
                
                if not trades:
                    return {}
                
                # Calcular métricas
                pnls = [t.pnl_pct for t in trades if t.pnl_pct is not None]
                wins = sum(1 for pnl in pnls if pnl > 0)
                
                if not pnls:
                    return {}
                
                import numpy as np
                mean_return = np.mean(pnls)
                std_return = np.std(pnls)
                sharpe_ratio = mean_return / std_return if std_return > 0 else 0
                
                return {
                    'sharpe_ratio': sharpe_ratio,
                    'mean_return': mean_return,
                    'win_rate': wins / len(pnls) if pnls else 0,
                    'total_trades': len(trades)
                }
        except Exception as e:
            log.error(f"Error obteniendo performance: {e}")
            return {}
    
    def _get_trade_count_since_last_retrain(self) -> int:
        """Contar trades desde último reentrenamiento"""
        try:
            with db_manager.get_session() as session:
                count = session.query(Trade).filter(
                    Trade.timestamp >= self.last_retrain
                ).count()
                return count
        except:
            return 0
    
    def retrain_model(
        self,
        rl_agent: RLAgent,
        get_training_data_callback: Callable,
        timesteps: int = 50000
    ) -> dict:
        """
        Ejecutar reentrenamiento del modelo
        
        Args:
            rl_agent: Agente RL a reentrenar
            get_training_data_callback: Función que retorna DataFrame de entrenamiento
            timesteps: Timesteps para reentrenamiento
        
        Returns:
            dict con resultados del reentrenamiento
        """
        log.info("=" * 60)
        log.info("[AUTO-RETRAIN] Iniciando reentrenamiento automático")
        log.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # 1. Obtener datos de entrenamiento
            log.info("1. Obteniendo datos de entrenamiento...")
            df = get_training_data_callback()
            
            if df is None or len(df) < 100:
                log.error("❌ Datos insuficientes para reentrenamiento")
                return {'success': False, 'error': 'Insufficient data'}
            
            log.info(f"   ✓ Dataset: {len(df)} filas")
            
            # 2. Guardar modelo anterior (backup)
            log.info("2. Respaldando modelo actual...")
            backup_path = f"{rl_agent.model_path}_backup_{int(time.time())}"
            if os.path.exists(f"{rl_agent.model_path}.zip"):
                import shutil
                shutil.copy(f"{rl_agent.model_path}.zip", f"{backup_path}.zip")
                log.info(f"   ✓ Backup: {backup_path}")
            
            # 3. Entrenar nuevo modelo
            log.info(f"3. Entrenando modelo ({timesteps} timesteps)...")
            rl_agent.train(df, total_timesteps=timesteps)
            log.info("   ✓ Entrenamiento completado")
            
            # 4. Evaluar nuevo modelo
            log.info("4. Evaluando nuevo modelo...")
            metrics = rl_agent.evaluate(df)
            log.info(f"   ✓ Total Return: {metrics.get('total_return_pct', 0):.2f}%")
            
            # 5. Actualizar estadísticas
            self.last_retrain = datetime.now()
            duration = (self.last_retrain - start_time).total_seconds()
            
            retrain_record = {
                'timestamp': self.last_retrain.isoformat(),
                'duration_seconds': duration,
                'timesteps': timesteps,
                'metrics': metrics,
                'backup_path': backup_path
            }
            
            self.retrain_history.append(retrain_record)
            self._save_config()
            
            log.info("=" * 60)
            log.info("✅ Reentrenamiento completado exitosamente")
            log.info(f"   Duración: {duration:.1f}s")
            log.info("=" * 60)
            
            return {
                'success': True,
                'metrics': metrics,
                'duration': duration,
                'backup_path': backup_path
            }
            
        except Exception as e:
            log.error(f"❌ Error en reentrenamiento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_and_retrain(
        self,
        rl_agent: RLAgent,
        ensemble: Optional[DynamicEnsemble],
        get_training_data_callback: Callable
    ) -> dict:
        """
        Verificar si se debe reentrenar y ejecutar si corresponde
        
        Args:
            rl_agent: Agente RL
            ensemble: Ensemble dinámico
            get_training_data_callback: Callback para obtener datos
        
        Returns:
            dict con resultado de la verificación/reentrenamiento
        """
        self.last_check = datetime.now()
        
        # Evaluar si se debe reentrenar
        evaluation = self.should_retrain(ensemble)
        
        log.info("[AUTO-RETRAIN] Evaluación de reentrenamiento:")
        log.info(f"  Debería reentrenar: {evaluation['should_retrain']}")
        log.info(f"  Confianza: {evaluation['confidence']:.2f}")
        log.info(f"  Razones: {', '.join(evaluation['reasons'])}")
        
        if evaluation['should_retrain']:
            if self.auto_mode:
                # Ejecutar reentrenamiento automático
                log.info("[AUTO-RETRAIN] Modo automático: Ejecutando reentrenamiento")
                result = self.retrain_model(rl_agent, get_training_data_callback)
                evaluation['retrain_result'] = result
            else:
                # Solo recomendar
                log.info("[AUTO-RETRAIN] Modo manual: Reentrenamiento recomendado")
                recommendation = {
                    'timestamp': datetime.now().isoformat(),
                    'evaluation': evaluation
                }
                self.recommendations.append(recommendation)
                evaluation['action'] = 'recommendation_only'
        else:
            log.info("[AUTO-RETRAIN] No es necesario reentrenar en este momento")
        
        return evaluation
    
    def start_scheduler(
        self,
        rl_agent: RLAgent,
        ensemble: Optional[DynamicEnsemble],
        get_training_data_callback: Callable
    ):
        """Iniciar scheduler en thread separado"""
        if self.running:
            log.warning("[AUTO-RETRAIN] Scheduler ya está corriendo")
            return
        
        self.running = True
        
        def scheduler_loop():
            log.info("[AUTO-RETRAIN] Scheduler iniciado")
            
            while self.running:
                try:
                    # Dormir por intervalo de chequeo
                    time.sleep(self.check_interval_hours * 3600)
                    
                    if not self.running:
                        break
                    
                    # Verificar y reentrenar si es necesario
                    self.check_and_retrain(rl_agent, ensemble, get_training_data_callback)
                    
                except Exception as e:
                    log.error(f"[AUTO-RETRAIN] Error en scheduler loop: {e}")
        
        self.thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.thread.start()
        
        log.info(f"[AUTO-RETRAIN] Scheduler corriendo (intervalo: {self.check_interval_hours}h)")
    
    def stop_scheduler(self):
        """Detener scheduler"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            log.info("[AUTO-RETRAIN] Scheduler detenido")
    
    def get_status(self) -> dict:
        """Obtener estado del scheduler"""
        return {
            'running': self.running,
            'auto_mode': self.auto_mode,
            'last_check': self.last_check.isoformat(),
            'last_retrain': self.last_retrain.isoformat(),
            'days_since_retrain': (datetime.now() - self.last_retrain).days,
            'retrain_count': len(self.retrain_history),
            'pending_recommendations': len(self.recommendations),
            'check_interval_hours': self.check_interval_hours
        }
