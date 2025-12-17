"""
Performance Metrics Calculator
Métricas profesionales para evaluación de estrategias
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime


class PerformanceMetrics:
    """Calculador de métricas de rendimiento profesionales"""
    
    @staticmethod
    def calculate_returns(equity_curve: pd.Series) -> pd.Series:
        """Calcula retornos porcentuales"""
        return equity_curve.pct_change().fillna(0)
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
        """
        Calcula el Sharpe Ratio
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        
        Args:
            returns: Serie de retornos
            risk_free_rate: Tasa libre de riesgo anualizada (default: 0%)
            periods_per_year: Períodos por año (252 para días, 12 para meses)
        
        Returns:
            float: Sharpe Ratio anualizado
        """
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std()
        return sharpe * np.sqrt(periods_per_year)
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
        """
        Calcula el Sortino Ratio (solo considera downside volatility)
        
        Args:
            returns: Serie de retornos
            risk_free_rate: Tasa libre de riesgo anualizada
            periods_per_year: Períodos por año
        
        Returns:
            float: Sortino Ratio anualizado
        """
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        sortino = excess_returns.mean() / downside_returns.std()
        return sortino * np.sqrt(periods_per_year)
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Dict:
        """
        Calcula el Maximum Drawdown
        
        Returns:
            Dict con: max_drawdown (%), max_drawdown_duration (días), recovery_time
        """
        if len(equity_curve) < 2:
            return {'max_drawdown': 0.0, 'max_drawdown_duration': 0, 'recovery_time': 0}
        
        # Calcular running maximum
        running_max = equity_curve.expanding().max()
        
        # Calcular drawdown
        drawdown = (equity_curve - running_max) / running_max * 100
        
        max_dd = drawdown.min()
        
        # Encontrar duración del drawdown
        dd_duration = 0
        recovery_time = 0
        current_dd_duration = 0
        in_drawdown = False
        
        for i, dd in enumerate(drawdown):
            if dd < 0:
                if not in_drawdown:
                    in_drawdown = True
                    current_dd_duration = 1
                else:
                    current_dd_duration += 1
            else:
                if in_drawdown:
                    if current_dd_duration > dd_duration:
                        dd_duration = current_dd_duration
                    in_drawdown = False
                    current_dd_duration = 0
        
        return {
            'max_drawdown': abs(max_dd),
            'max_drawdown_duration': dd_duration,
            'drawdown_series': drawdown
        }
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, equity_curve: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calcula el Calmar Ratio
        
        Calmar = Annualized Return / Maximum Drawdown
        
        Args:
            returns: Serie de retornos
            equity_curve: Curva de equidad
            periods_per_year: Períodos por año
        
        Returns:
            float: Calmar Ratio
        """
        if len(returns) < 2:
            return 0.0
        
        # Retorno anualizado
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        years = len(returns) / periods_per_year
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Max drawdown
        max_dd_info = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        max_dd = max_dd_info['max_drawdown'] / 100  # Convertir a decimal
        
        if max_dd == 0:
            return 0.0
        
        return annualized_return / max_dd
    
    @staticmethod
    def calculate_win_rate(trades: List[Dict]) -> Dict:
        """
        Calcula métricas de win rate
        
        Args:
            trades: Lista de trades con campo 'pnl'
        
        Returns:
            Dict con métricas de trades
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
        
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        total_trades = len(trades)
        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        
        win_rate = (num_wins / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        largest_win = max([t['pnl'] for t in winning_trades]) if winning_trades else 0
        largest_loss = min([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': num_wins,
            'losing_trades': num_losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss
        }
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """
        Calcula el Profit Factor
        
        Profit Factor = Gross Profit / Gross Loss
        
        Args:
            trades: Lista de trades con campo 'pnl'
        
        Returns:
            float: Profit Factor
        """
        if not trades:
            return 0.0
        
        gross_profit = sum(t['pnl'] for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def calculate_expectancy(trades: List[Dict]) -> float:
        """
        Calcula la Expectancy (ganancia esperada por trade)
        
        Args:
            trades: Lista de trades con campo 'pnl'
        
        Returns:
            float: Expectancy
        """
        if not trades:
            return 0.0
        
        win_rate_info = PerformanceMetrics.calculate_win_rate(trades)
        
        win_rate = win_rate_info['win_rate'] / 100
        avg_win = win_rate_info['avg_win']
        avg_loss = abs(win_rate_info['avg_loss'])
        
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        return expectancy
    
    @staticmethod
    def calculate_cagr(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calcula el CAGR (Compound Annual Growth Rate)
        
        Args:
            equity_curve: Curva de equidad
            periods_per_year: Períodos por año
        
        Returns:
            float: CAGR en porcentaje
        """
        if len(equity_curve) < 2:
            return 0.0
        
        initial_value = equity_curve.iloc[0]
        final_value = equity_curve.iloc[-1]
        years = len(equity_curve) / periods_per_year
        
        if years == 0 or initial_value == 0:
            return 0.0
        
        cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
        
        return cagr
    
    @staticmethod
    def calculate_all_metrics(equity_curve: pd.Series, trades: List[Dict], periods_per_year: int = 252) -> Dict:
        """
        Calcula todas las métricas de rendimiento
        
        Args:
            equity_curve: Serie temporal del valor del portafolio
            trades: Lista de trades ejecutados
            periods_per_year: Períodos por año (252 para días, 12 para meses)
        
        Returns:
            Dict con todas las métricas
        """
        returns = PerformanceMetrics.calculate_returns(equity_curve)
        
        # Métricas de retorno
        total_return = ((equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1) * 100 if len(equity_curve) > 0 else 0
        
        # Métricas de riesgo
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns, periods_per_year=periods_per_year)
        sortino = PerformanceMetrics.calculate_sortino_ratio(returns, periods_per_year=periods_per_year)
        calmar = PerformanceMetrics.calculate_calmar_ratio(returns, equity_curve, periods_per_year)
        
        # Drawdown
        dd_info = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        
        # CAGR
        cagr = PerformanceMetrics.calculate_cagr(equity_curve, periods_per_year)
        
        # Métricas de trades
        win_rate_info = PerformanceMetrics.calculate_win_rate(trades)
        profit_factor = PerformanceMetrics.calculate_profit_factor(trades)
        expectancy = PerformanceMetrics.calculate_expectancy(trades)
        
        return {
            # Retornos
            'total_return_pct': total_return,
            'cagr_pct': cagr,
            
            # Ratios de riesgo
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            
            # Drawdown
            'max_drawdown_pct': dd_info['max_drawdown'],
            'max_drawdown_duration': dd_info['max_drawdown_duration'],
            
            # Trades
            'total_trades': win_rate_info['total_trades'],
            'winning_trades': win_rate_info['winning_trades'],
            'losing_trades': win_rate_info['losing_trades'],
            'win_rate_pct': win_rate_info['win_rate'],
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'avg_win': win_rate_info['avg_win'],
            'avg_loss': win_rate_info['avg_loss'],
            'largest_win': win_rate_info['largest_win'],
            'largest_loss': win_rate_info['largest_loss']
        }
