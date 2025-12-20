# 📊 Sistema de Indicadores Técnicos + Validación de Órdenes

## 🎯 Resumen

Implementación completa de un sistema profesional de análisis técnico y validación de órdenes para el bot de trading IOL.

## ✅ Componentes Implementados

### 1. 📈 Sistema de Indicadores Técnicos

**Ubicación:** `src/analysis/`

#### `technical_indicators.py`
Clase mejorada con soporte para:
- **RSI (Relative Strength Index)** - Indicador de sobreventa/sobrecompra
- **MACD (Moving Average Convergence Divergence)** - Cruces alcistas/bajistas
- **Bandas de Bollinger** - Volatilidad y rangos de precio
- **ATR (Average True Range)** - Medida de volatilidad
- **Medias Móviles (SMA/EMA)** - Tendencias de precio

**Nuevas Funcionalidades:**
```python
# Generar señales de trading automáticas
signals = TechnicalIndicators.get_trading_signals(df)
# Retorna: {'rsi_signal': 'COMPRA (Sobreventa)', 'macd_signal': 'NEUTRAL', ...}

# Obtener valores actuales
latest = TechnicalIndicators.get_latest_indicators(df)
# Retorna dict con todos los valores actuales
```

#### `indicator_visualizer.py`
Visualización interactiva con Plotly:
- Gráfico de 4 paneles:
  1. **Precio + Bandas de Bollinger** (Candlestick)
  2. **RSI** con líneas de sobrecompra (70) y sobreventa (30)
  3. **MACD** con línea de señal e histograma
  4. **Volumen** de trading

```python
visualizer = IndicatorVisualizer()
fig = visualizer.create_comprehensive_chart(prices, indicators)
```

### 2. 🛡️ Sistema de Validación de Órdenes

**Ubicación:** `src/validators/`

#### `order_validator.py`
Validador multi-nivel con 8 reglas críticas:

1. ✅ **Saldo Suficiente** - Verifica fondos disponibles
2. ✅ **Límites de Posición** - Evita posiciones demasiado grandes
3. ✅ **Horario de Mercado** - Valida que el mercado esté abierto (11:00-17:00)
4. ✅ **Precio Razonable** - Detecta desviaciones anormales (>5%)
5. ✅ **Cantidad Válida** - Cantidad > 0
6. ✅ **Límite Diario** - Máximo de órdenes por día
7. ✅ **Exposición por Activo** - Limita exposición al 30% del capital
8. ✅ **Símbolo Válido** - Verifica formato del símbolo

**Uso:**
```python
validator = OrderValidator(config={
    'max_position_size': 100000,
    'max_daily_orders': 50,
    'max_price_deviation': 0.05,
    'max_exposure_per_asset': 0.3
})

is_valid, results = validator.validate_order(
    order={'symbol': 'GGAL', 'side': 'BUY', 'quantity': 100, 'price': 500},
    account_balance=200000,
    current_positions={},
    last_price=500,
    daily_order_count=10
)

if is_valid:
    # Ejecutar orden
else:
    # Rechazar orden
    for result in results:
        if not result.passed:
            print(f"❌ {result.message}")
```

**Niveles de Validación:**
- `ERROR` - Bloquea la orden completamente
- `WARNING` - Permite pero advierte al usuario
- `INFO` - Solo informativo

### 3. 📊 Integración en Dashboard

**Ubicación:** `src/dashboard/app.py`

Nueva pestaña de **"📈 Análisis"** con:

1. **Selector de Símbolo** - Analiza cualquier activo
2. **Gráfico Interactivo** - 4 paneles con todos los indicadores
3. **Señales de Trading** - Código de colores:
   - 🟢 Verde = Señal de COMPRA
   - 🔴 Rojo = Señal de VENTA
   - 🔵 Azul = NEUTRAL
4. **Valores Actuales** - Métricas en tiempo real de todos los indicadores

## 🧪 Tests Implementados

### Test de Indicadores Técnicos
**Archivo:** `tests/test_trading_signals.py`

✅ 4/4 tests pasando:
- Generación de señales
- Señal RSI en sobreventa
- Cálculo completo de indicadores
- Consistencia de señales

### Test de Order Validator
**Archivo:** `tests/test_order_validator.py`

✅ 11/11 tests pasando:
- Inicialización y configuración
- Validación de saldo
- Límites de posición
- Desviación de precio
- Validación de cantidad
- Límite diario de órdenes
- Exposición por activo
- Validación de símbolos
- Resumen de validaciones

### Test de Integración Dashboard
**Archivo:** `tests/test_dashboard_integration.py`

✅ 3/3 tests pasando:
- Integración completa del dashboard
- Análisis de múltiples símbolos
- Generación de gráficos

## 🚀 Cómo Usar

### 1. Ejecutar Tests
```bash
cd "fiancial de 0/bot2.0"

# Test de validador
python tests/test_order_validator.py

# Test de señales
python tests/test_trading_signals.py

# Test de integración
python tests/test_dashboard_integration.py
```

### 2. Ejecutar Demo
```bash
python demo_indicators_validator.py
```

Salida esperada:
```
✅ Análisis técnico completado
✅ Validación de órdenes completada
✅ Flujo completo finalizado
🎉 TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE
```

### 3. Ver Visualización
```bash
python generate_sample_viz.py
# Abre technical_analysis_demo.html en tu navegador
```

### 4. Ejecutar Dashboard
```bash
streamlit run src/dashboard/app.py
```

Navega a la pestaña **"📈 Análisis"** y:
1. Selecciona un símbolo (ej: GGAL, YPFD, PAMP)
2. Ajusta días de historia (30-365)
3. Haz clic en **"🔍 Generar Análisis Técnico"**

## 📈 Ejemplo de Uso en Código

### Análisis Técnico Completo
```python
from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.indicator_visualizer import IndicatorVisualizer

# Cargar datos históricos
historical_data = get_historical_data('GGAL', days=90)

# Calcular indicadores
indicators = TechnicalIndicators()
indicators_df = indicators.calculate_all_indicators(historical_data)

# Obtener señales
signals = indicators.get_trading_signals(historical_data)
print(f"RSI: {signals['rsi_signal']}")
print(f"MACD: {signals['macd_signal']}")
print(f"Bollinger: {signals['bb_signal']}")

# Visualizar
visualizer = IndicatorVisualizer()
fig = visualizer.create_comprehensive_chart(historical_data, indicators_df)
fig.show()
```

### Validación de Órdenes
```python
from src.validators.order_validator import OrderValidator

# Configurar validador
validator = OrderValidator({
    'max_position_size': 100000,
    'max_daily_orders': 50
})

# Preparar orden
order = {
    'symbol': 'GGAL',
    'side': 'BUY',
    'quantity': 100,
    'price': 500
}

# Validar antes de ejecutar
is_valid, results = validator.validate_order(
    order=order,
    account_balance=200000,
    current_positions={},
    last_price=500,
    daily_order_count=10
)

if is_valid:
    execute_order(order)
    print("✅ Orden ejecutada")
else:
    print("❌ Orden rechazada")
    for r in results:
        if not r.passed:
            print(f"   {r.message}")
```

## 📊 Estructura de Archivos

```
fiancial de 0/bot2.0/
├── src/
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── technical_indicators.py     # Cálculo de indicadores ✅
│   │   └── indicator_visualizer.py     # Visualización Plotly ✅
│   ├── validators/
│   │   ├── __init__.py
│   │   └── order_validator.py          # Validación de órdenes ✅
│   └── dashboard/
│       └── app.py                       # Dashboard integrado ✅
├── tests/
│   ├── test_order_validator.py          # 11/11 ✅
│   ├── test_trading_signals.py          # 4/4 ✅
│   └── test_dashboard_integration.py    # 3/3 ✅
├── demo_indicators_validator.py         # Demo completo ✅
└── generate_sample_viz.py               # Generador de viz ✅
```

## 🎉 Resultados

**Total de Tests:** 18/18 ✅ (100% passing)
- Order Validator: 11/11 ✅
- Trading Signals: 4/4 ✅
- Dashboard Integration: 3/3 ✅

**Componentes Implementados:** 5/5 ✅
- ✅ TechnicalIndicators mejorado
- ✅ IndicatorVisualizer
- ✅ OrderValidator
- ✅ Dashboard Integration
- ✅ Tests completos

## 🔧 Configuración

### Dependencias Necesarias
Ya incluidas en `requirements.txt`:
```
ta==0.11.0              # Technical Analysis Library
plotly==5.18.0          # Gráficos interactivos
pandas==2.1.4           # Data manipulation
numpy==1.26.2           # Numerical computing
streamlit==1.29.0       # Dashboard
```

### Variables de Configuración del Validador
```python
config = {
    'max_position_size': 100000,      # Tamaño máximo de posición ($)
    'max_daily_orders': 50,           # Órdenes máximas por día
    'max_price_deviation': 0.05,      # Desviación máxima de precio (5%)
    'max_exposure_per_asset': 0.3     # Exposición máxima por activo (30%)
}
```

## 📝 Notas

- Los indicadores técnicos funcionan con datos OHLCV (Open, High, Low, Close, Volume)
- Las señales son generadas automáticamente basadas en reglas estándar
- El validador puede configurarse para diferentes perfiles de riesgo
- Todos los gráficos son interactivos (zoom, pan, hover)
- El sistema es completamente modular y extensible

## 🚀 Próximos Pasos Sugeridos

1. Integrar con API real de IOL para datos históricos
2. Agregar más indicadores (Stochastic, Williams %R, etc.)
3. Implementar backtesting con indicadores
4. Agregar alertas automáticas por Telegram
5. Crear estrategias basadas en combinación de señales

---

**Autor:** Copilot AI  
**Fecha:** 2025-12-20  
**Status:** ✅ Completado e implementado
