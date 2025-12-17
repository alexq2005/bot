"""
Telegram Listener Service
Escucha comandos de Telegram para controlar el bot de trading.
Se ejecuta en paralelo al Dashboard.
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv, find_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Agregar root al path
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
except:
    pass

from src.utils.bot_controller import bot_controller
from src.utils.logger import log

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Cargar variables de entorno explícitamente desde cualquier lugar
load_dotenv(find_dotenv())

# Intentar cargar desde settings global, o fallback a env vars
TOKEN = None
ALLOWED_USER_ID = None

try:
    from src.bot.config import settings
    # Intentar obtener de settings (pydantic busca en env vars también)
    # Buscamos atributos comunes
    if hasattr(settings, 'telegram_token'):
        TOKEN = settings.telegram_token
    elif hasattr(settings, 'telegram_bot_token'):
        TOKEN = settings.telegram_bot_token
        
    if hasattr(settings, 'telegram_chat_id'):
        ALLOWED_USER_ID = str(settings.telegram_chat_id)
except ImportError:
    print("⚠️ No se pudo importar settings global, usando os.getenv directo")

# Fallback manual si settings falló o devolvió None
if not TOKEN:
    TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

if not ALLOWED_USER_ID:
    ALLOWED_USER_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_USER_ID")

async def start_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica permisos"""
    user_id = str(update.effective_user.id)
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text(f"⛔ No autorizado ({user_id}).")
        print(f"⛔ Intento de acceso no autorizado: {user_id}")
        return False
    return True

async def cmd_start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start_bot"""
    if not await start_check(update, context): return
    
    await update.message.reply_text("⏳ Iniciando Bot de Trading...")
    
    # IMPORTANTE: Pasamos env vars extra si es necesario
    result = bot_controller.start()
    if result['success']:
        await update.message.reply_text(f"✅ Bot INICIADO.\nPID: {result.get('pid')}\nModo: {result.get('mode')}")
    else:
        await update.message.reply_text(f"❌ Error al iniciar: {result.get('message')}")

async def cmd_stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stop_bot"""
    if not await start_check(update, context): return
    
    await update.message.reply_text("⏳ Deteniendo Bot...")
    
    result = bot_controller.stop()
    if result['success']:
        await update.message.reply_text("🛑 Bot DETENIDO correctamente.")
    else:
        await update.message.reply_text(f"⚠️ Alerta al detener: {result.get('message')}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    if not await start_check(update, context): return
    
    status = bot_controller.get_status()
    state = "🟢 CORRIENDO" if status['running'] else "🔴 DETENIDO"
    
    msg = f"""
🤖 Estado del Sistema
-------------------
Estado: {state}
PID: {status.get('pid', 'N/A')}
Uptime: {status.get('uptime', 'N/A')}
    """
    await update.message.reply_text(msg)

def run_listener():
    """Ejecuta el listener de Telegram"""
    print(f"🔍 Buscando Token... Encuentro: {'OK' if TOKEN else 'FALTA'}")
    
    if not TOKEN:
        log.error("❌ ERROR CRÍTICO: No se encontró Token de Telegram.")
        log.error("   Asegúrate de tener .env con TELEGRAM_TOKEN o TELEGRAM_BOT_TOKEN")
        return

    application = Application.builder().token(TOKEN).build()
    
    # Comandos
    application.add_handler(CommandHandler("start_bot", cmd_start_bot))
    application.add_handler(CommandHandler("stop_bot", cmd_stop_bot))
    application.add_handler(CommandHandler("status", cmd_status))
    
    # Ayuda simple
    async def help_cmd(update, context):
        await update.message.reply_text("Comandos:\n/start_bot\n/stop_bot\n/status")
    application.add_handler(CommandHandler("help", help_cmd))
    
    print("📡 Telegram Listener Activo. Esperando comandos...")
    application.run_polling()

if __name__ == "__main__":
    run_listener()
