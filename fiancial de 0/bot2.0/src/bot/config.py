"""
Configuration Management
Gestión centralizada de configuración usando Pydantic
"""

import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global del bot"""
    
    # ==================== MODE ====================
    mock_mode: bool = Field(default=True, description="Modo simulación (True) o real (False)")
    paper_mode: bool = Field(default=False, description="Modo paper trading (precios reales sin dinero)")
    
    def __init__(self, **kwargs):
        """Inicializa settings cargando primero de bot_config.json"""
        super().__init__(**kwargs)
        self._load_from_config_file()
    
    def _load_from_config_file(self):
        """Carga configuraciones de bot_config.json si existe"""
        import json
        from pathlib import Path
        
        config_file = Path("data/bot_config.json")
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Aplicar configuraciones del archivo
                if 'mode' in config:
                    mode = config['mode']
                    if mode == 'mock':
                        self.mock_mode = True
                        self.paper_mode = False
                    elif mode == 'paper':
                        self.mock_mode = False
                        self.paper_mode = True
                    elif mode == 'live':
                        self.mock_mode = False
                        self.paper_mode = False
                
                # Trading parameters
                if 'trading_interval' in config:
                    self.trading_interval = int(config['trading_interval'])
                
                if 'mock_initial_capital' in config:
                    self.mock_initial_capital = float(config['mock_initial_capital'])
                
                # Risk management
                if 'risk_per_trade' in config:
                    self.risk_per_trade = float(config['risk_per_trade'])
                
                if 'max_position_size' in config:
                    self.max_position_size = float(config['max_position_size'])
                
                if 'stop_loss' in config:
                    self.stop_loss_percent = float(config['stop_loss'])
                
                if 'take_profit' in config:
                    self.take_profit_percent = float(config['take_profit'])
                
                if 'max_symbols' in config:
                    self.max_symbols = int(config['max_symbols'])
                
                # ML parameters
                if 'use_rl_agent' in config:
                    self.use_rl_agent = bool(config['use_rl_agent'])
                
                if 'use_sentiment_analysis' in config:
                    self.use_sentiment_analysis = bool(config['use_sentiment_analysis'])
                
                if 'use_multi_timeframe' in config:
                    self.use_multi_timeframe = bool(config['use_multi_timeframe'])
                
                # Advanced systems
                if 'enable_hybrid_advanced' in config:
                    self.enable_hybrid_advanced = bool(config['enable_hybrid_advanced'])
                
                if 'enable_model_ensemble' in config:
                    self.enable_model_ensemble = bool(config['enable_model_ensemble'])
                
                if 'enable_regime_detection' in config:
                    self.enable_regime_detection = bool(config['enable_regime_detection'])
                
                if 'enable_dynamic_risk' in config:
                    self.enable_dynamic_risk = bool(config['enable_dynamic_risk'])
                
                print("[OK] Configuraciones cargadas de bot_config.json")
                
            except Exception as e:
                print(f"[WARNING] Error cargando bot_config.json: {e}")
    
    # ==================== IOL API ====================
    iol_username: str = Field(default="", description="Usuario de IOL")
    iol_password: str = Field(default="", description="Contraseña de IOL")
    iol_base_url: str = Field(
        default="https://api.invertironline.com",
        description="URL base de la API de IOL"
    )
    
    # ==================== NEWS APIs ====================
    newsdata_api_key: str = Field(default="", description="API key de NewsData.io")
    finnhub_api_key: str = Field(default="", description="API key de Finnhub")
    alphavantage_api_key: str = Field(default="", description="API key de Alpha Vantage")
    news_api_key: str = Field(default="", description="API key de NewsAPI.org")
    gnews_api_key: str = Field(default="", description="API key de GNews.io")
    
    # ==================== TRADING PARAMETERS ====================
    trading_symbols: str = Field(
        default="GGAL,YPFD,PAMP,ALUA,BMA",
        description="Lista de símbolos a operar (separados por coma)"
    )
    
    def get_trading_symbols_list(self) -> List[str]:
        """Obtiene la lista de símbolos parseada"""
        if isinstance(self.trading_symbols, str):
            return [s.strip() for s in self.trading_symbols.split(',')]
        return self.trading_symbols
    trading_interval: int = Field(
        default=300,
        description="Intervalo de trading en segundos (300 = 5 min)"
    )
    mock_initial_capital: float = Field(
        default=1000000.0,
        description="Capital inicial en modo MOCK (ARS)"
    )
    
    # ==================== RISK MANAGEMENT ====================
    risk_per_trade: float = Field(
        default=2.0,
        description="Porcentaje de riesgo por operación"
    )
    max_position_size: float = Field(
        default=20.0,
        description="Máximo porcentaje de portafolio por activo"
    )
    stop_loss_percent: float = Field(
        default=5.0,
        description="Stop loss porcentual"
    )
    take_profit_percent: float = Field(
        default=10.0,
        description="Take profit porcentual"
    )
    max_symbols: int = Field(
        default=20,
        description="Máximo número de símbolos a monitorear"
    )
    
    # ==================== ML PARAMETERS ====================
    use_rl_agent: bool = Field(
        default=True,
        description="Activar agente de Reinforcement Learning"
    )
    use_sentiment_analysis: bool = Field(
        default=True,
        description="Activar análisis de sentimiento"
    )
    use_multi_timeframe: bool = Field(
        default=True,
        description="Activar análisis multi-timeframe"
    )
    retrain_frequency_days: int = Field(
        default=7,
        description="Frecuencia de reentrenamiento en días"
    )
    
    # ==================== DYNAMIC RISK ====================
    enable_dynamic_risk: bool = Field(
        default=True,
        description="Activar auto-ajuste dinámico de riesgo"
    )
    dynamic_risk_adjustment_days: int = Field(
        default=7,
        description="Frecuencia de ajuste de riesgo en días"
    )
    min_risk_per_trade: float = Field(
        default=0.5,
        description="Riesgo mínimo por trade"
    )
    max_risk_per_trade: float = Field(
        default=5.0,
        description="Riesgo máximo por trade"
    )
    
    # ==================== PORTFOLIO REBALANCING ====================
    enable_rebalancing: bool = Field(
        default=False,
        description="Activar rebalanceo automático"
    )
    rebalance_frequency_days: int = Field(
        default=7,
        description="Frecuencia de rebalanceo en días"
    )
    rebalance_threshold: float = Field(
        default=5.0,
        description="Umbral de desviación para rebalancear"
    )
    
    # ==================== HYBRID ADVANCED SYSTEM ====================
    enable_hybrid_advanced: bool = Field(
        default=True,
        description="Activar sistema híbrido avanzado"
    )
    enable_model_ensemble: bool = Field(
        default=True,
        description="Activar ensemble de modelos ML"
    )
    enable_regime_detection: bool = Field(
        default=True,
        description="Activar detección de régimen de mercado"
    )
    enable_alternative_data: bool = Field(
        default=False,
        description="Activar datos alternativos"
    )
    enable_llm_reasoning: bool = Field(
        default=False,
        description="Activar razonamiento con LLM"
    )
    openai_api_key: str = Field(
        default="",
        description="API key de OpenAI"
    )
    deepseek_api_key: str = Field(
        default="",
        description="API key de DeepSeek"
    )
    gemini_api_key: str = Field(
        default="",
        description="API key de Google Gemini"
    )
    llm_model: str = Field(
        default="gpt-4",
        description="Modelo LLM a usar"
    )
    llm_provider: str = Field(
        default="openai",
        description="Proveedor LLM (openai, anthropic, deepseek, gemini)"
    )
    paper_mode: bool = Field(
        default=False,
        description="Modo paper trading"
    )
    
    # ==================== DATABASE ====================
    database_url: str = Field(
        default="sqlite:///./data/trades.db",
        description="URL de conexión a base de datos"
    )
    
    # ==================== LOGGING ====================
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_file: str = Field(default="./logs/bot.log", description="Archivo de logs")
    
    # ==================== DASHBOARD ====================
    dashboard_port: int = Field(default=8501, description="Puerto del dashboard")
    dashboard_host: str = Field(default="0.0.0.0", description="Host del dashboard")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Permitir campos extra del .env
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Obtiene la configuración global"""
    return settings


def reload_settings():
    """Recarga la configuración desde el archivo .env"""
    global settings
    settings = Settings()
    return settings

