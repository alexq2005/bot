"""
Refactored Trading Bot (v2.0)
Bot de trading con arquitectura limpia y desacoplada

Este es el nuevo TradingBot que usa:
- Objetos de dominio (Signal, OrderDecision, Order)
- BaseStrategy interface
- ProfessionalRiskManager
- DataFeed abstraction
- OrderExecutor

El bot ahora SOLO orquesta, no toma decisiones.
"""

from typing import List, Optional
from datetime import datetime
import time

from ..strategy.base import BaseStrategy
from ..risk.professional_risk_manager import ProfessionalRiskManager
from ..datafeed.feed import DataFeed
from ..execution.executor import OrderExecutor
from ..domain.signal import Signal
from ..domain.decision import OrderDecision
from ..domain.order import Order


class RefactoredTradingBot:
    """
    Trading Bot con arquitectura limpia
    
    Responsabilidades:
    1. Orquestar el flujo: Data → Strategy → Risk → Execution
    2. Mantener el loop de trading
    3. Logging y monitoring
    
    NO es responsable de:
    - Generar señales (eso es Strategy)
    - Evaluar riesgo (eso es RiskManager)
    - Ejecutar órdenes (eso es Executor)
    - Obtener datos (eso es DataFeed)
    """
    
    def __init__(
        self,
        data_feed: DataFeed,
        strategies: List[BaseStrategy],
        risk_manager: ProfessionalRiskManager,
        executor: OrderExecutor,
        symbols: List[str],
        interval_seconds: int = 300
    ):
        """
        Inicializa el bot
        
        Args:
            data_feed: Feed de datos de mercado
            strategies: Lista de estrategias a ejecutar
            risk_manager: Risk manager profesional
            executor: Executor de órdenes
            symbols: Lista de símbolos a operar
            interval_seconds: Intervalo entre análisis (segundos)
        """
        self.data_feed = data_feed
        self.strategies = strategies
        self.risk_manager = risk_manager
        self.executor = executor
        self.symbols = symbols
        self.interval_seconds = interval_seconds
        
        # Estado
        self.running = False
        self.total_signals_generated = 0
        self.total_signals_approved = 0
        self.total_signals_rejected = 0
        self.total_orders_executed = 0
        
        print(f"🤖 RefactoredTradingBot inicializado")
        print(f"   Estrategias: {[s.get_name() for s in strategies]}")
        print(f"   Símbolos: {len(symbols)}")
        print(f"   Intervalo: {interval_seconds}s")
    
    def analyze_symbol(self, symbol: str) -> Optional[Signal]:
        """
        Analiza un símbolo con todas las estrategias
        
        Args:
            symbol: Símbolo a analizar
        
        Returns:
            Signal con mayor confidence, o None si no hay señales
        """
        # Obtener datos de mercado
        market_data = self.data_feed.get_latest(symbol, lookback=100)
        
        if market_data is None or len(market_data) == 0:
            return None
        
        # Ejecutar todas las estrategias
        signals = []
        for strategy in self.strategies:
            try:
                signal = strategy.generate_signal(market_data)
                if signal:
                    signals.append(signal)
            except Exception as e:
                print(f"❌ Error en estrategia {strategy.get_name()}: {e}")
        
        # Retornar señal con mayor confidence
        if signals:
            best_signal = max(signals, key=lambda s: s.confidence)
            return best_signal
        
        return None
    
    def run_once(self):
        """
        Ejecuta un ciclo completo de análisis
        
        Flujo:
        1. Para cada símbolo
        2. Obtener datos (DataFeed)
        3. Generar señal (Strategy)
        4. Evaluar riesgo (RiskManager)
        5. Ejecutar si aprobado (Executor)
        """
        if not self.data_feed.is_market_open():
            print("⏸️  Mercado cerrado")
            return
        
        print(f"\n{'='*60}")
        print(f"🔄 Ciclo de análisis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for symbol in self.symbols:
            try:
                # 1. Generar señal
                signal = self.analyze_symbol(symbol)
                
                if not signal:
                    continue
                
                self.total_signals_generated += 1
                
                print(f"\n📊 Señal generada para {symbol}:")
                print(f"   Estrategia: {signal.strategy_name}")
                print(f"   Lado: {signal.side}")
                print(f"   Entry: ${signal.entry:.2f}")
                print(f"   Stop Loss: ${signal.stop_loss:.2f}")
                print(f"   Take Profit: ${signal.take_profit:.2f}")
                print(f"   Confidence: {signal.confidence:.2%}")
                print(f"   Risk/Reward: {signal.risk_reward_ratio:.2f}")
                
                # 2. Evaluar riesgo
                current_exposure = self.executor.get_total_exposure()
                decision = self.risk_manager.evaluate(signal, current_exposure)
                
                if decision.approved:
                    self.total_signals_approved += 1
                    
                    print(f"✅ Señal APROBADA por Risk Manager")
                    print(f"   Tamaño: {decision.size:.2f} acciones")
                    print(f"   Riesgo: ${decision.risk_amount:.2f}")
                    
                    # 3. Ejecutar orden
                    order = self.executor.execute(decision)
                    
                    if order:
                        self.total_orders_executed += 1
                        
                        print(f"✅ Orden EJECUTADA")
                        print(f"   ID: {order.id}")
                        print(f"   Fill: ${order.filled_price:.2f}")
                        print(f"   Comisión: ${order.commission:.2f}")
                        
                        # Actualizar equity del risk manager
                        # (En producción, esto vendría del portfolio real)
                        # self.risk_manager.update_equity(new_equity)
                    else:
                        print(f"❌ Orden RECHAZADA por broker")
                else:
                    self.total_signals_rejected += 1
                    
                    print(f"❌ Señal RECHAZADA por Risk Manager")
                    print(f"   Razón: {decision.reason}")
                
            except Exception as e:
                print(f"❌ Error procesando {symbol}: {e}")
                import traceback
                traceback.print_exc()
        
        # Mostrar estadísticas
        self._print_stats()
    
    def run_trading_loop(self):
        """
        Loop principal de trading
        
        Ejecuta run_once() cada interval_seconds mientras running=True
        """
        self.running = True
        
        print(f"\n{'='*60}")
        print(f"🚀 Iniciando Trading Loop")
        print(f"{'='*60}\n")
        
        try:
            while self.running:
                self.run_once()
                
                if self.running:
                    print(f"\n⏳ Esperando {self.interval_seconds}s hasta próximo ciclo...")
                    time.sleep(self.interval_seconds)
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupción manual detectada")
            self.stop()
        
        except Exception as e:
            print(f"\n\n❌ Error crítico en trading loop: {e}")
            import traceback
            traceback.print_exc()
            self.stop()
    
    def stop(self):
        """
        Detiene el bot
        """
        print(f"\n{'='*60}")
        print(f"⏹️  Deteniendo Trading Bot")
        print(f"{'='*60}")
        
        self.running = False
        
        # Mostrar resumen final
        self._print_final_summary()
    
    def _print_stats(self):
        """
        Imprime estadísticas del ciclo actual
        """
        rm_stats = self.risk_manager.get_stats()
        exec_stats = self.executor.get_stats()
        
        print(f"\n📈 Estadísticas del Bot:")
        print(f"   Señales generadas: {self.total_signals_generated}")
        print(f"   Señales aprobadas: {self.total_signals_approved}")
        print(f"   Señales rechazadas: {self.total_signals_rejected}")
        print(f"   Órdenes ejecutadas: {self.total_orders_executed}")
        
        print(f"\n💰 Risk Manager:")
        print(f"   Equity: ${rm_stats['equity']:,.2f}")
        print(f"   Drawdown: {rm_stats['current_drawdown']:.2%}")
        print(f"   Riesgo/trade: {rm_stats['risk_per_trade']:.2%}")
        print(f"   Trading habilitado: {rm_stats['trading_enabled']}")
        
        print(f"\n📋 Executor:")
        print(f"   Órdenes activas: {exec_stats['active_orders']}")
        print(f"   Órdenes completadas: {exec_stats['completed_orders']}")
        print(f"   Exposición total: ${exec_stats['total_exposure']:,.2f}")
    
    def _print_final_summary(self):
        """
        Imprime resumen final al detener el bot
        """
        rm_stats = self.risk_manager.get_stats()
        
        print(f"\n📊 Resumen Final:")
        print(f"   Total señales: {self.total_signals_generated}")
        print(f"   Aprobadas: {self.total_signals_approved} ({self.total_signals_approved/max(1,self.total_signals_generated)*100:.1f}%)")
        print(f"   Rechazadas: {self.total_signals_rejected} ({self.total_signals_rejected/max(1,self.total_signals_generated)*100:.1f}%)")
        print(f"   Órdenes ejecutadas: {self.total_orders_executed}")
        print(f"\n   Equity final: ${rm_stats['equity']:,.2f}")
        print(f"   Drawdown máximo: {rm_stats['current_drawdown']:.2%}")
        print(f"   Win rate: {rm_stats['win_rate']:.1f}%")
        
        print(f"\n✅ Bot detenido correctamente\n")
