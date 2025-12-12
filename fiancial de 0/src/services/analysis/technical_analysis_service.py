"""
Servicio de Análisis Técnico

Implementa indicadores técnicos reales usando pandas-ta:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA/EMA (Moving Averages)
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
import pandas as pd
import pandas_ta as ta

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Servicio de análisis técnico completo usando pandas-ta"""
    
    def __init__(self):
        """Inicializa el servicio de análisis técnico"""
        logger.info("📊 Inicializando Servicio de Análisis Técnico")
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Realiza análisis técnico completo de un símbolo.
        
        Args:
            symbol: Símbolo a analizar
            data: DataFrame con datos históricos (debe tener columnas: open, high, low, close, volume)
                  Las columnas pueden estar en español (apertura, cierre, etc) y se renombrarán.
            
        Returns:
            Diccionario con resultados del análisis
        """
        if data is None or data.empty:
            logger.warning(f"No hay datos para analizar en {symbol}")
            return self._empty_result(symbol)

        # Normalizar columnas para pandas-ta
        df = self._normalize_columns(data)
        
        if len(df) < 20: # Mínimo necesario para algunos indicadores
             logger.warning(f"Datos insuficientes para {symbol} ({len(df)} filas)")
             return self._empty_result(symbol)

        try:
            # 1. RSI (14)
            df.ta.rsi(length=14, append=True)
            current_rsi = df['RSI_14'].iloc[-1]

            # 2. MACD (12, 26, 9)
            df.ta.macd(fast=12, slow=26, signal=9, append=True)
            macd = df['MACD_12_26_9'].iloc[-1]
            macd_signal = df['MACDs_12_26_9'].iloc[-1]
            macd_hist = df['MACDh_12_26_9'].iloc[-1]

            # 3. Bollinger Bands (20, 2)
            df.ta.bbands(length=20, std=2, append=True)
            bb_upper = df['BBU_20_2.0'].iloc[-1]
            bb_middle = df['BBM_20_2.0'].iloc[-1]
            bb_lower = df['BBL_20_2.0'].iloc[-1]

            # 4. EMAs
            df.ta.ema(length=50, append=True)
            df.ta.ema(length=200, append=True)
            ema_50 = df['EMA_50'].iloc[-1]
            ema_200 = df['EMA_200'].iloc[-1] if 'EMA_200' in df.columns else None

            # Generar señal básica
            signal = self._generate_signal(current_rsi, macd, macd_signal, df['close'].iloc[-1], bb_lower, bb_upper)

            logger.info(f"Análisis {symbol}: RSI={current_rsi:.2f}, Signal={signal}")

            return {
                "symbol": symbol,
                "price": df['close'].iloc[-1],
                "rsi": round(current_rsi, 2),
                "macd": {
                    "value": round(macd, 4),
                    "signal": round(macd_signal, 4),
                    "hist": round(macd_hist, 4)
                },
                "bollinger_bands": {
                    "upper": round(bb_upper, 2),
                    "middle": round(bb_middle, 2),
                    "lower": round(bb_lower, 2)
                },
                "trends": {
                    "ema_50": round(ema_50, 2) if ema_50 else None,
                    "ema_200": round(ema_200, 2) if ema_200 else None
                },
                "signal": signal,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculando indicadores para {symbol}: {e}")
            return self._empty_result(symbol)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza nombres de columnas a formato inglés estándar"""
        # Mapeo de columnas IOL/Español a Inglés
        mapping = {
            'cierre': 'close',
            'apertura': 'open',
            'maximo': 'high',
            'minimo': 'low',
            'volumen': 'volume',
            'ultimo': 'close', # A veces viene como ultimo
            'last_price': 'close'
        }

        new_df = df.rename(columns=mapping)

        # Asegurarse que sean floats
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in new_df.columns:
                new_df[col] = pd.to_numeric(new_df[col], errors='coerce')

        return new_df

    def _generate_signal(self, rsi, macd, macd_signal, price, bb_lower, bb_upper) -> str:
        """Lógica simple para generar señales de compra/venta"""
        score = 0

        # RSI
        if rsi < 30: score += 1 # Sobrevendido -> Compra
        elif rsi > 70: score -= 1 # Sobrecomprado -> Venta

        # MACD
        if macd > macd_signal: score += 1 # Cruce alcista
        elif macd < macd_signal: score -= 1 # Cruce bajista

        # BB
        if price <= bb_lower: score += 1 # Precio bajo banda inferior -> Rebote probable
        elif price >= bb_upper: score -= 1 # Precio sobre banda superior -> Corrección probable

        if score >= 2: return "STRONG_BUY"
        if score == 1: return "BUY"
        if score <= -2: return "STRONG_SELL"
        if score == -1: return "SELL"
        return "HOLD"

    def _empty_result(self, symbol):
        return {
            "symbol": symbol,
            "rsi": None,
            "macd": None,
            "bollinger_bands": None,
            "signal": "HOLD"
        }

# Exportar servicio
__all__ = ['TechnicalAnalysisService']
