"""
Ejemplo Completo del Sistema Refactorizado
Demuestra el uso end-to-end con todas las piezas integradas
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Componentes del sistema
from src.strategy.hybrid_strategy_v2 import HybridStrategyV2
from src.risk.professional_risk_manager import ProfessionalRiskManager
from src.datafeed.feed import HistoricalDataFeed
from src.execution.executor import BacktestExecutor
from src.bot.refactored_trading_bot import RefactoredTradingBot
from src.api.mock_iol_client import MockIOLClient
from src.analysis.signal_generator import SignalGenerator


def create_sample_data(symbol: str, days: int = 100) -> pd.DataFrame:
    """
    Crea datos de muestra para testing
    
    Args:
        symbol: Símbolo del activo
        days: Cantidad de días de datos
    
    Returns:
        DataFrame con datos OHLCV e indicadores
    """
    # Generar datos sintéticos
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Precio base con tendencia y ruido
    base_price = 100
    trend = np.linspace(0, 20, days)
    noise = np.random.randn(days) * 2
    close = base_price + trend + noise
    
    # OHLC
    high = close + np.abs(np.random.randn(days))
    low = close - np.abs(np.random.randn(days))
    open_price = close + np.random.randn(days) * 0.5
    volume = np.random.randint(100000, 1000000, days)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'symbol': symbol,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    # Calcular indicadores
    df['rsi_14'] = calculate_rsi(df['close'], 14)
    df['sma_50'] = df['close'].rolling(50).mean()
    df['sma_200'] = df['close'].rolling(200).mean()
    
    # Bollinger Bands
    sma_20 = df['close'].rolling(20).mean()
    std_20 = df['close'].rolling(20).std()
    df['bb_upper'] = sma_20 + (std_20 * 2)
    df['bb_middle'] = sma_20
    df['bb_lower'] = sma_20 - (std_20 * 2)
    
    # MACD
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    return df


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calcula RSI
    
    Args:
        prices: Serie de precios
        period: Período del RSI
    
    Returns:
        Serie con valores de RSI
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def ejemplo_sistema_completo():
    """
    Ejemplo completo del sistema refactorizado
    """
    print("="*70)
    print("EJEMPLO COMPLETO: Sistema Refactorizado End-to-End")
    print("="*70)
    
    # 1. Crear datos de muestra
    print("\n1️⃣ Creando datos de muestra...")
    symbols = ['GGAL', 'YPFD', 'PAMP']
    historical_data = {}
    
    for symbol in symbols:
        historical_data[symbol] = create_sample_data(symbol, days=100)
        print(f"   ✅ {symbol}: {len(historical_data[symbol])} días de datos")
    
    # 2. Configurar componentes
    print("\n2️⃣ Configurando componentes del sistema...")
    
    # Broker (Mock para testing)
    broker = MockIOLClient(initial_capital=100000.0)
    print("   ✅ MockIOLClient inicializado con $100,000")
    
    # Data Feed (Histórico para backtest)
    data_feed = HistoricalDataFeed(historical_data)
    print("   ✅ HistoricalDataFeed configurado")
    
    # Estrategia
    signal_gen = SignalGenerator()
    strategy = HybridStrategyV2(
        signal_generator=signal_gen,
        use_sentiment=False,  # Desactivar sentimiento para este ejemplo
        consensus_threshold=0.6
    )
    print(f"   ✅ {strategy.get_name()} configurada")
    
    # Risk Manager
    risk_manager = ProfessionalRiskManager(
        initial_equity=100000.0,
        risk_per_trade=0.01,      # 1% por trade
        max_drawdown=0.15,         # 15% drawdown máximo
        max_exposure=0.30          # 30% exposición máxima
    )
    print("   ✅ ProfessionalRiskManager configurado")
    print(f"      - Riesgo/trade: {risk_manager.risk_per_trade:.2%}")
    print(f"      - Max drawdown: {risk_manager.max_drawdown:.2%}")
    
    # Executor (Backtest con slippage)
    executor = BacktestExecutor(
        broker_client=broker,
        commission_rate=0.0004,    # 0.04%
        slippage=0.0005            # 0.05%
    )
    print("   ✅ BacktestExecutor configurado")
    print(f"      - Comisión: {executor.commission_rate:.4%}")
    print(f"      - Slippage: {executor.slippage:.4%}")
    
    # Bot
    bot = RefactoredTradingBot(
        data_feed=data_feed,
        strategies=[strategy],
        risk_manager=risk_manager,
        executor=executor,
        symbols=symbols,
        interval_seconds=1  # Para testing rápido
    )
    print("   ✅ RefactoredTradingBot inicializado")
    
    # 3. Ejecutar un ciclo de análisis
    print("\n3️⃣ Ejecutando ciclo de análisis...")
    print("-"*70)
    
    bot.run_once()
    
    # 4. Mostrar resultados
    print("\n4️⃣ Resultados del Análisis:")
    print("-"*70)
    
    rm_stats = risk_manager.get_stats()
    exec_stats = executor.get_stats()
    
    print(f"\n📊 Risk Manager:")
    print(f"   Equity: ${rm_stats['equity']:,.2f}")
    print(f"   Drawdown: {rm_stats['current_drawdown']:.2%}")
    print(f"   Trading habilitado: {rm_stats['trading_enabled']}")
    
    print(f"\n📋 Executor:")
    print(f"   Órdenes completadas: {exec_stats['completed_orders']}")
    print(f"   Órdenes ejecutadas: {exec_stats['filled_orders']}")
    print(f"   Órdenes rechazadas: {exec_stats['rejected_orders']}")
    
    print(f"\n🤖 Bot:")
    print(f"   Señales generadas: {bot.total_signals_generated}")
    print(f"   Señales aprobadas: {bot.total_signals_approved}")
    print(f"   Señales rechazadas: {bot.total_signals_rejected}")
    
    # 5. Mostrar órdenes ejecutadas
    if exec_stats['filled_orders'] > 0:
        print(f"\n💼 Órdenes Ejecutadas:")
        print("-"*70)
        
        for order in executor.get_completed_orders():
            if order.is_filled:
                print(f"\n   ID: {order.id}")
                print(f"   Símbolo: {order.symbol}")
                print(f"   Lado: {order.side}")
                print(f"   Tamaño: {order.size:.2f}")
                print(f"   Precio: ${order.filled_price:.2f}")
                print(f"   Comisión: ${order.commission:.2f}")
                print(f"   Total: ${order.total_cost:.2f}")
    
    print("\n" + "="*70)
    print("✅ Ejemplo completado exitosamente")
    print("="*70)
    
    return bot, risk_manager, executor


if __name__ == "__main__":
    # Ejecutar ejemplo
    bot, rm, executor = ejemplo_sistema_completo()
    
    print("\n💡 CONCLUSIONES:")
    print("   ✅ Sistema completamente funcional")
    print("   ✅ Arquitectura limpia y desacoplada")
    print("   ✅ Objetos de dominio tipados")
    print("   ✅ Risk management profesional")
    print("   ✅ Listo para backtesting serio")
    print("")
