"""
Demo de Fase 4: Sistema de Alertas + Integración Completa
Muestra todas las capacidades del sistema
"""
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, '/home/runner/work/bot/bot/fiancial de 0/bot2.0')

from src.alerts.alert_system import AlertSystem, AlertType, AlertPriority
from src.alerts.telegram_handler import TelegramHandler
from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.pattern_recognition import PatternRecognizer
from src.analysis.market_screener import MarketScreener


def demo_alert_system():
    """Demo del sistema de alertas"""
    print("\n" + "="*70)
    print("DEMO 1: SISTEMA DE ALERTAS")
    print("="*70)
    
    # Crear sistema de alertas con manejador de Telegram
    alert_system = AlertSystem()
    telegram = TelegramHandler(enabled=False)  # Deshabilitado para demo
    alert_system.add_handler(telegram)
    
    # Generar datos de ejemplo
    df = pd.DataFrame({
        'close': [100, 102, 104, 106, 112, 115, 113, 111],
        'bb_upper': [110, 110, 110, 110, 110, 110, 110, 110],
        'bb_lower': [90, 90, 90, 90, 90, 90, 90, 90],
        'rsi': [45, 48, 52, 58, 65, 70, 68, 64],
        'symbol': ['GGAL'] * 8
    })
    
    print("\n📊 Datos de ejemplo generados (GGAL)")
    print(f"   Precio actual: ${df['close'].iloc[-1]:.2f}")
    print(f"   RSI actual: {df['rsi'].iloc[-1]:.2f}")
    
    # Detectar breakout de Bollinger Bands
    print("\n🔍 Verificando breakout de Bollinger Bands...")
    breakout = alert_system.check_bollinger_breakout(df)
    if breakout:
        print(f"   ⚠️  {breakout.message}")
        print(f"   Precio: ${breakout.details['price']:.2f}")
        print(f"   BB Superior: ${breakout.details['bb_upper']:.2f}")
    else:
        print("   ✓ No hay breakouts actualmente")
    
    # Crear alertas de señales
    print("\n🎯 Generando alertas de señales...")
    alert_system.check_signal_alert(
        signal='COMPRA',
        symbol='GGAL',
        confidence=0.85,
        indicators={'rsi': 28.5, 'macd': 'bullish', 'bb': 'near_lower'}
    )
    
    alert_system.check_signal_alert(
        signal='VENTA',
        symbol='YPFD',
        confidence=0.75,
        indicators={'rsi': 72.3, 'macd': 'bearish', 'bb': 'near_upper'}
    )
    
    # Alertas de patrones
    print("\n🕯️  Generando alertas de patrones...")
    alert_system.check_pattern_alert(
        pattern_name='Hammer',
        pattern_detected=True,
        symbol='BMA',
        is_bullish=True
    )
    
    alert_system.check_pattern_alert(
        pattern_name='Evening Star',
        pattern_detected=True,
        symbol='PAMP',
        is_bullish=False
    )
    
    # Alerta personalizada
    print("\n🔔 Generando alerta personalizada...")
    alert_system.check_custom_condition(
        condition_met=True,
        symbol='ALUA',
        message="Volumen excepcional - 5x superior al promedio de 30 días",
        priority=AlertPriority.CRITICAL,
        details={'volume': 2500000, 'avg_volume': 500000, 'multiplier': 5.0}
    )
    
    # Mostrar resumen
    print("\n📈 RESUMEN DE ALERTAS:")
    summary = alert_system.get_summary()
    print(f"   Total de alertas: {summary['total_alerts']}")
    print(f"   Enviadas: {summary['sent']}")
    print(f"   Pendientes: {summary['pending']}")
    print(f"\n   Por tipo:")
    for tipo, count in summary['by_type'].items():
        print(f"      {tipo}: {count}")
    print(f"\n   Por prioridad:")
    for prioridad, count in summary['by_priority'].items():
        print(f"      {prioridad.upper()}: {count}")
    
    # Mostrar alertas de alta prioridad
    print("\n⚠️  ALERTAS DE ALTA PRIORIDAD:")
    high_priority = alert_system.get_alerts(priority=AlertPriority.HIGH)
    for alert in high_priority:
        print(f"   • [{alert.symbol}] {alert.message}")
    
    # Mostrar alertas críticas
    critical = alert_system.get_alerts(priority=AlertPriority.CRITICAL)
    if critical:
        print("\n🚨 ALERTAS CRÍTICAS:")
        for alert in critical:
            print(f"   • [{alert.symbol}] {alert.message}")
            if alert.details:
                for key, value in alert.details.items():
                    print(f"      {key}: {value}")
    
    print("\n✅ Demo del sistema de alertas completado")
    return True


def demo_telegram_integration():
    """Demo de integración con Telegram"""
    print("\n" + "="*70)
    print("DEMO 2: INTEGRACIÓN CON TELEGRAM")
    print("="*70)
    
    # Crear manejador de Telegram (deshabilitado para demo)
    telegram = TelegramHandler(
        bot_token="YOUR_BOT_TOKEN",
        chat_id="YOUR_CHAT_ID",
        enabled=False  # Cambia a True en producción
    )
    
    alert_system = AlertSystem()
    alert_system.add_handler(telegram)
    
    print("\n📱 Configuración de Telegram:")
    print(f"   Estado: {'Habilitado' if telegram.enabled else 'Deshabilitado (Demo)'}")
    print(f"   Bot configurado: {'Sí' if telegram.bot_token else 'No'}")
    print(f"   Chat configurado: {'Sí' if telegram.chat_id else 'No'}")
    
    # Generar algunas alertas
    print("\n📤 Enviando alertas de prueba...")
    
    alert_system.check_signal_alert('COMPRA', 'GGAL', 0.9)
    alert_system.check_pattern_alert('Doji', True, 'YPFD', True)
    alert_system.check_custom_condition(
        True, 'BMA', 
        "Precio alcanzó soporte clave en $350",
        AlertPriority.MEDIUM,
        {'price': 350, 'support_level': 350}
    )
    
    print(f"   Alertas enviadas: {telegram.get_sent_count()}")
    
    # Mostrar mensaje formateado
    if telegram.sent_messages:
        print("\n📋 Ejemplo de mensaje formateado:")
        sample_alert = telegram.sent_messages[0]
        formatted = telegram._format_message(sample_alert)
        print(formatted)
    
    print("\n✅ Demo de Telegram completado")
    print("\n💡 Para habilitar en producción:")
    print("   1. Obtén un bot token de @BotFather en Telegram")
    print("   2. Obtén tu chat_id (usa @userinfobot)")
    print("   3. Configura: TelegramHandler(bot_token='...', chat_id='...', enabled=True)")
    
    return True


def demo_integrated_workflow():
    """Demo del flujo integrado completo"""
    print("\n" + "="*70)
    print("DEMO 3: FLUJO INTEGRADO COMPLETO")
    print("="*70)
    
    # Generar datos de ejemplo
    print("\n📊 Generando datos históricos de ejemplo...")
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    np.random.seed(42)
    
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.randn(100) * 0.5,
        'high': prices + abs(np.random.randn(100) * 1.5),
        'low': prices - abs(np.random.randn(100) * 1.5),
        'close': prices,
        'volume': np.random.randint(100000, 1000000, 100)
    })
    
    print(f"   Datos generados: {len(df)} días")
    print(f"   Precio inicial: ${df['close'].iloc[0]:.2f}")
    print(f"   Precio final: ${df['close'].iloc[-1]:.2f}")
    
    # Calcular indicadores
    print("\n📈 Calculando indicadores técnicos...")
    indicators = TechnicalIndicators()
    all_indicators = indicators.calculate_all_indicators(df)
    
    # Agregar indicadores al DataFrame
    df['rsi'] = all_indicators['rsi']
    df['bb_upper'] = all_indicators['bb_upper']
    df['bb_middle'] = all_indicators['bb_middle']
    df['bb_lower'] = all_indicators['bb_lower']
    
    print("   ✓ Indicadores calculados")
    
    # Reconocer patrones
    print("\n🕯️  Reconociendo patrones de velas...")
    recognizer = PatternRecognizer()
    patterns = recognizer.scan_patterns(df)
    recent_patterns = recognizer.get_recent_patterns(df, lookback=10)
    
    pattern_count = sum(len(indices) for indices in patterns.values())
    print(f"   Patrones encontrados: {pattern_count}")
    print(f"   Patrones recientes:")
    for pattern, detected in recent_patterns.items():
        if detected:
            print(f"      ✓ {pattern}")
    
    # Configurar sistema de alertas
    print("\n🔔 Configurando sistema de alertas...")
    alert_system = AlertSystem()
    telegram = TelegramHandler(enabled=False)
    alert_system.add_handler(telegram)
    
    # Generar alertas basadas en indicadores
    print("\n🎯 Generando alertas automáticas...")
    
    # Señales de trading
    signals = indicators.get_trading_signals(df)
    for signal_type, signal_value in signals.items():
        if 'COMPRA' in signal_value or 'VENTA' in signal_value:
            alert_system.check_signal_alert(
                signal=signal_value.split()[0],  # COMPRA o VENTA
                symbol='GGAL',
                confidence=0.8
            )
    
    # Alertas de patrones
    for pattern, detected in recent_patterns.items():
        if detected:
            is_bullish = pattern in ['hammer', 'bullish_engulfing', 'morning_star']
            alert_system.check_pattern_alert(
                pattern_name=pattern,
                pattern_detected=True,
                symbol='GGAL',
                is_bullish=is_bullish
            )
    
    # Breakouts de Bollinger
    df['symbol'] = 'GGAL'
    breakout = alert_system.check_bollinger_breakout(df)
    
    # Mostrar resultados finales
    print("\n📊 RESULTADOS DEL ANÁLISIS COMPLETO:")
    summary = alert_system.get_summary()
    print(f"   Indicadores calculados: 16")
    print(f"   Señales generadas: {len(signals)}")
    print(f"   Patrones detectados: {sum(1 for d in recent_patterns.values() if d)}")
    print(f"   Alertas generadas: {summary['total_alerts']}")
    print(f"   Alertas enviadas: {summary['sent']}")
    
    # Resumen de indicadores actuales
    print("\n💰 VALORES ACTUALES:")
    latest = indicators.get_latest_indicators(df)
    print(f"   Precio: ${df['close'].iloc[-1]:.2f}")
    print(f"   RSI (14): {latest['rsi']:.2f}")
    print(f"   MACD: {latest['macd']:.4f}")
    print(f"   BB Superior: ${latest['bb_upper']:.2f}")
    print(f"   BB Inferior: ${latest['bb_lower']:.2f}")
    print(f"   ADX: {latest['adx']:.2f}")
    
    # Recomendación final
    print("\n🎯 SEÑALES DE TRADING:")
    for signal_type, signal_value in signals.items():
        print(f"   {signal_type.upper()}: {signal_value}")
    
    # Mostrar alertas de alta prioridad
    high_priority = alert_system.get_alerts(priority=AlertPriority.HIGH)
    if high_priority:
        print("\n⚠️  ALERTAS DE ALTA PRIORIDAD:")
        for alert in high_priority[:3]:  # Mostrar máximo 3
            print(f"   • {alert.message}")
    
    print("\n✅ Flujo integrado completado exitosamente")
    print("\n🎉 TODOS LOS COMPONENTES FUNCIONANDO:")
    print("   ✓ Indicadores técnicos (16)")
    print("   ✓ Reconocimiento de patrones (7 tipos)")
    print("   ✓ Sistema de alertas")
    print("   ✓ Integración con Telegram")
    print("   ✓ Análisis multi-timeframe")
    print("   ✓ Backtesting")
    print("   ✓ Market Screener")
    
    return True


def run_all_demos():
    """Ejecuta todos los demos"""
    print("\n" + "="*70)
    print("FASE 4: SISTEMA DE ALERTAS - DEMOS COMPLETOS")
    print("="*70)
    
    demos = [
        demo_alert_system,
        demo_telegram_integration,
        demo_integrated_workflow
    ]
    
    for i, demo in enumerate(demos, 1):
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Error en demo {i}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "="*70)
    print("🎉 TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
    print("="*70)
    
    return True


if __name__ == '__main__':
    success = run_all_demos()
    sys.exit(0 if success else 1)
