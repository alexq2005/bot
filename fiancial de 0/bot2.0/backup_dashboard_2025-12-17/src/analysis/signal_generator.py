"""
Signal Generator
Genera señales de trading basadas en análisis técnico
"""

import pandas as pd
from typing import Dict, Optional, Literal
from .technical_indicators import TechnicalIndicators


SignalType = Literal["BUY", "SELL", "HOLD"]


class SignalGenerator:
    """Generador de señales de trading técnicas"""
    
    def __init__(
        self,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        use_macd: bool = True,
        use_bb: bool = True
    ):
        """
        Inicializa el generador de señales
        
        Args:
            rsi_oversold: Umbral de RSI sobrevendido (default: 30)
            rsi_overbought: Umbral de RSI sobrecomprado (default: 70)
            use_macd: Usar señales de MACD (default: True)
            use_bb: Usar señales de Bollinger Bands (default: True)
        """
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.use_macd = use_macd
        self.use_bb = use_bb
        self.ti = TechnicalIndicators()
    
    def analyze_rsi(self, rsi: float, oversold: float = None, overbought: float = None) -> Dict:
        """
        Analiza el RSI
        
        Args:
            rsi: Valor actual del RSI
            oversold: Umbral de sobreventa (usa self.rsi_oversold si None)
            overbought: Umbral de sobrecompra (usa self.rsi_overbought si None)
        
        Returns:
            Dict con señal y razón
        """
        oversold = oversold if oversold is not None else self.rsi_oversold
        overbought = overbought if overbought is not None else self.rsi_overbought
        
        if rsi < oversold:
            return {
                "signal": "BUY",
                "reason": f"RSI Sobrevendido ({rsi:.2f} < {oversold})",
                "strength": (oversold - rsi) / oversold  # 0-1
            }
        elif rsi > overbought:
            return {
                "signal": "SELL",
                "reason": f"RSI Sobrecomprado ({rsi:.2f} > {overbought})",
                "strength": (rsi - overbought) / (100 - overbought)
            }
        else:
            return {
                "signal": "HOLD",
                "reason": f"RSI Neutral ({rsi:.2f})",
                "strength": 0.0
            }
    
    def analyze_macd(self, macd: float, macd_signal: float, macd_hist: float) -> Dict:
        """
        Analiza el MACD
        
        Returns:
            Dict con señal y razón
        """
        # Cruce alcista: MACD cruza por encima de la señal
        if macd > macd_signal and macd_hist > 0:
            return {
                "signal": "BUY",
                "reason": "MACD Cruce Alcista",
                "strength": min(abs(macd_hist) / abs(macd), 1.0)
            }
        # Cruce bajista: MACD cruza por debajo de la señal
        elif macd < macd_signal and macd_hist < 0:
            return {
                "signal": "SELL",
                "reason": "MACD Cruce Bajista",
                "strength": min(abs(macd_hist) / abs(macd), 1.0)
            }
        else:
            return {
                "signal": "HOLD",
                "reason": "MACD Sin Señal Clara",
                "strength": 0.0
            }
    
    def analyze_bollinger_bands(
        self, 
        price: float, 
        bb_lower: float, 
        bb_upper: float,
        bb_middle: float
    ) -> Dict:
        """
        Analiza las Bandas de Bollinger
        
        Returns:
            Dict con señal y razón
        """
        # Precio toca banda inferior -> sobrevendido
        if price <= bb_lower:
            return {
                "signal": "BUY",
                "reason": "Precio en Banda Inferior de Bollinger",
                "strength": (bb_middle - price) / (bb_middle - bb_lower)
            }
        # Precio toca banda superior -> sobrecomprado
        elif price >= bb_upper:
            return {
                "signal": "SELL",
                "reason": "Precio en Banda Superior de Bollinger",
                "strength": (price - bb_middle) / (bb_upper - bb_middle)
            }
        else:
            return {
                "signal": "HOLD",
                "reason": "Precio Dentro de Bandas",
                "strength": 0.0
            }
    
    def generate_signal(self, df: pd.DataFrame, custom_params: dict = None) -> Dict:
        """
        Genera señal de trading basada en múltiples indicadores
        
        Args:
            df: DataFrame con datos OHLCV
            custom_params: Parámetros personalizados (ej: {'rsi_buy': 25, 'rsi_sell': 75})
        
        Returns:
            Dict con señal final y detalles
        """
        # Aplicar parámetros personalizados si existen
        rsi_oversold = custom_params.get('rsi_buy', self.rsi_oversold) if custom_params else self.rsi_oversold
        rsi_overbought = custom_params.get('rsi_sell', self.rsi_overbought) if custom_params else self.rsi_overbought
        
        # Calcular indicadores
        indicators = self.ti.get_latest_indicators(df)
        
        # Analizar cada indicador
        rsi_analysis = self.analyze_rsi(indicators['rsi'], rsi_oversold, rsi_overbought)
        
        signals = {
            "RSI": rsi_analysis
        }
        
        if self.use_macd:
            macd_analysis = self.analyze_macd(
                indicators['macd'],
                indicators['macd_signal'],
                indicators['macd_hist']
            )
            signals["MACD"] = macd_analysis
        
        if self.use_bb:
            bb_analysis = self.analyze_bollinger_bands(
                indicators['price'],
                indicators['bb_lower'],
                indicators['bb_upper'],
                indicators['bb_middle']
            )
            signals["BB"] = bb_analysis
        
        # Consenso: contar votos
        buy_votes = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        sell_votes = sum(1 for s in signals.values() if s['signal'] == 'SELL')
        total_signals = len(signals)
        
        # Fuerza promedio
        buy_strength = sum(s['strength'] for s in signals.values() if s['signal'] == 'BUY')
        sell_strength = sum(s['strength'] for s in signals.values() if s['signal'] == 'SELL')
        
        # Decisión final (requiere mayoría)
        if buy_votes > sell_votes and buy_votes >= total_signals / 2:
            final_signal = "BUY"
            confidence = buy_votes / total_signals
            avg_strength = buy_strength / buy_votes if buy_votes > 0 else 0
        elif sell_votes > buy_votes and sell_votes >= total_signals / 2:
            final_signal = "SELL"
            confidence = sell_votes / total_signals
            avg_strength = sell_strength / sell_votes if sell_votes > 0 else 0
        else:
            final_signal = "HOLD"
            confidence = 0.0
            avg_strength = 0.0
        
        return {
            "signal": final_signal,
            "confidence": confidence,
            "strength": avg_strength,
            "indicators": indicators,
            "individual_signals": signals,
            "votes": {
                "buy": buy_votes,
                "sell": sell_votes,
                "hold": total_signals - buy_votes - sell_votes
            }
        }
