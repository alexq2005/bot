"""
Training Notifier
Sistema de notificaciones para eventos de entrenamiento y reentrenamiento
"""

import os
from datetime import datetime
from typing import Optional, List
from enum import Enum

from ..utils.logger import log


class NotificationLevel(Enum):
    """Niveles de notificación"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TrainingNotifier:
    """
    Sistema de notificaciones para eventos de ML
    
    Soporta múltiples canales:
    - Console (logs)
    - Email (futuro)
    - Slack (futuro)
    - Telegram (futuro)
    - Dashboard (archivo de estado)
    """
    
    def __init__(
        self,
        enable_console: bool = True,
        enable_dashboard: bool = True,
        dashboard_file: str = "data/training_notifications.json"
    ):
        """
        Args:
            enable_console: Habilitar notificaciones en consola
            enable_dashboard: Habilitar notificaciones para dashboard
            dashboard_file: Archivo para notificaciones del dashboard
        """
        self.enable_console = enable_console
        self.enable_dashboard = enable_dashboard
        self.dashboard_file = dashboard_file
        
        self.notifications_history = []
        
        log.info("[NOTIFIER] Sistema de notificaciones inicializado")
    
    def notify(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        details: Optional[dict] = None
    ):
        """
        Enviar notificación
        
        Args:
            level: Nivel de notificación
            title: Título
            message: Mensaje
            details: Detalles adicionales (opcional)
        """
        notification = {
            'timestamp': datetime.now().isoformat(),
            'level': level.value,
            'title': title,
            'message': message,
            'details': details or {}
        }
        
        # Agregar a historial
        self.notifications_history.append(notification)
        
        # Console
        if self.enable_console:
            self._notify_console(level, title, message, details)
        
        # Dashboard
        if self.enable_dashboard:
            self._notify_dashboard(notification)
    
    def _notify_console(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        details: Optional[dict]
    ):
        """Notificar en consola"""
        emoji_map = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.SUCCESS: "✅",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨"
        }
        
        emoji = emoji_map.get(level, "📢")
        
        log_message = f"{emoji} {title}: {message}"
        
        if level == NotificationLevel.ERROR or level == NotificationLevel.CRITICAL:
            log.error(log_message)
        elif level == NotificationLevel.WARNING:
            log.warning(log_message)
        else:
            log.info(log_message)
        
        if details:
            log.info(f"   Detalles: {details}")
    
    def _notify_dashboard(self, notification: dict):
        """Guardar notificación para dashboard"""
        import json
        from pathlib import Path
        
        file_path = Path(self.dashboard_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar notificaciones existentes
        notifications = []
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    notifications = json.load(f)
            except:
                pass
        
        # Agregar nueva
        notifications.append(notification)
        
        # Mantener solo las últimas 50
        notifications = notifications[-50:]
        
        # Guardar
        with open(file_path, 'w') as f:
            json.dump(notifications, f, indent=2)
    
    # Métodos de conveniencia
    
    def notify_training_start(self, timesteps: int, symbol: str):
        """Notificar inicio de entrenamiento"""
        self.notify(
            NotificationLevel.INFO,
            "Entrenamiento Iniciado",
            f"Iniciando entrenamiento de {timesteps:,} timesteps para {symbol}",
            {'timesteps': timesteps, 'symbol': symbol}
        )
    
    def notify_training_complete(
        self,
        duration_seconds: float,
        metrics: dict
    ):
        """Notificar fin de entrenamiento"""
        self.notify(
            NotificationLevel.SUCCESS,
            "Entrenamiento Completado",
            f"Entrenamiento finalizado en {duration_seconds:.1f}s",
            {
                'duration_seconds': duration_seconds,
                'metrics': metrics
            }
        )
    
    def notify_training_failed(self, error: str):
        """Notificar fallo en entrenamiento"""
        self.notify(
            NotificationLevel.ERROR,
            "Entrenamiento Fallido",
            f"Error durante entrenamiento: {error}",
            {'error': error}
        )
    
    def notify_model_improved(
        self,
        improvement_pct: float,
        old_metric: float,
        new_metric: float
    ):
        """Notificar mejora de modelo"""
        self.notify(
            NotificationLevel.SUCCESS,
            "Modelo Mejorado",
            f"Nuevo modelo {improvement_pct:.1f}% mejor ({old_metric:.2f} → {new_metric:.2f})",
            {
                'improvement_pct': improvement_pct,
                'old_metric': old_metric,
                'new_metric': new_metric
            }
        )
    
    def notify_model_degraded(
        self,
        degradation_pct: float,
        old_metric: float,
        new_metric: float
    ):
        """Notificar degradación de modelo"""
        self.notify(
            NotificationLevel.WARNING,
            "Modelo Degradado",
            f"Nuevo modelo {degradation_pct:.1f}% peor ({old_metric:.2f} → {new_metric:.2f})",
            {
                'degradation_pct': degradation_pct,
                'old_metric': old_metric,
                'new_metric': new_metric
            }
        )
    
    def notify_drift_detected(self, model_name: str, r2_score: float):
        """Notificar drift detectado"""
        self.notify(
            NotificationLevel.WARNING,
            "Drift Detectado",
            f"Modelo {model_name} muestra drift (R²={r2_score:.3f})",
            {'model': model_name, 'r2_score': r2_score}
        )
    
    def notify_auto_retrain_triggered(self, reasons: List[str]):
        """Notificar reentrenamiento automático"""
        self.notify(
            NotificationLevel.INFO,
            "Reentrenamiento Automático Activado",
            f"Reentrenamiento iniciado. Razones: {', '.join(reasons)}",
            {'reasons': reasons}
        )
    
    def notify_ab_test_result(
        self,
        model_replaced: bool,
        improvement: float
    ):
        """Notificar resultado de A/B test"""
        if model_replaced:
            self.notify(
                NotificationLevel.SUCCESS,
                "A/B Test: Modelo Reemplazado",
                f"Nuevo modelo adoptado con {improvement:.1f}% de mejora",
                {'replaced': True, 'improvement': improvement}
            )
        else:
            self.notify(
                NotificationLevel.INFO,
                "A/B Test: Modelo Mantenido",
                "Modelo actual supera al nuevo candidato",
                {'replaced': False}
            )
    
    def notify_version_saved(self, version_id: str, tag: Optional[str]):
        """Notificar versión guardada"""
        tag_msg = f" (tag: {tag})" if tag else ""
        self.notify(
            NotificationLevel.INFO,
            "Versión Guardada",
            f"Modelo guardado como versión {version_id}{tag_msg}",
            {'version_id': version_id, 'tag': tag}
        )
    
    def notify_rollback(self, version_id: str):
        """Notificar rollback"""
        self.notify(
            NotificationLevel.WARNING,
            "Rollback Ejecutado",
            f"Restaurado a versión {version_id}",
            {'version_id': version_id}
        )
    
    def notify_low_performance(self, metric: str, value: float, threshold: float):
        """Notificar performance bajo"""
        self.notify(
            NotificationLevel.WARNING,
            "Performance Bajo",
            f"{metric}={value:.2f} está por debajo del threshold ({threshold:.2f})",
            {
                'metric': metric,
                'value': value,
                'threshold': threshold
            }
        )
    
    def get_recent_notifications(self, limit: int = 10) -> List[dict]:
        """Obtener notificaciones recientes"""
        return self.notifications_history[-limit:]
    
    def clear_history(self):
        """Limpiar historial de notificaciones"""
        self.notifications_history = []
        log.info("[NOTIFIER] Historial limpiado")
