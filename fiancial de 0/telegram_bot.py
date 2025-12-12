"""
Bot de Telegram para Control Remoto

Comandos disponibles:
- /start - Iniciar sesión
- /status - Estado del bot de trading
- /start_trading - Iniciar trading
- /stop_trading - Detener trading
- /balance - Ver saldo simulado
- /help - Ayuda

Versión: 1.1.0
"""

import logging
import os
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Bot de Telegram para control remoto del trading bot"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Inicializa el bot de Telegram.
        """
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.app = None
        
        if not self.token:
            logger.warning("⚠️ Token de Telegram no configurado (TELEGRAM_TOKEN)")
        
    def run(self):
        """Inicia el polling del bot"""
        if not self.token:
            logger.error("No se puede iniciar el bot de Telegram sin token.")
            return

        self.app = ApplicationBuilder().token(self.token).build()
        
        # Handlers
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('help', self.help))
        self.app.add_handler(CommandHandler('status', self.status))
        self.app.add_handler(CommandHandler('start_trading', self.start_trading))
        self.app.add_handler(CommandHandler('stop_trading', self.stop_trading))
        self.app.add_handler(CommandHandler('balance', self.balance))
        
        logger.info("🚀 Iniciando polling de Telegram...")
        self.app.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 *IOL Quantum AI Bot*\n\n"
            "Bienvenido al panel de control remoto.\n"
            "Usa /help para ver los comandos disponibles.",
            parse_mode='Markdown'
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "📋 *Comandos Disponibles:*\n\n"
            "/status - Ver estado del sistema\n"
            "/start_trading - Iniciar bot de trading\n"
            "/stop_trading - Detener bot de trading\n"
            "/balance - Ver saldo\n"
            "/help - Mostrar este mensaje"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # En una implementación real, esto consultaría el estado del TradingBot
        await update.message.reply_text("✅ Estado: **ONLINE** (Modo Espera)")

    async def start_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚀 Iniciando secuencia de trading...")
        # Aquí se llamaría a TradingBot.run() en un thread o proceso aparte

    async def stop_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🛑 Deteniendo operaciones...")
        # Aquí se llamaría a TradingBot.stop()

    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💰 Saldo (Simulado): **$1,000,000 ARS**", parse_mode='Markdown')


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    bot = TelegramBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot detenido por usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
