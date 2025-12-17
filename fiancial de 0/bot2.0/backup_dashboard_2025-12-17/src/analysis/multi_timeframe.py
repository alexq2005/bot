"""
Multi-Timeframe Analysis
Análisis en múltiples marcos temporales para mejor precisión
"""

import pandas as pd
from typing import Dict, List, Literal
from ..analysis.signal_generator import SignalGenerator


TimeFrame = Literal["5min", "1h", "1d"]


class MultiTimeframeAnalyzer:
    """Analizador multi-timeframe"""
    
    def __init__(self):
        """Inicializa el analizador"""
        self.signal_generators = {
            "5min": SignalGenerator(rsi_oversold=25, rsi_overbought=75),  # Más agresivo
            "1h": SignalGenerator(rsi_oversold=30, rsi_overbought=70),    # Estándar
            "1d": SignalGenerator(rsi_oversold=35, rsi_overbought=65)     # Más conservador
        }
    
    def resample_data(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Resamplea datos a un timeframe específico
        
        Args:
            df: DataFrame con datos OHLCV
            timeframe: '5min', '1h', '1d'
        
        Returns:
            DataFrame resampleado
        """
        # Asegurar que date es el índice
        df_copy = df.copy()
        if 'date' in df_copy.columns:
            df_copy = df_copy.set_index('date')
        
        # Mapeo de timeframes
        freq_map = {
            "5min": "5T",
            "1h": "1H",
            "1d": "1D"
        }
        
        freq = freq_map.get(timeframe, "1D")
        
        # Resamplear
        resampled = df_copy.resample(freq).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # Resetear índice
        resampled = resampled.reset_index()
        
        return resampled
    
    def analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """
        Analiza un timeframe específico
        
        Args:
            df: DataFrame con datos
            timeframe: Timeframe a analizar
        
        Returns:
            Dict con señal y detalles
        """
        # Resamplear si es necesario
        if timeframe != "1d":
            df_resampled = self.resample_data(df, timeframe)
        else:
            df_resampled = df
        
        # Generar señal
        signal_gen = self.signal_generators[timeframe]
        signal = signal_gen.generate_signal(df_resampled)
        
        return {
            "timeframe": timeframe,
            "signal": signal["signal"],
            "confidence": signal["confidence"],
            "strength": signal["strength"],
            "indicators": signal["indicators"]
        }
    
    def analyze_all_timeframes(self, df: pd.DataFrame) -> Dict:
        """
        Analiza todos los timeframes
        
        Args:
            df: DataFrame con datos diarios
        
        Returns:
            Dict con análisis de todos los timeframes
        """
        results = {}
        
        for timeframe in ["5min", "1h", "1d"]:
            try:
                results[timeframe] = self.analyze_timeframe(df, timeframe)
            except Exception as e:
                print(f"⚠ Error analizando timeframe {timeframe}: {e}")
                results[timeframe] = {
                    "timeframe": timeframe,
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "strength": 0.0
                }
        
        return results
    
    def get_consensus_signal(self, timeframe_results: Dict) -> Dict:
        """
        Obtiene señal de consenso entre timeframes
        
        Args:
            timeframe_results: Resultados de todos los timeframes
        
        Returns:
            Dict con señal de consenso
        """
        # Pesos por timeframe (más peso a timeframes largos)
        weights = {
            "5min": 0.2,
            "1h": 0.3,
            "1d": 0.5
        }
        
        # Contar votos ponderados
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        for timeframe, result in timeframe_results.items():
            signal = result["signal"]
            weight = weights.get(timeframe, 0.33)
            confidence = result["confidence"]
            
            votes[signal] += weight * confidence
        
        # Determinar señal ganadora
        max_votes = max(votes.values())
        winning_signals = [sig for sig, v in votes.items() if v == max_votes]
        
        if len(winning_signals) > 1:
            final_signal = "HOLD"
            consensus_strength = 0.0
        else:
            final_signal = winning_signals[0]
            consensus_strength = votes[final_signal] / sum(votes.values())
        
        # Verificar alineación
        signals_list = [r["signal"] for r in timeframe_results.values()]
        alignment = len([s for s in signals_list if s == final_signal]) / len(signals_list)
        
        return {
            "signal": final_signal,
            "consensus_strength": consensus_strength,
            "alignment": alignment,
            "timeframe_signals": {
                tf: r["signal"] for tf, r in timeframe_results.items()
            },
            "votes": votes
        }
