#!/usr/bin/env python
"""
Script wrapper para ejecutar mock en Windows con encoding UTF-8
"""

import os
import sys
import subprocess

# Configurar encoding UTF-8 para Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Ejecutar el script de mock
if __name__ == "__main__":
    import chcp
    # Cambiar página de códigos a UTF-8
    os.system("chcp 65001 > nul 2>&1")
    
    # Importar y ejecutar
    from run_mock_3days import run_mock_trading_session
    try:
        run_mock_trading_session()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
