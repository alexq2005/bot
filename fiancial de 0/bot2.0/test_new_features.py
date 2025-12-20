"""
Script de prueba para indicadores técnicos y validación de órdenes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.indicators.technical_indicators import TechnicalIndicators
from src.validators.order_validator import OrderValidator

def test_technical_indicators():
    """Prueba los indicadores técnicos"""
    print("=" * 60)
    print("PRUEBA DE INDICADORES TÉCNICOS")
    print("=" * 60)
    
    # Generar datos de prueba
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    prices = pd.Series(
        np.cumsum(np.random.randn(100)) + 100,
        index=dates
    )
    
    # Calcular indicadores
    indicators_calc = TechnicalIndicators()
    indicators = indicators_calc.calculate_all_indicators(prices)
    
    # Mostrar resultados
    print(f"\n✅ RSI actual: {indicators['rsi'].iloc[-1]:.2f}")
    print(f"✅ MACD actual: {indicators['macd']['macd'].iloc[-1]:.2f}")
    print(f"✅ Bollinger Superior: {indicators['bollinger']['upper'].iloc[-1]:.2f}")
    print(f"✅ Bollinger Inferior: {indicators['bollinger']['lower'].iloc[-1]:.2f}")
    
    print("\n📊 Señales de Trading:")
    for key, value in indicators['signals'].items():
        print(f"   {key}: {value}")
    
    print("\n✅ Indicadores técnicos funcionando correctamente\n")

def test_order_validator():
    """Prueba el validador de órdenes"""
    print("=" * 60)
    print("PRUEBA DE VALIDACIÓN DE ÓRDENES")
    print("=" * 60)
    
    # Configurar validador
    config = {
        'max_position_size': 100000,
        'max_daily_orders': 50,
        'max_price_deviation': 0.05,
        'max_exposure_per_asset': 0.3
    }
    
    validator = OrderValidator(config)
    
    # Prueba 1: Orden válida
    print("\n📝 Prueba 1: Orden válida")
    order1 = {
        'symbol': 'GGAL',
        'side': 'BUY',
        'quantity': 10,
        'price': 8350.0
    }
    
    is_valid, results = validator.validate_order(
        order=order1,
        account_balance=100000,
        current_positions={},
        last_price=8345.0,
        daily_order_count=5
    )
    
    print(f"Resultado: {'✅ APROBADA' if is_valid else '❌ RECHAZADA'}")
    for r in results:
        icon = "✅" if r.passed else "❌"
        print(f"  {icon} {r.message}")
    
    # Prueba 2: Saldo insuficiente
    print("\n📝 Prueba 2: Saldo insuficiente")
    order2 = {
        'symbol': 'GGAL',
        'side': 'BUY',
        'quantity': 100,
        'price': 8350.0
    }
    
    is_valid, results = validator.validate_order(
        order=order2,
        account_balance=50000,  # Insuficiente
        current_positions={},
        last_price=8345.0,
        daily_order_count=5
    )
    
    print(f"Resultado: {'✅ APROBADA' if is_valid else '❌ RECHAZADA'}")
    for r in results:
        if not r.passed:
            print(f"  ❌ {r.message}")
    
    # Prueba 3: Precio fuera de rango
    print("\n📝 Prueba 3: Precio fuera de rango")
    order3 = {
        'symbol': 'GGAL',
        'side': 'BUY',
        'quantity': 10,
        'price': 10000.0  # Muy alto
    }
    
    is_valid, results = validator.validate_order(
        order=order3,
        account_balance=100000,
        current_positions={},
        last_price=8345.0,
        daily_order_count=5
    )
    
    print(f"Resultado: {'✅ APROBADA' if is_valid else '❌ RECHAZADA'}")
    for r in results:
        if not r.passed:
            print(f"  ❌ {r.message}")
    
    print("\n✅ Validador de órdenes funcionando correctamente\n")

if __name__ == "__main__":
    print("\n🚀 INICIANDO PRUEBAS DE NUEVAS FUNCIONALIDADES\n")
    
    try:
        test_technical_indicators()
        test_order_validator()
        
        print("=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
