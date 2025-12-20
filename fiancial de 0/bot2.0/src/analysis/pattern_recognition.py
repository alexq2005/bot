"""
Pattern Recognition
Detecta patrones de velas japonesas (candlestick patterns)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class CandlestickPatterns:
    """
    Reconocimiento de patrones de velas japonesas
    Detecta patrones alcistas y bajistas comunes
    """
    
    @staticmethod
    def detect_doji(
        open_price: float,
        close_price: float,
        high_price: float,
        low_price: float,
        threshold: float = 0.001
    ) -> bool:
        """
        Detecta patrón Doji
        Vela con cuerpo muy pequeño (apertura ≈ cierre)
        
        Args:
            threshold: Porcentaje máximo de diferencia entre apertura y cierre
            
        Returns:
            True si es un Doji
        """
        body = abs(close_price - open_price)
        range_price = high_price - low_price
        
        if range_price == 0:
            return False
        
        return (body / range_price) <= threshold
    
    @staticmethod
    def detect_hammer(
        open_price: float,
        close_price: float,
        high_price: float,
        low_price: float
    ) -> bool:
        """
        Detecta patrón Hammer (alcista)
        Cuerpo pequeño en la parte superior, sombra inferior larga
        
        Returns:
            True si es un Hammer
        """
        body = abs(close_price - open_price)
        range_price = high_price - low_price
        
        if range_price == 0:
            return False
        
        # Cuerpo en el tercio superior
        body_position = min(open_price, close_price) - low_price
        
        # Sombra inferior debe ser al menos 2x el cuerpo
        lower_shadow = min(open_price, close_price) - low_price
        upper_shadow = high_price - max(open_price, close_price)
        
        return (
            lower_shadow >= 2 * body and
            upper_shadow <= body and
            body_position >= 0.6 * range_price
        )
    
    @staticmethod
    def detect_shooting_star(
        open_price: float,
        close_price: float,
        high_price: float,
        low_price: float
    ) -> bool:
        """
        Detecta patrón Shooting Star (bajista)
        Cuerpo pequeño en la parte inferior, sombra superior larga
        
        Returns:
            True si es un Shooting Star
        """
        body = abs(close_price - open_price)
        range_price = high_price - low_price
        
        if range_price == 0:
            return False
        
        # Sombra superior debe ser al menos 2x el cuerpo
        upper_shadow = high_price - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low_price
        
        # Cuerpo en el tercio inferior
        body_position = max(open_price, close_price) - low_price
        
        return (
            upper_shadow >= 2 * body and
            lower_shadow <= body and
            body_position <= 0.4 * range_price
        )
    
    @staticmethod
    def detect_engulfing(
        prev_open: float,
        prev_close: float,
        curr_open: float,
        curr_close: float
    ) -> Optional[str]:
        """
        Detecta patrón Engulfing (envolvente)
        
        Returns:
            'bullish' para envolvente alcista
            'bearish' para envolvente bajista
            None si no hay patrón
        """
        # Bullish Engulfing: vela bajista seguida de vela alcista más grande
        if prev_close < prev_open and curr_close > curr_open:
            if curr_close >= prev_open and curr_open <= prev_close:
                return 'bullish'
        
        # Bearish Engulfing: vela alcista seguida de vela bajista más grande
        if prev_close > prev_open and curr_close < curr_open:
            if curr_close <= prev_open and curr_open >= prev_close:
                return 'bearish'
        
        return None
    
    @staticmethod
    def detect_morning_star(
        open_1: float,
        close_1: float,
        high_1: float,
        low_1: float,
        open_2: float,
        close_2: float,
        high_2: float,
        low_2: float,
        open_3: float,
        close_3: float,
        high_3: float,
        low_3: float
    ) -> bool:
        """
        Detecta patrón Morning Star (alcista, 3 velas)
        1. Vela bajista larga
        2. Vela pequeña (puede ser alcista o bajista)
        3. Vela alcista larga
        
        Returns:
            True si es un Morning Star
        """
        # Primera vela: bajista
        if close_1 >= open_1:
            return False
        
        # Segunda vela: pequeña (gap down)
        body_2 = abs(close_2 - open_2)
        body_1 = abs(close_1 - open_1)
        
        if body_2 > 0.3 * body_1:  # Cuerpo debe ser pequeño
            return False
        
        # Tercera vela: alcista
        if close_3 <= open_3:
            return False
        
        body_3 = abs(close_3 - open_3)
        
        # Vela 3 debe cerrar por encima del 50% de vela 1
        midpoint_1 = (open_1 + close_1) / 2
        
        return close_3 > midpoint_1
    
    @staticmethod
    def detect_evening_star(
        open_1: float,
        close_1: float,
        high_1: float,
        low_1: float,
        open_2: float,
        close_2: float,
        high_2: float,
        low_2: float,
        open_3: float,
        close_3: float,
        high_3: float,
        low_3: float
    ) -> bool:
        """
        Detecta patrón Evening Star (bajista, 3 velas)
        1. Vela alcista larga
        2. Vela pequeña (puede ser alcista o bajista)
        3. Vela bajista larga
        
        Returns:
            True si es un Evening Star
        """
        # Primera vela: alcista
        if close_1 <= open_1:
            return False
        
        # Segunda vela: pequeña (gap up)
        body_2 = abs(close_2 - open_2)
        body_1 = abs(close_1 - open_1)
        
        if body_2 > 0.3 * body_1:
            return False
        
        # Tercera vela: bajista
        if close_3 >= open_3:
            return False
        
        # Vela 3 debe cerrar por debajo del 50% de vela 1
        midpoint_1 = (open_1 + close_1) / 2
        
        return close_3 < midpoint_1


class PatternRecognizer:
    """
    Reconocedor de patrones en datos históricos
    Identifica patrones de velas en un DataFrame
    """
    
    def __init__(self):
        self.patterns = CandlestickPatterns()
    
    def scan_patterns(self, df: pd.DataFrame) -> Dict[str, List]:
        """
        Escanea todos los patrones en el DataFrame
        
        Args:
            df: DataFrame con columnas OHLC
            
        Returns:
            Dict con listas de índices donde se encontraron patrones
        """
        results = {
            'doji': [],
            'hammer': [],
            'shooting_star': [],
            'bullish_engulfing': [],
            'bearish_engulfing': [],
            'morning_star': [],
            'evening_star': []
        }
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Patrones de 1 vela
            if self.patterns.detect_doji(
                row['open'], row['close'], row['high'], row['low']
            ):
                results['doji'].append(i)
            
            if self.patterns.detect_hammer(
                row['open'], row['close'], row['high'], row['low']
            ):
                results['hammer'].append(i)
            
            if self.patterns.detect_shooting_star(
                row['open'], row['close'], row['high'], row['low']
            ):
                results['shooting_star'].append(i)
            
            # Patrones de 2 velas
            if i > 0:
                prev_row = df.iloc[i-1]
                engulfing = self.patterns.detect_engulfing(
                    prev_row['open'], prev_row['close'],
                    row['open'], row['close']
                )
                
                if engulfing == 'bullish':
                    results['bullish_engulfing'].append(i)
                elif engulfing == 'bearish':
                    results['bearish_engulfing'].append(i)
            
            # Patrones de 3 velas
            if i > 1:
                row_1 = df.iloc[i-2]
                row_2 = df.iloc[i-1]
                row_3 = df.iloc[i]
                
                if self.patterns.detect_morning_star(
                    row_1['open'], row_1['close'], row_1['high'], row_1['low'],
                    row_2['open'], row_2['close'], row_2['high'], row_2['low'],
                    row_3['open'], row_3['close'], row_3['high'], row_3['low']
                ):
                    results['morning_star'].append(i)
                
                if self.patterns.detect_evening_star(
                    row_1['open'], row_1['close'], row_1['high'], row_1['low'],
                    row_2['open'], row_2['close'], row_2['high'], row_2['low'],
                    row_3['open'], row_3['close'], row_3['high'], row_3['low']
                ):
                    results['evening_star'].append(i)
        
        return results
    
    def get_recent_patterns(
        self,
        df: pd.DataFrame,
        lookback: int = 10
    ) -> Dict[str, bool]:
        """
        Obtiene patrones en las últimas N velas
        
        Args:
            df: DataFrame con columnas OHLC
            lookback: Número de velas a revisar
            
        Returns:
            Dict con patrones encontrados (True/False)
        """
        all_patterns = self.scan_patterns(df.tail(lookback))
        
        # Simplificar a True/False
        return {
            pattern: len(indices) > 0
            for pattern, indices in all_patterns.items()
        }
    
    def get_pattern_signal(self, df: pd.DataFrame) -> str:
        """
        Genera señal basada en patrones recientes
        
        Args:
            df: DataFrame con columnas OHLC
            
        Returns:
            'BULLISH', 'BEARISH', o 'NEUTRAL'
        """
        recent = self.get_recent_patterns(df, lookback=5)
        
        bullish_count = sum([
            recent.get('hammer', False),
            recent.get('bullish_engulfing', False),
            recent.get('morning_star', False)
        ])
        
        bearish_count = sum([
            recent.get('shooting_star', False),
            recent.get('bearish_engulfing', False),
            recent.get('evening_star', False)
        ])
        
        if bullish_count > bearish_count:
            return 'BULLISH (Patrones alcistas detectados)'
        elif bearish_count > bullish_count:
            return 'BEARISH (Patrones bajistas detectados)'
        else:
            return 'NEUTRAL (Sin patrones claros)'
