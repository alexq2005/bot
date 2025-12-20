"""
Test de Pattern Recognition
Pruebas para reconocimiento de patrones de velas
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.pattern_recognition import CandlestickPatterns, PatternRecognizer


def test_detect_doji():
    """Test detección de Doji"""
    try:
        patterns = CandlestickPatterns()
        
        # Doji: apertura ≈ cierre
        is_doji = patterns.detect_doji(
            open_price=100.0,
            close_price=100.05,  # Muy cerca de apertura (0.05%)
            high_price=102.0,
            low_price=98.0,
            threshold=0.02  # 2% threshold
        )
        
        assert is_doji, "Debe detectar Doji"
        
        # No Doji: cuerpo grande
        not_doji = patterns.detect_doji(
            open_price=100.0,
            close_price=105.0,
            high_price=106.0,
            low_price=99.0
        )
        
        assert not not_doji, "No debe detectar Doji con cuerpo grande"
        
        print("✅ Detección de Doji funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en Doji: {e}")
        return False


def test_detect_hammer():
    """Test detección de Hammer"""
    try:
        patterns = CandlestickPatterns()
        
        # Hammer: sombra inferior larga, cuerpo pequeño arriba
        is_hammer = patterns.detect_hammer(
            open_price=100.0,
            close_price=101.0,
            high_price=102.0,
            low_price=95.0  # Sombra larga abajo
        )
        
        assert is_hammer, "Debe detectar Hammer"
        
        print("✅ Detección de Hammer funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en Hammer: {e}")
        return False


def test_detect_shooting_star():
    """Test detección de Shooting Star"""
    try:
        patterns = CandlestickPatterns()
        
        # Shooting Star: sombra superior larga, cuerpo pequeño abajo
        is_shooting = patterns.detect_shooting_star(
            open_price=100.0,
            close_price=99.0,
            high_price=105.0,  # Sombra larga arriba
            low_price=98.0
        )
        
        assert is_shooting, "Debe detectar Shooting Star"
        
        print("✅ Detección de Shooting Star funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en Shooting Star: {e}")
        return False


def test_detect_engulfing():
    """Test detección de Engulfing"""
    try:
        patterns = CandlestickPatterns()
        
        # Bullish Engulfing
        result = patterns.detect_engulfing(
            prev_open=102.0,
            prev_close=100.0,  # Vela bajista
            curr_open=99.0,
            curr_close=103.0   # Vela alcista que envuelve
        )
        
        assert result == 'bullish', "Debe detectar Bullish Engulfing"
        
        # Bearish Engulfing
        result = patterns.detect_engulfing(
            prev_open=100.0,
            prev_close=102.0,  # Vela alcista
            curr_open=103.0,
            curr_close=99.0    # Vela bajista que envuelve
        )
        
        assert result == 'bearish', "Debe detectar Bearish Engulfing"
        
        print("✅ Detección de Engulfing funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en Engulfing: {e}")
        return False


def test_pattern_recognizer():
    """Test reconocedor de patrones en DataFrame"""
    try:
        recognizer = PatternRecognizer()
        
        # Crear datos de ejemplo
        np.random.seed(42)
        length = 50
        base_price = 100
        
        prices = base_price + np.cumsum(np.random.randn(length) * 2)
        
        df = pd.DataFrame({
            'open': prices + np.random.randn(length) * 0.5,
            'close': prices + np.random.randn(length) * 0.5,
            'high': prices + np.abs(np.random.randn(length)) * 1.5,
            'low': prices - np.abs(np.random.randn(length)) * 1.5
        })
        
        # Escanear patrones
        patterns = recognizer.scan_patterns(df)
        
        assert isinstance(patterns, dict), "Debe retornar un dict"
        assert 'doji' in patterns, "Debe incluir patrones Doji"
        assert 'hammer' in patterns, "Debe incluir patrones Hammer"
        
        print("✅ Pattern Recognizer funciona:")
        print(f"   Dojis encontrados: {len(patterns['doji'])}")
        print(f"   Hammers encontrados: {len(patterns['hammer'])}")
        print(f"   Shooting Stars encontrados: {len(patterns['shooting_star'])}")
        print(f"   Bullish Engulfing: {len(patterns['bullish_engulfing'])}")
        print(f"   Bearish Engulfing: {len(patterns['bearish_engulfing'])}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en Pattern Recognizer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_recent_patterns():
    """Test obtención de patrones recientes"""
    try:
        recognizer = PatternRecognizer()
        
        # Crear datos
        np.random.seed(42)
        length = 30
        prices = 100 + np.cumsum(np.random.randn(length) * 2)
        
        df = pd.DataFrame({
            'open': prices,
            'close': prices + np.random.randn(length) * 0.5,
            'high': prices + np.abs(np.random.randn(length)),
            'low': prices - np.abs(np.random.randn(length))
        })
        
        recent = recognizer.get_recent_patterns(df, lookback=10)
        
        assert isinstance(recent, dict), "Debe retornar un dict"
        
        # Todos los valores deben ser booleanos
        for pattern, found in recent.items():
            assert isinstance(found, bool), f"{pattern} debe ser bool"
        
        print("✅ Patrones recientes funciona:")
        print(f"   Patrones en últimas 10 velas:")
        for pattern, found in recent.items():
            if found:
                print(f"      ✓ {pattern}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en patrones recientes: {e}")
        return False


def test_get_pattern_signal():
    """Test generación de señal desde patrones"""
    try:
        recognizer = PatternRecognizer()
        
        # Crear datos con tendencia alcista
        np.random.seed(42)
        length = 20
        prices = 100 + np.cumsum(np.random.randn(length) * 0.5 + 0.5)
        
        df = pd.DataFrame({
            'open': prices,
            'close': prices + 0.5,  # Velas alcistas
            'high': prices + 1,
            'low': prices - 0.5
        })
        
        signal = recognizer.get_pattern_signal(df)
        
        assert signal in ['BULLISH (Patrones alcistas detectados)', 
                         'BEARISH (Patrones bajistas detectados)', 
                         'NEUTRAL (Sin patrones claros)']
        
        print("✅ Señal de patrones funciona:")
        print(f"   Señal generada: {signal}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo en señal de patrones: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE PATTERN RECOGNITION")
    print("=" * 70 + "\n")
    
    tests = [
        ("Detección Doji", test_detect_doji),
        ("Detección Hammer", test_detect_hammer),
        ("Detección Shooting Star", test_detect_shooting_star),
        ("Detección Engulfing", test_detect_engulfing),
        ("Pattern Recognizer", test_pattern_recognizer),
        ("Patrones Recientes", test_get_recent_patterns),
        ("Señal de Patrones", test_get_pattern_signal),
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
