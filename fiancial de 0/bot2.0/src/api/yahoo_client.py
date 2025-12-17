"""
Yahoo Finance Client
Cliente para obtener datos históricos y de mercado desde Yahoo Finance.
Se utiliza como fuente secundaria de datos y para backtesting.
"""

import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import warnings

# Silenciar warnings de yfinance
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
yf.pdr_override()  # Silencia otros warnings

logger = logging.getLogger(__name__)
# Reducir verbosidad de yfinance
logging.getLogger('yfinance').setLevel(logging.ERROR)

class YahooClient:
    """
    Cliente wrapper para yfinance.
    Maneja la conversión de símbolos y la obtención de datos.
    """
    
    def __init__(self):
        self.suffix_ba = ".BA"  # Proporciona datos de BCBA
        
    def _format_symbol(self, symbol: str, market: str = "BCBA") -> str:
        """
        Formatea el símbolo para Yahoo Finance.
        Ej: GGAL -> GGAL.BA (para Buenos Aires)
            GGAL -> GGAL (para ADR en USA)
        """
        symbol = symbol.upper().strip()
        
        # Si ya tiene punto, asumimos que está formateado (ej: GGAL.BA)
        if "." in symbol:
            return symbol
            
        if market == "BCBA":
            return f"{symbol}{self.suffix_ba}"
        return symbol

    def get_historical_data(self, 
                          symbol: str, 
                          period: str = "1mo", 
                          interval: str = "1d",
                          market: str = "BCBA",
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Obtiene datos históricos (OHLCV).
        
        Args:
            symbol: Símbolo del activo (ej: GGAL)
            period: Periodo de historia ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max', 'ytd')
            interval: Intervalo de velas ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            market: 'BCBA' para local, 'USA' para ADRs
            start_date: Fecha de inicio (opcional, anula period)
            end_date: Fecha de fin (opcional, anula period)
            
        Returns:
            DataFrame con columnas: Open, High, Low, Close, Volume
        """
        yf_symbol = self._format_symbol(symbol, market)
        try:
            ticker = yf.Ticker(yf_symbol)
            
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No se encontraron datos para {yf_symbol}")
                return pd.DataFrame()
            
            # Limpieza y estandarización
            df.reset_index(inplace=True)
            
            # Renombrar columnas a minúsculas para compatibilidad con el resto del sistema
            df.rename(columns={
                "Date": "timestamp",
                "Datetime": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }, inplace=True)
            
            # Mantener solo columnas necesarias
            desired_cols = ["timestamp", "open", "high", "low", "close", "volume"]
            df = df[[c for c in desired_cols if c in df.columns]]
            
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de Yahoo para {yf_symbol}: {e}")
            return pd.DataFrame()

    def get_market_info(self, symbol: str, market: str = "BCBA") -> Dict[str, Any]:
        """Obtiene información fundamental y de mercado en tiempo real (con delay)."""
        yf_symbol = self._format_symbol(symbol, market)
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            return info
        except Exception as e:
            logger.error(f"Error obteniendo info de Yahoo para {yf_symbol}: {e}")
            return {}

    def get_ccl_price(self, symbol: str) -> Optional[float]:
        """
        Calcula el dólar CCL implícito usando el activo local vs ADR.
        Requiere que el activo tenga ADR (ej: GGAL, YPF, BMA, PAM).
        """
        try:
            # Precio Local (ARS) y ADR (USD)
            local_df = self.get_historical_data(symbol, period="1d", interval="1m", market="BCBA")
            adr_df = self.get_historical_data(symbol, period="1d", interval="1m", market="USA")
            if local_df.empty or adr_df.empty:
                return None

            last_local = float(local_df["close"].iloc[-1])
            last_adr = float(adr_df["close"].iloc[-1])
            if last_adr <= 0:
                return None

            # Factor de conversión (número de acciones locales por 1 ADR)
            conversion_factors = {
                "GGAL": 10,
                "BMA": 10,
                "YPFD": 1,
                "PAMP": 25,
                "CRES": 10,
                "EDN": 20,
                "TECO2": 5,
                "SUPV": 5,
                "BBAR": 3,
            }
            ratio = float(conversion_factors.get(symbol.upper(), 10))

            # Convención: CCL = (precio local en ARS / precio ADR en USD) * ratio
            return (last_local / last_adr) * ratio

        except Exception as e:
            logger.error(f"Error calculando CCL para {symbol}: {e}")
            return None

# Instancia global para uso fácil
yahoo_client = YahooClient()
