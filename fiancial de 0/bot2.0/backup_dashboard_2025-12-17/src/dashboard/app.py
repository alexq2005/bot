"""
IOL Trading Bot Dashboard
Dashboard principal Streamlit para monitoreo, trading manual y análisis
VERSIÓN CON CAMBIO DE MODO DESDE INTERFAZ
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import time
import traceback
import json
from pathlib import Path

# Agregar directorio raíz al path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.market_manager import MarketManager

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="IOL Trading Bot Pro",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CONFIGURACIÓN PERSONALIZADA (SIN .env para modo)
# ==============================================================================
class AppSettings:
    """Configuración de la aplicación que no depende de .env para el modo"""
    
    def __init__(self):
        # Cargar configuración desde archivo JSON o usar defaults
        self.config_file = Path("data/app_config.json")
        self.config = self._load_config()
        
        # Credenciales IOL (SI vienen de .env)
        self.iol_username = os.getenv("IOL_USERNAME", "usuario_demo")
        self.iol_password = os.getenv("IOL_PASSWORD", "password_demo")
        self.iol_base_url = os.getenv("IOL_BASE_URL", "https://api.invertironline.com")
        
        # Modo de operación (se configura desde la UI)
        self.mock_mode = self.config.get("mock_mode", True)
        self.paper_mode = self.config.get("paper_mode", False)
        
        # Parámetros de trading
        self.mock_initial_capital = float(self.config.get("mock_initial_capital", 1000000.0))
        self.trading_interval = int(self.config.get("trading_interval", 300))
        self.risk_per_trade = float(self.config.get("risk_per_trade", 2.0))
        self.max_position_size = float(self.config.get("max_position_size", 20.0))
        self.stop_loss_percent = float(self.config.get("stop_loss_percent", 5.0))
        self.take_profit_percent = float(self.config.get("take_profit_percent", 10.0))
    
    def _load_config(self):
        """Carga la configuración desde JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Guarda la configuración en JSON"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config_to_save = {
            "mock_mode": self.mock_mode,
            "paper_mode": self.paper_mode,
            "mock_initial_capital": self.mock_initial_capital,
            "trading_interval": self.trading_interval,
            "risk_per_trade": self.risk_per_trade,
            "max_position_size": self.max_position_size,
            "stop_loss_percent": self.stop_loss_percent,
            "take_profit_percent": self.take_profit_percent
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
    
    def set_mode(self, mode: str):
        """Configura el modo de operación"""
        if mode == "MOCK":
            self.mock_mode = True
            self.paper_mode = False
        elif mode == "PAPER":
            self.mock_mode = False
            self.paper_mode = True
        elif mode == "LIVE":
            self.mock_mode = False
            self.paper_mode = False
        else:
            raise ValueError(f"Modo no válido: {mode}")
        
        # Guardar cambios
        self.save_config()
        return True
    
    def get_current_mode(self):
        """Obtiene el modo actual como string"""
        if self.mock_mode:
            return "MOCK"
        elif self.paper_mode:
            return "PAPER"
        else:
            return "LIVE"

# ==============================================================================
# INICIALIZACIÓN DE ESTADO
# ==============================================================================
def init_session_state():
    """Inicializa variables de estado críticas"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.selected_symbol = 'GGAL'
        st.session_state.selected_category = 'acciones'
        st.session_state.current_price = 1.0
        st.session_state.iol_client = None
        
        # Para tracking de cambios
        st.session_state.last_mode_change = None
        st.session_state.last_symbol_change = datetime.now()

# ==============================================================================
# CLIENTE IOL DINÁMICO
# ==============================================================================
def get_client(settings):
    """Obtiene el cliente IOL según el modo actual"""
    
    # Si ya tenemos un cliente y no ha cambiado el modo, reutilizarlo
    if ('iol_client' in st.session_state and st.session_state.iol_client and 
        'current_mode' in st.session_state and 
        st.session_state.current_mode == settings.get_current_mode()):
        return st.session_state.iol_client
    
    try:
        # Registrar el modo actual
        st.session_state.current_mode = settings.get_current_mode()
        
        # Determinar qué cliente usar basado en configuración
        if settings.mock_mode:
            from src.api.mock_iol_client import MockIOLClient
            client = MockIOLClient(
                settings.iol_username, 
                settings.iol_password, 
                settings.iol_base_url, 
                settings.mock_initial_capital
            )
            
        elif settings.paper_mode:
            # Intentar usar PaperIOLClient, si no existe usar Mock
            try:
                from src.api.paper_iol_client import PaperIOLClient
                client = PaperIOLClient(
                    settings.iol_username, 
                    settings.iol_password, 
                    settings.iol_base_url
                )
            except ImportError:
                from src.api.mock_iol_client import MockIOLClient
                client = MockIOLClient(
                    settings.iol_username, 
                    settings.iol_password, 
                    settings.iol_base_url, 
                    settings.mock_initial_capital
                )
        else:
            # Modo LIVE - cliente real
            from src.api.iol_client import IOLClient
            client = IOLClient(
                settings.iol_username, 
                settings.iol_password, 
                settings.iol_base_url
            )
        
        # Autenticar
        if client and client.authenticate():
            st.session_state.iol_client = client
            return client
        else:
            st.error("❌ Fallo de autenticación")
            return None
            
    except Exception as e:
        st.error(f"Error inicializando cliente IOL: {e}")
        return None

# ==============================================================================
# SIDEBAR CON SELECTOR DE MODO
# ==============================================================================
def render_sidebar(settings):
    """Renderiza la barra lateral con controles y estado"""
    st.sidebar.title("🤖 Configuración del Bot")
    
    # === SECCIÓN DE MODO DE OPERACIÓN ===
    st.sidebar.markdown("### 🎮 Modo de Operación")
    
    # Determinar modo actual
    current_mode = settings.get_current_mode()
    
    # Crear radio buttons para seleccionar modo
    new_mode = st.sidebar.radio(
        "Selecciona el modo:",
        ["MOCK", "PAPER", "LIVE"],
        index=["MOCK", "PAPER", "LIVE"].index(current_mode),
        help="MOCK: Simulación completa\nPAPER: Paper trading con datos reales\nLIVE: Trading con dinero real"
    )
    
    # Si cambió el modo, actualizar configuración
    if new_mode != current_mode:
        if st.sidebar.button("✅ Aplicar Cambio de Modo", type="primary"):
            settings.set_mode(new_mode)
            # Limpiar cliente para forzar nueva creación
            if 'iol_client' in st.session_state:
                del st.session_state.iol_client
            st.session_state.last_mode_change = datetime.now()
            st.success(f"Modo cambiado a: {new_mode}")
            time.sleep(1)
            st.rerun()
    
    # Mostrar información del modo actual
    mode_info = {
        "MOCK": {"icon": "🔧", "desc": "Simulación completa con datos falsos"},
        "PAPER": {"icon": "📊", "desc": "Paper trading con datos reales"},
        "LIVE": {"icon": "⚠️", "desc": "Trading con dinero REAL"}
    }
    
    info = mode_info.get(current_mode, mode_info["MOCK"])
    st.sidebar.info(f"{info['icon']} **Modo {current_mode}**\n\n{info['desc']}")
    
    st.sidebar.divider()
    
    # === ESTADO DEL MERCADO ===
    st.sidebar.markdown("### 📊 Estado del Mercado")
    
    market_manager = MarketManager()
    status = market_manager.get_market_status()
    
    status_color = "🟢" if status['is_open'] else "🔴"
    st.sidebar.info(f"{status_color} Mercado **{status['status']}**")
    st.sidebar.caption(f"Hora: {status['current_time'].strftime('%H:%M:%S')}")
    
    st.sidebar.divider()
    
    # === CONFIGURACIÓN AVANZADA ===
    with st.sidebar.expander("⚙️ Configuración Avanzada"):
        # Capital inicial para MOCK mode
        if settings.mock_mode:
            new_capital = st.number_input(
                "Capital Inicial (MOCK)",
                min_value=1000.0,
                max_value=10000000.0,
                value=float(settings.mock_initial_capital),
                step=10000.0,
                format="%.2f"
            )
            
            if new_capital != settings.mock_initial_capital:
                settings.mock_initial_capital = new_capital
                if st.button("💾 Guardar Capital", key="save_capital"):
                    settings.save_config()
                    st.success("Capital guardado")
        
        # Parámetros de riesgo
        st.markdown("**📉 Gestión de Riesgo:**")
        risk = st.slider(
            "Riesgo por Operación (%)",
            min_value=0.1,
            max_value=10.0,
            value=float(settings.risk_per_trade),
            step=0.1
        )
        
        if risk != settings.risk_per_trade:
            settings.risk_per_trade = risk
            if st.button("💾 Guardar Riesgo", key="save_risk"):
                settings.save_config()
                st.success("Riesgo guardado")
    
    st.sidebar.divider()
    
    # === CONTROLES GENERALES ===
    st.sidebar.markdown("### 🕹️ Controles")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reiniciar", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'initialized':
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 Ver Logs", use_container_width=True):
            st.session_state.show_logs = True
    
    # Mostrar logs si está activado
    if st.session_state.get('show_logs', False):
        st.sidebar.divider()
        st.sidebar.markdown("### 📝 Logs del Sistema")
        # Aquí puedes agregar visualización de logs

# ==============================================================================
# TAB 1: MÉTRICAS
# ==============================================================================
def render_metrics_tab(client, settings):
    """Renderiza tab de métricas principales"""
    st.subheader("📊 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Operaciones Totales", "0", delta=None)
    
    with col2:
        st.metric("Tasa de Victorias", "0.0%", delta=None)
    
    with col3:
        # Mostrar P&L según modo
        if settings.mock_mode:
            pnl = "$0.00"
            delta_pnl = None
        elif settings.paper_mode:
            pnl = "$0.00"
            delta_pnl = "Paper Trading"
        else:
            pnl = "---"
            delta_pnl = "Modo LIVE"
        
        st.metric("P&L Total", pnl, delta=delta_pnl)
    
    with col4:
        # Mostrar capital según modo
        if settings.mock_mode:
            capital = f"${settings.mock_initial_capital:,.2f}"
            delta_capital = "Simulación"
        elif settings.paper_mode:
            capital = "$1,000,000"
            delta_capital = "Paper Trading"
        else:
            if client and hasattr(client, 'get_account_balance'):
                try:
                    balance = client.get_account_balance()
                    capital = f"${balance:,.2f}" if balance else "---"
                except:
                    capital = "---"
            else:
                capital = "---"
            delta_capital = "Real"
        
        st.metric("Capital Disponible", capital, delta=delta_capital)
    
    st.divider()
    
    # Información específica por modo
    mode_col1, mode_col2 = st.columns(2)
    
    with mode_col1:
        st.info(f"""
        **Información del Modo:**
        
        🎮 **Modo Actual:** {settings.get_current_mode()}
        ⏰ **Intervalo de Trading:** {settings.trading_interval}s
        📉 **Riesgo por Operación:** {settings.risk_per_trade}%
        🛡️ **Stop Loss:** {settings.stop_loss_percent}%
        🎯 **Take Profit:** {settings.take_profit_percent}%
        """)
    
    with mode_col2:
        # Mostrar estado de conexión
        if client:
            client_type = type(client).__name__
            if "Mock" in client_type:
                status_icon = "🔧"
                status_text = "Modo Simulación"
            elif "Paper" in client_type:
                status_icon = "📊"
                status_text = "Paper Trading"
            else:
                status_icon = "🌐"
                status_text = "Conexión Real"
            
            st.success(f"""
            **Estado de Conexión:**
            
            {status_icon} **Cliente:** {client_type}
            ✅ **Autenticado:** Sí
            🕒 **Última actualización:** {datetime.now().strftime('%H:%M:%S')}
            """)
        else:
            st.error("❌ Cliente no disponible")
    
    st.divider()
    st.info("📈 Las métricas se actualizarán automáticamente durante la operación.")

# ==============================================================================
# TAB 2: PORTAFOLIO
# ==============================================================================
def render_portfolio_tab(client, settings):
    """Renderiza tab de portafolio actual"""
    st.subheader("💼 Portafolio Actual")
    
    if not client:
        st.warning("⚠️ Cliente desconectado. Verifica la conexión.")
        return
    
    # Información del modo
    mode_badge = {
        "MOCK": "🔧 SIMULACIÓN",
        "PAPER": "📊 PAPER",
        "LIVE": "⚠️ LIVE"
    }.get(settings.get_current_mode(), "🔧 SIMULACIÓN")
    
    st.caption(f"Modo: {mode_badge} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with st.spinner("Cargando portafolio..."):
        try:
            portfolio_data = client.get_portfolio()
            
            if portfolio_data:
                # Manejar diferentes estructuras
                if isinstance(portfolio_data, dict):
                    if "activos" in portfolio_data:
                        activos = portfolio_data["activos"]
                    else:
                        activos = []
                else:
                    activos = []
                
                if activos and len(activos) > 0:
                    # Construir DataFrame
                    data = []
                    total_value = 0
                    
                    for a in activos:
                        if isinstance(a, dict):
                            symbol = a.get("titulo", {}).get("simbolo", "N/A") if "titulo" in a else a.get("simbolo", "N/A")
                            qty = a.get("cantidad", 0)
                            val = a.get("valorActual", 0)
                            var = a.get("gananciaPerdida", 0)
                            
                            data.append({
                                "Símbolo": symbol,
                                "Cantidad": qty,
                                "Precio Unitario": f"${val/qty:,.2f}" if qty > 0 else "$0.00",
                                "Valor Total": f"${val:,.2f}",
                                "P&L": f"${var:,.2f}"
                            })
                            
                            total_value += val
                    
                    # Mostrar resumen
                    col_sum1, col_sum2, col_sum3 = st.columns(3)
                    
                    with col_sum1:
                        st.metric("Total Activos", f"{len(data)}")
                    
                    with col_sum2:
                        st.metric("Valor Total", f"${total_value:,.2f}")
                    
                    with col_sum3:
                        # Calcular P&L total
                        total_pl = sum([float(d["P&L"].replace('$', '').replace(',', '')) for d in data])
                        st.metric("P&L Total", f"${total_pl:,.2f}")
                    
                    st.divider()
                    
                    # Mostrar tabla
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                    
                    # Gráfico de distribución
                    if len(data) > 0:
                        st.subheader("📊 Distribución del Portafolio")
                        
                        try:
                            values = [float(d["Valor Total"].replace('$', '').replace(',', '')) for d in data]
                            symbols = [d["Símbolo"] for d in data]
                            
                            if sum(values) > 0:
                                fig = px.pie(
                                    names=symbols,
                                    values=values,
                                    title="Distribución por Activo",
                                    hole=0.3
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        except:
                            st.info("No se pudo generar el gráfico de distribución.")
                    
                else:
                    st.info("📭 Portafolio vacío.")
                    
                    if settings.mock_mode:
                        st.caption("En modo MOCK, puedes empezar a operar para ver tu portafolio.")
                    elif settings.paper_mode:
                        st.caption("En modo PAPER, puedes simular operaciones para construir tu portafolio.")
                    else:
                        st.caption("En modo LIVE, las operaciones se realizarán con dinero real.")
                        
            else:
                st.error("No se pudo obtener datos del portafolio.")
                
        except Exception as e:
            st.error(f"Error obteniendo portafolio: {e}")

# ==============================================================================
# TAB 3: OPERACIÓN MANUAL
# ==============================================================================
def render_manual_trading_tab(client, settings):
    """Renderiza tab de operación manual"""
    st.subheader("🎯 Panel de Operación Manual")
    
    if not client:
        st.error("❌ Cliente desconectado. No se pueden ejecutar órdenes.")
        return
    
    # Advertencia para modo LIVE
    if settings.get_current_mode() == "LIVE":
        st.warning("""
        ⚠️ **MODO LIVE ACTIVADO** ⚠️
        
        Estás operando con **DINERO REAL**. 
        Todas las órdenes se ejecutarán en tu cuenta real de IOL.
        """)
    
    market_manager = MarketManager()
    categories = ['acciones', 'cedears', 'bonos_soberanos', 'letras', 'ons']
    
    # === SECCIÓN 1: SELECCIONAR ACTIVO ===
    st.markdown("### 1️⃣ Selecciona Activo")
    
    col_cat, col_sym = st.columns([1, 2])
    
    with col_cat:
        selected_category = st.selectbox(
            "Categoría",
            categories,
            key="manual_category"
        )
    
    symbols = market_manager.get_symbols_by_category([selected_category])
    
    with col_sym:
        selected_symbol = st.selectbox(
            f"Símbolo ({len(symbols)} opciones)",
            symbols,
            key="manual_symbol"
        )
    
    # Mostrar símbolo seleccionado
    st.info(f"**Activo seleccionado:** `{selected_symbol}` | **Categoría:** `{selected_category}`")
    
    # === SECCIÓN 2: OBTENER PRECIO ===
    st.markdown("### 2️⃣ Información de Precio")
    
    # Botón para refrescar precio
    refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 2, 1])
    with refresh_col2:
        if st.button("🔄 Actualizar Precio", use_container_width=True, key="refresh_price"):
            if 'last_price' in st.session_state:
                del st.session_state.last_price
            st.rerun()
    
    # Obtener precio
    price = 0.0
    quote = None
    
    try:
        # Usar caché para no hacer requests innecesarias
        cache_key = f"price_{selected_symbol}"
        if cache_key in st.session_state:
            price = st.session_state[cache_key]
            st.info(f"💰 Precio en caché: ${price:,.2f}")
        else:
            with st.spinner(f"Obteniendo precio de {selected_symbol}..."):
                if hasattr(client, 'get_last_price'):
                    quote = client.get_last_price(selected_symbol, "bCBA")
                elif hasattr(client, 'get_current_price'):
                    price_val = client.get_current_price(selected_symbol, "bCBA")
                    if price_val:
                        quote = {'price': price_val}
                
                if quote and isinstance(quote, dict):
                    # Intentar extraer precio
                    if 'price' in quote and quote['price']:
                        price = float(quote['price'])
                    elif 'ultimoPrecio' in quote and quote['ultimoPrecio']:
                        price = float(quote['ultimoPrecio'])
                    elif 'puntas' in quote and isinstance(quote['puntas'], dict):
                        puntas = quote['puntas']
                        if 'precioCompra' in puntas:
                            price = float(puntas['precioCompra'])
                    
                    # Guardar en caché
                    if price > 0:
                        st.session_state[cache_key] = price
                        st.success(f"✅ Precio actualizado: ${price:,.2f}")
                    else:
                        st.warning("⚠️ No se pudo obtener precio válido")
                        price = 100.0  # Valor por defecto
                else:
                    st.warning("⚠️ Sin datos de precio disponibles")
                    price = 100.0  # Valor por defecto
                    
    except Exception as e:
        st.error(f"❌ Error obteniendo precio: {e}")
        price = 100.0  # Valor por defecto
    
    # Mostrar precio
    st.markdown(f"""
    <div style="
        padding: 20px;
        background: {'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)' if settings.get_current_mode() == 'LIVE' else 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 20px 0;
    ">
        <h3 style="margin: 0; font-size: 18px;">Precio Actual</h3>
        <h1 style="margin: 10px 0; font-size: 42px; font-weight: bold;">${price:,.2f}</h1>
        <p style="margin: 0; font-size: 16px;">{selected_symbol} | Modo: {settings.get_current_mode()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # === SECCIÓN 3: CONFIGURAR ORDEN ===
    st.markdown("### 3️⃣ Configurar Orden")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        side = st.radio("Operación", ["Compra", "Venta"], horizontal=True)
    
    with col2:
        qty = st.number_input("Cantidad", min_value=1, max_value=10000, value=100, step=1)
    
    with col3:
        total_est = price * qty
        st.metric("Total Estimado", f"${total_est:,.2f}")
    
    st.divider()
    
    # === SECCIÓN 4: EJECUTAR ORDEN ===
    st.markdown("### 4️⃣ Ejecutar")
    
    # Mostrar resumen
    st.info(f"""
    **Resumen de la orden:**
    
    🎯 **Operación:** {side}
    📊 **Símbolo:** {selected_symbol}
    🔢 **Cantidad:** {qty}
    💰 **Precio estimado:** ${price:,.2f}
    🧮 **Total estimado:** ${total_est:,.2f}
    🎮 **Modo:** {settings.get_current_mode()}
    """)
    
    # Botón de ejecución con confirmación para LIVE
    if settings.get_current_mode() == "LIVE":
        confirm = st.checkbox("✅ Confirmo que esta operación usará DINERO REAL")
        if not confirm:
            st.button("🚀 EJECUTAR ORDEN", disabled=True, help="Debes confirmar primero")
            return
    
    if st.button("🚀 EJECUTAR ORDEN", type="primary", use_container_width=True):
        execute_order(client, selected_symbol, side, qty, price, settings)

def execute_order(client, symbol, side, quantity, price, settings):
    """Ejecuta una orden de trading"""
    result_container = st.empty()
    
    with result_container.container():
        st.subheader("📊 Procesando orden...")
        
        with st.spinner(f"Enviando orden de {side.lower()}..."):
            try:
                # Mapear lado
                iol_side = "compra" if side == "Compra" else "venta"
                
                # Verificar método
                if not hasattr(client, 'place_market_order'):
                    st.error("❌ Cliente no soporta órdenes de mercado")
                    return
                
                # Enviar orden
                result = client.place_market_order(
                    symbol=symbol,
                    quantity=quantity,
                    side=iol_side,
                    market="bCBA"
                )
                
                # Procesar resultado
                if result:
                    if isinstance(result, dict) and result.get("success"):
                        tx_price = result.get("price", price)
                        
                        st.success(f"""
                        ✅ **ORDEN EXITOSA**
                        
                        **Detalles:**
                        - Operación: {side}
                        - Símbolo: {symbol}
                        - Cantidad: {quantity}
                        - Precio: ${tx_price:,.2f}
                        - Total: ${tx_price * quantity:,.2f}
                        - Modo: {settings.get_current_mode()}
                        """)
                        
                        st.balloons()
                        
                        # Limpiar caché de precio
                        cache_key = f"price_{symbol}"
                        if cache_key in st.session_state:
                            del st.session_state[cache_key]
                        
                        # Botón para continuar
                        if st.button("🔄 Realizar otra operación"):
                            st.rerun()
                        
                    else:
                        error_msg = result.get("error", result.get("message", "Error desconocido"))
                        st.error(f"❌ Orden rechazada: {error_msg}")
                        
                else:
                    st.error("❌ No hubo respuesta del servidor")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ==============================================================================
# TAB 4: ANÁLISIS
# ==============================================================================
def render_analysis_tab(settings):
    """Renderiza tab de análisis de mercado"""
    st.subheader("📈 Análisis de Mercado")
    
    # Mostrar información del modo
    mode_badge = {
        "MOCK": ("🔧", "Análisis con datos simulados"),
        "PAPER": ("📊", "Análisis con datos reales (paper trading)"),
        "LIVE": ("⚠️", "Análisis con datos en tiempo real")
    }.get(settings.get_current_mode(), ("🔧", "Análisis con datos simulados"))
    
    st.info(f"""
    {mode_badge[0]} **Modo {settings.get_current_mode()}**
    
    {mode_badge[1]}
    """)
    
    # Placeholder para análisis futuro
    st.info("""
    🚧 **En construcción**
    
    Próximamente:
    - 📊 Gráficos en tiempo real
    - 📈 Indicadores técnicos
    - 📰 Análisis de noticias
    - 🤖 Recomendaciones de trading
    """)

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    """Función principal"""
    # Inicializar estado
    init_session_state()
    
    # Cargar configuración
    settings = AppSettings()
    
    # Renderizar sidebar
    render_sidebar(settings)
    
    # Título principal
    st.title("📱 IOL Trading Bot Pro Dashboard")
    
    # Obtener cliente
    client = get_client(settings)
    
    if not client:
        st.error("❌ No se pudo inicializar el cliente IOL.")
        st.info("""
        **Posibles soluciones:**
        1. Verifica que las credenciales IOL estén en el archivo `.env`
        2. Asegúrate de que estés conectado a internet
        3. Intenta cambiar a modo MOCK si el problema persiste
        """)
        
        # Permitir usar modo MOCK incluso sin credenciales
        if st.button("🔧 Usar Modo MOCK como fallback"):
            settings.set_mode("MOCK")
            st.rerun()
        
        return
    
    # Mostrar información del modo actual
    mode_col1, mode_col2, mode_col3 = st.columns(3)
    
    with mode_col1:
        mode_display = {
            "MOCK": "🔧 MOCK (Simulación)",
            "PAPER": "📊 PAPER (Paper Trading)", 
            "LIVE": "⚠️ LIVE (Real)"
        }.get(settings.get_current_mode(), "🔧 MOCK")
        
        st.info(f"**Modo:** {mode_display}")
    
    with mode_col2:
        client_type = type(client).__name__
        st.info(f"**Cliente:** {client_type}")
    
    with mode_col3:
        if hasattr(client, 'get_account_balance'):
            try:
                balance = client.get_account_balance()
                if balance is not None:
                    st.info(f"**Saldo:** ${balance:,.2f}")
                else:
                    st.info("**Saldo:** ---")
            except:
                st.info("**Saldo:** ---")
        else:
            st.info("**Saldo:** Simulado")
    
    st.divider()
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Métricas",
        "💼 Portafolio", 
        "🎯 Operar",
        "📈 Análisis"
    ])
    
    with tab1:
        render_metrics_tab(client, settings)
    
    with tab2:
        render_portfolio_tab(client, settings)
    
    with tab3:
        render_manual_trading_tab(client, settings)
    
    with tab4:
        render_analysis_tab(settings)

if __name__ == "__main__":
    main()
