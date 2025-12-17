"""
Backtesting Engine
Motor de backtesting event-driven para validación de estrategias
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.signal_generator import SignalGenerator
from src.strategy.hybrid_strategy import HybridStrategy
from src.risk.position_sizer import PositionSizer
from src.risk.risk_manager import RiskManager
from .metrics import PerformanceMetrics


class Backtester:
    """Motor de backtesting event-driven"""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        """
        Inicializa el backtester
        
        Args:
            initial_capital: Capital inicial
            commission: Comisión por operación (0.001 = 0.1%)
            slippage: Slippage estimado (0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # Estado del portafolio
        self.cash = initial_capital
        self.positions = {}  # {symbol: quantity}
        self.equity_curve = []
        self.trades = []
        
        # Componentes
        self.ti = TechnicalIndicators()
        self.signal_generator = SignalGenerator()
        self.position_sizer = PositionSizer()
        self.risk_manager = RiskManager()
    
    def run(
        self,
        data: Dict[str, pd.DataFrame],
        strategy: HybridStrategy,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Ejecuta el backtest
        
        Args:
            data: Dict de DataFrames {symbol: df} con datos OHLCV
            strategy: Estrategia a testear
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
        
        Returns:
            Dict con resultados del backtest
        """
        print(f"\n{'='*60}")
        print(f"🔬 INICIANDO BACKTEST")
        print(f"{'='*60}")
        print(f"Capital Inicial: ${self.initial_capital:,.2f}")
        print(f"Símbolos: {', '.join(data.keys())}")
        print(f"Comisión: {self.commission*100:.2f}%")
        print(f"Slippage: {self.slippage*100:.3f}%")
        print(f"{'='*60}\n")
        
        # Preparar datos
        prepared_data = {}
        for symbol, df in data.items():
            # Calcular indicadores
            df_with_indicators = self.ti.calculate_all_indicators(df)
            df_with_indicators = df_with_indicators.dropna()
            
            # Filtrar por fechas si se especifican
            if start_date:
                df_with_indicators = df_with_indicators[df_with_indicators['date'] >= start_date]
            if end_date:
                df_with_indicators = df_with_indicators[df_with_indicators['date'] <= end_date]
            
            prepared_data[symbol] = df_with_indicators
        
        # Obtener fechas únicas y ordenadas
        all_dates = set()
        for df in prepared_data.values():
            all_dates.update(df['date'].tolist())
        
        dates = sorted(list(all_dates))
        
        print(f"Período: {dates[0]} a {dates[-1]}")
        print(f"Total días: {len(dates)}\n")
        
        # Event loop
        for i, current_date in enumerate(dates):
            # Calcular valor del portafolio
            portfolio_value = self._calculate_portfolio_value(prepared_data, current_date)
            self.equity_curve.append({
                'date': current_date,
                'value': portfolio_value
            })
            
            # Procesar cada símbolo
            for symbol, df in prepared_data.items():
                # Obtener datos hasta la fecha actual
                historical_data = df[df['date'] <= current_date]
                
                if len(historical_data) < 50:  # Necesitamos suficiente historia
                    continue
                
                # Generar señal
                decision = strategy.generate_decision(historical_data, symbol, rl_prediction=None)
                
                current_price = historical_data.iloc[-1]['close']
                signal = decision['signal']
                
                # Ejecutar trade si hay señal
                if signal == "BUY":
                    self._execute_buy(symbol, current_price, historical_data, current_date)
                elif signal == "SELL":
                    self._execute_sell(symbol, current_price, current_date)
            
            # Mostrar progreso cada 10%
            if (i + 1) % max(1, len(dates) // 10) == 0:
                progress = ((i + 1) / len(dates)) * 100
                print(f"Progreso: {progress:.0f}% - Valor: ${portfolio_value:,.2f}")
        
        # Calcular métricas finales
        results = self._calculate_results()
        
        print(f"\n{'='*60}")
        print(f"✓ BACKTEST COMPLETADO")
        print(f"{'='*60}\n")
        
        return results
    
    def _execute_buy(self, symbol: str, price: float, historical_data: pd.DataFrame, date: datetime):
        """Ejecuta una compra"""
        # Calcular tamaño de posición
        atr = historical_data.iloc[-1]['atr']
        position_info = self.position_sizer.calculate_position_size_atr(
            account_balance=self.cash,
            current_price=price,
            atr=atr
        )
        
        quantity = position_info['quantity']
        
        if quantity == 0:
            return
        
        # Aplicar slippage y comisión
        execution_price = price * (1 + self.slippage)
        total_cost = quantity * execution_price * (1 + self.commission)
        
        if total_cost > self.cash:
            return
        
        # Ejecutar compra
        self.cash -= total_cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        
        # Registrar trade
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': execution_price,
            'total_value': total_cost,
            'pnl': 0
        })
    
    def _execute_sell(self, symbol: str, price: float, date: datetime):
        """Ejecuta una venta"""
        quantity = self.positions.get(symbol, 0)
        
        if quantity == 0:
            return
        
        # Aplicar slippage y comisión
        execution_price = price * (1 - self.slippage)
        total_revenue = quantity * execution_price * (1 - self.commission)
        
        # Ejecutar venta
        self.cash += total_revenue
        
        # Calcular P&L
        buy_trades = [t for t in self.trades if t['symbol'] == symbol and t['action'] == 'BUY']
        if buy_trades:
            avg_buy_price = sum(t['price'] * t['quantity'] for t in buy_trades) / sum(t['quantity'] for t in buy_trades)
            pnl = (execution_price - avg_buy_price) * quantity
        else:
            pnl = 0
        
        # Registrar trade
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': execution_price,
            'total_value': total_revenue,
            'pnl': pnl
        })
        
        # Cerrar posición
        self.positions[symbol] = 0
    
    def _calculate_portfolio_value(self, data: Dict[str, pd.DataFrame], current_date: datetime) -> float:
        """Calcula el valor total del portafolio"""
        total_value = self.cash
        
        for symbol, quantity in self.positions.items():
            if quantity > 0 and symbol in data:
                df = data[symbol]
                current_data = df[df['date'] <= current_date]
                
                if len(current_data) > 0:
                    current_price = current_data.iloc[-1]['close']
                    total_value += quantity * current_price
        
        return total_value
    
    def _calculate_results(self) -> Dict:
        """Calcula resultados finales del backtest"""
        # Crear DataFrame de equity curve
        equity_df = pd.DataFrame(self.equity_curve)
        equity_series = pd.Series(equity_df['value'].values, index=equity_df['date'])
        
        # Calcular métricas
        metrics = PerformanceMetrics.calculate_all_metrics(
            equity_curve=equity_series,
            trades=self.trades,
            periods_per_year=252
        )
        
        # Agregar información adicional
        metrics['initial_capital'] = self.initial_capital
        metrics['final_value'] = equity_series.iloc[-1] if len(equity_series) > 0 else self.initial_capital
        metrics['equity_curve'] = equity_df
        metrics['trades'] = self.trades
        
        return metrics
    
    def print_results(self, results: Dict):
        """Imprime resultados del backtest"""
        print("📊 RESULTADOS DEL BACKTEST")
        print("="*60)
        print(f"\n💰 RENDIMIENTO")
        print(f"  Capital Inicial:    ${results['initial_capital']:,.2f}")
        print(f"  Valor Final:        ${results['final_value']:,.2f}")
        print(f"  Retorno Total:      {results['total_return_pct']:.2f}%")
        print(f"  CAGR:               {results['cagr_pct']:.2f}%")
        
        print(f"\n📈 RATIOS DE RIESGO")
        print(f"  Sharpe Ratio:       {results['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio:      {results['sortino_ratio']:.2f}")
        print(f"  Calmar Ratio:       {results['calmar_ratio']:.2f}")
        
        print(f"\n📉 DRAWDOWN")
        print(f"  Max Drawdown:       {results['max_drawdown_pct']:.2f}%")
        print(f"  Duración:           {results['max_drawdown_duration']} días")
        
        print(f"\n🎯 TRADES")
        print(f"  Total Trades:       {results['total_trades']}")
        print(f"  Ganadores:          {results['winning_trades']}")
        print(f"  Perdedores:         {results['losing_trades']}")
        print(f"  Win Rate:           {results['win_rate_pct']:.1f}%")
        print(f"  Profit Factor:      {results['profit_factor']:.2f}")
        print(f"  Expectancy:         ${results['expectancy']:.2f}")
        print(f"  Ganancia Promedio:  ${results['avg_win']:.2f}")
        print(f"  Pérdida Promedio:   ${results['avg_loss']:.2f}")
        
        print("="*60)
