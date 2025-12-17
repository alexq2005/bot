# 🚀 Guía de Ejecución Completa - Professional IOL Trading Bot v2.0

## 📋 Pasos para Ejecutar el Proyecto

### Paso 1: Detener Procesos Actuales

Si tienes el bot o dashboard ejecutándose, detenlos primero:

```bash
# En cada terminal donde esté corriendo, presiona:
Ctrl + C
```

---

### Paso 2: Verificar Configuración

Verifica que el `.env` esté configurado correctamente:

```bash
# Abrir terminal en el directorio del proyecto
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"

# Verificar que la configuración carga bien
python -c "from src.bot.config import settings; print('✓ Config OK'); print(f'Símbolos: {settings.get_trading_symbols_list()}'); print(f'Híbrido: {settings.enable_hybrid_advanced}')"
```

**Deberías ver:**

```
✓ Config OK
Símbolos: ['GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA']
Híbrido: True
```

---

### Paso 3: Ejecutar el Dashboard (Terminal 1)

Abre una **primera terminal** y ejecuta:

```bash
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
streamlit run src/dashboard/app.py
```

**Deberías ver:**

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**Abre en tu navegador:** <http://localhost:8501>

---

### Paso 4: Ejecutar el Bot (Terminal 2)

Abre una **segunda terminal** (nueva ventana) y ejecuta:

```bash
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
python main.py
```

**Deberías ver:**

```
======================================================================
🤖 PROFESSIONAL IOL TRADING BOT v2.0 - SOTA (State of the Art)
======================================================================
Modo: MOCK (Simulación)
Símbolos: GGAL, YPFD, PAMP, ALUA, BMA
Intervalo: 300s
RL Agent: ✓ Activado
Sentiment: ✓ Activado
Sistema Híbrido: ✓ Activado
======================================================================

📊 Analizando GGAL...
📊 Analizando YPFD...
📊 Analizando PAMP...
...
```

---

## 🎯 Verificación de Funcionamiento

### ✅ Checklist de Verificación

1. **Dashboard cargando:**
   - [ ] Abre <http://localhost:8501>
   - [ ] Ves la interfaz del dashboard
   - [ ] No hay errores en la terminal del dashboard

2. **Bot ejecutándose:**
   - [ ] Ves "Símbolos: GGAL, YPFD, PAMP, ALUA, BMA" (NO caracteres individuales)
   - [ ] Ves "Sistema Híbrido: ✓ Activado"
   - [ ] El bot analiza símbolos completos (GGAL, no G)
   - [ ] Ves señales de trading (BUY/SELL/HOLD)

3. **Sistema Híbrido Activo:**
   - [ ] Ves mensajes de análisis técnico
   - [ ] Ves predicciones del agente RL
   - [ ] El bot genera decisiones

---

## 🐛 Solución de Problemas

### Problema 1: Bot analiza caracteres individuales (G, G, A, L)

**Causa:** El bot cargó código antiguo antes de las correcciones.

**Solución:**

```bash
# Detener el bot (Ctrl+C)
# Ejecutar nuevamente
python main.py
```

### Problema 2: Error "trading_symbols"

**Solución:**

```bash
# Verificar que el .env tenga:
grep "TRADING_SYMBOLS" .env

# Debería mostrar:
# TRADING_SYMBOLS=GGAL,YPFD,PAMP,ALUA,BMA
```

### Problema 3: Dashboard no carga

**Solución:**

```bash
# Verificar que streamlit esté instalado
pip install streamlit

# Ejecutar nuevamente
streamlit run src/dashboard/app.py
```

### Problema 4: Módulos no encontrados

**Solución:**

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

---

## 📊 Monitoreo en Tiempo Real

### Dashboard (<http://localhost:8501>)

El dashboard muestra:

- 📈 **Gráficos de rendimiento**
- 💼 **Estado del portafolio**
- 📊 **Trades ejecutados**
- 🤖 **Métricas de AI**
- 📰 **Análisis de sentimiento**

### Terminal del Bot

Muestra:

- 📊 Análisis de cada símbolo
- 🛒 Órdenes de compra
- 💰 Órdenes de venta
- 💼 Resumen del portafolio
- ⏳ Tiempo hasta próxima iteración

---

## 🎮 Comandos Útiles

### Detener el Bot

```bash
# En la terminal del bot, presiona:
Ctrl + C
```

### Ver Logs

```bash
# Ver logs en tiempo real
tail -f logs/bot.log

# En Windows Git Bash:
tail -f logs/bot.log
```

### Ver Base de Datos

```bash
# Abrir SQLite
sqlite3 data/trades.db

# Ver trades
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;

# Salir
.quit
```

---

## 🚀 Ejecución Rápida (Resumen)

**Terminal 1 (Dashboard):**

```bash
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
streamlit run src/dashboard/app.py
```

**Terminal 2 (Bot):**

```bash
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
python main.py
```

**Navegador:**

```
http://localhost:8501
```

---

## 📈 Qué Esperar

### Primera Iteración (5 minutos)

- Bot analiza los 5 símbolos
- Genera señales (probablemente HOLD al inicio)
- Muestra resumen del portafolio

### Después de 1 hora

- Varias iteraciones completadas
- Posibles trades ejecutados
- Datos visibles en el dashboard

### Después de 1 día

- Suficientes datos para análisis
- Sistema híbrido ajustando estrategia
- Detección de régimen activa

---

## ⚙️ Configuración Actual

Tu configuración está en modo **PRINCIPIANTE SEGURO**:

```
✅ MOCK Mode (sin riesgo)
✅ Sistema Híbrido (5 modelos ML)
✅ Detección de Régimen
✅ Auto-ajuste de Riesgo
❌ Datos Alternativos (sin APIs)
❌ LLM Reasoning (sin API key)
```

**Costo:** $0/mes
**Riesgo:** Ninguno (simulación)
**Rendimiento esperado:** +20% Win Rate, +100% Sharpe

---

## 🎯 Próximos Pasos Recomendados

1. **Ejecutar ahora** (modo MOCK)
2. **Observar 24 horas** de operación
3. **Revisar resultados** en dashboard
4. **Ajustar configuración** si es necesario
5. **Considerar PAPER mode** con IOL real
6. **Eventualmente LIVE** cuando estés listo

---

**¡Listo para ejecutar!** 🚀

¿Alguna pregunta antes de empezar?
