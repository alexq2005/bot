# Configuración del Bot - Guía de Migración

## 📋 **IMPORTANTE: Nueva Arquitectura de Configuración**

A partir de ahora, el archivo `.env` **solo contiene credenciales**.  
Todas las configuraciones del bot están en `data/bot_config.json`.

---

## 🔑 **`.env` - Solo Credenciales**

El archivo `.env` ahora solo contiene:

- Credenciales de IOL
- API Keys de servicios externos
- Tokens de Telegram
- Configuraciones de base de datos y logging

**NO contiene:**

- Modo de operación (MOCK/PAPER/LIVE)
- Parámetros de trading
- Configuraciones de riesgo
- Configuraciones de ML

---

## ⚙️ **`data/bot_config.json` - Configuraciones del Bot**

Todas las configuraciones del bot están ahora en `data/bot_config.json`:

```json
{
  "mode": "mock",                    // mock, paper, live
  "symbol_categories": ["acciones", "cedears"],
  "max_symbols": 20,
  "risk_per_trade": 2.0,
  "stop_loss": 5.0,
  "take_profit": 10.0,
  // ... más configuraciones
}
```

---

## 🎯 **Cómo Configurar el Bot**

### **Opción 1: Dashboard (Recomendado)** ⭐

1. Abre el dashboard: `streamlit run src/dashboard/app.py --server.port 8501`
2. Ve al tab "⚙️ Configuración"
3. Ajusta los parámetros
4. Click en "💾 Guardar Configuración"
5. Reinicia el bot

### **Opción 2: Editar Manualmente**

1. Edita `data/bot_config.json`
2. Guarda el archivo
3. Reinicia el bot

---

## 🔄 **Migración desde .env Antiguo**

Si tienes un `.env` antiguo con configuraciones del bot:

1. **Copia el template:**

   ```bash
   cp docs/bot_config.template.json data/bot_config.json
   ```

2. **Transfiere tus configuraciones:**
   - `MOCK_MODE` → `"mode": "mock"`
   - `RISK_PER_TRADE` → `"risk_per_trade": 2.0`
   - `STOP_LOSS_PERCENT` → `"stop_loss": 5.0`
   - etc.

3. **Limpia tu `.env`:**
   - Usa el nuevo `.env.template` como referencia
   - Deja solo credenciales

---

## 📝 **Ejemplo de Migración**

### **Antes (.env):**

```bash
MOCK_MODE=True
RISK_PER_TRADE=2.0
STOP_LOSS_PERCENT=5.0
USE_RL_AGENT=True
```

### **Después:**

**`.env` (solo credenciales):**

```bash
IOL_USERNAME=tu_usuario
IOL_PASSWORD=tu_password
TELEGRAM_BOT_TOKEN=tu_token
```

**`data/bot_config.json` (configuraciones):**

```json
{
  "mode": "mock",
  "risk_per_trade": 2.0,
  "stop_loss": 5.0,
  "use_rl_agent": true
}
```

---

## ✅ **Ventajas de la Nueva Arquitectura**

- ✅ Separación clara de credenciales y configuraciones
- ✅ Cambios de configuración sin tocar `.env`
- ✅ Configuración desde el dashboard
- ✅ Versionado más limpio (`.env` no cambia)
- ✅ Más seguro (credenciales separadas)

---

## 🚀 **Inicio Rápido**

1. **Copia los templates:**

   ```bash
   cp .env.template .env
   cp docs/bot_config.template.json data/bot_config.json
   ```

2. **Edita `.env` con tus credenciales**

3. **Configura el bot desde el dashboard**

4. **Inicia el bot:**

   ```bash
   python main.py
   ```

¡Listo! El bot leerá automáticamente de `bot_config.json`.
