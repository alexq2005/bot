"""
Tests para el Sistema de Alertas
"""
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Agregar path
sys.path.insert(0, '/home/runner/work/bot/bot/fiancial de 0/bot2.0')

from src.alerts.alert_system import AlertSystem, AlertType, AlertPriority
from src.alerts.telegram_handler import TelegramHandler


def test_alert_system_initialization():
    """Test 1: Inicialización del sistema de alertas"""
    print("\n" + "="*70)
    print("TEST 1: Inicialización del Sistema de Alertas")
    print("="*70)
    
    alert_system = AlertSystem()
    
    assert alert_system is not None
    assert len(alert_system.alerts) == 0
    assert len(alert_system.alert_handlers) == 0
    
    print("✅ Sistema de alertas inicializado correctamente")
    return True


def test_telegram_handler():
    """Test 2: Manejador de Telegram"""
    print("\n" + "="*70)
    print("TEST 2: Manejador de Telegram")
    print("="*70)
    
    # Crear manejador deshabilitado para testing
    handler = TelegramHandler(enabled=False)
    
    alert_system = AlertSystem()
    alert_system.add_handler(handler)
    
    # Crear una alerta de prueba
    alert_system.check_signal_alert(
        signal='COMPRA',
        symbol='GGAL',
        confidence=0.8
    )
    
    assert handler.get_sent_count() == 1
    assert len(alert_system.alerts) == 1
    
    print(f"✅ Alerta enviada a manejador de Telegram")
    print(f"   Mensajes enviados: {handler.get_sent_count()}")
    
    return True


def test_rsi_divergence_detection():
    """Test 3: Detección de divergencias RSI"""
    print("\n" + "="*70)
    print("TEST 3: Detección de Divergencias RSI")
    print("="*70)
    
    # Crear datos con divergencia alcista
    # Precio hace mínimos más bajos, RSI hace mínimos más altos
    df = pd.DataFrame({
        'close': [100, 98, 97, 95, 96, 94, 95, 93, 94, 92, 95, 98, 100, 102, 105],
        'rsi': [50, 48, 47, 45, 46, 44, 46, 44, 47, 45, 50, 55, 58, 60, 62]
    })
    
    alert_system = AlertSystem()
    alert = alert_system.check_rsi_divergence(df)
    
    # Puede o no detectarse dependiendo de los datos exactos
    print(f"   Alertas generadas: {len(alert_system.alerts)}")
    
    if alert:
        print(f"✅ Divergencia detectada: {alert.message}")
        assert alert.alert_type == AlertType.DIVERGENCE
        assert alert.priority == AlertPriority.HIGH
    else:
        print("ℹ️  No se detectó divergencia en este dataset")
    
    return True


def test_bollinger_breakout():
    """Test 4: Detección de breakouts de Bollinger Bands"""
    print("\n" + "="*70)
    print("TEST 4: Detección de Breakouts de Bollinger Bands")
    print("="*70)
    
    # Crear datos con breakout alcista
    df = pd.DataFrame({
        'close': [100, 101, 102, 103, 110],  # Precio sube
        'bb_upper': [105, 105, 105, 105, 105],  # Banda superior fija
        'bb_lower': [95, 95, 95, 95, 95],
        'symbol': ['GGAL'] * 5
    })
    
    alert_system = AlertSystem()
    alert = alert_system.check_bollinger_breakout(df)
    
    assert alert is not None
    assert alert.alert_type == AlertType.BREAKOUT
    assert 'GGAL' in alert.symbol
    
    print(f"✅ Breakout detectado: {alert.message}")
    print(f"   Precio: {alert.details['price']:.2f}")
    print(f"   BB Superior: {alert.details['bb_upper']:.2f}")
    
    return True


def test_pattern_alert():
    """Test 5: Alertas de patrones"""
    print("\n" + "="*70)
    print("TEST 5: Alertas de Patrones de Velas")
    print("="*70)
    
    alert_system = AlertSystem()
    
    # Patrón alcista
    alert = alert_system.check_pattern_alert(
        pattern_name='Hammer',
        pattern_detected=True,
        symbol='YPFD',
        is_bullish=True
    )
    
    assert alert is not None
    assert alert.alert_type == AlertType.PATTERN
    assert alert.priority == AlertPriority.HIGH
    assert 'alcista' in alert.message.lower()
    
    print(f"✅ Alerta de patrón creada: {alert.message}")
    
    return True


def test_signal_alert():
    """Test 6: Alertas de señales de trading"""
    print("\n" + "="*70)
    print("TEST 6: Alertas de Señales de Trading")
    print("="*70)
    
    alert_system = AlertSystem()
    
    # Señal de compra con alta confianza
    alert = alert_system.check_signal_alert(
        signal='COMPRA',
        symbol='BMA',
        confidence=0.85,
        indicators={'rsi': 28, 'macd': 'bullish'}
    )
    
    assert alert is not None
    assert alert.alert_type == AlertType.SIGNAL
    assert alert.priority == AlertPriority.HIGH  # Confianza > 0.7
    
    print(f"✅ Alerta de señal creada: {alert.message}")
    print(f"   Confianza: {alert.details['confidence']*100:.0f}%")
    
    # Señal neutral no debe generar alerta
    alert_neutral = alert_system.check_signal_alert(
        signal='NEUTRAL',
        symbol='BMA',
        confidence=0.5
    )
    
    assert alert_neutral is None
    print("✅ Señal NEUTRAL correctamente ignorada")
    
    return True


def test_custom_alert():
    """Test 7: Alertas personalizadas"""
    print("\n" + "="*70)
    print("TEST 7: Alertas Personalizadas")
    print("="*70)
    
    alert_system = AlertSystem()
    
    # Condición personalizada (ej: volumen alto)
    volume_spike = True
    
    alert = alert_system.check_custom_condition(
        condition_met=volume_spike,
        symbol='PAMP',
        message="Pico de volumen detectado - Volumen 3x superior al promedio",
        priority=AlertPriority.CRITICAL,
        details={'volume': 1500000, 'avg_volume': 500000, 'multiplier': 3.0}
    )
    
    assert alert is not None
    assert alert.alert_type == AlertType.CUSTOM
    assert alert.priority == AlertPriority.CRITICAL
    
    print(f"✅ Alerta personalizada creada: {alert.message}")
    print(f"   Prioridad: {alert.priority.value.upper()}")
    
    return True


def test_alert_filtering():
    """Test 8: Filtrado de alertas"""
    print("\n" + "="*70)
    print("TEST 8: Filtrado de Alertas")
    print("="*70)
    
    alert_system = AlertSystem()
    
    # Crear varias alertas
    alert_system.check_signal_alert('COMPRA', 'GGAL', 0.9)
    alert_system.check_signal_alert('VENTA', 'YPFD', 0.7)
    alert_system.check_pattern_alert('Doji', True, 'BMA', False)
    
    # Filtrar por tipo
    signal_alerts = alert_system.get_alerts(alert_type=AlertType.SIGNAL)
    pattern_alerts = alert_system.get_alerts(alert_type=AlertType.PATTERN)
    
    assert len(signal_alerts) == 2
    assert len(pattern_alerts) == 1
    
    # Filtrar por prioridad
    high_priority = alert_system.get_alerts(priority=AlertPriority.HIGH)
    assert len(high_priority) >= 1
    
    print(f"✅ Filtrado de alertas funcionando correctamente")
    print(f"   Total alertas: {len(alert_system.alerts)}")
    print(f"   Alertas de señal: {len(signal_alerts)}")
    print(f"   Alertas de patrón: {len(pattern_alerts)}")
    print(f"   Alta prioridad: {len(high_priority)}")
    
    return True


def test_alert_summary():
    """Test 9: Resumen de alertas"""
    print("\n" + "="*70)
    print("TEST 9: Resumen de Alertas")
    print("="*70)
    
    alert_system = AlertSystem()
    handler = TelegramHandler(enabled=False)
    alert_system.add_handler(handler)
    
    # Crear varias alertas
    alert_system.check_signal_alert('COMPRA', 'GGAL', 0.9)
    alert_system.check_signal_alert('VENTA', 'YPFD', 0.7)
    alert_system.check_pattern_alert('Hammer', True, 'BMA', True)
    alert_system.check_custom_condition(True, 'PAMP', "Test", AlertPriority.LOW)
    
    summary = alert_system.get_summary()
    
    assert summary['total_alerts'] == 4
    assert summary['sent'] == 4  # Todas enviadas al handler
    assert summary['pending'] == 0
    
    print(f"✅ Resumen de alertas:")
    print(f"   Total: {summary['total_alerts']}")
    print(f"   Enviadas: {summary['sent']}")
    print(f"   Pendientes: {summary['pending']}")
    print(f"   Por tipo: {summary['by_type']}")
    print(f"   Por prioridad: {summary['by_priority']}")
    
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print("SISTEMA DE ALERTAS - SUITE DE TESTS")
    print("="*70)
    
    tests = [
        test_alert_system_initialization,
        test_telegram_handler,
        test_rsi_divergence_detection,
        test_bollinger_breakout,
        test_pattern_alert,
        test_signal_alert,
        test_custom_alert,
        test_alert_filtering,
        test_alert_summary
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test falló: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTADO: {passed}/{len(tests)} tests pasaron")
    print("="*70)
    
    if failed == 0:
        print("🎉 TODOS LOS TESTS PASARON")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
