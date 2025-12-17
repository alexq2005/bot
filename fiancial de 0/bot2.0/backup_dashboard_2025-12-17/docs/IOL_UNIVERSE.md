# 🌐 Universo Completo IOL - Todas las Herramientas

## 📊 RESUMEN DEL UNIVERSO

**Total de Instrumentos:** ~150+

### Categorías Disponibles

1. **Acciones Argentinas** - 42 símbolos
2. **CEDEARs** - 40 símbolos
3. **Bonos Soberanos** - 12 símbolos
4. **Letras del Tesoro** - 4 símbolos
5. **Obligaciones Negociables** - 4 símbolos

---

## 📈 ACCIONES ARGENTINAS (42)

### Panel General - Más Líquidos (Top 10)

1. **GGAL** - Grupo Financiero Galicia
2. **YPFD** - YPF
3. **PAMP** - Pampa Energía
4. **BMA** - Banco Macro
5. **ALUA** - Aluar
6. **TXAR** - Ternium Argentina
7. **COME** - Sociedad Comercial del Plata
8. **EDN** - Edenor
9. **LOMA** - Loma Negra
10. **MIRG** - Mirgor

### Otros Líquidos

- TRAN, CRES, TGSU2, CEPU, VALO
- SUPV, BBAR, BYMA, TGNO4, AGRO
- HARG, BOLT, DGCU2, METR, SEMI
- IRSA, MOLI, CAPX, CARC, CTIO
- DYCA, FERR, GBAN, GCLA, GRIM
- INTR, LONG, OEST, RICH, ROSE
- SAMI, TECO2

---

## 🌎 CEDEARS (40)

### Tech Giants

- **AAPL** - Apple
- **GOOGL** - Google (Alphabet)
- **MSFT** - Microsoft
- **AMZN** - Amazon
- **META** - Meta (Facebook)
- **TSLA** - Tesla
- **NVDA** - NVIDIA
- **NFLX** - Netflix

### Finance

- **JPM** - JPMorgan Chase
- **BAC** - Bank of America
- **WFC** - Wells Fargo
- **GS** - Goldman Sachs
- **V** - Visa
- **MA** - Mastercard
- **PYPL** - PayPal

### Consumer

- **KO** - Coca-Cola
- **PEP** - PepsiCo
- **WMT** - Walmart
- **NKE** - Nike
- **MCD** - McDonald's
- **SBUX** - Starbucks
- **DIS** - Disney

### Energy

- **XOM** - ExxonMobil
- **CVX** - Chevron

### Healthcare

- **JNJ** - Johnson & Johnson
- **PFE** - Pfizer
- **ABBV** - AbbVie

### Industrial

- **BA** - Boeing
- **CAT** - Caterpillar
- **GE** - General Electric

### Tech Latam

- **MELI** - MercadoLibre
- **GLOB** - Globant

### Otros

- **GOLD** - Barrick Gold
- **VALE** - Vale
- **DESP** - Despegar

---

## 💰 BONOS SOBERANOS (12)

### Bonos en USD - Ley Argentina

- **AL30** - Bono Argentina 2030
- **AL35** - Bono Argentina 2035
- **AL41** - Bono Argentina 2041

### Bonos en USD - Ley Nueva York

- **GD30** - Bono Argentina 2030 (Ley NY)
- **GD35** - Bono Argentina 2035 (Ley NY)
- **GD41** - Bono Argentina 2041 (Ley NY)
- **GD46** - Bono Argentina 2046 (Ley NY)

### Bonos en ARS

- **T2V4** - Bono del Tesoro
- **TO26** - Bono del Tesoro 2026
- **TZX26** - Bono CER 2026

### Bonares

- **AE38** - Bonar 2038
- **DICA** - Bono Discount

---

## 📜 LETRAS DEL TESORO (4)

- **S31O4** - LEDE (Letra del Tesoro)
- **S30N4** - LEDE
- **S30D4** - LEDE
- **S31E5** - LEDE

---

## 🏢 OBLIGACIONES NEGOCIABLES (4)

- **TVPP** - Telecom ON
- **PAMP** - Pampa ON
- **YPF** - YPF ON
- **IRSA** - IRSA ON

---

## 🎯 RECOMENDACIONES POR PERFIL

### Conservador (Bajo Riesgo)

```python
symbols = [
    # Bonos soberanos
    'AL30', 'GD30', 'TO26',
    # Acciones blue chips
    'GGAL', 'YPFD', 'BMA',
    # CEDEARs estables
    'KO', 'JNJ', 'WMT'
]
```

### Moderado (Riesgo Medio)

```python
symbols = [
    # Acciones líquidas
    'GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA',
    # CEDEARs tech
    'AAPL', 'MSFT', 'GOOGL',
    # Bonos
    'AL30', 'GD35'
]
```

### Agresivo (Alto Riesgo)

```python
symbols = [
    # Acciones volátiles
    'COME', 'EDN', 'MIRG', 'TRAN',
    # CEDEARs tech growth
    'TSLA', 'NVDA', 'META', 'NFLX',
    # Latam tech
    'MELI', 'GLOB'
]
```

### Diversificado (Recomendado)

```python
symbols = [
    # Acciones (40%)
    'GGAL', 'YPFD', 'PAMP', 'BMA',
    # CEDEARs (40%)
    'AAPL', 'MSFT', 'MELI', 'KO',
    # Bonos (20%)
    'AL30', 'GD30'
]
```

---

## 🔧 CONFIGURACIÓN EN EL BOT

### Opción 1: Usar Universo Completo

```bash
# .env
USE_DYNAMIC_SYMBOLS=True
MAX_SYMBOLS=150
SYMBOL_CATEGORIES=acciones,cedears,bonos
```

### Opción 2: Solo Acciones

```bash
USE_DYNAMIC_SYMBOLS=True
MAX_SYMBOLS=42
SYMBOL_CATEGORIES=acciones
```

### Opción 3: Solo CEDEARs

```bash
USE_DYNAMIC_SYMBOLS=True
MAX_SYMBOLS=40
SYMBOL_CATEGORIES=cedears
```

### Opción 4: Mixto (Recomendado)

```bash
USE_DYNAMIC_SYMBOLS=True
MAX_SYMBOLS=20
SYMBOL_CATEGORIES=acciones,cedears
```

---

## 📊 FILTROS DISPONIBLES

### Por Liquidez

```python
# Top 10 más líquidos
symbols = market_manager.get_recommended_symbols(max_symbols=10)

# Top 50 más líquidos
symbols = market_manager.get_recommended_symbols(max_symbols=50)
```

### Por Categoría

```python
# Solo acciones argentinas
symbols = market_manager.get_symbols_by_category('acciones')

# Solo CEDEARs
symbols = market_manager.get_symbols_by_category('cedears')

# Solo bonos
symbols = market_manager.get_symbols_by_category('bonos_soberanos')
```

### Por Volumen

```python
# Mínimo 1M de volumen diario
symbols = market_manager.filter_symbols_by_liquidity(
    symbols=all_symbols,
    min_volume=1000000
)
```

---

## ⚠️ CONSIDERACIONES

### Liquidez

- ✅ **Alta:** Acciones top 10, CEDEARs tech giants
- ⚠️ **Media:** Resto de acciones, CEDEARs mid-cap
- ❌ **Baja:** Algunos bonos, letras

### Volatilidad

- 🔴 **Alta:** CEDEARs tech, acciones pequeñas
- 🟡 **Media:** Acciones blue chips
- 🟢 **Baja:** Bonos, letras

### Horarios

- **Acciones/CEDEARs:** 11:00 - 17:00
- **Bonos:** 11:00 - 17:00
- **Futuros/Opciones:** Horario extendido

---

## 🚀 PRÓXIMOS PASOS

1. **Implementar filtros por categoría**
2. **Agregar selector en dashboard**
3. **Integrar con bot**
4. **Optimizar por liquidez**

---

**Total Universo IOL:** ~150+ instrumentos
**Recomendado para empezar:** 10-20 símbolos más líquidos
