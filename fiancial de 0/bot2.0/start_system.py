"""
🚀 Launcher del Sistema IOL Trading Bot v2.0
============================================
Este script inicia:
1. El Dashboard (Streamlit) para visualización y control manual.
2. El Listener de Telegram para control remoto (/start_bot, /stop_bot).

Uso: python start_system.py
"""
import subprocess
import time
import os
import signal
import sys

def main():
    print("="*60)
    print("   🚀 INICIANDO ECOSISTEMA IOL TRADING BOT v2.0")
    print("="*60)
    
    # 1. Iniciar Telegram Listener (Servicio de Control Remoto)
    print("\n📡 Iniciando Servicio de Telegram...")
    telegram_process = subprocess.Popen(
        [sys.executable, "src/services/telegram_listener.py"],
        cwd=os.getcwd(),
        shell=True
    )
    
    # 2. Iniciar Dashboard (Interfaz Visual)
    print("\n🖥️  Iniciando Dashboard...")
    dashboard_process = subprocess.Popen(
        ["streamlit", "run", "src/dashboard/app.py"],
        cwd=os.getcwd(),
        shell=True
    )
    
    print("\n✅ SISTEMA CORRIENDO")
    print("   - Dashboard: http://localhost:8501")
    print("   - Telegram:  Esperando comandos (/help)")
    print("\n[Presiona Ctrl+C para detener todo]")

    try:
        while True:
            time.sleep(1)
            
            # Verificar si se cayeron
            if telegram_process.poll() is not None:
                print("❌ Error: El servicio de Telegram se detuvo.")
                break
            if dashboard_process.poll() is not None:
                print("❌ Error: El Dashboard se detuvo.")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        
        # Matar procesos
        try:
            # En Windows subprocess.kill() a veces no mata el árbol de procesos shell=True
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(dashboard_process.pid)])
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(telegram_process.pid)])
        except Exception as e:
            print(f"Error matando procesos: {e}")
            
        print("Hasta luego. 👋")

if __name__ == "__main__":
    main()
