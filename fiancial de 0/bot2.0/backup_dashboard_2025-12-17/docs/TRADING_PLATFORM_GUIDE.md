# 📈 Guía de Uso - Trading Platform Dashboard

## 🎯 PLATAFORMA COMPLETA DE TRADING

El dashboard ahora es una **plataforma completa** donde puedes:

1. ✅ Ver análisis y recomendaciones del bot
2. ✅ Operar manualmente
3. ✅ Ver tu portfolio real de IOL
4. ✅ Ver saldo y posiciones
5. ✅ Recibir señales de trading en tiempo real

---

## 🚀 CÓMO USAR

### **Iniciar la Plataforma:**

```bash
streamlit run src/dashboard/trading_platform.py --server.port 8502
```

**URL:** <http://localhost:8502>

---

## 📊 TABS DISPONIBLES

### **1. 🏠 Overview**

**Vista general del sistema:**

- Estado del mercado (ABIERTO/CERRADO)
- Estado del bot (ACTIVO/DETENIDO)
- Modo de operación (MOCK/PAPER/LIVE)
- Resumen rápido del portfolio
- Valor total de posiciones

**Uso:** Vista rápida del estado general

---

### **2. 📊 Análisis & Señales**

**Recomendaciones del bot en tiempo real:**

**Muestra:**

- Señales activas (BUY/SELL/HOLD)
- Nivel de confianza (%)
- Precio actual
- Precio objetivo
- Stop loss
- Razón del análisis

**Filtros:**

- Por acción (BUY/SELL/HOLD)
- Por confianza mínima
- Ordenar por confianza/símbolo/precio

**Botón:** "🎯 Operar" - Te lleva directo al panel de operación

**Uso:** Ver qué recomienda el bot y decidir si operar

---

### **3. 💼 Mi Portfolio**

**Tu portfolio real desde IOL:**

**Muestra:**

- Valor total del portfolio
- Costo total (inversión inicial)
- P&L total (ganancia/pérdida)
- Número de posiciones
- Tabla detallada de cada posición
- Gráfico de distribución (pie chart)

**Datos en tiempo real desde IOL**

**Uso:** Ver tu situación actual de inversiones

---

### **4. 🎯 Operar**

**Panel de operación manual:**

**Formulario:**

- Símbolo (ej: GGAL)
- Acción (BUY/SELL)
- Cantidad
- Precio
- Total calculado automáticamente

**Botón:** "🚀 Ejecutar Orden"

**Información del activo:**

- Precio actual
- Volumen
- Datos relevantes

**Uso:** Ejecutar trades manualmente con asistencia del bot

---

### **5. 📈 Rendimiento**

**Análisis de rendimiento histórico:**

- Gráficos de P&L
- Métricas de rendimiento
- Win rate
- Sharpe ratio
- Drawdown

**Uso:** Analizar tu rendimiento histórico

---

## 🎮 FLUJO DE USO TÍPICO

### **Escenario 1: Seguir Recomendaciones del Bot**

1. Abre tab "📊 Análisis & Señales"
2. Revisa las señales activas
3. Filtra por confianza > 70%
4. Lee la razón del análisis
5. Click en "🎯 Operar"
6. Ajusta cantidad si es necesario
7. Click "🚀 Ejecutar Orden"

### **Escenario 2: Operar Manualmente**

1. Abre tab "🎯 Operar"
2. Ingresa símbolo
3. Selecciona BUY o SELL
4. Ingresa cantidad y precio
5. Verifica el total
6. Click "🚀 Ejecutar Orden"

### **Escenario 3: Monitorear Portfolio**

1. Abre tab "💼 Mi Portfolio"
2. Ve tus posiciones actuales
3. Revisa P&L de cada posición
4. Analiza distribución del portfolio
5. Decide si rebalancear

---

## 🔄 INTEGRACIÓN CON IOL

### **Portfolio Real:**

El dashboard se conecta directamente con IOL para obtener:

- Posiciones actuales
- Precios en tiempo real
- Saldo disponible
- Órdenes pendientes

### **Ejecución de Trades:**

Cuando ejecutas una orden:

1. Se envía directamente a IOL
2. IOL procesa la orden
3. Recibes confirmación
4. Se actualiza tu portfolio

---

## ⚙️ CONFIGURACIÓN

### **Modo MOCK:**

- Usa datos simulados
- No ejecuta trades reales
- Perfecto para practicar

### **Modo PAPER:**

- Usa precios reales de IOL
- Simula ejecución de trades
- No arriesga dinero real

### **Modo LIVE:**

- Conecta con IOL real
- Ejecuta trades reales
- ⚠️ Usa dinero real

---

## 📱 ACCESO RÁPIDO

**Dashboard Principal (Control):**

```
http://localhost:8501
```

**Trading Platform (Operar):**

```
http://localhost:8502
```

---

## 💡 CONSEJOS

### **Para Principiantes:**

1. Empieza en modo MOCK
2. Sigue las recomendaciones del bot
3. Usa confianza > 70%
4. Opera con cantidades pequeñas

### **Para Intermedios:**

1. Combina análisis del bot con tu criterio
2. Ajusta cantidades según tu riesgo
3. Monitorea tu portfolio regularmente
4. Usa stop loss siempre

### **Para Avanzados:**

1. Usa el bot como segunda opinión
2. Opera manualmente cuando veas oportunidades
3. Optimiza tu portfolio activamente
4. Analiza métricas de rendimiento

---

## 🚨 IMPORTANTE

### **Antes de Operar en LIVE:**

1. ✅ Prueba en MOCK primero
2. ✅ Verifica credenciales de IOL
3. ✅ Confirma que tienes saldo
4. ✅ Entiende los riesgos
5. ✅ Usa stop loss

### **Seguridad:**

- Nunca compartas tus credenciales
- Usa contraseñas fuertes
- Revisa cada orden antes de ejecutar
- Monitorea tu portfolio regularmente

---

## 🎯 PRÓXIMOS PASOS

1. **Inicia la plataforma:**

   ```bash
   streamlit run src/dashboard/trading_platform.py --server.port 8502
   ```

2. **Explora cada tab**

3. **Configura tu universo de símbolos**

4. **Inicia el bot para generar señales**

5. **¡Empieza a operar!**

---

**¡Disfruta de tu plataforma de trading profesional!** 🚀
