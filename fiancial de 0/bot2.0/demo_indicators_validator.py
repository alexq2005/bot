"""
Demo del Panel de Análisis Técnico
Muestra cómo funcionan los indicadores y el validador
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.indicator_visualizer import IndicatorVisualizer
from src.validators.order_validator import OrderValidator


def demo_technical_analysis():
    """Demo de análisis técnico"""
    print("\n" + "=" * 70)
    print("DEMO: ANÁLISIS TÉCNICO PROFESIONAL")
    print("=" * 70 + "\n")
    
    # Generar datos de ejemplo
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
    print(f"📊 Analizando {symbol}...")
    indicators_calc = TechnicalIndicators()
    indicators_df = indicators_calc.calculate_all_indicators(historical_data)
    
    # Obtener valores actuales
    latest = indicators_calc.get_latest_indicators(historical_data)
    
    print(f"\n💰 Valores Actuales:")
    print(f"   Precio: ${latest['price']:.2f}")
    print(f"   RSI (14): {latest['rsi']:.2f}")
    print(f"   MACD: {latest['macd']:.4f}")
    print(f"   MACD Signal: {latest['macd_signal']:.4f}")
    print(f"   BB Superior: ${latest['bb_upper']:.2f}")
    print(f"   BB Media: ${latest['bb_middle']:.2f}")
    print(f"   BB Inferior: ${latest['bb_lower']:.2f}")
    print(f"   SMA 20: ${latest['sma_20']:.2f}")
    print(f"   SMA 50: ${latest['sma_50']:.2f}")
    
    # Obtener señales
    signals = indicators_calc.get_trading_signals(historical_data)
    
    print(f"\n🎯 Señales de Trading:")
    print(f"   RSI: {signals['rsi_signal']}")
    print(f"   MACD: {signals['macd_signal']}")
    print(f"   Bollinger Bands: {signals['bb_signal']}")
    
    print("\n✅ Análisis técnico completado")


def demo_order_validation():
    """Demo de validación de órdenes"""
    print("\n" + "=" * 70)
    print("DEMO: VALIDACIÓN DE ÓRDENES PRE-EJECUCIÓN")
    print("=" * 70 + "\n")
    
    # Configurar validador
    config = {
        'max_position_size': 100000,
        'max_daily_orders': 50,
        'max_price_deviation': 0.05,
        'max_exposure_per_asset': 0.3
    }
    
    validator = OrderValidator(config)
    
    # Test 1: Orden válida
    print("📝 Test 1: Orden válida")
    order1 = {
        'symbol': 'GGAL',
        'side': 'BUY',
        'quantity': 50,
        'price': 500
    }
    
    is_valid, results = validator.validate_order(
        order=order1,
        account_balance=100000,
        current_positions={},
        last_price=500,
        daily_order_count=5
    )
    
    print(f"   Resultado: {'✅ VÁLIDA' if is_valid else '❌ RECHAZADA'}")
    print(f"   Validaciones: {len(results)}")
    
    # Test 2: Orden con saldo insuficiente
    print("\n📝 Test 2: Saldo insuficiente")
    order2 = {
        'symbol': 'GGAL',
        'side': 'BUY',
        'quantity': 1000,
        'price': 500
    }
    
    is_valid, results = validator.validate_order(
        order=order2,
        account_balance=100000,
        current_positions={},
        last_price=500,
        daily_order_count=5
    )
    
    print(f"   Resultado: {'✅ VÁLIDA' if is_valid else '❌ RECHAZADA'}")
    for r in results:
        if not r.passed and r.level.value == 'ERROR':
            print(f"   Error: {r.message}")
    
    # Test 3: Precio muy desviado
    print("\n📝 Test 3: Precio con alta desviación")
    order3 = {
        'symbol': 'GGAL',
        'side': 'BUY',
        'quantity': 10,
        'price': 600  # 20% más alto
    }
    
    is_valid, results = validator.validate_order(
        order=order3,
        account_balance=100000,
        current_positions={},
        last_price=500,
        daily_order_count=5
    )
    
    print(f"   Resultado: {'✅ VÁLIDA' if is_valid else '❌ RECHAZADA'}")
    for r in results:
        if not r.passed and r.level.value == 'ERROR':
            print(f"   Error: {r.message}")
    
    # Resumen de validaciones
    print("\n📊 Resumen de Validaciones:")
    summary = validator.get_validation_summary()
    print(f"   Total: {summary['total_validations']}")
    print(f"   Pasadas: {summary['passed']}")
    print(f"   Falladas: {summary['failed']}")
    print(f"   Tasa de éxito: {summary['success_rate']:.1f}%")
    
    print("\n✅ Validación de órdenes completada")


def demo_combined():
    """Demo combinado: análisis + validación"""
    print("\n" + "=" * 70)
    print("DEMO: FLUJO COMPLETO DE TRADING")
    print("=" * 70 + "\n")
    
    # 1. Análisis técnico
    print("🔍 Paso 1: Análisis Técnico")
    symbol = "GGAL"
    
    # Generar datos
    np.random.seed(42)
    days = 60
    prices = 500 * np.exp(np.cumsum(np.random.randn(days) * 0.02))
    
    historical_data = pd.DataFrame({
        'date': pd.date_range(end=datetime.now(), periods=days, freq='D'),
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(100000, 10000000, days)
    })
    
    indicators = TechnicalIndicators()
    signals = indicators.get_trading_signals(historical_data)
    latest = indicators.get_latest_indicators(historical_data)
    
    print(f"   Símbolo: {symbol}")
    print(f"   Precio: ${latest['price']:.2f}")
    print(f"   Señal RSI: {signals['rsi_signal']}")
    print(f"   Señal MACD: {signals['macd_signal']}")
    
    # 2. Decisión de trading (simplificada)
    print("\n💭 Paso 2: Decisión de Trading")
    # Si hay señal de compra, preparar orden
    if 'COMPRA' in signals['rsi_signal'] or 'COMPRA' in signals['macd_signal']:
        decision = 'BUY'
        print(f"   Decisión: COMPRAR (señales alcistas)")
    elif 'VENTA' in signals['rsi_signal'] or 'VENTA' in signals['macd_signal']:
        decision = 'SELL'
        print(f"   Decisión: VENDER (señales bajistas)")
    else:
        decision = 'HOLD'
        print(f"   Decisión: MANTENER (señales neutrales)")
    
    # 3. Validación de orden
    if decision in ['BUY', 'SELL']:
        print(f"\n🛡️ Paso 3: Validación de Orden")
        
        order = {
            'symbol': symbol,
            'side': decision,
            'quantity': 50,
            'price': latest['price']
        }
        
        validator = OrderValidator()
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=100000,
            current_positions={},
            last_price=latest['price'],
            daily_order_count=10
        )
        
        if is_valid:
            print(f"   ✅ Orden APROBADA")
            print(f"   Ejecutando: {order['side']} {order['quantity']} {order['symbol']} @ ${order['price']:.2f}")
        else:
            print(f"   ❌ Orden RECHAZADA")
            for r in results:
                if not r.passed and r.level.value == 'ERROR':
                    print(f"      - {r.message}")
    
    print("\n✅ Flujo completo finalizado")


if __name__ == "__main__":
    demo_technical_analysis()
    demo_order_validation()
    demo_combined()
    
    print("\n" + "=" * 70)
    print("🎉 TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
    print("=" * 70 + "\n")
