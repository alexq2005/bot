# 🚀 Guía Rápida - Configuración del Universo IOL

## ✅ Configuración Aplicada desde Dashboard

Has seleccionado todas las categorías del universo IOL. Para aplicar esto permanentemente:

---

## 📝 Paso 1: Editar `.env`

Abre el archivo `.env` y agrega o modifica estas líneas:

```bash
# -------------------- SYMBOL UNIVERSE --------------------
# Categorías seleccionadas: TODAS
SYMBOL_CATEGORIES=acciones,cedears,bonos_soberanos,letras,ons

# Límite de símbolos (0 = sin límite, recomendado: 20-50)
MAX_SYMBOLS=30
```

---

## 🎯 Configuraciones Recomendadas

### Opción 1: Solo Acciones y CEDEARs (Recomendado) ⭐

```bash
SYMBOL_CATEGORIES=acciones,cedears
MAX_SYMBOLS=20
```

**Resultado:** ~20 símbolos más líquidos (10 acciones + 10 CEDEARs)

### Opción 2: Diversificado

```bash
SYMBOL_CATEGORIES=acciones,cedears,bonos_soberanos
MAX_SYMBOLS=30
```

**Resultado:** ~30 símbolos (acciones + CEDEARs + bonos)

### Opción 3: Universo Completo

```bash
SYMBOL_CATEGORIES=acciones,cedears,bonos_soberanos,letras,ons
MAX_SYMBOLS=50
```

**Resultado:** ~50 símbolos de todas las categorías

### Opción 4: Solo Acciones Argentinas

```bash
SYMBOL_CATEGORIES=acciones
MAX_SYMBOLS=15
```

**Resultado:** Top 15 acciones argentinas más líquidas

### Opción 5: Solo CEDEARs

```bash
SYMBOL_CATEGORIES=cedears
MAX_SYMBOLS=15
```

**Resultado:** Top 15 CEDEARs más líquidos

---

## 🔄 Paso 2: Reiniciar el Bot

Después de editar `.env`, reinicia el bot:

```bash
# Detener el bot actual (Ctrl+C)
# Luego ejecutar:
python main.py
```

---

## 📊 Categorías Disponibles

| Categoría | Símbolos | Descripción |
|-----------|----------|-------------|
| `acciones` | 42 | Acciones argentinas (GGAL, YPFD, etc.) |
| `cedears` | 40 | CEDEARs (AAPL, MSFT, MELI, etc.) |
| `bonos_soberanos` | 12 | Bonos argentinos (AL30, GD30, etc.) |
| `letras` | 4 | Letras del Tesoro |
| `ons` | 4 | Obligaciones Negociables |

**Total:** ~150 instrumentos

---

## ⚙️ Configuración Actual del Bot

Para ver qué símbolos está usando actualmente el bot:

```bash
python -c "from src.bot.config import settings; print(settings.get_trading_symbols_list())"
```

---

## 💡 Consejos

### Para Principiantes

```bash
SYMBOL_CATEGORIES=acciones
MAX_SYMBOLS=10
```

- Menos símbolos = más fácil de monitorear
- Acciones argentinas son más predecibles

### Para Traders Experimentados

```bash
SYMBOL_CATEGORIES=acciones,cedears
MAX_SYMBOLS=30
```

- Diversificación entre local e internacional
- Mayor oportunidad de trades

### Para Inversores Conservadores

```bash
SYMBOL_CATEGORIES=bonos_soberanos,letras
MAX_SYMBOLS=10
```

- Menor volatilidad
- Instrumentos de renta fija

---

## 🎮 Desde el Dashboard

También puedes cambiar el universo desde el dashboard:

1. Abre <http://localhost:8501>
2. Ve a la sección "🌐 Selector de Universo"
3. Marca/desmarca las categorías
4. Click en "🚀 Aplicar Universo Seleccionado"
5. Sigue las instrucciones que aparecen

---

## ✅ Verificación

Después de reiniciar el bot, verifica que esté usando el universo correcto:

**En el banner del bot:**

```
Símbolos: GGAL, YPFD, PAMP, ALUA, BMA, AAPL, MSFT, ...
```

**En el dashboard:**

- Sidebar → "📊 Estado del Sistema"
- Verás el número de símbolos activos

---

## 🚀 ¡Listo

Tu bot ahora operará con el universo IOL que seleccionaste.

**Dashboard:** <http://localhost:8501>
