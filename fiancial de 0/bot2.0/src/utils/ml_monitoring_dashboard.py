"""
ML Monitoring Dashboard
Panel de monitoreo unificado para todos los sistemas de ML
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.logger import log


class MLMonitoringDashboard:
    """
    Dashboard unificado de monitoreo ML
    
    Centraliza información de:
    - Auto-retrain scheduler
    - A/B testing
    - Model version manager
    - Training notifier
    - Performance metrics
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: Directorio para archivos de estado
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.status_file = self.data_dir / "ml_dashboard_status.json"
        
        log.info("[ML DASHBOARD] Inicializado")
    
    def update_status(
        self,
        scheduler_status: Optional[Dict] = None,
        ab_test_summary: Optional[Dict] = None,
        version_summary: Optional[Dict] = None,
        recent_notifications: Optional[List] = None,
        model_performance: Optional[Dict] = None
    ):
        """
        Actualizar estado del dashboard
        
        Args:
            scheduler_status: Estado del auto-retrain scheduler
            ab_test_summary: Resumen de A/B tests
            version_summary: Resumen de versiones
            recent_notifications: Notificaciones recientes
            model_performance: Métricas de performance actual
        """
        status = {
            'last_update': datetime.now().isoformat(),
            'scheduler': scheduler_status or {},
            'ab_testing': ab_test_summary or {},
            'versions': version_summary or {},
            'notifications': recent_notifications or [],
            'performance': model_performance or {}
        }
        
        # Agregar análisis
        status['analysis'] = self._generate_analysis(status)
        
        # Guardar
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2, default=str)
    
    def _generate_analysis(self, status: Dict) -> Dict:
        """Generar análisis del estado actual"""
        analysis = {
            'health_score': 100,  # 0-100
            'issues': [],
            'recommendations': [],
            'alerts': []
        }
        
        # Analizar scheduler
        if status['scheduler']:
            days_since_retrain = status['scheduler'].get('days_since_retrain', 0)
            if days_since_retrain > 14:
                analysis['health_score'] -= 20
                analysis['issues'].append(f"Modelo sin reentrenar por {days_since_retrain} días")
                analysis['recommendations'].append("Considerar reentrenamiento manual")
        
        # Analizar A/B testing
        if status['ab_testing']:
            replacement_rate = status['ab_testing'].get('replacement_rate', 0)
            if replacement_rate < 0.1 and status['ab_testing'].get('total_tests', 0) > 5:
                analysis['health_score'] -= 15
                analysis['issues'].append("Baja tasa de reemplazo en A/B tests (<10%)")
                analysis['recommendations'].append("Revisar hiperparámetros o estrategia de entrenamiento")
        
        # Analizar performance
        if status['performance']:
            sharpe = status['performance'].get('sharpe_ratio', 0)
            if sharpe < 0.5:
                analysis['health_score'] -= 25
                analysis['alerts'].append("Sharpe ratio bajo (<0.5)")
                analysis['recommendations'].append("Urgente: Reentrenar modelo")
        
        # Analizar notificaciones
        if status['notifications']:
            error_count = sum(
                1 for n in status['notifications']
                if n.get('level') in ['error', 'critical']
            )
            if error_count > 2:
                analysis['health_score'] -= 10
                analysis['alerts'].append(f"{error_count} errores recientes detectados")
        
        # Nivel de salud
        if analysis['health_score'] >= 80:
            analysis['health_level'] = "Excelente"
        elif analysis['health_score'] >= 60:
            analysis['health_level'] = "Bueno"
        elif analysis['health_score'] >= 40:
            analysis['health_level'] = "Regular"
        else:
            analysis['health_level'] = "Crítico"
        
        return analysis
    
    def get_status(self) -> Dict:
        """Obtener estado actual del dashboard"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'last_update': None,
            'scheduler': {},
            'ab_testing': {},
            'versions': {},
            'notifications': [],
            'performance': {},
            'analysis': {
                'health_score': 0,
                'health_level': 'Desconocido',
                'issues': [],
                'recommendations': [],
                'alerts': []
            }
        }
    
    def get_health_report(self) -> str:
        """Generar reporte de salud en texto"""
        status = self.get_status()
        analysis = status.get('analysis', {})
        
        report = []
        report.append("="*60)
        report.append("REPORTE DE SALUD DEL SISTEMA ML")
        report.append("="*60)
        report.append("")
        
        # Health score
        health_score = analysis.get('health_score', 0)
        health_level = analysis.get('health_level', 'Desconocido')
        report.append(f"Salud General: {health_level} ({health_score}/100)")
        report.append("")
        
        # Alertas
        alerts = analysis.get('alerts', [])
        if alerts:
            report.append("🚨 ALERTAS:")
            for alert in alerts:
                report.append(f"  - {alert}")
            report.append("")
        
        # Issues
        issues = analysis.get('issues', [])
        if issues:
            report.append("⚠️  PROBLEMAS DETECTADOS:")
            for issue in issues:
                report.append(f"  - {issue}")
            report.append("")
        
        # Recomendaciones
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            report.append("💡 RECOMENDACIONES:")
            for rec in recommendations:
                report.append(f"  - {rec}")
            report.append("")
        
        # Scheduler
        scheduler = status.get('scheduler', {})
        if scheduler:
            report.append("📅 AUTO-RETRAIN SCHEDULER:")
            report.append(f"  Estado: {'Activo' if scheduler.get('running') else 'Inactivo'}")
            report.append(f"  Días desde retrain: {scheduler.get('days_since_retrain', 'N/A')}")
            report.append(f"  Recomendaciones pendientes: {scheduler.get('pending_recommendations', 0)}")
            report.append("")
        
        # A/B Testing
        ab_test = status.get('ab_testing', {})
        if ab_test:
            report.append("🧪 A/B TESTING:")
            report.append(f"  Tests realizados: {ab_test.get('total_tests', 0)}")
            report.append(f"  Modelos reemplazados: {ab_test.get('models_replaced', 0)}")
            report.append(f"  Tasa de reemplazo: {ab_test.get('replacement_rate', 0):.1%}")
            report.append("")
        
        # Versions
        versions = status.get('versions', {})
        if versions:
            report.append("📦 VERSIONES:")
            report.append(f"  Total versiones: {versions.get('total_versions', 0)}")
            report.append(f"  Versión actual: {versions.get('current_version', 'N/A')}")
            report.append(f"  Mejor versión: {versions.get('best_version', 'N/A')}")
            report.append("")
        
        # Performance
        performance = status.get('performance', {})
        if performance:
            report.append("📈 PERFORMANCE:")
            report.append(f"  Sharpe Ratio: {performance.get('sharpe_ratio', 'N/A')}")
            report.append(f"  Win Rate: {performance.get('win_rate', 'N/A')}")
            report.append(f"  Mean Return: {performance.get('mean_return', 'N/A')}")
            report.append("")
        
        report.append("="*60)
        report.append(f"Última actualización: {status.get('last_update', 'N/A')}")
        report.append("="*60)
        
        return "\n".join(report)
    
    def export_report(self, filepath: str):
        """Exportar reporte a archivo"""
        report = self.get_health_report()
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        log.info(f"📄 Reporte exportado a: {filepath}")
    
    def get_metrics_for_plotting(self) -> Dict:
        """Obtener métricas formateadas para gráficas"""
        status = self.get_status()
        
        return {
            'health_score': status.get('analysis', {}).get('health_score', 0),
            'days_since_retrain': status.get('scheduler', {}).get('days_since_retrain', 0),
            'ab_test_replacement_rate': status.get('ab_testing', {}).get('replacement_rate', 0),
            'total_versions': status.get('versions', {}).get('total_versions', 0),
            'sharpe_ratio': status.get('performance', {}).get('sharpe_ratio', 0),
            'notification_count': len(status.get('notifications', []))
        }
