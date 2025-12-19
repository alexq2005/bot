# Guía de Aprendizaje Continuo y Auto-Mejora

## 📚 Introducción

Este bot ahora incluye un **sistema completo de aprendizaje continuo** con 6 niveles de capacidades, desde ajuste automático básico hasta reentrenamiento totalmente autónomo.

---

## 🎯 Niveles de Aprendizaje

### ✅ Nivel 1-3: Automático (Ya Funciona)
Estos niveles están activos por defecto sin necesidad de configuración:
- **Nivel 1:** Ajuste dinámico de pesos de modelos
- **Nivel 2:** Detección automática de drift
- **Nivel 3:** Recomendaciones de reentrenamiento

### 🔧 Nivel 4-6: Requieren Activación
Estos niveles están implementados pero necesitas activarlos:
- **Nivel 4:** Reentrenamiento manual fácil
- **Nivel 5:** Reentrenamiento automático programado
- **Nivel 6:** A/B testing de modelos

---

## 🚀 Uso Rápido

### Reentrenamiento Manual (Nivel 4)

**Opción 1: Modo Interactivo (Recomendado para principiantes)**

```bash
cd "fiancial de 0/bot2.0"
python scripts/easy_retrain.py
```

El script te hará preguntas:
- ¿Qué símbolo entrenar? (ej: GGAL)
- ¿Cuántos días de datos? (ej: 365)
- ¿Cuántos timesteps? (ej: 50000)
- ¿Comparar con modelo actual? (S/n)

**Opción 2: Entrenamiento Rápido**

```bash
# Entrenamiento rápido (10k timesteps, ~5 minutos)
python scripts/easy_retrain.py --quick

# Con comparación A/B automática
python scripts/easy_retrain.py --quick --compare
```

**Opción 3: Entrenamiento Personalizado**

```bash
# Entrenamiento completo
python scripts/easy_retrain.py --symbol YPFD --days 365 --timesteps 100000 --compare
```

**¿Qué hace el script?**
1. ✅ Descarga datos históricos
2. ✅ Calcula indicadores técnicos
3. ✅ Entrena nuevo modelo
4. ✅ Evalúa performance
5. ✅ Compara con modelo actual (si usas --compare)
6. ✅ Reemplaza automáticamente si es mejor

---

### Reentrenamiento Automático (Nivel 5)

**Integración en el Bot**

Edita `src/bot/trading_bot.py`:

```python
from src.utils.auto_retrain_scheduler import AutoRetrainScheduler

class TradingBot:
    def __init__(self):
        # ... código existente ...
        
        # Configurar scheduler automático
        self.auto_retrain = AutoRetrainScheduler(
            check_interval_hours=24,      # Chequear cada 24 horas
            min_trades_for_retrain=100,   # Mínimo 100 trades para reentrenar
            performance_threshold=0.6,     # Threshold de Sharpe ratio
            auto_mode=True                # True = automático, False = solo recomienda
        )
        
        # Función para obtener datos de entrenamiento
        def get_training_data():
            # Obtener últimos N días de datos
            from datetime import datetime, timedelta
            to_date = datetime.now()
            from_date = to_date - timedelta(days=180)
            
            # Usar primer símbolo del universo
            symbol = self.symbols[0] if self.symbols else 'GGAL'
            df = self.client.get_historical_data(symbol, from_date, to_date)
            
            # Calcular indicadores
            df = self.technical_indicators.calculate_all_indicators(df)
            df = df.dropna()
            df['sentiment'] = 0.0  # Agregar sentimiento
            
            return df
        
        # Iniciar scheduler
        if self.settings.use_rl_agent:
            self.auto_retrain.start_scheduler(
                self.rl_agent,
                getattr(self, 'ensemble', None),
                get_training_data
            )
    
    def stop(self):
        # Detener scheduler al cerrar el bot
        if hasattr(self, 'auto_retrain'):
            self.auto_retrain.stop_scheduler()
        
        # ... resto del código ...
```

**Configuración del Scheduler**

Parámetros importantes:

```python
AutoRetrainScheduler(
    check_interval_hours=24,    # Cada cuánto verificar (en horas)
    min_trades_for_retrain=100, # Mínimo de trades para considerar retrain
    performance_threshold=0.6,  # Sharpe ratio mínimo aceptable
    drift_threshold=0.3,        # Threshold para detectar drift
    auto_mode=True              # True = automático, False = solo recomienda
)
```

**Modos de Operación:**

- **auto_mode=True**: Reentrena automáticamente cuando detecta problemas
- **auto_mode=False**: Solo genera recomendaciones, no reentrena

**Monitoreo:**

```python
# Ver estado del scheduler
status = bot.auto_retrain.get_status()
print(f"Running: {status['running']}")
print(f"Last retrain: {status['last_retrain']}")
print(f"Days since retrain: {status['days_since_retrain']}")
```

---

### A/B Testing de Modelos (Nivel 6)

**Uso Básico**

```python
from src.utils.model_ab_tester import ModelABTester

# Crear tester
tester = ModelABTester(
    validation_episodes=10,      # Episodios de validación
    significance_threshold=0.05, # Nivel de significancia (95% confianza)
    min_improvement=0.02         # 2% mínimo de mejora requerida
)

# Comparar dos modelos
result = tester.auto_replace_if_better(
    current_model_path="./models/ppo_trading_agent",
    new_model_path="./models/temp_new_model",
    validation_data=validation_df,
    backup=True  # Crear backup del modelo actual
)

# Interpretar resultado
if result['success']:
    if result['replaced']:
        print("✅ Nuevo modelo es mejor!")
        print(f"Mejora: {result['comparison']['comparison']['improvement_return_pct']:.2f}%")
    else:
        print("❌ Modelo actual es mejor")
        print(f"Razón: {result['reason']}")
```

**Métricas Evaluadas:**

El tester evalúa múltiples métricas:
- **Retorno promedio** (mean return)
- **Sharpe ratio** (return/volatilidad)
- **Consistencia** (1 - std_normalized)
- **Significancia estadística** (z-score)

**Ver Histórico:**

```python
# Resumen de todos los tests A/B realizados
summary = tester.get_test_history_summary()

print(f"Tests totales: {summary['total_tests']}")
print(f"Modelos reemplazados: {summary['models_replaced']}")
print(f"Tasa de reemplazo: {summary['replacement_rate']:.1%}")
print(f"Mejora promedio: {summary['average_improvement']:.2f}%")

# Obtener recomendación
recommendation = tester.get_recommendation()
print(f"Recomendación: {recommendation}")
```

---

## 📊 Workflow Completo

### Flujo Recomendado de Aprendizaje Continuo

```
1. Bot opera normalmente
   ↓
2. Ensemble ajusta pesos automáticamente (Nivel 1-2)
   ↓
3. Scheduler chequea performance cada 24h (Nivel 5)
   ↓
4. Si detecta degradación → Reentrena automáticamente
   ↓
5. A/B Testing compara nuevo vs actual (Nivel 6)
   ↓
6. Si nuevo es mejor → Reemplaza automáticamente
   ↓
7. Vuelve al paso 1
```

### Flujo Manual (Control Total)

```
1. Observas performance del bot
   ↓
2. Decides manualmente reentrenar
   ↓
3. Ejecutas: python scripts/easy_retrain.py --compare
   ↓
4. Script compara automáticamente y reemplaza si es mejor
   ↓
5. Continúas operando con el mejor modelo
```

---

## ⚙️ Configuración Avanzada

### Personalizar Reentrenamiento Automático

Crea archivo `data/auto_retrain_config.json`:

```json
{
  "check_interval_hours": 24,
  "min_trades_for_retrain": 100,
  "performance_threshold": 0.6,
  "auto_mode": true
}
```

### Ajustar A/B Testing

```python
tester = ModelABTester(
    validation_episodes=20,      # Más episodios = más confiable pero más lento
    significance_threshold=0.01, # Más estricto (99% confianza)
    min_improvement=0.05         # Requerir 5% de mejora mínima
)
```

---

## 📈 Monitoreo y Logs

### Ver Estado del Sistema

```python
# Estado del scheduler
scheduler_status = bot.auto_retrain.get_status()
print(f"Scheduler activo: {scheduler_status['running']}")
print(f"Días desde último retrain: {scheduler_status['days_since_retrain']}")

# Histórico de reentrenamientos
for retrain in bot.auto_retrain.retrain_history[-5:]:
    print(f"Fecha: {retrain['timestamp']}")
    print(f"Duración: {retrain['duration_seconds']:.1f}s")
    print(f"Retorno: {retrain['metrics'].get('total_return_pct', 0):.2f}%")

# Histórico de A/B tests
summary = tester.get_test_history_summary()
print(f"Tests A/B realizados: {summary['total_tests']}")
print(f"Mejora promedio cuando se reemplaza: {summary['average_improvement']:.2f}%")
```

### Logs del Sistema

Los logs se guardan en:
- `./logs/bot.log` - Logs generales
- `data/auto_retrain_config.json` - Estado del scheduler
- `data/ab_test_results.json` - Resultados de A/B tests

---

## 🎓 Mejores Prácticas

### ✅ Recomendaciones

1. **Empezar en modo manual**: Usa `easy_retrain.py` para familiarizarte
2. **Probar con --quick primero**: Entrenamientos rápidos para experimentar
3. **Siempre usar --compare**: Asegura que solo usas modelos mejores
4. **Activar scheduler gradualmente**: Empieza con auto_mode=False
5. **Monitorear regularmente**: Revisa logs y métricas

### ⚠️ Precauciones

1. **No reentrenar con muy pocos datos**: Mínimo 100 trades o 180 días
2. **Verificar recursos**: El reentrenamiento usa CPU/RAM
3. **Mantener backups**: Siempre usa backup=True
4. **Validar en papel primero**: Prueba modelos en paper trading antes de LIVE

### 📋 Checklist de Implementación

- [ ] Probar reentrenamiento manual con `easy_retrain.py`
- [ ] Verificar que A/B testing funciona correctamente
- [ ] Configurar scheduler en el bot
- [ ] Establecer intervalos apropiados
- [ ] Monitorear primeros reentrenamientos automáticos
- [ ] Ajustar thresholds según tu estrategia
- [ ] Documentar configuración personalizada

---

## 🔍 Solución de Problemas

### Error: "Datos insuficientes"
**Solución:** Aumenta `--days` o verifica que el símbolo tenga datos históricos

### Scheduler no reentrena automáticamente
**Solución:** 
1. Verifica `auto_mode=True`
2. Revisa que hay suficientes trades (`min_trades_for_retrain`)
3. Chequea logs para ver evaluaciones

### A/B test siempre mantiene modelo actual
**Solución:**
1. Reduce `min_improvement` (ej: 0.01 = 1%)
2. Aumenta `timesteps` en entrenamiento
3. Verifica datos de validación sean representativos

### Modelo nuevo es peor que el actual
**Solución:**
1. Aumenta timesteps de entrenamiento
2. Usa más días de datos históricos
3. Considera ajustar hiperparámetros del RL agent

---

## 📞 Soporte

Para más información consulta:
- `CONTINUOUS_LEARNING_ANALYSIS.md` - Análisis técnico detallado
- `src/utils/auto_retrain_scheduler.py` - Código del scheduler
- `src/utils/model_ab_tester.py` - Código del A/B tester
- `scripts/easy_retrain.py` - Script de reentrenamiento

---

**Última actualización:** 2025-12-18
**Versión:** 2.0 - Sistema completo de aprendizaje continuo
