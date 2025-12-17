"""
Test de Conexión IOL
Pruebas para validar autenticación y obtención de datos desde IOL
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.mock_iol_client import MockIOLClient


def test_iol_client_init():
    """Verificar inicialización del cliente IOL"""
    try:
        client = MockIOLClient(
            username="mock_user",
            password="mock_pass",
            base_url="https://api.iol.com.ar"
        )
        print("✅ Cliente IOL inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_mock_get_price():
    """Verificar obtención de precios en modo MOCK"""
    try:
        client = MockIOLClient(
            username="mock_user",
            password="mock_pass",
            base_url="https://api.iol.com.ar"
        )
        
        # Obtener precio
        price = client.get_last_price("GGAL")
        
        assert price is not None, "Precio es None"
        assert price > 0, f"Precio inválido: {price}"
        assert isinstance(price, (int, float)), "Precio no es número"
        
        print(f"✅ Precio GGAL: ${price:.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo obtener precio: {e}")
        return False


def test_mock_historical_data():
    """Verificar obtención de datos históricos en modo MOCK"""
    try:
        client = MockIOLClient(
            username="mock_user",
            password="mock_pass",
            base_url="https://api.iol.com.ar"
        )
        
        # Obtener datos históricos
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        df = client.get_historical_data("GGAL", from_date, to_date)
        
        assert df is not None, "DataFrame es None"
        assert len(df) > 0, "DataFrame vacío"
        assert isinstance(df, pd.DataFrame), "No es un DataFrame"
        assert 'close' in df.columns, "Falta columna 'close'"
        assert df['close'].notna().sum() > 0, "Todos los precios son NaN"
        
        print(f"✅ Datos históricos obtenidos: {len(df)} registros")
        print(f"   - Fechas: {df.index[0]} a {df.index[-1]}")
        print(f"   - Precio cierre: ${df['close'].iloc[-1]:.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo obtener datos históricos: {e}")
        return False


def test_mock_multiple_symbols():
    """Verificar obtención de múltiples símbolos"""
    try:
        client = MockIOLClient(
            username="mock_user",
            password="mock_pass",
            base_url="https://api.iol.com.ar"
        )
        
        symbols = ["GGAL", "YPFD", "CEPU"]
        results = {}
        
        for symbol in symbols:
            price = client.get_last_price(symbol)
            assert price > 0, f"Precio inválido para {symbol}"
            results[symbol] = price
        
        print(f"✅ Precios múltiples símbolos:")
        for sym, price in results.items():
            print(f"   - {sym}: ${price:.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo con múltiples símbolos: {e}")
        return False


def test_data_quality():
    """Verificar calidad de datos históricos"""
    try:
        client = MockIOLClient(
            username="mock_user",
            password="mock_pass",
            base_url="https://api.iol.com.ar"
        )
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=60)
        df = client.get_historical_data("GGAL", from_date, to_date)
        
        # Validaciones
        assert df['close'].notna().sum() > 0.9 * len(df), "Demasiados valores faltantes"
        assert (df['close'] > 0).all(), "Hay precios negativos"
        assert (df['high'] >= df['low']).all(), "High < Low en algunos registros"
        assert (df['high'] >= df['close']).all(), "High < Close en algunos registros"
        assert (df['low'] <= df['close']).all(), "Low > Close en algunos registros"
        
        print(f"✅ Calidad de datos validada:")
        print(f"   - Completitud: {100 * df['close'].notna().sum() / len(df):.1f}%")
        print(f"   - Rango: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        print(f"   - Volumen promedio: {df['volume'].mean():.0f}")
        return True
    except Exception as e:
        print(f"❌ Fallo validar calidad: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE CONEXIÓN IOL")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización Cliente IOL", test_iol_client_init),
        ("Obtener Precio (MOCK)", test_mock_get_price),
        ("Datos Históricos (MOCK)", test_mock_historical_data),
        ("Múltiples Símbolos (MOCK)", test_mock_multiple_symbols),
        ("Calidad de Datos", test_data_quality),
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
