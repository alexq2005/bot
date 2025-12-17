"""
Gestor de Configuraciones Óptimas
Almacena y recupera parámetros óptimos encontrados por el optimizador
"""

import json
import os
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

class OptimalConfigManager:
    """Gestiona configuraciones óptimas por símbolo"""
    
    def __init__(self, config_file: str = "data/optimal_configs.json"):
        self.config_file = config_file
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Crea el archivo si no existe"""
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def save_config(self, symbol: str, config: Dict[str, Any], metrics: Dict[str, float]):
        """
        Guarda configuración óptima para un símbolo
        
        Args:
            symbol: Símbolo del activo (ej: "GGAL")
            config: Parámetros óptimos {"rsi_buy": 30, "rsi_sell": 70, ...}
            metrics: Métricas de performance {"return_pct": 25.5, "sharpe": 1.8, ...}
        """
        configs = self.load_all()
        
        configs[symbol] = {
            "parameters": config,
            "metrics": metrics,
            "updated_at": datetime.now().isoformat(),
            "backtest_period": metrics.get("period", "unknown")
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(configs, f, indent=2)
            
    def get_config(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene configuración óptima para un símbolo
        
        Returns:
            Dict con 'parameters' y 'metrics', o None si no existe
        """
        configs = self.load_all()
        return configs.get(symbol)
    
    def load_all(self) -> Dict[str, Dict]:
        """Carga todas las configuraciones"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
            
    def get_parameters(self, symbol: str, defaults: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene solo los parámetros para un símbolo, con fallback a defaults
        
        Args:
            symbol: Símbolo del activo
            defaults: Valores por defecto si no hay config guardada
            
        Returns:
            Dict con parámetros
        """
        config = self.get_config(symbol)
        if config and "parameters" in config:
            return config["parameters"]
        return defaults or {}


# Singleton global
optimal_config_manager = OptimalConfigManager()
