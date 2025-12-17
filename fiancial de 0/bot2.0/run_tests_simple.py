"""
Master Test Runner - Versión Simplificada
Script para ejecutar todos los tests del proyecto
"""

import sys
from pathlib import Path
import subprocess
import os

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("\n" + "=" * 80)
print("TEST SUITE - PROYECTO BOT TRADING v2.0")
print("=" * 80)

base_path = Path(__file__).parent

# Tests a ejecutar
tests = [
    ("IOL Connection", "tests/test_iol_connection.py"),
    ("Market Manager", "tests/test_market_manager.py"),
    ("Technical Indicators", "tests/test_indicators.py"),
    ("Risk Manager", "tests/test_risk_manager.py"),
    ("Database", "tests/test_database.py"),
    ("Trading Bot", "tests/test_trading_bot.py"),
]

results = []

for test_name, test_file in tests:
    test_path = base_path / test_file
    
    if not test_path.exists():
        print(f"\nFAIL: {test_name} - Archivo no encontrado: {test_file}")
        results.append((test_name, False))
        continue
    
    print(f"\nEjecutando: {test_name}...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[:200])
        
        success = result.returncode == 0
        results.append((test_name, success))
        
        status = "PASS" if success else "FAIL"
        print(f"Status: {status}")
        
    except subprocess.TimeoutExpired:
        print(f"FAIL: {test_name} - Timeout")
        results.append((test_name, False))
    except Exception as e:
        print(f"FAIL: {test_name} - {str(e)[:100]}")
        results.append((test_name, False))

# Resumen final
print("\n\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

passed = sum(1 for _, s in results if s)
total = len(results)

print(f"\nPASADOS: {passed}/{total}")
print(f"FALLIDOS: {total - passed}/{total}")

if total > 0:
    percentage = (passed * 100) // total
    print(f"TASA DE EXITO: {percentage}%")

if total - passed > 0:
    print("\nTests que fallaron:")
    for name, success in results:
        if not success:
            print(f"  - {name}")

print("\n" + "=" * 80)

if passed == total:
    print("RESULTADO: TODOS LOS TESTS PASARON")
    print("El proyecto esta listo para usar")
else:
    print(f"RESULTADO: {total - passed} tests fallaron")
    print("Por favor revisar los errores arriba")

print("=" * 80 + "\n")

sys.exit(0 if passed == total else 1)
