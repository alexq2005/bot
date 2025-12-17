#!/usr/bin/env python3
"""
Monitor de cambios en tiempo real para app.py
Detecta y reporta cambios automáticamente
"""

import os
import time
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

class AppMonitor:
    def __init__(self, filepath="src/dashboard/app.py"):
        self.filepath = Path(filepath).resolve()
        self.last_hash = None
        self.last_lines = 0
        self.change_count = 0
        
    def get_hash(self):
        """Calcula hash del archivo"""
        if not self.filepath.exists():
            return None
        with open(self.filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def get_lines(self):
        """Cuenta líneas del archivo"""
        if not self.filepath.exists():
            return 0
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    
    def show_last_lines(self, n=10):
        """Muestra las últimas n líneas"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-n:]
                for i, line in enumerate(lines, len(f.readlines()) - n + 1):
                    print(f"  {i:4d}: {line.rstrip()}")
        except:
            pass
    
    def check_syntax(self):
        """Verifica sintaxis de Python"""
        try:
            result = subprocess.run(
                ['python', '-m', 'py_compile', str(self.filepath)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, "✅ Sintaxis válida"
            else:
                return False, f"❌ Error de sintaxis: {result.stderr[:100]}"
        except:
            return None, "⚠️ No se pudo verificar"
    
    def monitor(self, interval=3):
        """Monitorea cambios continuamente"""
        print("🔍 MONITOR DE CAMBIOS ACTIVADO")
        print(f"📁 Archivo: {self.filepath}")
        print(f"⏱️ Intervalo: {interval}s")
        print("=" * 80)
        
        self.last_hash = self.get_hash()
        self.last_lines = self.get_lines()
        
        try:
            while True:
                time.sleep(interval)
                
                current_hash = self.get_hash()
                current_lines = self.get_lines()
                
                if current_hash is None:
                    print(f"⚠️ [{self.timestamp()}] Archivo no encontrado")
                    continue
                
                if current_hash != self.last_hash:
                    self.change_count += 1
                    line_diff = current_lines - self.last_lines
                    
                    print(f"\n{'='*80}")
                    print(f"✏️  CAMBIO #{self.change_count} detectado [{self.timestamp()}]")
                    print(f"{'='*80}")
                    print(f"📊 Líneas: {self.last_lines} → {current_lines} ({line_diff:+d})")
                    print(f"📦 Tamaño: {os.path.getsize(self.filepath)} bytes")
                    
                    # Verificar sintaxis
                    valid, msg = self.check_syntax()
                    print(f"{msg}")
                    
                    print(f"\n📋 Últimas 8 líneas modificadas:")
                    print("-" * 80)
                    self.show_last_lines(8)
                    print("-" * 80)
                    print()
                    
                    self.last_hash = current_hash
                    self.last_lines = current_lines
        
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Monitoreo detenido")
            print(f"📊 Total de cambios detectados: {self.change_count}")
    
    def timestamp(self):
        return datetime.now().strftime('%H:%M:%S')

if __name__ == "__main__":
    monitor = AppMonitor()
    monitor.monitor(interval=2)
