"""
Technical Indicators
Cálculo de indicadores técnicos usando la librería 'ta'
"""

import pandas as pd
from typing import Dict
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


class TechnicalIndicators:
    """Calculador de indicadores técnicos"""
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calcula el RSI (Relative Strength Index)
        
        Args:
            df: DataFrame con columna 'close'
            period: Período del RSI (default: 14)
        
        Returns:
            Series con valores de RSI (0-100)
        """
        rsi = RSIIndicator(close=df['close'], window=period)
        return rsi.rsi()
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame, 
        fast: int = 12, 
        slow: int = 26, 
        signal: int = 9
    ) -> pd.DataFrame:
        """
        Calcula el MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame con columna 'close'
            fast: Período EMA rápida (default: 12)
            slow: Período EMA lenta (default: 26)
            signal: Período de señal (default: 9)
        
        Returns:
            DataFrame con columnas: macd, macd_signal, macd_hist
        """
        macd_indicator = MACD(
            close=df['close'],
            window_slow=slow,
            window_fast=fast,
            window_sign=signal
        )
        
        result = pd.DataFrame()
        result['macd'] = macd_indicator.macd()
        result['macd_signal'] = macd_indicator.macd_signal()
        result['macd_hist'] = macd_indicator.macd_diff()
        
        return result
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calcula el ATR (Average True Range) - medida de volatilidad
        
        Args:
            df: DataFrame con columnas 'high', 'low', 'close'
            period: Período del ATR (default: 14)
        
        Returns:
            Series con valores de ATR
        """
        atr = AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=period
        )
        return atr.average_true_range()
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame, 
        period: int = 20, 
        std: float = 2.0
    ) -> pd.DataFrame:
        """
        Calcula Bandas de Bollinger
        
        Args:
            df: DataFrame con columna 'close'
            period: Período de la media móvil (default: 20)
            std: Desviaciones estándar (default: 2.0)
        
        Returns:
            DataFrame con columnas: bb_lower, bb_middle, bb_upper
        """
        bb = BollingerBands(
            close=df['close'],
            window=period,
            window_dev=std
        )
        
        result = pd.DataFrame()
        result['bb_lower'] = bb.bollinger_lband()
        result['bb_middle'] = bb.bollinger_mavg()
        result['bb_upper'] = bb.bollinger_hband()
        
        return result
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calcula SMA (Simple Moving Average)
        
        Args:
            df: DataFrame con columna 'close'
            period: Período de la media (default: 20)
        
        Returns:
            Series con valores de SMA
        """
        sma = SMAIndicator(close=df['close'], window=period)
        return sma.sma_indicator()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calcula EMA (Exponential Moving Average)
        
        Args:
            df: DataFrame con columna 'close'
            period: Período de la media (default: 20)
        
        Returns:
            Series con valores de EMA
        """
        ema = EMAIndicator(close=df['close'], window=period)
        return ema.ema_indicator()
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos los indicadores principales
        
        Args:
            df: DataFrame con columnas OHLCV
        
        Returns:
            DataFrame con todos los indicadores agregados
        """
        result = df.copy()
        
        # RSI
        result['rsi'] = TechnicalIndicators.calculate_rsi(df)
        
        # MACD
        macd = TechnicalIndicators.calculate_macd(df)
        result['macd'] = macd['macd']
        result['macd_signal'] = macd['macd_signal']
        result['macd_hist'] = macd['macd_hist']
        
        # ATR
        result['atr'] = TechnicalIndicators.calculate_atr(df)
        
        # Bollinger Bands
        bbands = TechnicalIndicators.calculate_bollinger_bands(df)
        result['bb_lower'] = bbands['bb_lower']
        result['bb_middle'] = bbands['bb_middle']
        result['bb_upper'] = bbands['bb_upper']
        
        # Moving Averages
        result['sma_20'] = TechnicalIndicators.calculate_sma(df, 20)
        result['sma_50'] = TechnicalIndicators.calculate_sma(df, 50)
        result['ema_12'] = TechnicalIndicators.calculate_ema(df, 12)
        result['ema_26'] = TechnicalIndicators.calculate_ema(df, 26)
        
        return result
    
    @staticmethod
    def get_latest_indicators(df: pd.DataFrame) -> Dict:
        """
        Obtiene los valores más recientes de todos los indicadores
        
        Args:
            df: DataFrame con indicadores calculados
        
        Returns:
            Dict con valores actuales de indicadores
        """
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        latest = df_with_indicators.iloc[-1]
        
        return {
            'price': latest['close'],
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'macd_signal': latest['macd_signal'],
            'macd_hist': latest['macd_hist'],
            'atr': latest['atr'],
            'bb_lower': latest['bb_lower'],
            'bb_middle': latest['bb_middle'],
            'bb_upper': latest['bb_upper'],
            'sma_20': latest['sma_20'],
            'sma_50': latest['sma_50'],
            'ema_12': latest['ema_12'],
            'ema_26': latest['ema_26']
        }
