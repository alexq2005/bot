#!/usr/bin/env python3
"""
Dashboard de Monitoreo en Vivo
Muestra cambios en app.py en tiempo real
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

def print_header():
    """Imprime encabezado del dashboard"""
    print("\033[2J\033[H")  # Limpia pantalla
    print("╔" + "═"*78 + "╗")
    print("║" + " DASHBOARD DE MONITOREO - app.py ".center(78) + "║")
    print("║" + f" Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".ljust(78) + "║")
    print("╚" + "═"*78 + "╝")

def get_file_stats():
    """Obtiene estadísticas del archivo"""
    app_path = "src/dashboard/app.py"
    
    if not os.path.exists(app_path):
        return None
    
    size = os.path.getsize(app_path)
    modified = os.path.getmtime(app_path)
    
    with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = len(f.readlines())
    
    return {
        'size': size,
        'lines': lines,
        'modified': datetime.fromtimestamp(modified),
        'path': app_path
    }

def check_syntax():
    """Verifica si el código es válido"""
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'src/dashboard/app.py'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def show_dashboard():
    """Muestra el dashboard"""
    while True:
        print_header()
        
        stats = get_file_stats()
        
        if stats:
            print(f"\n📁 ARCHIVO: {stats['path']}")
            print("─" * 80)
            print(f"   📊 Líneas de código:    {stats['lines']:,}")
            print(f"   📦 Tamaño:              {stats['size']:,} bytes")
            print(f"   ⏰ Última modificación: {stats['modified'].strftime('%H:%M:%S')}")
            
            # Sintaxis
            print("\n🔍 VALIDACIÓN:")
            print("─" * 80)
            is_valid = check_syntax()
            status = "✅ VÁLIDO" if is_valid else "❌ ERRORES"
            print(f"   {status}")
            
            # Info adicional
            print("\n📋 INFORMACIÓN:")
            print("─" * 80)
            print(f"   🎯 El dashboard está en monitoreo activo")
            print(f"   🔄 Auto-refresh cada 3 segundos")
            print(f"   💾 Cambios se guardan automáticamente")
            
            print("\n" + "═"*80)
            print("Presiona Ctrl+C para detener el monitoreo")
            print("="*80 + "\n")
        
        time.sleep(3)

if __name__ == "__main__":
    try:
        show_dashboard()
    except KeyboardInterrupt:
        print("\n\n✅ Monitoreo detenido")
