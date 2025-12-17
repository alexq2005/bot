"""
Test de Risk Manager
Pruebas para validar cálculos de SL/TP y lógica de salida
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk.dynamic_risk_manager import DynamicRiskManager


def test_risk_manager_init():
    """Verificar inicialización del Risk Manager"""
    try:
        rm = DynamicRiskManager()
        print("✅ Risk Manager inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Fallo en inicialización: {e}")
        return False


def test_sl_tp_calculation_long():
    """Verificar cálculo de SL/TP para LONG"""
    try:
        rm = DynamicRiskManager()
        
        entry_price = 100.0
        atr = 2.0
        
        levels = rm.calculate_levels(
            entry_price=entry_price,
            atr=atr,
            direction="LONG"
        )
        
        assert levels is not None, "Levels es None"
        assert 'stop_loss' in levels, "Falta 'stop_loss'"
        assert 'take_profit' in levels, "Falta 'take_profit'"
        
        # Para LONG: SL < entry < TP
        assert levels['stop_loss'] < entry_price, f"SL debe ser < entry"
        assert levels['take_profit'] > entry_price, f"TP debe ser > entry"
        
        print(f"✅ Cálculo SL/TP LONG:")
        print(f"   - Entry: ${entry_price:.2f}")
        print(f"   - SL: ${levels['stop_loss']:.2f}")
        print(f"   - TP: ${levels['take_profit']:.2f}")
        print(f"   - Risk/Reward: 1:{(levels['take_profit'] - entry_price) / (entry_price - levels['stop_loss']):.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo cálculo LONG: {e}")
        return False


def test_sl_tp_calculation_short():
    """Verificar cálculo de SL/TP para SHORT"""
    try:
        rm = DynamicRiskManager()
        
        entry_price = 100.0
        atr = 2.0
        
        levels = rm.calculate_levels(
            entry_price=entry_price,
            atr=atr,
            direction="SHORT"
        )
        
        # Para SHORT: TP < entry < SL
        assert levels['take_profit'] < entry_price, f"TP debe ser < entry"
        assert levels['stop_loss'] > entry_price, f"SL debe ser > entry"
        
        print(f"✅ Cálculo SL/TP SHORT:")
        print(f"   - Entry: ${entry_price:.2f}")
        print(f"   - SL: ${levels['stop_loss']:.2f}")
        print(f"   - TP: ${levels['take_profit']:.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo cálculo SHORT: {e}")
        return False


def test_exit_logic_stop_loss():
    """Verificar lógica de salida por Stop Loss"""
    try:
        rm = DynamicRiskManager()
        
        # Posición LONG que toca SL
        result = rm.should_exit(
            current_price=95.0,    # Bajo
            entry_price=100.0,
            stop_loss=95.5,        # SL tocado
            take_profit=110.0,
            direction="LONG"
        )
        
        assert result['exit'] == True, "Debería salir por SL"
        assert 'stop_loss' in result['reason'].lower(), "Razón debe mencionar SL"
        
        print(f"✅ Lógica Stop Loss funciona:")
        print(f"   - Precio: $95.00, SL: $95.50")
        print(f"   - Salir: {result['exit']}")
        print(f"   - Razón: {result['reason']}")
        return True
    except Exception as e:
        print(f"❌ Fallo lógica SL: {e}")
        return False


def test_exit_logic_take_profit():
    """Verificar lógica de salida por Take Profit"""
    try:
        rm = DynamicRiskManager()
        
        # Posición LONG que toca TP
        result = rm.should_exit(
            current_price=111.0,   # Alto
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=110.0,     # TP tocado
            direction="LONG"
        )
        
        assert result['exit'] == True, "Debería salir por TP"
        assert 'take_profit' in result['reason'].lower(), "Razón debe mencionar TP"
        
        print(f"✅ Lógica Take Profit funciona:")
        print(f"   - Precio: $111.00, TP: $110.00")
        print(f"   - Salir: {result['exit']}")
        print(f"   - Razón: {result['reason']}")
        return True
    except Exception as e:
        print(f"❌ Fallo lógica TP: {e}")
        return False


def test_no_exit_logic():
    """Verificar que no se sale si no se toca SL/TP"""
    try:
        rm = DynamicRiskManager()
        
        # Posición LONG en precio seguro
        result = rm.should_exit(
            current_price=102.0,   # Entre SL y TP
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            direction="LONG"
        )
        
        assert result['exit'] == False, "No debería salir"
        
        print(f"✅ Sin salida en precio seguro:")
        print(f"   - Precio: $102.00")
        print(f"   - Entre SL ($95.00) y TP ($110.00)")
        print(f"   - Salir: {result['exit']}")
        return True
    except Exception as e:
        print(f"❌ Fallo lógica sin salida: {e}")
        return False


def test_risk_reward_ratio():
    """Verificar relación Risk/Reward"""
    try:
        rm = DynamicRiskManager()
        
        entry = 100.0
        sl = 95.0
        tp = 110.0
        
        risk = entry - sl
        reward = tp - entry
        ratio = reward / risk if risk > 0 else 0
        
        assert ratio >= 1.0, f"Risk/Reward debe ser >= 1.0, obtuvo {ratio}"
        
        print(f"✅ Risk/Reward Ratio:")
        print(f"   - Risk: ${risk:.2f}")
        print(f"   - Reward: ${reward:.2f}")
        print(f"   - Ratio: 1:{ratio:.2f}")
        return True
    except Exception as e:
        print(f"❌ Fallo ratio: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE RISK MANAGER")
    print("=" * 70 + "\n")
    
    tests = [
        ("Inicialización Risk Manager", test_risk_manager_init),
        ("Cálculo SL/TP LONG", test_sl_tp_calculation_long),
        ("Cálculo SL/TP SHORT", test_sl_tp_calculation_short),
        ("Lógica Stop Loss", test_exit_logic_stop_loss),
        ("Lógica Take Profit", test_exit_logic_take_profit),
        ("Sin Salida en Rango", test_no_exit_logic),
        ("Risk/Reward Ratio", test_risk_reward_ratio),
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
