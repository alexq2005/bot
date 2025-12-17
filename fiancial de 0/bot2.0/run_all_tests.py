"""
Master Test Runner
Script para ejecutar todos los tests del proyecto
"""

import sys
from pathlib import Path
import subprocess
import time

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("\n" + "=" * 80)
print("🧪 SUITE COMPLETA DE TESTS - PROYECTO BOT TRADING v2.0")
print("=" * 80)
print(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80 + "\n")

tests_to_run = [
    ("IOL Connection Tests", "tests/test_iol_connection.py"),
    ("Market Manager Tests", "tests/test_market_manager.py"),
    ("Technical Indicators Tests", "tests/test_indicators.py"),
    ("Risk Manager Tests", "tests/test_risk_manager.py"),
    ("Database Tests", "tests/test_database.py"),
    ("Trading Bot Tests", "tests/test_trading_bot.py"),
]

base_path = Path(__file__).parent
all_results = []

for test_name, test_file in tests_to_run:
    print("\n" + "=" * 80)
    print(f"🧪 {test_name}")
    print("=" * 80)
    
    test_path = base_path / test_file
    
    if not test_path.exists():
        print(f"❌ Archivo no encontrado: {test_file}")
        all_results.append((test_name, False, "Archivo no encontrado"))
        continue
    
    try:
        # Ejecutar el test
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=False,
            timeout=120
        )
        
        success = result.returncode == 0
        all_results.append((test_name, success, None))
        
    except subprocess.TimeoutExpired:
        print(f"❌ Test timeout (>120s)")
        all_results.append((test_name, False, "Timeout"))
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        all_results.append((test_name, False, str(e)[:50]))

# Resumen final
print("\n\n" + "=" * 80)
print("📊 RESUMEN FINAL DE TESTS")
print("=" * 80)

passed = sum(1 for _, success, _ in all_results if success)
failed = sum(1 for _, success, _ in all_results if not success)

print(f"\n✅ Tests Exitosos: {passed}/{len(all_results)}")
print(f"❌ Tests Fallidos: {failed}/{len(all_results)}")
print(f"📈 Tasa de Éxito: {passed * 100 // len(all_results)}%")

if failed > 0:
    print(f"\n⚠️  TESTS FALLIDOS:")
    for name, success, error in all_results:
        if not success:
            print(f"   - {name}")
            if error:
                print(f"     {error}")

print("\n" + "=" * 80)

if failed == 0:
    print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
    print("🚀 EL PROYECTO ESTÁ LISTO PARA USAR")
else:
    print(f"⚠️  {failed} TEST(S) FALLARON - REVISAR ANTES DE USAR EN PRODUCCIÓN")

print("=" * 80 + "\n")

sys.exit(0 if failed == 0 else 1)
