"""
Demo de Fase 2: Market Screener + Pattern Recognition
Muestra las nuevas funcionalidades implementadas
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.market_screener import MarketScreener
from src.analysis.pattern_recognition import PatternRecognizer


def create_sample_data(symbol, length=100, trend='neutral'):
    """Crear datos de ejemplo"""
    np.random.seed(hash(symbol) % 2**32)
    base_price = np.random.uniform(100, 500)
    
    if trend == 'uptrend':
        returns = np.random.randn(length) * 0.015 + 0.005
    elif trend == 'downtrend':
        returns = np.random.randn(length) * 0.015 - 0.005
    else:
        returns = np.random.randn(length) * 0.02
    
    prices = base_price * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'close': prices,
        'open': prices * (1 + np.random.randn(length) * 0.005),
        'high': prices + np.abs(np.random.randn(length) * prices * 0.01),
        'low': prices - np.abs(np.random.randn(length) * prices * 0.01),
        'volume': np.random.randint(100000, 10000000, length)
    })


def demo_market_screener():
    """Demo del Market Screener"""
    print("\n" + "=" * 70)
    print("DEMO: MARKET SCREENER")
    print("=" * 70 + "\n")
    
    # Crear screener
    screener = MarketScreener()
    
    # Símbolos del mercado argentino
    symbols = [
        'GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA',
        'COME', 'TXAR', 'CRES', 'EDN', 'SUPV'
    ]
    
    print(f"📊 Escaneando {len(symbols)} activos del mercado argentino...")
    
    # Crear datos históricos simulados
    historical_data = {}
    for i, symbol in enumerate(symbols):
        if i % 3 == 0:
            trend = 'uptrend'
        elif i % 3 == 1:
            trend = 'downtrend'
        else:
            trend = 'neutral'
        
        historical_data[symbol] = create_sample_data(symbol, length=90, trend=trend)
    
    # Escanear todos los símbolos
    results = screener.scan_symbols(symbols, historical_data)
    
    print(f"\n✅ Escaneo completado!\n")
    
    # Mostrar resumen
    summary = screener.get_summary()
    print("📈 RESUMEN DEL ESCANEO:")
    print(f"   Total de activos: {summary['total_scanned']}")
    print(f"   Señales de COMPRA: {summary['buy_signals']}")
    print(f"   Señales de VENTA: {summary['sell_signals']}")
    print(f"   Señales NEUTRAL: {summary['neutral_signals']}")
    print(f"   RSI promedio: {summary['avg_rsi']:.2f}")
    print(f"   ADX promedio: {summary['avg_adx']:.2f}")
    print(f"   Tendencias fuertes (ADX>25): {summary['strong_trends']}")
    
    # Top oportunidades de COMPRA
    print("\n🎯 TOP 5 OPORTUNIDADES DE COMPRA:")
    top_buy = screener.get_top_opportunities(n=5, direction='buy')
    
    for idx, row in top_buy.iterrows():
        print(f"\n   {idx+1}. {row['symbol']}")
        print(f"      Precio: ${row['price']:.2f}")
        print(f"      Score: {row['signal_score']}")
        print(f"      RSI: {row['rsi']:.2f}")
        print(f"      ADX: {row['adx']:.2f}")
        print(f"      Señales:")
        print(f"         RSI: {row['rsi_signal']}")
        print(f"         MACD: {row['macd_signal']}")
        print(f"         Stochastic: {row['stoch_signal']}")
    
    # Filtrar por RSI sobreventa
    print("\n🔍 ACTIVOS EN SOBREVENTA (RSI < 30):")
    oversold = screener.filter_by_rsi('oversold', threshold=30)
    
    if len(oversold) > 0:
        for idx, row in oversold.iterrows():
            print(f"   - {row['symbol']}: RSI={row['rsi']:.2f}, Precio=${row['price']:.2f}")
    else:
        print("   No hay activos en sobreventa extrema")
    
    # Activos con tendencia fuerte
    print("\n📊 ACTIVOS CON TENDENCIA FUERTE (ADX > 25):")
    strong_trends = screener.filter_by_trend_strength(min_adx=25)
    
    for idx, row in strong_trends.head(5).iterrows():
        print(f"   - {row['symbol']}: ADX={row['adx']:.2f}, Score={row['signal_score']}")


def demo_pattern_recognition():
    """Demo de Pattern Recognition"""
    print("\n\n" + "=" * 70)
    print("DEMO: PATTERN RECOGNITION")
    print("=" * 70 + "\n")
    
    # Crear recognizer
    recognizer = PatternRecognizer()
    
    # Analizar un activo específico
    symbol = 'GGAL'
    print(f"🔍 Analizando patrones de velas en {symbol}...\n")
    
    # Crear datos con varios patrones
    np.random.seed(42)
    length = 50
    prices = 100 + np.cumsum(np.random.randn(length) * 2)
    
    df = pd.DataFrame({
        'open': prices + np.random.randn(length) * 0.5,
        'close': prices + np.random.randn(length) * 0.5,
        'high': prices + np.abs(np.random.randn(length)) * 1.5,
        'low': prices - np.abs(np.random.randn(length)) * 1.5
    })
    
    # Escanear todos los patrones
    all_patterns = recognizer.scan_patterns(df)
    
    print("📊 PATRONES ENCONTRADOS EN LAS ÚLTIMAS 50 VELAS:")
    print(f"   Doji: {len(all_patterns['doji'])} ocurrencias")
    print(f"   Hammer (alcista): {len(all_patterns['hammer'])} ocurrencias")
    print(f"   Shooting Star (bajista): {len(all_patterns['shooting_star'])} ocurrencias")
    print(f"   Bullish Engulfing: {len(all_patterns['bullish_engulfing'])} ocurrencias")
    print(f"   Bearish Engulfing: {len(all_patterns['bearish_engulfing'])} ocurrencias")
    print(f"   Morning Star (alcista): {len(all_patterns['morning_star'])} ocurrencias")
    print(f"   Evening Star (bajista): {len(all_patterns['evening_star'])} ocurrencias")
    
    # Patrones recientes
    print("\n🎯 PATRONES EN LAS ÚLTIMAS 10 VELAS:")
    recent = recognizer.get_recent_patterns(df, lookback=10)
    
    bullish_patterns = []
    bearish_patterns = []
    
    for pattern, found in recent.items():
        if found:
            if pattern in ['hammer', 'bullish_engulfing', 'morning_star']:
                bullish_patterns.append(pattern)
            elif pattern in ['shooting_star', 'bearish_engulfing', 'evening_star']:
                bearish_patterns.append(pattern)
    
    if bullish_patterns:
        print(f"   ✅ Patrones ALCISTAS detectados:")
        for p in bullish_patterns:
            print(f"      - {p}")
    
    if bearish_patterns:
        print(f"   ⚠️  Patrones BAJISTAS detectados:")
        for p in bearish_patterns:
            print(f"      - {p}")
    
    if not bullish_patterns and not bearish_patterns:
        print("   No hay patrones significativos en las últimas velas")
    
    # Señal general
    signal = recognizer.get_pattern_signal(df)
    print(f"\n📈 SEÑAL GENERAL DE PATRONES:")
    print(f"   {signal}")


def demo_combined_analysis():
    """Demo de análisis combinado"""
    print("\n\n" + "=" * 70)
    print("DEMO: ANÁLISIS COMBINADO (Screener + Patterns)")
    print("=" * 70 + "\n")
    
    screener = MarketScreener()
    recognizer = PatternRecognizer()
    
    # Símbolos a analizar
    symbols = ['GGAL', 'YPFD', 'PAMP']
    
    print(f"🔍 Análisis combinado de {len(symbols)} activos...\n")
    
    # Crear datos
    historical_data = {
        sym: create_sample_data(sym, length=60) 
        for sym in symbols
    }
    
    # Escanear indicadores
    screener.scan_symbols(symbols, historical_data)
    
    # Analizar cada símbolo
    for symbol in symbols:
        df = historical_data[symbol]
        
        # Obtener señales de indicadores
        results = screener.results
        symbol_data = next((r for r in results if r['symbol'] == symbol), None)
        
        if not symbol_data:
            continue
        
        # Obtener patrones
        pattern_signal = recognizer.get_pattern_signal(df)
        
        print(f"📊 {symbol}:")
        print(f"   Precio: ${symbol_data['price']:.2f}")
        print(f"   Score de señales: {symbol_data['signal_score']}")
        print(f"   RSI: {symbol_data['rsi']:.2f} ({symbol_data['rsi_signal']})")
        print(f"   ADX: {symbol_data['adx']:.2f} ({symbol_data['trend_strength']})")
        print(f"   Patrones: {pattern_signal}")
        
        # Recomendación
        if symbol_data['signal_score'] >= 3:
            action = "🟢 COMPRA FUERTE"
        elif symbol_data['signal_score'] >= 1:
            action = "🟢 COMPRA"
        elif symbol_data['signal_score'] <= -3:
            action = "🔴 VENTA FUERTE"
        elif symbol_data['signal_score'] <= -1:
            action = "🔴 VENTA"
        else:
            action = "🔵 MANTENER / NEUTRAL"
        
        print(f"   Recomendación: {action}\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FASE 2: MARKET SCREENER + PATTERN RECOGNITION")
    print("=" * 70)
    
    demo_market_screener()
    demo_pattern_recognition()
    demo_combined_analysis()
    
    print("\n" + "=" * 70)
    print("✅ DEMOS COMPLETADOS EXITOSAMENTE")
    print("=" * 70 + "\n")
