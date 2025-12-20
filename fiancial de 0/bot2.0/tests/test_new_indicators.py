"""
Test de Nuevos Indicadores
Pruebas para Stochastic, ADX y Stop Loss/Take Profit
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.technical_indicators import TechnicalIndicators


def create_sample_data(length=100):
    """Crear datos de ejemplo"""
    np.random.seed(42)
    base_price = 100
    returns = np.random.randn(length) * 0.02
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = {
        'close': prices,
        'open': prices * (1 + np.random.randn(length) * 0.005),
        'high': prices + np.abs(np.random.randn(length) * 0.5),
        'low': prices - np.abs(np.random.randn(length) * 0.5),
        'volume': np.random.randint(1000000, 10000000, length),
    }
    
    return pd.DataFrame(data)


def test_stochastic_calculation():
    """Test cálculo de Stochastic Oscillator"""
    try:
        df = create_sample_data(length=100)
        
        stoch = TechnicalIndicators.calculate_stochastic(df)
        
        assert 'stoch_k' in stoch.columns, "Debe incluir %K"
        assert 'stoch_d' in stoch.columns, "Debe incluir %D"
        assert len(stoch) == len(df), "Longitud debe coincidir"
        
        # Verificar rango 0-100
        valid_k = stoch['stoch_k'].dropna()
        valid_d = stoch['stoch_d'].dropna()
        
        assert (valid_k >= 0).all() and (valid_k <= 100).all(), "Stoch %K debe estar entre 0-100"
        assert (valid_d >= 0).all() and (valid_d <= 100).all(), "Stoch %D debe estar entre 0-100"
        
        print("✅ Cálculo de Stochastic:")
        print(f"   %K último: {stoch['stoch_k'].iloc[-1]:.2f}")
        print(f"   %D último: {stoch['stoch_d'].iloc[-1]:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo Stochastic: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_adx_calculation():
    """Test cálculo de ADX"""
    try:
        df = create_sample_data(length=100)
        
        adx = TechnicalIndicators.calculate_adx(df)
        
        assert len(adx) == len(df), "Longitud debe coincidir"
        
        # Verificar valores válidos
        valid_adx = adx.dropna()
        assert (valid_adx >= 0).all(), "ADX debe ser >= 0"
        assert (valid_adx <= 100).all(), "ADX debe ser <= 100"
        
        current_adx = adx.iloc[-1]
        
        print("✅ Cálculo de ADX:")
        print(f"   ADX actual: {current_adx:.2f}")
        
        if current_adx < 25:
            print(f"   Interpretación: Tendencia DÉBIL")
        elif current_adx < 50:
            print(f"   Interpretación: Tendencia FUERTE")
        else:
            print(f"   Interpretación: Tendencia MUY FUERTE")
        
        return True
    except Exception as e:
        print(f"❌ Fallo ADX: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_atr_stop_loss():
    """Test cálculo de Stop Loss y Take Profit basado en ATR"""
    try:
        df = create_sample_data(length=100)
        entry_price = df['close'].iloc[-1]
        
        # Test para compra
        stop_buy, tp_buy = TechnicalIndicators.calculate_atr_stop_loss(
            df, entry_price, side='BUY', atr_multiplier=2.0
        )
        
        assert stop_buy < entry_price, "Stop loss debe estar debajo del precio de entrada (BUY)"
        assert tp_buy > entry_price, "Take profit debe estar arriba del precio de entrada (BUY)"
        
        # Test para venta
        stop_sell, tp_sell = TechnicalIndicators.calculate_atr_stop_loss(
            df, entry_price, side='SELL', atr_multiplier=2.0
        )
        
        assert stop_sell > entry_price, "Stop loss debe estar arriba del precio de entrada (SELL)"
        assert tp_sell < entry_price, "Take profit debe estar debajo del precio de entrada (SELL)"
        
        risk_buy = entry_price - stop_buy
        reward_buy = tp_buy - entry_price
        rr_ratio = reward_buy / risk_buy if risk_buy > 0 else 0
        
        print("✅ Cálculo de Stop Loss/Take Profit (ATR):")
        print(f"   Precio entrada: ${entry_price:.2f}")
        print(f"\n   COMPRA:")
        print(f"   Stop Loss: ${stop_buy:.2f} (Riesgo: ${risk_buy:.2f})")
        print(f"   Take Profit: ${tp_buy:.2f} (Beneficio: ${reward_buy:.2f})")
        print(f"   Ratio R/R: {rr_ratio:.2f}:1")
        
        print(f"\n   VENTA:")
        print(f"   Stop Loss: ${stop_sell:.2f}")
        print(f"   Take Profit: ${tp_sell:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo Stop Loss: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_new_signals():
    """Test señales de Stochastic y ADX"""
    try:
        df = create_sample_data(length=100)
        
        signals = TechnicalIndicators.get_trading_signals(df)
        
        assert 'stoch_signal' in signals, "Debe incluir señal Stochastic"
        assert 'trend_strength' in signals, "Debe incluir fuerza de tendencia (ADX)"
        
        print("✅ Nuevas señales de trading:")
        print(f"   Stochastic: {signals['stoch_signal']}")
        print(f"   Fuerza de tendencia: {signals['trend_strength']}")
        print(f"\n   Señales existentes:")
        print(f"   RSI: {signals['rsi_signal']}")
        print(f"   MACD: {signals['macd_signal']}")
        print(f"   Bollinger: {signals['bb_signal']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo señales: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_indicators_integration():
    """Test integración de todos los indicadores nuevos"""
    try:
        df = create_sample_data(length=100)
        
        # Calcular todos los indicadores
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Verificar que los nuevos indicadores están presentes
        assert 'stoch_k' in df_with_indicators.columns, "Debe incluir Stoch %K"
        assert 'stoch_d' in df_with_indicators.columns, "Debe incluir Stoch %D"
        assert 'adx' in df_with_indicators.columns, "Debe incluir ADX"
        
        # Obtener valores actuales
        latest = TechnicalIndicators.get_latest_indicators(df)
        
        assert 'stoch_k' in latest, "Latest debe incluir Stoch %K"
        assert 'stoch_d' in latest, "Latest debe incluir Stoch %D"
        assert 'adx' in latest, "Latest debe incluir ADX"
        
        print("✅ Integración completa:")
        print(f"   Total de columnas: {len(df_with_indicators.columns)}")
        print(f"   Total de indicadores en latest: {len(latest)}")
        print(f"\n   Nuevos indicadores:")
        print(f"   Stochastic %K: {latest['stoch_k']:.2f}")
        print(f"   Stochastic %D: {latest['stoch_d']:.2f}")
        print(f"   ADX: {latest['adx']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo integración: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE NUEVOS INDICADORES")
    print("=" * 70 + "\n")
    
    tests = [
        ("Stochastic Oscillator", test_stochastic_calculation),
        ("ADX (Trend Strength)", test_adx_calculation),
        ("Stop Loss/Take Profit ATR", test_atr_stop_loss),
        ("Nuevas Señales", test_new_signals),
        ("Integración Completa", test_all_indicators_integration),
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
