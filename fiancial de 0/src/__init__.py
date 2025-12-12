"""Paquete principal del bot"""

__version__ = "1.1.0"
__author__ = "Equipo de Desarrollo"
__description__ = "IOL Quantum AI Trading Bot"

from .services import (
    TechnicalAnalysisService,
    IOLClient,
    AdvancedLearningSystem
)

__all__ = [
    'TechnicalAnalysisService',
    'IOLClient',
    'AdvancedLearningSystem'
]
