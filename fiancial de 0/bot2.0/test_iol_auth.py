"""
Script para probar la autenticación con IOL
"""
import os
from dotenv import load_dotenv
import requests

# Cargar variables de entorno
load_dotenv()

username = os.getenv('IOL_USERNAME')
password = os.getenv('IOL_PASSWORD')
base_url = os.getenv('IOL_BASE_URL', 'https://api.invertironline.com')

print("=" * 70)
print("TEST DE AUTENTICACIÓN IOL")
print("=" * 70)
print(f"Usuario: {username}")
print(f"Password: {'*' * len(password) if password else 'NO CONFIGURADO'}")
print(f"Base URL: {base_url}")
print("=" * 70)

# Intentar autenticación
url = f"{base_url}/token"
payload = {
    "username": username,
    "password": password,
    "grant_type": "password"
}

print(f"\nIntentando autenticar en: {url}")
print(f"Payload: username={username}, grant_type=password")

try:
    response = requests.post(url, data=payload, timeout=10)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ AUTENTICACIÓN EXITOSA!")
        print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        print(f"Expira en: {data.get('expires_in', 'N/A')} segundos")
    else:
        print(f"\n❌ ERROR DE AUTENTICACIÓN")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 70)
print("POSIBLES SOLUCIONES:")
print("=" * 70)
print("1. Verifica que tu usuario y contraseña de IOL sean correctos")
print("2. Asegúrate de tener una cuenta activa en InvertirOnline.com")
print("3. Verifica que tu cuenta tenga acceso a la API")
print("4. Intenta iniciar sesión en https://www.invertironline.com")
print("5. Contacta al soporte de IOL para verificar acceso a API")
print("=" * 70)
