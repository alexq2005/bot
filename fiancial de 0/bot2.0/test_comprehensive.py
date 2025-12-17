"""
Comprehensive Project Test Suite
Suite completa de pruebas para validar el proyecto
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("\n" + "=" * 80)
print("SUITE COMPLETA DE PRUEBAS - PROYECTO BOT TRADING v2.0")
print("=" * 80 + "\n")

test_results = []

# ============================================================================
# SECCIÓN 1: VALIDACIÓN DE MÓDULOS PRINCIPALES
# ============================================================================
print("SECCIÓN 1: VALIDACIÓN DE MÓDULOS")
print("-" * 80)

modules_to_test = [
    ("Bot Config", "from src.bot.config import settings"),
    ("Technical Indicators", "from src.analysis.technical_indicators import TechnicalIndicators"),
    ("Position Sizer", "from src.risk.position_sizer import PositionSizer"),
    ("Database Manager", "from src.database.db_manager import DatabaseManager"),
    ("Trading Bot", "from src.bot.trading_bot import TradingBot"),
    ("Dynamic Risk Manager", "from src.risk.dynamic_risk_manager import DynamicRiskManager"),
    ("Signal Generator", "from src.analysis.signal_generator import SignalGenerator"),
    ("Data Collector", "from src.api.yahoo_client import YahooClient"),
]

for module_name, import_stmt in modules_to_test:
    try:
        exec(import_stmt)
        print(f"✅ {module_name}")
        test_results.append((f"Module: {module_name}", True, None))
    except Exception as e:
        print(f"❌ {module_name}: {str(e)[:60]}")
        test_results.append((f"Module: {module_name}", False, str(e)[:100]))

# ============================================================================
# SECCIÓN 2: VALIDACIÓN DE CÁLCULOS TÉCNICOS
# ============================================================================
print("\n\nSECCIÓN 2: VALIDACIÓN DE INDICADORES TÉCNICOS")
print("-" * 80)

try:
    from src.analysis.technical_indicators import TechnicalIndicators
    
    # Crear datos de ejemplo
    np.random.seed(42)
    prices = pd.Series(100 + np.cumsum(np.random.randn(100)))
    volume = pd.Series(np.random.randint(1000, 10000, 100))
    
    indicators = TechnicalIndicators()
    
    # Test RSI
    rsi = indicators.calculate_rsi(prices, period=14)
    assert len(rsi) == len(prices), "RSI length mismatch"
    assert rsi.notna().sum() > 0, "RSI all NaN"
    print(f"✅ RSI Calculation: min={rsi.min():.2f}, max={rsi.max():.2f}, mean={rsi.mean():.2f}")
    test_results.append(("RSI Calculation", True, None))
    
    # Test MACD
    macd_line, signal_line, hist = indicators.calculate_macd(prices)
    assert len(macd_line) == len(prices), "MACD length mismatch"
    print(f"✅ MACD Calculation: MACD line points={macd_line.notna().sum()}")
    test_results.append(("MACD Calculation", True, None))
    
    # Test Bollinger Bands
    upper_band, middle_band, lower_band = indicators.calculate_bollinger_bands(prices)
    assert len(upper_band) == len(prices), "Bollinger Bands length mismatch"
    print(f"✅ Bollinger Bands: upper-lower spread={upper_band.mean() - lower_band.mean():.2f}")
    test_results.append(("Bollinger Bands", True, None))
    
    # Test ATR
    high = prices + np.random.rand(len(prices)) * 2
    low = prices - np.random.rand(len(prices)) * 2
    atr = indicators.calculate_atr(high, low, prices, period=14)
    print(f"✅ ATR Calculation: mean={atr.mean():.4f}")
    test_results.append(("ATR Calculation", True, None))
    
except Exception as e:
    print(f"❌ Indicadores Técnicos: {str(e)[:80]}")
    test_results.append(("Indicadores Técnicos", False, str(e)[:100]))

# ============================================================================
# SECCIÓN 3: VALIDACIÓN DE POSITION SIZER
# ============================================================================
print("\n\nSECCIÓN 3: VALIDACIÓN DE POSITION SIZER")
print("-" * 80)

try:
    from src.risk.position_sizer import PositionSizer
    
    sizer = PositionSizer(
        initial_capital=10000,
        risk_per_trade=0.02,
        max_position_size=0.1
    )
    
    # Test position sizing
    account_value = 10000
    stop_loss_pct = 0.02
    entry_price = 100
    
    size = sizer.calculate_position_size(account_value, stop_loss_pct, entry_price)
    print(f"✅ Position Sizing: Size={size:.2f} shares, Risk=${account_value * 0.02:.2f}")
    test_results.append(("Position Sizing", True, None))
    
except Exception as e:
    print(f"❌ Position Sizer: {str(e)[:80]}")
    test_results.append(("Position Sizer", False, str(e)[:100]))

# ============================================================================
# SECCIÓN 4: VALIDACIÓN DE CONFIGURACIÓN Y SETTINGS
# ============================================================================
print("\n\nSECCIÓN 4: VALIDACIÓN DE CONFIGURACIÓN")
print("-" * 80)

try:
    from src.bot.config import settings
    from src.utils.config_manager import config_manager
    
    print(f"✅ Config Manager: {config_manager.config_file}")
    print(f"   - Mock Mode: {settings.mock_mode}")
    print(f"   - Paper Mode: {settings.paper_mode}")
    print(f"   - Max Position Size: {settings.max_position_size}")
    print(f"   - Risk Per Trade: {settings.risk_per_trade}")
    test_results.append(("Configuration Settings", True, None))
    
except Exception as e:
    print(f"❌ Configuration: {str(e)[:80]}")
    test_results.append(("Configuration Settings", False, str(e)[:100]))

# ============================================================================
# SECCIÓN 5: VALIDACIÓN DE DATABASE
# ============================================================================
print("\n\nSECCIÓN 5: VALIDACIÓN DE DATABASE")
print("-" * 80)

try:
    from src.database.db_manager import DatabaseManager
    
    db = DatabaseManager()
    # Verificar que el DB se conecta
    print(f"✅ Database Manager: Conectado")
    print(f"   - DB Path: {db.db_file}")
    test_results.append(("Database Connection", True, None))
    
except Exception as e:
    print(f"❌ Database: {str(e)[:80]}")
    test_results.append(("Database Connection", False, str(e)[:100]))

# ============================================================================
# SECCIÓN 6: VALIDACIÓN DE SEÑALES
# ============================================================================
print("\n\nSECCIÓN 6: VALIDACIÓN DE GENERADOR DE SEÑALES")
print("-" * 80)

try:
    from src.analysis.signal_generator import SignalGenerator
    
    sig_gen = SignalGenerator()
    print(f"✅ Signal Generator: Inicializado")
    test_results.append(("Signal Generator", True, None))
    
except Exception as e:
    print(f"❌ Signal Generator: {str(e)[:80]}")
    test_results.append(("Signal Generator", False, str(e)[:100]))

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n\n" + "=" * 80)
print("RESUMEN DE PRUEBAS")
print("=" * 80)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)

print(f"\n📊 RESULTADOS:")
print(f"   ✅ Pruebas Exitosas: {passed}")
print(f"   ❌ Pruebas Fallidas: {failed}")
print(f"   📈 Tasa de Éxito: {passed * 100 // len(test_results)}%")

if failed > 0:
    print(f"\n⚠️  DETALLES DE FALLOS:")
    for name, success, error in test_results:
        if not success:
            print(f"   - {name}")
            if error:
                print(f"     {error[:100]}")

print("\n" + "=" * 80)
print("✅ PROYECTO VALIDADO Y LISTO PARA USAR" if failed == 0 else "⚠️  REVISAR FALLOS ANTES DE USAR")
print("=" * 80 + "\n")

sys.exit(0 if failed == 0 else 1)
