"""
Logger Configuration
Sistema de logging estructurado
"""

import os
import sys
from datetime import datetime
import logging

# Usar logging estándar de Python en lugar de loguru para evitar problemas de encoding
def setup_logger(log_level: str = "INFO", log_file: str = "./logs/bot.log"):
    """
    Configura el sistema de logging
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta del archivo de logs
    """
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger('TradingBot')
    logger.setLevel(getattr(logging, log_level))
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_formatter = logging.Formatter(
        '[%(levelname)s] [%(asctime)s] %(name)s:%(funcName)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level))
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Agregar handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"[OK] Logger configurado - Nivel: {log_level}, Archivo: {log_file}")
    
    return logger


# Instancia global del logger
log = setup_logger()

