"""
ENV Manager
Gestiona cambios en el archivo .env
"""

import os
from pathlib import Path
from typing import Dict


class EnvManager:
    """
    Gestor del archivo .env
    Permite modificar variables de entorno
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Inicializa el gestor
        
        Args:
            env_file: Ruta al archivo .env
        """
        self.env_file = env_file
    
    def read_env(self) -> Dict[str, str]:
        """
        Lee el archivo .env
        
        Returns:
            Dict con variables de entorno
        """
        env_vars = {}
        
        if not os.path.exists(self.env_file):
            return env_vars
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Ignorar comentarios y líneas vacías
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parsear variable
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        except Exception as e:
            print(f"Error leyendo .env: {e}")
        
        return env_vars
    
    def write_env(self, env_vars: Dict[str, str]) -> bool:
        """
        Escribe el archivo .env
        
        Args:
            env_vars: Dict con variables de entorno
        
        Returns:
            True si se escribió correctamente
        """
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error escribiendo .env: {e}")
            return False
    
    def update_env(self, updates: Dict[str, str]) -> bool:
        """
        Actualiza variables en .env
        
        Args:
            updates: Dict con variables a actualizar
        
        Returns:
            True si se actualizó correctamente
        """
        env_vars = self.read_env()
        env_vars.update(updates)
        return self.write_env(env_vars)
    
    def set_mode(self, mode: str) -> bool:
        """
        Establece modo de operación
        
        Args:
            mode: 'mock', 'paper', 'live'
        
        Returns:
            True si se actualizó correctamente
        """
        if mode == 'mock':
            updates = {
                'MOCK_MODE': 'True',
                'PAPER_MODE': 'False'
            }
        elif mode == 'paper':
            updates = {
                'MOCK_MODE': 'False',
                'PAPER_MODE': 'True'
            }
        elif mode == 'live':
            updates = {
                'MOCK_MODE': 'False',
                'PAPER_MODE': 'False'
            }
        else:
            return False
        
        return self.update_env(updates)


# Instancia global
env_manager = EnvManager()
