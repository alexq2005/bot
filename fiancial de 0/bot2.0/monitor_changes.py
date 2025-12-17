#!/usr/bin/env python3
"""
Monitor de cambios en app.py
Rastreia cambios en tiempo real en el archivo del dashboard
"""

import subprocess
import time
import os
from datetime import datetime

def get_file_hash(filepath):
    """Obtiene hash MD5 del archivo"""
    import hashlib
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def show_git_diff(filepath):
    """Muestra el diff de git del archivo"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--no-index', 'HEAD', filepath],
            cwd=os.path.dirname(filepath),
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
    except:
        pass

def monitor_file(filepath, check_interval=5):
    """Monitorea cambios en un archivo"""
    filepath = os.path.abspath(filepath)
    
    if not os.path.exists(filepath):
        print(f"❌ Archivo no encontrado: {filepath}")
        return
    
    print(f"📁 Monitoreando: {filepath}")
    print(f"⏱️ Intervalo de verificación: {check_interval}s")
    print("=" * 80)
    print("Presiona Ctrl+C para detener\n")
    
    last_hash = get_file_hash(filepath)
    last_modified = os.path.getmtime(filepath)
    
    try:
        while True:
            time.sleep(check_interval)
            
            if not os.path.exists(filepath):
                print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Archivo eliminado")
                break
            
            current_hash = get_file_hash(filepath)
            current_modified = os.path.getmtime(filepath)
            
            if current_hash != last_hash:
                print(f"\n✏️ [{datetime.now().strftime('%H:%M:%S')}] CAMBIOS DETECTADOS")
                print(f"📊 Tamaño actual: {os.path.getsize(filepath)} bytes")
                print("-" * 80)
                
                # Mostrar últimas 5 líneas
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    print("📋 Últimas 5 líneas modificadas:")
                    for line in lines[-5:]:
                        print(f"   {line.rstrip()}")
                print("-" * 80 + "\n")
                
                last_hash = current_hash
                last_modified = current_modified
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoreo detenido")

if __name__ == "__main__":
    app_path = "src/dashboard/app.py"
    monitor_file(app_path)
