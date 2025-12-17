"""
SQLAlchemy Database Models
Modelos para almacenar trades, sentimiento, logs y métricas
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Trade(Base):
    """Registro de operaciones ejecutadas"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    
    # Señales que generaron la operación
    technical_signal = Column(String(50))  # RSI_OVERSOLD, MACD_CROSS, etc.
    rl_prediction = Column(String(10))  # BUY, SELL, HOLD
    sentiment_score = Column(Float)  # -1.0 a 1.0
    
    # Gestión de riesgo
    position_size_pct = Column(Float)  # Porcentaje del portafolio
    atr_value = Column(Float)  # Average True Range al momento
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # Resultado (se actualiza al cerrar posición)
    pnl = Column(Float, default=0.0)  # Profit & Loss
    pnl_pct = Column(Float, default=0.0)  # P&L porcentual
    is_closed = Column(Boolean, default=False)
    close_timestamp = Column(DateTime)
    
    # Metadata
    mode = Column(String(10), default="MOCK")  # MOCK o LIVE
    notes = Column(Text)

    def __repr__(self):
        return f"<Trade {self.symbol} {self.action} {self.quantity}@{self.price}>"


class SentimentLog(Base):
    """Registro de análisis de sentimiento de noticias"""
    __tablename__ = "sentiment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Noticia analizada
    headline = Column(Text, nullable=False)
    source = Column(String(50))  # NewsData, Finnhub, AlphaVantage
    url = Column(Text)
    
    # Resultado del análisis FinBERT
    sentiment_score = Column(Float, nullable=False)  # -1.0 a 1.0
    sentiment_label = Column(String(20))  # positive, negative, neutral
    confidence = Column(Float)  # Confianza del modelo
    
    def __repr__(self):
        return f"<Sentiment {self.symbol} {self.sentiment_label} ({self.sentiment_score:.2f})>"


class SystemLog(Base):
    """Logs del sistema para auditoría y debugging"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    component = Column(String(50), nullable=False)  # IOL_CLIENT, RL_AGENT, etc.
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Información adicional en formato JSON
    
    def __repr__(self):
        return f"<Log [{self.level}] {self.component}: {self.message[:50]}>"


class PerformanceMetric(Base):
    """Métricas de rendimiento del bot"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    period = Column(String(20), nullable=False)  # HOURLY, DAILY, WEEKLY
    
    # Métricas de portafolio
    total_value = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)
    invested_value = Column(Float, nullable=False)
    
    # Métricas de rendimiento
    total_return = Column(Float, default=0.0)  # Retorno total
    total_return_pct = Column(Float, default=0.0)  # Retorno porcentual
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)  # Porcentaje de trades ganadores
    
    # Métricas de trading
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # Métricas de IA
    rl_accuracy = Column(Float)  # Precisión del agente RL
    sentiment_correlation = Column(Float)  # Correlación sentimiento-precio
    
    def __repr__(self):
        return f"<Metrics {self.period} Return: {self.total_return_pct:.2f}%>"


class ModelCheckpoint(Base):
    """Checkpoints de modelos de ML para versionado"""
    __tablename__ = "model_checkpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_type = Column(String(50), nullable=False)  # PPO, FINBERT, etc.
    version = Column(String(20), nullable=False)
    file_path = Column(String(255), nullable=False)
    
    # Métricas del modelo
    training_episodes = Column(Integer)
    avg_reward = Column(Float)
    validation_accuracy = Column(Float)
    
    # Metadata
    hyperparameters = Column(JSON)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ModelCheckpoint {self.model_type} v{self.version}>"


class ActivePosition(Base):
    """Posiciones activas con Stop Loss y Take Profit"""
    __tablename__ = "active_positions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Datos de entrada
    entry_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    direction = Column(String(10), nullable=False)  # LONG, SHORT
    
    # Gestión de riesgo (ATR-based)
    atr = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    trailing_stop = Column(Boolean, default=True)
    
    # Estado actual
    current_price = Column(Float)
    current_pnl = Column(Float, default=0.0)
    current_pnl_pct = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    trade_id = Column(Integer)  # Referencia al Trade que abrió esta posición
    mode = Column(String(10), default="MOCK")
    
    def __repr__(self):
        return f"<ActivePosition {self.symbol} {self.direction} {self.quantity}@{self.entry_price}>"
