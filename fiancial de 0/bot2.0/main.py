"""
Main Entry Point
Punto de entrada principal del bot
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.trading_bot import TradingBot
from src.bot.config import settings
from src.utils.logger import log


def main():
    """Función principal"""
    try:
        # Cargar configuraciones del ConfigManager
        from src.utils.config_manager import config_manager
        
        # Leer configuraciones guardadas
        saved_config = config_manager._load()
        
        # Banner
        print("\n" + "="*70)
        print("🤖 PROFESSIONAL IOL TRADING BOT v2.0 - SOTA (State of the Art)")
        print("="*70)
        print(f"Modo: {'MOCK (Simulación)' if settings.mock_mode else 'PAPER (Precios Reales)' if settings.paper_mode else 'LIVE (Dinero Real)'}")
        print(f"Intervalo: {settings.trading_interval}s")
        print(f"RL Agent: {'✓ Activado' if settings.use_rl_agent else '✗ Desactivado'}")
        print(f"Sentiment: {'✓ Activado' if settings.use_sentiment_analysis else '✗ Desactivado'}")
        print(f"Sistema Híbrido: {'✓ Activado' if settings.enable_hybrid_advanced else '✗ Desactivado'}")
        
        # Mostrar configuraciones del ConfigManager
        if saved_config:
            print("\n📋 Configuraciones del Dashboard:")
            print(f"  • Máximo de símbolos: {saved_config.get('max_symbols', 'N/A')}")
            print(f"  • Riesgo por trade: {saved_config.get('risk_per_trade', 'N/A')}%")
            print(f"  • Stop Loss: {saved_config.get('stop_loss', 'N/A')}%")
            print(f"  • Take Profit: {saved_config.get('take_profit', 'N/A')}%")
            print(f"  • Modo operación: {saved_config.get('operation_mode', 'N/A').title()}")
        
        print("="*70 + "\n")
        
        # Crear bot
        bot = TradingBot()
        
        # Mostrar símbolos después de inicializar el bot
        print(f"📊 Símbolos activos: {', '.join(bot.symbols)}")
        print(f"📈 Total: {len(bot.symbols)} instrumentos\n")
        
        # Iniciar loop de trading
        bot.run_trading_loop()
        
    except KeyboardInterrupt:
        log.info("\n👋 Bot detenido por el usuario")
    except Exception as e:
        log.error(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
