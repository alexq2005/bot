"""
Backtesting Engine
Motor de backtesting para probar estrategias de trading
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
from src.analysis.technical_indicators import TechnicalIndicators


class BacktestResult:
    """Resultado de un backtest"""
    
    def __init__(self):
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[datetime] = []
        self.initial_capital: float = 0
        self.final_capital: float = 0
        
    def add_trade(self, trade: Dict):
        """Agrega un trade al resultado"""
        self.trades.append(trade)
    
    def calculate_metrics(self) -> Dict:
        """Calcula métricas de performance"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'total_return_pct': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'max_drawdown_pct': 0
            }
        
        # Trades ganadores y perdedores
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        # Métricas básicas
        total_trades = len(self.trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # Retorno total
        total_return = ((self.final_capital - self.initial_capital) / 
                       self.initial_capital) if self.initial_capital > 0 else 0
        
        # PnL promedio
        pnls = [t['pnl'] for t in self.trades]
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        total_profit = sum([t['pnl'] for t in winning_trades])
        total_loss = abs(sum([t['pnl'] for t in losing_trades]))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Sharpe Ratio (simplificado)
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1] if len(self.equity_curve) > 1 else []
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if len(returns) > 0 and np.std(returns) > 0 else 0
        
        # Max Drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calcula máximo drawdown"""
        if len(self.equity_curve) < 2:
            return 0
        
        equity = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        return abs(np.min(drawdown))


class SimpleBacktester:
    """
    Motor de backtesting simple
    Prueba estrategias basadas en indicadores técnicos
    """
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001  # 0.1%
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.indicators_calc = TechnicalIndicators()
    
    def run_strategy(
        self,
        df: pd.DataFrame,
        strategy_func: Callable[[Dict, Dict], str],
        position_size: float = 0.95  # 95% del capital
    ) -> BacktestResult:
        """
        Ejecuta una estrategia de backtesting
        
        Args:
            df: DataFrame con datos OHLCV
            strategy_func: Función que retorna 'BUY', 'SELL', o 'HOLD'
                          Recibe (signals, latest_indicators) como argumentos
            position_size: Porcentaje del capital a usar por trade
            
        Returns:
            BacktestResult con resultados del backtest
        """
        result = BacktestResult()
        result.initial_capital = self.initial_capital
        
        capital = self.initial_capital
        position = None  # {'entry_price': float, 'quantity': int, 'entry_date': datetime}
        
        result.equity_curve.append(capital)
        result.timestamps.append(df.iloc[0]['date'] if 'date' in df.columns else datetime.now())
        
        # Iterar sobre los datos
        for i in range(50, len(df)):  # Empezar después de tener suficientes datos para indicadores
            current_data = df.iloc[:i+1]
            current_row = df.iloc[i]
            
            current_price = current_row['close']
            current_date = current_row.get('date', datetime.now())
            
            # Calcular indicadores
            try:
                signals = self.indicators_calc.get_trading_signals(current_data)
                latest = self.indicators_calc.get_latest_indicators(current_data)
            except:
                continue
            
            # Ejecutar estrategia
            action = strategy_func(signals, latest)
            
            # Procesar acción
            if action == 'BUY' and position is None and capital > 0:
                # Abrir posición de compra
                trade_value = capital * position_size
                commission_cost = trade_value * self.commission
                quantity = int((trade_value - commission_cost) / current_price)
                
                if quantity > 0:
                    position = {
                        'entry_price': current_price,
                        'quantity': quantity,
                        'entry_date': current_date,
                        'side': 'BUY'
                    }
                    capital -= (quantity * current_price + commission_cost)
            
            elif action == 'SELL' and position is not None:
                # Cerrar posición
                exit_value = position['quantity'] * current_price
                commission_cost = exit_value * self.commission
                capital += (exit_value - commission_cost)
                
                # Calcular PnL
                pnl = (current_price - position['entry_price']) * position['quantity'] - (commission_cost * 2)
                pnl_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
                
                # Registrar trade
                trade = {
                    'entry_date': position['entry_date'],
                    'exit_date': current_date,
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'quantity': position['quantity'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'side': position['side']
                }
                
                result.add_trade(trade)
                position = None
            
            # Calcular equity actual
            current_equity = capital
            if position is not None:
                current_equity += position['quantity'] * current_price
            
            result.equity_curve.append(current_equity)
            result.timestamps.append(current_date)
        
        # Cerrar posición abierta al final
        if position is not None:
            final_price = df.iloc[-1]['close']
            final_date = df.iloc[-1].get('date', datetime.now())
            
            exit_value = position['quantity'] * final_price
            commission_cost = exit_value * self.commission
            capital += (exit_value - commission_cost)
            
            pnl = (final_price - position['entry_price']) * position['quantity'] - (commission_cost * 2)
            pnl_pct = ((final_price - position['entry_price']) / position['entry_price']) * 100
            
            trade = {
                'entry_date': position['entry_date'],
                'exit_date': final_date,
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'quantity': position['quantity'],
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'side': position['side']
            }
            
            result.add_trade(trade)
        
        result.final_capital = capital
        
        return result
    
    def run_rsi_strategy(
        self,
        df: pd.DataFrame,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70
    ) -> BacktestResult:
        """
        Ejecuta estrategia simple basada en RSI
        
        Args:
            df: DataFrame con datos
            rsi_oversold: Umbral de sobreventa
            rsi_overbought: Umbral de sobrecompra
            
        Returns:
            BacktestResult
        """
        def rsi_strategy(signals: Dict, latest: Dict) -> str:
            rsi = latest.get('rsi', 50)
            
            if rsi < rsi_oversold:
                return 'BUY'
            elif rsi > rsi_overbought:
                return 'SELL'
            else:
                return 'HOLD'
        
        return self.run_strategy(df, rsi_strategy)
    
    def run_macd_strategy(self, df: pd.DataFrame) -> BacktestResult:
        """
        Ejecuta estrategia basada en cruces MACD
        
        Args:
            df: DataFrame con datos
            
        Returns:
            BacktestResult
        """
        def macd_strategy(signals: Dict, latest: Dict) -> str:
            macd_signal = signals.get('macd_signal', '')
            
            if 'COMPRA' in macd_signal:
                return 'BUY'
            elif 'VENTA' in macd_signal:
                return 'SELL'
            else:
                return 'HOLD'
        
        return self.run_strategy(df, macd_strategy)
    
    def run_combined_strategy(self, df: pd.DataFrame) -> BacktestResult:
        """
        Estrategia combinada usando múltiples indicadores
        
        Args:
            df: DataFrame con datos
            
        Returns:
            BacktestResult
        """
        def combined_strategy(signals: Dict, latest: Dict) -> str:
            # Calcular score
            score = 0
            
            if 'COMPRA' in signals.get('rsi_signal', ''):
                score += 2
            elif 'VENTA' in signals.get('rsi_signal', ''):
                score -= 2
            
            if 'COMPRA' in signals.get('macd_signal', ''):
                score += 2
            elif 'VENTA' in signals.get('macd_signal', ''):
                score -= 2
            
            if 'COMPRA' in signals.get('stoch_signal', ''):
                score += 1
            elif 'VENTA' in signals.get('stoch_signal', ''):
                score -= 1
            
            # Solo operar con señales fuertes
            if score >= 3:
                return 'BUY'
            elif score <= -3:
                return 'SELL'
            else:
                return 'HOLD'
        
        return self.run_strategy(df, combined_strategy)
