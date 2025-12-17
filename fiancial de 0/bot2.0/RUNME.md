## EJECUCIÓN DEL BOT EN MODO MOCK

Después de los cambios realizados (configuración de IA), ahora puedes ejecutar el bot en modo MOCK.

### PREREQUISITOS

✅ El archivo `.env` tiene `MOCK_MODE=True`
✅ El archivo `data/bot_config.json` tiene `"mode": "mock"`
✅ El logger está configurado para evitar errores de encoding

### CÓMO EJECUTAR

**Opción 1: En Bash/Terminal Unix (Recomendado)**

```bash
export PYTHONIOENCODING=utf-8
cd "c:/Users/Lexus/.gemini/antigravity/scratch/fiancial de 0/bot2.0"
python run_mock_3days.py
```

**Opción 2: En PowerShell (Windows)**

```powershell
$env:PYTHONIOENCODING='utf-8'
cd "c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0"
python run_mock_3days.py
```

**Opción 3: Comando rápido (Bash)**

```bash
export PYTHONIOENCODING=utf-8 && python "c:/Users/Lexus/.gemini/antigravity/scratch/fiancial de 0/bot2.0/run_mock_3days.py"
```

### QUÉ ESPERAR

El bot mostrará:

1. **Configuración inicial**
   - Modo: MOCK (Simulación)
   - Capital inicial: $10,000,000
   - Símbolos: GGAL, YPFD, CEPU

2. **Loop de trading** (cada 60 segundos)
   - Análisis de cada símbolo
   - Decisiones de compra/venta
   - Monitoreo de posiciones
   - Resumen del portafolio

3. **Logs en tiempo real**
   - Guardados en: `./logs/bot.log`
   - Mostrados en consola

### SALIDA ESPERADA

```
======================================================================
BOT TRADING - MODO MOCK (3 DIAS)
======================================================================
Inicio: 2025-12-16 04:14:49.544995
Fin programado: 2025-12-19 04:14:49.545495
Simbolos: GGAL, YPFD, CEPU
Intervalo: 60 segundos
======================================================================

[OK] Modo MOCK activado (sin riesgo de dinero real)

[*] Inicializando bot...
[INFO] [2025-12-16 04:14:49,545] TradingBot:__init__ - Inicializando Professional IOL Trading Bot v2.0...
[OK] Bot inicializado correctamente

[*] Iniciando trading loop...

======================================================================
[ITERATION #1]
[TIME] 2025-12-16 04:14:52
[REMAINING] 3 days, 0:00:00
======================================================================

[ANALYZE] GGAL...
[INFO] [2025-12-16 04:14:52,084] TradingBot:analyze_symbol - Analizando GGAL...
[SKIP] GGAL: Trade rechazado por risk manager

[ANALYZE] YPFD...
[SKIP] YPFD: Trade rechazado por risk manager

[ANALYZE] CEPU...
[SKIP] CEPU: Trade rechazado por risk manager

[MONITOR] 0 posiciones | SL: 0 | TP: 0

============================================================
RESUMEN DEL PORTAFOLIO
====================================================
Capital Inicial: $10,000,000.00
Valor Actual:    $10,000,000.00
Retorno:         $0.00 (0.00%)
Efectivo:        $10,000,000.00
Posiciones:      0
====================================================

[WAIT] Esperando 60 segundos...
```

### POSIBLES PROBLEMAS

**1. UnicodeEncodeError**
- Solución: Usar `export PYTHONIOENCODING=utf-8`
- Esto configura Python para usar UTF-8 en Windows

**2. Módulos no encontrados**
- Solución: Verificar que estés en el directorio correcto
- `cd "c:/Users/Lexus/.gemini/antigravity/scratch/fiancial de 0/bot2.0"`

**3. Errores de API (429 Too Many Requests)**
- Esto es normal, las APIs de news tienen límites
- El bot continúa funcionando sin este dato

### PRÓXIMOS PASOS (Después de probar MOCK)

1. **Probar en PAPER MODE** (precios reales, sin dinero)
   - Editar `.env`: `PAPER_MODE=true`, `MOCK_MODE=false`
   - Verificar que funciona con datos reales

2. **Integrar módulos de IA** (Phase 1)
   - Anomaly Detector (protección)
   - Dynamic Ensemble (mejora de predicciones)
   - Advanced Transformer (modelo moderno)
   - Explainable AI (transparencia)

3. **Backtesting**
   - `python scripts/run_backtest.py`

### RECURSOS ÚTILES

- Documentación de integración: `docs/AI_ENHANCEMENTS_INTEGRATION.md`
- Checklist de implementación: `docs/IMPLEMENTATION_CHECKLIST.md`
- Índice de mejoras: `docs/AI_IMPROVEMENTS_INDEX.md`

---

**Estado**: ✅ Bot listo para ejecutar en MOCK mode
**Fecha**: 2025-12-16
**Modo actual**: MOCK (seguro, sin dinero real)
