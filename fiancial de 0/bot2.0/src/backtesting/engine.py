
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BacktestResult:
    """Resultados de una ejecución de backtest"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    total_return_pct: float
    max_drawdown: float
    sharpe_ratio: float
    equity_curve: List[float]
    trades_log: pd.DataFrame
    initial_capital: float
    final_capital: float

class BacktestEngine:
    """Motor de Backtesting Event-Driven"""
    
    def __init__(self, initial_capital: float = 1000000.0, commission: float = 0.006):
        """
        Args:
            initial_capital: Capital inicial en ARS
            commission: Comisión por operación (ej: 0.006 = 0.6% - IOL real)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run(self, data: pd.DataFrame, strategy_logic: Callable) -> BacktestResult:
        """
        Ejecuta el backtest sobre un DataFrame de datos históricos.
        
        Args:
            data: DataFrame con columnas 'open', 'high', 'low', 'close', 'volume' y 'timestamp'
            strategy_logic: Función que toma (row, context) y devuelve {'signal': 'BUY'/'SELL'/'HOLD'}
            
        Returns:
            BacktestResult con todas las métricas
        """
        if data.empty:
            return self._empty_result()

        cash = self.initial_capital
        position = 0
        equity_curve = []
        trades = []
        
        # Pre-calcular indicadores si es necesario (asumimos que data ya los trae)
        # La simulación es fila por fila
        
        for i, row in data.iterrows():
            current_price = row['close']
            date = row.get('timestamp', i)
            
            # Contexto que ve la estrategia
            context = {
                'cash': cash,
                'position': position,
                'price': current_price,
                'portfolio_value': cash + (position * current_price),
                'history': data.iloc[:i] # Ojo con performance aquí, mejor pasar solo ventanas
            }
            
            # Ejecutar lógica de estrategia
            try:
                decision = strategy_logic(row, context)
            except Exception as e:
                print(f"Error en estrategia en {date}: {e}")
                decision = {'signal': 'HOLD'}
                
            signal = decision.get('signal', 'HOLD')
            
            # Ejecución de Órdenes
            if signal == 'BUY' and cash > 0 and position == 0:
                # ESTRATEGIA SIMPLE: All-in (o configurable)
                # Dejamos un buffer de 1% para comisiones estimadas
                max_buy_val = cash * 0.99
                quantity = int(max_buy_val / current_price)
                
                if quantity > 0:
                    cost = quantity * current_price
                    comm = cost * self.commission
                    cash -= (cost + comm)
                    position += quantity
                    
                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': current_price,
                        'quantity': quantity,
                        'commission': comm,
                        'balance': cash,
                        'pnl': 0
                    })
            
            elif signal == 'SELL' and position > 0:
                revenue = position * current_price
                comm = revenue * self.commission
                cash += (revenue - comm)
                
                # Calcular PnL de este trade (FIFO simple o promedio)
                # Asumimos que cerramos toda la posición
                last_buy = next((t for t in reversed(trades) if t['type']=='BUY'), None)
                buy_price = last_buy['price'] if last_buy else 0
                
                trade_pnl = (current_price - buy_price) * position - comm - (last_buy['commission'] if last_buy else 0)
                
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': position,
                    'commission': comm,
                    'balance': cash,
                    'pnl': trade_pnl
                })
                
                position = 0
                
            # Actualizar Equity Curve
            current_equity = cash + (position * current_price)
            equity_curve.append(current_equity)
            
        return self._calculate_metrics(equity_curve, trades)

    def _calculate_metrics(self, equity_curve: List[float], trades: List[Dict]) -> BacktestResult:
        if not equity_curve:
            return self._empty_result()
            
        final_capital = equity_curve[-1]
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Win Rate
        closed_trades = [t for t in trades if t['type'] == 'SELL']
        winning_trades = len([t for t in closed_trades if t['pnl'] > 0])
        losing_trades = len([t for t in closed_trades if t['pnl'] <= 0])
        total_trades_count = len(closed_trades)
        win_rate = (winning_trades / total_trades_count * 100) if total_trades_count > 0 else 0.0
        
        # Max Drawdown
        equity_series = pd.Series(equity_curve)
        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax
        max_drawdown = drawdown.min() * 100 # En porcentaje negativo
        
        # Sharpe (Simplificado, anualizado asumiendo datos diarios)
        returns = equity_series.pct_change().dropna()
        if len(returns) > 1 and returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * (252**0.5)
        else:
            sharpe = 0.0
            
        return BacktestResult(
            total_trades=total_trades_count,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_return=total_return,
            total_return_pct=total_return_pct,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            equity_curve=equity_curve,
            trades_log=pd.DataFrame(trades),
            initial_capital=self.initial_capital,
            final_capital=final_capital
        )

    def _empty_result(self) -> BacktestResult:
        return BacktestResult(0,0,0,0.0,0.0,0.0,0.0,0.0,[], pd.DataFrame(), self.initial_capital, self.initial_capital)
