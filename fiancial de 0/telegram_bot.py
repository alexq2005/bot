"""
Bot de Telegram para Control Remoto - VERSIÓN MEJORADA

Comandos disponibles:
- /start - Iniciar sesión
- /help - Lista de comandos
- /status - Estado del bot y sistema
- /portfolio - Ver portafolio completo
- /precio [SYMBOL] - Cotización en tiempo real
- /analisis [SYMBOL] - Análisis técnico completo
- /comprar [SYMBOL] [CANT] - Orden de compra
- /vender [SYMBOL] [CANT] - Orden de venta
- /startbot - Iniciar bot autónomo
- /stopbot - Detener bot autónomo
- /alertas - Configurar alertas de precio

Versión: 2.0.0 - Enhanced Edition
"""

import logging
import os
import asyncio
import threading
import sys
import time
from typing import Optional, Dict, Callable
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from datetime import datetime

# Intentar importar DatabaseService para guardar eventos
try:
    from src.services.data.database import DatabaseService
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("DatabaseService no disponible - eventos de Telegram no se guardarán")

# Importar gestor de estado del bot
from bot_state_manager import bot_state

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_trading_active(func):
    """
    Decorator para comandos que requieren que el bot de trading esté activo.
    Si el bot está inactivo, envía un mensaje de error.
    """
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not bot_state.is_trading_active():
            await update.message.reply_text(
                "⚠️ *Bot de trading inactivo*\n\n"
                "Este comando requiere que el bot de trading esté activo.\n"
                "Usa /start para activar el bot.",
                parse_mode='Markdown'
            )
            return
        return await func(self, update, context)
    return wrapper

class TelegramBot:
    """Bot de Telegram mejorado para control remoto del trading bot"""
    
    # Variable de clase para rastrear si ya hay una instancia corriendo
    _running_instance = None
    _lock = threading.Lock()
    
    def __init__(self, token: Optional[str] = None, controller: Optional[Dict[str, Callable]] = None):
        """
        Inicializa el bot de Telegram.
        :param token: Token del bot de Telegram
        :param controller: Diccionario de funciones callbacks del TradingBot
        """
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.controller = controller or {}
        self.app = None
        self.loop = None
        
        # NO registrar instancia aquí - se hará en run() cuando realmente inicie
        
        # Inicializar base de datos para guardar eventos
        if DB_AVAILABLE:
            try:
                self.db = DatabaseService()
                logger.info("✅ Base de datos conectada para eventos de Telegram")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo conectar a BD: {e}")
                self.db = None
        else:
            self.db = None
        
        if not self.token:
            logger.warning("⚠️ Token de Telegram no configurado (TELEGRAM_TOKEN)")
    
    def _log_telegram_event(self, command: str, user_id: int, username: str = None, data: Dict = None):
        """Registra un evento de Telegram en la base de datos"""
        if self.db:
            try:
                event_data = {
                    "command": command,
                    "user_id": user_id,
                    "username": username,
                    "data": data or {}
                }
                self.db.log_event(
                    event_type=f"telegram_{command}",
                    event_data=event_data,
                    severity="info"
                )
            except Exception as e:
                logger.debug(f"No se pudo registrar evento de Telegram: {e}")
        
    def _stop_existing_instance(self):
        """Detiene cualquier instancia anterior del bot"""
        with TelegramBot._lock:
            if TelegramBot._running_instance is not None and TelegramBot._running_instance != self:
                try:
                    old_instance = TelegramBot._running_instance
                    logger.info("🛑 Deteniendo instancia anterior del bot de Telegram...")
                    
                    # Detener el polling de la instancia anterior
                    if old_instance.app:
                        try:
                            # Intentar detener el polling de forma suave
                            old_instance.app.stop()
                            old_instance.app.shutdown()
                            logger.info("✅ Instancia anterior detenida correctamente")
                        except Exception as e:
                            logger.debug(f"Error deteniendo app anterior: {e}")
                    
                    # Esperar un poco para que se detenga completamente
                    time.sleep(3)
                    
                    # Limpiar la referencia
                    TelegramBot._running_instance = None
                except Exception as e:
                    logger.debug(f"Error deteniendo instancia anterior: {e}")
                    TelegramBot._running_instance = None
    
    def run(self):
        """Inicia el polling del bot"""
        if not self.token:
            logger.error("No se puede iniciar el bot de Telegram sin token.")
            return

        # SINGLETON: Verificar si ya hay una instancia de Telegram corriendo
        if bot_state.is_telegram_running():
            logger.warning("⚠️ Bot de Telegram ya está corriendo. No se iniciará otra instancia.")
            logger.info("💡 Si necesitas reiniciar el bot, primero detén la instancia actual.")
            return
        
        # Detener cualquier instancia anterior primero
        self._stop_existing_instance()

        # Verificar si ya hay una instancia corriendo (después de detener la anterior)
        with TelegramBot._lock:
            if TelegramBot._running_instance is not None and TelegramBot._running_instance != self:
                logger.warning("⚠️ Ya hay una instancia del bot de Telegram corriendo. No se iniciará otra.")
                return
            
            # Marcar esta instancia como la que está corriendo
            TelegramBot._running_instance = self
            logger.info("🔒 Instancia del bot de Telegram bloqueada para evitar conflictos")

        try:
            # Crear nuevo event loop para el thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            logger.info(f"🔧 Creando aplicación de Telegram con token: {self.token[:10]}...")
            self.app = ApplicationBuilder().token(self.token).build()
            
            # Handlers Básicos
            self.app.add_handler(CommandHandler('start', self.start))
            self.app.add_handler(CommandHandler('help', self.help))
            self.app.add_handler(CommandHandler('status', self.status))
            
            # Handlers de Información
            self.app.add_handler(CommandHandler('portfolio', self.cmd_portfolio))
            self.app.add_handler(CommandHandler('precio', self.cmd_price))
            self.app.add_handler(CommandHandler('analisis', self.cmd_analysis))
            
            # Handlers de Trading
            self.app.add_handler(CommandHandler('comprar', self.cmd_buy))
            self.app.add_handler(CommandHandler('vender', self.cmd_sell))
            
            # Handlers de Control del Bot
            self.app.add_handler(CommandHandler('startbot', self.cmd_start_bot))
            self.app.add_handler(CommandHandler('stopbot', self.cmd_stop_bot))
            self.app.add_handler(CommandHandler('pausebot', self.cmd_pause_bot))
            self.app.add_handler(CommandHandler('restart', self.cmd_restart))
            self.app.add_handler(CommandHandler('reset', self.cmd_full_reset))
            
            # Handlers de Configuración y Estado
            self.app.add_handler(CommandHandler('config', self.cmd_config))
            self.app.add_handler(CommandHandler('learning', self.cmd_learning_status))
            
            # Handlers de Nuevas Funcionalidades
            self.app.add_handler(CommandHandler('risk', self.cmd_risk_status))
            self.app.add_handler(CommandHandler('backtest', self.cmd_backtest))
            self.app.add_handler(CommandHandler('alert', self.cmd_create_alert))
            self.app.add_handler(CommandHandler('alerts', self.cmd_list_alerts))
            self.app.add_handler(CommandHandler('delalert', self.cmd_delete_alert))
            self.app.add_handler(CommandHandler('paper', self.cmd_paper_status))
            self.app.add_handler(CommandHandler('logs', self.cmd_search_logs))
            
            # Handlers de Aprendizaje Adaptativo
            self.app.add_handler(CommandHandler('setmode', self.cmd_set_learning_mode))
            self.app.add_handler(CommandHandler('learnstats', self.cmd_learning_stats))
            
            logger.info("🚀 Iniciando polling de Telegram...")
            logger.info("✅ Bot de Telegram listo para recibir mensajes")
            
            # Configurar error handler para conflictos
            async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
                """Maneja errores del bot de Telegram"""
                error = context.error
                if isinstance(error, Exception):
                    if "Conflict" in str(error) or "getUpdates" in str(error):
                        logger.warning(f"⚠️ Conflicto de polling detectado. Deteniendo esta instancia...")
                        # Detener esta instancia si hay conflicto
                        try:
                            with TelegramBot._lock:
                                if TelegramBot._running_instance == self:
                                    TelegramBot._running_instance = None
                            
                            # Estos métodos son corutinas, deben ser esperados
                            await self.app.stop()
                            await self.app.shutdown()
                            
                            logger.info("🛑 Instancia detenida debido a conflicto de polling")
                        except Exception as stop_error:
                            logger.debug(f"Error deteniendo bot por conflicto: {stop_error}")
                    else:
                        logger.error(f"❌ Error en bot de Telegram: {error}")
            
            self.app.add_error_handler(error_handler)
            
            logger.info("🚀 Iniciando polling de Telegram...")
            
            # Marcar como corriendo AHORA que vamos a iniciar el polling
            bot_state.set_telegram_instance(self)
            
            self.app.run_polling()
            
            logger.info("✅ Bot de Telegram listo para recibir mensajes")
            
        except Exception as e:
            # Ignorar errores de conflicto (otra instancia ya corriendo)
            if "Conflict" in str(e) or "getUpdates" in str(e):
                logger.warning(f"⚠️ Conflicto de polling: {e}. Otra instancia del bot ya está corriendo.")
                # Detener el polling si hay conflicto
                try:
                    if self.app:
                        self.app.stop()
                except:
                    pass
            else:
                logger.error(f"❌ Error crítico en bot de Telegram: {e}")
                import traceback
                logger.error(traceback.format_exc())
        finally:
            # Liberar el lock cuando el bot se detiene
            with TelegramBot._lock:
                if TelegramBot._running_instance == self:
                    TelegramBot._running_instance = None
                    bot_state.set_state('telegram_bot_running', False)
                    bot_state.set_telegram_instance(None)
                    logger.info("🔓 Instancia del bot de Telegram liberada")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Bienvenida y activación del bot de Telegram"""
        # Registrar evento
        user = update.effective_user
        self._log_telegram_event("start", user.id, user.username)
        
        # Guardar chat ID del usuario
        bot_state.set_user_chat_id(str(update.effective_chat.id))
        
        welcome_msg = (
            "🤖 *IOL Quantum AI Trading Bot v2.0*\n\n"
            "✅ Bot de Telegram ACTIVO\n\n"
            "📊 *Comandos disponibles:*\n\n"
            "🚀 *Control del Bot de Trading:*\n"
            "• /startbot - Iniciar bot de trading\n"
            "• /stopbot - Detener bot de trading\n"
            "• /restart - Reiniciar bot de trading\n"
            "• /pausebot - Pausar temporalmente\n\n"
            "📈 *Información:*\n"
            "• /status - Estado del sistema\n"
            "• /portfolio - Ver portafolio\n"
            "• /analisis [símbolo] - Análisis técnico\n"
            "• /precio [símbolo] - Cotización actual\n\n"
            "⚡ *Trading Manual:*\n"
            "• /comprar [símbolo] [cant] - Orden de compra\n"
            "• /vender [símbolo] [cant] - Orden de venta\n\n"
            "📊 *Avanzado:*\n"
            "• /risk - Métricas de riesgo\n"
            "• /config - Ver configuración\n"
            "• /help - Ayuda completa\n\n"
            "💡 *Usa /startbot para activar el bot de trading*"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Lista de comandos"""
        help_text = (
            "📋 *COMANDOS DISPONIBLES*\n\n"
            "📊 *INFORMACIÓN*\n"
            "/status - Estado del sistema\n"
            "/portfolio - Ver portafolio completo\n"
            "/precio [SYMBOL] - Cotización actual\n"
            "/analisis [SYMBOL] - Análisis técnico\n"
            "/learning - Estado de aprendizaje IA\n"
            "/risk - Métricas de riesgo\n\n"
            "⚡ *TRADING*\n"
            "/comprar [SYMBOL] [CANT] - Compra manual\n"
            "/vender [SYMBOL] [CANT] - Venta manual\n\n"
            "🤖 *CONTROL DEL BOT*\n"
            "/startbot - Iniciar bot autónomo\n"
            "/stopbot - Detener bot\n"
            "/pausebot - Pausar bot\n"
            "/restart - Reiniciar bot\n"
            "/reset - Reinicio total (⚠️ borra datos)\n\n"
            "⚙️ *CONFIGURACIÓN*\n"
            "/config - Ver configuración actual\n\n"
            "📈 *ANÁLISIS AVANZADO*\n"
            "/backtest [SYMBOL] - Ejecutar backtest\n"
            "/paper - Estado paper trading\n"
            "/logs [FILTRO] - Buscar en logs\n\n"
            "🔔 *ALERTAS*\n"
            "/alert [TIPO] [SYMBOL] [VALOR] - Crear alerta\n"
            "/alerts - Ver alertas activas\n"
            "/delalert [ID] - Eliminar alerta\n\n"
            "💡 *Ejemplo:* `/precio GGAL`\n"
            "💡 *Ejemplo:* `/alert price GGAL 8000`"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Estado del sistema"""
        # Registrar evento
        user = update.effective_user
        self._log_telegram_event("status", user.id, user.username)
        
        try:
            if 'get_status' in self.controller:
                status_data = self.controller["get_status"]()
                
                # Manejar string o dict
                if isinstance(status_data, str):
                    status_msg = status_data
                else:
                    status_msg = "✅ *SISTEMA ONLINE*"
            else:
                status_msg = (
                    "✅ *SISTEMA ONLINE*\n\n"
                    "⚠️ Controlador no conectado\n"
                    "El bot de Telegram está activo pero no tiene acceso\n"
                    "a las funciones del trading bot."
                )
            
            await update.message.reply_text(status_msg, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error obteniendo estado: {str(e)}")

    async def cmd_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /portfolio - Ver portafolio completo"""
        # Registrar evento
        user = update.effective_user
        self._log_telegram_event("portfolio", user.id, user.username)
        
        try:
            if 'get_portfolio' not in self.controller:
                await update.message.reply_text("⚠️ Función no disponible")
                return
            
            await update.message.reply_text("📊 Consultando portafolio...")
            
            loop = asyncio.get_running_loop()
            portfolio = await loop.run_in_executor(None, self.controller['get_portfolio'])
            
            if not portfolio or 'assets' not in portfolio:
                await update.message.reply_text("⚠️ Portafolio vacío")
                return
            
            # Formatear portafolio
            msg = "💼 *TU PORTAFOLIO*\n\n"
            
            total_value = portfolio.get('total_value', 0)
            cash = portfolio.get('available_cash', 0)
            
            msg += f"💰 Efectivo: ${cash:,.2f}\n"
            msg += f"📊 Total invertido: ${total_value:,.2f}\n\n"
            msg += "*POSICIONES:*\n"
            
            for asset in portfolio.get('assets', []):
                symbol = asset.get('symbol', 'N/A')
                qty = asset.get('quantity', 0)
                price = asset.get('last_price', 0)
                value = qty * price
                
                msg += f"\n📈 *{symbol}*\n"
                msg += f"   Cantidad: {qty}\n"
                msg += f"   Precio: ${price:,.2f}\n"
                msg += f"   Valor: ${value:,.2f}\n"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /precio [SYMBOL] - Cotización en tiempo real"""
        # Registrar evento
        user = update.effective_user
        symbol = context.args[0] if context.args else None
        self._log_telegram_event("precio", user.id, user.username, {"symbol": symbol})
        
        if not context.args:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/precio [SYMBOL]`\n"
                "💡 Ejemplo: `/precio GGAL`",
                parse_mode='Markdown'
            )
            return
            
        symbol = context.args[0].upper()
        
        if 'get_market_data' in self.controller:
            await update.message.reply_text(f"🔍 Consultando {symbol}...")
            loop = asyncio.get_running_loop()
            try:
                data = await loop.run_in_executor(None, self.controller['get_market_data'], symbol)
                if data:
                    price = data.get('last_price', 0)
                    change = data.get('pct_change', 0)
                    volume = data.get('volume', 0)
                    
                    emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    
                    msg = (
                        f"📊 *{symbol}*\n\n"
                        f"💰 Precio: ${price:,.2f}\n"
                        f"{emoji} Variación: {change:+.2f}%\n"
                        f"📊 Volumen: {volume:,}\n\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text(f"⚠️ No hay datos disponibles para {symbol}")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Función no disponible")

    async def cmd_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analisis [SYMBOL] - Análisis técnico completo"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/analisis [SYMBOL]`\n"
                "💡 Ejemplo: `/analisis AAPL`",
                parse_mode='Markdown'
            )
            return
        
        symbol = context.args[0].upper()
        
        if 'get_analysis' in self.controller:
            await update.message.reply_text(f"🔬 Analizando {symbol}...")
            loop = asyncio.get_running_loop()
            try:
                analysis = await loop.run_in_executor(None, self.controller['get_analysis'], symbol)
                
                if analysis:
                    signal = analysis.get('signal', 'HOLD')
                    rsi = analysis.get('indicators', {}).get('rsi', 0)
                    macd = analysis.get('indicators', {}).get('macd', {}).get('macd', 0)
                    
                    signal_emoji = "🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "🟡"
                    
                    msg = (
                        f"🔬 *ANÁLISIS TÉCNICO: {symbol}*\n\n"
                        f"{signal_emoji} *Señal: {signal}*\n\n"
                        f"📊 *Indicadores:*\n"
                        f"• RSI: {rsi:.1f}\n"
                        f"• MACD: {macd:.2f}\n\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text(f"⚠️ No se pudo analizar {symbol}")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Función no disponible")

    async def cmd_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /comprar [SYMBOL] [CANT] - Orden de compra"""
        # Registrar evento
        user = update.effective_user
        symbol = context.args[0] if context.args else None
        quantity = context.args[1] if len(context.args) > 1 else None
        self._log_telegram_event("comprar", user.id, user.username, {"symbol": symbol, "quantity": quantity})
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/comprar [SYMBOL] [CANTIDAD]`\n"
                "💡 Ejemplo: `/comprar GGAL 10`",
                parse_mode='Markdown'
            )
            return
            
        symbol = context.args[0].upper()
        try:
            quantity = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Cantidad inválida (debe ser un número entero)")
            return

        if 'manual_order' in self.controller:
            await update.message.reply_text(f"⏳ Procesando compra de {quantity} {symbol}...")
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(None, self.controller['manual_order'], symbol, "buy", quantity)
                await update.message.reply_text(f"✅ {result}", parse_mode='Markdown')
            except Exception as e:
                await update.message.reply_text(f"❌ Error de ejecución: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Función no disponible")

    async def cmd_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /vender [SYMBOL] [CANT] - Orden de venta"""
        # Registrar evento
        user = update.effective_user
        symbol = context.args[0] if context.args else None
        quantity = context.args[1] if len(context.args) > 1 else None
        self._log_telegram_event("vender", user.id, user.username, {"symbol": symbol, "quantity": quantity})
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/vender [SYMBOL] [CANTIDAD]`\n"
                "💡 Ejemplo: `/vender GGAL 10`",
                parse_mode='Markdown'
            )
            return
            
        symbol = context.args[0].upper()
        try:
            quantity = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Cantidad inválida (debe ser un número entero)")
            return

        if 'manual_order' in self.controller:
            await update.message.reply_text(f"⏳ Procesando venta de {quantity} {symbol}...")
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(None, self.controller['manual_order'], symbol, "sell", quantity)
                await update.message.reply_text(f"✅ {result}", parse_mode='Markdown')
            except Exception as e:
                await update.message.reply_text(f"❌ Error de ejecución: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Función no disponible")

    async def cmd_start_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /startbot - Iniciar bot autónomo (igual que el botón del dashboard)"""
        # Registrar evento
        user = update.effective_user
        self._log_telegram_event("startbot", user.id, user.username)
        
        if 'start_bot' in self.controller:
            await update.message.reply_text("🚀 Iniciando bot autónomo en proceso separado...")
            loop = asyncio.get_running_loop()
            try:
                # Llamar al método que inicia el bot en proceso separado
                result = await loop.run_in_executor(None, self.controller['start_bot'])
                
                # El resultado ya es un mensaje formateado
                await update.message.reply_text(result, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error en cmd_start_bot: {e}")
                await update.message.reply_text(
                    f"❌ *Error al iniciar bot*\n\n"
                    f"`{str(e)}`\n\n"
                    f"💡 Verifica que el archivo `monitor_bot_live.py` exista y que Python esté en el PATH.",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text("⚠️ Función no disponible. El bot no está correctamente inicializado.")

    async def cmd_stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stopbot - Detener bot autónomo"""
        if 'stop_bot' in self.controller:
            await update.message.reply_text("🛑 Deteniendo bot autónomo...")
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(None, self.controller['stop_bot'])
                await update.message.reply_text(
                    "🛑 *BOT DETENIDO*\n\n"
                    "El bot autónomo ha sido detenido correctamente.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Función no disponible")

    async def cmd_pause_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /pausebot - Pausar bot autónomo"""
        if 'pause_bot' in self.controller:
            await update.message.reply_text("⏸️ Pausando bot autónomo...")
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(None, self.controller['pause_bot'])
                await update.message.reply_text(
                    "⏸️ *BOT PAUSADO*\n\n"
                    "El bot autónomo está en pausa. Usa /startbot para reanudar.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Función no disponible")

    async def cmd_restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /restart - Reiniciar bot de trading"""
        # Registrar evento
        user = update.effective_user
        self._log_telegram_event("restart", user.id, user.username)
        
        await update.message.reply_text("🔄 Reiniciando bot de trading...")
        
        # Desactivar y reactivar
        bot_state.deactivate_trading()
        
        # Detener bot si hay controller
        if 'stop_bot' in self.controller:
            try:
                self.controller['stop_bot']()
            except Exception as e:
                logger.error(f"Error al detener bot: {e}")
        
        # Esperar un momento
        await asyncio.sleep(2)
        
        # Reactivar
        bot_state.activate_trading()
        
        # Iniciar bot si hay controller
        if 'start_bot' in self.controller:
            try:
                result = self.controller['start_bot']()
                logger.info(f"Bot reiniciado: {result}")
            except Exception as e:
                logger.error(f"Error al reiniciar bot: {e}")
                bot_state.deactivate_trading()
                await update.message.reply_text(
                    f"❌ *Error al reiniciar bot*\n\n"
                    f"`{str(e)}`",
                    parse_mode='Markdown'
                )
                return
        
        await update.message.reply_text(
            "✅ *Bot reiniciado correctamente*\n\n"
            "El bot de trading está activo nuevamente.",
            parse_mode='Markdown'
        )

    async def cmd_full_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /reset - Reinicio total del sistema"""
        # Registrar evento
        user = update.effective_user
        self._log_telegram_event("reset", user.id, user.username, {"confirmed": bool(context.args and context.args[0].upper() == 'CONFIRMAR')})
        
        # Confirmación de seguridad
        if not context.args or context.args[0].upper() != 'CONFIRMAR':
            await update.message.reply_text(
                "⚠️ *ADVERTENCIA: REINICIO TOTAL*\n\n"
                "Este comando eliminará:\n"
                "• Historial de operaciones\n"
                "• Datos de aprendizaje\n"
                "• Configuración personalizada\n"
                "• Todos los datos de la base de datos\n\n"
                "⚠️ *ESTA ACCIÓN NO SE PUEDE DESHACER*\n\n"
                "Para confirmar, usa:\n"
                "`/reset CONFIRMAR`",
                parse_mode='Markdown'
            )
            return
        
        if 'full_reset' in self.controller:
            await update.message.reply_text("🔄 Ejecutando reinicio total...\n⚠️ Esto puede tardar unos segundos.")
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(None, self.controller['full_reset'])
                
                # El resultado ya viene formateado desde full_reset()
                await update.message.reply_text(
                    f"✅ *REINICIO TOTAL COMPLETADO*\n\n"
                    f"{result}\n\n"
                    f"• Base de datos limpiada\n"
                    f"• Modelos IA reiniciados\n"
                    f"• Configuración por defecto restaurada\n\n"
                    f"💡 Usa /startbot para comenzar de nuevo.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error en cmd_full_reset: {e}")
                import traceback
                logger.error(traceback.format_exc())
                await update.message.reply_text(
                    f"❌ *Error al ejecutar reinicio total*\n\n"
                    f"`{str(e)}`",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text("⚠️ Función no disponible. El bot no está correctamente inicializado.")

    async def cmd_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /config - Ver configuración actual"""
        try:
            if 'get_config' in self.controller:
                await update.message.reply_text("⚙️ Consultando configuración...")
                loop = asyncio.get_running_loop()
                config = await loop.run_in_executor(None, self.controller['get_config'])
                
                if config:
                    msg = (
                        "⚙️ *CONFIGURACIÓN ACTUAL*\n\n"
                        f"🤖 *Bot:*\n"
                        f"• Modo: {config.get('mode', 'N/A')}\n"
                        f"• Símbolos: {config.get('symbols_count', 0)}\n"
                        f"• Intervalo: {config.get('interval_minutes', 0)} min\n\n"
                        f"💰 *Trading:*\n"
                        f"• Max posición: {config.get('max_position', 0)*100:.1f}%\n"
                        f"• Stop loss: {config.get('stop_loss', 0)*100:.1f}%\n"
                        f"• Take profit: {config.get('take_profit', 0)*100:.1f}%\n\n"
                        f"🧠 *IA:*\n"
                        f"• Análisis técnico: {'✅' if config.get('ta_enabled') else '❌'}\n"
                        f"• Sentimiento: {'✅' if config.get('sentiment_enabled') else '❌'}\n"
                        f"• LSTM: {'✅' if config.get('lstm_enabled') else '❌'}\n"
                        f"• Alpha Vantage: {'✅' if config.get('av_enabled') else '❌'}"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ No se pudo obtener configuración")
            else:
                await update.message.reply_text("⚠️ Función no disponible")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_learning_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /learning - Estado de aprendizaje IA"""
        try:
            if 'get_learning_status' in self.controller:
                await update.message.reply_text("🧠 Consultando estado de aprendizaje...")
                loop = asyncio.get_running_loop()
                status = await loop.run_in_executor(None, self.controller['get_learning_status'])
                
                if status:
                    msg = (
                        "🧠 *ESTADO DE APRENDIZAJE IA*\n\n"
                        f"📊 *LSTM Predictor:*\n"
                        f"• Estado: {status.get('lstm_status', 'N/A')}\n"
                        f"• Épocas entrenadas: {status.get('epochs', 0)}\n"
                        f"• Precisión: {status.get('accuracy', 0)*100:.1f}%\n"
                        f"• Última actualización: {status.get('last_training', 'N/A')}\n\n"
                        f"📈 *Rendimiento:*\n"
                        f"• Predicciones correctas: {status.get('correct_predictions', 0)}\n"
                        f"• Predicciones totales: {status.get('total_predictions', 0)}\n"
                        f"• Tasa de acierto: {status.get('hit_rate', 0)*100:.1f}%\n\n"
                        f"🔄 *Auto-reentrenamiento:*\n"
                        f"• {'✅ Activo' if status.get('auto_retrain') else '❌ Desactivado'}\n"
                        f"• Próximo entrenamiento: {status.get('next_training', 'N/A')}"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ No hay datos de aprendizaje disponibles")
            else:
                await update.message.reply_text("⚠️ Función no disponible")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    def send_message(self, message: str, chat_id: str = None):
        """Envía mensaje proactivo (Thread-Safe)"""
        if not self.app or not self.loop:
            logger.warning("No se puede enviar mensaje: App o loop no inicializados")
            return
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.warning("No se puede enviar mensaje: chat_id no configurado")
            return
        
        try:
            # Enviar mensaje de forma thread-safe
            asyncio.run_coroutine_threadsafe(
                self.app.bot.send_message(chat_id=target_chat_id, text=message, parse_mode='Markdown'),
                self.loop
            )
        except Exception as e:
            logger.error(f"Error enviando mensaje proactivo: {e}")
    
    # ===== NUEVOS COMANDOS - FUNCIONALIDADES AVANZADAS =====
    
    async def cmd_risk_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /risk - Métricas de riesgo"""
        try:
            if 'get_risk_metrics' in self.controller:
                await update.message.reply_text("📊 Consultando métricas de riesgo...")
                loop = asyncio.get_running_loop()
                metrics = await loop.run_in_executor(None, self.controller['get_risk_metrics'])
                
                if metrics:
                    msg = (
                        f"⚠️ *MÉTRICAS DE RIESGO*\n\n"
                        f"📊 *Operaciones Hoy:*\n"
                        f"• Ejecutadas: {metrics.get('daily_trades', 0)}\n"
                        f"• Restantes: {metrics.get('remaining_trades', 0)}\n\n"
                        f"💰 *P&L Diario:*\n"
                        f"• ${metrics.get('daily_pnl', 0):,.2f}\n"
                        f"• {metrics.get('daily_pnl_pct', 0):.2f}%\n\n"
                        f"🎯 *Exposición:*\n"
                        f"• Total: {metrics.get('total_exposure_pct', 0):.1f}%\n\n"
                        f"🛑 *Circuit Breaker:*\n"
                        f"• {'🔴 ACTIVO' if metrics.get('circuit_breaker_active') else '🟢 Inactivo'}\n\n"
                        f"📈 *Trailing Stops:*\n"
                        f"• Activos: {metrics.get('trailing_stops_active', 0)}"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ No hay datos de riesgo disponibles")
            else:
                await update.message.reply_text("⚠️ Función no disponible")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /backtest [SYMBOL] - Ejecutar backtest"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/backtest [SYMBOL]`\n"
                "💡 Ejemplo: `/backtest GGAL`",
                parse_mode='Markdown'
            )
            return
        
        symbol = context.args[0].upper()
        await update.message.reply_text(f"🔬 Backtest para {symbol} - Función en desarrollo")
    
    async def cmd_create_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alert [TYPE] [SYMBOL] [VALUE] - Crear alerta"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/alert [TYPE] [SYMBOL] [VALUE]`\n"
                "💡 Tipos: price, pattern, volatility\n"
                "💡 Ejemplo: `/alert price GGAL 8000`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("✅ Alerta creada (función en desarrollo)")
    
    async def cmd_list_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alerts - Ver alertas activas"""
        await update.message.reply_text("📭 No tienes alertas activas")
    
    async def cmd_delete_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /delalert [ID] - Eliminar alerta"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/delalert [ID]`\n"
                "💡 Ejemplo: `/delalert 1`",
                parse_mode='Markdown'
            )
            return
        await update.message.reply_text("✅ Función en desarrollo")
    
    async def cmd_paper_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /paper - Estado de paper trading"""
        await update.message.reply_text("⚠️ Paper trading no está activo")
    
    async def cmd_search_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /logs [FILTER] - Buscar en logs"""
        await update.message.reply_text("📝 Función de búsqueda de logs en desarrollo")
    
    # ===== COMANDOS DE APRENDIZAJE ADAPTATIVO =====
    
    async def cmd_set_learning_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /setmode [MODE] - Cambiar modo de aprendizaje"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso incorrecto\n\n"
                "📝 Formato: `/setmode [MODE]`\n\n"
                "Modos disponibles:\n"
                "• `AGGRESSIVE` - Sin restricciones, máximo aprendizaje\n"
                "• `SUPERVISED` - Seguro con límites (recomendado)\n"
                "• `PAPER` - Experimentación sin riesgo\n\n"
                "💡 Ejemplo: `/setmode SUPERVISED`",
                parse_mode='Markdown'
            )
            return
        
        mode = context.args[0].upper()
        
        if mode not in ['AGGRESSIVE', 'SUPERVISED', 'PAPER']:
            await update.message.reply_text(
                f"❌ Modo inválido: {mode}\n\n"
                "Modos válidos: AGGRESSIVE, SUPERVISED, PAPER"
            )
            return
        
        try:
            if 'set_learning_mode' in self.controller:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, self.controller['set_learning_mode'], mode)
                
                if result:
                    emoji = "🔥" if mode == "AGGRESSIVE" else "✅" if mode == "SUPERVISED" else "📝"
                    msg = (
                        f"{emoji} *MODO CAMBIADO: {mode}*\n\n"
                        f"Modo anterior: {result.get('old_mode', 'N/A')}\n"
                        f"Modo nuevo: {result.get('new_mode', mode)}\n\n"
                    )
                    
                    if mode == "AGGRESSIVE":
                        msg += "⚠️ *ADVERTENCIA:* Sin límites de riesgo\n"
                        msg += "Puede perder todo tu capital"
                    elif mode == "SUPERVISED":
                        msg += "✅ Modo seguro con límites activos"
                    else:
                        msg += "📝 Experimentación sin dinero real"
                    
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ No se pudo cambiar el modo")
            else:
                await update.message.reply_text("⚠️ Función no disponible")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_learning_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /learnstats - Estadísticas de aprendizaje"""
        try:
            if 'get_learning_stats' in self.controller:
                await update.message.reply_text("📊 Consultando estadísticas de aprendizaje...")
                loop = asyncio.get_running_loop()
                stats = await loop.run_in_executor(None, self.controller['get_learning_stats'])
                
                if stats:
                    mode_emoji = "🔥" if stats['mode'] == "AGGRESSIVE" else "✅" if stats['mode'] == "SUPERVISED" else "📝"
                    
                    msg = (
                        f"{mode_emoji} *ESTADÍSTICAS DE APRENDIZAJE*\n\n"
                        f"🎯 *Modo Actual:* {stats['mode']}\n\n"
                        f"📊 *Trades:*\n"
                        f"• Total: {stats.get('total_trades', 0)}\n"
                        f"• Ganadores: {stats.get('winning_trades', 0)}\n"
                        f"• Perdedores: {stats.get('losing_trades', 0)}\n"
                        f"• Win Rate: {stats.get('winning_trades', 0) / max(stats.get('total_trades', 1), 1) * 100:.1f}%\n\n"
                        f"💰 *P&L:*\n"
                        f"• Total: ${stats.get('total_pnl', 0):,.2f}\n"
                        f"• Promedio: ${stats.get('avg_pnl', 0):,.2f}\n\n"
                        f"📈 *Aprendizaje:*\n"
                        f"• Tasa: {stats.get('learning_rate', 0):.2f}%\n\n"
                        f"⚙️ *Parámetros Actuales:*\n"
                        f"• Multiplier: {stats.get('current_params', {}).get('position_size_multiplier', 1.0):.2f}x\n"
                        f"• Risk Tolerance: {stats.get('current_params', {}).get('risk_tolerance', 0.02):.2%}"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ No hay estadísticas disponibles")
            else:
                await update.message.reply_text("⚠️ Función no disponible")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("TELEGRAM_TOKEN") 
    if not token:
        logger.error("No token configurado")
    else:
        bot = TelegramBot(token)
        try:
            bot.run()
        except KeyboardInterrupt:
            logger.info("Bot detenido por usuario")
        except Exception as e:
            logger.error(f"Error fatal: {e}")
