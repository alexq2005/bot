"""
Market Screener
Escanea múltiples activos y filtra por señales de trading
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.analysis.technical_indicators import TechnicalIndicators


class MarketScreener:
    """
    Escáner de mercado para múltiples activos
    Filtra y compara activos basados en indicadores y señales
    """
    
    def __init__(self):
        self.indicators_calc = TechnicalIndicators()
        self.results = []
    
    def scan_symbols(
        self,
        symbols: List[str],
        historical_data_dict: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Escanea múltiples símbolos y retorna resultados
        
        Args:
            symbols: Lista de símbolos a escanear
            historical_data_dict: Dict con datos históricos por símbolo
            
        Returns:
            DataFrame con resultados del escaneo
        """
        results = []
        
        for symbol in symbols:
            if symbol not in historical_data_dict:
                continue
                
            df = historical_data_dict[symbol]
            
            if df is None or len(df) < 50:  # Mínimo de datos
                continue
            
            try:
                # Calcular indicadores
                signals = self.indicators_calc.get_trading_signals(df)
                latest = self.indicators_calc.get_latest_indicators(df)
                
                # Calcular score de señal
                signal_score = self._calculate_signal_score(signals)
                
                result = {
                    'symbol': symbol,
                    'price': latest['price'],
                    'rsi': latest['rsi'],
                    'macd': latest['macd'],
                    'stoch_k': latest['stoch_k'],
                    'adx': latest['adx'],
                    'rsi_signal': signals['rsi_signal'],
                    'macd_signal': signals['macd_signal'],
                    'stoch_signal': signals['stoch_signal'],
                    'trend_strength': signals['trend_strength'],
                    'signal_score': signal_score,
                    'timestamp': datetime.now()
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"Error escaneando {symbol}: {e}")
                continue
        
        self.results = results
        return pd.DataFrame(results)
    
    def _calculate_signal_score(self, signals: Dict[str, str]) -> int:
        """
        Calcula un score de señal (-5 a +5)
        +5 = Muy alcista, -5 = Muy bajista
        """
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
    
    def filter_by_signal(
        self,
        signal_type: str = 'buy',
        min_score: int = 2
    ) -> pd.DataFrame:
        """
        Filtra resultados por tipo de señal
        
        Args:
            signal_type: 'buy', 'sell', o 'neutral'
            min_score: Score mínimo (para buy) o máximo (para sell)
            
        Returns:
            DataFrame filtrado
        """
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        
        if signal_type == 'buy':
            return df[df['signal_score'] >= min_score].sort_values('signal_score', ascending=False)
        elif signal_type == 'sell':
            return df[df['signal_score'] <= -min_score].sort_values('signal_score', ascending=True)
        else:  # neutral
            return df[df['signal_score'].abs() < min_score]
    
    def filter_by_rsi(
        self,
        condition: str = 'oversold',
        threshold: float = 30
    ) -> pd.DataFrame:
        """
        Filtra por condiciones de RSI
        
        Args:
            condition: 'oversold', 'overbought', o 'neutral'
            threshold: Umbral de RSI
            
        Returns:
            DataFrame filtrado
        """
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        
        if condition == 'oversold':
            return df[df['rsi'] < threshold].sort_values('rsi')
        elif condition == 'overbought':
            return df[df['rsi'] > (100 - threshold)].sort_values('rsi', ascending=False)
        else:  # neutral
            return df[(df['rsi'] >= threshold) & (df['rsi'] <= (100 - threshold))]
    
    def filter_by_trend_strength(
        self,
        min_adx: float = 25
    ) -> pd.DataFrame:
        """
        Filtra por fuerza de tendencia (ADX)
        
        Args:
            min_adx: ADX mínimo para considerar tendencia fuerte
            
        Returns:
            DataFrame con activos en tendencia fuerte
        """
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        return df[df['adx'] >= min_adx].sort_values('adx', ascending=False)
    
    def get_top_opportunities(
        self,
        n: int = 10,
        direction: str = 'both'
    ) -> pd.DataFrame:
        """
        Obtiene las mejores oportunidades de trading
        
        Args:
            n: Número de oportunidades a retornar
            direction: 'buy', 'sell', o 'both'
            
        Returns:
            DataFrame con mejores oportunidades
        """
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        
        if direction == 'buy':
            return df.nlargest(n, 'signal_score')
        elif direction == 'sell':
            return df.nsmallest(n, 'signal_score')
        else:  # both
            # Tomar los n/2 mejores buy y n/2 mejores sell
            buy_ops = df.nlargest(n // 2, 'signal_score')
            sell_ops = df.nsmallest(n // 2, 'signal_score')
            return pd.concat([buy_ops, sell_ops]).sort_values('signal_score', ascending=False)
    
    def get_summary(self) -> Dict:
        """
        Obtiene un resumen del escaneo
        
        Returns:
            Dict con estadísticas del escaneo
        """
        if not self.results:
            return {
                'total_scanned': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'neutral_signals': 0
            }
        
        df = pd.DataFrame(self.results)
        
        return {
            'total_scanned': len(df),
            'buy_signals': len(df[df['signal_score'] >= 2]),
            'sell_signals': len(df[df['signal_score'] <= -2]),
            'neutral_signals': len(df[df['signal_score'].abs() < 2]),
            'avg_rsi': df['rsi'].mean(),
            'avg_adx': df['adx'].mean(),
            'strong_trends': len(df[df['adx'] >= 25]),
            'timestamp': datetime.now()
        }
