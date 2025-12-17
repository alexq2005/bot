"""
Database Manager
Gestiona conexiones, sesiones y operaciones de base de datos
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base


class DatabaseManager:
    """Gestor centralizado de base de datos"""
    
    def __init__(self, database_url: str = None):
        """
        Inicializa el gestor de base de datos
        
        Args:
            database_url: URL de conexión (ej: sqlite:///./data/trades.db)
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "sqlite:///./data/trades.db"
        )
        
        # Configuración del engine
        connect_args = {}
        poolclass = None
        
        # SQLite requiere configuración especial para threading
        if self.database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            poolclass = StaticPool
        
        self.engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            poolclass=poolclass,
            echo=False  # Set True para debug SQL
        )
        
        # Session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Crear tablas si no existen
        self._create_tables()
    
    def _create_tables(self):
        """Crea todas las tablas en la base de datos"""
        # Crear directorio data si no existe
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager para sesiones de base de datos
        
        Uso:
            with db_manager.get_session() as session:
                session.add(trade)
                session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_db(self) -> Session:
        """
        Obtiene una sesión de base de datos (para uso con FastAPI)
        
        Returns:
            Session: Sesión de SQLAlchemy
        """
        return self.SessionLocal()
    
    def close(self):
        """Cierra el engine de base de datos"""
        self.engine.dispose()


# Instancia global del gestor
db_manager = DatabaseManager()


# Helper function para obtener sesión
def get_session() -> Generator[Session, None, None]:
    """Helper para obtener sesión de base de datos"""
    with db_manager.get_session() as session:
        yield session
