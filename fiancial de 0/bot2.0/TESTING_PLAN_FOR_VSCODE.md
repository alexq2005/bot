# 🧪 Plan de Testing del Proyecto - Para VSCode Copilot

## Objetivo

Testear todo el sistema de trading bot end-to-end para validar funcionalidad antes de operación real.

---

## 📋 Tests Requeridos

### 1. Test de Conexión IOL

```python
# tests/test_iol_connection.py
def test_iol_auth():
    """Verificar que credenciales IOL funcionan"""
    from src.api.iol_client import iol_client
    
    assert iol_client.authenticate(), "Falló autenticación IOL"
    print("✅ Autenticación IOL exitosa")

def test_get_price():
    """Verificar obtención de precios"""
    from src.api.iol_client import iol_client
    
    price = iol_client.get_last_price("GGAL", "bCBA")
    assert price is not None, "No se pudo obtener precio"
    assert price > 0, "Precio inválido"
    print(f"✅ Precio GGAL: ${price}")

def test_get_historical():
    """Verificar datos históricos"""
    from src.api.iol_client import iol_client
    from datetime import datetime, timedelta
    
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    
    df = iol_client.get_historical_data("GGAL", from_date, to_date)
    assert df is not None, "No se obtuvieron datos históricos"
    assert len(df) > 0, "DataFrame vacío"
    print(f"✅ Datos históricos: {len(df)} días")
```

### 2. Test de Market Manager

```python
# tests/test_market_manager.py
def test_market_hours():
    """Verificar detección de horarios"""
    from src.utils.market_manager import MarketManager
    
    mm = MarketManager()
    status = mm.get_market_status()
    
    assert 'is_open' in status
    assert 'current_time' in status
    print(f"✅ Mercado: {status['status']}")

def test_universe():
    """Verificar universo de símbolos"""
    from src.utils.market_manager import MarketManager
    
    mm = MarketManager()
    symbols = mm._get_curated_symbols()
    
    assert len(symbols) > 0, "Universo vacío"
    assert 'GGAL' in symbols, "GGAL no está en universo"
    print(f"✅ Universo: {len(symbols)} símbolos")
```

### 3. Test de Optimizador

```python
# tests/test_optimizer.py
def test_grid_search():
    """Verificar optimización de parámetros"""
    from src.backtesting.optimizer import StrategyOptimizer
    from src.api.iol_client import iol_client
    from datetime import datetime, timedelta
    import pandas as pd
    
    # Obtener datos
    to_date = datetime.now()
    from_date = to_date - timedelta(days=180)
    df = iol_client.get_historical_data("GGAL", from_date, to_date)
    
    assert df is not None, "No hay datos para optimizar"
    
    # Optimizar
    optimizer = StrategyOptimizer()
    param_grid = {
        'rsi_buy_thr': [25, 30],
        'rsi_sell_thr': [70, 75],
        'sma_len': [40, 50]
    }
    
    results = optimizer.grid_search(df, param_grid)
    
    assert len(results) > 0, "No hay resultados"
    print(f"✅ Optimización: {len(results)} combinaciones probadas")
    
    best = results[0]
    print(f"✅ Mejor config: Return {best['metrics']['return_pct']:.2f}%")
```

### 4. Test de Risk Manager

```python
# tests/test_risk_manager.py
def test_sl_tp_calculation():
    """Verificar cálculo de SL/TP"""
    from src.risk.dynamic_risk_manager import DynamicRiskManager
    
    rm = DynamicRiskManager()
    levels = rm.calculate_levels(
        entry_price=1000,
        atr=25,
        direction="LONG"
    )
    
    assert levels['stop_loss'] < 1000, "SL debe ser menor al entry"
    assert levels['take_profit'] > 1000, "TP debe ser mayor al entry"
    print(f"✅ SL: ${levels['stop_loss']:.2f} | TP: ${levels['take_profit']:.2f}")

def test_should_exit():
    """Verificar lógica de salida"""
    from src.risk.dynamic_risk_manager import DynamicRiskManager
    
    rm = DynamicRiskManager()
    
    # Tocar SL
    exit_sl = rm.should_exit(
        current_price=950,
        entry_price=1000,
        stop_loss=975,
        take_profit=1100
    )
    assert exit_sl['exit'] == True, "Debería salir por SL"
    print("✅ Lógica SL funciona")
    
    # Tocar TP
    exit_tp = rm.should_exit(
        current_price=1105,
        entry_price=1000,
        stop_loss=975,
        take_profit=1100
    )
    assert exit_tp['exit'] == True, "Debería salir por TP"
    print("✅ Lógica TP funciona")
```

### 5. Test de Bot Intelligence

```python
# tests/test_bot_intelligence.py
def test_analysis():
    """Verificar análisis del sistema"""
    from src.ai.bot_intelligence import BotIntelligence
    from src.database.db_manager import db_manager
    
    intelligence = BotIntelligence(db_manager)
    analysis = intelligence.run_full_analysis()
    
    assert 'performance' in analysis
    assert 'risk_metrics' in analysis
    assert 'recommendations' in analysis
    print("✅ Bot Intelligence funciona")

def test_report_generation():
    """Verificar generación de reporte"""
    from src.ai.bot_intelligence import BotIntelligence
    from src.database.db_manager import db_manager
    
    intelligence = BotIntelligence(db_manager)
    intelligence.run_full_analysis()
    report = intelligence.generate_report()
    
    assert len(report) > 0, "Reporte vacío"
    assert "BOT INTELLIGENCE" in report
    print("✅ Reporte generado correctamente")
```

### 6. Test de Trading Loop (MOCK)

```python
# tests/test_trading_loop.py
def test_mock_trading():
    """Test completo en modo MOCK"""
    from src.bot.trading_bot import TradingBot
    import time
    
    # Asegurar modo MOCK
    from src.bot.config import settings
    assert settings.mock_mode == True, "Debe estar en modo MOCK"
    
    # Inicializar bot
    bot = TradingBot(symbols=['GGAL'])
    
    # Ejecutar 3 ciclos
    for i in range(3):
        print(f"\n📊 Ciclo {i+1}/3")
        decision = bot.analyze_symbol('GGAL')
        
        if decision:
            result = bot.execute_trade(decision)
            if result:
                print("✅ Trade ejecutado (MOCK)")
        
        time.sleep(2)
    
    print("✅ Trading loop funciona en MOCK")
```

### 7. Test de Dashboard

```python
# tests/test_dashboard.py
def test_dashboard_imports():
    """Verificar que el dashboard carga"""
    try:
        import src.dashboard.app as dashboard
        print("✅ Dashboard importa sin errores")
    except Exception as e:
        raise AssertionError(f"Dashboard falló: {e}")

def test_database_connection():
    """Verificar conexión a DB"""
    from src.database.db_manager import db_manager
    
    with db_manager.get_session() as session:
        assert session is not None
        print("✅ Conexión a DB funciona")
```

---

## 🚀 Cómo Ejecutar los Tests

### Opción 1: Test Individual

```bash
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
python tests/test_iol_connection.py
```

### Opción 2: Todos los Tests

```bash
python -m pytest tests/ -v
```

### Opción 3: Test Específico

```bash
python -c "from tests.test_iol_connection import test_iol_auth; test_iol_auth()"
```

---

## ✅ Checklist de Testing

Pre-requisitos:

- [ ] `.env` configurado con credenciales IOL
- [ ] `MOCK_MODE=true` en `.env`
- [ ] `pip install pytest` (si usas pytest)
- [ ] Base de datos inicializada

Tests básicos:

- [ ] Conexión IOL
- [ ] Obtención de precios
- [ ] Datos históricos
- [ ] Detección horarios de mercado
- [ ] Universo de símbolos

Tests de lógica:

- [ ] Optimizador funciona
- [ ] SL/TP se calculan correctamente
- [ ] Position monitor detecta salidas
- [ ] Bot Intelligence genera análisis

Tests integración:

- [ ] Trading loop en MOCK
- [ ] Dashboard carga sin errores
- [ ] Database funciona

---

## 📊 Resultados Esperados

Todos los tests deben pasar con:

- ✅ Sin errores críticos
- ✅ Conexión IOL exitosa
- ✅ Datos obtenidos correctamente
- ✅ Lógica de trading funcional

Si algún test falla:

1. Revisar error específico
2. Verificar configuración (.env)
3. Verificar conexión a internet
4. Verificar credenciales IOL

---

**Creado para**: VSCode Copilot  
**Fecha**: 2025-12-16  
**Propósito**: Validar sistema antes de operación real
