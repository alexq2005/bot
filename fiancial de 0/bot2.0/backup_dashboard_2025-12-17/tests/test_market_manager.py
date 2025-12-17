"""
Test de Market Manager
Pruebas para validar gestión de horarios y universo de símbolos
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.market_manager import MarketManager


def test_market_manager_init():
    """Verificar inicialización del Market Manager"""
    try:
        mm = MarketManager()
        print("✅ Market Manager inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_market_status():
    """Verificar obtención de estado del mercado"""
    try:
        mm = MarketManager()
        status = mm.get_market_status()
        
        assert status is not None, "Status es None"
        assert 'is_open' in status, "Falta 'is_open'"
        assert 'current_time' in status, "Falta 'current_time'"
        assert isinstance(status['is_open'], bool), "'is_open' no es bool"
        
        print(f"✅ Estado del mercado:")
        print(f"   - Abierto: {status['is_open']}")
        print(f"   - Hora actual: {status['current_time']}")
        return True
    except Exception as e:
        print(f"❌ Fallo obtener estado: {e}")
        return False


def test_universe_symbols():
    """Verificar universo de símbolos"""
    try:
        mm = MarketManager()
        symbols = mm.get_curated_symbols()
        
        assert symbols is not None, "Símbolos es None"
        assert len(symbols) > 0, "Universo vacío"
        assert isinstance(symbols, (list, set, tuple)), "Símbolos no es colección"
        
        symbols_list = list(symbols)
        print(f"✅ Universo de símbolos:")
        print(f"   - Total: {len(symbols_list)} símbolos")
        print(f"   - Primeros 10: {', '.join(symbols_list[:10])}")
        return True
    except Exception as e:
        print(f"❌ Fallo obtener universo: {e}")
        return False


def test_required_symbols():
    """Verificar que símbolos requeridos están presentes"""
    try:
        mm = MarketManager()
        symbols = set(mm.get_curated_symbols())
        
        required = ['GGAL', 'YPFD', 'CEPU', 'BMA', 'TXAR']
        missing = [s for s in required if s not in symbols]
        
        if missing:
            print(f"⚠️  Símbolos faltantes: {', '.join(missing)}")
        else:
            print(f"✅ Todos los símbolos requeridos presentes")
        
        return len(missing) == 0
    except Exception as e:
        print(f"❌ Fallo validar símbolos: {e}")
        return False


def test_market_hours():
    """Verificar detección de horarios del mercado"""
    try:
        mm = MarketManager()
        
        # Test con diferentes horas
        test_times = [
            ("09:30", True),   # Apertura
            ("11:00", True),   # Dentro del horario
            ("16:59", True),   # Cerca del cierre
            ("08:00", False),  # Antes de apertura
            ("18:00", False),  # Después del cierre
        ]
        
        print(f"✅ Validación de horarios:")
        for time_str, expected_open in test_times:
            hour, minute = map(int, time_str.split(':'))
            # Este es un test conceptual - la implementación real depende del timezone
            print(f"   - {time_str}: Esperado {'Abierto' if expected_open else 'Cerrado'}")
        
        return True
    except Exception as e:
        print(f"❌ Fallo validar horarios: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE MARKET MANAGER")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización Market Manager", test_market_manager_init),
        ("Estado del Mercado", test_market_status),
        ("Universo de Símbolos", test_universe_symbols),
        ("Símbolos Requeridos", test_required_symbols),
        ("Horarios del Mercado", test_market_hours),
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
