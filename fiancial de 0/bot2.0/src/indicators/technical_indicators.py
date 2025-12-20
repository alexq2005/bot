"""
Sistema de cálculo de indicadores técnicos
Soporta: RSI, MACD, Bandas de Bollinger
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

class TechnicalIndicators:
    """Calcula indicadores técnicos para análisis de trading"""
    
    def __init__(self):
        self.cache = {}
    
    def calculate_rsi(
        self, 
        prices: pd.Series, 
        period: int = 14
    ) -> pd.Series:
        """
        Calcula RSI (Relative Strength Index)
        
        Args:
            prices: Serie de precios de cierre
            period: Período para el cálculo (default: 14)
            
        Returns:
            Serie con valores de RSI (0-100)
        """
        rsi = RSIIndicator(close=prices, window=period)
        return rsi.rsi()
    
    def calculate_macd(
        self,
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """
        Calcula MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Serie de precios de cierre
            fast_period: Período EMA rápida (default: 12)
            slow_period: Período EMA lenta (default: 26)
            signal_period: Período línea de señal (default: 9)
            
        Returns:
            Dict con 'macd', 'signal', 'histogram'
        """
        macd = MACD(
            close=prices,
            window_fast=fast_period,
            window_slow=slow_period,
            window_sign=signal_period
        )
        
        return {
            'macd': macd.macd(),
            'signal': macd.macd_signal(),
            'histogram': macd.macd_diff()
        }
    
    def calculate_bollinger_bands(
        self,
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calcula Bandas de Bollinger
        
        Args:
            prices: Serie de precios de cierre
            period: Período para media móvil (default: 20)
            std_dev: Desviaciones estándar (default: 2.0)
            
        Returns:
            Dict con 'upper', 'middle', 'lower', 'bandwidth'
        """
        bb = BollingerBands(
            close=prices,
            window=period,
            window_dev=std_dev
        )
        
        return {
            'upper': bb.bollinger_hband(),
            'middle': bb.bollinger_mavg(),
            'lower': bb.bollinger_lband(),
            'bandwidth': bb.bollinger_wband()
        }
    
    def get_trading_signals(
        self,
        prices: pd.Series
    ) -> Dict[str, str]:
        """
        Genera señales de trading basadas en indicadores
        
        Returns:
            Dict con señales: 'rsi_signal', 'macd_signal', 'bb_signal'
        """
        signals = {}
        
        # RSI Signal
        rsi = self.calculate_rsi(prices)
        current_rsi = rsi.iloc[-1]
        if current_rsi < 30:
            signals['rsi_signal'] = 'COMPRA (Sobreventa)'
            signals['rsi_value'] = current_rsi
        elif current_rsi > 70:
            signals['rsi_signal'] = 'VENTA (Sobrecompra)'
            signals['rsi_value'] = current_rsi
        else:
            signals['rsi_signal'] = 'NEUTRAL'
            signals['rsi_value'] = current_rsi
        
        # MACD Signal
        macd_data = self.calculate_macd(prices)
        macd_current = macd_data['macd'].iloc[-1]
        signal_current = macd_data['signal'].iloc[-1]
        
        if macd_current > signal_current:
            signals['macd_signal'] = 'COMPRA (Cruce alcista)'
        elif macd_current < signal_current:
            signals['macd_signal'] = 'VENTA (Cruce bajista)'
        else:
            signals['macd_signal'] = 'NEUTRAL'
        
        # Bollinger Bands Signal
        bb = self.calculate_bollinger_bands(prices)
        current_price = prices.iloc[-1]
        upper = bb['upper'].iloc[-1]
        lower = bb['lower'].iloc[-1]
        
        if current_price < lower:
            signals['bb_signal'] = 'COMPRA (Precio bajo banda inferior)'
        elif current_price > upper:
            signals['bb_signal'] = 'VENTA (Precio sobre banda superior)'
        else:
            signals['bb_signal'] = 'NEUTRAL'
        
        return signals
    
    def calculate_all_indicators(
        self,
        prices: pd.Series
    ) -> Dict:
        """
        Calcula todos los indicadores de una vez
        
        Returns:
            Dict completo con todos los indicadores y señales
        """
        return {
            'rsi': self.calculate_rsi(prices),
            'macd': self.calculate_macd(prices),
            'bollinger': self.calculate_bollinger_bands(prices),
            'signals': self.get_trading_signals(prices)
        }
