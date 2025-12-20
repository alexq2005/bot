"""
Demo de Fase 3: Multi-Timeframe Analysis + Backtesting
Muestra las nuevas funcionalidades de Fase 3
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.enhanced_multi_timeframe import EnhancedMultiTimeframeAnalyzer
from src.backtesting.backtest_engine import SimpleBacktester


def create_sample_data(length=200, trend='uptrend'):
    """Crear datos de ejemplo"""
    np.random.seed(42)
    base_price = 350
    
    if trend == 'uptrend':
        returns = np.random.randn(length) * 0.018 + 0.006
    elif trend == 'downtrend':
        returns = np.random.randn(length) * 0.018 - 0.006
    else:
        returns = np.random.randn(length) * 0.02
    
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
        'volume': np.random.randint(500000, 5000000, length)
    })


def demo_multi_timeframe_analysis():
    """Demo de análisis multi-timeframe"""
    print("\n" + "=" * 70)
    print("DEMO: MULTI-TIMEFRAME ANALYSIS")
    print("=" * 70 + "\n")
    
    analyzer = EnhancedMultiTimeframeAnalyzer()
    
    # Crear datos de ejemplo (tendencia alcista)
    symbol = 'GGAL'
    print(f"📊 Analizando {symbol} en múltiples timeframes...\n")
    
    df = create_sample_data(length=180, trend='uptrend')
    
    # Analizar todos los timeframes
    results = analyzer.analyze_all_timeframes(df)
    
    print("📈 ANÁLISIS POR TIMEFRAME:\n")
    
    for tf, data in results.items():
        if 'error' in data:
            print(f"{tf}: Error - {data['error']}")
            continue
        
        print(f"{tf}:")
        print(f"   Precio actual: ${data['price']:.2f}")
        print(f"   RSI: {data['rsi']:.2f}")
        print(f"   MACD: {data['macd']:.4f}")
        print(f"   ADX: {data['adx']:.2f}")
        print(f"   Tendencia: {data['trend']}")
        print(f"   Signal Score: {data['signal_score']}")
        print(f"   Señales:")
        for signal_name, signal_value in data['signals'].items():
            print(f"      {signal_name}: {signal_value}")
        print()
    
    # Obtener consenso
    print("🎯 CONSENSO MULTI-TIMEFRAME:\n")
    
    consensus = analyzer.get_multi_timeframe_consensus(results)
    
    print(f"Señal de Consenso: {consensus['consensus_signal']}")
    print(f"Score de Consenso: {consensus['consensus_score']:.2f}")
    print(f"Alineación: {consensus['alignment']*100:.1f}%")
    print(f"\nRecomendación:")
    print(f"   {consensus['recommendation']}\n")
    
    print("📊 Señales por Timeframe:")
    for tf, data in consensus['timeframe_signals'].items():
        print(f"   {tf}: {data['trend']} (Score: {data['score']})")


def demo_backtesting():
    """Demo de backtesting"""
    print("\n\n" + "=" * 70)
    print("DEMO: BACKTESTING ENGINE")
    print("=" * 70 + "\n")
    
    # Crear backtester
    backtester = SimpleBacktester(initial_capital=100000, commission=0.001)
    
    print(f"💰 Configuración del Backtesting:")
    print(f"   Capital inicial: ${backtester.initial_capital:,.2f}")
    print(f"   Comisión: {backtester.commission*100}%\n")
    
    # Crear datos de prueba (tendencia alcista para mejores resultados)
    df = create_sample_data(length=200, trend='uptrend')
    
    print(f"📊 Datos de prueba:")
    print(f"   Período: {len(df)} días")
    print(f"   Precio inicial: ${df.iloc[0]['close']:.2f}")
    print(f"   Precio final: ${df.iloc[-1]['close']:.2f}")
    print(f"   Cambio B&H: {((df.iloc[-1]['close'] - df.iloc[0]['close']) / df.iloc[0]['close'] * 100):.2f}%\n")
    
    # Estrategia 1: RSI
    print("=" * 70)
    print("ESTRATEGIA 1: RSI (Sobreventa/Sobrecompra)")
    print("=" * 70 + "\n")
    
    result_rsi = backtester.run_rsi_strategy(df, rsi_oversold=30, rsi_overbought=70)
    metrics_rsi = result_rsi.calculate_metrics()
    
    print(f"📈 Resultados:")
    print(f"   Total trades: {metrics_rsi['total_trades']}")
    print(f"   Trades ganadores: {metrics_rsi['winning_trades']}")
    print(f"   Trades perdedores: {metrics_rsi['losing_trades']}")
    print(f"   Win Rate: {metrics_rsi['win_rate']*100:.1f}%")
    print(f"   Retorno total: {metrics_rsi['total_return_pct']:.2f}%")
    print(f"   Capital final: ${result_rsi.final_capital:,.2f}")
    
    if metrics_rsi['total_trades'] > 0:
        print(f"   Ganancia promedio: ${metrics_rsi['avg_win']:.2f}")
        print(f"   Pérdida promedio: ${metrics_rsi['avg_loss']:.2f}")
        print(f"   Profit Factor: {metrics_rsi['profit_factor']:.2f}")
        print(f"   Sharpe Ratio: {metrics_rsi['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {metrics_rsi['max_drawdown_pct']:.2f}%")
    
    # Estrategia 2: MACD
    print("\n" + "=" * 70)
    print("ESTRATEGIA 2: MACD (Cruces)")
    print("=" * 70 + "\n")
    
    result_macd = backtester.run_macd_strategy(df)
    metrics_macd = result_macd.calculate_metrics()
    
    print(f"📈 Resultados:")
    print(f"   Total trades: {metrics_macd['total_trades']}")
    print(f"   Trades ganadores: {metrics_macd['winning_trades']}")
    print(f"   Trades perdedores: {metrics_macd['losing_trades']}")
    print(f"   Win Rate: {metrics_macd['win_rate']*100:.1f}%")
    print(f"   Retorno total: {metrics_macd['total_return_pct']:.2f}%")
    print(f"   Capital final: ${result_macd.final_capital:,.2f}")
    
    if metrics_macd['total_trades'] > 0:
        print(f"   Ganancia promedio: ${metrics_macd['avg_win']:.2f}")
        print(f"   Pérdida promedio: ${metrics_macd['avg_loss']:.2f}")
        print(f"   Profit Factor: {metrics_macd['profit_factor']:.2f}")
        print(f"   Sharpe Ratio: {metrics_macd['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {metrics_macd['max_drawdown_pct']:.2f}%")
    
    # Estrategia 3: Combinada
    print("\n" + "=" * 70)
    print("ESTRATEGIA 3: COMBINADA (Múltiples Indicadores)")
    print("=" * 70 + "\n")
    
    result_combined = backtester.run_combined_strategy(df)
    metrics_combined = result_combined.calculate_metrics()
    
    print(f"📈 Resultados:")
    print(f"   Total trades: {metrics_combined['total_trades']}")
    print(f"   Trades ganadores: {metrics_combined['winning_trades']}")
    print(f"   Trades perdedores: {metrics_combined['losing_trades']}")
    print(f"   Win Rate: {metrics_combined['win_rate']*100:.1f}%")
    print(f"   Retorno total: {metrics_combined['total_return_pct']:.2f}%")
    print(f"   Capital final: ${result_combined.final_capital:,.2f}")
    
    if metrics_combined['total_trades'] > 0:
        print(f"   Ganancia promedio: ${metrics_combined['avg_win']:.2f}")
        print(f"   Pérdida promedio: ${metrics_combined['avg_loss']:.2f}")
        print(f"   Profit Factor: {metrics_combined['profit_factor']:.2f}")
        print(f"   Sharpe Ratio: {metrics_combined['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {metrics_combined['max_drawdown_pct']:.2f}%")
    
    # Comparación de estrategias
    print("\n" + "=" * 70)
    print("COMPARACIÓN DE ESTRATEGIAS")
    print("=" * 70 + "\n")
    
    strategies = [
        ("RSI", metrics_rsi),
        ("MACD", metrics_macd),
        ("Combinada", metrics_combined)
    ]
    
    print(f"{'Estrategia':<15} {'Trades':<8} {'Win%':<8} {'Retorno%':<12} {'Sharpe':<8}")
    print("-" * 60)
    
    for name, metrics in strategies:
        print(f"{name:<15} {metrics['total_trades']:<8} "
              f"{metrics['win_rate']*100:<7.1f}% "
              f"{metrics['total_return_pct']:<11.2f}% "
              f"{metrics['sharpe_ratio']:<8.2f}")
    
    # Determinar mejor estrategia
    best_strategy = max(strategies, key=lambda x: x[1]['total_return_pct'])
    print(f"\n🏆 Mejor estrategia: {best_strategy[0]} con {best_strategy[1]['total_return_pct']:.2f}% de retorno")


def demo_integrated_analysis():
    """Demo de análisis integrado"""
    print("\n\n" + "=" * 70)
    print("DEMO: ANÁLISIS INTEGRADO (Multi-TF + Backtesting)")
    print("=" * 70 + "\n")
    
    symbol = 'YPFD'
    print(f"🔍 Análisis completo de {symbol}\n")
    
    df = create_sample_data(length=180, trend='neutral')
    
    # Análisis multi-timeframe
    analyzer = EnhancedMultiTimeframeAnalyzer()
    results = analyzer.analyze_all_timeframes(df)
    consensus = analyzer.get_multi_timeframe_consensus(results)
    
    print("📊 ANÁLISIS MULTI-TIMEFRAME:")
    print(f"   Señal: {consensus['consensus_signal']}")
    print(f"   Score: {consensus['consensus_score']:.2f}")
    print(f"   Alineación: {consensus['alignment']*100:.1f}%")
    print(f"   Recomendación: {consensus['recommendation']}\n")
    
    # Backtesting de estrategia recomendada
    print("💼 BACKTESTING DE ESTRATEGIA:")
    backtester = SimpleBacktester(initial_capital=100000)
    result = backtester.run_combined_strategy(df)
    metrics = result.calculate_metrics()
    
    print(f"   Performance histórica:")
    print(f"   Trades ejecutados: {metrics['total_trades']}")
    print(f"   Win Rate: {metrics['win_rate']*100:.1f}%")
    print(f"   Retorno: {metrics['total_return_pct']:.2f}%")
    print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    print(f"\n✅ DECISIÓN FINAL:")
    if consensus['consensus_score'] >= 2 and metrics['sharpe_ratio'] > 1:
        print(f"   🟢 COMPRA RECOMENDADA")
        print(f"   Razón: Consenso fuerte ({consensus['consensus_score']:.2f}) y buen backtest (Sharpe: {metrics['sharpe_ratio']:.2f})")
    elif consensus['consensus_score'] <= -2:
        print(f"   🔴 VENTA RECOMENDADA")
        print(f"   Razón: Señal bajista consistente ({consensus['consensus_score']:.2f})")
    else:
        print(f"   🔵 MANTENER / ESPERAR")
        print(f"   Razón: No hay señal clara o backtest no confirma")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FASE 3: MULTI-TIMEFRAME ANALYSIS + BACKTESTING")
    print("=" * 70)
    
    demo_multi_timeframe_analysis()
    demo_backtesting()
    demo_integrated_analysis()
    
    print("\n" + "=" * 70)
    print("✅ DEMOS DE FASE 3 COMPLETADOS EXITOSAMENTE")
    print("=" * 70 + "\n")
