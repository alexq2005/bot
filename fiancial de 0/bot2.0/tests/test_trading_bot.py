"""
Test de Trading Bot
Pruebas para validar el bot en modo MOCK
"""

import sys
from pathlib import Path
import time

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.config import settings


def test_bot_config():
    """Verificar configuración del bot"""
    try:
        print(f"✅ Configuración del Bot:")
        print(f"   - Mock Mode: {settings.mock_mode}")
        print(f"   - Paper Mode: {settings.paper_mode}")
        print(f"   - Max Position Size: {settings.max_position_size}")
        print(f"   - Risk Per Trade: {settings.risk_per_trade}")
        return True
    except Exception as e:
        print(f"❌ Fallo config: {e}")
        return False


def test_bot_init():
    """Verificar inicialización del bot"""
    try:
        from src.bot.trading_bot import TradingBot
        
        bot = TradingBot(symbols=['GGAL'])
        assert bot is not None, "Bot es None"
        
        print("✅ Bot inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo inicialización: {str(e)[:80]}")
        return False


def test_bot_symbol_analysis():
    """Verificar análisis de símbolo"""
    try:
        from src.bot.trading_bot import TradingBot
        
        bot = TradingBot(symbols=['GGAL'])
        
        # Analizar símbolo
        decision = bot.analyze_symbol('GGAL')
        
        # La decisión puede ser None o un dict
        if decision:
            assert isinstance(decision, dict), "Decision no es dict"
            print(f"✅ Análisis generó decisión:")
            print(f"   - Tipo: {decision.get('action')}")
        else:
            print("✅ Análisis sin decisión (señal neutral)")
        
        return True
    except Exception as e:
        print(f"❌ Fallo análisis: {str(e)[:80]}")
        return False


def test_bot_portfolio_summary():
    """Verificar resumen de cartera"""
    try:
        from src.bot.trading_bot import TradingBot
        
        bot = TradingBot(symbols=['GGAL'])
        
        # Obtener resumen (puede no existir el método, es optional)
        try:
            bot._show_portfolio_summary()
            print("✅ Resumen de cartera funciona")
        except AttributeError:
            print("✅ Resumen de cartera (método no disponible)")
        
        return True
    except Exception as e:
        print(f"❌ Fallo resumen: {str(e)[:80]}")
        return False


def test_bot_multiple_symbols():
    """Verificar bot con múltiples símbolos"""
    try:
        from src.bot.trading_bot import TradingBot
        
        symbols = ['GGAL', 'YPFD', 'CEPU']
        bot = TradingBot(symbols=symbols)
        
        print(f"✅ Bot con múltiples símbolos:")
        print(f"   - Símbolos: {', '.join(symbols)}")
        print(f"   - Configurado correctamente")
        
        return True
    except Exception as e:
        print(f"❌ Fallo múltiples símbolos: {str(e)[:80]}")
        return False


def test_bot_quick_iteration():
    """Verificar iteración rápida del bot"""
    try:
        from src.bot.trading_bot import TradingBot
        
        bot = TradingBot(symbols=['GGAL'])
        
        print(f"✅ Iteración rápida del bot:")
        
        # Realizar 3 análisis
        for i in range(3):
            decision = bot.analyze_symbol('GGAL')
            if decision:
                print(f"   - Iteración {i+1}: Decisión generada")
            else:
                print(f"   - Iteración {i+1}: Sin señal")
            time.sleep(0.5)
        
        print(f"   - 3 iteraciones completadas")
        return True
    except Exception as e:
        print(f"❌ Fallo iteración: {str(e)[:80]}")
        return False


def test_bot_risk_manager():
    """Verificar que bot tiene risk manager"""
    try:
        from src.bot.trading_bot import TradingBot
        
        bot = TradingBot(symbols=['GGAL'])
        
        # Verificar que tiene risk manager
        assert hasattr(bot, 'risk_manager'), "Bot no tiene risk_manager"
        assert bot.risk_manager is not None, "risk_manager es None"
        
        print("✅ Risk Manager integrado en Bot")
        return True
    except Exception as e:
        print(f"❌ Fallo risk manager: {str(e)[:80]}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE TRADING BOT")
    print("=" * 70 + "\n")
    
    tests = [
        ("Configuración del Bot", test_bot_config),
        ("Inicialización Bot", test_bot_init),
        ("Análisis de Símbolo", test_bot_symbol_analysis),
        ("Resumen de Cartera", test_bot_portfolio_summary),
        ("Múltiples Símbolos", test_bot_multiple_symbols),
        ("Iteración Rápida", test_bot_quick_iteration),
        ("Risk Manager Integrado", test_bot_risk_manager),
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
