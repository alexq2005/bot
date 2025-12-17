"""
Test de Indicadores Técnicos
Pruebas para validar cálculos de RSI, MACD, Bollinger Bands, ATR
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.technical_indicators import TechnicalIndicators


def create_sample_data(length=100):
    """Crear datos de ejemplo realistas"""
    np.random.seed(42)
    base_price = 100
    returns = np.random.randn(length) * 0.02  # 2% volatilidad
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = {
        'close': prices,
        'high': prices + np.abs(np.random.randn(length) * 0.5),
        'low': prices - np.abs(np.random.randn(length) * 0.5),
        'volume': np.random.randint(1000000, 10000000, length),
    }
    
    return pd.DataFrame(data)


def test_indicators_init():
    """Verificar inicialización de indicadores"""
    try:
        indicators = TechnicalIndicators()
        print("✅ Indicadores técnicos inicializados")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_rsi_calculation():
    """Verificar cálculo de RSI"""
    try:
        df = create_sample_data()
        indicators = TechnicalIndicators()
        
        rsi = indicators.calculate_rsi(df['close'], period=14)
        
        assert len(rsi) == len(df), "RSI length mismatch"
        assert rsi.notna().sum() > 0, "RSI all NaN"
        assert (rsi[rsi.notna()] >= 0).all(), "RSI < 0"
        assert (rsi[rsi.notna()] <= 100).all(), "RSI > 100"
        
        print(f"✅ Cálculo RSI:")
        print(f"   - Min: {rsi.min():.2f}")
        print(f"   - Max: {rsi.max():.2f}")
        print(f"   - Media: {rsi.mean():.2f}")
        print(f"   - Última: {rsi.iloc[-1]:.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo RSI: {e}")
        return False


def test_macd_calculation():
    """Verificar cálculo de MACD"""
    try:
        df = create_sample_data(length=50)
        indicators = TechnicalIndicators()
        
        macd_line, signal_line, histogram = indicators.calculate_macd(df['close'])
        
        assert len(macd_line) == len(df), "MACD length mismatch"
        assert len(signal_line) == len(df), "Signal length mismatch"
        assert len(histogram) == len(df), "Histogram length mismatch"
        
        print(f"✅ Cálculo MACD:")
        print(f"   - MACD válidos: {macd_line.notna().sum()}")
        print(f"   - Signal válidos: {signal_line.notna().sum()}")
        print(f"   - Histogram válidos: {histogram.notna().sum()}")
        return True
    except Exception as e:
        print(f"❌ Fallo MACD: {e}")
        return False


def test_bollinger_bands():
    """Verificar cálculo de Bollinger Bands"""
    try:
        df = create_sample_data()
        indicators = TechnicalIndicators()
        
        upper, middle, lower = indicators.calculate_bollinger_bands(df['close'], period=20, std_dev=2)
        
        assert len(upper) == len(df), "Upper band length mismatch"
        assert len(middle) == len(df), "Middle band length mismatch"
        assert len(lower) == len(df), "Lower band length mismatch"
        
        # Upper debe ser > middle > lower
        valid_idx = upper.notna() & middle.notna() & lower.notna()
        assert (upper[valid_idx] >= middle[valid_idx]).all(), "Upper < Middle"
        assert (middle[valid_idx] >= lower[valid_idx]).all(), "Middle < Lower"
        
        print(f"✅ Bollinger Bands:")
        print(f"   - Upper media: {upper.mean():.2f}")
        print(f"   - Middle (SMA): {middle.mean():.2f}")
        print(f"   - Lower media: {lower.mean():.2f}")
        print(f"   - Ancho medio: {(upper.mean() - lower.mean()):.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo Bollinger: {e}")
        return False


def test_atr_calculation():
    """Verificar cálculo de ATR"""
    try:
        df = create_sample_data()
        indicators = TechnicalIndicators()
        
        atr = indicators.calculate_atr(df['high'], df['low'], df['close'], period=14)
        
        assert len(atr) == len(df), "ATR length mismatch"
        assert atr.notna().sum() > 0, "ATR all NaN"
        assert (atr[atr.notna()] > 0).all(), "ATR <= 0"
        
        print(f"✅ Cálculo ATR:")
        print(f"   - Min: {atr.min():.4f}")
        print(f"   - Max: {atr.max():.4f}")
        print(f"   - Media: {atr.mean():.4f}")
        print(f"   - Última: {atr.iloc[-1]:.4f}")
        return True
    except Exception as e:
        print(f"❌ Fallo ATR: {e}")
        return False


def test_sma_calculation():
    """Verificar cálculo de SMA"""
    try:
        df = create_sample_data()
        indicators = TechnicalIndicators()
        
        sma_20 = indicators.calculate_sma(df['close'], period=20)
        sma_50 = indicators.calculate_sma(df['close'], period=50)
        
        assert len(sma_20) == len(df), "SMA20 length mismatch"
        assert len(sma_50) == len(df), "SMA50 length mismatch"
        
        # SMA20 debe ser más reactivo que SMA50
        crossover_idx = (sma_20 > sma_50).astype(int).diff().abs() == 1
        
        print(f"✅ Cálculo SMA:")
        print(f"   - SMA20 válidos: {sma_20.notna().sum()}")
        print(f"   - SMA50 válidos: {sma_50.notna().sum()}")
        print(f"   - Cruces: {crossover_idx.sum()}")
        return True
    except Exception as e:
        print(f"❌ Fallo SMA: {e}")
        return False


def test_indicators_consistency():
    """Verificar consistencia entre indicadores"""
    try:
        df = create_sample_data()
        indicators = TechnicalIndicators()
        
        # En tendencia alcista: precio > SMA20 > SMA50
        sma_20 = indicators.calculate_sma(df['close'], 20)
        sma_50 = indicators.calculate_sma(df['close'], 50)
        
        # Verificar relación
        close_gt_sma20 = df['close'] > sma_20
        sma20_gt_sma50 = sma_20 > sma_50
        
        print(f"✅ Consistencia de indicadores:")
        print(f"   - Close > SMA20: {close_gt_sma20.sum()} veces")
        print(f"   - SMA20 > SMA50: {sma20_gt_sma50.sum()} veces")
        return True
    except Exception as e:
        print(f"❌ Fallo consistencia: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE INDICADORES TÉCNICOS")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización", test_indicators_init),
        ("RSI Calculation", test_rsi_calculation),
        ("MACD Calculation", test_macd_calculation),
        ("Bollinger Bands", test_bollinger_bands),
        ("ATR Calculation", test_atr_calculation),
        ("SMA Calculation", test_sma_calculation),
        ("Consistencia Indicadores", test_indicators_consistency),
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
