"""
Telegram Coordinator
Sistema centralizado de Telegram que evita conflictos de polling
"""

import os
import asyncio
from typing import Optional, Callable, Dict
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)


class TelegramCoordinator:
    """
    Coordinador central de Telegram
    
    Evita conflictos de polling teniendo una sola instancia
    que escucha y distribuye mensajes a diferentes handlers
    """
    
    _instance: Optional['TelegramCoordinator'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el coordinador"""
        if self._initialized:
            return
        
        self.app: Optional[Application] = None
        self.token: Optional[str] = None
        self.running = False
        self.handlers: Dict[str, Callable] = {}
        self._initialized = True
    
    def initialize(self, token: str):
        """
        Inicializa la aplicación de Telegram
        
        Args:
            token: Token del bot de Telegram
        """
        if self.app is not None:
            return
        
        self.token = token
        self.app = Application.builder().token(token).build()
        
        # Agregar handlers por defecto
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("help", self._handle_help))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    def register_command(self, command: str, handler: Callable):
        """
        Registra un handler para un comando
        
        Args:
            command: Nombre del comando (sin /)
            handler: Función handler
        """
        if self.app is None:
            raise RuntimeError("Coordinator not initialized")
        
        self.handlers[command] = handler
        self.app.add_handler(CommandHandler(command, handler))
    
    def register_callback(self, handler: Callable):
        """
        Registra un handler para callbacks de botones
        
        Args:
            handler: Función handler
        """
        if self.app is None:
            raise RuntimeError("Coordinator not initialized")
        
        self.app.add_handler(CallbackQueryHandler(handler))
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler por defecto para /start"""
        await update.message.reply_text(
            "🤖 *Professional IOL Trading Bot*\n\n"
            "Bot de trading algorítmico.\n"
            "Usa /help para ver comandos disponibles.",
            parse_mode='Markdown'
        )
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler por defecto para /help"""
        commands = "\n".join([f"/{cmd}" for cmd in self.handlers.keys()])
        
        await update.message.reply_text(
            f"📋 *Comandos Disponibles:*\n\n{commands}",
            parse_mode='Markdown'
        )
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler por defecto para mensajes de texto"""
        # Aquí podrías procesar mensajes generales
        pass
    
    def start_polling(self):
        """Inicia el polling de Telegram"""
        if self.app is None:
            raise RuntimeError("Coordinator not initialized")
        
        if self.running:
            print("⚠️ Telegram coordinator already running")
            return
        
        self.running = True
        print("🤖 Telegram Coordinator iniciado")
        print("📱 Escuchando mensajes de Telegram...")
        
        self.app.run_polling()
    
    def stop(self):
        """Detiene el polling"""
        self.running = False
        if self.app:
            self.app.stop()


# Instancia global
telegram_coordinator = TelegramCoordinator()
