"""
Script de prueba rápida para verificar MockIOLClient
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.mock_iol_client import MockIOLClient

# Crear cliente
client = MockIOLClient("test", "test", "https://mock.iol")

# Autenticar
print("🔧 Autenticando...")
auth_result = client.authenticate()
print(f"Resultado autenticación: {auth_result}")

# Obtener precio
print("\n🔧 Obteniendo precio de GGAL...")
quote = client.get_last_price("GGAL", "bCBA")
print(f"Quote completo: {quote}")

if quote:
    price = quote.get('price')
    print(f"\n✅ Precio extraído: ${price}")
else:
    print("\n❌ Quote es None!")

# Intentar con otros símbolos
for symbol in ['YPFD', 'BMA', 'CEPU']:
    print(f"\n🔧 Probando {symbol}...")
    q = client.get_last_price(symbol, "bCBA")
    if q:
        print(f"  ✅ ${q.get('price')}")
    else:
        print(f"  ❌ None")
