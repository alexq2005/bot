from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # IOL Credentials
    IOL_USERNAME: Optional[str] = Field(None, description="IOL Username")
    IOL_PASSWORD: Optional[str] = Field(None, description="IOL Password")

    # Trading Configuration
    # Supports multiple symbols separated by comma, e.g., "GGAL,YPFD,PAMP"
    TRADING_SYMBOLS: List[str] = Field(["GGAL", "YPFD", "PAMP"], description="List of symbols to trade")
    TIMEFRAME: str = "15m" # Used for logging/reference, though pandas-ta works on DFs
    MOCK_MODE: bool = Field(True, description="Force Mock Mode if True or credentials missing")

    # API Keys for News
    NEWSDATA_API_KEY: Optional[str] = Field(None, env='NEWSDATA_API_KEY')
    FINNHUB_API_KEY: Optional[str] = Field(None, env='FINNHUB_API_KEY')
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(None, env='ALPHA_VANTAGE_API_KEY')
    NEWS_API_KEY: Optional[str] = Field(None, env='NEWS_API_KEY')

    # Strategy Parameters
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: int = 70
    RSI_OVERSOLD: int = 30
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9

    # Database
    DB_URL: str = "sqlite:///trades.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
