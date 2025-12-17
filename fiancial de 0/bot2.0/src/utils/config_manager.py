"""
Configuration Manager
Gestiona configuraciones dinámicas del bot (símbolos, parámetros, etc.)
"""

import json
import os
from typing import List, Optional, Any
from pathlib import Path

class ConfigManager:
    """Gestor de configuración dinámica del bot"""
    
    def __init__(self, config_file: str = "data/bot_config.json"):
        self.config_file = config_file
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Crea el archivo de configuración si no existe"""
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.config_file):
            default_config = {
                "mode": "mock",
                "symbol_categories": [],
                "max_symbols": 10,
                "risk_per_trade": 2.0
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def _load(self) -> dict:
        """Carga configuraciones del archivo"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save(self, config: dict):
        """Guarda configuraciones al archivo"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración"""
        config = self._load()
        return config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Establece un valor de configuración"""
        try:
            config = self._load()
            config[key] = value
            self._save(config)
            return True
        except Exception:
            return False
    
    def get_max_symbols(self) -> int:
        """Obtiene el número máximo de símbolos"""
        return self.get('max_symbols', 10)
    
    def set_max_symbols(self, value: int):
        """Establece el número máximo de símbolos"""
        return self.set('max_symbols', value)
    
    def get_symbol_categories(self) -> List[str]:
        """Obtiene las categorías de símbolos seleccionadas"""
        return self.get('symbol_categories', [])
    
    def set_symbol_categories(self, categories: List[str]) -> bool:
        """Establece las categorías de símbolos"""
        return self.set('symbol_categories', categories)
    
    def get_mode(self) -> str:
        """Obtiene el modo de operación"""
        return self.get('mode', 'mock')
    
    def set_mode(self, mode: str) -> bool:
        """Establece el modo de operación"""
        return self.set('mode', mode)
    
    def update(self, config_updates: dict) -> bool:
        """Actualiza múltiples valores de configuración a la vez"""
        try:
            config = self._load()
            config.update(config_updates)
            self._save(config)
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False

# Singleton global
config_manager = ConfigManager()
