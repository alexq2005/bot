"""
Telegram Bot Controller
Control remoto del bot de trading vía Telegram
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from src.bot.config import settings
from src.utils.bot_controller import bot_controller
from src.utils.config_manager import config_manager
from src.utils.market_manager import MarketManager


class TelegramBotController:
    """
    Controlador del bot vía Telegram
    Permite controlar el bot remotamente desde el celular
    """
    
    def __init__(self, token: str):
        """
        Inicializa el controlador de Telegram
        
        Args:
            token: Token del bot de Telegram
        """
        self.token = token
        self.app = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        keyboard = [
            [
                InlineKeyboardButton("▶️ Iniciar Bot", callback_data="bot_start"),
                InlineKeyboardButton("⏸️ Detener Bot", callback_data="bot_stop")
            ],
            [
                InlineKeyboardButton("📊 Estado", callback_data="bot_status"),
                InlineKeyboardButton("💼 Portfolio", callback_data="show_portfolio")
            ],
            [
                InlineKeyboardButton("📈 Señales", callback_data="show_signals"),
                InlineKeyboardButton("⚙️ Config", callback_data="show_config")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *Professional IOL Trading Bot*\n\n"
            "Control remoto del bot de trading.\n"
            "Selecciona una opción:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja callbacks de botones"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        
        if action == "bot_start":
            result = bot_controller.start()
            if result['success']:
                await query.edit_message_text(
                    f"✅ Bot iniciado correctamente\n"
                    f"PID: {result['pid']}"
                )
            else:
                await query.edit_message_text(
                    f"❌ Error: {result['message']}"
                )
        
        elif action == "bot_stop":
            result = bot_controller.stop()
            if result['success']:
                await query.edit_message_text("✅ Bot detenido correctamente")
            else:
                await query.edit_message_text(f"❌ Error: {result['message']}")
        
        elif action == "bot_status":
            status = bot_controller.get_status()
            
            if status['running']:
                uptime = int(status.get('uptime_seconds', 0) / 60)
                message = (
                    f"✅ *Bot ACTIVO*\n\n"
                    f"PID: {status['pid']}\n"
                    f"Uptime: {uptime} minutos\n"
                )
            else:
                message = "⏹️ *Bot DETENIDO*"
            
            # Agregar estado del mercado
            market_manager = MarketManager()
            market_status = market_manager.get_market_status()
            
            if market_status['is_open']:
                message += f"\n\n📊 Mercado: ABIERTO ✅"
            else:
                message += f"\n\n📊 Mercado: CERRADO ⚠️"
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        elif action == "show_portfolio":
            # Aquí obtendrías el portfolio real
            await query.edit_message_text(
                "💼 *Mi Portfolio*\n\n"
                "Conectando con IOL...\n"
                "(Implementar integración con IOL)"
            )
        
        elif action == "show_signals":
            # Aquí obtendrías las señales actuales
            await query.edit_message_text(
                "📈 *Señales Activas*\n\n"
                "Obteniendo recomendaciones del bot...\n"
                "(Implementar obtención de señales)"
            )
        
        elif action == "show_config":
            # Mostrar configuración actual
            categories = config_manager.get_symbol_categories()
            max_symbols = config_manager.get_max_symbols()
            mode = config_manager.get_mode()
            
            await query.edit_message_text(
                f"⚙️ *Configuración Actual*\n\n"
                f"Categorías: {', '.join(categories)}\n"
                f"Max Símbolos: {max_symbols}\n"
                f"Modo: {mode.upper()}"
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status"""
        status = bot_controller.get_status()
        
        if status['running']:
            uptime = int(status.get('uptime_seconds', 0) / 60)
            message = (
                f"✅ *Bot ACTIVO*\n\n"
                f"PID: {status['pid']}\n"
                f"Uptime: {uptime} minutos"
            )
        else:
            message = "⏹️ *Bot DETENIDO*"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def start_bot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /startbot"""
        result = bot_controller.start()
        
        if result['success']:
            await update.message.reply_text(
                f"✅ Bot iniciado correctamente\nPID: {result['pid']}"
            )
        else:
            await update.message.reply_text(f"❌ Error: {result['message']}")
    
    async def stop_bot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stopbot"""
        result = bot_controller.stop()
        
        if result['success']:
            await update.message.reply_text("✅ Bot detenido correctamente")
        else:
            await update.message.reply_text(f"❌ Error: {result['message']}")
    
    def run(self):
        """Inicia el bot de Telegram"""
        # Crear aplicación
        self.app = Application.builder().token(self.token).build()
        
        # Agregar handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("startbot", self.start_bot_command))
        self.app.add_handler(CommandHandler("stopbot", self.stop_bot_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Iniciar bot
        print("🤖 Telegram Bot Controller iniciado")
        print("📱 Puedes controlar el bot desde Telegram")
        self.app.run_polling()


def main():
    """Función principal"""
    if not settings.telegram_bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN no configurado en .env")
        return
    
    controller = TelegramBotController(settings.telegram_bot_token)
    controller.run()


if __name__ == "__main__":
    main()
