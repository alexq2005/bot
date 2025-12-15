from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from contextlib import contextmanager
from .config import settings

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String) # BUY / SELL
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    strategy_signal = Column(String)
    notes = Column(String, nullable=True)

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    level = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database Initialization
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
