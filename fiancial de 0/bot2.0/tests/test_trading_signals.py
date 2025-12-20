"""
Test de Trading Signals
Pruebas para las señales de trading generadas por indicadores
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.technical_indicators import TechnicalIndicators


def create_sample_data(length=100, trend='neutral'):
    """Crear datos de ejemplo con tendencia específica"""
    np.random.seed(42)
    base_price = 100
    
    if trend == 'uptrend':
        # Tendencia alcista
        returns = np.random.randn(length) * 0.01 + 0.005  # Tendencia positiva
    elif trend == 'downtrend':
        # Tendencia bajista
        returns = np.random.randn(length) * 0.01 - 0.005  # Tendencia negativa
    else:
        # Neutral
        returns = np.random.randn(length) * 0.02
    
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = {
        'close': prices,
        'open': prices * (1 + np.random.randn(length) * 0.005),
        'high': prices + np.abs(np.random.randn(length) * 0.5),
        'low': prices - np.abs(np.random.randn(length) * 0.5),
        'volume': np.random.randint(1000000, 10000000, length),
    }
    
    df = pd.DataFrame(data)
    df['date'] = pd.date_range(start='2024-01-01', periods=length, freq='D')
    
    return df


def test_get_trading_signals():
    """Test generación de señales de trading"""
    try:
        df = create_sample_data(length=100)
        
        signals = TechnicalIndicators.get_trading_signals(df)
        
        assert 'rsi_signal' in signals, "Debe incluir señal RSI"
        assert 'macd_signal' in signals, "Debe incluir señal MACD"
        assert 'bb_signal' in signals, "Debe incluir señal Bollinger Bands"
        
        print("✅ Señales de trading generadas:")
        print(f"   RSI: {signals['rsi_signal']}")
        print(f"   MACD: {signals['macd_signal']}")
        print(f"   Bollinger Bands: {signals['bb_signal']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en generación de señales: {e}")
        return False


def test_rsi_oversold_signal():
    """Test señal de sobreventa en RSI"""
    try:
        # Crear datos con tendencia bajista para generar RSI bajo
        df = create_sample_data(length=50, trend='downtrend')
        
        # Forzar un precio muy bajo al final
        df.loc[df.index[-5:], 'close'] = df['close'].iloc[-6] * 0.8
        
        signals = TechnicalIndicators.get_trading_signals(df)
        
        # Verificar que se genera alguna señal
        assert signals['rsi_signal'] != 'N/A', "Señal RSI no debe ser N/A"
        
        print("✅ Señal RSI con tendencia bajista:")
        print(f"   {signals['rsi_signal']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en test RSI sobreventa: {e}")
        return False


def test_calculate_all_with_signals():
    """Test cálculo de todos los indicadores incluyendo señales"""
    try:
        df = create_sample_data(length=100)
        
        # Calcular todos los indicadores
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Verificar que se agregaron las columnas
        expected_cols = ['rsi', 'macd', 'macd_signal', 'macd_hist', 
                        'bb_lower', 'bb_middle', 'bb_upper']
        
        for col in expected_cols:
            assert col in df_with_indicators.columns, f"Columna {col} faltante"
        
        # Generar señales
        signals = TechnicalIndicators.get_trading_signals(df)
        
        print("✅ Indicadores y señales calculados correctamente")
        print(f"   Columnas en DataFrame: {len(df_with_indicators.columns)}")
        print(f"   Señales generadas: {len(signals)}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en test completo: {e}")
        return False


def test_signals_consistency():
    """Test consistencia de señales"""
    try:
        # Generar señales múltiples veces con mismos datos
        df = create_sample_data(length=100)
        
        signals1 = TechnicalIndicators.get_trading_signals(df)
        signals2 = TechnicalIndicators.get_trading_signals(df)
        
        # Las señales deben ser idénticas
        assert signals1 == signals2, "Señales deben ser consistentes"
        
        print("✅ Señales son consistentes entre llamadas")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en test de consistencia: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE SEÑALES DE TRADING")
    print("=" * 70 + "\n")
    
    tests = [
        ("Generación de Señales", test_get_trading_signals),
        ("Señal RSI Sobreventa", test_rsi_oversold_signal),
        ("Cálculo Completo", test_calculate_all_with_signals),
        ("Consistencia de Señales", test_signals_consistency),
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
