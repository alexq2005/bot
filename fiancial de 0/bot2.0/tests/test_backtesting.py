"""
Test de Backtesting Engine
Pruebas para el motor de backtesting
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backtesting.backtest_engine import SimpleBacktester, BacktestResult


def create_sample_data(length=200, trend='uptrend'):
    """Crear datos de ejemplo para backtesting"""
    np.random.seed(42)
    base_price = 100
    
    if trend == 'uptrend':
        returns = np.random.randn(length) * 0.015 + 0.008  # Tendencia alcista
    elif trend == 'downtrend':
        returns = np.random.randn(length) * 0.015 - 0.008  # Tendencia bajista
    else:
        returns = np.random.randn(length) * 0.02  # Neutral
    
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Crear fechas
    start_date = datetime.now() - timedelta(days=length)
    dates = [start_date + timedelta(days=i) for i in range(length)]
    
    return pd.DataFrame({
        'date': dates,
        'close': prices,
        'open': prices * (1 + np.random.randn(length) * 0.005),
        'high': prices + np.abs(np.random.randn(length) * prices * 0.01),
        'low': prices - np.abs(np.random.randn(length) * prices * 0.01),
        'volume': np.random.randint(100000, 10000000, length)
    })


def test_backtester_initialization():
    """Test inicialización del backtester"""
    try:
        backtester = SimpleBacktester(initial_capital=100000, commission=0.001)
        
        assert backtester.initial_capital == 100000
        assert backtester.commission == 0.001
        
        print("✅ Backtester inicializado correctamente")
        print(f"   Capital inicial: ${backtester.initial_capital:,.2f}")
        print(f"   Comisión: {backtester.commission*100}%")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_backtest_result():
    """Test clase BacktestResult"""
    try:
        result = BacktestResult()
        result.initial_capital = 100000
        result.final_capital = 110000
        
        # Agregar trades de ejemplo
        result.add_trade({
            'entry_price': 100,
            'exit_price': 105,
            'quantity': 100,
            'pnl': 500,
            'pnl_pct': 5.0
        })
        
        result.add_trade({
            'entry_price': 105,
            'exit_price': 103,
            'quantity': 100,
            'pnl': -200,
            'pnl_pct': -1.9
        })
        
        # Calcular métricas
        metrics = result.calculate_metrics()
        
        assert metrics['total_trades'] == 2
        assert metrics['winning_trades'] == 1
        assert metrics['losing_trades'] == 1
        assert 0 <= metrics['win_rate'] <= 1
        
        print("✅ BacktestResult funciona correctamente")
        print(f"   Total trades: {metrics['total_trades']}")
        print(f"   Win rate: {metrics['win_rate']*100:.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en BacktestResult: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rsi_strategy():
    """Test estrategia RSI"""
    try:
        backtester = SimpleBacktester(initial_capital=100000)
        df = create_sample_data(length=150, trend='uptrend')
        
        result = backtester.run_rsi_strategy(df, rsi_oversold=30, rsi_overbought=70)
        
        metrics = result.calculate_metrics()
        
        assert metrics['total_trades'] >= 0
        
        print("✅ Estrategia RSI ejecutada:")
        print(f"   Total trades: {metrics['total_trades']}")
        print(f"   Win rate: {metrics['win_rate']*100:.1f}%")
        print(f"   Retorno total: {metrics['total_return_pct']:.2f}%")
        print(f"   Capital final: ${result.final_capital:,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en estrategia RSI: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_macd_strategy():
    """Test estrategia MACD"""
    try:
        backtester = SimpleBacktester(initial_capital=100000)
        df = create_sample_data(length=150, trend='uptrend')
        
        result = backtester.run_macd_strategy(df)
        
        metrics = result.calculate_metrics()
        
        assert metrics['total_trades'] >= 0
        
        print("✅ Estrategia MACD ejecutada:")
        print(f"   Total trades: {metrics['total_trades']}")
        print(f"   Win rate: {metrics['win_rate']*100:.1f}%")
        print(f"   Retorno total: {metrics['total_return_pct']:.2f}%")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en estrategia MACD: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_strategy():
    """Test estrategia combinada"""
    try:
        backtester = SimpleBacktester(initial_capital=100000)
        df = create_sample_data(length=150, trend='uptrend')
        
        result = backtester.run_combined_strategy(df)
        
        metrics = result.calculate_metrics()
        
        assert metrics['total_trades'] >= 0
        
        print("✅ Estrategia Combinada ejecutada:")
        print(f"   Total trades: {metrics['total_trades']}")
        print(f"   Trades ganadores: {metrics['winning_trades']}")
        print(f"   Trades perdedores: {metrics['losing_trades']}")
        print(f"   Win rate: {metrics['win_rate']*100:.1f}%")
        print(f"   Retorno total: {metrics['total_return_pct']:.2f}%")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"   Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en estrategia combinada: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_strategy():
    """Test estrategia personalizada"""
    try:
        backtester = SimpleBacktester(initial_capital=100000)
        df = create_sample_data(length=150)
        
        # Estrategia simple: comprar si RSI < 35, vender si RSI > 65
        def custom_strategy(signals, latest):
            rsi = latest.get('rsi', 50)
            if rsi < 35:
                return 'BUY'
            elif rsi > 65:
                return 'SELL'
            return 'HOLD'
        
        result = backtester.run_strategy(df, custom_strategy)
        
        metrics = result.calculate_metrics()
        
        print("✅ Estrategia Personalizada ejecutada:")
        print(f"   Total trades: {metrics['total_trades']}")
        print(f"   Retorno total: {metrics['total_return_pct']:.2f}%")
        
        if metrics['total_trades'] > 0:
            print(f"   Ganancia promedio: ${metrics['avg_win']:.2f}")
            print(f"   Pérdida promedio: ${metrics['avg_loss']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en estrategia personalizada: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_calculation():
    """Test cálculo de métricas detalladas"""
    try:
        backtester = SimpleBacktester(initial_capital=100000)
        df = create_sample_data(length=150, trend='uptrend')
        
        result = backtester.run_combined_strategy(df)
        metrics = result.calculate_metrics()
        
        # Verificar que todas las métricas existan
        required_metrics = [
            'total_trades', 'winning_trades', 'losing_trades',
            'win_rate', 'total_return', 'total_return_pct',
            'avg_win', 'avg_loss', 'profit_factor',
            'sharpe_ratio', 'max_drawdown', 'max_drawdown_pct'
        ]
        
        for metric in required_metrics:
            assert metric in metrics, f"Métrica faltante: {metric}"
        
        print("✅ Cálculo de métricas completo:")
        print(f"   Métricas calculadas: {len(metrics)}")
        print(f"   Win Rate: {metrics['win_rate']*100:.1f}%")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   Max DD: {metrics['max_drawdown_pct']:.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en cálculo de métricas: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE BACKTESTING ENGINE")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización del Backtester", test_backtester_initialization),
        ("BacktestResult", test_backtest_result),
        ("Estrategia RSI", test_rsi_strategy),
        ("Estrategia MACD", test_macd_strategy),
        ("Estrategia Combinada", test_combined_strategy),
        ("Estrategia Personalizada", test_custom_strategy),
        ("Cálculo de Métricas", test_metrics_calculation),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}...")
        result = test_func()
        results.append((name, result))
    
    # Resumen
    print("\n" + "=" * 70)
    passed = sum(1 for _, r in results if r)
    print(f"RESULTADO: {passed}/{len(results)} tests pasaron")
    print("=" * 70 + "\n")
    
    exit(0 if passed == len(results) else 1)
