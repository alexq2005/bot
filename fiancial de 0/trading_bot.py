"""
IOL Quantum AI Trading Bot - Bot Principal de Trading Autónomo

Este módulo coordina:
- Conexión con IOL (Cliente)
- Análisis Técnico
- Gestión de Riesgo
- Ejecución de Órdenes

Versión: 1.1.0 (Auditada y Funcional)
"""

import json
import logging
import time
import os
import threading
import pandas as pd
from typing import List, Dict, Optional, Callable
from datetime import datetime
from dotenv import load_dotenv

from src.services.trading.iol_client import IOLClient
from src.services.analysis.technical_analysis_service import TechnicalAnalysisService
from src.services.data.database import DatabaseService

from telegram_bot import TelegramBot

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importación opcional de LSTMPredictor (requiere TensorFlow)
try:
    from src.services.learning.lstm_predictor import LSTMPredictor
    LSTM_AVAILABLE = True
except ImportError as e:
    LSTMPredictor = None
    LSTM_AVAILABLE = False
    logger.warning(f"⚠️ TensorFlow no disponible. Funcionalidad LSTM deshabilitada: {e}")

# Silenciar logs de httpx (Telegram API requests)
logging.getLogger("httpx").setLevel(logging.WARNING)


class TradingBot:
    """
    Bot de Trading Autónomo que integra IOL y Análisis Técnico.
    """
    
    def __init__(self, config_path: str = "professional_config.json"):
        """
        Inicializa el bot de trading.
        """
        logger.info("🤖 Inicializando IOL Quantum AI Trading Bot v1.1.0")
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        self.running = False

        # Inicializar clientes y servicios
        # Credenciales desde variables de entorno (Prioridad)
        username = os.getenv("IOL_USERNAME")
        password = os.getenv("IOL_PASSWORD")
        
        # Validar credenciales
        if not username or not password:
            logger.warning("⚠️ IOL_USERNAME o IOL_PASSWORD no están configurados en .env")
            logger.warning("⚠️ El bot funcionará en modo MOCK (simulación)")
        
        self.iol_client = IOLClient(username, password)
        self.ta_service = TechnicalAnalysisService()
        self.db = DatabaseService()  # Servicio de persistencia
        
        # Inicializar Análisis de Sentimiento (NewsAPI + Finnhub)
        try:
            from src.services.analysis.sentiment_service import SentimentService
            self.sentiment_service = SentimentService()
            logger.info("📰 Servicio de Análisis de Sentimiento activado")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar SentimentService: {e}")
            self.sentiment_service = None
        
        # Inicializar Alpha Vantage (Datos de alta calidad para CEDEARs)
        try:
            from src.services.data.alpha_vantage_service import AlphaVantageService
            self.alpha_vantage = AlphaVantageService()
            if self.alpha_vantage.enabled:
                logger.info("📊 Alpha Vantage Service activado para CEDEARs")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar AlphaVantageService: {e}")
            self.alpha_vantage = None
        
        # ===== NUEVOS MÓDULOS - INTEGRACIÓN SEGURA =====
        
        # Risk Management
        try:
            from src.services.risk import RiskManager, PositionSizer, CorrelationAnalyzer
            risk_config = self.config.get('risk_management', {})
            self.risk_manager = RiskManager(risk_config)
            self.position_sizer = PositionSizer(risk_per_trade=0.02)
            self.correlation_analyzer = CorrelationAnalyzer()
            logger.info("✅ Risk Management System activado")
        except Exception as e:
            logger.warning(f"⚠️ Risk Management no disponible: {e}")
            self.risk_manager = None
            self.position_sizer = None
            self.correlation_analyzer = None
        
        # Structured Logging
        try:
            from src.services.logging import StructuredLogger, LogAnalyzer
            self.structured_logger = StructuredLogger('trading_bot')
            self.log_analyzer = LogAnalyzer()
            logger.info("✅ Structured Logging activado")
        except Exception as e:
            logger.warning(f"⚠️ Structured Logging no disponible: {e}")
            self.structured_logger = None
            self.log_analyzer = None
        
        # Performance Analytics
        try:
            from src.services.analytics import PerformanceAnalyzer
            self.performance_analyzer = PerformanceAnalyzer()
            logger.info("✅ Performance Analytics activado")
        except Exception as e:
            logger.warning(f"⚠️ Performance Analytics no disponible: {e}")
            self.performance_analyzer = None
        
        # Alert Manager
        try:
            from src.services.alerts import AlertManager
            self.alert_manager = AlertManager()
            logger.info("✅ Alert Manager activado")
        except Exception as e:
            logger.warning(f"⚠️ Alert Manager no disponible: {e}")
            self.alert_manager = None
        
        # Paper Trading (opcional, controlado por config)
        try:
            from src.services.paper_trading import PaperAccount
            if self.config.get('paper_trading', {}).get('enabled', False):
                initial_capital = self.config.get('paper_trading', {}).get('initial_capital', 10000)
                self.paper_account = PaperAccount(initial_capital=initial_capital)
                logger.info(f"✅ Paper Trading activado con ${initial_capital:,.2f}")
            else:
                self.paper_account = None
        except Exception as e:
            logger.warning(f"⚠️ Paper Trading no disponible: {e}")
            self.paper_account = None
        
        # Backtesting Engine (para uso bajo demanda)
        try:
            from src.services.backtesting import BacktestEngine
            self.backtest_engine = BacktestEngine
            logger.info("✅ Backtest Engine disponible")
        except Exception as e:
            logger.warning(f"⚠️ Backtest Engine no disponible: {e}")
            self.backtest_engine = None
        
        # Adaptive Learning System
        try:
            from src.services.learning.adaptive_learning import AdaptiveLearning
            learning_mode = self.config.get('adaptive_learning', {}).get('default_mode', 'SUPERVISED')
            self.adaptive_learning = AdaptiveLearning(mode=learning_mode, config=self.config)
            logger.info(f"✅ Adaptive Learning activado en modo {learning_mode}")
        except Exception as e:
            logger.warning(f"⚠️ Adaptive Learning no disponible: {e}")
            self.adaptive_learning = None
        
        # Inicializar LSTM Predictor (opcional, requiere TensorFlow)
        if LSTM_AVAILABLE and LSTMPredictor:
            try:
                self.predictor = LSTMPredictor()
                self.lstm_predictor = self.predictor  # Alias para compatibilidad
                logger.info("✅ LSTM Predictor activado")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo inicializar LSTM Predictor: {e}")
                self.predictor = None
                self.lstm_predictor = None
        else:
            self.predictor = None
            self.lstm_predictor = None

        # Inicializar Telegram con Controller
        self.telegram = TelegramBot(controller=self._get_controller())

        # Estado
        self.symbols = []
        self.portfolio = {} # { "GGAL": { "quantity": 100, "price": ... } }
        self.trades_history = []  # Mantener en memoria para compatibilidad
        
        # Capital disponible (saldo para operar)
        # Se inicializa al conectar con IOL o al refrescar portfolio
        self.capital = 0.0
        
        # Cargar historial desde base de datos
        self._load_trades_from_db()
        
        # Cargar universo de símbolos (simulado o config)
        self._load_universe()
        
        # Inicializar capital desde IOL si está autenticado
        if not self.iol_client.mock_mode:
            try:
                if self.iol_client.authenticate():
                    self.capital = self.iol_client.get_available_cash()
                    logger.info(f"💰 Capital disponible inicializado: ${self.capital:,.2f}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener capital inicial: {e}")
        
        logger.info(f"✅ Bot inicializado con {len(self.symbols)} símbolos. Modo: {'MOCK' if self.iol_client.mock_mode else 'LIVE'}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Carga la configuración desde archivo JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return {}
    
    def _load_universe(self):
        """
        Carga el universo de símbolos a monitorear.
        Prioridad: 1) Configuración personalizada, 2) Lista predeterminada
        """
        logger.info("🌍 Cargando universo de símbolos...")
        
        # Intentar cargar símbolos personalizados desde configuración
        custom_symbols = self.config.get("monitoring", {}).get("custom_symbols", None)
        
        if custom_symbols and len(custom_symbols) > 0:
            # Usar símbolos personalizados guardados
            self.symbols = custom_symbols
            logger.info(f"✅ Cargados {len(self.symbols)} símbolos personalizados desde configuración")
        else:
            # Usar lista predeterminada
            self.symbols = [
                # --- Panel Merval ---
                "GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "BMA", "CRES", "EDN", 
                "LOMA", "MIRG", "TECO2", "TGNO4", "TGSU2", "TRAN", "VALO", 
                "SUPV", "BYMA", "CEPU", "COME",
                # --- CEDEARs Top Vol ---
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD",
                "MELI", "VIST", "KO", "MCD", "DIS", "NFLX", "QYLD", "SPY", "DIA"
            ]
            logger.info(f"✅ Cargados {len(self.symbols)} símbolos predeterminados")
    
    def start_bot_in_separate_process(self) -> str:
        """
        Inicia el bot en un proceso separado (igual que el botón del dashboard).
        Retorna un mensaje de estado.
        """
        try:
            import subprocess
            import os
            import sys
            
            # Verificar si ya está corriendo
            if self.running:
                return "⚠️ El bot ya está corriendo. Usa /restart para reiniciarlo."
            
            # Determinar el comando según el sistema operativo
            # Preparar entorno para el subproceso (Plan C: Archivo Bandera)
            # Usar ruta ABSOLUTA para que ambos procesos lo vean
            flag_file = os.path.abspath("no_polling.flag")
            logger.info(f"🏁 Creando archivo flag: {flag_file}")
            
            with open(flag_file, "w") as f:
                f.write("1")
                f.flush()
                os.fsync(f.fileno())  # Forzar escritura inmediata a disco
            
            # Verificar que se creó
            if os.path.exists(flag_file):
                logger.info(f"✅ Archivo flag creado correctamente")
            else:
                logger.warning(f"⚠️ Archivo flag NO se creó")
            
            # Determinar el comando según el sistema operativo
            if os.name == 'nt':  # Windows
                # Usar sys.executable para asegurar el mismo intérprete y CREATE_NEW_CONSOLE para nueva ventana
                cmd = [sys.executable, os.path.abspath('monitor_bot_live.py')]
                process = subprocess.Popen(
                    cmd, 
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=os.getcwd()
                )
            else:  # Linux/Mac
                # Abrir nueva terminal con el bot
                cmd = ['gnome-terminal', '--', sys.executable, 'monitor_bot_live.py']
                process = subprocess.Popen(cmd, cwd=os.getcwd())
            
            # Marcar como ejecutando
            self.running = True
            
            logger.info(f"🚀 Bot iniciado en proceso separado (PID: {process.pid})")
            return (
                f"✅ *BOT AUTÓNOMO INICIADO*\n\n"
                f"📊 Monitoreando {len(self.symbols)} símbolos\n"
                f"💡 El bot está analizando el mercado y ejecutando operaciones automáticamente.\n\n"
                f"🔍 Usa /status para ver el estado actual."
            )
            
        except Exception as e:
            logger.error(f"❌ Error iniciando bot en proceso separado: {e}")
            return f"❌ Error al iniciar bot: {str(e)}"
    
    def _get_controller(self) -> Dict[str, Callable]:
        """Crea el controlador para el bot de Telegram"""
        return {
            "get_status": self.get_account_status_summary,
            "get_market_data": self.get_market_data_safe,
            "manual_order": self.execute_manual_order,
            "get_portfolio": self.get_portfolio_for_telegram,
            "get_analysis": self.get_analysis_for_telegram,
            "start_bot": self.start_bot_in_separate_process,  # Cambiado para usar proceso separado
            "stop_bot": self.stop,
            "pause_bot": self.pause,
            "restart_bot": self.restart_bot,
            "full_reset": self.full_reset,
            "get_config": self.get_config_for_telegram,
            "get_learning_status": self.get_learning_status,
            "get_risk_metrics": self.get_risk_metrics,
            "set_learning_mode": self.set_learning_mode,
            "get_learning_stats": self.get_learning_stats
        }
    
    def set_learning_mode(self, mode: str) -> Dict:
        """Cambia el modo de aprendizaje adaptativo"""
        if self.adaptive_learning:
            return self.adaptive_learning.switch_mode(mode)
        return {}
    
    def get_learning_stats(self) -> Dict:
        """Obtiene estadísticas de aprendizaje"""
        if self.adaptive_learning:
            return self.adaptive_learning.get_learning_stats()
        return {}

    def get_account_status_summary(self) -> str:
        """Resumen de estado para Telegram"""
        pl_total = 0 # Implementar cálculo real si es necesario
        return (
            f"🛠 **Modo**: {'MOCK' if self.iol_client.mock_mode else 'LIVE'}\n"
            f"💰 **Activos**: {len(self.portfolio)}\n"
            f"📜 **Operaciones**: {len(self.trades_history)}"
        )

    def get_market_data_safe(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Wrapper mejorado para market data con fallback automático a datos históricos.
        
        Funcionalidad:
        1. Intenta obtener cotización en tiempo real
        2. Prueba múltiples variaciones del símbolo (.BA, mayúsculas, etc.)
        3. Si falla, obtiene automáticamente último precio de cierre
        4. Permite al bot operar 24/7, incluso cuando el mercado está cerrado
        
        Args:
            symbol: Símbolo del activo
            market: Mercado (bCBA por defecto para Argentina)
        
        Returns:
            Dict con datos de mercado o None si no se encuentra
        """
        try:
            # Determinar si es un bono para ajustar variaciones de símbolo
            symbol_upper = symbol.upper()
            is_bono = (
                symbol_upper.startswith("AL") or
                symbol_upper.startswith("GD") or
                symbol_upper.startswith("AE") or
                symbol_upper.startswith("CUAP") or
                symbol_upper.startswith("DICA") or
                symbol_upper.startswith("PARP") or
                symbol_upper.startswith("TO") or
                symbol_upper.startswith("TJ")
            )
            
            # Crear lista de variaciones del símbolo a intentar
            symbol_variations = [symbol]  # Siempre intentar primero el símbolo tal cual
            
            if not is_bono:
                # Para acciones y CEDEARs, intentar con .BA
                symbol_variations.extend([
                    f"{symbol}.BA",
                    symbol.upper(),
                    f"{symbol.upper()}.BA"
                ])
                # También intentar sin el sufijo si ya lo tiene
                if symbol.endswith(".BA"):
                    symbol_variations.insert(1, symbol.replace(".BA", ""))
            else:
                # Para bonos, solo intentar mayúsculas si es diferente
                if symbol != symbol.upper():
                    symbol_variations.append(symbol.upper())
            
            logger.debug(f"🔍 Intentando obtener datos para {symbol} con {len(symbol_variations)} variaciones")
            
            # Intentar obtener datos en tiempo real con cada variación
            market_data = None
            for symbol_variant in symbol_variations:
                try:
                    data = self.iol_client.get_market_data(symbol_variant, market=market)
                    
                    if data:
                        price = data.get('last_price') or data.get('ultimoPrecio') or 0
                        if price and price > 0:
                            market_data = data
                            logger.info(f"✅ Datos en tiempo real obtenidos para {symbol} usando '{symbol_variant}': ${price}")
                            return market_data
                except Exception as e:
                    logger.debug(f"Variación '{symbol_variant}' falló: {e}")
                    continue
            
            # Si no se obtuvieron datos en tiempo real, intentar con datos históricos
            logger.info(f"🔄 No hay cotización en tiempo real para {symbol}, intentando último cierre...")
            
            for symbol_variant in symbol_variations:
                try:
                    historical_data = self.iol_client.get_last_close_price(symbol_variant, market=market)
                    
                    if historical_data and historical_data.get('last_price', 0) > 0:
                        logger.info(f"✅ Último cierre obtenido para {symbol} usando '{symbol_variant}': ${historical_data['last_price']} (fecha: {historical_data.get('close_date', 'N/A')})")
                        # Marcar como datos históricos
                        historical_data['is_historical'] = True
                        historical_data['data_source'] = 'Último Cierre'
                        return historical_data
                except Exception as e:
                    logger.debug(f"Error obteniendo último cierre para '{symbol_variant}': {e}")
                    continue
            
            # Si todo falla, retornar None
            logger.warning(f"⚠️ No se pudieron obtener datos (ni tiempo real ni históricos) para {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en get_market_data_safe para {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def execute_manual_order(self, symbol: str, side: str, quantity: int) -> str:
        """Ejecuta orden manual desde Telegram"""
        try:
            # Validar precio actual
            data = self.iol_client.get_market_data(symbol)
            if not data: return "❌ Error: No se pudo obtener cotización"
            price = data['last_price']
            
            if side.lower() == "buy":
                self._execute_buy(symbol, price, "MANUAL_TELEGRAM", quantity)
                return f"✅ Orden de COMPRA enviada: {quantity} {symbol} @ ${price}"
            elif side.lower() == "sell":
                self._execute_sell(symbol, price, "MANUAL_TELEGRAM", quantity)
                return f"✅ Orden de VENTA enviada: {quantity} {symbol} @ ${price}"
            else:
                return "❌ Lado inválido (buy/sell)"
        except Exception as e:
            return f"❌ Error ejecutando orden: {str(e)}"

    def run(self, enable_polling: bool = True):
        """
        Ejecuta el ciclo principal del bot
        
        Args:
            enable_polling: Si es True, inicia el hilo de polling de Telegram.
                           Si es False, solo permite envío de mensajes (sin recibir comandos).
        """
        logger.info("🚀 Iniciando bucle de trading...")
        self.running = True
        
        # Iniciar Telegram en hilo separado SOLO si se solicita y no está ya corriendo
        if enable_polling and self.telegram and self.telegram.token:
            # Verificar si ya hay un thread corriendo
            if not hasattr(self, 'telegram_thread') or not self.telegram_thread or not self.telegram_thread.is_alive():
                try:
                    self.telegram_thread = threading.Thread(target=self.telegram.run, daemon=True, name="TelegramBot-TradingBot")
                    self.telegram_thread.start()
                    logger.info("📡 Bot de Telegram iniciado en segundo plano desde trading_bot.run()")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo iniciar bot de Telegram desde trading_bot: {e}")
            else:
                logger.info("📡 Bot de Telegram ya está corriendo (probablemente iniciado desde dashboard)")
        elif not enable_polling:
            logger.info("🔕 Telegram Polling deshabilitado para esta instancia (modo worker)")

        # Autenticación inicial
        if not self.iol_client.authenticate():
            logger.error("❌ Fallo crítico en autenticación. Deteniendo.")
            self.running = False
            return

        # Cargar portfolio inicial
        self._refresh_portfolio()

        while self.running:
            try:
                logger.info(f"--- Ciclo de análisis {datetime.now().strftime('%H:%M:%S')} ---")

                for symbol in self.symbols:
                    if not self.running: break

                    self._process_symbol(symbol)

                    # Evitar Rate Limiting
                    time.sleep(1)

                # Esperar antes del siguiente ciclo completo (según config)
                interval = self.config.get("monitoring", {}).get("update_interval_minutes", 15) * 60
                # En modo demo/test, reducimos el intervalo
                if self.iol_client.mock_mode:
                    interval = 10

                logger.info(f"💤 Esperando {interval}s para el siguiente ciclo...")
                time.sleep(interval)

            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                logger.error(f"Error en bucle principal: {e}")
                time.sleep(10) # Espera de error

    def _refresh_portfolio(self):
        """Actualiza el estado del portafolio localmente y guarda snapshot en BD"""
        try:
            portfolio_data = self.iol_client.get_portfolio()
            if portfolio_data and "assets" in portfolio_data:
                self.portfolio = {
                    item["symbol"]: item for item in portfolio_data["assets"]
                }
            
            # Actualizar capital disponible desde IOL
            try:
                self.capital = self.iol_client.get_available_cash()
                logger.info(f"💰 Capital disponible actualizado: ${self.capital:,.2f}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar capital: {e}")
            
            logger.info("💼 Portafolio actualizado")
            
            # Guardar snapshot en base de datos
            self.save_portfolio_snapshot()
        except Exception as e:
            logger.error(f"Error actualizando portafolio: {e}")

    def _process_symbol(self, symbol: str):
        """Procesa un símbolo individual: Datos -> Análisis -> Señal -> Orden"""
        try:
            # 1. Obtener Datos Históricos
            # Usar Alpha Vantage para CEDEARs, IOL para acciones argentinas
            historical_data = None
            
            if self.alpha_vantage and self.alpha_vantage.enabled and self.alpha_vantage.is_cedear(symbol):
                # CEDEAR: Usar Alpha Vantage (mejor calidad)
                logger.info(f"📊 Obteniendo datos de {symbol} desde Alpha Vantage...")
                df = self.alpha_vantage.get_historical_data(symbol, interval="daily")
                if df is not None and len(df) > 30:
                    historical_data = df.to_dict('records')
            
            if not historical_data:
                # Fallback a IOL o para acciones argentinas
                logger.info(f"📈 Obteniendo datos de {symbol} desde IOL...")
                historical_data = self.iol_client.get_historical_data(symbol, "2023-01-01", "2024-01-01")

            if not historical_data:
                logger.warning(f"⚠️ No se pudieron obtener datos para {symbol}")
                return

            df = pd.DataFrame(historical_data)

            # 2. Análisis Técnico
            analysis = self.ta_service.analyze(symbol, df)
            signal = analysis.get("signal")

            # 3. Predicción IA (LSTM)
            ai_prediction = None
            if LSTM_AVAILABLE and self.lstm_predictor and self.predictor:
                try:
                    # Entrenar incrementalmente (simulado para demo)
                    # self.predictor.train(df, epochs=1) 
                    ai_prediction = self.predictor.predict(df)
                    if ai_prediction:
                        logger.info(f"🧠 LSTM Predicción para {symbol}: ${ai_prediction:.2f}")
                except Exception as e:
                    logger.warning(f"Error en predicción IA: {e}")
            
            # 3.5. Análisis de Sentimiento (NewsAPI + Finnhub)
            sentiment_score = 0  # Neutral por defecto
            if self.sentiment_service:
                try:
                    # El método correcto es get_market_sentiment() que retorna un float (-1 a +1)
                    sentiment_score = self.sentiment_service.get_market_sentiment(symbol)
                    
                    # Determinar label basado en el score
                    if sentiment_score > 0.3:
                        sentiment_label = "POSITIVO"
                    elif sentiment_score < -0.3:
                        sentiment_label = "NEGATIVO"
                    else:
                        sentiment_label = "NEUTRAL"
                    
                    if sentiment_score != 0:
                        logger.info(f"📰 Sentimiento para {symbol}: {sentiment_label} ({sentiment_score:.2f})")
                except Exception as e:
                    logger.warning(f"Error en análisis de sentimiento: {e}")

            # 3. Obtener Precio Actual
            market_data = self.iol_client.get_market_data(symbol)
            if not market_data:
                logger.warning(f"⚠️ No se pudieron obtener datos para {symbol}")
                return

            # Normalizar precio desde diferentes campos de IOL
            current_price = (
                market_data.get("last_price") or 
                market_data.get("ultimoPrecio") or 
                market_data.get("precio") or 
                market_data.get("close") or 
                0
            )
            
            # Validar que el precio sea válido
            if not current_price or current_price <= 0:
                logger.warning(f"⚠️ Precio inválido para {symbol}: {current_price}")
                return

            # 4. Lógica de Ejecución (TA + IA + Sentimiento)
            # Combinar señales: Análisis Técnico + IA + Sentimiento
            
            # IA Confirmation
            if ai_prediction and current_price:
                if ai_prediction > current_price * 1.01 and "BUY" in signal:
                    signal = "STRONG_BUY_AI_CONFIRMED"
                    logger.info(f"🚀 SEÑAL IA CONFIRMADA: {symbol} (Target: {ai_prediction:.2f})")
            
            # Sentiment Confirmation/Rejection
            if sentiment_score > 0.3 and "BUY" in signal:
                # Sentimiento positivo confirma compra
                signal = "STRONG_BUY_SENTIMENT_CONFIRMED"
                logger.info(f"📈 Sentimiento POSITIVO confirma COMPRA para {symbol}")
            elif sentiment_score < -0.3 and "SELL" in signal:
                # Sentimiento negativo confirma venta
                signal = "STRONG_SELL_SENTIMENT_CONFIRMED"
                logger.info(f"📉 Sentimiento NEGATIVO confirma VENTA para {symbol}")
            elif abs(sentiment_score) > 0.3:
                # Sentimiento contradice señal técnica -> HOLD
                if (sentiment_score > 0 and "SELL" in signal) or (sentiment_score < 0 and "BUY" in signal):
                    logger.warning(f"⚠️ Sentimiento contradice señal técnica para {symbol}. HOLD.")
                    signal = "HOLD"
            
            if signal in ["BUY", "STRONG_BUY", "STRONG_BUY_AI_CONFIRMED", "STRONG_BUY_SENTIMENT_CONFIRMED"]:
                self._execute_buy(symbol, current_price, signal)
            elif signal in ["SELL", "STRONG_SELL", "STRONG_SELL_SENTIMENT_CONFIRMED"]:
                self._execute_sell(symbol, current_price, signal)
            else:
                pass # HOLD

        except Exception as e:
            logger.error(f"Error procesando {symbol}: {e}")

    def _execute_buy(self, symbol: str, price: float, signal: str, quantity: int = 10):
        """Ejecuta compra con validación de riesgo y logging estructurado"""
        # Validar que el precio sea válido
        if not price or price <= 0:
            logger.error(f"❌ No se puede ejecutar compra de {symbol}: Precio inválido ({price})")
            return
        
        logger.info(f"🔵 Señal de COMPRA para {symbol} ({signal}) a ${price}")
        
        # === VALIDACIÓN DE RIESGO ===
        if self.risk_manager:
            try:
                # Usar capital disponible para validación de riesgo
                available_capital = self._get_available_capital()
                portfolio_value = self._get_portfolio_value()  # Para contexto total
                current_positions = self.portfolio
                
                validation = self.risk_manager.validate_trade(
                    symbol=symbol,
                    action='buy',
                    quantity=quantity,
                    price=price,
                    portfolio_value=available_capital,  # Usar capital disponible, no total
                    current_positions=current_positions
                )
                
                if not validation['approved']:
                    logger.warning(f"⚠️ Compra rechazada por Risk Manager: {validation['reason']}")
                    if self.structured_logger:
                        self.structured_logger.warning(
                            f"Trade rejected: {validation['reason']}",
                            symbol=symbol,
                            action='buy',
                            price=price,
                            reason=validation['reason']
                        )
                    return
            except Exception as e:
                logger.warning(f"⚠️ Error en validación de riesgo: {e}")
        
        # === POSITION SIZING DINÁMICO ===
        if self.position_sizer:
            try:
                # Obtener datos históricos para calcular ATR
                historical_data = self.iol_client.get_historical_data(symbol, "2023-01-01", "2024-01-01")
                if historical_data:
                    df = pd.DataFrame(historical_data)
                    # Usar capital disponible para calcular tamaño de posición
                    available_capital = self._get_available_capital()
                    
                    size_calc = self.position_sizer.calculate_position_size(
                        symbol=symbol,
                        current_price=price,
                        portfolio_value=available_capital,  # Usar capital disponible
                        historical_data=df,
                        method='atr'
                    )
                    
                    # Usar cantidad calculada si es válida
                    if size_calc['quantity'] > 0:
                        quantity = size_calc['quantity']
                        logger.info(f"📊 Position sizing: {quantity} unidades (método: {size_calc['method']})")
            except Exception as e:
                logger.warning(f"⚠️ Error en position sizing: {e}")
        
        # === EJECUTAR ORDEN ===
        order = self.iol_client.place_order(symbol, "comprar", quantity, price)
        if order:
            self._record_trade("BUY", symbol, quantity, price, signal)
            
            # Structured Logging
            if self.structured_logger:
                self.structured_logger.trade(
                    action='BUY',
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    signal=signal,
                    order_id=order.get('numero', 'N/A')
                )
            
            # Registrar en Performance Analyzer
            if self.performance_analyzer:
                self.performance_analyzer.add_trade({
                    'timestamp': datetime.now(),
                    'action': 'BUY',
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': price,
                    'pnl': 0  # Se calculará al vender
                })
            
            # Registrar trade en Risk Manager
            if self.risk_manager:
                self.risk_manager.record_trade()
            
            logger.info(f"✅ Compra ejecutada: {quantity} {symbol} a ${price}")
        else:
            logger.error(f"❌ Error ejecutando compra de {symbol}")

        # Verificar tenencia en portafolio
        if self.iol_client.mock_mode:
            # En mock mode, simulamos tenerlo si lo hemos "comprado" o si está en el portfolio mock inicial
            asset = self.portfolio.get(symbol)
            current_qty = asset.get("quantity", 0) if asset else 0
            if current_qty < quantity:
                logger.warning(f"⚠️ No se puede vender {symbol}: Tenencia insuficiente ({current_qty})")
                return

    def _execute_sell(self, symbol: str, price: float, signal: str, quantity: int = 10):
        """Ejecuta venta si se tiene el activo"""
        # Validar que el precio sea válido
        if not price or price <= 0:
            logger.error(f"❌ No se puede ejecutar venta de {symbol}: Precio inválido ({price})")
            return
        
        logger.info(f"🔴 Señal de VENTA para {symbol} ({signal}) a ${price} | Qty: {quantity}")

        # Verificar tenencia en portafolio (TANTO EN MOCK COMO EN REAL)
        # Refrescar portfolio primero para tener datos actualizados
        self._refresh_portfolio()
        
        # Buscar el activo en el portfolio
        asset = self.portfolio.get(symbol)
        current_qty = asset.get("quantity", 0) if asset else 0
        
        # Si no está en self.portfolio, intentar obtenerlo del portfolio de IOL directamente
        if current_qty == 0 and not self.iol_client.mock_mode:
            try:
                portfolio_data = self.iol_client.get_portfolio()
                if portfolio_data and "assets" in portfolio_data:
                    for item in portfolio_data["assets"]:
                        if item.get("symbol") == symbol or item.get("symbol") == f"{symbol}.BA":
                            current_qty = item.get("quantity", 0)
                            logger.info(f"📊 Tenencia encontrada en IOL: {symbol} = {current_qty}")
                            break
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo tenencia de IOL: {e}")
        
        # Validar tenencia suficiente
        if current_qty < quantity:
            logger.warning(f"⚠️ No se puede vender {symbol}: Tenencia insuficiente ({current_qty} < {quantity})")
            return
        
        # Ejecutar orden de venta
        order = self.iol_client.place_order(symbol, "vender", quantity, price)
        if order:
            # Verificar que la orden fue ejecutada exitosamente
            order_status = order.get("status", "").lower() if isinstance(order, dict) else ""
            order_executed = order.get("executed", False) if isinstance(order, dict) else False
            
            # Solo registrar si la orden fue ejecutada o está pendiente de ejecución
            if order_executed or "pending" in order_status or "executed" in order_status:
                self._record_trade("SELL", symbol, quantity, price, signal)
                self._refresh_portfolio()
                logger.info(f"✅ Venta ejecutada: {quantity} {symbol} a ${price}")
            else:
                logger.warning(f"⚠️ Orden de venta enviada pero no ejecutada: {order}")
        else:
            logger.error(f"❌ Error ejecutando venta de {symbol}: Orden rechazada por IOL")

    def _record_trade(self, side, symbol, quantity, price, signal):
        """Registra el trade en el historial y en la base de datos"""
        timestamp = datetime.now()
        total = quantity * price
        commission = total * self.config.get('trading', {}).get('commission_rate', 0.006)
        
        trade = {
            "timestamp": timestamp.isoformat(),
            "side": side,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "signal": signal
        }
        
        # Guardar en memoria (para compatibilidad)
        self.trades_history.append(trade)
        
        # Guardar en base de datos
        try:
            db_trade = {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "total": total,
                "commission": commission,
                "timestamp": timestamp,
                "signal": signal,
                "status": "executed"
            }
            trade_id = self.db.save_trade(db_trade)
            logger.info(f"✅ Trade registrado (ID: {trade_id}): {symbol} {side} {quantity} @ ${price}")
            
            # Registrar evento
            self.db.log_event("trade_executed", {
                "trade_id": trade_id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price
            }, "info")
        except Exception as e:
            logger.error(f"❌ Error guardando trade en BD: {e}")
    
    def _load_trades_from_db(self):
        """Carga los últimos trades desde la base de datos"""
        try:
            recent_trades = self.db.get_trades(limit=100)
            # Convertir formato de BD a formato en memoria
            for trade in recent_trades:
                self.trades_history.append({
                    "timestamp": trade['timestamp'],
                    "side": trade['side'],
                    "symbol": trade['symbol'],
                    "quantity": trade['quantity'],
                    "price": trade['price'],
                    "signal": trade.get('signal')
                })
            logger.info(f"📥 Cargados {len(recent_trades)} trades desde la base de datos")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron cargar trades desde BD: {e}")
    
    def save_portfolio_snapshot(self):
        """Guarda un snapshot del portafolio actual en la base de datos"""
        try:
            portfolio_data = {}
            for symbol, data in self.portfolio.items():
                current_price = data.get('current_price', data.get('price', 0))
                quantity = data.get('quantity', 0)
                avg_price = data.get('avg_price', current_price)
                total_value = quantity * current_price
                pnl = (current_price - avg_price) * quantity if avg_price > 0 else 0
                pnl_percentage = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
                
                portfolio_data[symbol] = {
                    "quantity": quantity,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "total_value": total_value,
                    "pnl": pnl,
                    "pnl_percentage": pnl_percentage
                }
            
            self.db.save_portfolio_snapshot(portfolio_data)
            logger.debug(f"💾 Snapshot de portafolio guardado: {len(portfolio_data)} activos")
        except Exception as e:
            logger.error(f"❌ Error guardando snapshot de portafolio: {e}")

    def stop(self):
        """Detiene el bot de forma segura"""
        logger.info("🛑 Deteniendo bot...")
        self.running = False
        
        # Guardar snapshot final del portafolio
        try:
            self.save_portfolio_snapshot()
            self._save_daily_metrics()
            logger.info("💾 Datos finales guardados en base de datos")
        except Exception as e:
            logger.error(f"Error guardando datos finales: {e}")
    
    def _save_daily_metrics(self):
        """Calcula y guarda métricas diarias"""
        try:
            today = datetime.now()
            stats = self.db.get_trade_stats()
            
            # Calcular métricas básicas
            total_trades = stats.get('total_trades', 0) or 0
            buy_trades = stats.get('buy_trades', 0) or 0
            sell_trades = stats.get('sell_trades', 0) or 0
            total_volume = stats.get('total_volume', 0) or 0
            
            # Obtener trades del día
            start_of_day = datetime(today.year, today.month, today.day)
            today_trades = self.db.get_trades(start_date=start_of_day, end_date=today)
            
            # Calcular PnL del día (simplificado)
            daily_pnl = 0  # Se puede calcular más complejo con precios de entrada/salida
            
            metrics = {
                "total_trades": len(today_trades),
                "winning_trades": 0,  # Se puede calcular con más detalle
                "losing_trades": 0,
                "total_pnl": daily_pnl,
                "total_volume": total_volume
            }
            
            self.db.save_daily_metrics(today, metrics)
            logger.debug(f"📊 Métricas diarias guardadas: {metrics}")
        except Exception as e:
            logger.error(f"Error guardando métricas diarias: {e}")
    
    def get_trade_statistics(self) -> Dict:
        """
        Obtiene estadísticas de trades desde la base de datos.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            stats = self.db.get_trade_stats()
            recent_trades = self.db.get_trades(limit=10)
            
            return {
                "total_trades": stats.get('total_trades', 0) or 0,
                "buy_trades": stats.get('buy_trades', 0) or 0,
                "sell_trades": stats.get('sell_trades', 0) or 0,
                "total_volume": stats.get('total_volume', 0) or 0,
                "avg_price": stats.get('avg_price', 0) or 0,
                "recent_trades": recent_trades
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _get_portfolio_value(self) -> float:
        """
        Calcula el valor total del portafolio (activos + efectivo disponible).
        Para cálculos de riesgo y posición, usa el capital disponible.
        """
        try:
            portfolio_data = self.iol_client.get_portfolio()
            if portfolio_data and 'total_value' in portfolio_data:
                return float(portfolio_data['total_value'])
            
            # Fallback: calcular manualmente
            total = portfolio_data.get('available_cash', 0) if portfolio_data else 0
            if portfolio_data and 'assets' in portfolio_data:
                for asset in portfolio_data['assets']:
                    qty = asset.get('quantity', 0)
                    price = asset.get('last_price', 0)
                    total += qty * price
            
            return total
        except:
            return 100000  # Default fallback
    
    def _get_available_capital(self) -> float:
        """
        Obtiene el capital disponible para operar (solo efectivo).
        Este es el valor que debe usarse para calcular tamaños de posición.
        """
        # Si ya tenemos el capital actualizado, usarlo
        if self.capital > 0:
            return self.capital
        
        # Si no, intentar obtenerlo desde IOL
        try:
            self.capital = self.iol_client.get_available_cash()
            return self.capital
        except Exception as e:
            logger.warning(f"⚠️ No se pudo obtener capital disponible: {e}")
            # Fallback: usar portfolio value si no hay capital disponible
            return self._get_portfolio_value()
    
    def get_risk_metrics(self) -> Dict:
        """Obtiene métricas de riesgo para Telegram"""
        if self.risk_manager:
            try:
                portfolio_value = self._get_portfolio_value()
                return self.risk_manager.get_risk_metrics(portfolio_value, self.portfolio)
            except Exception as e:
                logger.error(f"Error obteniendo métricas de riesgo: {e}")
                return {}
        return {}

    # ===== FUNCIONES PARA TELEGRAM BOT =====
    
    def get_portfolio_for_telegram(self) -> Dict:
        """Obtiene portafolio formateado para Telegram"""
        try:
            portfolio_data = self.iol_client.get_portfolio()
            return portfolio_data if portfolio_data else {}
        except Exception as e:
            logger.error(f"Error obteniendo portafolio para Telegram: {e}")
            return {}
    
    def get_analysis_for_telegram(self, symbol: str) -> Dict:
        """Obtiene análisis técnico formateado para Telegram"""
        try:
            # Obtener datos históricos
            historical_data = self.iol_client.get_historical_data(symbol, "2023-01-01", "2024-01-01")
            if not historical_data:
                return {}
            
            df = pd.DataFrame(historical_data)
            analysis = self.ta_service.analyze(symbol, df)
            return analysis if analysis else {}
        except Exception as e:
            logger.error(f"Error obteniendo análisis para Telegram: {e}")
            return {}
    
    def pause(self):
        """Pausa el bot autónomo"""
        try:
            self.running = False
            logger.info("⏸️ Bot pausado")
            return "Bot pausado correctamente"
        except Exception as e:
            logger.error(f"Error pausando bot: {e}")
            return f"Error: {str(e)}"
    
    def restart_bot(self):
        """Reinicia el bot autónomo (detiene proceso actual y reinicia en proceso separado)"""
        try:
            logger.info("🔄 Reiniciando bot...")
            
            # Detener si está corriendo
            was_running = self.running
            if self.running:
                self.stop()
                time.sleep(2)
            
            # Recargar configuración
            self.config = self._load_config("professional_config.json")
            
            # Recargar universo de símbolos
            self._load_universe()
            
            # Reconectar IOL
            if not self.iol_client.authenticate():
                logger.error("Error reconectando con IOL")
                return "❌ Error: No se pudo reconectar con IOL"
            
            # Refrescar portafolio
            self._refresh_portfolio()
            
            # Si estaba corriendo, reiniciarlo en proceso separado
            if was_running:
                logger.info("🔄 Reiniciando bot en proceso separado...")
                restart_result = self.start_bot_in_separate_process()
                if "✅" in restart_result:
                    return (
                        "✅ *BOT REINICIADO*\n\n"
                        "• Configuración recargada\n"
                        "• Conexiones restablecidas\n"
                        "• Bot reiniciado en proceso separado\n"
                        "• Análisis reiniciado"
                    )
                else:
                    return (
                        "⚠️ *BOT REINICIADO PARCIALMENTE*\n\n"
                        "• Configuración recargada\n"
                        "• Conexiones restablecidas\n"
                        f"• {restart_result}\n\n"
                        "💡 Usa /startbot para iniciar el bot manualmente."
                    )
            else:
                logger.info("✅ Bot reiniciado correctamente (no estaba corriendo)")
                return (
                    "✅ *BOT REINICIADO*\n\n"
                    "• Configuración recargada\n"
                    "• Conexiones restablecidas\n"
                    "• Análisis reiniciado\n\n"
                    "💡 El bot no estaba corriendo. Usa /startbot para iniciarlo."
                )
            
        except Exception as e:
            logger.error(f"Error reiniciando bot: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"❌ Error: {str(e)}"
    
    def full_reset(self):
        """Reinicio total del sistema (⚠️ DESTRUCTIVO)"""
        try:
            logger.warning("⚠️ Ejecutando reinicio total...")
            
            # Detener bot
            if self.running:
                self.stop()
            
            # Limpiar base de datos
            try:
                self.db.clear_all_data()
                logger.info("✅ Base de datos limpiada")
            except Exception as e:
                logger.warning(f"Error limpiando BD: {e}")
            
            # Resetear portafolio
            self.portfolio = {}
            self.trades_history = []
            
            # Resetear predictor LSTM si existe
            if LSTM_AVAILABLE and LSTMPredictor:
                try:
                    self.predictor = LSTMPredictor()
                    self.lstm_predictor = self.predictor
                    logger.info("✅ Modelo LSTM reiniciado")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo reiniciar LSTM Predictor: {e}")
                    self.predictor = None
                    self.lstm_predictor = None
            
            # Recargar configuración por defecto
            self.config = self._load_config("professional_config.json")
            self._load_universe()
            
            logger.info("✅ Reinicio total completado")
            return "Sistema restablecido a estado inicial"
            
        except Exception as e:
            logger.error(f"Error en reinicio total: {e}")
            return f"Error: {str(e)}"
    
    def get_config_for_telegram(self) -> Dict:
        """Obtiene configuración actual formateada para Telegram"""
        try:
            return {
                "mode": "LIVE" if not self.iol_client.mock_mode else "MOCK",
                "symbols_count": len(self.symbols),
                "interval_minutes": self.config.get("monitoring", {}).get("update_interval_minutes", 15),
                "max_position": self.config.get("trading", {}).get("max_position_size", 0.1),
                "stop_loss": self.config.get("risk_management", {}).get("stop_loss_percentage", 0.02),
                "take_profit": self.config.get("risk_management", {}).get("take_profit_percentage", 0.04),
                "ta_enabled": self.config.get("strategies", {}).get("technical_analysis", {}).get("enabled", True),
                "sentiment_enabled": self.config.get("strategies", {}).get("sentiment_analysis", {}).get("enabled", True),
                "lstm_enabled": self.predictor is not None,
                "av_enabled": self.alpha_vantage and self.alpha_vantage.enabled if hasattr(self, 'alpha_vantage') else False
            }
        except Exception as e:
            logger.error(f"Error obteniendo config para Telegram: {e}")
            return {}
    
    def get_learning_status(self) -> Dict:
        """Obtiene estado de aprendizaje IA formateado para Telegram"""
        try:
            if not self.predictor:
                return {
                    "lstm_status": "No disponible",
                    "epochs": 0,
                    "accuracy": 0,
                    "last_training": "N/A",
                    "correct_predictions": 0,
                    "total_predictions": 0,
                    "hit_rate": 0,
                    "auto_retrain": False,
                    "next_training": "N/A"
                }
            
            # Obtener métricas del predictor
            # Nota: Estas métricas deberían estar implementadas en LSTMPredictor
            return {
                "lstm_status": "Entrenado" if hasattr(self.predictor, 'model') else "No entrenado",
                "epochs": getattr(self.predictor, 'epochs_trained', 0),
                "accuracy": getattr(self.predictor, 'accuracy', 0),
                "last_training": getattr(self.predictor, 'last_training_date', 'N/A'),
                "correct_predictions": getattr(self.predictor, 'correct_predictions', 0),
                "total_predictions": getattr(self.predictor, 'total_predictions', 0),
                "hit_rate": getattr(self.predictor, 'hit_rate', 0),
                "auto_retrain": True,
                "next_training": "Cada 24 horas"
            }
        except Exception as e:
            logger.error(f"Error obteniendo estado de aprendizaje: {e}")
            return {}


if __name__ == "__main__":
    # Crear e iniciar el bot
    bot = TradingBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Interrupción del usuario")
    finally:
        bot.stop()
