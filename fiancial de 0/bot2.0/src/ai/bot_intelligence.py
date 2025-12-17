"""
Bot Intelligence Analyzer
Sistema de auto-análisis y mejora continua del trading bot
VSCode no puede hacer esto 😎
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path


class BotIntelligence:
    """Analizador inteligente del sistema de trading"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.analysis = {}
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Ejecuta análisis completo del sistema"""
        print("🧠 Iniciando análisis de inteligencia del bot...")
        
        self.analysis = {
            'timestamp': datetime.now().isoformat(),
            'performance': self._analyze_performance(),
            'strategy_effectiveness': self._analyze_strategies(),
            'risk_metrics': self._analyze_risk(),
            'optimization_opportunities': self._find_optimizations(),
            'predictions': self._generate_predictions(),
            'recommendations': self._generate_recommendations()
        }
        
        return self.analysis
    
    def _analyze_performance(self) -> Dict:
        """Analiza rendimiento histórico del bot"""
        try:
            from ..database.models import Trade
            
            with self.db.get_session() as session:
                # Últimos 30 días
                since = datetime.now() - timedelta(days=30)
                trades = session.query(Trade).filter(
                    Trade.timestamp >= since,
                    Trade.is_closed == True
                ).all()
                
                if not trades:
                    return {'status': 'insufficient_data'}
                
                # Calcular métricas
                total_trades = len(trades)
                winning_trades = [t for t in trades if t.pnl > 0]
                losing_trades = [t for t in trades if t.pnl <= 0]
                
                total_pnl = sum(t.pnl for t in trades)
                avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
                avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
                
                win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
                
                # Detectar racha actual
                recent_5 = trades[-5:] if len(trades) >= 5 else trades
                recent_wins = sum(1 for t in recent_5 if t.pnl > 0)
                
                streak_status = "🔥 HOT" if recent_wins >= 4 else "⚠️ COLD" if recent_wins <= 1 else "✅ STABLE"
                
                return {
                    'total_trades': total_trades,
                    'win_rate': round(win_rate, 2),
                    'total_pnl': round(total_pnl, 2),
                    'avg_win': round(avg_win, 2),
                    'avg_loss': round(avg_loss, 2),
                    'profit_factor': round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
                    'streak_status': streak_status,
                    'best_trade': max(trades, key=lambda t: t.pnl).pnl if trades else 0,
                    'worst_trade': min(trades, key=lambda t: t.pnl).pnl if trades else 0
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_strategies(self) -> Dict:
        """Analiza efectividad de cada componente de la estrategia"""
        try:
            from ..database.models import Trade
            
            with self.db.get_session() as session:
                trades = session.query(Trade).filter(Trade.is_closed == True).all()
                
                if not trades:
                    return {'status': 'insufficient_data'}
                
                # Agrupar por señal técnica
                by_signal = {}
                for trade in trades:
                    signal = trade.technical_signal or 'UNKNOWN'
                    if signal not in by_signal:
                        by_signal[signal] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
                    
                    if trade.pnl > 0:
                        by_signal[signal]['wins'] += 1
                    else:
                        by_signal[signal]['losses'] += 1
                    by_signal[signal]['total_pnl'] += trade.pnl
                
                # Encontrar mejor y peor señal
                best_signal = max(by_signal.items(), key=lambda x: x[1]['total_pnl'])
                worst_signal = min(by_signal.items(), key=lambda x: x[1]['total_pnl'])
                
                return {
                    'by_signal': by_signal,
                    'best_signal': {'name': best_signal[0], 'pnl': round(best_signal[1]['total_pnl'], 2)},
                    'worst_signal': {'name': worst_signal[0], 'pnl': round(worst_signal[1]['total_pnl'], 2)},
                    'total_signals': len(by_signal)
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_risk(self) -> Dict:
        """Analiza métricas de riesgo"""
        try:
            from ..database.models import Trade, ActivePosition
            
            with self.db.get_session() as session:
                closed_trades = session.query(Trade).filter(Trade.is_closed == True).all()
                active_positions = session.query(ActivePosition).all()
                
                # Calcular drawdown máximo
                equity_curve = []
                running_total = 0
                for trade in sorted(closed_trades, key=lambda t: t.timestamp):
                    running_total += trade.pnl
                    equity_curve.append(running_total)
                
                max_drawdown = 0
                peak = 0
                for value in equity_curve:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak * 100 if peak > 0 else 0
                    max_drawdown = max(max_drawdown, drawdown)
                
                # Exposición actual
                current_exposure = sum(
                    pos.entry_price * pos.quantity 
                    for pos in active_positions
                )
                
                # Riesgo actual (suma de distancias a Stop Loss)
                total_risk = sum(
                    abs(pos.entry_price - pos.stop_loss) * pos.quantity
                    for pos in active_positions
                )
                
                return {
                    'max_drawdown': round(max_drawdown, 2),
                    'current_exposure': round(current_exposure, 2),
                    'current_risk': round(total_risk, 2),
                    'active_positions': len(active_positions),
                    'risk_status': '🟢 LOW' if total_risk < 10000 else '🟡 MEDIUM' if total_risk < 50000 else '🔴 HIGH'
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _find_optimizations(self) -> List[Dict]:
        """Encuentra oportunidades de optimización automáticamente"""
        opportunities = []
        
        # Revisar configuraciones no optimizadas
        try:
            from ..utils.optimal_config import optimal_config_manager
            from ..utils.market_manager import MarketManager
            from ..utils.config_manager import config_manager
            
            market_mgr = MarketManager()
            categories = config_manager.get_symbol_categories()
            
            if categories:
                all_symbols = market_mgr.get_symbols_by_category(categories)
                optimized = optimal_config_manager.load_all()
                
                missing = [s for s in all_symbols if s not in optimized]
                
                if missing:
                    opportunities.append({
                        'type': 'OPTIMIZATION_NEEDED',
                        'priority': 'HIGH',
                        'description': f"{len(missing)} símbolos sin optimizar",
                        'symbols': missing[:5],  # Top 5
                        'action': 'Ejecutar backtesting en Tab 🧪 Backtest'
                    })
        except:
            pass
        
        # Revisar posiciones sin protección
        try:
            from ..database.models import Trade
            
            with self.db.get_session() as session:
                unprotected = session.query(Trade).filter(
                    Trade.is_closed == False,
                    Trade.stop_loss == None
                ).count()
                
                if unprotected > 0:
                    opportunities.append({
                        'type': 'RISK_EXPOSURE',
                        'priority': 'CRITICAL',
                        'description': f"{unprotected} posiciones sin Stop Loss",
                        'action': 'Cerrar manualmente o configurar SL'
                    })
        except:
            pass
        
        # Sugerir re-optimización de configs viejas
        try:
            configs = optimal_config_manager.load_all()
            old_threshold = datetime.now() - timedelta(days=30)
            
            old_configs = [
                symbol for symbol, data in configs.items()
                if datetime.fromisoformat(data['updated_at']) < old_threshold
            ]
            
            if old_configs:
                opportunities.append({
                    'type': 'STALE_CONFIGS',
                    'priority': 'MEDIUM',
                    'description': f"{len(old_configs)} configuraciones con +30 días",
                    'symbols': old_configs,
                    'action': 'Re-optimizar para adaptarse al mercado actual'
                })
        except:
            pass
        
        return opportunities
    
    def _generate_predictions(self) -> Dict:
        """Genera predicciones de rendimiento futuro"""
        try:
            perf = self.analysis.get('performance', {})
            
            if 'total_trades' not in perf or perf['total_trades'] < 10:
                return {'status': 'insufficient_data'}
            
            # Proyección simple basada en métricas actuales
            avg_trades_per_day = perf['total_trades'] / 30
            avg_pnl_per_trade = perf['total_pnl'] / perf['total_trades']
            
            # Proyecciones
            daily_projection = avg_trades_per_day * avg_pnl_per_trade
            weekly_projection = daily_projection * 7
            monthly_projection = daily_projection * 30
            
            return {
                'daily_estimate': round(daily_projection, 2),
                'weekly_estimate': round(weekly_projection, 2),
                'monthly_estimate': round(monthly_projection, 2),
                'confidence': 'HIGH' if perf['total_trades'] > 50 else 'MEDIUM' if perf['total_trades'] > 20 else 'LOW'
            }
        except:
            return {'error': 'calculation_failed'}
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones inteligentes"""
        recommendations = []
        
        perf = self.analysis.get('performance', {})
        risk = self.analysis.get('risk_metrics', {})
        
        # Basado en Win Rate
        if 'win_rate' in perf:
            if perf['win_rate'] < 50:
                recommendations.append(
                    "⚠️ Win Rate bajo (<50%). Considera ajustar parámetros de entrada más conservadores."
                )
            elif perf['win_rate'] > 70:
                recommendations.append(
                    "✅ Excelente Win Rate (>70%). Considera aumentar tamaño de posiciones gradualmente."
                )
        
        # Basado en Profit Factor
        if 'profit_factor' in perf:
            if perf['profit_factor'] < 1.5:
                recommendations.append(
                    "📉 Profit Factor bajo. Revisa estrategia de salida y Stop Loss."
                )
        
        # Basado en drawdown
        if 'max_drawdown' in risk:
            if risk['max_drawdown'] > 20:
                recommendations.append(
                    "🔴 Drawdown alto (>20%). URGENTE: Reducir tamaño de posiciones y revisar risk management."
                )
        
        # Basado en optimizaciones
        opps = self.analysis.get('optimization_opportunities', [])
        if len(opps) > 0:
            recommendations.append(
                f"🎯 {len(opps)} oportunidades de mejora detectadas. Revisar sección de optimizaciones."
            )
        
        if not recommendations:
            recommendations.append("🎉 Sistema operando óptimamente. Mantener monitoreo regular.")
        
        return recommendations
    
    def generate_report(self) -> str:
        """Genera reporte visual en texto"""
        if not self.analysis:
            self.run_full_analysis()
        
        report = []
        report.append("="*70)
        report.append("🧠 BOT INTELLIGENCE REPORT")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*70)
        
        # Performance
        perf = self.analysis.get('performance', {})
        if perf and 'total_trades' in perf:
            report.append("\n📊 PERFORMANCE (Últimos 30 días)")
            report.append(f"  Total Trades: {perf['total_trades']}")
            report.append(f"  Win Rate: {perf['win_rate']}%")
            report.append(f"  Total P&L: ${perf['total_pnl']:,.2f}")
            report.append(f"  Profit Factor: {perf['profit_factor']}")
            report.append(f"  Estado: {perf['streak_status']}")
        
        # Risk
        risk = self.analysis.get('risk_metrics', {})
        if risk:
            report.append("\n🛡️ RISK METRICS")
            report.append(f"  Max Drawdown: {risk.get('max_drawdown', 0)}%")
            report.append(f"  Current Risk: ${risk.get('current_risk', 0):,.2f}")
            report.append(f"  Status: {risk.get('risk_status', 'N/A')}")
        
        # Predictions
        pred = self.analysis.get('predictions', {})
        if pred and 'monthly_estimate' in pred:
            report.append("\n🔮 PROYECCIONES")
            report.append(f"  Estimado Mensual: ${pred['monthly_estimate']:,.2f}")
            report.append(f"  Confianza: {pred['confidence']}")
        
        # Recommendations
        recs = self.analysis.get('recommendations', [])
        if recs:
            report.append("\n💡 RECOMENDACIONES")
            for rec in recs:
                report.append(f"  • {rec}")
        
        # Optimizations
        opps = self.analysis.get('optimization_opportunities', [])
        if opps:
            report.append("\n🎯 OPORTUNIDADES DE MEJORA")
            for opp in opps:
                report.append(f"  [{opp['priority']}] {opp['description']}")
                report.append(f"       → {opp['action']}")
        
        report.append("\n" + "="*70)
        report.append("VSCode nunca podría hacer esto 😎")
        report.append("="*70)
        
        return "\n".join(report)


def get_bot_intelligence(db_manager):
    """Factory para crear analizador"""
    return BotIntelligence(db_manager)
