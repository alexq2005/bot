"""
Test de Market Screener
Pruebas para el escáner de mercado
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.market_screener import MarketScreener


def create_sample_data(symbol, length=100, trend='neutral'):
    """Crear datos de ejemplo con tendencia específica"""
    np.random.seed(hash(symbol) % 2**32)
    base_price = np.random.uniform(50, 500)
    
    if trend == 'uptrend':
        returns = np.random.randn(length) * 0.01 + 0.003
    elif trend == 'downtrend':
        returns = np.random.randn(length) * 0.01 - 0.003
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


def test_screener_initialization():
    """Test inicialización del screener"""
    try:
        screener = MarketScreener()
        assert screener is not None
        print("✅ Screener inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_scan_multiple_symbols():
    """Test escaneo de múltiples símbolos"""
    try:
        screener = MarketScreener()
        
        # Crear datos para múltiples símbolos
        symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA']
        historical_data = {
            'GGAL': create_sample_data('GGAL', trend='uptrend'),
            'YPFD': create_sample_data('YPFD', trend='downtrend'),
            'PAMP': create_sample_data('PAMP', trend='neutral'),
            'ALUA': create_sample_data('ALUA', trend='uptrend'),
            'BMA': create_sample_data('BMA', trend='neutral')
        }
        
        # Escanear
        results = screener.scan_symbols(symbols, historical_data)
        
        assert len(results) == 5, "Debe escanear 5 símbolos"
        assert 'symbol' in results.columns
        assert 'signal_score' in results.columns
        assert 'rsi' in results.columns
        
        print("✅ Escaneo de múltiples símbolos:")
        print(f"   Símbolos escaneados: {len(results)}")
        print(f"   Columnas: {len(results.columns)}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en escaneo: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_by_signal():
    """Test filtrado por señales"""
    try:
        screener = MarketScreener()
        
        symbols = ['GGAL', 'YPFD', 'PAMP']
        historical_data = {
            'GGAL': create_sample_data('GGAL', trend='uptrend'),
            'YPFD': create_sample_data('YPFD', trend='downtrend'),
            'PAMP': create_sample_data('PAMP', trend='neutral')
        }
        
        screener.scan_symbols(symbols, historical_data)
        
        # Filtrar señales de compra
        buy_signals = screener.filter_by_signal('buy', min_score=1)
        
        print("✅ Filtrado por señales:")
        print(f"   Señales de COMPRA: {len(buy_signals)}")
        
        if len(buy_signals) > 0:
            print(f"   Mejor oportunidad: {buy_signals.iloc[0]['symbol']} (Score: {buy_signals.iloc[0]['signal_score']})")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en filtrado: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_by_rsi():
    """Test filtrado por RSI"""
    try:
        screener = MarketScreener()
        
        symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA']
        historical_data = {sym: create_sample_data(sym) for sym in symbols}
        
        screener.scan_symbols(symbols, historical_data)
        
        # Filtrar sobreventa
        oversold = screener.filter_by_rsi('oversold', threshold=40)
        
        print("✅ Filtrado por RSI:")
        print(f"   Activos en sobreventa (RSI<40): {len(oversold)}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en filtro RSI: {e}")
        return False


def test_get_top_opportunities():
    """Test obtención de mejores oportunidades"""
    try:
        screener = MarketScreener()
        
        symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA', 'COME']
        historical_data = {sym: create_sample_data(sym) for sym in symbols}
        
        screener.scan_symbols(symbols, historical_data)
        
        # Top 3 oportunidades
        top = screener.get_top_opportunities(n=3, direction='buy')
        
        assert len(top) <= 3, "Debe retornar máximo 3 oportunidades"
        
        print("✅ Top oportunidades:")
        print(f"   Top 3 para COMPRA:")
        for idx, row in top.iterrows():
            print(f"      {row['symbol']}: Score {row['signal_score']}, RSI {row['rsi']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en top opportunities: {e}")
        return False


def test_get_summary():
    """Test resumen del escaneo"""
    try:
        screener = MarketScreener()
        
        symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA']
        historical_data = {sym: create_sample_data(sym) for sym in symbols}
        
        screener.scan_symbols(symbols, historical_data)
        
        summary = screener.get_summary()
        
        assert 'total_scanned' in summary
        assert summary['total_scanned'] == 5
        
        print("✅ Resumen del escaneo:")
        print(f"   Total escaneados: {summary['total_scanned']}")
        print(f"   Señales COMPRA: {summary['buy_signals']}")
        print(f"   Señales VENTA: {summary['sell_signals']}")
        print(f"   Señales NEUTRAL: {summary['neutral_signals']}")
        print(f"   RSI promedio: {summary['avg_rsi']:.2f}")
        print(f"   ADX promedio: {summary['avg_adx']:.2f}")
        print(f"   Tendencias fuertes (ADX>25): {summary['strong_trends']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en resumen: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE MARKET SCREENER")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización", test_screener_initialization),
        ("Escaneo Múltiples Símbolos", test_scan_multiple_symbols),
        ("Filtrado por Señales", test_filter_by_signal),
        ("Filtrado por RSI", test_filter_by_rsi),
        ("Top Oportunidades", test_get_top_opportunities),
        ("Resumen de Escaneo", test_get_summary),
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
