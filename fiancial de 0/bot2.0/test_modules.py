"""
Module Validation Test
Script para validar que todos los módulos principales se cargan correctamente
"""

import sys
import os
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=" * 70)
print("PRUEBAS DE VALIDACION DEL PROYECTO")
print("=" * 70 + "\n")

test_results = []

# Test 1: Config Module
print("Testing Bot Config...")
try:
    from src.bot.config import settings
    print("✅ Bot Config cargado correctamente")
    print(f"   - Mock Mode: {settings.mock_mode}")
    print(f"   - Paper Mode: {settings.paper_mode}\n")
    test_results.append(("Bot Config", True, None))
except Exception as e:
    print(f"❌ Bot Config: {str(e)}\n")
    test_results.append(("Bot Config", False, str(e)))

# Test 2: Mock IOL Client
print("Testing Mock IOL Client...")
try:
    from src.api.mock_iol_client import MockIOLClient
    client = MockIOLClient()
    print("✅ Mock IOL Client inicializado correctamente\n")
    test_results.append(("Mock IOL Client", True, None))
except Exception as e:
    print(f"❌ Mock IOL Client: {str(e)}\n")
    test_results.append(("Mock IOL Client", False, str(e)))

# Test 3: Technical Indicators
print("Testing Technical Indicators...")
try:
    from src.analysis.technical_indicators import TechnicalIndicators
    indicators = TechnicalIndicators()
    print("✅ Technical Indicators inicializado correctamente\n")
    test_results.append(("Technical Indicators", True, None))
except Exception as e:
    print(f"❌ Technical Indicators: {str(e)}\n")
    test_results.append(("Technical Indicators", False, str(e)))

# Test 4: Position Sizer
print("Testing Position Sizer...")
try:
    from src.risk.position_sizer import PositionSizer
    print("✅ Position Sizer importado correctamente\n")
    test_results.append(("Position Sizer", True, None))
except Exception as e:
    print(f"❌ Position Sizer: {str(e)}\n")
    test_results.append(("Position Sizer", False, str(e)))

# Test 5: Database Manager
print("Testing Database Manager...")
try:
    from src.database.db_manager import DatabaseManager
    print("✅ Database Manager importado correctamente\n")
    test_results.append(("Database Manager", True, None))
except Exception as e:
    print(f"❌ Database Manager: {str(e)}\n")
    test_results.append(("Database Manager", False, str(e)))

# Test 6: Trading Bot
print("Testing Trading Bot...")
try:
    from src.bot.trading_bot import TradingBot
    print("✅ Trading Bot importado correctamente\n")
    test_results.append(("Trading Bot", True, None))
except Exception as e:
    print(f"❌ Trading Bot: {str(e)}\n")
    test_results.append(("Trading Bot", False, str(e)))

# Test 7: Risk Manager
print("Testing Risk Manager...")
try:
    from src.risk.dynamic_risk_manager import DynamicRiskManager
    print("✅ Dynamic Risk Manager importado correctamente\n")
    test_results.append(("Risk Manager", True, None))
except Exception as e:
    print(f"❌ Risk Manager: {str(e)}\n")
    test_results.append(("Risk Manager", False, str(e)))

# Summary
print("=" * 70)
print("RESUMEN DE PRUEBAS")
print("=" * 70)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)

for name, success, error in test_results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {name}")
    if error:
        print(f"       Error: {error}")

print("\n" + "=" * 70)
print(f"RESULTADO: {passed}/{len(test_results)} pruebas pasaron correctamente")
print("=" * 70)

if failed > 0:
    sys.exit(1)
