"""
Backtester con estrategia agresiva para testing
Genera trades más frecuentes para validar sistema
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Setup path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.api.mock_iol_client import MockIOLClient
from src.analysis.technical_indicators import TechnicalIndicators


class SimpleBacktester:
    """Backtester simple con estrategia agresiva"""
    
    def __init__(self, capital=1000000, commission=0.001):
        self.initial_capital = capital
        self.current_capital = capital
        self.commission = commission
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.dates = []
        
    def run(self, symbol, data, start_idx=30):
        """
        Ejecutar backtest con estrategia simple RSI + MACD
        
        Reglas:
        - BUY: RSI < 40 AND MACD positivo
        - SELL: RSI > 60 OR MACD negativo
        """
        
        print(f"\n[*] Backtesting {symbol}...")
        print(f"    Datos: {len(data)} barras")
        
        ti = TechnicalIndicators()
        wins = 0
        losses = 0
        total_return = 0
        
        for i in range(start_idx, len(data)):
            date = data.index[i]
            close = data['close'].iloc[i]
            
            # Usar datos hasta el índice actual
            df_slice = data.iloc[:i+1].copy()
            
            # Calcular indicadores
            rsi_series = ti.calculate_rsi(df_slice)
            macd_data = ti.calculate_macd(df_slice)
            
            if len(rsi_series) == 0 or macd_data is None:
                continue
            
            rsi = rsi_series.iloc[-1]
            macd_line = macd_data['macd'].iloc[-1]
                
            # Señal de compra
            if rsi < 40 and macd_line > 0 and symbol not in self.positions:
                # Entrar con 10% del capital disponible
                position_size = self.current_capital * 0.1
                quantity = position_size / close
                cost = quantity * close * (1 + self.commission)
                
                if self.current_capital >= cost:
                    self.current_capital -= cost
                    self.positions[symbol] = {
                        'entry_price': close,
                        'quantity': quantity,
                        'entry_date': date,
                        'entry_idx': i
                    }
                    
                    self.trades.append({
                        'symbol': symbol,
                        'type': 'BUY',
                        'date': date,
                        'price': close,
                        'quantity': quantity,
                        'capital_left': self.current_capital
                    })
            
            # Señal de venta
            elif symbol in self.positions:
                pos = self.positions[symbol]
                
                sell_signal = (rsi > 60) or (macd_line < 0) or (i - pos['entry_idx'] > 20)
                
                if sell_signal:
                    exit_value = pos['quantity'] * close * (1 - self.commission)
                    profit = exit_value - (pos['quantity'] * pos['entry_price'])
                    
                    self.current_capital += exit_value
                    
                    self.trades.append({
                        'symbol': symbol,
                        'type': 'SELL',
                        'date': date,
                        'price': close,
                        'quantity': pos['quantity'],
                        'profit': profit,
                        'capital_left': self.current_capital
                    })
                    
                    if profit > 0:
                        wins += 1
                    else:
                        losses += 1
                    
                    total_return += profit
                    del self.positions[symbol]
            
            # Registrar equity
            self.equity_curve.append(self.current_capital)
            self.dates.append(date)
        
        return {
            'symbol': symbol,
            'trades': len([t for t in self.trades if t['symbol'] == symbol]),
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0,
            'total_return': total_return,
            'final_capital': self.current_capital
        }


def main():
    print("=" * 70)
    print("BACKTEST - ESTRATEGIA SIMPLE (RSI + MACD)")
    print("=" * 70)
    
    # Parámetros
    symbols = ['GGAL', 'YPFD', 'CEPU']
    capital = 1000000
    days = 90
    
    print(f"\nCapital inicial: ${capital:,.2f}")
    print(f"Símbolos: {', '.join(symbols)}")
    print(f"Período: {days} días\n")
    
    # Obtener datos
    client = MockIOLClient("", "", "")
    
    backtester = SimpleBacktester(capital=capital)
    
    all_results = []
    
    for symbol in symbols:
        # Obtener datos históricos
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        print(f"Descargando {symbol}...", end=" ", flush=True)
        historical = client.get_historical_data(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date
        )
        
        if historical is not None and len(historical) > 0:
            print(f"OK ({len(historical)} barras)")
            
            # Convertir a DataFrame
            df = pd.DataFrame(historical)
            df = df.set_index('date')
            
            # Ejecutar backtest
            results = backtester.run(symbol, df)
            all_results.append(results)
        else:
            print("FALLO - Sin datos")
    
    # Mostrar resultados
    print("\n" + "=" * 70)
    print("RESULTADOS DEL BACKTEST")
    print("=" * 70)
    
    total_trades = 0
    total_wins = 0
    total_losses = 0
    total_return = 0
    
    for result in all_results:
        print(f"\n{result['symbol']}")
        print(f"  Trades:     {result['trades']}")
        print(f"  Ganadores:  {result['wins']}")
        print(f"  Perdedores: {result['losses']}")
        print(f"  Win Rate:   {result['win_rate']:.1f}%")
        print(f"  Retorno:    ${result['total_return']:,.2f}")
        
        total_trades += result['trades']
        total_wins += result['wins']
        total_losses += result['losses']
        total_return += result['total_return']
    
    print("\n" + "=" * 70)
    print("RESUMEN GENERAL")
    print("=" * 70)
    
    final_return_pct = ((backtester.current_capital - capital) / capital) * 100
    
    print(f"Capital Inicial:    ${capital:,.2f}")
    print(f"Capital Final:      ${backtester.current_capital:,.2f}")
    print(f"Retorno Total:      ${total_return:,.2f} ({final_return_pct:.2f}%)")
    print(f"Total Trades:       {total_trades}")
    print(f"Trades Ganadores:   {total_wins}")
    print(f"Trades Perdedores:  {total_losses}")
    
    if (total_wins + total_losses) > 0:
        overall_wr = (total_wins / (total_wins + total_losses)) * 100
        print(f"Win Rate Overall:   {overall_wr:.1f}%")
    
    # Calcular Sharpe Ratio
    if len(backtester.equity_curve) > 1:
        returns = np.diff(backtester.equity_curve) / backtester.equity_curve[:-1]
        if returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
            print(f"Sharpe Ratio:       {sharpe:.2f}")
    
    print("\n" + "=" * 70)
    
    # Guardar resultados
    if backtester.trades:
        df_trades = pd.DataFrame(backtester.trades)
        filename = f"backtest_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_trades.to_csv(filename, index=False)
        print(f"\nResultados guardados en: {filename}")
    else:
        print("\nSin trades ejecutados")


if __name__ == "__main__":
    main()
