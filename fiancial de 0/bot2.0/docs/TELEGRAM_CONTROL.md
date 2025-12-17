# 📱 Control del Bot vía Telegram

## 🤖 CONTROL REMOTO DEL BOT

Controla tu bot de trading desde tu celular usando Telegram.

---

## 🚀 CONFIGURACIÓN

### **Paso 1: Crear Bot de Telegram**

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Sigue las instrucciones
4. Copia el **token** que te da

### **Paso 2: Configurar Token**

Edita tu archivo `.env`:

```bash
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id
```

### **Paso 3: Iniciar Controlador**

```bash
python src/notifications/telegram_controller.py
```

---

## 📱 COMANDOS DISPONIBLES

### **Comandos Básicos:**

```
/start - Menú principal con botones
/status - Ver estado del bot
/startbot - Iniciar el bot
/stopbot - Detener el bot
```

### **Menú Interactivo:**

Cuando envías `/start`, recibes un menú con botones:

```
┌─────────────────────────────┐
│  ▶️ Iniciar Bot  ⏸️ Detener  │
├─────────────────────────────┤
│  📊 Estado      💼 Portfolio │
├─────────────────────────────┤
│  📈 Señales     ⚙️ Config    │
└─────────────────────────────┘
```

---

## 🎮 CÓMO USAR

### **Escenario 1: Iniciar el Bot**

1. Abre Telegram
2. Busca tu bot
3. Envía `/start`
4. Click en "▶️ Iniciar Bot"
5. Recibes confirmación

### **Escenario 2: Ver Estado**

1. Envía `/status`
2. Recibes:

   ```
   ✅ Bot ACTIVO
   PID: 12345
   Uptime: 45 minutos
   
   📊 Mercado: ABIERTO ✅
   ```

### **Escenario 3: Detener el Bot**

1. Envía `/start`
2. Click en "⏸️ Detener Bot"
3. Recibes confirmación

### **Escenario 4: Ver Portfolio**

1. Envía `/start`
2. Click en "💼 Portfolio"
3. Recibes resumen de tu portfolio IOL

### **Escenario 5: Ver Señales**

1. Envía `/start`
2. Click en "📈 Señales"
3. Recibes recomendaciones actuales del bot

---

## 🔐 SEGURIDAD

### **Importante:**

- ✅ Solo TÚ puedes controlar el bot
- ✅ Usa el `TELEGRAM_CHAT_ID` para restringir acceso
- ✅ Nunca compartas tu token
- ✅ El bot verifica tu identidad

### **Configurar Chat ID:**

1. Envía un mensaje a tu bot
2. Visita: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Busca tu `chat_id`
4. Agrégalo al `.env`

---

## 🚀 EJECUCIÓN

### **Opción 1: Terminal Separada**

```bash
# Terminal 1: Dashboard
streamlit run src/dashboard/app.py --server.port 8501

# Terminal 2: Telegram Controller
python src/notifications/telegram_controller.py
```

### **Opción 2: Background**

```bash
# Windows
start /B python src/notifications/telegram_controller.py

# Linux/Mac
python src/notifications/telegram_controller.py &
```

---

## 💡 CASOS DE USO

### **Desde el Trabajo:**

- Ver estado del bot
- Detener si hay problemas
- Ver portfolio

### **Desde Casa:**

- Iniciar el bot
- Ver señales
- Ajustar configuración

### **En Movimiento:**

- Monitorear estado
- Recibir alertas
- Control total remoto

---

## 📊 NOTIFICACIONES AUTOMÁTICAS

El bot también puede enviarte notificaciones automáticas:

```python
# En tu código
from src.notifications.telegram_notifier import telegram_notifier

# Enviar alerta
telegram_notifier.send_trade_notification(
    symbol="GGAL",
    action="BUY",
    quantity=10,
    price=1250.50
)
```

---

## 🎯 PRÓXIMAS FUNCIONALIDADES

- [ ] Ejecutar trades desde Telegram
- [ ] Cambiar configuración remotamente
- [ ] Recibir alertas de señales
- [ ] Ver gráficos
- [ ] Historial de trades

---

## ⚙️ CONFIGURACIÓN COMPLETA

```bash
# .env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ENABLED=True
```

---

## 🔧 TROUBLESHOOTING

### **Bot no responde:**

- Verifica el token
- Verifica que el controlador esté corriendo
- Revisa logs

### **No puedo iniciar el bot:**

- Verifica que tengas permisos
- Revisa que el bot no esté ya corriendo

---

## 📱 EJEMPLO DE USO

```
Tú: /start

Bot: 🤖 Professional IOL Trading Bot
     Control remoto del bot de trading.
     Selecciona una opción:
     
     [▶️ Iniciar Bot] [⏸️ Detener Bot]
     [📊 Estado] [💼 Portfolio]
     [📈 Señales] [⚙️ Config]

Tú: [Click en "▶️ Iniciar Bot"]

Bot: ✅ Bot iniciado correctamente
     PID: 12345

Tú: /status

Bot: ✅ Bot ACTIVO
     PID: 12345
     Uptime: 2 minutos
     
     📊 Mercado: ABIERTO ✅
```

---

**¡Controla tu bot desde cualquier lugar!** 📱🚀
