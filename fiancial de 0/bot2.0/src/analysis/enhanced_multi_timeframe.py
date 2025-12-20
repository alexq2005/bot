"""
Enhanced Multi-Timeframe Analysis
Integración con indicadores técnicos para análisis multi-timeframe
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from src.analysis.technical_indicators import TechnicalIndicators


class EnhancedMultiTimeframeAnalyzer:
    """
    Analizador multi-timeframe mejorado
    Utiliza indicadores técnicos en múltiples marcos temporales
    """
    
    def __init__(self):
        self.indicators_calc = TechnicalIndicators()
        self.timeframes = {
            '1D': '1D',   # Daily
            '4H': '4h',   # 4 hours (lowercase h)
            '1H': '1h',   # 1 hour (lowercase h)
        }
    
    def resample_to_timeframe(
        self,
        df: pd.DataFrame,
        timeframe: str
    ) -> pd.DataFrame:
        """
        Resamplea datos a un timeframe específico
        
        Args:
            df: DataFrame con datos OHLCV y columna 'date' como datetime
            timeframe: '1D', '4H', '1H'
            
        Returns:
            DataFrame resampleado
        """
        df_copy = df.copy()
        
        # Asegurar que date es datetime
        if 'date' in df_copy.columns:
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            df_copy = df_copy.set_index('date')
        elif not isinstance(df_copy.index, pd.DatetimeIndex):
            raise ValueError("DataFrame debe tener índice datetime o columna 'date'")
        
        # Resamplear OHLCV
        resampled = df_copy.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        resampled = resampled.reset_index()
        
        return resampled
    
    def analyze_timeframe(
        self,
        df: pd.DataFrame,
        timeframe: str
    ) -> Dict:
        """
        Analiza un timeframe específico con todos los indicadores
        
        Args:
            df: DataFrame con datos originales
            timeframe: Timeframe a analizar ('1D', '4H', '1H')
            
        Returns:
            Dict con análisis completo del timeframe
        """
        try:
            # Resamplear si no es diario
            if timeframe != '1D':
                df_tf = self.resample_to_timeframe(df, timeframe)
            else:
                df_tf = df.copy()
            
            # Calcular indicadores
            signals = self.indicators_calc.get_trading_signals(df_tf)
            latest = self.indicators_calc.get_latest_indicators(df_tf)
            
            # Calcular score de señal
            score = self._calculate_signal_score(signals)
            
            return {
                'timeframe': timeframe,
                'price': latest['price'],
                'rsi': latest['rsi'],
                'macd': latest['macd'],
                'adx': latest['adx'],
                'signals': signals,
                'signal_score': score,
                'trend': self._determine_trend(signals, latest),
                'data_points': len(df_tf)
            }
        except Exception as e:
            return {
                'timeframe': timeframe,
                'error': str(e),
                'signal_score': 0
            }
    
    def analyze_all_timeframes(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Dict]:
        """
        Analiza todos los timeframes disponibles
        
        Args:
            df: DataFrame con datos diarios (mínimo 90 días recomendado)
            
        Returns:
            Dict con análisis de cada timeframe
        """
        results = {}
        
        for tf_name, tf_code in self.timeframes.items():
            results[tf_name] = self.analyze_timeframe(df, tf_code)
        
        return results
    
    def get_multi_timeframe_consensus(
        self,
        timeframe_results: Dict[str, Dict]
    ) -> Dict:
        """
        Obtiene consenso entre timeframes
        
        Args:
            timeframe_results: Resultados de analyze_all_timeframes
            
        Returns:
            Dict con señal de consenso
        """
        # Pesos: más importancia a timeframes largos
        weights = {
            '1D': 0.5,
            '4H': 0.3,
            '1H': 0.2
        }
        
        # Calcular señal ponderada
        weighted_score = 0
        total_weight = 0
        
        signals_by_tf = {}
        
        for tf, result in timeframe_results.items():
            if 'error' in result:
                continue
            
            weight = weights.get(tf, 0.33)
            score = result.get('signal_score', 0)
            
            weighted_score += score * weight
            total_weight += weight
            
            signals_by_tf[tf] = {
                'score': score,
                'trend': result.get('trend', 'NEUTRAL'),
                'rsi': result.get('rsi', 50),
                'adx': result.get('adx', 0)
            }
        
        if total_weight == 0:
            consensus_score = 0
        else:
            consensus_score = weighted_score / total_weight
        
        # Determinar señal final
        if consensus_score >= 2:
            final_signal = 'STRONG BUY'
        elif consensus_score >= 1:
            final_signal = 'BUY'
        elif consensus_score <= -2:
            final_signal = 'STRONG SELL'
        elif consensus_score <= -1:
            final_signal = 'SELL'
        else:
            final_signal = 'NEUTRAL'
        
        # Calcular alineación
        trend_counts = {}
        for tf_data in signals_by_tf.values():
            trend = tf_data['trend']
            trend_counts[trend] = trend_counts.get(trend, 0) + 1
        
        max_trend_count = max(trend_counts.values()) if trend_counts else 0
        alignment = max_trend_count / len(signals_by_tf) if signals_by_tf else 0
        
        return {
            'consensus_signal': final_signal,
            'consensus_score': consensus_score,
            'alignment': alignment,
            'timeframe_signals': signals_by_tf,
            'recommendation': self._get_recommendation(final_signal, alignment)
        }
    
    def _calculate_signal_score(self, signals: Dict[str, str]) -> int:
        """Calcula score de señal (-5 a +5)"""
        score = 0
        
        # RSI
        if 'COMPRA' in signals.get('rsi_signal', ''):
            score += 2
        elif 'VENTA' in signals.get('rsi_signal', ''):
            score -= 2
        
        # MACD
        if 'COMPRA' in signals.get('macd_signal', ''):
            score += 2
        elif 'VENTA' in signals.get('macd_signal', ''):
            score -= 2
        
        # Stochastic
        if 'COMPRA' in signals.get('stoch_signal', ''):
            score += 1
        elif 'VENTA' in signals.get('stoch_signal', ''):
            score -= 1
        
        return score
    
    def _determine_trend(self, signals: Dict, latest: Dict) -> str:
        """Determina la tendencia general"""
        adx = latest.get('adx', 0)
        
        if adx < 25:
            return 'SIDEWAYS'
        
        # Usar señales para determinar dirección
        bullish = sum([
            'COMPRA' in signals.get('rsi_signal', ''),
            'COMPRA' in signals.get('macd_signal', ''),
            'COMPRA' in signals.get('stoch_signal', '')
        ])
        
        bearish = sum([
            'VENTA' in signals.get('rsi_signal', ''),
            'VENTA' in signals.get('macd_signal', ''),
            'VENTA' in signals.get('stoch_signal', '')
        ])
        
        if bullish > bearish:
            return 'UPTREND'
        elif bearish > bullish:
            return 'DOWNTREND'
        else:
            return 'NEUTRAL'
    
    def _get_recommendation(self, signal: str, alignment: float) -> str:
        """Genera recomendación basada en señal y alineación"""
        if alignment < 0.5:
            return "⚠️ Señales contradictorias - ESPERAR confirmación"
        
        if signal == 'STRONG BUY' and alignment >= 0.7:
            return "🟢 COMPRA FUERTE - Todos los timeframes alineados"
        elif signal == 'BUY':
            return "🟢 COMPRA - Señal alcista predominante"
        elif signal == 'STRONG SELL' and alignment >= 0.7:
            return "🔴 VENTA FUERTE - Todos los timeframes alineados"
        elif signal == 'SELL':
            return "🔴 VENTA - Señal bajista predominante"
        else:
            return "🔵 MANTENER - Sin señal clara"
