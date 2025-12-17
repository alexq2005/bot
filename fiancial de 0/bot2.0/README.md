# Professional IOL Trading Bot v2.0 (SOTA)

🤖 **Sistema de Trading Algorítmico de Nivel Institucional** con Inteligencia Artificial Evolutiva

## 🌟 Características Principales

### 🧠 Inteligencia Artificial Multicapa

- **Deep Reinforcement Learning (PPO)**: Agente que aprende de sus propias operaciones
- **FinBERT Sentiment Analysis**: Comprensión de lenguaje financiero en tiempo real
- **Análisis Técnico Avanzado**: RSI, MACD, ATR, Bollinger Bands
- **Estrategia de Consenso Híbrido**: Combina múltiples fuentes para decisiones robustas

### 💼 Gestión de Riesgo Profesional

- **Position Sizing Dinámico**: Basado en volatilidad (ATR)
- **Risk Management Institucional**: Límites de concentración y drawdown
- **Stop Loss / Take Profit Automáticos**: Protección de capital

### 📊 Observabilidad Total

- **Dashboard Web (Streamlit)**: Monitoreo en tiempo real
- **Base de Datos SQLite**: Auditoría completa de operaciones
- **Logging Estructurado**: Trazabilidad de todas las decisiones

### 🐳 Despliegue Profesional

- **Docker & Docker Compose**: Containerización completa
- **Modo MOCK**: Testing seguro sin riesgo
- **Modo LIVE**: Trading real con dinero real

---

## 🚀 Instalación Rápida

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd bot2.0

# 2. Configurar variables de entorno
cp .env.template .env
# Editar .env con tus credenciales

# 3. Construir y ejecutar
docker-compose up -d

# 4. Ver logs
docker-compose logs -f bot

# 5. Acceder al dashboard
# Abrir http://localhost:8501 en tu navegador
```

### Opción 2: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
cp .env.template .env
# Editar .env con tus credenciales

# 4. Ejecutar bot
python main.py

# 5. Ejecutar dashboard (en otra terminal)
streamlit run src/dashboard/app.py
```

---

## ⚙️ Configuración

### Variables de Entorno Principales

```bash
# Modo de operación
MOCK_MODE=True  # True = Simulación, False = Dinero Real

# Credenciales IOL
IOL_USERNAME=tu_usuario
IOL_PASSWORD=tu_contraseña

# Símbolos a operar
TRADING_SYMBOLS=GGAL,YPFD,PAMP,ALUA,BMA

# Gestión de Riesgo
RISK_PER_TRADE=2.0  # 2% de riesgo por operación
MAX_POSITION_SIZE=20.0  # Máximo 20% por activo

# AI/ML
USE_RL_AGENT=True
USE_SENTIMENT_ANALYSIS=True
```

Ver `.env.template` para configuración completa.

---

## 📖 Uso

### Modo MOCK (Simulación)

```bash
# En .env
MOCK_MODE=True
MOCK_INITIAL_CAPITAL=1000000

# Ejecutar
python main.py
```

El bot operará con datos simulados y dinero virtual. **Perfecto para testing y aprendizaje.**

### Modo LIVE (Dinero Real)

⚠️ **ADVERTENCIA**: Esto opera con dinero real. Asegúrate de:

1. Haber probado extensivamente en modo MOCK
2. Entender completamente la estrategia
3. Configurar límites de riesgo apropiados

```bash
# En .env
MOCK_MODE=False

# Ejecutar
python main.py
```

---

## 🧪 Entrenamiento del Modelo RL

```bash
# Entrenar agente PPO con datos históricos
python scripts/train_model.py --symbols GGAL,YPFD --timesteps 100000

# Evaluar modelo
python scripts/evaluate_model.py --model ./models/ppo_trading_agent.zip
```

---

## 📊 Dashboard

El dashboard web proporciona:

- ✅ **Métricas en Tiempo Real**: Win rate, P&L, Sharpe ratio
- ✅ **Curva de Equidad**: Visualización de rendimiento
- ✅ **Distribución de Portafolio**: Pie chart de asignación
- ✅ **Análisis de Sentimiento**: Timeline de noticias
- ✅ **Historial de Trades**: Tabla completa de operaciones

Acceder en: `http://localhost:8501`

---

## 🏗️ Arquitectura

```
bot2.0/
├── src/
│   ├── api/              # Clientes IOL (real y mock)
│   ├── analysis/         # Análisis técnico
│   ├── ai/               # ML (PPO, FinBERT, News)
│   ├── bot/              # Orquestador principal
│   ├── database/         # SQLAlchemy models
│   ├── dashboard/        # Streamlit UI
│   ├── risk/             # Gestión de riesgo
│   ├── strategy/         # Estrategia híbrida
│   └── utils/            # Utilidades
├── data/                 # Base de datos SQLite
├── logs/                 # Archivos de log
├── models/               # Modelos ML entrenados
├── main.py               # Punto de entrada
├── docker-compose.yml    # Orquestación Docker
└── requirements.txt      # Dependencias Python
```

---

## 🔬 Estrategia de Trading

### Sistema de Consenso Híbrido

El bot requiere **alineación de múltiples fuentes** para ejecutar una operación:

#### Señal de COMPRA requiere

1. ✅ **Técnico**: RSI sobrevendido (<30) O MACD cruce alcista
2. ✅ **RL Agent**: Predicción "BUY"
3. ✅ **Sentimiento**: Score positivo (>0.3)

#### Señal de VENTA requiere

1. ✅ **Técnico**: RSI sobrecomprado (>70) O MACD cruce bajista
2. ✅ **RL Agent**: Predicción "SELL"
3. ✅ **Sentimiento**: Score negativo (<-0.3)

**Umbral de Consenso**: 60% (configurable)

---

## 📈 Gestión de Riesgo

### Position Sizing Dinámico

```python
# Basado en ATR (Average True Range)
Position Size = (Account Balance × Risk%) / (ATR × 2)

# Ejemplo:
# Balance: $1,000,000
# Risk: 2%
# ATR: $100
# Position Size = ($1,000,000 × 0.02) / ($100 × 2) = 100 acciones
```

### Límites de Protección

- ✅ Máximo 20% del portafolio por activo
- ✅ Máximo 10% de riesgo total del portafolio
- ✅ Stop loss automático en 5%
- ✅ Take profit automático en 10%
- ✅ Drawdown máximo: 20%

---

## 🤝 Contribuciones

Este es un proyecto de código abierto. Contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## ⚠️ Disclaimer

**IMPORTANTE**: Este software es para fines educativos y de investigación. El trading algorítmico conlleva riesgos significativos:

- ❌ No garantiza ganancias
- ❌ Puede resultar en pérdidas de capital
- ❌ Los resultados pasados no garantizan resultados futuros
- ❌ Usa bajo tu propio riesgo

**Recomendaciones**:

- Comienza con modo MOCK
- Prueba extensivamente antes de usar dinero real
- Nunca inviertas más de lo que puedes permitirte perder
- Consulta con un asesor financiero profesional

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles

---

## 📞 Soporte

- 📧 Email: <support@example.com>
- 💬 Discord: [Link al servidor]
- 📚 Documentación: [Link a docs]

---

## 🙏 Agradecimientos

- **Invertir Online (IOL)**: Por proporcionar la API
- **HuggingFace**: Por FinBERT
- **OpenAI**: Por Stable-Baselines3
- **Streamlit**: Por el framework de dashboard

---

**Desarrollado con ❤️ para la comunidad de trading algorítmico**

🚀 **¡Happy Trading!** 🚀
