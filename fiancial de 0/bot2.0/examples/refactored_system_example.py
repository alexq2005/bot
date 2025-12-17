"""
Ejemplo de Uso del Sistema Refactorizado
Demuestra cómo usar la nueva arquitectura limpia
"""

from datetime import datetime
from src.strategy.base import BaseStrategy
from src.risk.professional_risk_manager import ProfessionalRiskManager
from src.datafeed.feed import LiveDataFeed
from src.execution.executor import OrderExecutor
from src.bot.refactored_trading_bot import RefactoredTradingBot
from src.domain.signal import Signal
from src.api.mock_iol_client import MockIOLClient
import pandas as pd


# ==============================================================================
# EJEMPLO 1: Estrategia Simple
# ==============================================================================
class SimpleRSIStrategy(BaseStrategy):
    """
    Estrategia simple basada en RSI
    """
    
    def __init__(self):
        super().__init__(name="Simple RSI")
        self.rsi_oversold = 30
        self.rsi_overbought = 70
    
    def generate_signal(self, market_data: pd.DataFrame) -> Signal | None:
        """
        Genera señal cuando RSI está en extremos
        """
        if not self.validate_market_data(market_data):
            return None
        
        if 'rsi_14' not in market_data.columns:
            return None
        
        if len(market_data) < 2:
            return None
        
        current = market_data.iloc[-1]
        rsi = current['rsi_14']
        price = current['close']
        
        # Señal de COMPRA cuando RSI < 30
        if rsi < self.rsi_oversold:
            return Signal(
                symbol=current.get('symbol', 'UNKNOWN'),
                side="BUY",
                entry=price,
                stop_loss=price * 0.97,  # Stop 3% abajo
                take_profit=price * 1.06,  # Target 6% arriba
                confidence=0.7,
                timestamp=datetime.now(),
                strategy_name=self.name
            )
        
        # Señal de VENTA cuando RSI > 70
        elif rsi > self.rsi_overbought:
            return Signal(
                symbol=current.get('symbol', 'UNKNOWN'),
                side="SELL",
                entry=price,
                stop_loss=price * 1.03,  # Stop 3% arriba
                take_profit=price * 0.94,  # Target 6% abajo
                confidence=0.7,
                timestamp=datetime.now(),
                strategy_name=self.name
            )
        
        return None
    
    def get_required_indicators(self) -> list:
        """
        Indicadores requeridos
        """
        return ['rsi_14']


# ==============================================================================
# EJEMPLO 2: Configuración y Ejecución
# ==============================================================================
def ejemplo_configuracion_basica():
    """
    Ejemplo de configuración básica del sistema
    """
    print("="*60)
    print("EJEMPLO: Configuración Básica del Sistema Refactorizado")
    print("="*60)
    
    # 1. Crear cliente del broker (Mock para testing)
    broker = MockIOLClient(initial_capital=100000.0)
    
    # 2. Crear Data Feed
    data_feed = LiveDataFeed(broker)
    
    # 3. Crear Estrategias
    strategies = [
        SimpleRSIStrategy()
    ]
    
    # 4. Crear Risk Manager
    risk_manager = ProfessionalRiskManager(
        initial_equity=100000.0,
        risk_per_trade=0.01,      # 1% por trade
        max_drawdown=0.15,         # 15% drawdown máximo
        max_exposure=0.30          # 30% exposición máxima
    )
    
    # 5. Crear Executor
    executor = OrderExecutor(
        broker_client=broker,
        commission_rate=0.0004     # 0.04% comisión
    )
    
    # 6. Crear Bot
    bot = RefactoredTradingBot(
        data_feed=data_feed,
        strategies=strategies,
        risk_manager=risk_manager,
        executor=executor,
        symbols=['GGAL', 'YPFD', 'PAMP'],
        interval_seconds=60  # Analizar cada 60 segundos
    )
    
    print("\n✅ Sistema configurado correctamente")
    print(f"   Estrategias: {[s.get_name() for s in strategies]}")
    print(f"   Capital inicial: ${risk_manager.equity:,.2f}")
    print(f"   Riesgo por trade: {risk_manager.risk_per_trade:.2%}")
    
    return bot


# ==============================================================================
# EJEMPLO 3: Flujo Completo
# ==============================================================================
def ejemplo_flujo_completo():
    """
    Ejemplo del flujo completo: Signal → Decision → Order
    """
    print("\n" + "="*60)
    print("EJEMPLO: Flujo Completo Signal → Decision → Order")
    print("="*60)
    
    # Crear componentes
    broker = MockIOLClient(initial_capital=100000.0)
    risk_manager = ProfessionalRiskManager(initial_equity=100000.0)
    executor = OrderExecutor(broker, commission_rate=0.0004)
    
    # 1. Crear una señal
    signal = Signal(
        symbol="GGAL",
        side="BUY",
        entry=100.0,
        stop_loss=95.0,  # 5% stop
        take_profit=110.0,  # 10% target
        confidence=0.8,
        timestamp=datetime.now(),
        strategy_name="Ejemplo"
    )
    
    print("\n1️⃣ SEÑAL GENERADA:")
    print(f"   Símbolo: {signal.symbol}")
    print(f"   Lado: {signal.side}")
    print(f"   Entry: ${signal.entry:.2f}")
    print(f"   Stop: ${signal.stop_loss:.2f}")
    print(f"   Target: ${signal.take_profit:.2f}")
    print(f"   R/R: {signal.risk_reward_ratio:.2f}")
    
    # 2. Evaluar con Risk Manager
    decision = risk_manager.evaluate(signal, current_exposure=0.0)
    
    print("\n2️⃣ DECISIÓN DEL RISK MANAGER:")
    print(f"   Aprobada: {decision.approved}")
    print(f"   Tamaño: {decision.size:.2f} acciones")
    print(f"   Riesgo: ${decision.risk_amount:.2f}")
    print(f"   Razón: {decision.reason}")
    
    # 3. Ejecutar si aprobada
    if decision.approved:
        order = executor.execute(decision)
        
        if order:
            print("\n3️⃣ ORDEN EJECUTADA:")
            print(f"   ID: {order.id}")
            print(f"   Estado: {order.status.value}")
            print(f"   Fill: ${order.filled_price:.2f}")
            print(f"   Comisión: ${order.commission:.2f}")
            print(f"   Costo total: ${order.total_cost:.2f}")
    
    print("\n✅ Flujo completado exitosamente")


# ==============================================================================
# EJEMPLO 4: Comparación Antes vs Después
# ==============================================================================
def ejemplo_comparacion():
    """
    Muestra la diferencia entre la arquitectura antigua y nueva
    """
    print("\n" + "="*60)
    print("COMPARACIÓN: Arquitectura Antigua vs Nueva")
    print("="*60)
    
    print("\n❌ ANTES (dict-based, acoplado):")
    print("""
    # TradingBot hacía TODO:
    signal = {
        "symbol": "GGAL",
        "side": "BUY",
        "entry": 100.0,
        "stop_loss": 95.0  # ¿Validado? ¿Qué pasa si > entry?
    }
    
    # Riesgo mezclado con lógica
    if signal["entry"] > 0:
        size = calculate_size(signal)  # ¿Dónde está esto?
        broker.place_order(...)  # ¿Qué pasa si falla?
    """)
    
    print("\n✅ DESPUÉS (tipado, desacoplado):")
    print("""
    # 1. Estrategia genera Signal (validado automáticamente)
    signal = Signal(
        symbol="GGAL",
        side="BUY",
        entry=100.0,
        stop_loss=95.0,  # Validado: debe ser < entry para BUY
        take_profit=110.0,
        confidence=0.8,
        timestamp=datetime.now()
    )
    
    # 2. Risk Manager evalúa (drawdown, exposure, sizing)
    decision = risk_manager.evaluate(signal)
    
    # 3. Executor ejecuta (comisiones, tracking, logging)
    if decision.approved:
        order = executor.execute(decision)
    """)
    
    print("\n📊 BENEFICIOS:")
    print("   ✅ Tipado fuerte → errores en desarrollo, no en producción")
    print("   ✅ Validación automática → sin datos inválidos")
    print("   ✅ Separación de responsabilidades → fácil de testear")
    print("   ✅ Plug & play → cambiar estrategias sin tocar el bot")
    print("   ✅ Backtesting 1:1 → mismo código para backtest y live")


# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 EJEMPLOS DE USO - SISTEMA REFACTORIZADO")
    print("="*60)
    
    # Ejemplo 1: Configuración básica
    bot = ejemplo_configuracion_basica()
    
    # Ejemplo 2: Flujo completo
    ejemplo_flujo_completo()
    
    # Ejemplo 3: Comparación
    ejemplo_comparacion()
    
    print("\n" + "="*60)
    print("✅ Todos los ejemplos completados")
    print("="*60)
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Migrar estrategias existentes a BaseStrategy")
    print("   2. Integrar con dashboard")
    print("   3. Crear backtester usando mismos componentes")
    print("   4. Tests de integración")
    print("")
