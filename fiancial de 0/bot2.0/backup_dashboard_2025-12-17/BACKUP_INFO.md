# Backup Dashboard - Bot 2.0

**Fecha:** 2025-12-17 10:26
**Versión:** Dashboard v4.0 - Completo

## 📁 Contenido

Este directorio contiene el backup completo del proyecto Bot 2.0 con Dashboard v4.0.

### Estructura

```
backup_dashboard_2025-12-17/
├── src/                    # Código fuente completo
│   ├── api/               # Clientes IOL (Mock, Paper, Real)
│   │   ├── iol_client.py         # Cliente real IOL
│   │   ├── mock_iol_client.py    # Cliente simulado
│   │   └── paper_iol_client.py   # Cliente paper trading
│   ├── dashboard/         # Dashboard Streamlit v4.0
│   │   └── app.py                # Aplicación principal
│   ├── bot/               # Lógica del bot de trading
│   ├── ai/                # Módulos de IA
│   ├── analysis/          # Análisis técnico
│   ├── backtest/          # Backtesting
│   ├── database/          # Base de datos
│   ├── notifications/     # Notificaciones
│   ├── optimization/      # Optimización
│   ├── utils/             # Utilidades
│   └── alternative/       # Datos alternativos
├── docs/                  # Documentación
├── scripts/               # Scripts de utilidad
├── tests/                 # Tests unitarios
├── data/                  # Datos y configuración
├── .env                   # Variables de entorno (CREDENCIALES)
├── .env.example           # Template de variables
├── .gitignore             # Git ignore
├── README.md              # Documentación principal
├── requirements.txt       # Dependencias Python
├── Dockerfile             # Docker
├── docker-compose.yml     # Docker Compose
└── BACKUP_INFO.md         # Este archivo
```

## 🎯 Versión Dashboard v4.0

### Características Principales

#### 1. Cambio de Modo desde Interfaz

- Radio buttons en sidebar para seleccionar MOCK/PAPER/LIVE
- Botón "Aplicar Cambio de Modo" para confirmar
- Configuración persistente en JSON

#### 2. Configuración Avanzada

- Capital inicial (modo MOCK)
- Riesgo por operación
- Stop Loss / Take Profit
- Intervalo de trading
- Todo configurable desde la UI

#### 3. Seguridad para Modo LIVE

- Advertencia prominente en rojo
- Display de precio en rojo
- Checkbox de confirmación obligatorio
- Mensaje claro "Esta operación usará DINERO REAL"

#### 4. Gestión de Precios

- Caché inteligente de precios
- Botón "Actualizar Precio" manual
- Múltiples fallbacks (price, ultimoPrecio, puntas, settlementPrice)
- Soporte para mercado cerrado

#### 5. Tabs del Dashboard

- **Métricas:** Operaciones, P&L, capital, estado de conexión
- **Portafolio:** Lista de activos, distribución, gráficos
- **Operar:** Selección de activos, configuración de órdenes, ejecución
- **Análisis:** Placeholder para análisis futuro

## 🔧 Archivos Clave

### Dashboard (`src/dashboard/app.py`)

- **Clase AppSettings:** Configuración independiente de .env
- **Función get_client():** Obtiene cliente según modo
- **Función render_sidebar():** Sidebar con selector de modo
- **Función render_manual_trading_tab():** Tab de operación manual
- **Función execute_order():** Ejecución de órdenes

### Cliente IOL (`src/api/iol_client.py`)

- **Método get_last_price():** Obtiene precio con fallbacks
- **Método place_market_order():** Ejecuta órdenes de mercado
- **Método get_portfolio():** Obtiene portafolio
- **Método get_account_balance():** Obtiene saldo

### Cliente Mock (`src/api/mock_iol_client.py`)

- Simulación completa sin conexión a IOL
- Precios base para 15 símbolos
- Random walk para variación de precios
- Capital inicial configurable

## 📊 Configuración

### Variables de Entorno (.env)

```bash
IOL_USERNAME=tu_usuario
IOL_PASSWORD=tu_contraseña
IOL_BASE_URL=https://api.invertironline.com
```

### Configuración de Aplicación (data/app_config.json)

```json
{
    "mock_mode": true,
    "paper_mode": false,
    "mock_initial_capital": 1000000.0,
    "trading_interval": 300,
    "risk_per_trade": 2.0,
    "max_position_size": 20.0,
    "stop_loss_percent": 5.0,
    "take_profit_percent": 10.0
}
```

## 🚀 Cómo Usar

### 1. Restaurar desde Backup

```bash
# Desde el directorio bot2.0
cp -r backup_dashboard_2025-12-17/* .
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Credenciales

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales
nano .env
```

### 4. Ejecutar Dashboard

```bash
streamlit run src/dashboard/app.py --server.port 8502
```

### 5. Acceder

Abre tu navegador en: <http://localhost:8502>

## 🎮 Modos de Operación

### 🔧 MOCK (Simulación)

- **Descripción:** Simulación completa sin conexión a IOL
- **Datos:** Completamente simulados
- **Capital:** Configurable desde UI
- **Uso:** Desarrollo y pruebas

### 📊 PAPER (Paper Trading)

- **Descripción:** Trading simulado con datos reales
- **Datos:** Reales de IOL
- **Órdenes:** Simuladas
- **Uso:** Practicar estrategias

### ⚠️ LIVE (Real)

- **Descripción:** Trading con dinero real
- **Datos:** Reales de IOL
- **Órdenes:** REALES
- **Uso:** Operación en producción
- **⚠️ PRECAUCIÓN:** Usa dinero real

## 🔒 Seguridad

### Credenciales

- ⚠️ El archivo `.env` contiene credenciales reales
- ⚠️ NO compartir este backup
- ⚠️ NO subir a repositorios públicos
- ⚠️ Mantener en lugar seguro

### Modo LIVE

- Advertencia clara en la interfaz
- Confirmación obligatoria
- Display en rojo
- Mensaje explícito sobre dinero real

## 📝 Notas

### Persistencia

- La configuración se guarda en `data/app_config.json`
- El modo seleccionado persiste entre sesiones
- Los parámetros de riesgo se guardan automáticamente

### Caché

- Los precios se cachean para evitar requests innecesarias
- Botón "Actualizar Precio" para refrescar manualmente
- El caché se limpia al ejecutar una orden

### Mercado

- Horario: Lunes a Viernes, 11:00-17:00 (Argentina)
- Fuera de horario: Usa precios de cierre
- El dashboard muestra el estado en tiempo real

## 🐛 Solución de Problemas

### Error de autenticación

1. Verifica credenciales en `.env`
2. Usa modo MOCK como fallback
3. Botón "Usar Modo MOCK como fallback" disponible

### Precios en $0.00

1. Haz clic en "Actualizar Precio"
2. Verifica que el mercado esté abierto
3. En modo MOCK, los precios son simulados

### Modo no cambia

1. Haz clic en "Aplicar Cambio de Modo"
2. El dashboard debe reiniciarse
3. Verifica `data/app_config.json`

## 📞 Información Adicional

**Ubicación del backup:**

```
c:\Users\Lexus\.gemini\antigravity\scratch\fiancial de 0\bot2.0\backup_dashboard_2025-12-17\
```

**Versión:** Dashboard v4.0
**Fecha:** 2025-12-17 10:26:13
**Estado:** ✅ Completo y funcional

---

Para más información, consulta el README.md principal del proyecto.
