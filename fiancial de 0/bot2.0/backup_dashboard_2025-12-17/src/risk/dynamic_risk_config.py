"""
Dynamic Risk Configurator
Auto-configura niveles de riesgo basándose en rendimiento
"""

from typing import Dict
from datetime import datetime, timedelta
import numpy as np


class DynamicRiskConfigurator:
    """
    Ajusta automáticamente los niveles de riesgo del bot
    basándose en su rendimiento histórico
    """
    
    def __init__(
        self,
        initial_risk_per_trade: float = 2.0,
        initial_max_position: float = 20.0,
        min_risk: float = 0.5,
        max_risk: float = 5.0,
        adjustment_period_days: int = 7
    ):
        """
        Inicializa el configurador dinámico de riesgo
        
        Args:
            initial_risk_per_trade: Riesgo inicial por trade (%)
            initial_max_position: Posición máxima inicial (%)
            min_risk: Riesgo mínimo permitido (%)
            max_risk: Riesgo máximo permitido (%)
            adjustment_period_days: Días para evaluar rendimiento
        """
        self.current_risk_per_trade = initial_risk_per_trade
        self.current_max_position = initial_max_position
        self.min_risk = min_risk
        self.max_risk = max_risk
        self.adjustment_period_days = adjustment_period_days
        
        # Tracking
        self.last_adjustment = datetime.now()
        self.performance_history = []
    
    def analyze_performance(self, trades: list) -> Dict:
        """
        Analiza el rendimiento reciente del bot
        
        Args:
            trades: Lista de trades recientes
        
        Returns:
            Dict con métricas de rendimiento
        """
        if not trades:
            return {
                'win_rate': 0.0,
                'avg_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'consistency': 0.0
            }
        
        # Filtrar trades cerrados
        closed_trades = [t for t in trades if t.get('pnl', 0) != 0]
        
        if not closed_trades:
            return {
                'win_rate': 0.0,
                'avg_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'consistency': 0.0
            }
        
        # Win rate
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / len(closed_trades) * 100
        
        # Retorno promedio
        returns = [t.get('pnl_pct', 0) for t in closed_trades]
        avg_return = np.mean(returns)
        
        # Sharpe ratio simplificado
        if len(returns) > 1:
            sharpe = avg_return / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        # Max drawdown
        cumulative = np.cumsum([t.get('pnl', 0) for t in closed_trades])
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max * 100
        max_drawdown = abs(np.min(drawdown)) if len(drawdown) > 0 else 0
        
        # Consistencia (% de trades con ganancia > 0)
        consistency = win_rate
        
        return {
            'win_rate': win_rate,
            'avg_return': avg_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'consistency': consistency,
            'total_trades': len(closed_trades)
        }
    
    def calculate_risk_score(self, performance: Dict) -> float:
        """
        Calcula un score de riesgo basado en rendimiento
        
        Score alto = Bot funcionando bien = Puede aumentar riesgo
        Score bajo = Bot con problemas = Debe reducir riesgo
        
        Args:
            performance: Métricas de rendimiento
        
        Returns:
            float: Score de 0 a 100
        """
        # Pesos para cada métrica
        weights = {
            'win_rate': 0.3,
            'sharpe_ratio': 0.25,
            'avg_return': 0.25,
            'max_drawdown': 0.2
        }
        
        # Normalizar métricas a 0-100
        win_rate_score = min(performance['win_rate'], 100)
        
        # Sharpe ratio (normalizar: 0-3 → 0-100)
        sharpe_score = min(max(performance['sharpe_ratio'] / 3 * 100, 0), 100)
        
        # Avg return (normalizar: -10% a +10% → 0-100)
        avg_return_score = min(max((performance['avg_return'] + 10) / 20 * 100, 0), 100)
        
        # Max drawdown (invertir: menos drawdown = mejor score)
        drawdown_score = max(100 - performance['max_drawdown'] * 5, 0)
        
        # Score total ponderado
        total_score = (
            win_rate_score * weights['win_rate'] +
            sharpe_score * weights['sharpe_ratio'] +
            avg_return_score * weights['avg_return'] +
            drawdown_score * weights['max_drawdown']
        )
        
        return total_score
    
    def adjust_risk_levels(self, performance: Dict) -> Dict:
        """
        Ajusta automáticamente los niveles de riesgo
        
        Args:
            performance: Métricas de rendimiento
        
        Returns:
            Dict con nuevos niveles de riesgo y razones
        """
        risk_score = self.calculate_risk_score(performance)
        
        # Guardar niveles anteriores
        old_risk = self.current_risk_per_trade
        old_position = self.current_max_position
        
        # Estrategia de ajuste basada en score
        if risk_score >= 80:
            # Rendimiento excelente → Aumentar riesgo moderadamente
            adjustment_factor = 1.15
            reason = "Rendimiento excelente (score: {:.1f}) - Aumentando riesgo".format(risk_score)
        
        elif risk_score >= 60:
            # Rendimiento bueno → Aumentar riesgo ligeramente
            adjustment_factor = 1.05
            reason = "Rendimiento bueno (score: {:.1f}) - Aumentando riesgo levemente".format(risk_score)
        
        elif risk_score >= 40:
            # Rendimiento neutro → Mantener riesgo
            adjustment_factor = 1.0
            reason = "Rendimiento neutro (score: {:.1f}) - Manteniendo riesgo".format(risk_score)
        
        elif risk_score >= 20:
            # Rendimiento malo → Reducir riesgo
            adjustment_factor = 0.85
            reason = "Rendimiento bajo (score: {:.1f}) - Reduciendo riesgo".format(risk_score)
        
        else:
            # Rendimiento muy malo → Reducir riesgo significativamente
            adjustment_factor = 0.70
            reason = "Rendimiento crítico (score: {:.1f}) - Reduciendo riesgo significativamente".format(risk_score)
        
        # Aplicar ajuste
        self.current_risk_per_trade *= adjustment_factor
        self.current_max_position *= adjustment_factor
        
        # Aplicar límites
        self.current_risk_per_trade = max(
            self.min_risk,
            min(self.current_risk_per_trade, self.max_risk)
        )
        
        self.current_max_position = max(
            10.0,  # Mínimo 10% por posición
            min(self.current_max_position, 30.0)  # Máximo 30% por posición
        )
        
        # Actualizar timestamp
        self.last_adjustment = datetime.now()
        
        return {
            'old_risk_per_trade': old_risk,
            'new_risk_per_trade': self.current_risk_per_trade,
            'old_max_position': old_position,
            'new_max_position': self.current_max_position,
            'risk_score': risk_score,
            'adjustment_factor': adjustment_factor,
            'reason': reason,
            'timestamp': self.last_adjustment
        }
    
    def should_adjust(self) -> bool:
        """
        Determina si es momento de ajustar los niveles de riesgo
        
        Returns:
            bool: True si debe ajustar
        """
        days_since_last = (datetime.now() - self.last_adjustment).days
        return days_since_last >= self.adjustment_period_days
    
    def get_current_config(self) -> Dict:
        """
        Obtiene la configuración actual de riesgo
        
        Returns:
            Dict con configuración actual
        """
        return {
            'risk_per_trade': self.current_risk_per_trade,
            'max_position_size': self.current_max_position,
            'last_adjustment': self.last_adjustment,
            'days_until_next': self.adjustment_period_days - (datetime.now() - self.last_adjustment).days
        }
    
    def get_recommendation(self, performance: Dict) -> str:
        """
        Genera recomendación en lenguaje natural
        
        Args:
            performance: Métricas de rendimiento
        
        Returns:
            str: Recomendación
        """
        risk_score = self.calculate_risk_score(performance)
        
        if risk_score >= 80:
            return f"""
🟢 RENDIMIENTO EXCELENTE (Score: {risk_score:.1f}/100)

El bot está funcionando muy bien:
- Win Rate: {performance['win_rate']:.1f}%
- Sharpe Ratio: {performance['sharpe_ratio']:.2f}
- Retorno Promedio: {performance['avg_return']:.2f}%

Recomendación: Aumentar riesgo a {self.current_risk_per_trade * 1.15:.1f}%
"""
        
        elif risk_score >= 60:
            return f"""
🟡 RENDIMIENTO BUENO (Score: {risk_score:.1f}/100)

El bot está funcionando bien:
- Win Rate: {performance['win_rate']:.1f}%
- Sharpe Ratio: {performance['sharpe_ratio']:.2f}

Recomendación: Aumentar riesgo levemente a {self.current_risk_per_trade * 1.05:.1f}%
"""
        
        elif risk_score >= 40:
            return f"""
⚪ RENDIMIENTO NEUTRO (Score: {risk_score:.1f}/100)

El bot está funcionando de forma estable.

Recomendación: Mantener riesgo actual en {self.current_risk_per_trade:.1f}%
"""
        
        elif risk_score >= 20:
            return f"""
🟠 RENDIMIENTO BAJO (Score: {risk_score:.1f}/100)

El bot necesita ajustes:
- Win Rate: {performance['win_rate']:.1f}%
- Max Drawdown: {performance['max_drawdown']:.1f}%

Recomendación: Reducir riesgo a {self.current_risk_per_trade * 0.85:.1f}%
"""
        
        else:
            return f"""
🔴 RENDIMIENTO CRÍTICO (Score: {risk_score:.1f}/100)

El bot está teniendo dificultades:
- Win Rate: {performance['win_rate']:.1f}%
- Max Drawdown: {performance['max_drawdown']:.1f}%

Recomendación: Reducir riesgo significativamente a {self.current_risk_per_trade * 0.70:.1f}%
Considerar revisar estrategia.
"""
