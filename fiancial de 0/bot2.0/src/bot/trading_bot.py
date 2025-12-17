"""
Trading Bot Main Orchestrator
Orquestador principal del sistema de trading
"""

import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..bot.config import settings
from ..api.iol_client import IOLClient
from ..api.mock_iol_client import MockIOLClient
from ..analysis.technical_indicators import TechnicalIndicators
from ..analysis.signal_generator import SignalGenerator
from ..ai.rl_agent import RLAgent
from ..ai.sentiment_analyzer import SentimentAnalyzer
from ..ai.news_aggregator import NewsAggregator
from ..strategy.hybrid_strategy import HybridStrategy
from ..risk.position_sizer import PositionSizer
from ..risk.risk_manager import RiskManager
from ..database.db_manager import db_manager
from ..database.models import Trade, SentimentLog, SystemLog, PerformanceMetric
from ..utils.logger import log
from ..utils.optimal_config import optimal_config_manager


class TradingBot:
    """Bot de trading algorítmico principal"""
    
    def __init__(self):
        """Inicializa el bot de trading"""
        log.info("🤖 Inicializando Professional IOL Trading Bot v2.0...")
        
        # Configuración
        self.settings = settings
        self.running = False
        
        # Cargar configuración dinámica
        from src.utils.config_manager import config_manager
        from src.utils.market_manager import MarketManager
        
        self.config_manager = config_manager
        self.market_manager = MarketManager()
        
        # Obtener símbolos desde configuración dinámica
        symbol_categories = self.config_manager.get_symbol_categories()
        if symbol_categories:
            all_symbols = self.market_manager.get_symbols_by_category(symbol_categories)
            max_symbols = self.config_manager.get_max_symbols()
            
            # Limitar número de símbolos
            if max_symbols > 0:
                self.symbols = all_symbols[:max_symbols]
            else:
                self.symbols = all_symbols
            
            log.info(f"📊 Universo dinámico: {len(self.symbols)} símbolos de categorías {symbol_categories}")
        else:
            # Fallback a símbolos del .env
            self.symbols = self.settings.get_trading_symbols_list()
            log.info(f"📊 Usando símbolos configurados: {self.symbols}")
        
        # Cliente IOL (real o mock)
        if self.settings.mock_mode:
            log.info("📊 Modo: MOCK (Simulación)")
            self.client = MockIOLClient(
                username=self.settings.iol_username,
                password=self.settings.iol_password,
                base_url=self.settings.iol_base_url,
                initial_capital=self.settings.mock_initial_capital
            )
        else:
            log.warning("💰 Modo: LIVE (Dinero Real)")
            self.client = IOLClient(
                username=self.settings.iol_username,
                password=self.settings.iol_password,
                base_url=self.settings.iol_base_url
            )
        
        # Autenticar
        self.client.authenticate()
        
        # Componentes de análisis
        self.technical_indicators = TechnicalIndicators()
        self.signal_generator = SignalGenerator()
        
        # Componentes de AI
        self.rl_agent = None
        if self.settings.use_rl_agent:
            self.rl_agent = RLAgent()
            # Intentar cargar modelo existente
            if not self.rl_agent.load():
                log.warning("⚠ No se encontró modelo RL pre-entrenado")
        
        self.sentiment_analyzer = None
        self.news_aggregator = None
        if self.settings.use_sentiment_analysis:
            self.sentiment_analyzer = SentimentAnalyzer()
            self.news_aggregator = NewsAggregator(
                newsdata_api_key=self.settings.newsdata_api_key,
                finnhub_api_key=self.settings.finnhub_api_key,
                alphavantage_api_key=self.settings.alphavantage_api_key
            )
        
        # Estrategia híbrida
        self.strategy = HybridStrategy(
            signal_generator=self.signal_generator,
            sentiment_analyzer=self.sentiment_analyzer,
            news_aggregator=self.news_aggregator,
            use_sentiment=self.settings.use_sentiment_analysis
        )
        
        # Gestión de riesgo
        self.position_sizer = PositionSizer(
            risk_per_trade=self.settings.risk_per_trade,
            max_position_size=self.settings.max_position_size
        )
        self.risk_manager = RiskManager(
            max_position_size=self.settings.max_position_size
        )
        
        # Monitor de posiciones activas (para SL/TP automático)
        from ..risk.position_monitor import PositionMonitor
        self.position_monitor = PositionMonitor(self.client)
        
        # Anomaly Detector (Phase 1 IA Enhancement)
        try:
            from ..ai.anomaly_detector import AnomalyDetector
            self.anomaly_detector = AnomalyDetector(sensitivity=2.0)
            log.info("[OK] Anomaly Detector inicializado")
        except ImportError:
            self.anomaly_detector = None
            log.warning("[WARNING] Anomaly Detector no disponible")
        
        log.info("✓ Bot inicializado correctamente")
    
    def get_historical_data(self, symbol: str, days: int = 100) -> Optional[pd.DataFrame]:
        """Obtiene datos históricos con indicadores calculados"""
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            df = self.client.get_historical_data(symbol, from_date, to_date)
            
            if df is None or len(df) < 50:
                log.warning(f"⚠ Datos insuficientes para {symbol}")
                return None
            
            # Calcular indicadores
            df = self.technical_indicators.calculate_all_indicators(df)
            
            # Eliminar NaN
            df = df.dropna()
            
            return df
            
        except Exception as e:
            log.error(f"❌ Error obteniendo datos de {symbol}: {e}")
            return None
    
    def analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analiza un símbolo y genera decisión de trading"""
        try:
            log.info(f"📊 Analizando {symbol}...")
            
            # Obtener datos históricos
            df = self.get_historical_data(symbol)
            if df is None:
                return None
            
            # [PHASE 1 IA] ANOMALY DETECTOR: Verificar anomalías de mercado
            anomaly_result = None
            if self.anomaly_detector:
                try:
                    current_price = df.iloc[-1]['close']
                    prev_price = df.iloc[-2]['close'] if len(df) > 1 else current_price
                    
                    # Preparar datos para anomaly detector (requiere columnas específicas)
                    price_data = pd.DataFrame({
                        'close': df['close'],
                        'volume': df['volume'] if 'volume' in df.columns else [0]*len(df)
                    })
                    
                    anomaly_result = self.anomaly_detector.update(price_data, prev_price)
                    action = self.anomaly_detector.get_action_recommendation(anomaly_result)
                    
                    log.info(f"[ANOMALY] {symbol}: Severity={anomaly_result['severity']}, Action={action}")
                    
                    # Si hay anomalía crítica, pausar trading
                    if action == 'CLOSE_POSITIONS' or anomaly_result['severity'] == 'CRITICAL':
                        log.warning(f"[ALERT] Anomalía crítica en {symbol} - Trading pausado")
                        return None  # Skip trading para este símbolo
                    
                    if action == 'PAUSE':
                        log.warning(f"[ALERT] Anomalía en {symbol} - Esperando claridad")
                        return None
                except Exception as e:
                    log.warning(f"[WARNING] Error en anomaly detector: {e}")
            
            # CARGAR CONFIGURACIONES ÓPTIMAS (si existen)
            optimal_params = optimal_config_manager.get_parameters(symbol, defaults={
                'rsi_buy': 30,
                'rsi_sell': 70,
                'sma_period': 50
            })
            
            if optimal_params != {'rsi_buy': 30, 'rsi_sell': 70, 'sma_period': 50}:
                log.info(f"✨ Usando configuración óptima para {symbol}: {optimal_params}")
            # Predicción del agente RL
            rl_prediction = None
            if self.rl_agent and self.rl_agent.model:
                # Obtener estado actual
                indicators = self.technical_indicators.get_latest_indicators(df)
                
                # Obtener sentimiento
                sentiment_score = 0.0
                if self.sentiment_analyzer and self.news_aggregator:
                    sentiment_data = self.strategy.get_sentiment_score(symbol)
                    sentiment_score = sentiment_data['score']
                
                # Predecir (necesitamos normalización)
                price_min = df['close'].min()
                price_max = df['close'].max()
                macd_min = df['macd'].min()
                macd_max = df['macd'].max()
                
                rl_prediction = self.rl_agent.predict_from_state(
                    price=indicators['price'],
                    rsi=indicators['rsi'],
                    macd=indicators['macd'],
                    sentiment=sentiment_score,
                    position_ratio=0.0,  # Simplificado
                    cash_ratio=1.0,
                    price_min=price_min,
                    price_max=price_max,
                    macd_min=macd_min,
                    macd_max=macd_max
                )
            
            # Generar decisión con estrategia híbrida (pasando parámetros óptimos)
            decision = self.strategy.generate_decision(df, symbol, rl_prediction, optimal_params)
            
            # Agregar datos actuales
            current_price = df.iloc[-1]['close']
            atr = df.iloc[-1]['atr']
            
            decision['symbol'] = symbol
            decision['current_price'] = current_price
            decision['atr'] = atr
            decision['timestamp'] = datetime.now()
            
            log.info(f"✓ {symbol}: {decision['signal']} (confianza: {decision['confidence']*100:.1f}%)")
            log.info(f"  Razón: {decision['reasoning']}")
            
            return decision
            
        except Exception as e:
            log.error(f"❌ Error analizando {symbol}: {e}")
            return None
    
    def execute_trade(self, decision: Dict) -> bool:
        """Ejecuta una operación basada en la decisión"""
        try:
            symbol = decision['symbol']
            signal = decision['signal']
            current_price = decision['current_price']
            atr = decision['atr']
            
            if signal == "HOLD":
                return False
            
            # Obtener balance y posiciones
            balance = self.client.get_account_balance()
            current_position = self.client.get_position(symbol)
            
            if signal == "BUY":
                # Calcular tamaño de posición
                position_info = self.position_sizer.calculate_position_size_atr(
                    account_balance=balance,
                    current_price=current_price,
                    atr=atr
                )
                
                quantity = position_info['quantity']
                
                if quantity == 0:
                    log.warning(f"⚠ Cantidad calculada es 0 para {symbol}")
                    return False
                
                # Verificar con risk manager
                portfolio = self.client.get_portfolio()
                positions = {}
                if portfolio and 'activos' in portfolio:
                    positions = {
                        a['titulo']['simbolo']: a['valorActual']
                        for a in portfolio['activos']
                    }
                
                approval = self.risk_manager.check_trade_approval(
                    action="BUY",
                    symbol=symbol,
                    quantity=quantity,
                    price=current_price,
                    current_positions=positions,
                    account_balance=balance
                )
                
                if not approval['approved']:
                    log.warning(f"⚠ Operación rechazada: {approval['reason']}")
                    return False
                
                # Ejecutar compra
                log.info(f"🛒 COMPRANDO {quantity} {symbol} @ ${current_price:,.2f}")
                result = self.client.buy(symbol, quantity)
                
                if result:
                    # CALCULAR STOP LOSS Y TAKE PROFIT
                    from ..risk.dynamic_risk_manager import DynamicRiskManager
                    risk_mgr = DynamicRiskManager(
                        sl_atr_multiplier=2.0,
                        tp_atr_multiplier=3.0,
                        trailing_stop=True
                    )
                    
                    levels = risk_mgr.calculate_levels(
                        entry_price=current_price,
                        atr=atr,
                        direction="LONG"
                    )
                    
                    log.info(f"🛡️ Stop Loss: ${levels['stop_loss']:,.2f} | 🎯 Take Profit: ${levels['take_profit']:,.2f}")
                    
                    # Registrar trade en base de datos
                    trade_id = self._log_trade(
                        symbol=symbol,
                        action="BUY",
                        quantity=quantity,
                        price=current_price,
                        decision=decision,
                        position_info=position_info,
                        stop_loss=levels['stop_loss'],
                        take_profit=levels['take_profit']
                    )
                    
                    # CREAR POSICIÓN ACTIVA
                    from ..database.models import ActivePosition
                    with db_manager.get_session() as session:
                        active_pos = ActivePosition(
                            symbol=symbol,
                            entry_price=current_price,
                            quantity=quantity,
                            direction="LONG",
                            atr=atr,
                            stop_loss=levels['stop_loss'],
                            take_profit=levels['take_profit'],
                            trailing_stop=True,
                            current_price=current_price,
                            trade_id=trade_id,
                            mode="LIVE" if not self.settings.mock_mode else "MOCK"
                        )
                        session.add(active_pos)
                        session.commit()
                        log.info(f"✅ Posición activa creada con protección SL/TP")
                    
                    log.info(f"✓ Compra ejecutada exitosamente")
                    return True
                
            elif signal == "SELL":
                # Vender posición actual
                if current_position == 0:
                    log.warning(f"⚠ No hay posición de {symbol} para vender")
                    return False
                
                log.info(f"💰 VENDIENDO {current_position} {symbol} @ ${current_price:,.2f}")
                result = self.client.sell(symbol, current_position)
                
                if result:
                    # Registrar en base de datos
                    self._log_trade(
                        symbol=symbol,
                        action="SELL",
                        quantity=current_position,
                        price=current_price,
                        decision=decision
                    )
                    log.info(f"✓ Venta ejecutada exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            log.error(f"❌ Error ejecutando trade: {e}")
            return False
    
    def _log_trade(self, symbol: str, action: str, quantity: int, price: float, 
                   decision: Dict, position_info: Dict = None, 
                   stop_loss: float = None, take_profit: float = None):
        """Registra un trade en la base de datos y retorna su ID"""
        try:
            with db_manager.get_session() as session:
                trade = Trade(
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    price=price,
                    total_value=quantity * price,
                    technical_signal=decision['components']['technical']['signal'],
                    rl_prediction=decision['components']['rl']['signal'],
                    sentiment_score=decision['components']['sentiment']['score'],
                    position_size_pct=position_info['position_pct'] if position_info else 0,
                    atr_value=decision.get('atr', 0),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    mode="MOCK" if self.settings.mock_mode else "LIVE",
                    notes=decision['reasoning']
                )
                session.add(trade)
                session.commit()
                session.refresh(trade)
                return trade.id
        except Exception as e:
            log.error(f"❌ Error guardando trade: {e}")
            return None
    
    def run_trading_loop(self):
        """Loop principal de trading"""
        log.info("🚀 Iniciando loop de trading...")
        self.running = True
        
        iteration = 0
        
        while self.running:
            try:
                iteration += 1
                log.info(f"\n{'='*60}")
                log.info(f"📈 Iteración #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                log.info(f"{'='*60}")
                
                # Analizar cada símbolo
                for symbol in self.symbols:
                    decision = self.analyze_symbol(symbol)
                    
                    if decision:
                        self.execute_trade(decision)
                    
                    # Pequeña pausa entre símbolos
                    time.sleep(2)
                
                # MONITOREAR POSICIONES ACTIVAS (SL/TP automático)
                try:
                    monitor_stats = self.position_monitor.check_all_positions()
                    if monitor_stats['checked'] > 0:
                        log.info(f"📡 Monitor: {monitor_stats['checked']} posiciones | "
                                f"SL: {monitor_stats['closed_sl']} | "
                                f"TP: {monitor_stats['closed_tp']} | "
                                f"Actualizadas: {monitor_stats['updated']}")
                except Exception as e:
                    log.error(f"❌ Error en position_monitor: {e}")
                
                # Mostrar resumen del portafolio
                self._show_portfolio_summary()
                
                # Esperar hasta la siguiente iteración
                log.info(f"\n⏳ Esperando {self.settings.trading_interval} segundos...")
                time.sleep(self.settings.trading_interval)
                
            except KeyboardInterrupt:
                log.info("\n⚠ Interrupción detectada - deteniendo bot...")
                self.running = False
            except Exception as e:
                log.error(f"❌ Error en loop de trading: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _show_portfolio_summary(self):
        """Muestra resumen del portafolio"""
        try:
            portfolio = self.client.get_portfolio()
            
            if not portfolio:
                return
            
            log.info("\n" + "="*60)
            log.info("💼 RESUMEN DEL PORTAFOLIO")
            log.info("="*60)
            
            if hasattr(self.client, 'get_performance'):
                perf = self.client.get_performance()
                log.info(f"Capital Inicial: ${perf['initial_capital']:,.2f}")
                log.info(f"Valor Actual:    ${perf['current_value']:,.2f}")
                log.info(f"Retorno:         ${perf['total_return']:,.2f} ({perf['total_return_pct']:.2f}%)")
                log.info(f"Efectivo:        ${perf['cash']:,.2f}")
                log.info(f"Posiciones:      {perf['positions']}")
            else:
                log.info(f"Valor Total:     ${portfolio.get('valorTotal', 0):,.2f}")
                log.info(f"Efectivo:        ${portfolio.get('efectivo', 0):,.2f}")
                log.info(f"Invertido:       ${portfolio.get('totalInvertido', 0):,.2f}")
            
            log.info("="*60 + "\n")
            
        except Exception as e:
            log.error(f"❌ Error mostrando resumen: {e}")
    
    def stop(self):
        """Detiene el bot"""
        log.info("🛑 Deteniendo bot...")
        self.running = False
