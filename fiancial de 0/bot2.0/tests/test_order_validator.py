"""
Test de Order Validator
Pruebas para validar el sistema de validación de órdenes
"""

import sys
from pathlib import Path
from datetime import datetime, time

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.validators.order_validator import OrderValidator, ValidationLevel, ValidationResult


def test_validator_initialization():
    """Test inicialización del validador"""
    try:
        validator = OrderValidator()
        assert validator.max_position_size == 100000
        assert validator.max_daily_orders == 50
        assert validator.max_price_deviation == 0.05
        print("✅ Validador inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_custom_config():
    """Test configuración personalizada"""
    try:
        config = {
            'max_position_size': 50000,
            'max_daily_orders': 20,
            'max_price_deviation': 0.10
        }
        validator = OrderValidator(config)
        assert validator.max_position_size == 50000
        assert validator.max_daily_orders == 20
        assert validator.max_price_deviation == 0.10
        print("✅ Configuración personalizada aplicada")
        return True
    except Exception as e:
        print(f"❌ Fallo en configuración: {e}")
        return False


def test_insufficient_balance():
    """Test validación de saldo insuficiente"""
    try:
        validator = OrderValidator()
        
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 100,
            'price': 1000
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=50000,  # Insuficiente para 100 * 1000 = 100,000
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        assert not is_valid, "Orden debería ser rechazada por saldo insuficiente"
        balance_result = next((r for r in results if 'Saldo insuficiente' in r.message), None)
        assert balance_result is not None, "Debe haber un resultado de validación de saldo"
        assert not balance_result.passed, "Validación de saldo debe fallar"
        
        print("✅ Validación de saldo insuficiente funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de saldo: {e}")
        return False


def test_sufficient_balance():
    """Test validación con saldo suficiente"""
    try:
        validator = OrderValidator()
        
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 10,
            'price': 1000
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=50000,  # Suficiente para 10 * 1000 = 10,000
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        # Should pass all validations (assuming we're in market hours)
        # At minimum, balance validation should pass
        balance_result = next((r for r in results if 'Saldo suficiente' in r.message), None)
        assert balance_result is not None, "Debe haber un resultado de validación de saldo"
        assert balance_result.passed, "Validación de saldo debe pasar"
        
        print("✅ Validación de saldo suficiente funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de saldo suficiente: {e}")
        return False


def test_position_size_limit():
    """Test límite de tamaño de posición"""
    try:
        validator = OrderValidator({'max_position_size': 50000})
        
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 100,
            'price': 1000
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=200000,
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        assert not is_valid, "Orden debe ser rechazada por exceder límite de posición"
        position_result = next((r for r in results if 'excede límite máximo' in r.message), None)
        assert position_result is not None
        assert not position_result.passed
        
        print("✅ Validación de límite de posición funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de límite de posición: {e}")
        return False


def test_price_deviation():
    """Test validación de desviación de precio"""
    try:
        validator = OrderValidator({'max_price_deviation': 0.05})  # 5%
        
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 10,
            'price': 1200  # 20% más alto que last_price
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=50000,
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        assert not is_valid, "Orden debe ser rechazada por desviación de precio"
        price_result = next((r for r in results if 'se desvía' in r.message), None)
        assert price_result is not None
        assert not price_result.passed
        
        print("✅ Validación de desviación de precio funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de desviación de precio: {e}")
        return False


def test_quantity_validation():
    """Test validación de cantidad"""
    try:
        validator = OrderValidator()
        
        # Cantidad cero
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 0,
            'price': 1000
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=50000,
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        assert not is_valid, "Orden con cantidad 0 debe ser rechazada"
        quantity_result = next((r for r in results if 'mayor a 0' in r.message), None)
        assert quantity_result is not None
        assert not quantity_result.passed
        
        print("✅ Validación de cantidad funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de cantidad: {e}")
        return False


def test_daily_order_limit():
    """Test límite de órdenes diarias"""
    try:
        validator = OrderValidator({'max_daily_orders': 10})
        
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 10,
            'price': 1000
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=50000,
            current_positions={},
            last_price=1000,
            daily_order_count=15  # Excede el límite
        )
        
        assert not is_valid, "Orden debe ser rechazada por límite diario"
        limit_result = next((r for r in results if 'Límite diario' in r.message), None)
        assert limit_result is not None
        assert not limit_result.passed
        
        print("✅ Validación de límite diario funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de límite diario: {e}")
        return False


def test_exposure_validation():
    """Test validación de exposición"""
    try:
        validator = OrderValidator({'max_exposure_per_asset': 0.3})  # 30%
        
        order = {
            'symbol': 'GGAL',
            'side': 'BUY',
            'quantity': 50,
            'price': 1000
        }
        
        # Balance de 100,000, orden de 50,000 = 50% de exposición
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=100000,
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        # WARNING level, not ERROR, so order might still be valid
        exposure_result = next((r for r in results if 'Exposición' in r.message), None)
        assert exposure_result is not None
        
        print("✅ Validación de exposición funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de exposición: {e}")
        return False


def test_symbol_validation():
    """Test validación de símbolo"""
    try:
        validator = OrderValidator()
        
        # Símbolo inválido
        order = {
            'symbol': '',
            'side': 'BUY',
            'quantity': 10,
            'price': 1000
        }
        
        is_valid, results = validator.validate_order(
            order=order,
            account_balance=50000,
            current_positions={},
            last_price=1000,
            daily_order_count=0
        )
        
        assert not is_valid, "Orden con símbolo vacío debe ser rechazada"
        symbol_result = next((r for r in results if 'Símbolo inválido' in r.message), None)
        assert symbol_result is not None
        assert not symbol_result.passed
        
        print("✅ Validación de símbolo funciona")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de símbolo: {e}")
        return False


def test_validation_summary():
    """Test resumen de validaciones"""
    try:
        validator = OrderValidator()
        
        # Ejecutar varias validaciones
        orders = [
            {'symbol': 'GGAL', 'side': 'BUY', 'quantity': 10, 'price': 1000},
            {'symbol': 'YPFD', 'side': 'BUY', 'quantity': 5, 'price': 2000},
            {'symbol': '', 'side': 'BUY', 'quantity': 0, 'price': 1000},  # Inválida
        ]
        
        for order in orders:
            validator.validate_order(
                order=order,
                account_balance=50000,
                current_positions={},
                last_price=order.get('price'),
                daily_order_count=0
            )
        
        summary = validator.get_validation_summary()
        assert summary['total_validations'] > 0
        assert 'passed' in summary
        assert 'failed' in summary
        assert 'success_rate' in summary
        
        print("✅ Resumen de validaciones funciona")
        print(f"   Total: {summary['total_validations']}")
        print(f"   Pasadas: {summary['passed']}")
        print(f"   Falladas: {summary['failed']}")
        print(f"   Tasa de éxito: {summary['success_rate']:.1f}%")
        return True
    except Exception as e:
        print(f"❌ Fallo en test de resumen: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE ORDER VALIDATOR")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización", test_validator_initialization),
        ("Configuración Personalizada", test_custom_config),
        ("Saldo Insuficiente", test_insufficient_balance),
        ("Saldo Suficiente", test_sufficient_balance),
        ("Límite de Posición", test_position_size_limit),
        ("Desviación de Precio", test_price_deviation),
        ("Validación de Cantidad", test_quantity_validation),
        ("Límite Diario", test_daily_order_limit),
        ("Exposición", test_exposure_validation),
        ("Validación de Símbolo", test_symbol_validation),
        ("Resumen de Validaciones", test_validation_summary),
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
    
    # Exit code
    exit(0 if passed == len(results) else 1)
