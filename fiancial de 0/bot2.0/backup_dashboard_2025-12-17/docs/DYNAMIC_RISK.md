# Sistema de Auto-Configuración Dinámica de Riesgo

## 🎯 ¿Qué hace?

El bot ahora **ajusta automáticamente** sus niveles de riesgo basándose en su propio rendimiento. Si está funcionando bien, aumenta el riesgo para maximizar ganancias. Si está teniendo problemas, reduce el riesgo para proteger el capital.

---

## 🔧 Cómo Funciona

### Cada 7 días, el bot

1. **Analiza su rendimiento:**
   - Win Rate (% de trades ganadores)
   - Sharpe Ratio (retorno ajustado por riesgo)
   - Retorno Promedio
   - Max Drawdown (pérdida máxima)

2. **Calcula un Score de Rendimiento (0-100):**
   - 80-100: Excelente 🟢
   - 60-79: Bueno 🟡
   - 40-59: Neutro ⚪
   - 20-39: Malo 🟠
   - 0-19: Crítico 🔴

3. **Ajusta automáticamente:**
   - `RISK_PER_TRADE` (riesgo por operación)
   - `MAX_POSITION_SIZE` (tamaño máximo de posición)

---

## 📊 Ejemplo Práctico

### Semana 1: Inicio

```
Configuración inicial:
  RISK_PER_TRADE = 2.0%
  MAX_POSITION_SIZE = 20.0%
```

### Semana 2: Rendimiento Excelente

```
Rendimiento:
  Win Rate: 65%
  Sharpe Ratio: 1.8
  Retorno Promedio: +3.2%
  
Score: 85/100 🟢

Ajuste automático:
  RISK_PER_TRADE = 2.3% (+15%)
  MAX_POSITION_SIZE = 23.0% (+15%)
  
Razón: "Rendimiento excelente - Aumentando riesgo"
```

### Semana 3: Rendimiento Malo

```
Rendimiento:
  Win Rate: 35%
  Sharpe Ratio: 0.4
  Max Drawdown: 8%
  
Score: 28/100 🟠

Ajuste automático:
  RISK_PER_TRADE = 1.96% (-15%)
  MAX_POSITION_SIZE = 19.6% (-15%)
  
Razón: "Rendimiento bajo - Reduciendo riesgo"
```

### Semana 4: Rendimiento Crítico

```
Rendimiento:
  Win Rate: 20%
  Max Drawdown: 15%
  
Score: 12/100 🔴

Ajuste automático:
  RISK_PER_TRADE = 1.37% (-30%)
  MAX_POSITION_SIZE = 13.7% (-30%)
  
Razón: "Rendimiento crítico - Reduciendo riesgo significativamente"
```

---

## ⚙️ Configuración

### Activar/Desactivar

En `.env`:

```bash
# Activar auto-ajuste de riesgo
ENABLE_DYNAMIC_RISK=True

# Frecuencia de ajuste (días)
DYNAMIC_RISK_ADJUSTMENT_DAYS=7

# Límites de seguridad
MIN_RISK_PER_TRADE=0.5   # Nunca bajará de 0.5%
MAX_RISK_PER_TRADE=5.0   # Nunca subirá de 5.0%
```

### Desactivar (usar riesgo fijo)

```bash
ENABLE_DYNAMIC_RISK=False
RISK_PER_TRADE=2.0  # Valor fijo
```

---

## 🛡️ Protecciones de Seguridad

1. **Límites Estrictos:**
   - Riesgo mínimo: 0.5% (nunca menos)
   - Riesgo máximo: 5.0% (nunca más)

2. **Ajustes Graduales:**
   - Aumentos: Máximo +15% por ajuste
   - Reducciones: Máximo -30% por ajuste

3. **Período de Evaluación:**
   - Mínimo 7 días entre ajustes
   - Requiere datos suficientes

4. **Emergency Stop:**
   - Si drawdown > 20%, detiene trading
   - Independiente del ajuste de riesgo

---

## 📈 Estrategia de Ajuste

| Score | Rendimiento | Ajuste | Factor |
|-------|-------------|--------|--------|
| 80-100 | Excelente 🟢 | +15% | 1.15x |
| 60-79 | Bueno 🟡 | +5% | 1.05x |
| 40-59 | Neutro ⚪ | 0% | 1.0x |
| 20-39 | Malo 🟠 | -15% | 0.85x |
| 0-19 | Crítico 🔴 | -30% | 0.70x |

---

## 💡 Ventajas

1. **Maximiza Ganancias:**
   - Aumenta riesgo cuando funciona bien
   - Aprovecha rachas ganadoras

2. **Protege Capital:**
   - Reduce riesgo cuando hay problemas
   - Evita pérdidas grandes

3. **Adaptación Automática:**
   - No necesitas ajustar manualmente
   - El bot aprende de su experiencia

4. **Conservador por Defecto:**
   - Prefiere reducir riesgo ante dudas
   - Protección de capital es prioridad

---

## 🔍 Monitoreo

El bot registra cada ajuste en los logs:

```
2025-12-22 10:00:00 | INFO | 🔧 AJUSTE DINÁMICO DE RIESGO
2025-12-22 10:00:00 | INFO | Score de Rendimiento: 85/100
2025-12-22 10:00:00 | INFO | Riesgo: 2.0% → 2.3% (+15%)
2025-12-22 10:00:00 | INFO | Posición Máx: 20.0% → 23.0% (+15%)
2025-12-22 10:00:00 | INFO | Razón: Rendimiento excelente
```

También puedes ver en el dashboard:

- Historial de ajustes
- Score de rendimiento actual
- Próximo ajuste programado

---

## ⚠️ Recomendaciones

1. **Empieza Conservador:**

   ```bash
   RISK_PER_TRADE=1.0  # Inicial bajo
   MAX_RISK_PER_TRADE=3.0  # Límite conservador
   ```

2. **Monitorea los Primeros Ajustes:**
   - Revisa los logs semanalmente
   - Verifica que los ajustes sean razonables

3. **Ajusta Límites Según tu Tolerancia:**

   ```bash
   # Muy conservador
   MIN_RISK_PER_TRADE=0.5
   MAX_RISK_PER_TRADE=2.0
   
   # Agresivo
   MIN_RISK_PER_TRADE=1.0
   MAX_RISK_PER_TRADE=5.0
   ```

4. **Combina con Paper Trading:**
   - Valida en PAPER mode primero
   - Observa cómo se ajusta el riesgo
   - Luego pasa a LIVE

---

## 🎓 Filosofía del Sistema

> "El bot debe ser agresivo cuando tiene razón,
> y conservador cuando se equivoca"

El sistema de auto-configuración implementa esta filosofía:

- **Éxito → Más confianza → Más riesgo**
- **Fracaso → Menos confianza → Menos riesgo**

Es como un trader humano experimentado que:

- Aumenta posiciones cuando está en racha
- Reduce exposición cuando pierde
- Aprende de sus errores
- Se adapta al mercado

**Pero sin emociones, con disciplina perfecta** 🤖

---

## 📝 Ejemplo de Uso en Código

```python
from src.risk.dynamic_risk_config import DynamicRiskConfigurator

# Crear configurador
risk_config = DynamicRiskConfigurator(
    initial_risk_per_trade=2.0,
    min_risk=0.5,
    max_risk=5.0
)

# Cada 7 días, el bot:
if risk_config.should_adjust():
    # Analiza rendimiento
    performance = risk_config.analyze_performance(trades)
    
    # Ajusta riesgo
    adjustment = risk_config.adjust_risk_levels(performance)
    
    # Muestra recomendación
    print(risk_config.get_recommendation(performance))
    
    # Usa nuevos niveles
    new_risk = risk_config.current_risk_per_trade
    new_position = risk_config.current_max_position
```

---

**¡El bot ahora se auto-configura para maximizar ganancias y minimizar pérdidas!** 🚀
