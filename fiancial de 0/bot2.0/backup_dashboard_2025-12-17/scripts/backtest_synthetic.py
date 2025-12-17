"""
Backtest con datos sintéticos realistas
Genera un escenario de trading para validar el sistema
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def generate_realistic_prices(base_price=100, days=90, volatility=0.02):
    """Genera precios realistas usando random walk"""
    returns = np.random.normal(0.0005, volatility, days)
    prices = base_price * np.exp(np.cumsum(returns))
    return prices


class SyntheticBacktester:
    """Backtester con datos sintéticos pero realistas"""
    
    def __init__(self, capital=1000000, commission=0.001):
        self.initial_capital = capital
        self.current_capital = capital
        self.commission = commission
        self.positions = {}
        self.trades = []
        self.equity_curve = [capital]
        
    def calculate_simple_rsi(self, prices, period=14):
        """Calcula RSI simple"""
        if len(prices) < period:
            return None
        
        deltas = np.diff(prices[-period-1:])
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def run_backtest(self, symbol, prices, dates):
        """Ejecuta backtest con estrategia simple"""
        
        print(f"\n[*] Backtesting {symbol} ({len(prices)} barras)...")
        
        wins = 0
        losses = 0
        total_return = 0
        
        for i in range(14, len(prices)):
            date = dates[i]
            price = prices[i]
            
            # Calcular RSI
            rsi = self.calculate_simple_rsi(prices[:i+1])
            
            if rsi is None:
                continue
            
            # Estrategia: RSI mean reversion
            # BUY cuando RSI < 30
            if rsi < 30 and symbol not in self.positions:
                position_size = self.current_capital * 0.15  # 15% del capital
                quantity = position_size / price
                cost = quantity * price * (1 + self.commission)
                
                if self.current_capital >= cost:
                    self.current_capital -= cost
                    self.positions[symbol] = {
                        'entry_price': price,
                        'quantity': quantity,
                        'entry_date': date,
                        'entry_idx': i,
                        'entry_rsi': rsi
                    }
                    
                    self.trades.append({
                        'symbol': symbol,
                        'type': 'BUY',
                        'date': date,
                        'price': price,
                        'quantity': quantity,
                        'rsi': rsi
                    })
            
            # SELL cuando RSI > 70 O si llevas más de 15 barras
            elif symbol in self.positions:
                pos = self.positions[symbol]
                
                should_sell = (rsi > 70) or ((i - pos['entry_idx']) > 15)
                
                if should_sell:
                    exit_value = pos['quantity'] * price * (1 - self.commission)
                    profit = exit_value - (pos['quantity'] * pos['entry_price'])
                    profit_pct = (profit / (pos['quantity'] * pos['entry_price'])) * 100
                    
                    self.current_capital += exit_value
                    self.equity_curve.append(self.current_capital)
                    
                    self.trades.append({
                        'symbol': symbol,
                        'type': 'SELL',
                        'date': date,
                        'price': price,
                        'quantity': pos['quantity'],
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'rsi': rsi,
                        'days_held': i - pos['entry_idx']
                    })
                    
                    if profit > 0:
                        wins += 1
                    else:
                        losses += 1
                    
                    total_return += profit
                    del self.positions[symbol]
            
            self.equity_curve.append(self.current_capital)
        
        return {
            'symbol': symbol,
            'trades': len([t for t in self.trades if t['symbol'] == symbol and t['type'] == 'BUY']),
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0,
            'total_return': total_return
        }


def main():
    print("=" * 70)
    print("BACKTEST - ESTRATEGIA RSI MEAN REVERSION")
    print("=" * 70)
    
    # Parámetros
    np.random.seed(42)  # Para reproducibilidad
    
    symbols = {
        'GGAL': 47.50,   # Precio base aproximado
        'YPFD': 8.50,
        'CEPU': 8.20
    }
    
    capital = 1000000
    days = 90
    
    print(f"\nCapital inicial: ${capital:,.2f}")
    print(f"Símbolos: {', '.join(symbols.keys())}")
    print(f"Período: {days} días")
    print(f"Volatilidad: 2% diario\n")
    
    backtester = SyntheticBacktester(capital=capital)
    
    # Generar datos y ejecutar backtest
    all_results = []
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    for symbol, base_price in symbols.items():
        # Generar precios realistas
        prices = generate_realistic_prices(base_price, days, volatility=0.02)
        
        # Ejecutar backtest
        results = backtester.run_backtest(symbol, prices, dates)
        all_results.append(results)
    
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
    print(f"Retorno Total:      ${total_return:,.2f}")
    print(f"Retorno %:          {final_return_pct:.2f}%")
    print(f"Total Trades:       {total_trades}")
    print(f"Trades Ganadores:   {total_wins}")
    print(f"Trades Perdedores:  {total_losses}")
    
    if (total_wins + total_losses) > 0:
        overall_wr = (total_wins / (total_wins + total_losses)) * 100
        print(f"Win Rate Overall:   {overall_wr:.1f}%")
    
    # Calcular Sharpe Ratio
    if len(backtester.equity_curve) > 1:
        equity_arr = np.array(backtester.equity_curve)
        returns = np.diff(equity_arr) / equity_arr[:-1]
        if returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
            print(f"Sharpe Ratio:       {sharpe:.2f}")
        
        # Max Drawdown
        running_max = np.maximum.accumulate(equity_arr)
        drawdown = (equity_arr - running_max) / running_max
        max_dd = drawdown.min()
        print(f"Max Drawdown:       {max_dd*100:.2f}%")
    
    print("\n" + "=" * 70)
    
    # Mostrar algunos trades
    if backtester.trades:
        print("\nULTIMOS 5 TRADES:")
        print("=" * 70)
        
        trade_count = 0
        for trade in reversed(backtester.trades):
            if trade_count >= 5:
                break
            
            if trade['type'] == 'SELL':
                profit_str = f"${trade['profit']:,.2f} ({trade['profit_pct']:+.2f}%)"
                print(f"{trade['symbol']} | {trade['date'].strftime('%Y-%m-%d')} | SELL @ ${trade['price']:.2f} | {profit_str}")
                trade_count += 1
    
    # Guardar resultados
    if backtester.trades:
        df_trades = pd.DataFrame(backtester.trades)
        filename = f"backtest_synthetic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_trades.to_csv(filename, index=False)
        print(f"\nResultados guardados en: {filename}")


if __name__ == "__main__":
    main()
