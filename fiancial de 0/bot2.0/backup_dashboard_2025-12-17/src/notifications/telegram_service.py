"""
Telegram Service
Servicio único de Telegram que evita conflictos
"""

from src.bot.config import settings
from src.notifications.telegram_coordinator import telegram_coordinator
from src.notifications.telegram_controller import TelegramBotController


def main():
    """
    Inicia el servicio único de Telegram
    """
    if not settings.telegram_bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN no configurado")
        return
    
    # Inicializar coordinador
    telegram_coordinator.initialize(settings.telegram_bot_token)
    
    # Registrar controlador del bot
    controller = TelegramBotController(settings.telegram_bot_token)
    
    # Registrar handlers
    telegram_coordinator.register_command("status", controller.status_command)
    telegram_coordinator.register_command("startbot", controller.start_bot_command)
    telegram_coordinator.register_command("stopbot", controller.stop_bot_command)
    telegram_coordinator.register_callback(controller.button_callback)
    
    # Iniciar polling (solo una instancia)
    print("🚀 Iniciando servicio único de Telegram...")
    print("📱 Evitando conflictos de polling...")
    
    telegram_coordinator.start_polling()


if __name__ == "__main__":
    main()
