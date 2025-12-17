"""
IOL Trading Bot Dashboard
Dashboard principal Streamlit para monitoreo, trading manual y análisis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import time

# Agregar directorio raíz al path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.bot.config import Settings
from src.utils.market_manager import MarketManager
from src.utils.config_manager import config_manager

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="IOL Trading Bot Pro",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar configuración global
try:
    settings = Settings()
except Exception as e:
    st.error(f"Error cargando configuración: {e}")
    st.stop()

# ==============================================================================
# INICIALIZACIÓN DE ESTADO
# ==============================================================================
def init_session_state():
    """Inicializa variables de estado críticas"""
    defaults = {
        'selected_symbol': 'GGAL',
        'selected_category': 'acciones',
        'current_price': 1.0,
        'asset_info': {},
        'bot_status': 'DETENIDO',
        'telegram_status': 'DETENIDO',
        'iol_client': None
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ==============================================================================
# CLIENTE IOL
# ==============================================================================
def get_client():
    """Obtiene el cliente IOL REAL (CON CACHE en session_state)"""
    
    # CRÍTICO: Reutilizar cliente existente para evitar resetear precios
    if 'iol_client' in st.session_state and st.session_state.iol_client:
        return st.session_state.iol_client
    
    try:
        username = settings.iol_username or "mock_user"
        password = settings.iol_password or "mock_pass"
        base_url = settings.iol_base_url or "https://api.invertironline.com"
        
        # FORZAR uso de cliente REAL de IOL para datos del universo
        from src.api.iol_client import IOLClient
        client = IOLClient(username, password, base_url)
        st.sidebar.info("🌐 Conectado a **IOL Real** (Datos del mercado)")
        
        if client and client.authenticate():
            # GUARDAR en session_state para persistir entre reruns
            st.session_state.iol_client = client
            return client
        else:
            st.sidebar.error("❌ Fallo de autenticación con IOL")
            return None
    except Exception as e:
        st.error(f"Error inicializando cliente IOL: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.info("💡 Verifica tus credenciales IOL_USERNAME y IOL_PASSWORD en .env")
        return None


# ==============================================================================
# SIDEBAR
# ==============================================================================
def render_sidebar():
    """Renderiza la barra lateral con controles y estado"""
    st.sidebar.title("🤖 Configuración del Bot")
    
    market_manager = MarketManager()
    status = market_manager.get_market_status()
    
    status_color = "🟢" if status['is_open'] else "🔴"
    st.sidebar.info(f"{status_color} Mercado **{status['status']}**")
    st.sidebar.caption(f"Hora: {status['current_time'].strftime('%H:%M:%S')}")
    
    # Modo de operación (ya se muestra en get_client, pero lo dejamos aquí también)
    if settings.mock_mode:
        mode_label = "MOCK (Simulación)"
        mode_icon = "🔧"
    elif settings.paper_mode:
        mode_label = "PAPER (Paper Trading)"
        mode_icon = "📊"
    else:
        mode_label = "LIVE (Real)"
        mode_icon = "⚠️"
    
    st.sidebar.markdown(f"**Modo:** {mode_icon} `{mode_label}`")
    st.sidebar.divider()
    
    # Controles
    st.sidebar.subheader("🕹️ Control")
    if st.sidebar.button("🔄 Reiniciar", type="secondary", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

# ==============================================================================
# TAB 1: MÉTRICAS
# ==============================================================================
def render_metrics_tab():
    """Renderiza tab de métricas principales"""
    st.subheader("📊 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Operaciones Totales", "0", delta=None)
    with col2:
        st.metric("Tasa de Victorias", "0.0%", delta=None)
    with col3:
        st.metric("P&L Total", "$0.00", delta=None)
    with col4:
        st.metric("Capital Disponible", "$1,000,000", delta=None)
    
    st.divider()
    st.info("📈 Métricas en construcción: Se actualizarán con datos de backtest y trading en vivo.")

# ==============================================================================
# TAB 2: PORTAFOLIO
# ==============================================================================
def render_portfolio_tab(client):
    """Renderiza tab de portafolio actual"""
    st.subheader("💼 Portafolio Actual")
    
    if not client:
        st.warning("⚠️ Cliente desconectado. Verifica la conexión.")
        return
    
    with st.spinner("Cargando portafolio..."):
        portfolio_data = client.get_portfolio()
    
    if portfolio_data and "activos" in portfolio_data:
        activos = portfolio_data["activos"]
        
        if activos:
            # Construir DataFrame
            data = []
            for a in activos:
                symbol = a.get("titulo", {}).get("simbolo", "N/A")
                qty = a.get("cantidad", 0)
                val = a.get("valorActual", 0)
                var = a.get("gananciaPerdida", 0)
                
                data.append({
                    "Símbolo": symbol,
                    "Cantidad": qty,
                    "Valor Total": f"${val:,.2f}",
                    "P&L": f"${var:,.2f}"
                })
            
            col_table, col_chart = st.columns([2, 1])
            
            with col_table:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            
            with col_chart:
                # Gráfico de distribución (usando valores numéricos internos)
                values = [a.get("valorActual", 0) for a in activos]
                symbols = [a.get("titulo", {}).get("simbolo", "N/A") for a in activos]
                
                if sum(values) > 0:
                    fig = px.pie(
                        names=symbols,
                        values=values,
                        title="Distribución de Portafolio"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Portafolio vacío.")
    else:
        st.error("No se pudo obtener datos del portafolio.")

# ==============================================================================
# TAB 3: OPERACIÓN MANUAL
# ==============================================================================
def render_manual_trading_tab(client):
    """Renderiza tab de operación manual"""
    st.subheader("🎯 Panel de Operación Manual")
    
    if not client:
        st.error("❌ Cliente desconectado. No se pueden ejecutar órdenes.")
        return
    
    market_manager = MarketManager()
    categories = ['acciones', 'cedears', 'bonos_soberanos', 'letras', 'ons']
    
    # === SECCIÓN 1: SELECCIONAR ACTIVO ===
    st.markdown("### 1️⃣ Selecciona Activo")
    col_cat, col_sym = st.columns([1, 2])
    
    with col_cat:
        selected_category = st.selectbox(
            "Categoría",
            categories,
            key="selected_category"
        )
    
    # Obtener símbolos de la categoría
    symbols = market_manager.get_symbols_by_category([selected_category])
    
    with col_sym:
        selected_symbol = st.selectbox(
            f"Símbolo ({len(symbols)} opciones)",
            symbols,
            key="selected_symbol"
        )
    
    # === SECCIÓN 2: OBTENER PRECIO ===
    st.markdown("### 2️⃣ Información de Precio")
    
    # Obtener precio actualizado - usar selected_symbol directamente del selectbox
    # Streamlit actualiza automáticamente cuando el usuario cambia la selección
    price = 0.0
    quote = None
    try:
        quote = client.get_last_price(selected_symbol, "bCBA")
        if quote and 'price' in quote:
            price = float(quote['price'])
            
            # FALLBACK 1: Si precio es 0 (mercado cerrado), usar precio de cierre
            if price == 0 and 'settlementPrice' in quote:
                price = float(quote['settlementPrice'])
                if price > 0:
                    st.info(f"ℹ️ Mercado cerrado. Mostrando precio de cierre: ${price:,.2f}")
            
            # FALLBACK 2: Si ambos son 0, intentar datos históricos
            if price == 0:
                try:
                    from datetime import datetime, timedelta
                    to_date = datetime.now()
                    from_date = to_date - timedelta(days=7)
                    hist_data = client.get_historical_data(selected_symbol, from_date, to_date, "bCBA")
                    
                    if hist_data is not None and len(hist_data) > 0:
                        price = float(hist_data.iloc[-1]['close'])
                        st.info(f"ℹ️ Usando último precio histórico (hace {(datetime.now() - hist_data.iloc[-1]['date']).days} días): ${price:,.2f}")
                except Exception as hist_error:
                    st.warning(f"⚠️ No se pudieron obtener datos históricos: {hist_error}")
            
            st.session_state.current_price = price
        else:
            st.warning(f"⚠️ Sin cotización para {selected_symbol}")
            st.caption(f"Respuesta API: {quote}")
            price = 0.0
    except Exception as e:
        st.error(f"❌ Error obteniendo precio de {selected_symbol}")
        st.code(str(e))
        price = 0.0
    
    # Mostrar precio prominente - usar selected_symbol directamente
    st.metric(
        label=f"Precio Actual {selected_symbol}",
        value=f"${price:,.2f}",
        delta=None
    )
    
    st.divider()
    
    # === SECCIÓN 3: CONFIGURAR ORDEN ===
    st.markdown("### 3️⃣ Configurar Orden")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        side = st.radio("Operación", ["Compra", "Venta"], horizontal=False)
    
    with col2:
        qty = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=10000,
            value=10,
            step=1
        )
    
    with col3:
        total_est = price * qty
        st.metric("Total Estimado", f"${total_est:,.2f}")
    
    st.divider()
    
    # === SECCIÓN 4: EJECUTAR ORDEN ===
    st.markdown("### 4️⃣ Ejecutar")
    
    if st.button("🚀 Ejecutar Orden", type="primary", use_container_width=True):
        # Validar
        if price <= 0:
            st.error("Precio inválido. Recarga la página.")
            st.stop()
        
        if qty <= 0:
            st.error("Cantidad debe ser mayor a 0.")
            st.stop()
        
        # Mapear lado
        iol_side = "compra" if side == "Compra" else "venta"
        
        # Enviar orden
        with st.spinner(f"Enviando orden de {side.lower()} ..."):
            try:
                result = client.place_market_order(
                    symbol=selected_symbol,
                    quantity=int(qty),
                    side=iol_side,
                    market="bCBA"
                )
                
                if result and result.get("success"):
                    tx_price = result.get("price", price)
                    st.success(
                        f"✅ **ORDEN EXITOSA**\n\n"
                        f"{side} {qty} {selected_symbol} a ${tx_price:,.2f}"
                    )
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    msg = result.get("message", "Respuesta inválida del servidor") if result else "Sin respuesta"
                    st.error(f"❌ Orden rechazada: {msg}")
            except Exception as e:
                st.error(f"❌ Error ejecutando orden: {e}")

# ==============================================================================
# TAB 4: ANÁLISIS
# ==============================================================================
def render_analysis_tab():
    """Renderiza tab de análisis de mercado"""
    st.subheader("📈 Análisis de Mercado")
    
    st.info(
        "🔄 **En construcción**\n\n"
        "Se integrarán visualizaciones avanzadas con datos históricos, "
        "análisis técnico multi-timeframe y correlaciones."
    )

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    """Función principal"""
    init_session_state()
    render_sidebar()
    
    st.title("📱 IOL Trading Bot Pro Dashboard")
    
    # Inicializar cliente (SIN CACHE para evitar problemas)
    # Limpiar caché de módulos si es necesario
    if 'src.api.paper_iol_client' in sys.modules:
        import importlib
        importlib.reload(sys.modules['src.api.paper_iol_client'])
    
    client = get_client()
    if not client:
        st.error("❌ Error: No se pudo inicializar el cliente IOL.")
        st.info("Verifica que la configuración sea correcta.")
        st.stop()
    
    # Verificar que el cliente tiene el método necesario
    if not hasattr(client, 'get_last_price'):
        st.error(f"❌ Error: El cliente {type(client).__name__} no tiene el método get_last_price")
        st.info("Métodos disponibles: " + ", ".join([m for m in dir(client) if not m.startswith('_') and 'price' in m.lower()]))
        st.stop()
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Métricas",
        "💼 Portafolio",
        "🎯 Operar",
        "📈 Análisis"
    ])
    
    with tab1:
        render_metrics_tab()
    
    with tab2:
        render_portfolio_tab(client)
    
    with tab3:
        render_manual_trading_tab(client)
    
    with tab4:
        render_analysis_tab()

if __name__ == "__main__":
    main()
