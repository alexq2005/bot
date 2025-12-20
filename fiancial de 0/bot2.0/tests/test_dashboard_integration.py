"""
Test de Dashboard con Indicadores Técnicos
Prueba el panel de análisis técnico del dashboard
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.indicator_visualizer import IndicatorVisualizer


def test_dashboard_integration():
    """Test integración completa del dashboard"""
    try:
        # Simular datos históricos como lo haría el dashboard
        symbol = "GGAL"
        days = 90
        
        np.random.seed(42)
        base_price = 500
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        returns = np.random.randn(days) * 0.02
        prices = base_price * np.exp(np.cumsum(returns))
        
        historical_data = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.randn(days) * 0.005),
            'high': prices + np.abs(np.random.randn(days) * prices * 0.01),
            'low': prices - np.abs(np.random.randn(days) * prices * 0.01),
            'close': prices,
            'volume': np.random.randint(100000, 10000000, days)
        })
        
        # Calcular indicadores
        indicators_calc = TechnicalIndicators()
        indicators_df = indicators_calc.calculate_all_indicators(historical_data)
        
        # Obtener señales
        signals = indicators_calc.get_trading_signals(historical_data)
        
        # Crear visualización
        visualizer = IndicatorVisualizer()
        fig = visualizer.create_comprehensive_chart(historical_data, indicators_df)
        
        # Verificaciones
        assert fig is not None, "Figura debe ser creada"
        assert 'rsi_signal' in signals, "Debe incluir señal RSI"
        assert 'macd_signal' in signals, "Debe incluir señal MACD"
        assert 'bb_signal' in signals, "Debe incluir señal Bollinger"
        
        # Obtener valores actuales
        latest_indicators = indicators_calc.get_latest_indicators(historical_data)
        
        assert 'price' in latest_indicators
        assert 'rsi' in latest_indicators
        assert 'macd' in latest_indicators
        
        print("✅ Integración del dashboard funciona correctamente")
        print(f"\n📊 Análisis para {symbol}:")
        print(f"   Precio actual: ${latest_indicators['price']:.2f}")
        print(f"   RSI: {latest_indicators['rsi']:.2f}")
        print(f"   MACD: {latest_indicators['macd']:.4f}")
        print(f"\n🎯 Señales de Trading:")
        print(f"   RSI: {signals['rsi_signal']}")
        print(f"   MACD: {signals['macd_signal']}")
        print(f"   Bollinger: {signals['bb_signal']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en integración: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_symbols():
    """Test análisis de múltiples símbolos"""
    try:
        symbols = ["GGAL", "YPFD", "PAMP"]
        results = []
        
        for symbol in symbols:
            np.random.seed(hash(symbol) % 2**32)
            base_price = np.random.uniform(50, 1000)
            days = 60
            
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            returns = np.random.randn(days) * 0.02
            prices = base_price * np.exp(np.cumsum(returns))
            
            historical_data = pd.DataFrame({
                'date': dates,
                'open': prices,
                'high': prices * 1.01,
                'low': prices * 0.99,
                'close': prices,
                'volume': np.random.randint(100000, 10000000, days)
            })
            
            indicators_calc = TechnicalIndicators()
            signals = indicators_calc.get_trading_signals(historical_data)
            latest = indicators_calc.get_latest_indicators(historical_data)
            
            results.append({
                'symbol': symbol,
                'price': latest['price'],
                'rsi': latest['rsi'],
                'signals': signals
            })
        
        print("✅ Análisis de múltiples símbolos funciona")
        print("\n📊 Resumen:")
        for r in results:
            print(f"\n   {r['symbol']}:")
            print(f"      Precio: ${r['price']:.2f}")
            print(f"      RSI: {r['rsi']:.2f}")
            print(f"      Señales: {r['signals']['rsi_signal']}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en test múltiple: {e}")
        return False


def test_chart_generation():
    """Test generación de gráficos"""
    try:
        days = 100
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = 100 * np.exp(np.cumsum(np.random.randn(days) * 0.02))
        
        historical_data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.randint(100000, 10000000, days)
        })
        
        indicators_calc = TechnicalIndicators()
        indicators_df = indicators_calc.calculate_all_indicators(historical_data)
        
        visualizer = IndicatorVisualizer()
        fig = visualizer.create_comprehensive_chart(historical_data, indicators_df)
        
        # Verificar estructura del gráfico
        assert hasattr(fig, 'data'), "Figura debe tener datos"
        assert len(fig.data) > 0, "Figura debe tener trazas"
        
        print("✅ Generación de gráficos funciona")
        print(f"   Trazas en el gráfico: {len(fig.data)}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en generación de gráfico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE INTEGRACIÓN DEL DASHBOARD")
    print("=" * 70 + "\n")
    
    tests = [
        ("Integración Dashboard", test_dashboard_integration),
        ("Múltiples Símbolos", test_multiple_symbols),
        ("Generación de Gráficos", test_chart_generation),
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
