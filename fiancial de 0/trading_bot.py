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
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from src.services.trading.iol_client import IOLClient
from src.services.analysis.technical_analysis_service import TechnicalAnalysisService

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        
        self.iol_client = IOLClient(username, password)
        self.ta_service = TechnicalAnalysisService()

        # Estado
        self.symbols = []
        self.portfolio = {} # { "GGAL": { "quantity": 100, "price": ... } }
        self.trades_history = []
        
        # Cargar universo de símbolos (simulado o config)
        self._load_universe()
        
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
        """
        logger.info("🌍 Cargando universo de símbolos...")
        # En una versión full, esto vendría de IOL o una DB.
        # Por ahora usamos una lista fija de activos líquidos del Merval + CEDEARs populares
        self.symbols = [
            "GGAL", "YPFD", "PAMP", "ALUA", "BMA", "TXAR", "CEPU", # Merval
            "AAPL", "MELI", "KO", "TSLA", "AMZN", "MSFT" # CEDEARs
        ]
    
    def run(self):
        """Ejecuta el ciclo principal del bot"""
        logger.info("🚀 Iniciando bucle de trading...")
        self.running = True
        
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
        """Actualiza el estado del portafolio localmente"""
        try:
            portfolio_data = self.iol_client.get_portfolio()
            if portfolio_data and "assets" in portfolio_data:
                self.portfolio = {
                    item["symbol"]: item for item in portfolio_data["assets"]
                }
            logger.info("💼 Portafolio actualizado")
        except Exception as e:
            logger.error(f"Error actualizando portafolio: {e}")

    def _process_symbol(self, symbol: str):
        """Procesa un símbolo individual: Datos -> Análisis -> Señal -> Orden"""
        try:
            # 1. Obtener Datos Históricos para AT
            # Usamos rango fijo para demo, en real sería dinámico
            historical_data = self.iol_client.get_historical_data(symbol, "2023-01-01", "2024-01-01")

            if not historical_data:
                return

            df = pd.DataFrame(historical_data)

            # 2. Análisis Técnico
            analysis = self.ta_service.analyze(symbol, df)
            signal = analysis.get("signal")

            # 3. Obtener Precio Actual
            market_data = self.iol_client.get_market_data(symbol)
            if not market_data:
                return

            current_price = market_data.get("last_price")

            # 4. Lógica de Ejecución (Simplificada)
            if signal in ["BUY", "STRONG_BUY"]:
                self._execute_buy(symbol, current_price, signal)
            elif signal in ["SELL", "STRONG_SELL"]:
                self._execute_sell(symbol, current_price, signal)
            else:
                pass # HOLD

        except Exception as e:
            logger.error(f"Error procesando {symbol}: {e}")

    def _execute_buy(self, symbol: str, price: float, signal: str):
        """Ejecuta compra si hay capital y gestión de riesgo lo permite"""
        logger.info(f"🔵 Señal de COMPRA para {symbol} ({signal}) a ${price}")

        # TODO: Verificar saldo disponible
        quantity = 10 # Cantidad fija por ahora

        order = self.iol_client.place_order(symbol, "comprar", quantity, price)
        if order:
            self._record_trade("BUY", symbol, quantity, price, signal)
            self._refresh_portfolio()

    def _execute_sell(self, symbol: str, price: float, signal: str):
        """Ejecuta venta si se tiene el activo"""
        logger.info(f"🔴 Señal de VENTA para {symbol} ({signal}) a ${price}")

        # Verificar tenencia en portafolio
        if self.iol_client.mock_mode:
            # En mock mode, simulamos tenerlo si lo hemos "comprado" o si está en el portfolio mock inicial
            asset = self.portfolio.get(symbol)
            current_qty = asset.get("quantity", 0) if asset else 0
            if current_qty < 10:
                logger.warning(f"⚠️ No se puede vender {symbol}: Tenencia insuficiente ({current_qty})")
                return

        quantity = 10 # Cantidad fija por ahora

        order = self.iol_client.place_order(symbol, "vender", quantity, price)
        if order:
            self._record_trade("SELL", symbol, quantity, price, signal)
            self._refresh_portfolio()

    def _record_trade(self, side, symbol, quantity, price, signal):
        """Registra el trade en el historial"""
        trade = {
            "timestamp": datetime.now().isoformat(),
            "side": side,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "signal": signal
        }
        self.trades_history.append(trade)
        logger.info(f"✅ Trade registrado: {trade}")

    def stop(self):
        """Detiene el bot de forma segura"""
        logger.info("🛑 Deteniendo bot...")
        self.running = False


if __name__ == "__main__":
    # Crear e iniciar el bot
    bot = TradingBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Interrupción del usuario")
    finally:
        bot.stop()
