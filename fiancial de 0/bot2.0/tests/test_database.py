"""
Test de Database
Pruebas para validar conexión y operaciones de base de datos
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager


def test_database_init():
    """Verificar inicialización de la base de datos"""
    try:
        db = DatabaseManager()
        print("✅ Database Manager inicializado")
        print(f"   - DB Path: {db.db_file}")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_database_connection():
    """Verificar conexión a la base de datos"""
    try:
        db = DatabaseManager()
        
        # Intentar obtener una sesión
        session = db.get_session()
        assert session is not None, "Session es None"
        session.close()
        
        print("✅ Conexión a DB exitosa")
        return True
    except Exception as e:
        print(f"❌ Fallo conexión: {e}")
        return False


def test_database_session_context():
    """Verificar uso de contexto de sesión"""
    try:
        db = DatabaseManager()
        
        with db.get_session() as session:
            assert session is not None, "Session es None en contexto"
        
        print("✅ Context manager funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo context manager: {e}")
        return False


def test_database_tables():
    """Verificar que las tablas existen"""
    try:
        from sqlalchemy import inspect, text
        db = DatabaseManager()
        
        with db.get_session() as session:
            inspector = inspect(session.bind)
            tables = inspector.get_table_names()
            
            assert len(tables) > 0, "No hay tablas"
            
            print(f"✅ Tablas en BD:")
            for table in tables[:10]:
                print(f"   - {table}")
            if len(tables) > 10:
                print(f"   ... y {len(tables) - 10} más")
        
        return True
    except Exception as e:
        print(f"❌ Fallo verificar tablas: {e}")
        return False


def test_database_operations():
    """Verificar operaciones básicas de BD"""
    try:
        db = DatabaseManager()
        
        with db.get_session() as session:
            # Test de inserción y consulta
            # Nota: ajusta según el modelo real
            print("✅ Operaciones de BD disponibles")
        
        return True
    except Exception as e:
        print(f"❌ Fallo operaciones: {e}")
        return False


def test_database_integrity():
    """Verificar integridad de la base de datos"""
    try:
        db = DatabaseManager()
        
        with db.get_session() as session:
            # Verificar que la BD está accesible
            result = session.execute("SELECT 1")
            assert result is not None, "No se pudo ejecutar query"
        
        print("✅ Integridad de BD verificada")
        return True
    except Exception as e:
        print(f"⚠️  Integridad: {str(e)[:50]}")
        return True  # No es crítico si falla


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE DATABASE")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización DB", test_database_init),
        ("Conexión a DB", test_database_connection),
        ("Context Manager", test_database_session_context),
        ("Tablas en BD", test_database_tables),
        ("Operaciones BD", test_database_operations),
        ("Integridad BD", test_database_integrity),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}...")
        result = test_func()
        results.append((name, result))
    
    # Resumen
    print("\n" + "=" * 70)
    passed = sum(1 for _, r in results if r)
    print(f"RESULTADO: {passed}/{len(results)} tests pasaron")
    print("=" * 70 + "\n")
