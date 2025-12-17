
import os
import sys
import json
from dotenv import load_dotenv

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.api.iol_client import IOLClient

# Cargar env
load_dotenv()

username = os.getenv("IOL_USERNAME")
password = os.getenv("IOL_PASSWORD")

print(f"Probando conexión con usuario: {username}")

client = IOLClient(username, password, "https://api.invertironline.com")

if client.authenticate():
    print("✅ Autenticado correctamente")
    
    try:
        url = "https://api.invertironline.com/api/v2/estadocuenta"
        print(f"Consultando: {url}")
        resp = client.session.get(url)
        print(f"Status Code: {resp.status_code}")
        
        data = resp.json()
        print("\n--- RESPUESTA JSON ---")
        print(json.dumps(data, indent=2))
        print("----------------------\n")
        
    except Exception as e:
        print(f"❌ Error consultando saldo: {e}")

else:
    print("❌ Falló autenticación")
