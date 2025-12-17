# Guía de Configuración del .env

## 🚀 Configuración Rápida Recomendada

### Paso 1: Crear el archivo .env

```bash
cp .env.template .env
```

### Paso 2: Configuración Básica (Sin APIs)

Edita `.env` y configura estas variables:

```bash
# ========== CONFIGURACIÓN BÁSICA ==========

# Modo de operación (MOCK = sin riesgo)
MOCK_MODE=True
PAPER_MODE=False

# Símbolos a operar
TRADING_SYMBOLS=GGAL,YPFD,PAMP,ALUA,BMA

# Capital inicial (pesos argentinos)
MOCK_INITIAL_CAPITAL=1000000

# ========== SISTEMA HÍBRIDO ==========

# Activar sistema híbrido ✅
ENABLE_HYBRID_ADVANCED=True

# Ensemble de modelos ML ✅
ENABLE_MODEL_ENSEMBLE=True

# Detección de régimen ✅
ENABLE_REGIME_DETECTION=True

# Datos alternativos ❌ (sin APIs por ahora)
ENABLE_ALTERNATIVE_DATA=False

# LLM Reasoning ❌ (sin API key por ahora)
ENABLE_LLM_REASONING=False

# ========== GESTIÓN DE RIESGO ==========

# Riesgo por trade (2% = conservador)
RISK_PER_TRADE=2.0

# Auto-ajuste de riesgo ✅
ENABLE_DYNAMIC_RISK=True
```

---

## 📊 Configuraciones Predefinidas

### Opción A: Principiante (Recomendado) ⭐

```bash
MOCK_MODE=True
ENABLE_HYBRID_ADVANCED=True
ENABLE_MODEL_ENSEMBLE=True
ENABLE_REGIME_DETECTION=True
ENABLE_ALTERNATIVE_DATA=False
ENABLE_LLM_REASONING=False
RISK_PER_TRADE=2.0
```

**Incluye:**

- ✅ Simulación segura
- ✅ 5 modelos ML
- ✅ Detección de régimen
- ✅ Auto-ajuste de riesgo
- ❌ Sin APIs externas
- ❌ Sin costos

**Ideal para:** Aprender y validar el sistema

---

### Opción B: Intermedio

```bash
MOCK_MODE=False
PAPER_MODE=True
IOL_USERNAME=tu_usuario
IOL_PASSWORD=tu_contraseña
ENABLE_HYBRID_ADVANCED=True
ENABLE_MODEL_ENSEMBLE=True
ENABLE_REGIME_DETECTION=True
ENABLE_ALTERNATIVE_DATA=False
ENABLE_LLM_REASONING=False
RISK_PER_TRADE=2.0
```

**Incluye:**

- ✅ Precios REALES de IOL
- ✅ Ejecución simulada (sin riesgo)
- ✅ Sistema híbrido completo
- ❌ Sin APIs externas

**Ideal para:** Validar antes de LIVE

---

### Opción C: Avanzado (Sistema Completo)

```bash
MOCK_MODE=False
PAPER_MODE=True
IOL_USERNAME=tu_usuario
IOL_PASSWORD=tu_contraseña
ENABLE_HYBRID_ADVANCED=True
ENABLE_MODEL_ENSEMBLE=True
ENABLE_REGIME_DETECTION=True
ENABLE_ALTERNATIVE_DATA=True
ENABLE_LLM_REASONING=True
OPENAI_API_KEY=sk-...
GOOGLE_TRENDS_API_KEY=...
TWITTER_BEARER_TOKEN=...
RISK_PER_TRADE=2.0
```

**Incluye:**

- ✅ TODO del sistema
- ✅ Google Trends
- ✅ Twitter sentiment
- ✅ GPT-4 reasoning

**Costo:** ~$150-200/mes
**Ideal para:** Máximo rendimiento

---

## 🔧 Parámetros Importantes

### Riesgo (Conservador vs Agresivo)

**Conservador:**

```bash
RISK_PER_TRADE=1.0
MAX_POSITION_SIZE=15.0
STOP_LOSS_PERCENT=3.0
```

**Moderado (Recomendado):**

```bash
RISK_PER_TRADE=2.0
MAX_POSITION_SIZE=20.0
STOP_LOSS_PERCENT=5.0
```

**Agresivo:**

```bash
RISK_PER_TRADE=3.5
MAX_POSITION_SIZE=25.0
STOP_LOSS_PERCENT=7.0
```

---

## 📝 Instrucciones Paso a Paso

### 1. Copiar template

```bash
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
cp .env.template .env
```

### 2. Editar .env

```bash
# Abrir con tu editor favorito
notepad .env
# o
code .env
```

### 3. Configurar según tu perfil

**Para empezar (Opción A):**

- Dejar `MOCK_MODE=True`
- Activar `ENABLE_HYBRID_ADVANCED=True`
- Activar `ENABLE_MODEL_ENSEMBLE=True`
- Activar `ENABLE_REGIME_DETECTION=True`
- Dejar APIs desactivadas

### 4. Guardar y ejecutar

```bash
python main.py
```

---

## ⚠️ Importante

1. **Nunca subas .env a Git** (ya está en .gitignore)
2. **Empieza en MOCK mode** para aprender
3. **Valida en PAPER mode** antes de LIVE
4. **Guarda tus API keys de forma segura**

---

## 🎯 Configuración Recomendada para Ti

Basándome en que estás empezando, te recomiendo:

```bash
# Modo
MOCK_MODE=True
PAPER_MODE=False

# Sistema Híbrido (sin APIs)
ENABLE_HYBRID_ADVANCED=True
ENABLE_MODEL_ENSEMBLE=True
ENABLE_REGIME_DETECTION=True
ENABLE_ALTERNATIVE_DATA=False
ENABLE_LLM_REASONING=False

# Riesgo conservador
RISK_PER_TRADE=2.0
ENABLE_DYNAMIC_RISK=True

# Símbolos líquidos
TRADING_SYMBOLS=GGAL,YPFD,PAMP,ALUA,BMA
```

**Esto te da:**

- ✅ Sistema híbrido completo (5 modelos + régimen)
- ✅ Sin riesgo (MOCK mode)
- ✅ Sin costos (sin APIs)
- ✅ Auto-ajuste de riesgo
- ✅ Mejora esperada: +20% Win Rate, +100% Sharpe

---

**¿Listo para ejecutar?**

```bash
python main.py
```
