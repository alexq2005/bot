"""
Test de Enhanced Multi-Timeframe Analysis
Pruebas para análisis multi-timeframe mejorado
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.enhanced_multi_timeframe import EnhancedMultiTimeframeAnalyzer


def create_sample_data_with_dates(length=200, trend='neutral'):
    """Crear datos de ejemplo con fechas"""
    np.random.seed(42)
    base_price = 100
    
    if trend == 'uptrend':
        returns = np.random.randn(length) * 0.015 + 0.005
    elif trend == 'downtrend':
        returns = np.random.randn(length) * 0.015 - 0.005
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
        'volume': np.random.randint(100000, 10000000, length)
    })


def test_initialization():
    """Test inicialización"""
    try:
        analyzer = EnhancedMultiTimeframeAnalyzer()
        assert analyzer is not None
        assert len(analyzer.timeframes) == 3
        
        print("✅ Inicialización correcta")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_resample_timeframe():
    """Test resampling de datos"""
    try:
        analyzer = EnhancedMultiTimeframeAnalyzer()
        df = create_sample_data_with_dates(length=100)
        
        # Resamplear a 1D (debería quedar igual)
        df_1d = analyzer.resample_to_timeframe(df, '1D')
        assert len(df_1d) <= len(df)
        
        print("✅ Resampling funciona correctamente")
        print(f"   Datos originales: {len(df)} días")
        print(f"   Resampled 1D: {len(df_1d)} días")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en resampling: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_single_timeframe():
    """Test análisis de un timeframe individual"""
    try:
        analyzer = EnhancedMultiTimeframeAnalyzer()
        df = create_sample_data_with_dates(length=120, trend='uptrend')
        
        result = analyzer.analyze_timeframe(df, '1D')
        
        assert 'timeframe' in result
        assert 'signals' in result or 'error' in result
        assert 'signal_score' in result
        
        print("✅ Análisis de timeframe individual:")
        print(f"   Timeframe: {result['timeframe']}")
        if 'error' not in result:
            print(f"   Score: {result['signal_score']}")
            print(f"   Trend: {result.get('trend', 'N/A')}")
            print(f"   RSI: {result.get('rsi', 'N/A'):.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en análisis de timeframe: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_all_timeframes():
    """Test análisis de todos los timeframes"""
    try:
        analyzer = EnhancedMultiTimeframeAnalyzer()
        df = create_sample_data_with_dates(length=150)
        
        results = analyzer.analyze_all_timeframes(df)
        
        assert isinstance(results, dict)
        assert len(results) == 3  # 1D, 4H, 1H
        
        print("✅ Análisis de todos los timeframes:")
        for tf, result in results.items():
            if 'error' not in result:
                print(f"\n   {tf}:")
                print(f"      Score: {result['signal_score']}")
                print(f"      Trend: {result.get('trend', 'N/A')}")
            else:
                print(f"\n   {tf}: Error - {result['error']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en análisis de todos los timeframes: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_timeframe_consensus():
    """Test consenso multi-timeframe"""
    try:
        analyzer = EnhancedMultiTimeframeAnalyzer()
        df = create_sample_data_with_dates(length=150, trend='uptrend')
        
        # Analizar todos los timeframes
        tf_results = analyzer.analyze_all_timeframes(df)
        
        # Obtener consenso
        consensus = analyzer.get_multi_timeframe_consensus(tf_results)
        
        assert 'consensus_signal' in consensus
        assert 'consensus_score' in consensus
        assert 'alignment' in consensus
        assert 'recommendation' in consensus
        
        print("✅ Consenso multi-timeframe:")
        print(f"   Señal: {consensus['consensus_signal']}")
        print(f"   Score: {consensus['consensus_score']:.2f}")
        print(f"   Alineación: {consensus['alignment']*100:.1f}%")
        print(f"   Recomendación: {consensus['recommendation']}")
        
        print(f"\n   Señales por timeframe:")
        for tf, data in consensus['timeframe_signals'].items():
            print(f"      {tf}: {data['trend']} (Score: {data['score']})")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en consenso: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_uptrend_detection():
    """Test detección de tendencia alcista"""
    try:
        analyzer = EnhancedMultiTimeframeAnalyzer()
        df = create_sample_data_with_dates(length=120, trend='uptrend')
        
        tf_results = analyzer.analyze_all_timeframes(df)
        consensus = analyzer.get_multi_timeframe_consensus(tf_results)
        
        # En tendencia alcista, el consenso debería ser positivo
        print("✅ Detección de tendencia alcista:")
        print(f"   Consenso: {consensus['consensus_signal']}")
        print(f"   Score: {consensus['consensus_score']:.2f}")
        
        assert consensus['consensus_score'] != 0  # Debería tener alguna señal
        
        return True
    except Exception as e:
        print(f"❌ Fallo en detección de tendencia: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE ENHANCED MULTI-TIMEFRAME ANALYSIS")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización", test_initialization),
        ("Resampling de Timeframes", test_resample_timeframe),
        ("Análisis de Timeframe Individual", test_analyze_single_timeframe),
        ("Análisis de Todos los Timeframes", test_analyze_all_timeframes),
        ("Consenso Multi-Timeframe", test_multi_timeframe_consensus),
        ("Detección de Tendencia Alcista", test_uptrend_detection),
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
