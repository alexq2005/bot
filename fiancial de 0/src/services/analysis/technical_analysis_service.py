"""
Servicio de Análisis Técnico
Implementa indicadores técnicos reales usando Pandas nativo (Sin dependencias pesadas):
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA/EMA (Moving Averages)
"""

import logging
from typing import Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

# Intentar importar pandas_ta opcionalmente (no es requerido, usamos implementaciones nativas)
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    # No es crítico, usamos implementaciones nativas de pandas

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    """Servicio de análisis técnico completo usando Pandas nativo"""
    
    def __init__(self):
        logger.info("📊 Inicializando Servicio de Análisis Técnico (Native Pandas)")
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        if data is None or data.empty:
            logger.warning(f"No hay datos para analizar en {symbol}")
            return self._empty_result(symbol)

        # Normalizar columnas
        df = self._normalize_columns(data)
        
        if len(df) < 26: # Mínimo para MACD
             logger.warning(f"Datos insuficientes para {symbol} ({len(df)} filas)")
             return self._empty_result(symbol)

        try:
            # Calcular Indicadores Nativos
            close = df['close']

            # 1. RSI (14)
            rsi_series = self._calculate_rsi(close, 14)
            current_rsi = rsi_series.iloc[-1]

            # 2. MACD (12, 26, 9)
            macd_line, signal_line, macd_hist = self._calculate_macd(close, 12, 26, 9)
            macd = macd_line.iloc[-1]
            macd_signal = signal_line.iloc[-1]
            hist_val = macd_hist.iloc[-1]

            # 3. Bollinger Bands (20, 2)
            upper, middle, lower = self._calculate_bbands(close, 20, 2)
            bb_upper = upper.iloc[-1]
            bb_middle = middle.iloc[-1]
            bb_lower = lower.iloc[-1]

            # 4. EMAs
            ema_50_series = self._calculate_ema(close, 50)
            ema_200_series = self._calculate_ema(close, 200)
            ema_50 = ema_50_series.iloc[-1] if not ema_50_series.empty else None
            ema_200 = ema_200_series.iloc[-1] if not ema_200_series.empty else None

            # Generar señal
            signal = self._generate_signal(current_rsi, macd, macd_signal, close.iloc[-1], bb_lower, bb_upper)

            logger.info(f"Análisis {symbol}: RSI={current_rsi:.2f}, Signal={signal}")

            return {
                "symbol": symbol,
                "price": close.iloc[-1],
                "rsi": round(float(current_rsi), 2),
                "macd": {
                    "value": round(float(macd), 4),
                    "signal": round(float(macd_signal), 4),
                    "hist": round(float(hist_val), 4)
                },
                "bollinger_bands": {
                    "upper": round(float(bb_upper), 2),
                    "middle": round(float(bb_middle), 2),
                    "lower": round(float(bb_lower), 2)
                },
                "trends": {
                    "ema_50": round(float(ema_50), 2) if ema_50 is not None else None,
                    "ema_200": round(float(ema_200), 2) if ema_200 is not None else None
                },
                "signal": signal,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculando indicadores para {symbol}: {e}")
            return self._empty_result(symbol)

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_ema(self, series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    def _calculate_macd(self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        exp1 = self._calculate_ema(series, fast)
        exp2 = self._calculate_ema(series, slow)
        macd = exp1 - exp2
        sig = self._calculate_ema(macd, signal)
        hist = macd - sig
        return macd, sig, hist

    def _calculate_bbands(self, series: pd.Series, length: int = 20, std: int = 2):
        ma = series.rolling(window=length).mean()
        sd = series.rolling(window=length).std()
        upper = ma + (sd * std)
        lower = ma - (sd * std)
        return upper, ma, lower

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        # Convertir a minúsculas
        df.columns = [c.lower() for c in df.columns]
        
        mapping = {
            'cierre': 'close',
            'apertura': 'open',
            'maximo': 'high',
            'minimo': 'low',
            'volumen': 'volume',
            'ultimo': 'close',
            'ultimoprecio': 'close',
            'last_price': 'close',
            'fecha': 'date',
            'fechahora': 'date'
        }
        new_df = df.rename(columns=mapping)
        
        # Log columns for debug if 'close' missing
        if 'close' not in new_df.columns:
            logger.warning(f"Columnas disponibles: {new_df.columns.tolist()}")
            
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in new_df.columns:
                new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
        return new_df

    def _generate_signal(self, rsi, macd, macd_signal, price, bb_lower, bb_upper) -> str:
        score = 0
        if rsi < 30: score += 1
        elif rsi > 70: score -= 1
        
        if macd > macd_signal: score += 1
        elif macd < macd_signal: score -= 1
        
        if price <= bb_lower: score += 1
        elif price >= bb_upper: score -= 1
        
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
