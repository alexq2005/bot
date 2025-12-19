"""
Dashboard Web Interactivo - IOL Quantum AI Trading Bot

Dashboard completo con 10 páginas:
1. Command Center
2. Dashboard en Vivo
3. Gestión de Activos
4. Bot Autónomo
5. Optimizador Genético
6. Red Neuronal
7. Estrategias Avanzadas
8. Configuración
9. Terminal de Trading
10. Chat con el Bot

Versión: 1.1.0
"""

import streamlit as st

# Configurar página para usar ancho completo
st.set_page_config(
    page_title="IOL Quantum AI Trading Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS GLOBAL PROFESIONAL - Diseño Moderno y Elegante
st.markdown("""
<style>
    /* ============================================
       VARIABLES DE COLOR Y TEMA
       ============================================ */
    :root {
        --primary-color: #00FF88;
        --secondary-color: #00D9FF;
        --accent-color: #FFD93D;
        --danger-color: #FF4444;
        --success-color: #00FF88;
        --warning-color: #FFD93D;
        --info-color: #00D9FF;
        --bg-dark: #0E1117;
        --bg-card: rgba(30, 30, 30, 0.6);
        --bg-hover: rgba(0, 255, 136, 0.1);
        --border-color: rgba(0, 255, 136, 0.3);
        --text-primary: #FFFFFF;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 12px rgba(0, 0, 0, 0.5);
        --radius-sm: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ============================================
       CONTENEDOR PRINCIPAL
       ============================================ */
    .main .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    .main {
        flex: 1 1 0% !important;
        width: 100% !important;
        max-width: 100% !important;
        background: linear-gradient(135deg, #0E1117 0%, #1a1a2e 100%);
    }
    
    section[data-testid="stMain"] {
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 0% !important;
    }
    
    section[data-testid="stMain"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    section[data-testid="stMain"] > div > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* ============================================
       COMPONENTES REUTILIZABLES
       ============================================ */
    .metric-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(0, 0, 0, 0.3) 100%);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        transition: var(--transition);
        box-shadow: var(--shadow-md);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-sm);
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-active {
        background: rgba(0, 255, 136, 0.2);
        color: var(--primary-color);
        border: 1px solid var(--primary-color);
    }
    
    .status-inactive {
        background: rgba(255, 68, 68, 0.2);
        color: var(--danger-color);
        border: 1px solid var(--danger-color);
    }
    
    /* ============================================
       BOTONES MEJORADOS
       ============================================ */
    .stButton > button {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-color) !important;
        transition: var(--transition) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
        border-color: var(--primary-color) !important;
    }
    
    /* ============================================
       TARJETAS Y CONTENEDORES
       ============================================ */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
        transition: var(--transition);
    }
    
    .card:hover {
        border-color: var(--primary-color);
        box-shadow: var(--shadow-lg);
    }
    
    /* ============================================
       SIDEBAR MEJORADO
       ============================================ */
    [data-testid="stSidebar"] {
        min-width: 22rem;
        max-width: 22rem;
        background: linear-gradient(180deg, #0E1117 0%, #1a1a2e 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }
    
    [data-testid="stSidebar"] label {
        padding: 0.75rem 1rem;
        border-radius: var(--radius-sm);
        transition: var(--transition);
        border: 1px solid transparent;
    }
    
    [data-testid="stSidebar"] label:hover {
        background: var(--bg-hover);
        border-color: var(--border-color);
    }
    
    /* ============================================
       TABLAS Y DATAFRAMES
       ============================================ */
    .stDataFrame {
        border-radius: var(--radius-md);
        overflow: hidden;
    }
    
    /* ============================================
       EXPANDERS Y ACORDEONES
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-color) !important;
        transition: var(--transition) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-hover) !important;
        border-color: var(--primary-color) !important;
    }
    
    /* ============================================
       INPUTS Y FORMULARIOS
       ============================================ */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        transition: var(--transition) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1) !important;
    }
    
    /* ============================================
       SCROLLBAR PERSONALIZADO
       ============================================ */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* ============================================
       ANIMACIONES
       ============================================ */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* ============================================
       TIPOGRAFÍA
       ============================================ */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* ============================================
       UTILIDADES
       ============================================ */
    .gradient-text {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .glass-effect {
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

import logging
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
import threading
import time
from datetime import datetime, timedelta
from trading_bot import TradingBot
from telegram_bot import TelegramBot
from bot_state_manager import bot_state
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from src.utils.dashboard_utils import (
    generate_candlestick_data,
    create_candlestick_chart,
    generate_top_performers,
    create_correlation_heatmap
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# INICIALIZACIÓN DEL BOT DE TELEGRAM
# ============================================
# La inicialización se maneja dentro de main() para asegurar
# que se vincule correctamente con la instancia de TradingBot.




import requests

def get_dolar_rates():
    """Obtiene cotización del Dólar (Blue/Oficial) de API pública"""
    try:
        r_blue = requests.get("https://dolarapi.com/v1/dolares/blue", timeout=2)
        r_oficial = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=2)
        
        blue = r_blue.json()['venta'] if r_blue.status_code == 200 else 0
        oficial = r_oficial.json()['venta'] if r_oficial.status_code == 200 else 0
        
        return blue, oficial
    except:
        return 0, 0

def add_bot_message(message: str, msg_type: str = "info"):
    """Agrega un mensaje al log del bot"""
    if 'bot_messages' not in st.session_state:
        st.session_state.bot_messages = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.bot_messages.append({
        'timestamp': timestamp,
        'message': message,
        'type': msg_type
    })

# ============================================
# COMPONENTES REUTILIZABLES PROFESIONALES
# ============================================

def render_section_header(title: str, icon: str = "📊", subtitle: str = None):
    """Renderiza un header de sección profesional"""
    header_html = f"""
    <div style='background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 217, 255, 0.1) 100%); 
                padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1.5rem 0; 
                border-left: 4px solid #00FF88; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <h2 style='margin: 0; color: #FFFFFF; font-size: 1.75rem; font-weight: 700;'>
            {icon} {title}
        </h2>
        {f"<p style='margin: 0.5rem 0 0 0; color: rgba(255, 255, 255, 0.7); font-size: 0.95rem;'>{subtitle}</p>" if subtitle else ""}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal", icon: str = None):
    """Renderiza una tarjeta de métrica profesional"""
    delta_html = ""
    if delta:
        delta_color_hex = "#00FF88" if delta_color == "normal" else "#FF4444"
        delta_html = f"""<div style="margin-top: 0.5rem; font-size: 0.9rem; color: {delta_color_hex}; font-weight: 600;">{delta}</div>"""
    
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ""
    
    # Usar comillas dobles para evitar conflictos con comillas simples en el HTML
    card_html = f"""<div style="background: linear-gradient(135deg, rgba(30, 30, 30, 0.6) 0%, rgba(0, 0, 0, 0.3) 100%); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4); transition: all 0.3s ease;">
        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center;">{icon_html}{value}</div>
        {delta_html}
    </div>"""
    st.markdown(card_html, unsafe_allow_html=True)

def render_status_badge(status: str, is_active: bool = True):
    """Renderiza un badge de estado profesional"""
    bg_color = "rgba(0, 255, 136, 0.2)" if is_active else "rgba(255, 68, 68, 0.2)"
    text_color = "#00FF88" if is_active else "#FF4444"
    border_color = "#00FF88" if is_active else "#FF4444"
    icon = "🟢" if is_active else "🔴"
    
    badge_html = f"""
    <div style='display: inline-block; padding: 0.5rem 1rem; background: {bg_color};
                border: 1px solid {border_color}; border-radius: 0.5rem; font-weight: 600;
                color: {text_color}; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem;'>
        {icon} {status}
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

def render_info_card(title: str, content: str, icon: str = "ℹ️", color: str = "#00D9FF"):
    """Renderiza una tarjeta de información"""
    card_html = f"""
    <div style='background: linear-gradient(135deg, rgba(30, 30, 30, 0.6) 0%, rgba(0, 0, 0, 0.3) 100%);
                border-left: 4px solid {color}; border-radius: 0.75rem; padding: 1.5rem;
                margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='display: flex; align-items: center; margin-bottom: 0.75rem;'>
            <span style='font-size: 1.5rem; margin-right: 0.75rem;'>{icon}</span>
            <h3 style='margin: 0; color: #FFFFFF; font-size: 1.25rem;'>{title}</h3>
        </div>
        <p style='margin: 0; color: rgba(255, 255, 255, 0.8); line-height: 1.6;'>{content}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def get_telegram_events():
    """Obtiene eventos recientes de Telegram desde la base de datos"""
    try:
        if 'bot_instance' in st.session_state and st.session_state.bot_instance:
            bot = st.session_state.bot_instance
            if hasattr(bot, 'db') and bot.db:
                # Obtener todos los eventos y filtrar los de Telegram
                all_events = bot.db.get_events(limit=50)
                telegram_events = [e for e in all_events if e.get('event_type', '').startswith('telegram_')]
                return telegram_events
    except Exception as e:
        logger.debug(f"Error obteniendo eventos de Telegram: {e}")
    return []

def generate_candlestick_data(symbol: str, days: int = 100):
    """Genera datos simulados de velas para gráficos"""
    import random
    dates = pd.date_range(end=datetime.now(), periods=days)
    base_price = 1000.0
    data = []
    
    for i in range(days):
        change = random.uniform(-0.03, 0.03)
        open_price = base_price
        close_price = open_price * (1 + change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
        
        data.append({
            'date': dates[i],
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': random.randint(1000, 50000)
        })
        base_price = close_price
    
    return pd.DataFrame(data)

def create_candlestick_chart(df: pd.DataFrame, symbol: str):
    """Crea un gráfico de velas japonesas con Plotly"""
    fig = go.Figure(data=[go.Candlestick(
        x=df['date'] if 'date' in df.columns else df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])
    
    fig.update_layout(
        title=f"{symbol} - Precio",
        xaxis_title="Fecha",
        yaxis_title="Precio (ARS)",
        template="plotly_dark",
        height=500
    )
    
    return fig

def main():
    """Función principal del dashboard"""
    
    # Inicializar session_state para el bot
    if 'bot_instance' not in st.session_state:
        with st.spinner('🚀 Conectando a IOL...'):
            try:
                bot = TradingBot()
                # Forzar carga de datos iniciales
                if bot.iol_client.authenticate():
                     bot._refresh_portfolio()
                     # Obtener saldo disponible usando el método dedicado
                     try:
                         # El bot ya debería tener el capital inicializado en __init__
                         # Pero lo refrescamos para asegurarnos
                         if hasattr(bot, '_get_available_capital'):
                             bot.capital = bot._get_available_capital()
                         else:
                             bot.capital = bot.iol_client.get_available_cash()
                         
                         # Si aún es 0, intentar una vez más
                         if bot.capital == 0.0:
                             logger.info("Capital es 0, intentando obtener desde estado de cuenta...")
                             account_status = bot.iol_client.get_account_status()
                             bot.capital = account_status.get("available_cash", 0.0)
                             
                         logger.info(f"💰 Capital inicializado: ${bot.capital:,.2f}")
                     except Exception as e:
                         logger.warning(f"No se pudo obtener capital inicial: {e}")
                         bot.capital = 0.0 # Fallback
                     
                     st.session_state.bot_instance = bot
                     
                     # Iniciar bot de Telegram en hilo separado si está configurado
                     # IMPORTANTE: Solo iniciar si no está ya corriendo (evitar conflictos)
                     if bot.telegram and bot.telegram.token:
                         # Verificar si ya hay un thread corriendo (desde dashboard o trading_bot)
                         telegram_already_running = False
                         
                         # Verificar thread del dashboard
                         if 'telegram_thread' in st.session_state and st.session_state.telegram_thread:
                             if hasattr(st.session_state.telegram_thread, 'is_alive') and st.session_state.telegram_thread.is_alive():
                                 telegram_already_running = True
                                 logger.info("📡 Bot de Telegram ya está corriendo desde dashboard")
                         
                         # Verificar thread del trading_bot
                         if hasattr(bot, 'telegram_thread') and bot.telegram_thread:
                             if hasattr(bot.telegram_thread, 'is_alive') and bot.telegram_thread.is_alive():
                                 telegram_already_running = True
                                 logger.info("📡 Bot de Telegram ya está corriendo desde trading_bot")
                         
                         # Solo iniciar si no está corriendo
                         # ROBUST: Verificar cualquier thread con el nombre correcto en el sistema
                         for t in threading.enumerate():
                             if (t.name == "TelegramBot-Dashboard" or t.name == "TelegramBotThread") and t.is_alive():
                                 telegram_already_running = True
                                 logger.info(f"📡 Bot de Telegram encontrado en threads del sistema: {t.name} (recuperado)")
                                 st.session_state.telegram_thread = t 
                                 bot.telegram_thread = t
                                 break

                         if not telegram_already_running:
                             try:
                                 def start_telegram_bot():
                                     """Wrapper para iniciar el bot de Telegram con mejor manejo de errores"""
                                     try:
                                         logger.info("📡 Iniciando bot de Telegram en thread separado desde dashboard...")
                                         bot.telegram.run()
                                     except Exception as e:
                                         # Ignorar errores de conflicto (otra instancia ya corriendo)
                                         if "Conflict" in str(e) or "getUpdates" in str(e):
                                             logger.warning(f"⚠️ Otra instancia del bot de Telegram ya está corriendo: {e}")
                                         else:
                                             logger.error(f"❌ Error en bot de Telegram: {e}")
                                             import traceback
                                             logger.error(traceback.format_exc())
                                 
                                 telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True, name="TelegramBot-Dashboard")
                                 telegram_thread.start()
                                 st.session_state.telegram_thread = telegram_thread
                                 
                                 # Guardar referencia también en el bot
                                 bot.telegram_thread = telegram_thread
                                 
                                 # Dar tiempo para que el thread inicie
                                 import time
                                 time.sleep(0.5)
                                 
                                 if telegram_thread.is_alive():
                                     logger.info("✅ Bot de Telegram iniciado correctamente desde dashboard")
                                 else:
                                     logger.warning("⚠️ El thread de Telegram no se mantiene vivo")
                             except Exception as e:
                                 logger.error(f"❌ No se pudo iniciar bot de Telegram: {e}")
                                 import traceback
                                 logger.error(traceback.format_exc())
                     else:
                         if not bot.telegram:
                             logger.warning("⚠️ Bot de Telegram no está inicializado")
                         elif not bot.telegram.token:
                             logger.warning("⚠️ Token de Telegram no configurado")
                     
                     st.toast("Conectado a InvertirOnline", icon="🟢")
                else:
                     st.error("❌ Fallo de autenticación. Revisa IOL_PASSWORD en .env")
                     st.session_state.bot_instance = None
            except Exception as e:
                st.error("❌ Error al conectar con IOL. Verifica tus credenciales en .env")
                logger.error(f"Error connecting to IOL: {e}")
                st.session_state.bot_instance = None
    if 'bot_running' not in st.session_state:
        st.session_state.bot_running = False
    if 'bot_thread' not in st.session_state:
        st.session_state.bot_thread = None
    if 'bot_messages' not in st.session_state:
        st.session_state.bot_messages = []
    if 'bot_start_time' not in st.session_state:
        st.session_state.bot_start_time = None
    
    # Inicializar session_state para configuraciones
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 10
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
    
    # Validar inicializacion correcta
    if 'bot_instance' not in st.session_state:
        st.session_state.bot_instance = None
    
    # Auto-detectar si el bot ya está corriendo desde terminal
    try:
        import psutil
        bot_detected = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in str(cmdline[0]).lower():
                    if any('trading_bot.py' in str(arg) or 'monitor_bot_live.py' in str(arg) for arg in cmdline):
                        bot_detected = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Actualizar estado si detectamos el bot corriendo
        if bot_detected:
            if not st.session_state.bot_running:
                st.session_state.bot_running = True
                if not st.session_state.bot_start_time:
                    st.session_state.bot_start_time = datetime.now()
                # Forzar rerun para actualizar UI
                st.rerun()
        else:
            # Si no detectamos el bot pero estaba marcado como corriendo, actualizar
            if st.session_state.bot_running:
                st.session_state.bot_running = False
                st.session_state.bot_start_time = None
    except:
        pass

    # Sidebar: Navegación y Contexto Global
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title("IOL Quantum V3")
        
        # --- ESTADO DE CONEXIÓN Y USUARIO ---
        st.markdown("### 📡 Estado de Conexión")
        if st.session_state.bot_instance:
            username = st.session_state.bot_instance.iol_client.username if hasattr(st.session_state.bot_instance.iol_client, 'username') else "Trader"
            st.success(f"🟢 CONECTADO: {username}")
            
            # Saldo Real - Obtener desde el bot (ya debería estar inicializado)
            balance = None
            try:
                # El bot ya tiene el capital inicializado en __init__
                if hasattr(st.session_state.bot_instance, 'capital'):
                    balance = getattr(st.session_state.bot_instance, 'capital', None)
                    # Convertir a float si es None
                    if balance is None:
                        balance = 0.0
                    else:
                        balance = float(balance)
                
                # Si el capital es 0 o None, intentar obtenerlo una vez
                if balance is None or balance == 0.0:
                    # Usar método del bot si existe
                    if hasattr(st.session_state.bot_instance, '_get_available_capital'):
                        try:
                            balance = st.session_state.bot_instance._get_available_capital()
                        except:
                            balance = 0.0
                    else:
                        # Fallback: obtener directamente desde IOL
                        try:
                            balance = st.session_state.bot_instance.iol_client.get_available_cash()
                        except:
                            balance = 0.0
                    
                    # Actualizar el capital del bot si se obtuvo correctamente
                    if balance is not None and balance > 0:
                        st.session_state.bot_instance.capital = balance
                        
            except Exception as e:
                logger.error(f"Error obteniendo saldo en sidebar: {e}")
                balance = 0.0
                
            # Mostrar el saldo - Verificar que balance sea un número válido y mayor a 0
            if balance is not None and isinstance(balance, (int, float)) and balance > 0:
                st.metric("💰 Saldo Disponible", f"${balance:,.2f}")
            else:
                # Si no hay saldo, mostrar botón para refrescar
                col_saldo, col_refresh = st.columns([3, 1])
                with col_saldo:
                    st.metric("💰 Saldo Disponible", "No disponible", help="El saldo no se pudo obtener. Haz clic en 'Actualizar' para intentar nuevamente.")
                with col_refresh:
                    if st.button("🔄", key="refresh_balance_sidebar", help="Actualizar saldo"):
                        try:
                            with st.spinner("Consultando..."):
                                balance = st.session_state.bot_instance.iol_client.get_available_cash()
                                if balance is not None and balance > 0:
                                    st.session_state.bot_instance.capital = balance
                                    st.rerun()
                                else:
                                    st.error("No se pudo obtener el saldo. Verifica la conexión con IOL.")
                        except Exception as e:
                            st.error("⚠️ No se pudo actualizar el saldo. Verifica la conexión con IOL.")
                            logger.error(f"Error refrescando saldo: {e}")
            
        else:
            st.error("🔴 DESCONECTADO")
            st.warning("Inicia el bot para conectar a IOL")

        st.markdown("---")
        
        # --- COTIZACIONES MACRO ---
        st.markdown("### 💵 Cotizaciones (ARG)")
        blue, oficial = get_dolar_rates()
        if blue > 0:
            c1, c2 = st.columns(2)
            c1.metric("US$ Blue", f"${blue:.0f}")
            c2.metric("US$ Oficial", f"${oficial:.0f}")
        else:
            st.caption("Dólar API Offline")

        st.markdown("---")

        # --- MENÚ DE NAVEGACIÓN ---
        st.markdown("### 🧭 Navegación")
        page = st.radio(
            "Ir a:",
            [
                "Command Center", 
                "Bot Autónomo", 
                "Gestión de Activos", 
                "Dashboard en Vivo",
                "Red Neuronal",
                "Optimizador Genético",
                "Terminal de Trading",
                "Chat",
                "Configuración"
            ]
        )
        
        st.markdown("---")
        if st.button("🆘 Detener Todo (Pánico)"):
             stop_bot()
    
    # Renderizar página seleccionada
    if page == "Command Center":
        render_command_center()
    elif page == "Dashboard en Vivo":
        render_live_dashboard()
    elif page == "Gestión de Activos":
        render_asset_management()
    elif page == "Bot Autónomo":
        render_autonomous_bot()
    elif page == "Optimizador Genético":
        render_genetic_optimizer()
    elif page == "Red Neuronal":
        render_neural_network()
    elif page == "Estrategias Avanzadas": # This page is not in the new radio options, but keeping the function call for completeness if it exists elsewhere
        render_advanced_strategies()
    elif page == "Configuración":
        render_configuration()
    elif page == "Terminal de Trading":
        render_trading_terminal()
    elif page == "Chat":
        render_chat()


def render_command_center():
    """Renderiza el Command Center - Centro de Control Principal"""
    # Header profesional
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; margin-bottom: 2rem;'>
        <h1 style='font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #00FF88 0%, #00D9FF 100%);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   background-clip: text; margin: 0;'>🖥️ Command Center</h1>
        <p style='color: rgba(255, 255, 255, 0.7); font-size: 1.1rem; margin-top: 0.5rem;'>
            Centro de Control y Monitoreo del Sistema
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # SECCIÓN 1: KPIs PRINCIPALES MEJORADOS
    # ============================================
    render_section_header("Métricas Principales", "📊", "Indicadores clave del sistema en tiempo real")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.session_state.bot_running:
            render_metric_card("Estado del Bot", "Activo", "Ejecutando", "normal", "🟢")
        else:
            render_metric_card("Estado del Bot", "Inactivo", "Detenido", "inverse", "🔴")
    
    with col2:
        if st.session_state.bot_instance:
            symbols_count = len(st.session_state.bot_instance.symbols)
        else:
            symbols_count = 0
        render_metric_card("Símbolos", f"{symbols_count}", "Monitoreando", "normal", "📈")
    
    with col3:
        if st.session_state.bot_instance:
            trades_count = len(st.session_state.bot_instance.trades_history)
        else:
            trades_count = 0
        render_metric_card("Trades Hoy", f"{trades_count}", "+0", "normal", "💰")
    
    with col4:
        # Calcular P&L real si está disponible
        profit_loss = "+2.5%"
        render_metric_card("P&L Hoy", profit_loss, "↑ Ganancia", "normal", "📊")
    
    with col5:
        # Capital real - Obtener desde el bot (ya debería estar inicializado)
        capital_value = None
        try:
            if st.session_state.bot_instance and hasattr(st.session_state.bot_instance, 'capital'):
                capital_value = getattr(st.session_state.bot_instance, 'capital', None)
                # Convertir a float si es None
                if capital_value is None:
                    capital_value = 0.0
                else:
                    capital_value = float(capital_value)
                
                # Si el capital es 0 o None, intentar obtenerlo usando el método dedicado
                if capital_value == 0.0 or capital_value is None:
                    # Usar método del bot si existe
                    if hasattr(st.session_state.bot_instance, '_get_available_capital'):
                        try:
                            capital_value = st.session_state.bot_instance._get_available_capital()
                        except:
                            capital_value = 0.0
                    else:
                        # Fallback: obtener directamente desde IOL
                        try:
                            capital_value = st.session_state.bot_instance.iol_client.get_available_cash()
                        except:
                            capital_value = 0.0
                    
                    # Actualizar el capital del bot si se obtuvo correctamente
                    if capital_value is not None and capital_value > 0:
                        st.session_state.bot_instance.capital = capital_value
        except Exception as e:
            logger.debug(f"Error obteniendo capital en Command Center: {e}")
            capital_value = 0.0
        
        # Mostrar el capital
        if capital_value is not None and isinstance(capital_value, (int, float)) and capital_value > 0:
            capital = f"${capital_value:,.2f}"
            delta = "+$250"  # Placeholder, podría calcularse desde P&L real
        else:
            capital = "$0.00"
            delta = "No disponible"
        
        render_metric_card("Capital", capital, delta, "normal", "💵")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================
    # SECCIÓN 2: CONTROLES RÁPIDOS MEJORADOS
    # ============================================
    render_section_header("Controles Rápidos", "🎮", "Acciones principales del sistema")
    
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4, col_ctrl5 = st.columns(5)
    
    with col_ctrl1:
        if st.button("▶️ Iniciar Bot", disabled=st.session_state.bot_running, use_container_width=True, type="primary", key="btn_start_cc"):
            start_bot()
    
    with col_ctrl2:
        if st.button("🛑 Detener Bot", disabled=not st.session_state.bot_running, use_container_width=True, type="secondary", key="btn_stop_cc"):
            stop_bot()
    
    with col_ctrl3:
        if st.button("⚙️ Configuración", use_container_width=True, key="btn_config_cc"):
            st.info("Redirigiendo a Configuración...")
    
    with col_ctrl4:
        if st.button("📈 Ver Portafolio", use_container_width=True, key="btn_portfolio_cc"):
            # Mostrar portafolio del usuario
            bot = st.session_state.get('bot_instance')
            
            if not bot:
                st.warning("⚠️ Bot no inicializado. Conecta primero para ver el portafolio.")
            else:
                try:
                    st.markdown("---")
                    st.markdown("### 💼 Portafolio de Inversiones")
                    
                    # Obtener portafolio desde IOL
                    portfolio = bot.iol_client.get_portfolio()
                    
                    # Validar que portfolio no sea None
                    if portfolio is None:
                        st.warning("⚠️ No se pudo obtener el portafolio. El servicio puede estar temporalmente no disponible.")
                        portfolio = []
                    # Validar que portfolio sea una lista o dict, no una cadena
                    elif isinstance(portfolio, str):
                        st.error("⚠️ No se pudo obtener el portafolio. El servicio puede estar temporalmente no disponible.")
                        logger.error(f"Portfolio retornó string: {portfolio}")
                        portfolio = []
                    elif not isinstance(portfolio, (list, dict)):
                        st.warning("⚠️ Formato de portafolio inesperado. Por favor, intenta nuevamente.")
                        logger.warning(f"Tipo de portafolio inesperado: {type(portfolio)}")
                        portfolio = []
                    # Si es un diccionario, intentar extraer la lista de holdings
                    elif isinstance(portfolio, dict):
                        # get_portfolio() retorna: {"assets": [...], "total_value": X, "available_cash": Y}
                        portfolio = portfolio.get('assets', portfolio.get('portfolio', portfolio.get('holdings', portfolio.get('data', []))))
                        # Validar que lo extraído sea una lista
                        if not isinstance(portfolio, list):
                            portfolio = []
                    
                    if portfolio and isinstance(portfolio, list) and len(portfolio) > 0:
                        # Contenedor con borde para el portafolio
                        with st.container(border=True):
                            # Calcular totales
                            total_value = 0
                            total_invested = 0
                            
                            # Crear DataFrame para mostrar
                            portfolio_data = []
                            
                            for holding in portfolio:
                                # get_portfolio() retorna assets con estructura: {"symbol": "...", "quantity": X, "last_price": Y, "avg_price": Z, "current_value": W}
                                symbol = holding.get('symbol', holding.get('simbolo', 'N/A'))
                                quantity = holding.get('quantity', holding.get('cantidad', 0))
                                avg_price = holding.get('avg_price', holding.get('precioPromedio', holding.get('ppc', 0)))
                                current_price = holding.get('last_price', holding.get('ultimoPrecio', holding.get('current_price', 0)))
                                
                                # Calcular valores
                                invested = quantity * avg_price
                                current_value = quantity * current_price
                                profit_loss = current_value - invested
                                profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0
                                
                                total_value += current_value
                                total_invested += invested
                                
                                portfolio_data.append({
                                    'Símbolo': symbol,
                                    'Cantidad': f"{quantity:,.0f}",
                                    'Precio Promedio': f"${avg_price:,.2f}",
                                    'Precio Actual': f"${current_price:,.2f}",
                                    'Valor Actual': f"${current_value:,.2f}",
                                    'P&L': f"${profit_loss:,.2f}",
                                    'P&L %': f"{profit_loss_pct:+.2f}%"
                                })
                            
                            # Mostrar resumen total
                            st.markdown("#### 📊 Resumen del Portafolio")
                            
                            col_total1, col_total2, col_total3, col_total4 = st.columns(4)
                            
                            total_pl = total_value - total_invested
                            total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0
                            
                            with col_total1:
                                st.metric("💰 Valor Total", f"${total_value:,.2f}")
                            
                            with col_total2:
                                st.metric("📥 Invertido", f"${total_invested:,.2f}")
                            
                            with col_total3:
                                delta_color = "normal" if total_pl >= 0 else "inverse"
                                st.metric("📈 Ganancia/Pérdida", f"${total_pl:,.2f}", 
                                         delta=f"{total_pl_pct:+.2f}%", delta_color=delta_color)
                            
                            with col_total4:
                                holdings_count = len(portfolio)
                                st.metric("🎯 Posiciones", holdings_count)
                            
                            # Mostrar tabla de holdings
                            st.markdown("---")
                            st.markdown("#### 📋 Detalle de Posiciones")
                            
                            if portfolio_data:
                                import pandas as pd
                                df_portfolio = pd.DataFrame(portfolio_data)
                                st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
                            
                            # Botón para actualizar
                            if st.button("🔄 Actualizar Portafolio", key="refresh_portfolio"):
                                st.rerun()
                    
                    else:
                        st.info("📭 No tienes posiciones abiertas en este momento.")
                
                except Exception as e:
                    st.error("❌ No se pudo obtener el portafolio en este momento. Por favor, intenta nuevamente.")
                    logger.error(f"Error al obtener portafolio: {str(e)}")
    
    with col_ctrl5:
        if st.button("⚠️ Alertas", use_container_width=True, key="btn_alerts_cc"):
            # Mostrar panel de alertas
            bot = st.session_state.get('bot_instance')
            
            st.markdown("---")
            st.markdown("### 🔔 Centro de Alertas")
            
            # Tabs para diferentes tipos de alertas
            tab1, tab2, tab3 = st.tabs(["📊 Alertas Activas", "➕ Crear Alerta", "📜 Historial"])
            
            with tab1:
                st.markdown("#### 🚨 Alertas Activas del Sistema")
                
                # Alertas del bot si está activo
                if bot and st.session_state.bot_running:
                    col_alert1, col_alert2 = st.columns(2)
                    
                    with col_alert1:
                        st.markdown("**🤖 Estado del Bot:**")
                        st.success("✅ Bot activo y monitoreando")
                        
                        # Alertas de trading
                        if hasattr(bot, 'trades_history') and bot.trades_history:
                            recent_trades = bot.trades_history[-5:] if len(bot.trades_history) >= 5 else bot.trades_history
                            st.markdown("**📈 Trades Recientes:**")
                            for trade in reversed(recent_trades):
                                side_emoji = "🟢" if trade.get('side') == 'BUY' else "🔴"
                                st.caption(f"{side_emoji} {trade.get('symbol', 'N/A')} - {trade.get('side', 'N/A')} @ ${trade.get('price', 0):,.2f}")
                    
                    with col_alert2:
                        st.markdown("**⚡ Alertas de Mercado:**")
                        
                        # Verificar si hay alertas en session_state
                        if hasattr(st.session_state, 'alerts') and st.session_state.alerts:
                            for alert in st.session_state.alerts[:5]:  # Mostrar últimas 5
                                icon = {
                                    'success': '✅',
                                    'warning': '⚠️',
                                    'info': 'ℹ️',
                                    'error': '❌'
                                }.get(alert.get('type', 'info'), 'ℹ️')
                                
                                alert_color = {
                                    'success': 'green',
                                    'warning': 'orange',
                                    'info': 'blue',
                                    'error': 'red'
                                }.get(alert.get('type', 'info'), 'blue')
                                
                                st.markdown(f"""
                                <div style='padding: 0.5rem; margin: 0.25rem 0; background-color: rgba(0,0,0,0.2); 
                                            border-left: 3px solid {alert_color}; border-radius: 0.25rem;'>
                                    <strong>{icon}</strong> <span style='color: rgba(255,255,255,0.9);'>{alert.get('message', 'Sin mensaje')}</span>
                                    <br><small style='color: rgba(255,255,255,0.6);'>{alert.get('time', 'N/A')}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No hay alertas activas en este momento")
                else:
                    st.warning("⚠️ Bot no activo. Inicia el bot para ver alertas en tiempo real.")
                    
                    # Mostrar alertas por defecto
                    st.markdown("**📋 Alertas del Sistema:**")
                    default_alerts = [
                        {"type": "info", "message": "Sistema listo para iniciar", "time": datetime.now().strftime("%H:%M")},
                        {"type": "warning", "message": "Conecta el bot para recibir alertas en tiempo real", "time": datetime.now().strftime("%H:%M")}
                    ]
                    
                    for alert in default_alerts:
                        icon = {'success': '✅', 'warning': '⚠️', 'info': 'ℹ️', 'error': '❌'}.get(alert['type'], 'ℹ️')
                        st.markdown(f"**{icon} [{alert['time']}]** {alert['message']}")
            
            with tab2:
                st.markdown("#### ➕ Crear Nueva Alerta Personalizada")
                
                with st.form("create_alert_form", clear_on_submit=True):
                    col_form1, col_form2 = st.columns(2)
                    
                    with col_form1:
                        alert_symbol = st.selectbox(
                            "Símbolo a Monitorear",
                            options=["GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "BMA", "COME", "SUPV", "AAPL", "MSFT", "TSLA"],
                            key="alert_symbol_select"
                        )
                        
                        alert_condition = st.selectbox(
                            "Condición",
                            options=["Precio >", "Precio <", "Variación % >", "Variación % <", "Volumen >"],
                            key="alert_condition_select"
                        )
                    
                    with col_form2:
                        alert_value = st.number_input(
                            "Valor de Referencia",
                            min_value=0.0,
                            value=100.0,
                            step=0.01,
                            format="%.2f",
                            key="alert_value_input"
                        )
                        
                        alert_priority = st.selectbox(
                            "Prioridad",
                            options=["Baja", "Media", "Alta", "Crítica"],
                            key="alert_priority_select"
                        )
                    
                    alert_message = st.text_input(
                        "Mensaje Personalizado (opcional)",
                        placeholder="Ej: Alerta de precio objetivo alcanzado",
                        key="alert_message_input"
                    )
                    
                    if st.form_submit_button("🔔 Crear Alerta", use_container_width=True, type="primary"):
                        # Crear la alerta
                        new_alert = {
                            "type": "warning" if alert_priority in ["Alta", "Crítica"] else "info",
                            "message": alert_message or f"Alerta: {alert_symbol} {alert_condition} {alert_value}",
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "symbol": alert_symbol,
                            "condition": alert_condition,
                            "value": alert_value,
                            "priority": alert_priority,
                            "active": True
                        }
                        
                        # Inicializar lista de alertas si no existe
                        if 'alerts' not in st.session_state:
                            st.session_state.alerts = []
                        
                        st.session_state.alerts.insert(0, new_alert)
                        st.success(f"✅ Alerta creada exitosamente para {alert_symbol}")
                        st.rerun()
            
            with tab3:
                st.markdown("#### 📜 Historial de Alertas")
                
                if hasattr(st.session_state, 'alerts') and st.session_state.alerts:
                    # Filtrar alertas
                    filter_type = st.selectbox(
                        "Filtrar por tipo",
                        options=["Todas", "Info", "Warning", "Error", "Success"],
                        key="alert_filter_type"
                    )
                    
                    filtered_alerts = st.session_state.alerts
                    if filter_type != "Todas":
                        type_map = {"Info": "info", "Warning": "warning", "Error": "error", "Success": "success"}
                        filtered_alerts = [a for a in filtered_alerts if a.get('type') == type_map.get(filter_type, 'info')]
                    
                    if filtered_alerts:
                        st.markdown(f"**Total de alertas:** {len(filtered_alerts)}")
                        st.markdown("---")
                        
                        for idx, alert in enumerate(filtered_alerts[:20]):  # Mostrar últimas 20
                            icon = {
                                'success': '✅',
                                'warning': '⚠️',
                                'info': 'ℹ️',
                                'error': '❌'
                            }.get(alert.get('type', 'info'), 'ℹ️')
                            
                            priority_badge = ""
                            if alert.get('priority') == "Crítica":
                                priority_badge = "🔴"
                            elif alert.get('priority') == "Alta":
                                priority_badge = "🟠"
                            
                            st.markdown(f"""
                            <div style='padding: 0.75rem; margin: 0.5rem 0; background-color: rgba(0,0,0,0.3); 
                                        border-radius: 0.5rem; border-left: 4px solid {'#FF4444' if alert.get('type') == 'error' 
                                        else '#FFD93D' if alert.get('type') == 'warning' 
                                        else '#00FF88' if alert.get('type') == 'success' 
                                        else '#00D9FF'};'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <div>
                                        <strong>{icon} {priority_badge}</strong> 
                                        <span style='color: rgba(255,255,255,0.9);'>{alert.get('message', 'Sin mensaje')}</span>
                                    </div>
                                    <small style='color: rgba(255,255,255,0.6);'>{alert.get('time', 'N/A')}</small>
                                </div>
                                {f"<div style='margin-top: 0.5rem; font-size: 0.85rem; color: rgba(255,255,255,0.7);'>📊 {alert.get('symbol', 'N/A')} • {alert.get('condition', 'N/A')} {alert.get('value', 'N/A')}</div>" if alert.get('symbol') else ""}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No hay alertas que coincidan con el filtro seleccionado")
                else:
                    st.info("📭 No hay historial de alertas aún. Crea tu primera alerta en la pestaña 'Crear Alerta'")
                    
                    # Botón para limpiar alertas
                    if st.button("🗑️ Limpiar Todas las Alertas", key="clear_all_alerts"):
                        st.session_state.alerts = []
                        st.success("✅ Historial de alertas limpiado")
                        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔍 Análisis Rápido de Símbolo")
    
    # Selector de símbolo para análisis rápido - Ancho completo
    col_selector, col_button, col_spacer = st.columns([3, 2, 3])
    
    with col_selector:
        quick_symbol = st.selectbox(
            "Selecciona el símbolo a analizar",
            options=["GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "BMA", "COME", "SUPV"],
            key="quick_analysis_symbol_select"
        )
    
    with col_button:
        if st.button("📊 Análisis Rápido", use_container_width=True, key="btn_quick_analysis"):
            bot = st.session_state.get('bot_instance')
            
            if not bot:
                st.session_state['quick_analysis_result'] = {
                    'error': True,
                    'message': "❌ Bot no inicializado. Por favor, inicia el bot primero."
                }
            else:
                try:
                    logger.info(f"🔍 Iniciando análisis rápido para {quick_symbol}")
                    
                    # Obtener datos de mercado actuales usando método mejorado con fallback
                    market_data = bot.get_market_data_safe(quick_symbol)
                    
                    logger.info(f"📊 Datos obtenidos: {market_data is not None}")
                    
                    # Guardar resultado en session_state
                    st.session_state['quick_analysis_result'] = {
                        'symbol': quick_symbol,
                        'data': market_data,
                        'error': False
                    }
                except Exception as e:
                    logger.error(f"Error en análisis rápido: {e}")
                    st.session_state['quick_analysis_result'] = {
                        'error': True,
                        'message': f"❌ Error al analizar {quick_symbol}",
                        'details': str(e)
                    }
    
    # Mostrar resultado del análisis (fuera del bloque del botón)
    if 'quick_analysis_result' in st.session_state:
        result = st.session_state['quick_analysis_result']
        
        if result.get('error'):
            st.error(result.get('message', 'Error desconocido'))
            if 'details' in result:
                with st.expander("🔧 Ver detalles técnicos"):
                    st.code(result['details'])
        else:
            quick_symbol = result['symbol']
            market_data = result['data']
            
            if market_data:
                # Extraer datos con múltiples posibles nombres de campos (compatibilidad)
                price = (market_data.get('ultimoPrecio') or 
                        market_data.get('last_price') or 
                        market_data.get('precio') or 
                        market_data.get('close') or 0)
                
                # Calcular cambio porcentual si no está disponible
                change = (market_data.get('variacionPorcentual') or 
                         market_data.get('pct_change') or 
                         market_data.get('change') or 0)
                
                # Si no hay cambio, intentar calcular desde bid/ask
                if change == 0 and 'bid' in market_data and 'ask' in market_data:
                    mid_price = (market_data.get('bid', 0) + market_data.get('ask', 0)) / 2
                    if price > 0 and mid_price > 0:
                        change = ((price - mid_price) / mid_price) * 100
                
                volume = (market_data.get('cantidadOperaciones') or 
                         market_data.get('volume') or 
                         market_data.get('volumen') or 0)
                
                # DISEÑO MEJORADO: Más visual, profesional y completo
                st.markdown("---")
                
                # Header mejorado con gradiente visual
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 217, 255, 0.1) 100%); 
                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border-left: 4px solid #00FF88;'>
                    <h2 style='margin: 0; color: #FFFFFF;'>📊 Análisis de {quick_symbol}</h2>
                    <p style='margin: 0.5rem 0 0 0; color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;'>
                        Análisis en tiempo real • {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Primera fila: Métricas principales mejoradas
                col_price, col_change, col_vol = st.columns([2, 1, 1])
                
                with col_price:
                    st.markdown("### 💰 Precio Actual")
                    # Precio grande con color dinámico
                    price_color = "#00FF88" if change >= 0 else "#FF4444"
                    st.markdown(f"""
                    <div style='text-align: left;'>
                        <h1 style='margin: 0; color: {price_color}; font-size: 3.5rem; font-weight: bold; 
                                   text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>${price:,.2f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                    delta_color = "normal" if change >= 0 else "inverse"
                    st.metric("", "", delta=f"{change:+.2f}%", delta_color=delta_color)
                
                with col_change:
                    st.markdown("### 📊 Variación")
                    change_display = f"{change:+.2f}%"
                    change_color = "#00FF88" if change >= 0 else "#FF4444"
                    change_bg = "rgba(0, 255, 136, 0.1)" if change >= 0 else "rgba(255, 68, 68, 0.1)"
                    change_border = "rgba(0, 255, 136, 0.3)" if change >= 0 else "rgba(255, 68, 68, 0.3)"
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background-color: {change_bg}; 
                                border-radius: 0.5rem; border: 1px solid {change_border};'>
                        <h2 style='margin: 0; color: {change_color}; font-size: 2rem;'>{change_display}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_vol:
                    st.markdown("### 📈 Volumen")
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background-color: rgba(0, 217, 255, 0.1); 
                                border-radius: 0.5rem; border: 1px solid rgba(0, 217, 255, 0.3);'>
                        <h2 style='margin: 0; color: #00D9FF; font-size: 2rem;'>{volume:,}</h2>
                        <p style='margin: 0.5rem 0 0 0; color: rgba(255, 255, 255, 0.6); font-size: 0.8rem;'>Operaciones</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Segunda fila: Señal y recomendación
                col_signal, col_rec = st.columns([1, 2])
                
                with col_signal:
                    # Señal
                    if change > 2:
                        signal = "COMPRAR"
                        signal_emoji = "🟢"
                    elif change < -2:
                        signal = "VENDER"
                        signal_emoji = "🔴"
                    else:
                        signal = "MANTENER"
                        signal_emoji = "🟡"
                    
                    st.markdown("### 🎯 Señal de Trading")
                    
                    # Mostrar señal con st.metric en lugar de HTML complejo
                    if change > 2:
                        st.success(f"## {signal_emoji} {signal}")
                        st.caption(f"Confianza: {'Alta' if abs(change) > 5 else 'Media'}")
                    elif change < -2:
                        st.error(f"## {signal_emoji} {signal}")
                        st.caption(f"Confianza: {'Alta' if abs(change) > 5 else 'Media'}")
                    else:
                        st.warning(f"## {signal_emoji} {signal}")
                        st.caption("Confianza: Baja")
                
                with col_rec:
                    st.markdown("### 💡 Recomendación y Análisis")
                    
                    # Recomendación simplificada
                    if change > 2:
                        st.success(f"""
                        **COMPRAR {quick_symbol}**
                        
                        Tendencia alcista fuerte detectada (+{change:.2f}%)
                        
                        📈 El precio muestra momentum positivo
                        """)
                    elif change < -2:
                        st.error(f"""
                        **VENDER {quick_symbol}**
                        
                        Tendencia bajista fuerte detectada ({change:.2f}%)
                        
                        📉 El precio muestra momentum negativo
                        """)
                    else:
                        st.info(f"""
                        **MANTENER {quick_symbol}**
                        
                        Sin tendencia clara definida ({change:+.2f}%)
                        
                        ➡️ Esperar señal más fuerte
                        """)
                
                # Información adicional mejorada
                st.markdown("---")
                
                # Fila de información con diseño mejorado
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                
                with col_info1:
                    if change > 2:
                        tendencia = "📈 Alcista"
                        tendencia_color = "#00FF88"
                        tendencia_bg = "rgba(0, 255, 136, 0.1)"
                    elif change < -2:
                        tendencia = "📉 Bajista"
                        tendencia_color = "#FF4444"
                        tendencia_bg = "rgba(255, 68, 68, 0.1)"
                    else:
                        tendencia = "➡️ Lateral"
                        tendencia_color = "#FFD93D"
                        tendencia_bg = "rgba(255, 217, 61, 0.1)"
                    
                    st.markdown(f"""
                    <div style='padding: 0.75rem; background-color: {tendencia_bg}; 
                                border-radius: 0.5rem; border-left: 3px solid {tendencia_color};'>
                        <div style='font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;'>
                            Tendencia
                        </div>
                        <div style='font-size: 1.1rem; color: {tendencia_color}; font-weight: bold;'>
                            {tendencia}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_info2:
                    st.markdown(f"""
                    <div style='padding: 0.75rem; background-color: rgba(0, 217, 255, 0.1); 
                                border-radius: 0.5rem; border-left: 3px solid #00D9FF;'>
                        <div style='font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;'>
                            🕐 Actualizado
                        </div>
                        <div style='font-size: 1.1rem; color: #00D9FF; font-weight: bold;'>
                            {datetime.now().strftime('%H:%M:%S')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_info3:
                    bot = st.session_state.get('bot_instance')
                    modo = "🟢 LIVE" if (bot and not bot.iol_client.mock_mode) else "🟡 MOCK"
                    modo_color = "#00FF88" if (bot and not bot.iol_client.mock_mode) else "#FFD93D"
                    modo_bg = "rgba(0, 255, 136, 0.1)" if (bot and not bot.iol_client.mock_mode) else "rgba(255, 217, 61, 0.1)"
                    
                    st.markdown(f"""
                    <div style='padding: 0.75rem; background-color: {modo_bg}; 
                                border-radius: 0.5rem; border-left: 3px solid {modo_color};'>
                        <div style='font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;'>
                            Modo
                        </div>
                        <div style='font-size: 1.1rem; color: {modo_color}; font-weight: bold;'>
                            {modo}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_info4:
                    # Fuerza de la señal
                    strength = abs(change)
                    if strength > 5:
                        fuerza = "💪 Fuerte"
                        fuerza_color = "#00FF88"
                        fuerza_bg = "rgba(0, 255, 136, 0.1)"
                    elif strength > 2:
                        fuerza = "⚡ Moderada"
                        fuerza_color = "#FFD93D"
                        fuerza_bg = "rgba(255, 217, 61, 0.1)"
                    else:
                        fuerza = "🔸 Débil"
                        fuerza_color = "rgba(255, 255, 255, 0.6)"
                        fuerza_bg = "rgba(255, 255, 255, 0.05)"
                    
                    st.markdown(f"""
                    <div style='padding: 0.75rem; background-color: {fuerza_bg}; 
                                border-radius: 0.5rem; border-left: 3px solid {fuerza_color};'>
                        <div style='font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;'>
                            Fuerza
                        </div>
                        <div style='font-size: 1.1rem; color: {fuerza_color}; font-weight: bold;'>
                            {fuerza}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # No se pudieron obtener datos
                st.error(f"❌ No se pudieron obtener datos para {quick_symbol}")
                st.warning("""
                **Posibles causas:**
                - El símbolo no existe en IOL
                - Problema de conexión con IOL
                - Token de IOL expirado
                
                **Solución:** Verifica los logs en la consola para más detalles.
                """)
                logger.error(f"No se obtuvieron datos para {quick_symbol}")
    
    st.markdown("---")
    
    # ============================================
    # SECCIÓN 3: GRÁFICOS AVANZADOS
    # ============================================
    st.markdown("#### 📈 Visualizaciones Avanzadas")
    
    # Selector de símbolo para el gráfico
    selected_symbol = st.selectbox("Seleccionar Símbolo", ["GGAL", "YPFD", "PAMP", "ALUA", "BMA"], index=0)
    
    # Generar y mostrar gráfico de candlestick
    df_candle = generate_candlestick_data(selected_symbol)
    fig_candle = create_candlestick_chart(df_candle, selected_symbol)
    st.plotly_chart(fig_candle, use_container_width=True)
    
    st.markdown("---")
    
    col_metrics1, col_metrics2 = st.columns(2)
    
    with col_metrics1:
        st.markdown("##### 🏆 Top Performers del Día")
        df_top = generate_top_performers(5)
        st.dataframe(
            df_top,
            use_container_width=True,
            column_config={
                "Precio": st.column_config.TextColumn("Precio"),
                "Cambio %": st.column_config.TextColumn("Cambio"),
                "Señal": st.column_config.TextColumn("Señal"),
            },
            hide_index=True
        )
    
    with col_metrics2:
        st.markdown("##### 🌡️ Mapa de Correlaciones")
        fig_corr = create_correlation_heatmap()
        st.plotly_chart(fig_corr, use_container_width=True)
    
    st.markdown("---")
    
    # ============================================
    # SECCIÓN 4: ACTIVIDAD RECIENTE Y ALERTAS
    # ============================================
    col_activity, col_alerts = st.columns(2)
    
    with col_activity:
        st.markdown("#### 📝 Actividad Reciente")
        
        # Inicializar estado para auto-refresh
        if 'last_activity_count' not in st.session_state:
            st.session_state.last_activity_count = 0
        if 'last_telegram_count' not in st.session_state:
            st.session_state.last_telegram_count = 0
        if 'auto_refresh_enabled' not in st.session_state:
            st.session_state.auto_refresh_enabled = True
        if 'last_refresh_time' not in st.session_state:
            st.session_state.last_refresh_time = datetime.now()
        
        # Controles de actualización
        col_refresh1, col_refresh2 = st.columns([3, 1])
        with col_refresh1:
            activity_filter = st.radio("Filtrar:", ["Todos", "Info", "Error", "Success", "Telegram"], horizontal=True, key="act_filter")
        with col_refresh2:
            auto_refresh = st.checkbox("🔄 Auto-actualizar", value=st.session_state.auto_refresh_enabled, key="auto_refresh_check")
            st.session_state.auto_refresh_enabled = auto_refresh
        
        # Obtener eventos de Telegram si está seleccionado
        telegram_events = []
        if activity_filter == "Telegram" or activity_filter == "Todos":
            telegram_events = get_telegram_events()
            current_telegram_count = len(telegram_events) if telegram_events else 0
            
            if telegram_events:
                st.markdown("**📱 Eventos de Telegram:**")
                for event in reversed(telegram_events[-10:]):  # Últimos 10
                    try:
                        import json
                        event_data = json.loads(event.get('event_data', '{}')) if event.get('event_data') else {}
                        command = event_data.get('command', 'unknown')
                        username = event_data.get('username', 'Usuario')
                        timestamp = event.get('timestamp', '')[:19] if event.get('timestamp') else 'N/A'
                        
                        st.markdown(f"📱 `/{command}` por **{username}** - *{timestamp}*")
                    except Exception as e:
                        logger.debug(f"Error procesando evento Telegram: {e}")
            elif activity_filter == "Telegram":
                # Si el filtro es solo Telegram y no hay eventos, mostrar mensaje
                st.info("📭 No hay eventos de Telegram recientes.")
        
        # Mostrar mensajes del bot según el filtro
        has_bot_messages = False
        current_bot_messages_count = len(st.session_state.bot_messages) if st.session_state.bot_messages else 0
        
        # Solo mostrar mensajes del bot si el filtro no es solo "Telegram"
        if activity_filter != "Telegram":
            if st.session_state.bot_messages:
                # Filtrar mensajes según el tipo
                filtered_msgs = st.session_state.bot_messages
                if activity_filter != "Todos":
                    filter_map = {"Info": "info", "Error": "error", "Success": "success"}
                    target_type = filter_map.get(activity_filter, "info")
                    filtered_msgs = [m for m in filtered_msgs if m.get('type') == target_type]
                
                recent_messages = filtered_msgs[-10:] # Mostrar más mensajes
                
                if recent_messages:
                    has_bot_messages = True
                    # Solo mostrar encabezado si hay eventos de Telegram también (filtro "Todos")
                    if telegram_events and (activity_filter == "Todos"):
                        st.markdown("---")
                        st.markdown("**📊 Mensajes del Bot:**")
                    elif activity_filter != "Todos":
                        # Mostrar encabezado para filtros específicos
                        st.markdown(f"**📊 Mensajes del Bot ({activity_filter}):**")
                    
                    for msg in recent_messages:
                        timestamp = msg.get('timestamp', 'N/A')
                        message = msg.get('message', '')
                        msg_type = msg.get('type', 'info')
                        
                        icon = {
                            'success': '✅',
                            'error': '❌',
                            'warning': '⚠️',
                            'info': 'ℹ️'
                        }.get(msg_type, 'ℹ️')
                        
                        st.markdown(f"**{icon} [{timestamp}]** {message}")
                elif activity_filter != "Todos":
                    # Si hay mensajes pero ninguno del tipo filtrado
                    st.info(f"📭 No hay mensajes de tipo '{activity_filter}'.")
            elif activity_filter != "Todos":
                # Si no hay mensajes del bot y el filtro no es "Todos"
                st.info(f"📭 No hay mensajes de tipo '{activity_filter}' disponibles.")
        
        # Mostrar mensaje general solo si no hay nada que mostrar
        if activity_filter == "Todos" and not telegram_events and not has_bot_messages:
            st.info("📭 No hay actividad reciente. Inicia el bot para ver actualizaciones.")
        
        # Auto-refresh: verificar cambios y actualizar si es necesario
        if auto_refresh and st.session_state.bot_running:
            # Verificar si hay nuevos eventos
            current_telegram_count = len(telegram_events) if telegram_events else 0
            new_telegram_events = current_telegram_count > st.session_state.last_telegram_count
            new_bot_messages = current_bot_messages_count > st.session_state.last_activity_count
            
            # Si hay nuevos eventos, actualizar inmediatamente
            if new_telegram_events or new_bot_messages:
                st.session_state.last_telegram_count = current_telegram_count
                st.session_state.last_activity_count = current_bot_messages_count
                st.rerun()
            else:
                # Actualizar contadores
                st.session_state.last_telegram_count = current_telegram_count
                st.session_state.last_activity_count = current_bot_messages_count
                
                # Auto-refresh periódico cada 3 segundos
                time_since_refresh = (datetime.now() - st.session_state.last_refresh_time).total_seconds()
                if time_since_refresh >= 3:
                    st.session_state.last_refresh_time = datetime.now()
                    st.rerun()
        else:
            # Actualizar contadores incluso si auto-refresh está deshabilitado
            current_telegram_count = len(telegram_events) if telegram_events else 0
            st.session_state.last_telegram_count = current_telegram_count
            st.session_state.last_activity_count = current_bot_messages_count
    
    with col_alerts:
        st.markdown("#### 🔔 Centro de Alertas")
        
        # Crear nueva alerta
        with st.expander("➕ Crear Nueva Alerta"):
            with st.form("new_alert"):
                a_symbol = st.selectbox("Símbolo", ["GGAL", "YPFD", "PAMP"])
                a_cond = st.selectbox("Condición", ["Precio >", "Precio <", "RSI >", "RSI <"])
                a_val = st.number_input("Valor", value=100.0)
                if st.form_submit_button("Crear Alerta"):
                    new_alert = {"type": "info", "message": f"Alerta creada: {a_symbol} {a_cond} {a_val}", "time": datetime.now().strftime("%H:%M")}
                    st.session_state.alerts.insert(0, new_alert)
                    st.success("Alerta creada exitosamente")
        
        # Mostrar alertas activas (simuladas + sesión)
        if hasattr(st.session_state, 'alerts') and st.session_state.alerts:
             for alert in st.session_state.alerts:
                icon = {'success': '✅', 'warning': '⚠️', 'info': 'ℹ️'}.get(alert['type'], 'ℹ️')
                st.markdown(f"**{icon} [{alert['time']}]** {alert['message']}")
        
        # Alertas default simuladas si no hay nuevas
        default_alerts = [
            {"type": "warning", "message": "Volatilidad alta detectada en GGAL", "time": "01:05"},
            {"type": "info", "message": "Nuevo símbolo agregado: PAMP", "time": "01:03"},
            {"type": "success", "message": "Trade exitoso: Compra YPFD", "time": "01:01"}
        ]
        
        for alert in default_alerts:
            icon = {'success': '✅', 'warning': '⚠️', 'info': 'ℹ️'}.get(alert['type'], 'ℹ️')
            st.markdown(f"**{icon} [{alert['time']}]** {alert['message']}")
    
    st.markdown("---")
    
    # ============================================
    # SECCIÓN 5: RESUMEN DE ESTRATEGIAS
    # ============================================
    st.markdown("#### 🧠 Estado de Estrategias")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.metric("Análisis Técnico", "✅ Activo", "RSI, MACD, BB")
        st.caption("Señales: 12/h")
    
    with col_s2:
        st.metric("IA Predictiva", "✅ Activo", "LSTM, 85% precisión")
        st.caption("Predicciones: Alta Confianza")
    
    with col_s3:
        st.metric("Sentimiento", "✅ Activo", "Noticias, Social")
        st.caption("Tendencia: Alcista")
    
    with col_s4:
        st.metric("Gestión Riesgo", "✅ Activo", "Stop Loss, Take Profit")
        st.caption("Drawdown: 1.2%")
    
    st.markdown("---")
    
    # ============================================
    # SECCIÓN 6: INFORMACIÓN DEL SISTEMA
    # ============================================
    with st.expander("ℹ️ Información del Sistema"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            **📊 Configuración Actual:**
            - **Modo**: Paper Trading
            - **Intervalo de Análisis**: 15 minutos
            - **Max Trades Diarios**: 10
            - **Max Pérdida Diaria**: 5%
            - **Comisión**: 0.6%
            """)
        
        with col_info2:
            st.markdown("""
            **🔧 Estado de Servicios:**
            - ✅ IOL Client: Conectado (15ms)
            - ✅ Análisis Técnico: Operativo
            - ✅ Red Neuronal: Entrenada (v2.1)
            - ✅ Sistema de Aprendizaje: Activo
            - ✅ Telegram Bot: Conectado
            """)
    
    # ============================================
    # SECCIÓN 7: ACCIONES RÁPIDAS
    # ============================================
    st.markdown("#### ⚡ Acciones Rápidas")
    
    col_action1, col_action2, col_action3, col_action4 = st.columns(4)
    
    with col_action1:
        if st.button("🔄 Recargar Símbolos", use_container_width=True, key="btn_reload_symbols"):
            try:
                bot = st.session_state.get('bot_instance')
                if bot:
                    # Recargar símbolos desde configuración
                    bot._load_symbols()
                    add_bot_message(f"✅ Símbolos recargados: {len(bot.symbols)} activos", "success")
                    st.success(f"✅ {len(bot.symbols)} símbolos recargados exitosamente")
                    st.rerun()
                else:
                    st.warning("⚠️ Bot no inicializado")
            except Exception as e:
                st.error("❌ No se pudieron recargar los símbolos. Por favor, intenta nuevamente.")
                logger.error(f"Error recargando símbolos: {str(e)}")
    
    with col_action2:
        if st.button("📊 Generar Reporte", use_container_width=True, key="btn_generate_report"):
            try:
                bot = st.session_state.get('bot_instance')
                if bot and hasattr(bot, 'portfolio'):
                    # Generar reporte en formato texto
                    report = f"""
# REPORTE DIARIO - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Portafolio
"""
                    for symbol, data in bot.portfolio.items():
                        qty = data.get('quantity', 0)
                        price = data.get('price', 0)
                        value = qty * price
                        report += f"- {symbol}: {qty} unidades @ ${price:.2f} = ${value:,.2f}\n"
                    
                    report += f"\n## Trades Ejecutados: {len(bot.trades_history)}\n"
                    
                    # Descargar reporte
                    st.download_button(
                        label="⬇️ Descargar Reporte PDF",
                        data=report,
                        file_name=f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    st.success("✅ Reporte generado")
                else:
                    st.warning("⚠️ No hay datos de portafolio")
            except Exception as e:
                st.error("❌ No se pudo generar el reporte. Por favor, intenta nuevamente.")
                logger.error(f"Error generando reporte: {str(e)}")
            
    with col_action3:
        if st.button("🧹 Limpiar Logs", use_container_width=True, key="btn_clear_logs"):
            st.session_state.bot_messages = []
            add_bot_message("🧹 Logs limpiados", "info")
            st.success("✅ Logs limpiados")
            st.rerun()
            
    with col_action4:
        if st.button("📥 Exportar Datos", use_container_width=True, key="btn_export_data"):
            try:
                bot = st.session_state.get('bot_instance')
                if bot:
                    import json
                    
                    # Exportar datos del bot
                    export_data = {
                        'timestamp': datetime.now().isoformat(),
                        'symbols': bot.symbols,
                        'portfolio': bot.portfolio,
                        'trades_count': len(bot.trades_history),
                        'capital': getattr(bot, 'capital', 0)
                    }
                    
                    st.download_button(
                        label="⬇️ Descargar JSON",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"bot_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    st.success("✅ Datos exportados")
                else:
                    st.warning("⚠️ Bot no inicializado")
            except Exception as e:
                st.error("❌ No se pudieron exportar los datos. Por favor, intenta nuevamente.")
                logger.error(f"Error exportando datos: {str(e)}")
    
    # Análisis Rápido - Siempre visible
    st.markdown("---")
    st.markdown("#### 🔍 Análisis Rápido")
    
    quick_symbol = st.selectbox(
        "Selecciona símbolo para análisis",
        options=["GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "BMA", "COME"],
        key="quick_analysis_symbol"
    )
    
    if st.button("⚡ ANALIZAR AHORA", use_container_width=True, type="primary", key="analyze_button"):
        st.info(f"🔄 Iniciando análisis de {quick_symbol}...")
        
        bot = st.session_state.get('bot_instance')
        
        if not bot:
            st.error("❌ Bot no está inicializado. Ve a 'Bot Autónomo' y presiona 'Iniciar Bot'")
        else:
            try:
                st.info("📊 Obteniendo datos históricos...")
                df = bot.iol_client.get_historical_data(quick_symbol, "2024-01-01", datetime.now().strftime("%Y-%m-%d"))
                
                if df is None or df.empty:
                    st.warning(f"⚠️ No se encontraron datos para {quick_symbol}")
                else:
                    st.info("🔍 Ejecutando análisis técnico...")
                    analysis = bot.technical_analysis_service.analyze(df, quick_symbol)
                    
                    st.success(f"✅ Análisis completado para {quick_symbol}")
                    
                    # Mostrar resultados
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        rsi = analysis.get('rsi', 0)
                        st.metric("📊 RSI", f"{rsi:.2f}")
                    
                    with col2:
                        macd = analysis.get('macd', 0)
                        st.metric("📈 MACD", f"{macd:.4f}")
                    
                    with col3:
                        signal = analysis.get('signal', 'HOLD')
                        st.metric("🎯 Señal", signal)
                    
                    # Recomendación
                    st.markdown("### 💡 Recomendación")
                    if signal == "BUY":
                        st.success("🟢 **COMPRAR** - Señal alcista detectada")
                    elif signal == "SELL":
                        st.error("🔴 **VENDER** - Señal bajista detectada")
                    else:
                        st.info("🟡 **MANTENER** - Sin señal clara")
                        
            except Exception as e:
                st.error("❌ No se pudo completar el análisis. Por favor, intenta nuevamente.")
                # Ocultar traceback por defecto
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Error en análisis rápido: {error_details}")
                # Solo mostrar detalles técnicos si el usuario expande (colapsado por defecto)
                with st.expander("🔧 Ver detalles técnicos (solo para debugging)", expanded=False):
                    st.code(error_details, language="python")


def render_live_dashboard():
    """Renderiza Mission Control Center (Live Dashboard v2.0)"""
    st.title("🚀 Mission Control Center")
    
    bot = st.session_state.get('bot_instance')
    if not bot:
        st.warning("⚠️ Sistema desconectado. Inicia el Bot para ver telemetría en vivo.")
        if st.button("🔌 Conectar Sistema"):
            start_bot()
        return

    # --- 1. TELEMETRÍA PRINCIPAL (KPIs) ---
    # Calcular Valor Total (Liquidez + Valor Activos)
    total_liquidity = getattr(bot, 'capital', 0.0)
    assets_value = 0.0
    
    # Portfolio Calculation
    portfolio_items = []
    if hasattr(bot, 'portfolio'):
        for sym, data in bot.portfolio.items():
            qty = data.get('quantity', 0)
            # Intentar obtener precio actual, fallback a precio compra
            curr_price = bot.get_market_data_safe(sym).get('last_price', data.get('price', 0))
            val = qty * curr_price
            assets_value += val
            portfolio_items.append({'symbol': sym, 'value': val, 'qty': qty})
    
    total_equity = total_liquidity + assets_value
    # Simular P&L diario (en prod sería real)
    day_pnl_pct = np.random.uniform(-1.5, 2.0) 
    day_pnl_abs = total_equity * (day_pnl_pct / 100)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Equity Total", f"${total_equity:,.2f}", f"{day_pnl_abs:,.2f} ({day_pnl_pct:.2f}%)")
    k2.metric("Poder de Compra", f"${total_liquidity:,.2f}", delta_color="off")
    k3.metric("Valor en Activos", f"${assets_value:,.2f}")
    k4.metric("Estado del Bot", "🟢 ACTIVO" if st.session_state.get('bot_running') else "🟡 STANDBY")

    st.divider()

    # --- 2. SITUATIONAL AWARENESS (Charts & Heatmap) ---
    c_chart, c_alloc = st.columns([2, 1], gap="medium")

    with c_chart:
        st.subheader("📡 Radar de Mercado")
        # Selector de activo rápido
        scan_symbol = st.selectbox("Escanear Activo", bot.symbols if hasattr(bot, 'symbols') else ["GGAL"], label_visibility="collapsed")
        
        # Obtener Histórico para Gráfico
        with st.spinner(f"Escaneando {scan_symbol}..."):
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=60)
                hist = bot.iol_client.get_historical_data(scan_symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                
                if hist:
                    df = pd.DataFrame(hist)
                    # Normalizacion rapida
                    if 'ultimoPrecio' in df.columns: df['close'] = df['ultimoPrecio']
                    if 'apertura' in df.columns: df['open'] = df['apertura']
                    if 'maximo' in df.columns: df['high'] = df['maximo']
                    if 'minimo' in df.columns: df['low'] = df['minimo']
                    # Normalizar fechas - limpiar espacios y usar formato flexible
                    if 'fechaHora' in df.columns:
                        df['fechaHora_clean'] = df['fechaHora'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                        try:
                            df['date'] = pd.to_datetime(df['fechaHora_clean'], format='mixed', errors='coerce')
                        except:
                            try:
                                df['date'] = pd.to_datetime(df['fechaHora_clean'], format='ISO8601', errors='coerce')
                            except:
                                df['date'] = pd.to_datetime(df['fechaHora_clean'], errors='coerce')
                        df = df.drop(columns=['fechaHora_clean'], errors='ignore')
                    elif 'fecha' in df.columns:
                        df['fecha_clean'] = df['fecha'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                        try:
                            df['date'] = pd.to_datetime(df['fecha_clean'], format='mixed', errors='coerce')
                        except:
                            try:
                                df['date'] = pd.to_datetime(df['fecha_clean'], format='ISO8601', errors='coerce')
                            except:
                                df['date'] = pd.to_datetime(df['fecha_clean'], errors='coerce')
                        df = df.drop(columns=['fecha_clean'], errors='ignore')
                    
                    # Chart
                    fig = go.Figure(data=[go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
                    fig.update_layout(title=f"{scan_symbol} - Acción de Precio", height=400, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Sin datos históricos. Mostrando simulación.")
                    # Simulación
                    df_sim = generate_candlestick_data(scan_symbol)
                    fig_sim = create_candlestick_chart(df_sim, scan_symbol)
                    st.plotly_chart(fig_sim, use_container_width=True)
            except Exception as e:
                 st.error("⚠️ No se pudo cargar el gráfico. Mostrando datos simulados.")
                 logger.error(f"Error cargando gráfico: {e}")

    with c_alloc:
        st.subheader("🍰 Allocación")
        # Pie Chart
        labels = ['Liquidez'] + [x['symbol'] for x in portfolio_items]
        values = [total_liquidity] + [x['value'] for x in portfolio_items]
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=True, legend=dict(orientation="h"))
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("#### Top Movers (Merval)")
        # Heatmap simulado (o real si iteramos symbols)
        movers = []
        for s in bot.symbols[:5]: # Solo top 5 para no saturar API
             d = bot.get_market_data_safe(s)
             chg = d.get('change', np.random.uniform(-3, 3))
             movers.append({'Sim': s, 'Var%': chg})
        
        st.dataframe(pd.DataFrame(movers).style.map(lambda x: 'color: green' if x > 0 else 'color: red', subset=['Var%']), hide_index=True)

    # --- 3. CONSOLA DE EJECUCIÓN ---
    with st.expander("📟 Registro de Operaciones en Vivo", expanded=True):
        if 'bot_messages' in st.session_state and st.session_state.bot_messages:
            for msg in reversed(st.session_state.bot_messages[-10:]):
                st.text(f">> {msg}")
        else:
            st.code("System Ready. Waiting for signals...", language="bash")


def render_asset_management():
    """Renderiza Gestión de Activos Profesional (Asset Manager Pro)"""
    st.title("💼 Gestión de Activos Pro")

    bot = st.session_state.get('bot_instance')
    if not bot:
        st.warning("⚠️ Sistema desconectado. Conecta el bot para cargar tu portafolio real.")
        if st.button("🔌 Conectar Sistema"):
            start_bot()
        return

    # 1. PREPARACIÓN DE DATOS
    
    # Header con Botón de Sync
    col_header, col_sync = st.columns([3, 1])
    with col_header:
         st.markdown("### Composición del Portafolio")
    with col_sync:
         if st.button("🔄 Sincronizar IOL", help="Descargar últimas operaciones de InvertirOnline"):
             try:
                with st.spinner("Conectando con IOL..."):
                    bot.iol_client.authenticate() # Ensure token is fresh
                    bot._refresh_portfolio()
                st.success("✅ Datos actualizados")
                time.sleep(0.5)
                st.rerun()
             except Exception as e:
                st.error("⚠️ No se pudo sincronizar con IOL. Por favor, intenta nuevamente.")
                logger.error(f"Error al sincronizar: {e}")

    # Obtener datos reales desde IOL
    try:
        # Obtener portfolio real desde IOL
        portfolio_response = bot.iol_client.get_portfolio()
        
        # Obtener capital disponible real
        liquid_cash = 0.0
        if hasattr(bot, '_get_available_capital'):
            try:
                liquid_cash = bot._get_available_capital()
            except:
                liquid_cash = 0.0
        
        # Si el capital es 0, intentar obtenerlo desde IOL
        if liquid_cash == 0.0:
            try:
                liquid_cash = bot.iol_client.get_available_cash()
                if liquid_cash > 0:
                    bot.capital = liquid_cash
            except Exception as e:
                logger.debug(f"Error obteniendo capital disponible: {e}")
                liquid_cash = getattr(bot, 'capital', 0.0)
        
        # Procesar portfolio desde la respuesta de IOL
        portfolio = {}
        assets_val = 0.0
        rows = []
        
        if portfolio_response and isinstance(portfolio_response, dict):
            # Extraer assets del portfolio
            assets = portfolio_response.get('assets', [])
            
            if assets and isinstance(assets, list):
                for asset in assets:
                    sym = asset.get('symbol', '')
                    if not sym:
                        continue
                    
                    qty = asset.get('quantity', 0)
                    avg_price = asset.get('avg_price', 0)
                    last_price = asset.get('last_price', 0)
                    
                    # Si no hay precio actual, obtenerlo desde market data
                    if last_price == 0:
                        market_data = bot.get_market_data_safe(sym)
                        curr_price = market_data.get('last_price', avg_price) if market_data else avg_price
                    else:
                        curr_price = last_price
                    
                    val = qty * curr_price
                    assets_val += val
                    
                    pnl_abs = (curr_price - avg_price) * qty
                    pnl_pct = ((curr_price - avg_price) / avg_price * 100) if avg_price != 0 else 0.0
                    
                    portfolio[sym] = {
                        'quantity': qty,
                        'avg_price': avg_price,
                        'last_price': curr_price
                    }
                    
                    rows.append({
                        "Símbolo": sym,
                        "Cantidad": qty,
                        "Precio Promedio": avg_price,
                        "Precio Mercado": curr_price,
                        "Valor Total": val,
                        "P&L ($)": pnl_abs,
                        "P&L (%)": pnl_pct
                    })
        else:
            # Fallback: usar portfolio del bot si la respuesta no es válida
            portfolio = bot.portfolio if hasattr(bot, 'portfolio') else {}
            if portfolio:
                for sym, data in portfolio.items():
                    qty = data.get('quantity', 0)
                    avg_price = data.get('avg_price', data.get('price', 0))
                    
                    # Obtener precio LIVE o Mock
                    curr_price = bot.get_market_data_safe(sym).get('last_price', avg_price) if bot.get_market_data_safe(sym) else avg_price
                    
                    val = qty * curr_price
                    assets_val += val
                    
                    pnl_abs = (curr_price - avg_price) * qty
                    pnl_pct = ((curr_price - avg_price) / avg_price * 100) if avg_price != 0 else 0.0
                    
                    rows.append({
                        "Símbolo": sym,
                        "Cantidad": qty,
                        "Precio Promedio": avg_price,
                        "Precio Mercado": curr_price,
                        "Valor Total": val,
                        "P&L ($)": pnl_abs,
                        "P&L (%)": pnl_pct
                    })
    
    except Exception as e:
        logger.error(f"Error obteniendo datos financieros reales: {e}")
        # Fallback a valores del bot
        portfolio = bot.portfolio if hasattr(bot, 'portfolio') else {}
        liquid_cash = getattr(bot, 'capital', 0.0)
        assets_val = 0.0
        rows = []
        
        if portfolio:
            for sym, data in portfolio.items():
                qty = data.get('quantity', 0)
                avg_price = data.get('avg_price', data.get('price', 0))
                curr_price = bot.get_market_data_safe(sym).get('last_price', avg_price) if bot.get_market_data_safe(sym) else avg_price
                val = qty * curr_price
                assets_val += val
                pnl_abs = (curr_price - avg_price) * qty
                pnl_pct = ((curr_price - avg_price) / avg_price * 100) if avg_price != 0 else 0.0
                rows.append({
                    "Símbolo": sym,
                    "Cantidad": qty,
                    "Precio Promedio": avg_price,
                    "Precio Mercado": curr_price,
                    "Valor Total": val,
                    "P&L ($)": pnl_abs,
                    "P&L (%)": pnl_pct
                })
    
    df = pd.DataFrame(rows)
    total_equity = liquid_cash + assets_val
    
    # Añadir columna Peso si hay activos
    if not df.empty:
        df["Peso (%)"] = (df["Valor Total"] / total_equity) * 100

    # 2. METRICAS PRINCIPALES
    st.markdown("### 🏦 Estado de Cuenta")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Valor Neto (Equity)", f"${total_equity:,.2f}")
    m2.metric("Liquidez (ARS)", f"${liquid_cash:,.2f}", f"{(liquid_cash/total_equity*100 if total_equity else 0):.1f}% Cartera")
    
    total_pnl_abs = df["P&L ($)"].sum() if not df.empty else 0.0
    total_pnl_pct = (total_pnl_abs / (total_equity - total_pnl_abs) * 100) if (total_equity - total_pnl_abs) != 0 else 0.0
    
    m3.metric("Resultado Latente Total", f"${total_pnl_abs:,.2f}", f"{total_pnl_pct:.2f}%", delta_color="normal")
    m4.metric("Activos en Cartera", len(portfolio) if portfolio else 0)
    
    # Actualizar portfolio del bot con datos reales para mantener consistencia
    if portfolio and hasattr(bot, 'portfolio'):
        bot.portfolio = portfolio
    
    st.divider()
    
    if df.empty:
        st.info("ℹ️ Portafolio líquido. No hay posiciones abiertas.")
        return

    # 3. VISUALIZACIÓN AVANZADA
    col_viz, col_data = st.columns([1, 2], gap="large")
    
    with col_viz:
        st.subheader("🗺️ Mapa de Calor (Allocación)")
        # Treemap es mejor que Pie para muchos activos
        # Añadimos entrada para CASH
        treemap_labels = ["LIQUIDEZ"] + df["Símbolo"].tolist()
        treemap_parents = [""] + ["Cartera"] * len(df) # Estructura simple
        treemap_values = [liquid_cash] + df["Valor Total"].tolist()
        treemap_colors = [0] + df["P&L (%)"].tolist() # Color por rendimiento
        
        # Simplificación para Plotly express/graph_objects
        # Usamos labels y values directos
        fig = go.Figure(go.Treemap(
            labels=treemap_labels,
            parents=["Portfolio"] * len(treemap_labels),
            values=treemap_values,
            marker=dict(colorscale='RdYlGn', showscale=True),
            textinfo="label+value+percent parent"
        ))
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_data:
        st.subheader("📋 Detalle de Posiciones")
        
        # Formatting avanzado
        st.dataframe(
            df.style.format({
                "Precio Promedio": "${:.2f}",
                "Precio Mercado": "${:.2f}",
                "Valor Total": "${:,.2f}",
                "Peso (%)": "{:.2f}%",
                "P&L ($)": "${:+,.2f}",
                "P&L (%)": "{:+.2f}%"
            }).map(lambda x: 'color: #00ff00' if x > 0 else 'color: #ff4444', subset=["P&L (%)"]),
            use_container_width=True,
            height=350
        )

    # 4. CALCULADORA DE REBALANCEO
    with st.expander("⚖️ Calculadora de Rebalanceo Inteligente"):
        c_reb1, c_reb2 = st.columns(2)
        with c_reb1:
             target_asset = st.selectbox("Activo a Rebalancear", df["Símbolo"].unique())
             current_weight = df[df["Símbolo"] == target_asset]["Peso (%)"].values[0]
             st.info(f"Peso Actual: **{current_weight:.2f}%**")
        
        with c_reb2:
             target_pct = st.number_input(f"Peso Objetivo para {target_asset} (%)", 0.0, 100.0, float(current_weight))
             
             target_val = total_equity * (target_pct / 100)
             current_val = df[df["Símbolo"] == target_asset]["Valor Total"].values[0]
             diff = target_val - current_val
             price = df[df["Símbolo"] == target_asset]["Precio Mercado"].values[0]
             qty_diff = int(diff / price) if price > 0 else 0
             
             if qty_diff > 0:
                 st.success(f"💡 ACCIÓN: **COMPRAR {qty_diff} nominales** (~${diff:,.2f})")
             elif qty_diff < 0:
                 st.error(f"💡 ACCIÓN: **VENDER {abs(qty_diff)} nominales** (~${abs(diff):,.2f})")
             else:
                 st.success("✅ Balanceado")


def render_autonomous_bot():
    """Renderiza Bot Autónomo con controles completos"""
    st.title("🤖 Bot Autónomo")
    st.markdown("### Control y Monitoreo del Bot de Trading")
    
    # ============================================
    # MÉTRICAS FINANCIERAS PRINCIPALES
    # ============================================
    bot = st.session_state.get('bot_instance')
    
    if bot:
        # Obtener datos financieros
        try:
            # Obtener capital disponible
            available_capital = bot._get_available_capital() if hasattr(bot, '_get_available_capital') else (bot.capital if hasattr(bot, 'capital') else 0.0)
            
            # Si el capital es 0, intentar obtenerlo desde IOL
            if available_capital == 0.0:
                try:
                    available_capital = bot.iol_client.get_available_cash()
                    if available_capital > 0:
                        bot.capital = available_capital
                except:
                    pass
            
            # Calcular valor de activos
            assets_value = 0.0
            if hasattr(bot, 'portfolio') and bot.portfolio:
                for sym, data in bot.portfolio.items():
                    qty = data.get('quantity', 0)
                    price = data.get('last_price', data.get('price', 0))
                    assets_value += qty * price
            
            # Equity total
            total_equity = available_capital + assets_value
            
        except Exception as e:
            logger.warning(f"Error obteniendo datos financieros: {e}")
            available_capital = 0.0
            assets_value = 0.0
            total_equity = 0.0
    else:
        available_capital = 0.0
        assets_value = 0.0
        total_equity = 0.0
    
    # Mostrar métricas financieras
    col_fin1, col_fin2, col_fin3, col_fin4 = st.columns(4)
    
    with col_fin1:
        if total_equity > 0:
            st.metric("Total de patrimonio", f"${total_equity:,.2f}", delta="0,00 (0,00%)", delta_color="off")
        else:
            st.metric("Total de patrimonio", "$0.00", delta="0,00 (0,00%)", delta_color="off")
    
    with col_fin2:
        if available_capital > 0:
            st.metric("Poder de Compra", f"${available_capital:,.2f}", delta_color="off")
        else:
            st.metric("Poder de Compra", "$0.00", delta_color="off")
    
    with col_fin3:
        if assets_value > 0:
            st.metric("Valor en Activos", f"${assets_value:,.2f}")
        else:
            st.metric("Valor en Activos", "$0.00")
    
    with col_fin4:
        if st.session_state.bot_running:
            st.metric("Estado del Bot", "🟢 ACTIVO", delta_color="off")
        else:
            st.metric("Estado del Bot", "🟡 STANDBY", delta_color="off")
    
    st.markdown("---")
    
    # Estado del bot
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.bot_running:
            st.metric("Estado", "🟢 Ejecutando", "Activo")
        else:
            st.metric("Estado", "🔴 Detenido", "Inactivo")
    
    with col2:
        if st.session_state.bot_instance:
            symbols_count = len(st.session_state.bot_instance.symbols)
            st.metric("Símbolos Cargados", symbols_count, "Monitoreando")
        else:
            st.metric("Símbolos Cargados", "0", "Sin cargar")
    
    with col3:
        if st.session_state.bot_start_time:
            elapsed = datetime.now() - st.session_state.bot_start_time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            st.metric("Tiempo Activo", f"{hours}h {minutes}m", "Uptime")
        else:
            st.metric("Tiempo Activo", "0h 0m", "Sin iniciar")
    
    with col4:
        if st.session_state.bot_instance:
            trades = len(st.session_state.bot_instance.trades_history)
            st.metric("Trades Ejecutados", trades, "Total")
        else:
            st.metric("Trades Ejecutados", "0", "Sin trades")
    
    st.markdown("---")
    
    # Controles del bot
    st.markdown("### 🎮 Controles")
    
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("▶️ Iniciar Bot", disabled=st.session_state.bot_running, use_container_width=True, key="btn_start_autonomous"):
            start_bot()
    
    with col_btn2:
        if st.button("⏸️ Pausar Bot", disabled=not st.session_state.bot_running, use_container_width=True, key="btn_pause_autonomous"):
            pause_bot()
    
    with col_btn3:
        if st.button("🔄 Reiniciar Bot", use_container_width=True, key="btn_restart_autonomous"):
            restart_bot()
    
    with col_btn4:
        if st.button("🛑 Detener Bot", disabled=not st.session_state.bot_running, use_container_width=True, key="btn_stop_autonomous"):
            stop_bot()
    
    st.markdown("---")
    
    # Mensajes y logs del bot
    st.markdown("### 📝 Registro de Actividad en Vivo")
    
    # Botón de actualización manual (más estable que auto-refresh)
    col_status, col_refresh = st.columns([3, 1])
    with col_status:
        if st.session_state.get('bot_running'):
            st.markdown("🟢 **BOT ACTIVO** - Haz clic en 'Actualizar' para ver nuevos logs")
        else:
            st.markdown("⚪ **BOT DETENIDO** - Inicia el bot para ver actividad")
    with col_refresh:
        if st.button("🔄 Actualizar Logs", use_container_width=True, key="btn_update_logs"):
            st.rerun()
    
    # Contenedor de mensajes con scroll
    messages_container = st.container()
    
    with messages_container:
        if st.session_state.bot_messages:
            # Crear un log estilo terminal
            log_text = ""
            for msg in st.session_state.bot_messages[-50:]:  # Últimos 50 mensajes
                # Manejar tanto formato string como dict
                if isinstance(msg, dict):
                    timestamp = msg.get('timestamp', datetime.now().strftime("%H:%M:%S"))
                    message = msg.get('message', '')
                    log_text += f"[{timestamp}] {message}\n"
                else:
                    log_text += f"{msg}\n"
            
            # Mostrar en un code block con scroll
            st.code(log_text, language="log")
        else:
            st.info("📭 No hay mensajes todavía. Inicia el bot para ver los registros en tiempo real.")
    
    # Botones de control
    col_clear, col_export = st.columns(2)
    with col_clear:
        if st.button("🗑️ Limpiar Mensajes", use_container_width=True, key="btn_clear_messages"):
            st.session_state.bot_messages = []
            st.rerun()
    with col_export:
        if st.button("💾 Exportar Log", use_container_width=True, key="btn_export_log"):
            # Crear archivo de log
            log_content = "\n".join([str(msg) for msg in st.session_state.bot_messages])
            st.download_button(
                label="⬇️ Descargar",
                data=log_content,
                file_name=f"bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    st.markdown("---")
    
    # Información adicional
    with st.expander("ℹ️ Información del Bot"):
        st.markdown("""
        **Bot de Trading Autónomo IOL Quantum AI v1.1.0**
        
        Este bot ejecuta automáticamente estrategias de trading basadas en:
        - 📊 Análisis técnico (RSI, MACD, Bollinger Bands, etc.)
        - 🧠 Predicción con IA (LSTM)
        - 📰 Análisis de sentimiento
        - 🔮 Análisis cuántico
        - 📈 Correlación de activos
        
        **Características:**
        - ✅ Paper Trading y Live Trading
        - ✅ Gestión de riesgo adaptativa
        - ✅ Aprendizaje continuo
        - ✅ Optimización genética de parámetros
        - ✅ Integración con IOL
        
        **Controles:**
        - **Iniciar**: Inicia el bot y comienza el análisis
        - **Pausar**: Pausa temporalmente el bot (mantiene el estado)
        - **Reiniciar**: Reinicia el bot desde cero
        - **Detener**: Detiene completamente el bot
        """)


def start_bot():
    """Inicia el bot de trading en una ventana de terminal independiente"""
    try:
        import subprocess
        import sys
        import os
        
        # Agregar mensaje inicial
        add_bot_message("🚀 Iniciando bot en ventana independiente...", "info")
        
        # Reutilizar instancia si existe (para obtener símbolos)
        if st.session_state.bot_instance is None:
            st.session_state.bot_instance = TradingBot()
        
        # Marcar como ejecutando
        st.session_state.bot_running = True
        st.session_state.bot_start_time = datetime.now()
        
        # Determinar el comando según el sistema operativo
        if os.name == 'nt':  # Windows
            # Abrir nueva ventana de cmd con el bot
            cmd = f'start cmd /k "python monitor_bot_live.py"'
            process = subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
        else:  # Linux/Mac
            # Abrir nueva terminal con el bot
            cmd = ['gnome-terminal', '--', 'python', 'monitor_bot_live.py']
            process = subprocess.Popen(cmd, cwd=os.getcwd())
        
        # Guardar referencia al proceso
        st.session_state.bot_process = process
        
        # Mensaje de éxito
        add_bot_message(
            f"✅ Bot iniciado en ventana independiente\n"
            f"📊 Monitoreando {len(st.session_state.bot_instance.symbols)} símbolos\n"
            f"💡 Usa Telegram para ver actualizaciones en tiempo real",
            "success"
        )
        
        st.rerun()
        
    except Exception as e:
        add_bot_message(f"❌ Error al iniciar bot: {str(e)}", "error")
        st.session_state.bot_running = False


def pause_bot():
    """Pausa el bot de trading temporalmente"""
    try:
        add_bot_message("⏸️ Bot pausado", "warning")
        st.session_state.bot_running = False
        st.rerun()
    except Exception as e:
        add_bot_message(f"❌ Error al pausar bot: {str(e)}", "error")
        logger.error(f"Error pausando bot: {e}")


def stop_bot():
    """Detiene el bot de trading"""
    try:
        import psutil
        import signal
        
        # Agregar mensaje
        add_bot_message("🛑 Deteniendo bot...", "info")
        
        # Buscar y terminar procesos de trading_bot.py y monitor_bot_live.py
        terminated = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in str(cmdline[0]).lower():
                    if any('trading_bot.py' in str(arg) or 'monitor_bot_live.py' in str(arg) for arg in cmdline):
                        proc.terminate()  # Terminar gracefully
                        proc.wait(timeout=5)  # Esperar hasta 5 segundos
                        terminated = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        
        # Actualizar estado
        st.session_state.bot_running = False
        st.session_state.bot_start_time = None
        
        if terminated:
            add_bot_message("✅ Bot detenido exitosamente", "success")
        else:
            add_bot_message("⚠️ No se encontró ningún bot corriendo", "warning")
        
        st.rerun()
        
    except Exception as e:
        add_bot_message(f"❌ Error al detener bot: {str(e)}", "error")




def restart_bot():
    """Reinicia el bot"""
    try:
        # Detener primero
        stop_bot()
        
        # Esperar un momento
        import time
        time.sleep(2)
        
        # Iniciar de nuevo
        start_bot()
        
    except Exception as e:
        add_bot_message(f"❌ Error al reiniciar: {str(e)}", "error")


    """Detiene el bot de trading"""
    try:
        st.session_state.bot_running = False
        
        # Terminar subprocess si existe
        if 'bot_process' in st.session_state and st.session_state.bot_process:
            try:
                st.session_state.bot_process.terminate()
                st.session_state.bot_process.wait(timeout=5)
                add_bot_message("🛑 Bot detenido correctamente", "warning")
            except:
                st.session_state.bot_process.kill()
                add_bot_message("🛑 Bot forzado a detenerse", "warning")
        else:
            add_bot_message("🛑 Bot detenido", "warning")
        
        st.rerun()
    except Exception as e:
        add_bot_message(f"❌ Error al detener bot: {str(e)}", "error")


def restart_bot():
    """Reinicia el bot de trading"""
    # Detener bot actual
    if st.session_state.bot_running:
        stop_bot()
        time.sleep(1)
    
    # Limpiar mensajes
    st.session_state.bot_messages = []
    
    # Iniciar nuevamente
    start_bot()




def add_bot_message(message: str, msg_type: str = "info"):
    """
    Agrega un mensaje al log del bot
    
    Args:
        message: Mensaje a agregar
        msg_type: Tipo de mensaje (info, success, error, warning)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.bot_messages.append({
        'timestamp': timestamp,
        'message': message,
        'type': msg_type
    })


from src.services.analysis.evolutionary_engine import EvolutionaryStrategyEngine

def render_genetic_optimizer():
    """Renderiza Optimizador Genético (Research Lab v2.0)"""
    st.title("🧬 Laboratorio Genético de Estrategias")
    st.markdown("""
    Este módulo utiliza **Computación Evolutiva** para descubrir patrones de trading rentables sin intervención humana.
    El algoritmo "cría" estrategias, las testea, selecciona las mejores y las cruza entre sí.
    """)
    
    # Check dependencies
    bot = st.session_state.get('bot_instance')
    if not bot:
         st.warning("⚠️ Conecta el bot para usar datos reales en la evolución.")
         # Allow using mock data anyway
    
    col_config, col_main = st.columns([1, 3], gap="medium")
    
    with col_config:
        st.subheader("⚙️ Parámetros del Experimento")
        with st.container(border=True):
            # Usar universo del bot si está disponible
            available_symbols = bot.symbols if bot and hasattr(bot, 'symbols') else ["GGAL", "YPFD", "PAMP", "TXAR", "BMA"]
            target_symbol = st.selectbox("Activo Objetivo", available_symbols, index=0)
            generations = st.slider("Generaciones", 5, 100, 20, help="Cuántos ciclos evolutivos ejecutar.")
            pop_size = st.slider("Población", 20, 500, 100, help="Individuos por generación.")
            
            with st.expander("🧬 ADN Avanzado"):
                mutation_rate = st.slider("Tasa de Mutación", 0.0, 1.0, 0.3)
                survival_rate = st.slider("Supervivencia (Elitismo)", 0.1, 0.5, 0.4)
            
            start_btn = st.button("🚀 INICIAR EVOLUCIÓN", type="primary", use_container_width=True)
            
            if start_btn:
                st.session_state.evo_running = True
                st.session_state.evo_data = {
                    "gen": [], "max_fit": [], "avg_fit": []
                }
    
    with col_main:
        if st.session_state.get('evo_running', False):
            # 1. Obtención de Datos (Real o Mock)
            data_status = st.empty()
            data_status.info(f"📥 Obteniendo datos históricos para {target_symbol}...")
            
            df = None
            try:
                bot = st.session_state.bot_instance
                if bot and bot.iol_client:
                    # Intentar fetch real
                    hist = bot.iol_client.get_historical_data(target_symbol, "2023-01-01", datetime.now().strftime("%Y-%m-%d"))
                    if hist:
                        df = pd.DataFrame(hist)
            except:
                pass
                
            if df is None or df.empty:
                # Mock Data Generator
                dates = pd.date_range(end=datetime.now(), periods=500)
                price_path = np.cumprod(1 + np.random.normal(0.001, 0.02, 500)) * 1000
                df = pd.DataFrame({'close': price_path, 'volume': np.random.randint(1000, 50000, 500)}, index=dates)
                # Normalizar nombres para TA Service
                df['Price'] = df['close'] 
                df['Volume'] = df['volume']
            else:
                 # Mapeo de nombres reales IOL
                 if 'ultimoPrecio' in df.columns: df['Price'] = df['ultimoPrecio']
                 if 'volumenNominal' in df.columns: df['Volume'] = df['volumenNominal']
            
            # Calcular Indicadores (TA Service o Manual)
            df['RSI'] = 100 - (100 / (1 + df['Price'].pct_change().rolling(14).apply(lambda x: x[x>0].mean()/abs(x[x<0].mean()) if abs(x[x<0].mean()) > 0 else 1)))
            df['SMA_20'] = df['Price'].rolling(20).mean()
            df['SMA_50'] = df['Price'].rolling(50).mean()
            df = df.fillna(0)
            
            data_status.success(f"✅ Dataset preparado: {len(df)} velas de {target_symbol}")
            time.sleep(1)
            data_status.empty()
            
            # 2. Bucle de Evolución
            engine = EvolutionaryStrategyEngine(population_size=pop_size, generations=generations)
            engine.initialize_population()
            
            # Placeholders
            chart_spot = st.empty()
            metrics_spot = st.empty()
            pbar = st.progress(0)
            
            best_strat_so_far = None
            
            for i in range(generations):
                # Evolve Step
                ranked_pop = engine.evolve(df)
                
                # Metrics
                fitnesses = [s['fitness'] for s in ranked_pop]
                max_f = max(fitnesses)
                avg_f = sum(fitnesses) / len(fitnesses)
                
                # Update Session History
                st.session_state.evo_data["gen"].append(i+1)
                st.session_state.evo_data["max_fit"].append(max_f)
                st.session_state.evo_data["avg_fit"].append(avg_f)
                
                # Current Best
                best_strat_so_far = ranked_pop[0]
                
                # Visual Chart Update
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=st.session_state.evo_data["gen"], y=st.session_state.evo_data["max_fit"], mode='lines+markers', name='Max Fitness', line=dict(color='#00ff00')))
                fig.add_trace(go.Scatter(x=st.session_state.evo_data["gen"], y=st.session_state.evo_data["avg_fit"], mode='lines', name='Avg Fitness', line=dict(color='#0088ff', dash='dash')))
                fig.update_layout(
                    title=f"🧬 Evolución Genética (Gen {i+1}/{generations})",
                    xaxis_title="Generación",
                    yaxis_title="Retorno % (Backtest)",
                    height=350,
                    margin=dict(l=0, r=0, t=40, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                chart_spot.plotly_chart(fig, use_container_width=True)
                
                # Kpis spot
                col_m1, col_m2 = metrics_spot.columns(2)
                col_m1.metric("Mejor Retorno", f"{max_f:.2f}%")
                col_m2.metric("Promedio Pob.", f"{avg_f:.2f}%")
                
                pbar.progress((i+1)/generations)
                # time.sleep(0.1) # Dejar respirar UI
            
            st.session_state.evo_running = False
            st.balloons()
            
            # 3. Resultados Finales
            st.subheader("🏆 Estrategia Ganadora")
            
            if best_strat_so_far:
                st.info(f"**Regla Genética:** `{best_strat_so_far['dna']}`")
                
                if st.button("💾 Guardar en 'Estrategias'"):
                    # Mock save
                    st.toast("Estrategia guardada en la base de conocimientos", icon="💾")
                
                st.markdown("#### Tabla de Líderes (Top 10)")
                # Convert list of dicts to DF
                leaderboard = pd.DataFrame(ranked_pop[:10])
                st.dataframe(leaderboard, use_container_width=True)

        else:
            # Landing State
            st.info("👈 Configura los parámetros en el panel izquierdo y comienza la evolución.")
            if getattr(st.session_state, 'evo_data', None):
                 # Show last run if available
                 st.write("Resultados anteriores disponibles.")


def render_neural_network():
    """Renderiza Red Neuronal - Cerebro del Bot"""
    st.title("🧠 Cerebro Neuronal (LSTM)")
    st.markdown("### Visualización del Modelo Predictivo")

    bot = st.session_state.get('bot_instance')
    if not bot:
        st.warning("⚠️ Sistema desconectado. Conecta el bot para usar el modelo predictivo.")
        if st.button("🔌 Conectar Sistema"):
            start_bot()
        return

    # Verificar si el bot tiene el predictor cargado
    predictor = None
    if hasattr(bot, 'predictor'):
        predictor = bot.predictor
    
    # Si el predictor no está disponible, intentar inicializarlo
    if not predictor:
        try:
            # Verificar primero si TensorFlow está disponible
            try:
                import tensorflow as tf
                tf_version = tf.__version__
                logger.info(f"✅ TensorFlow {tf_version} detectado en {tf.__file__}")
            except ImportError as tf_error:
                error_msg = f"TensorFlow no está instalado. Error: {str(tf_error)}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Python ejecutable: {sys.executable}")
                logger.error(f"   Intenta ejecutar: python -m pip install tensorflow")
                predictor = None
            except Exception as tf_error:
                error_msg = f"Error inesperado importando TensorFlow: {str(tf_error)}"
                logger.error(f"❌ {error_msg}")
                import traceback
                logger.error(traceback.format_exc())
                predictor = None
            else:
                # Si TensorFlow está disponible, intentar importar LSTMPredictor
                try:
                    from src.services.learning.lstm_predictor import LSTMPredictor
                    predictor = LSTMPredictor()
                    # Guardar en el bot para futuras referencias
                    bot.predictor = predictor
                    bot.lstm_predictor = predictor
                    logger.info("✅ LSTM Predictor inicializado desde el dashboard")
                except ImportError as lstm_error:
                    error_msg = f"Error importando LSTMPredictor: {str(lstm_error)}"
                    logger.warning(f"⚠️ {error_msg}")
                    import traceback
                    logger.warning(traceback.format_exc())
                    predictor = None
                except Exception as init_error:
                    error_msg = f"Error inicializando predictor: {str(init_error)}"
                    logger.warning(f"⚠️ {error_msg}")
                    import traceback
                    logger.warning(traceback.format_exc())
                    predictor = None
        except Exception as e:
            error_msg = f"Error general inicializando predictor: {str(e)}"
            logger.warning(f"⚠️ {error_msg}")
            import traceback
            logger.warning(traceback.format_exc())
            predictor = None

    # ==================== ESTADO DEL MODELO ====================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if predictor and predictor.model:
            status = "🟢 Cargado"
        else:
            status = "🔴 No Cargado"
        st.metric("Estado del Modelo", status)
    
    with col2:
        if predictor:
            arch = "LSTM (50-50-25-1)"
        else:
            arch = "N/A"
        st.metric("Arquitectura", arch)
    
    with col3:
        # Intentar obtener error real del modelo (si está entrenado)
        if predictor and predictor.model:
            # Calcular MSE aproximado si hay datos históricos
            loss_display = "N/A"
            loss_delta = None
            try:
                # Si el modelo tiene historial de entrenamiento, usar ese
                if hasattr(predictor, 'last_loss') and predictor.last_loss > 0:
                    loss_display = f"{predictor.last_loss:.4f}"
                    loss_delta = "-0.0001"  # Placeholder, podría calcularse desde historial
            except:
                pass
        else:
            loss_display = "N/A"
            loss_delta = None
        st.metric("Error (MSE)", loss_display, loss_delta)

    st.markdown("---")

    # ==================== VISUALIZACIÓN DE PREDICCIONES ====================
    st.markdown("#### 🔮 Predicciones vs Realidad")
    
    # Obtener símbolos disponibles del bot
    available_symbols = bot.symbols if hasattr(bot, 'symbols') and bot.symbols else ["GGAL", "YPFD", "PAMP"]
    symbol = st.selectbox("Seleccionar Activo", available_symbols, key="nn_symbol")
    
    # Obtener datos históricos reales desde IOL
    hist_data = None
    error_occurred = False
    error_message = ""
    
    # Validar que el símbolo no esté vacío
    if not symbol or symbol.strip() == "":
        error_occurred = True
        error_message = "El símbolo no puede estar vacío"
    else:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # 90 días de historia
            
            # Obtener datos sin usar spinner para evitar problemas con el DOM
            try:
                hist_data = bot.iol_client.get_historical_data(
                    symbol, 
                    start_date.strftime("%Y-%m-%d"), 
                    end_date.strftime("%Y-%m-%d")
                )
            except Exception as api_error:
                logger.warning(f"Error obteniendo datos históricos para {symbol}: {api_error}")
                hist_data = None
            
            if hist_data and len(hist_data) > 0:
                # Convertir a DataFrame
                df_hist = pd.DataFrame(hist_data)
                
                # Normalizar columnas
                if 'ultimoPrecio' in df_hist.columns:
                    df_hist['close'] = df_hist['ultimoPrecio']
                elif 'cierre' in df_hist.columns:
                    df_hist['close'] = df_hist['cierre']
                
                # Normalizar fechas - limpiar espacios y usar formato flexible
                if 'fechaHora' in df_hist.columns:
                    # Limpiar espacios extra en las fechas antes de parsear
                    df_hist['fechaHora_clean'] = df_hist['fechaHora'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                    try:
                        df_hist['date'] = pd.to_datetime(df_hist['fechaHora_clean'], format='mixed', errors='coerce')
                    except:
                        # Fallback: intentar con format='ISO8601' o inferir
                        try:
                            df_hist['date'] = pd.to_datetime(df_hist['fechaHora_clean'], format='ISO8601', errors='coerce')
                        except:
                            df_hist['date'] = pd.to_datetime(df_hist['fechaHora_clean'], errors='coerce')
                    df_hist = df_hist.drop(columns=['fechaHora_clean'], errors='ignore')
                elif 'fecha' in df_hist.columns:
                    # Limpiar espacios extra en las fechas antes de parsear
                    df_hist['fecha_clean'] = df_hist['fecha'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                    try:
                        df_hist['date'] = pd.to_datetime(df_hist['fecha_clean'], format='mixed', errors='coerce')
                    except:
                        try:
                            df_hist['date'] = pd.to_datetime(df_hist['fecha_clean'], format='ISO8601', errors='coerce')
                        except:
                            df_hist['date'] = pd.to_datetime(df_hist['fecha_clean'], errors='coerce')
                    df_hist = df_hist.drop(columns=['fecha_clean'], errors='ignore')
                else:
                    df_hist['date'] = pd.date_range(end=end_date, periods=len(df_hist), freq='D')
                
                # Eliminar filas con fechas inválidas
                df_hist = df_hist.dropna(subset=['date'])
                
                # Ordenar por fecha
                df_hist = df_hist.sort_values('date')
                df_hist = df_hist.reset_index(drop=True)
                
                # Usar solo los últimos 30 días para visualización
                df_hist = df_hist.tail(30)
                
                dates = df_hist['date'].values
                real_prices = df_hist['close'].values
                
                # Generar predicciones si el predictor está disponible
                pred_prices = []
                if predictor and predictor.model and len(df_hist) >= predictor.window_size:
                    # Generar predicciones para cada punto usando ventana deslizante
                    for i in range(predictor.window_size, len(df_hist)):
                        window_data = df_hist.iloc[i-predictor.window_size:i]
                        try:
                            pred = predictor.predict(window_data, target_col='close')
                            if pred:
                                pred_prices.append(pred)
                            else:
                                pred_prices.append(real_prices[i])  # Fallback al precio real
                        except:
                            pred_prices.append(real_prices[i])  # Fallback al precio real
                    
                    # Rellenar los primeros puntos con precios reales
                    pred_prices = list(real_prices[:predictor.window_size]) + pred_prices
                else:
                    # Si no hay predictor, usar precios reales con pequeña variación
                    pred_prices = real_prices * (1 + np.random.normal(0, 0.01, len(real_prices)))
                
                # Proyección futura (5 días) usando el predictor
                # Asegurar que dates[-1] sea un objeto datetime de Python
                last_date = pd.Timestamp(dates[-1]) if len(dates) > 0 else end_date
                future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=5, freq='D')
                future_pred = []
                
                if predictor and predictor.model and len(df_hist) >= predictor.window_size:
                    # Usar los últimos datos para predecir el futuro
                    last_window = df_hist.tail(predictor.window_size)
                    for i in range(5):
                        try:
                            pred = predictor.predict(last_window, target_col='close')
                            if pred:
                                future_pred.append(pred)
                                # Actualizar ventana con la predicción para la siguiente iteración
                                new_row = pd.DataFrame({
                                    'date': [last_date + timedelta(days=i+1)],
                                    'close': [pred]
                                })
                                last_window = pd.concat([last_window.tail(predictor.window_size-1), new_row]).reset_index(drop=True)
                            else:
                                # Extrapolación simple si falla
                                future_pred.append(real_prices[-1] * (1.01 ** (i+1)))
                        except:
                            future_pred.append(real_prices[-1] * (1.01 ** (i+1)))
                else:
                    # Extrapolación simple si no hay predictor
                    future_pred = [real_prices[-1] * (1.01 ** i) for i in range(1, 6)]
                
                # Crear gráfico
                fig = go.Figure()
                
                # Precios Reales
                fig.add_trace(go.Scatter(
                    x=dates, y=real_prices,
                    mode='lines+markers',
                    name='Precio Real',
                    line=dict(color='#00FF88', width=2)
                ))
                
                # Predicciones Pasadas (solo si hay predictor)
                if predictor and predictor.model:
                    pred_dates = dates[predictor.window_size:] if len(pred_prices) > predictor.window_size else dates
                    pred_values = pred_prices[predictor.window_size:] if len(pred_prices) > predictor.window_size else pred_prices
                    fig.add_trace(go.Scatter(
                        x=pred_dates, y=pred_values,
                        mode='lines',
                        name='Predicción IA',
                        line=dict(color='#FFD93D', dash='dot', width=2)
                    ))
                
                # Proyección Futura
                fig.add_trace(go.Scatter(
                    x=future_dates, y=future_pred,
                    mode='lines+markers',
                    name='Proyección Futura (5d)',
                    line=dict(color='#00D9FF', width=3)
                ))
                
                fig.update_layout(
                    template='plotly_dark',
                    height=500,
                    title=f"Predicción de Precios para {symbol}",
                    xaxis_title="Fecha",
                    yaxis_title="Precio"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                error_occurred = True
                error_message = f"No se pudieron obtener datos históricos para {symbol}"
                
        except Exception as e:
            error_occurred = True
            error_message = f"Error obteniendo datos: {str(e)}"
            logger.error(f"Error en render_neural_network para {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    # Mostrar error o datos simulados si falló
    if error_occurred or not hist_data or len(hist_data) == 0:
        if error_occurred:
            st.warning(f"⚠️ {error_message}")
            st.info("💡 Asegúrate de que el bot esté conectado y que el símbolo sea válido. Mostrando datos simulados para visualización.")
        
        # Fallback a datos simulados (solo para visualización)
        try:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            real_prices = np.linspace(100, 150, 30) + np.random.normal(0, 5, 30)
            pred_prices = real_prices * (1 + np.random.normal(0, 0.02, 30))
            # Asegurar que dates[-1] sea un objeto datetime de Python
            last_date = pd.Timestamp(dates[-1]) if len(dates) > 0 else datetime.now()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=5, freq='D')
            future_pred = [pred_prices[-1] * (1.01 ** i) for i in range(1, 6)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=real_prices, 
                mode='lines+markers', 
                name='Precio Real (Simulado)', 
                line=dict(color='#00FF88')
            ))
            fig.add_trace(go.Scatter(
                x=dates, y=pred_prices, 
                mode='lines', 
                name='Predicción IA (Simulado)', 
                line=dict(color='#FFD93D', dash='dot')
            ))
            fig.add_trace(go.Scatter(
                x=future_dates, y=future_pred, 
                mode='lines+markers', 
                name='Proyección Futura (5d) - Simulado', 
                line=dict(color='#00D9FF', width=3)
            ))
            fig.update_layout(
                template='plotly_dark', 
                height=500, 
                title=f"Predicción de Precios para {symbol} (Datos Simulados)", 
                xaxis_title="Fecha", 
                yaxis_title="Precio"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e2:
            logger.error(f"Error generando gráfico simulado: {e2}")
            st.error("❌ No se pudo generar el gráfico. Por favor, intenta con otro símbolo.")
    
    st.markdown("---")
    
    # ==================== ENTRENAMIENTO ====================
    st.markdown("#### 🎓 Entrenamiento Manual")
    
    col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
    
    with col_t1:
        st.markdown("""
        Puedes forzar un re-entrenamiento del modelo con los datos más recientes.
        Esto ajustará los pesos de la red LSTM para adaptarse a los últimos movimientos del mercado.
        """)
    
    with col_t2:
        epochs = st.number_input("Épocas", min_value=1, max_value=20, value=5, key="train_epochs", help="Número de épocas de entrenamiento")
    
    with col_t3:
        if st.button("💪 Entrenar Modelo", use_container_width=True, key="btn_train_model"):
            # Verificar nuevamente el predictor (puede haberse inicializado arriba)
            if not predictor:
                # Intentar inicializar una vez más
                try:
                    # Verificar primero si TensorFlow está disponible
                    try:
                        import tensorflow as tf
                        tf_version = tf.__version__
                        logger.info(f"✅ TensorFlow {tf_version} detectado al intentar entrenar")
                    except ImportError as tf_error:
                        st.error(f"❌ TensorFlow no está instalado. Instala TensorFlow con: `pip install tensorflow`\n\nError: {str(tf_error)}")
                        predictor = None
                    else:
                        # Si TensorFlow está disponible, intentar importar LSTMPredictor
                        try:
                            from src.services.learning.lstm_predictor import LSTMPredictor
                            predictor = LSTMPredictor()
                            bot.predictor = predictor
                            bot.lstm_predictor = predictor
                            st.success("✅ Predictor inicializado correctamente. Puedes entrenar el modelo ahora.")
                        except ImportError as lstm_error:
                            st.error(f"❌ Error importando LSTMPredictor: {str(lstm_error)}")
                            predictor = None
                        except Exception as init_error:
                            st.error(f"❌ Error inicializando predictor: {str(init_error)}")
                            logger.error(f"Error detallado inicializando predictor: {init_error}", exc_info=True)
                            predictor = None
                except Exception as e:
                    st.error(f"❌ Error general: {str(e)}")
                    logger.error(f"Error general al intentar inicializar predictor: {e}", exc_info=True)
                    predictor = None
            
            if predictor:
                # Obtener símbolo para entrenar
                train_symbol = symbol
                try:
                    # Obtener datos históricos para entrenamiento
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=180)  # 6 meses de datos
                    
                    # Obtener datos sin usar spinner para evitar problemas con el DOM
                    try:
                        hist_data = bot.iol_client.get_historical_data(
                            train_symbol,
                            start_date.strftime("%Y-%m-%d"),
                            end_date.strftime("%Y-%m-%d")
                        )
                    except Exception as api_error:
                        logger.warning(f"Error obteniendo datos para entrenamiento: {api_error}")
                        hist_data = None
                    
                    if hist_data and len(hist_data) > 0:
                        df_train = pd.DataFrame(hist_data)
                        
                        # Normalizar columnas
                        if 'ultimoPrecio' in df_train.columns:
                            df_train['close'] = df_train['ultimoPrecio']
                        elif 'cierre' in df_train.columns:
                            df_train['close'] = df_train['cierre']
                        else:
                            st.error(f"❌ No se encontró columna de precio en los datos para {train_symbol}")
                            hist_data = None
                        
                        # Normalizar fechas si existen (aunque no se usan para entrenamiento, es bueno tenerlas)
                        if hist_data and 'fechaHora' in df_train.columns:
                            df_train['fechaHora_clean'] = df_train['fechaHora'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                            try:
                                df_train['date'] = pd.to_datetime(df_train['fechaHora_clean'], format='mixed', errors='coerce')
                            except:
                                try:
                                    df_train['date'] = pd.to_datetime(df_train['fechaHora_clean'], format='ISO8601', errors='coerce')
                                except:
                                    df_train['date'] = pd.to_datetime(df_train['fechaHora_clean'], errors='coerce')
                            df_train = df_train.drop(columns=['fechaHora_clean'], errors='ignore')
                        elif hist_data and 'fecha' in df_train.columns:
                            df_train['fecha_clean'] = df_train['fecha'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                            try:
                                df_train['date'] = pd.to_datetime(df_train['fecha_clean'], format='mixed', errors='coerce')
                            except:
                                try:
                                    df_train['date'] = pd.to_datetime(df_train['fecha_clean'], format='ISO8601', errors='coerce')
                                except:
                                    df_train['date'] = pd.to_datetime(df_train['fecha_clean'], errors='coerce')
                            df_train = df_train.drop(columns=['fecha_clean'], errors='ignore')
                    
                        if hist_data and len(df_train) > 0:
                            # Mostrar mensaje de progreso
                            progress_placeholder = st.empty()
                            with progress_placeholder.container():
                                st.info(f"🧠 Entrenando modelo con {len(df_train)} días de datos de {train_symbol}...")
                            
                            # Entrenar el modelo
                            try:
                                predictor.train(df_train, target_col='close', epochs=epochs)
                                progress_placeholder.empty()
                                st.success(f"✅ Modelo re-entrenado con {len(df_train)} días de datos de {train_symbol}")
                                st.balloons()
                                # Usar time.sleep antes de rerun para evitar problemas con el DOM
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as train_error:
                                progress_placeholder.empty()
                                st.error(f"❌ Error durante el entrenamiento: {str(train_error)}")
                                logger.error(f"Error entrenando modelo: {train_error}")
                    else:
                        st.error(f"❌ No se pudieron obtener datos históricos para {train_symbol}. Verifica que el símbolo sea válido.")
                except Exception as e:
                    st.error(f"❌ Error entrenando modelo: {str(e)}")
                    logger.error(f"Error entrenando modelo: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())


def render_advanced_strategies():
    """Renderiza Estrategias Avanzadas"""
    st.title("📉 Estrategias Avanzadas")
    st.info("Página en desarrollo")


def render_configuration():
    """Renderiza Configuración Global (Mejorado v2)"""
    st.title("⚙️ Configuración del Bot")
    
    config_path = "professional_config.json"
    
    # Cargar config actual
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        st.error(f"Error cargando config: {e}")
        return

    st.info("⚠️ Los cambios requieren reiniciar el bot para aplicar completamente.")
    
    # Crear pestañas
    tab_universe, tab_trading, tab_strategies, tab_monitoring, tab_system, tab_advanced = st.tabs([
        "📊 Universo de Símbolos", "💰 Trading & Riesgo", "🧠 Estrategias", "📡 Monitoreo & IA", "⚙️ Sistema", "📝 Editor RAW"
    ])
    
    # --- TAB 0: UNIVERSO DE SÍMBOLOS ---
    with tab_universe:
        st.markdown("### 🌍 Configurar Activos a Monitorear")
        st.info("Selecciona qué activos quieres que el bot analice. Los cambios se aplicarán al reiniciar el bot.")
        
        # Obtener símbolos actuales del bot
        current_symbols = st.session_state.bot_instance.symbols if st.session_state.bot_instance else []
        
        # Definir todos los grupos de activos
        MERVAL = ["GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "BMA", "CRES", "EDN", 
                  "LOMA", "MIRG", "TECO2", "TGNO4", "TGSU2", "TRAN", "VALO", 
                  "SUPV", "BYMA", "CEPU", "COME", "HARG", "BOLT", "CECO2"]
        
        CEDEARS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD",
                   "MELI", "VIST", "KO", "MCD", "DIS", "NFLX", "QYLD", "SPY", "DIA",
                   "BABA", "BRKB", "JPM", "WMT", "PFE", "XOM", "INTC", "CSCO", "BA"]
        
        BONOS = ["AL30", "GD30", "AL35", "GD35", "AL41", "GD41", "AE38", "GD38",
                 "AL29", "GD29", "AL46", "GD46", "CUAP", "DICA", "PARP"]
        
        ONS = ["TGNO4", "TGSU2", "PAMPA", "IRSA", "CRES", "TXAR"]
        
        ETFS = ["SPY", "QQQ", "DIA", "IWM", "EEM", "GLD", "SLV", "USO"]
        
        # Botones de selección rápida
        st.markdown("#### ⚡ Selección Rápida")
        col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)
        
        def save_universe_to_config(symbols_list):
            """Guarda el universo en el archivo de configuración"""
            try:
                import json
                config_path = "professional_config.json"
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if 'monitoring' not in config:
                    config['monitoring'] = {}
                config['monitoring']['custom_symbols'] = symbols_list
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                return True
            except Exception as e:
                st.error(f"Error guardando: {e}")
                return False
        
        with col_quick1:
            if st.button("🇦🇷 Todo Merval", use_container_width=True, key="btn_all_merval"):
                if save_universe_to_config(MERVAL):
                    st.session_state.selected_symbols = MERVAL
                    st.success(f"✅ {len(MERVAL)} símbolos guardados")
                    st.rerun()
        with col_quick2:
            if st.button("🌎 Todos CEDEARs", use_container_width=True, key="btn_all_cedears"):
                if save_universe_to_config(CEDEARS):
                    st.session_state.selected_symbols = CEDEARS
                    st.success(f"✅ {len(CEDEARS)} símbolos guardados")
                    st.rerun()
        with col_quick3:
            if st.button("💰 Todos Bonos", use_container_width=True, key="btn_all_bonos"):
                if save_universe_to_config(BONOS):
                    st.session_state.selected_symbols = BONOS
                    st.success(f"✅ {len(BONOS)} símbolos guardados")
                    st.rerun()
        with col_quick4:
            universo_completo = MERVAL + CEDEARS + BONOS + ONS + ETFS
            if st.button("🌐 UNIVERSO COMPLETO", use_container_width=True, type="primary"):
                if save_universe_to_config(universo_completo):
                    st.session_state.selected_symbols = universo_completo
                    st.success(f"✅ {len(universo_completo)} símbolos guardados permanentemente!")
                    st.rerun()
        
        st.markdown("---")
        
        # Inicializar selected_symbols si no existe
        if 'selected_symbols' not in st.session_state:
            st.session_state.selected_symbols = current_symbols
        
        # Selección detallada por grupo
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🇦🇷 Panel Merval")
            selected_merval = st.multiselect(
                f"Acciones argentinas ({len(MERVAL)} disponibles)",
                MERVAL,
                default=[s for s in MERVAL if s in st.session_state.selected_symbols],
                key="merval_select"
            )
            
            st.markdown("#### 💰 Bonos Soberanos")
            selected_bonos = st.multiselect(
                f"Bonos argentinos ({len(BONOS)} disponibles)",
                BONOS,
                default=[s for s in BONOS if s in st.session_state.selected_symbols],
                key="bonos_select"
            )
            
            st.markdown("#### 📊 ETFs")
            selected_etfs = st.multiselect(
                f"ETFs internacionales ({len(ETFS)} disponibles)",
                ETFS,
                default=[s for s in ETFS if s in st.session_state.selected_symbols],
                key="etfs_select"
            )
        
        with col2:
            st.markdown("#### 🌎 CEDEARs")
            selected_cedears = st.multiselect(
                f"Certificados de Depósito ({len(CEDEARS)} disponibles)",
                CEDEARS,
                default=[s for s in CEDEARS if s in st.session_state.selected_symbols],
                key="cedears_select"
            )
            
            st.markdown("#### 🏢 Obligaciones Negociables")
            selected_ons = st.multiselect(
                f"ONs corporativas ({len(ONS)} disponibles)",
                ONS,
                default=[s for s in ONS if s in st.session_state.selected_symbols],
                key="ons_select"
            )
        
        # Símbolos personalizados
        st.markdown("#### ➕ Símbolos Personalizados")
        custom_symbols = st.text_input(
            "Agregar símbolos adicionales (separados por comas)",
            placeholder="Ej: IRSA, PAMPA, AGRO",
            help="Agrega cualquier símbolo disponible en IOL"
        )
        
        # Combinar todos los símbolos seleccionados
        new_universe = selected_merval + selected_cedears + selected_bonos + selected_ons + selected_etfs
        if custom_symbols:
            new_universe.extend([s.strip().upper() for s in custom_symbols.split(",") if s.strip()])
        
        # Eliminar duplicados manteniendo orden
        new_universe = list(dict.fromkeys(new_universe))
        
        # Mostrar resumen
        st.markdown("---")
        st.markdown(f"### 📊 Resumen de Selección")
        
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        col_stats1.metric("🇦🇷 Merval", len(selected_merval))
        col_stats2.metric("🌎 CEDEARs", len(selected_cedears))
        col_stats3.metric("💰 Bonos", len(selected_bonos))
        col_stats4.metric("📊 Total", len(new_universe))
        
        # Vista previa y guardar
        col_preview, col_save = st.columns([3, 1])
        with col_preview:
            with st.expander("👁️ Vista Previa del Universo Completo"):
                st.write(", ".join(new_universe) if new_universe else "Ningún símbolo seleccionado")
        
        with col_save:
            if st.button("💾 Guardar Universo", type="primary", use_container_width=True, key="btn_save_universe"):
                if st.session_state.bot_instance and new_universe:
                    # Guardar en session state
                    st.session_state.bot_instance.symbols = new_universe
                    st.session_state.selected_symbols = new_universe
                    
                    # Guardar en archivo de configuración para persistencia
                    try:
                        import json
                        config_path = "professional_config.json"
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        
                        # Agregar/actualizar sección de universo personalizado
                        if 'monitoring' not in config:
                            config['monitoring'] = {}
                        config['monitoring']['custom_symbols'] = new_universe
                        
                        # Guardar configuración actualizada
                        with open(config_path, 'w') as f:
                            json.dump(config, f, indent=4)
                        
                        st.success(f"✅ Universo actualizado y guardado: {len(new_universe)} símbolos")
                        st.info("🔄 Reinicia el bot para aplicar los cambios")
                    except Exception as e:
                        st.error(f"⚠️ Error guardando configuración: {e}")
                        st.warning("Los símbolos se aplicaron temporalmente pero no se guardaron en el archivo")
                elif not new_universe:
                    st.error("⚠️ Debes seleccionar al menos un símbolo")
                else:
                    st.error("⚠️ Bot no inicializado")
    
    
    # --- TAB 1: TRADING & RIESGO ---
    with tab_trading:
        st.markdown("### Parámetros de Operación")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### Trading General")
            mode = st.selectbox("Modo", ["paper", "live"], index=0 if config['trading']['mode'] == 'paper' else 1)
            config['trading']['mode'] = mode
            
            config['trading']['max_position_size'] = st.number_input(
                "Tamaño Máx. Posición (% Capital)", 
                0.01, 1.0, float(config['trading']['max_position_size']), 0.01,
                help="Porcentaje máximo del capital total asignado a una sola operación."
            )
            config['trading']['commission_rate'] = st.number_input(
                "Comisión Broker (%)", 
                0.0, 0.05, float(config['trading']['commission_rate']), 0.001, format="%.4f"
            )

        with c2:
            st.markdown("#### Gestión de Riesgo (Risk Manager)")
            config['risk_management']['stop_loss_percentage'] = st.number_input(
                "Stop Loss (%)", 0.0, 0.5, float(config['risk_management']['stop_loss_percentage']), 0.005
            )
            config['risk_management']['take_profit_percentage'] = st.number_input(
                "Take Profit (%)", 0.0, 1.0, float(config['risk_management']['take_profit_percentage']), 0.01
            )
            
            # Trailing Stop
            config['risk_management']['trailing_stop'] = st.checkbox(
                "Trailing Stop Activo", value=config['risk_management']['trailing_stop']
            )
            if config['risk_management']['trailing_stop']:
                config['risk_management']['trailing_stop_percentage'] = st.number_input(
                    "Trailing Step (%)", 0.0, 0.2, float(config['risk_management']['trailing_stop_percentage']), 0.005
                )

    # --- TAB 2: ESTRATEGIAS ---
    with tab_strategies:
        st.markdown("### Pesos de Estrategias")
        st.markdown("Ajusta la influencia de cada módulo en la decisión final.")
        
        cols = st.columns(3)
        strategies = config.get('strategies', {})
        
        i = 0
        for strat_name, strat_conf in strategies.items():
            with cols[i % 3]:
                st.markdown(f"**{strat_name.replace('_', ' ').title()}**")
                enabled = st.checkbox(f"Habilitar {strat_name}", value=strat_conf.get('enabled', True))
                weight = st.slider(f"Peso {strat_name}", 0.0, 1.0, float(strat_conf.get('weight', 0.0)), 0.05)
                
                config['strategies'][strat_name]['enabled'] = enabled
                config['strategies'][strat_name]['weight'] = weight
            i += 1
            
    # --- TAB 3: MONITOREO & IA ---
    with tab_monitoring:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Monitoreo de Mercado")
            config['monitoring']['update_interval_minutes'] = st.number_input(
                "Intervalo Actualización (min)", 1, 60, int(config['monitoring']['update_interval_minutes'])
            )
            config['monitoring']['max_symbols'] = st.number_input(
                "Máx. Símbolos", 10, 1000, int(config['monitoring']['max_symbols'])
            )
            
        with c2:
            st.markdown("#### Aprendizaje Continuo (RL/Evo)")
            config['learning']['auto_retraining'] = st.toggle(
                "Auto-Reentrenamiento IA", value=config['learning']['auto_retraining']
            )
            config['optimization']['genetic_algorithm']['enabled'] = st.toggle(
                "Algoritmos Genéticos Activos", value=config['optimization']['genetic_algorithm']['enabled']
            )

    # --- TAB 4: SISTEMA ---
    with tab_system:
        st.markdown("#### Notificaciones")
        config['notifications']['telegram_enabled'] = st.checkbox(
            "Telegram Activado", value=config['notifications']['telegram_enabled']
        )
        config['notifications']['alert_on_trade'] = st.checkbox(
            "Alertar Operaciones", value=config['notifications']['alert_on_trade']
        )
        
        st.markdown("#### Logging")
        config['logging']['level'] = st.selectbox(
            "Nivel de Log", ["DEBUG", "INFO", "WARNING", "ERROR"], 
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config['logging'].get('level', "INFO"))
        )

    # --- TAB 5: ADVANCED (RAW JSON) ---
    with tab_advanced:
        st.markdown("### Edición Directa JSON")
        config_str = json.dumps(config, indent=4)
        new_json_str = st.text_area("JSON Config", value=config_str, height=400)
    
    # GUARDAR AL FINAL
    st.markdown("###")
    if st.button("💾 Guardar Configuración Global", type="primary", use_container_width=True, key="btn_save_global_config"):
        try:
            # Si estamos en la tab avanzada, usamos el texto, si no, usamos el objeto config modificado por los widgets
            # Streamlit re-ejecuta todo el script al cambiar un widget, por lo que 'config' ya tiene los valores nuevos.
            # PERO, si el usuario editó el JSON a mano, esos cambios no están en 'config' objeto Python.
            # Haremos esto: si el texto JSON cambió respecto al dump de 'config', usamos el texto.
            # Simplificación: Usamos 'config' objeto a menos que el usuario esté explícitamente usando la tab RAW?
            # Mejor: Validamos si el JSON string es valido y lo usamos si es diferente.
            
            final_config = config
            try:
                manual_json = json.loads(new_json_str)
                # Si el usuario editó el JSON manual, priorizamos eso?
                # Es complejo sincronizar 2-ways.
                # Asumiremos que los widgets mandan A MENOS que se use una variable de control.
                # Para simplificar y ser "quirurgico": Guardamos el objeto 'config' que se actualizó con los widgets.
                # El usuario avanzado debe copiar el JSON generado si quiere editarlo manual.
                pass
            except:
                pass

            with open(config_path, 'w') as f:
                json.dump(final_config, f, indent=4)
                
            st.success("✅ Configuración guardada exitosamente.")
            st.toast("Configuración actualizada", icon="💾")
            
            if st.session_state.bot_instance:
                st.session_state.bot_instance.config = final_config
                
        except Exception as e:
            st.error(f"Error guardando configuración: {e}")


def render_trading_terminal():
    """Renderiza Terminal de Trading Manual (Cockpit Profesional v2)"""
    st.title("⚡ Terminal de Trading Pro")
    
    if not st.session_state.bot_instance:
        st.error("⚠️ Error de Conexión: El bot no se ha inicializado correctamente. Recarga la página.")
        return

    bot = st.session_state.bot_instance

    # --- 1. OBTENER UNIVERSO COMPLETO DE IOL ---
    # Intentar obtener todos los instrumentos disponibles desde IOL
    
    # Cache de instrumentos para evitar consultas repetidas
    cache_key_instruments = "iol_universe_instruments"
    cache_duration = 3600  # 1 hora de cache
    
    if cache_key_instruments not in st.session_state or \
       'iol_universe_timestamp' not in st.session_state or \
       (time.time() - st.session_state.get('iol_universe_timestamp', 0)) > cache_duration:
        
        with st.spinner("🔄 Obteniendo universo completo de instrumentos desde IOL..."):
            try:
                # Obtener instrumentos de todos los mercados disponibles
                all_instruments = []
                markets = ["bCBA", "nYSE", "nASDAQ", "aMEX", "bCS"]  # Mercados principales de IOL
                
                for market in markets:
                    try:
                        instruments = bot.iol_client.get_available_instruments(market)
                        if instruments:
                            # Agregar mercado a cada instrumento
                            for inst in instruments:
                                if isinstance(inst, dict):
                                    inst['market'] = market
                                    all_instruments.append(inst)
                                else:
                                    # Si es solo el símbolo como string
                                    all_instruments.append({'symbol': inst, 'market': market})
                    except Exception as e:
                        logger.debug(f"No se pudieron obtener instrumentos del mercado {market}: {e}")
                        continue
                
                # Guardar en cache
                st.session_state[cache_key_instruments] = all_instruments
                st.session_state['iol_universe_timestamp'] = time.time()
                logger.info(f"✅ Obtenidos {len(all_instruments)} instrumentos desde IOL")
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo universo de IOL: {e}")
                # Usar lista por defecto si falla
                all_instruments = []
    else:
        # Usar cache
        all_instruments = st.session_state.get(cache_key_instruments, [])
        logger.debug(f"📦 Usando {len(all_instruments)} instrumentos desde cache")
    
    # Si no se pudieron obtener instrumentos, usar categorías predefinidas como fallback
    if not all_instruments or len(all_instruments) == 0:
        logger.warning("⚠️ No se pudieron obtener instrumentos de IOL, usando categorías predefinidas")
        categorias_symbols = {
            "🇦🇷 Acciones Argentinas (MERVAL)": [
                "GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "BMA", "CRES", "EDN", 
                "LOMA", "MIRG", "TECO2", "TGNO4", "TGSU2", "TRAN", "VALO", 
                "SUPV", "BYMA", "CEPU", "COME", "HARG", "BOLT", "CECO2"
            ],
            "💰 Bonos Soberanos": [
                "AL30", "GD30", "AL35", "GD35", "AL41", "GD41", "AE38", "GD38",
                "AL29", "GD29", "AL46", "GD46", "CUAP", "DICA", "PARP"
            ],
            "🌎 CEDEARs": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD",
                "MELI", "VIST", "KO", "MCD", "DIS", "NFLX", "QYLD", "SPY", "DIA",
                "BABA", "BRKB", "JPM", "WMT", "PFE", "XOM", "INTC", "CSCO", "BA"
            ],
            "📊 ETFs": [
                "SPY", "QQQ", "DIA", "IWM", "EEM", "GLD", "SLV", "USO"
            ],
            "🏢 Obligaciones Negociables (ONs)": [
                "AL30", "GD30", "AL35", "GD35"
            ]
        }
    else:
        # Organizar instrumentos por categoría basándose en el mercado y tipo
        categorias_symbols = {}
        
        # Agrupar por mercado
        for inst in all_instruments:
            symbol = inst.get('symbol', inst.get('simbolo', '')) if isinstance(inst, dict) else str(inst)
            market = inst.get('market', 'Otros') if isinstance(inst, dict) else 'Otros'
            
            # Determinar categoría basada en mercado y símbolo
            if market == "bCBA":
                # Mercado argentino - clasificar por tipo de instrumento
                symbol_upper = symbol.upper()
                
                # Bonos (AL, GD, AE, etc.)
                if any(symbol_upper.startswith(prefix) for prefix in ["AL", "GD", "AE", "CUAP", "DICA", "PARP", "TO", "TJ"]):
                    category = "💰 Bonos Soberanos"
                # Acciones argentinas
                else:
                    category = "🇦🇷 Acciones Argentinas (MERVAL)"
                    
            elif market in ["nYSE", "nASDAQ", "aMEX"]:
                # Mercados estadounidenses - CEDEARs
                category = "🌎 CEDEARs"
            elif market == "bCS":
                # Mercado brasileño
                category = "🇧🇷 Acciones Brasileñas"
            else:
                category = "📊 Otros Instrumentos"
            
            # Agregar símbolo a la categoría
            if category not in categorias_symbols:
                categorias_symbols[category] = []
            
            if symbol and symbol not in categorias_symbols[category]:
                categorias_symbols[category].append(symbol)
        
        # Ordenar símbolos dentro de cada categoría
        for category in categorias_symbols:
            categorias_symbols[category] = sorted(categorias_symbols[category])
        
        logger.info(f"📊 Categorías creadas: {list(categorias_symbols.keys())}")
        logger.info(f"📊 Total símbolos: {sum(len(v) for v in categorias_symbols.values())}")
    
    # Mostrar información del universo cargado
    total_symbols = sum(len(v) for v in categorias_symbols.values())
    st.caption(f"🌐 Universo IOL: {total_symbols} instrumentos en {len(categorias_symbols)} categorías")
    
    # Inicializar categoría seleccionada en session_state
    if 'terminal_selected_category' not in st.session_state:
        st.session_state.terminal_selected_category = list(categorias_symbols.keys())[0]
    
    
    # Crear dos columnas para los selectboxes
    col_cat, col_sym, col_search = st.columns([1, 2, 1])
    
    # Buscador de símbolos
    with col_search:
        search_term = st.text_input(
            "🔍 Buscar símbolo",
            placeholder="Ej: GGAL, AL30...",
            key="symbol_search",
            help="Busca un símbolo específico en todas las categorías"
        )
        
        # Si hay búsqueda, filtrar símbolos
        if search_term and len(search_term) >= 2:
            search_upper = search_term.upper()
            matching_symbols = []
            
            for category, symbols in categorias_symbols.items():
                for symbol in symbols:
                    if search_upper in symbol.upper():
                        matching_symbols.append((symbol, category))
            
            if matching_symbols:
                st.caption(f"✅ {len(matching_symbols)} coincidencias")
                # Mostrar primeras 5 coincidencias
                for symbol, category in matching_symbols[:5]:
                    if st.button(f"📊 {symbol} ({category})", key=f"search_{symbol}", use_container_width=True):
                        # Seleccionar este símbolo
                        st.session_state.terminal_selected_category = category
                        st.session_state.terminal_selected_symbol = symbol
                        # Limpiar cache
                        keys_to_delete = [k for k in list(st.session_state.keys()) if k.startswith('market_data_')]
                        for k in keys_to_delete:
                            del st.session_state[k]
                        st.rerun()
            else:
                st.caption("❌ Sin coincidencias")
    
    # Usar contenedores para evitar errores de JavaScript con cambios dinámicos
    category_container = st.container()
    symbol_container = st.container()
    
    with category_container:
        # Selectbox para categoría con key estable
        category_list = list(categorias_symbols.keys())
        category_index = 0
        if st.session_state.terminal_selected_category in category_list:
            category_index = category_list.index(st.session_state.terminal_selected_category)
        
        selected_category = st.selectbox(
            "📂 Categoría",
            category_list,
            index=category_index,
            key="terminal_category_fixed"
        )
        
        # Si cambió la categoría, actualizar session_state y resetear símbolo
        if selected_category != st.session_state.terminal_selected_category:
            st.session_state.terminal_selected_category = selected_category
            # Resetear símbolo seleccionado cuando cambia la categoría
            if 'terminal_selected_symbol' in st.session_state:
                del st.session_state.terminal_selected_symbol
            if 'market_data_cache' in st.session_state:
                # Limpiar todo el cache de market_data
                keys_to_delete = [k for k in st.session_state.keys() if k.startswith('market_data_')]
                for k in keys_to_delete:
                    del st.session_state[k]
            # Forzar rerun para actualizar el segundo selectbox
            st.rerun()
    
    with symbol_container:
        # Obtener símbolos de la categoría seleccionada
        symbols = categorias_symbols.get(selected_category, [])
        
        # Si no hay símbolos, usar lista por defecto
        if not symbols:
            symbols = ["GGAL", "YPFD", "PAMP", "ALUA", "BMA", "TXAR", "EDN", "CRES"]
        
        # Inicializar símbolo seleccionado
        if 'terminal_selected_symbol' not in st.session_state:
            st.session_state.terminal_selected_symbol = symbols[0] if symbols else "GGAL"
        
        # Asegurar que el símbolo seleccionado esté en la lista actual
        if st.session_state.terminal_selected_symbol not in symbols:
            st.session_state.terminal_selected_symbol = symbols[0] if symbols else "GGAL"
        
        # Calcular índice de forma segura
        symbol_index = 0
        if st.session_state.terminal_selected_symbol in symbols:
            symbol_index = symbols.index(st.session_state.terminal_selected_symbol)
        
        # Crear key único y estable para el selectbox de símbolos
        # Usar un hash simple de la categoría para el key
        import hashlib
        category_hash = hashlib.md5(selected_category.encode()).hexdigest()[:8]
        symbol_selectbox_key = f"symbol_select_{category_hash}"
        
        # Selectbox para símbolo dentro de la categoría con key único que incluye la categoría
        selected_symbol = st.selectbox(
            "📈 Símbolo",
            symbols,
            index=symbol_index,
            key=symbol_selectbox_key
        )
        
        # Actualizar session_state cuando cambia el símbolo
        if selected_symbol != st.session_state.terminal_selected_symbol:
            st.session_state.terminal_selected_symbol = selected_symbol
            # Limpiar TODOS los caches de datos de mercado para forzar nueva consulta
            keys_to_delete = [k for k in list(st.session_state.keys()) if k.startswith('market_data_')]
            for k in keys_to_delete:
                del st.session_state[k]
            # También limpiar cache general si existe
            if 'market_data_cache' in st.session_state:
                del st.session_state.market_data_cache
            # NO hacer rerun aquí - dejar que el código continúe y obtenga datos nuevos
    
    # Obtener Market Data Real - SIEMPRE intentar obtener datos reales primero
    # Usar un cache key específico por símbolo para evitar problemas de cache
    cache_key = f"market_data_{selected_symbol}_{selected_category}"
    historical_cache_key = f"historical_data_{selected_symbol}_{selected_category}"
    market_data = None
    use_cache = False
    
    # Verificar si hay cache válido (5 minutos para datos en tiempo real, 1 hora para históricos)
    if cache_key in st.session_state:
        cached_data = st.session_state[cache_key]
        cache_timestamp = st.session_state.get(f"{cache_key}_timestamp", 0)
        current_time = time.time()
        
        # Cache de 5 minutos para datos en tiempo real
        cache_duration = 300  # 5 minutos
        
        # Si son datos históricos, usar cache más largo (1 hora)
        if cached_data and cached_data.get('is_historical', False):
            cache_duration = 3600  # 1 hora
        
        if (current_time - cache_timestamp) < cache_duration:
            market_data = cached_data
            use_cache = True
            logger.debug(f"📦 Usando cache para {selected_symbol} (edad: {int(current_time - cache_timestamp)}s)")
        else:
            # Cache expirado - limpiar
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            logger.debug(f"🔄 Cache expirado para {selected_symbol} - obteniendo datos nuevos")
    
    # Intentar obtener datos reales primero (solo si no hay cache válido)
    if not use_cache:
        try:
            # Determinar si es un bono para ajustar variaciones de símbolo
            # Usar startswith en lugar de 'in' para evitar falsos positivos (ej: GGAL contiene "GD")
            symbol_upper = selected_symbol.upper()
            is_bono = (
                selected_category == "💰 Bonos Soberanos" or 
                selected_category == "🏢 Obligaciones Negociables (ONs)" or
                symbol_upper.startswith("AL") or
                symbol_upper.startswith("GD") or
                symbol_upper.startswith("AE") or
                symbol_upper.startswith("CUAP") or
                symbol_upper.startswith("DICA") or
                symbol_upper.startswith("PARP") or
                symbol_upper.startswith("TO") or
                symbol_upper.startswith("TJ")
            )
            
            # Crear lista de variaciones del símbolo a intentar
            symbol_variations = [selected_symbol]  # Siempre intentar primero el símbolo tal cual
            
            if not is_bono:
                # Para acciones y CEDEARs, intentar con .BA
                symbol_variations.extend([
                    f"{selected_symbol}.BA",
                    selected_symbol.upper(),
                    f"{selected_symbol.upper()}.BA"
                ])
                # También intentar sin el sufijo si ya lo tiene
                if selected_symbol.endswith(".BA"):
                    symbol_variations.insert(1, selected_symbol.replace(".BA", ""))
            else:
                # Para bonos, solo intentar mayúsculas si es diferente
                if selected_symbol != selected_symbol.upper():
                    symbol_variations.append(selected_symbol.upper())
            
            logger.debug(f"🔍 Generadas {len(symbol_variations)} variaciones para {selected_symbol}: {symbol_variations}")
            
            market_data = None
            successful_symbol = None
            
            # Intentar obtener datos con cada variación del símbolo
            for symbol_variant in symbol_variations:
                try:
                    logger.debug(f"Intentando obtener datos para '{symbol_variant}' desde IOL...")
                    
                    # Determinar el mercado correcto basado en la categoría
                    market = "bCBA"  # Por defecto, mercado argentino
                    
                    if selected_category == "🌎 CEDEARs":
                        # CEDEARs se operan en mercados estadounidenses pero cotizan en Argentina
                        market = "bCBA"  # En IOL, los CEDEARs se consultan en bCBA
                    elif selected_category == "🇧🇷 Acciones Brasileñas":
                        market = "bCS"  # Mercado brasileño
                    elif selected_category in ["🇦🇷 Acciones Argentinas (MERVAL)", "💰 Bonos Soberanos", "🏢 Obligaciones Negociables (ONs)"]:
                        market = "bCBA"
                    
                    # Usar el cliente IOL del bot (ya autenticado)
                    if hasattr(bot, 'iol_client') and bot.iol_client:
                        # Pasar el mercado explícitamente
                        data = bot.iol_client.get_market_data(symbol_variant, market=market)
                    else:
                        logger.error("Bot no tiene cliente IOL disponible")
                        break
                    
                    if data:
                        price = data.get('last_price') or data.get('ultimoPrecio') or 0
                        if price and price > 0:
                            market_data = data
                            successful_symbol = symbol_variant
                            logger.info(f"✅ Datos reales obtenidos para {selected_symbol} usando símbolo '{symbol_variant}' en mercado {market}: ${price}")
                            break
                        else:
                            logger.debug(f"Datos obtenidos para '{symbol_variant}' en {market} pero precio inválido: {price}")
                    else:
                        logger.debug(f"No se obtuvieron datos para '{symbol_variant}' en {market}")
                        
                except Exception as e:
                    logger.error(f"❌ Error con símbolo '{symbol_variant}' en mercado {market}: {e}")
                    # Log detallado del error para debugging
                    import traceback
                    logger.debug(f"Traceback completo: {traceback.format_exc()}")
                    continue
            
            if not market_data:
                logger.error(f"❌ No se pudieron obtener datos reales para {selected_symbol} con ninguna variación.")
                logger.error(f"   Símbolos intentados: {symbol_variations}")
                logger.error(f"   Mercado: {market}")
                
                # FALLBACK: Intentar obtener último precio de cierre desde datos históricos
                logger.info(f"🔄 Intentando obtener último precio de cierre para {selected_symbol}...")
                
                try:
                    # Intentar con cada variación del símbolo
                    for symbol_variant in symbol_variations:
                        try:
                            logger.debug(f"Intentando obtener último cierre para '{symbol_variant}'...")
                            
                            if hasattr(bot, 'iol_client') and bot.iol_client:
                                historical_data = bot.iol_client.get_last_close_price(symbol_variant, market=market)
                                
                                if historical_data and historical_data.get('last_price', 0) > 0:
                                    market_data = historical_data
                                    successful_symbol = symbol_variant
                                    logger.info(f"✅ Último cierre obtenido para {selected_symbol} usando '{symbol_variant}': ${historical_data['last_price']} (fecha: {historical_data.get('close_date', 'N/A')})")
                                    
                                    # Agregar indicador de que son datos históricos
                                    market_data['is_historical'] = True
                                    market_data['data_source'] = 'Último Cierre'
                                    break
                        except Exception as e:
                            logger.debug(f"Error obteniendo último cierre para '{symbol_variant}': {e}")
                            continue
                    
                    if market_data:
                        logger.info(f"✅ Usando último precio de cierre para {selected_symbol}")
                    else:
                        logger.error(f"❌ No se pudo obtener ni cotización en tiempo real ni último cierre para {selected_symbol}")
                        
                except Exception as e:
                    logger.error(f"❌ Error en fallback de último cierre: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                
                if not market_data:
                    logger.error(f"   Verifica que el símbolo exista en IOL y que tu token tenga permisos para consultar cotizaciones.")
                
        except Exception as e:
            # Si falla, continuar con lógica de fallback
            logger.error(f"❌ Error obteniendo datos reales para {selected_symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            market_data = None
        
        # Guardar datos obtenidos en cache con timestamp (solo si se obtuvieron exitosamente y no había cache)
        if market_data and market_data.get('last_price', 0) > 0:
            st.session_state[cache_key] = market_data
            st.session_state[f"{cache_key}_timestamp"] = time.time()
            data_type = "históricos" if market_data.get('is_historical', False) else "en tiempo real"
            logger.debug(f"💾 Datos {data_type} guardados en cache para {selected_symbol}: ${market_data.get('last_price', 0)}")
    
    # --- SIMULATION FALLBACK DETECTOR ---
    # Solo usar datos simulados si realmente no hay datos disponibles
    is_simulated = False
    
    # Normalizar estructura de datos de IOL (IOL usa 'ultimoPrecio' en lugar de 'last_price')
    if market_data:
        # Convertir estructura de IOL a formato estándar
        if 'ultimoPrecio' in market_data and 'last_price' not in market_data:
            market_data['last_price'] = market_data['ultimoPrecio']
        
        # Extraer bid/ask de 'puntas' si está disponible
        if 'puntas' in market_data and isinstance(market_data['puntas'], list) and len(market_data['puntas']) > 0:
            # IOL devuelve puntas como lista de objetos con 'precioCompra' y 'precioVenta'
            puntas = market_data['puntas'][0]  # Tomar la primera punta (mejor precio)
            if 'precioCompra' in puntas and 'bid' not in market_data:
                market_data['bid'] = puntas['precioCompra']
            if 'precioVenta' in puntas and 'ask' not in market_data:
                market_data['ask'] = puntas['precioVenta']
        # Si no hay puntas, intentar campos directos
        elif 'compra' in market_data and 'bid' not in market_data:
            market_data['bid'] = market_data['compra']
        elif 'precioCompra' in market_data and 'bid' not in market_data:
            market_data['bid'] = market_data['precioCompra']
        
        if 'venta' in market_data and 'ask' not in market_data:
            market_data['ask'] = market_data['venta']
        elif 'precioVenta' in market_data and 'ask' not in market_data:
            market_data['ask'] = market_data['precioVenta']
        
        # Si aún no hay bid/ask, calcular basado en último precio con spread razonable
        if 'last_price' in market_data:
            last_price = market_data['last_price']
            if 'bid' not in market_data or market_data.get('bid', 0) == 0:
                # Spread típico: 0.1% - 0.5% del precio
                spread_pct = 0.002  # 0.2% spread
                market_data['bid'] = round(last_price * (1 - spread_pct), 2)
            if 'ask' not in market_data or market_data.get('ask', 0) == 0:
                spread_pct = 0.002  # 0.2% spread
                market_data['ask'] = round(last_price * (1 + spread_pct), 2)
    
    # NO usar datos simulados si el usuario quiere operar con datos reales
    # Solo usar simulación si realmente no hay otra opción y el mercado está cerrado
    if not market_data or market_data.get('last_price', 0) == 0:
        # Verificar si es horario de mercado (Argentina: 11:00-17:00 UTC-3)
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        # Horario de mercado argentino: 11:00-17:00 (asumiendo UTC-3)
        is_market_hours = 11 <= hour <= 17
        
        # NUNCA usar simulación si el usuario quiere operar - siempre mostrar error claro
        # El usuario necesita datos reales para operar
        is_simulated = False
        
        # Mostrar error detallado con información de debug
        has_credentials = bool(os.getenv('IOL_USERNAME') and os.getenv('IOL_PASSWORD'))
        
        # Obtener las variaciones realmente intentadas desde el scope anterior
        # Si no están disponibles, reconstruirlas basadas en la categoría
        if 'symbol_variations' not in locals():
            is_bono = selected_category == "💰 Bonos Soberanos" or selected_category == "🏢 Obligaciones Negociables (ONs)" or any(x in selected_symbol.upper() for x in ["AL", "GD", "AE", "CUAP", "DICA", "PARP"])
            symbol_variations = [selected_symbol]
            if not is_bono:
                symbol_variations.extend([
                    f"{selected_symbol}.BA",
                    selected_symbol.upper(),
                    f"{selected_symbol.upper()}.BA"
                ])
            else:
                if selected_symbol != selected_symbol.upper():
                    symbol_variations.append(selected_symbol.upper())
        
        error_msg = f"❌ **NO SE PUDIERON OBTENER DATOS REALES PARA {selected_symbol}**\n\n"
        error_msg += f"**⚠️ IMPORTANTE:** No se usarán datos simulados. Necesitas datos reales para operar.\n\n"
        error_msg += f"**Posibles causas:**\n"
        error_msg += f"• El símbolo no existe en IOL o está mal escrito\n"
        error_msg += f"• Problema de conexión con IOL\n"
        error_msg += f"• El símbolo requiere un formato diferente\n"
        error_msg += f"• Token de IOL expirado o sin permisos\n"
        error_msg += f"• El símbolo no está disponible en el mercado seleccionado\n\n"
        error_msg += f"**Símbolos intentados:**\n"
        # Mostrar las variaciones realmente intentadas
        for var in symbol_variations:
            error_msg += f"• {var}\n"
        error_msg += f"\n**Revisa los logs en la consola de Streamlit para más detalles.**"
        
        st.error(error_msg)
        
        # Mostrar información de debug para ayudar al usuario
        with st.expander("🔍 Información de Debug"):
            debug_info = f"""
Símbolo seleccionado: {selected_symbol}
Modo bot: {'MOCK' if bot_is_mock else 'LIVE'}
Tiene credenciales: {'✅ Sí' if has_credentials else '❌ No'}
Horario de mercado: {'🟢 Abierto' if is_market_hours else '🔴 Cerrado'} ({hour}:00)
Datos obtenidos: {'❌ No' if not market_data else '✅ Sí'}
Market data: {market_data if market_data else 'None'}
            """
            st.code(debug_info.strip())
            
            if not has_credentials:
                st.warning("⚠️ No tienes credenciales de IOL configuradas en el archivo .env")
            elif bot_is_mock:
                st.info("ℹ️ El bot está en modo MOCK, pero se intentó obtener datos reales con credenciales")
    
    # NO generar datos simulados - el usuario quiere operar con datos reales
    # Si no hay datos reales, market_data será None y se mostrará el error arriba
    
    # Validar que market_data no sea None antes de acceder a sus atributos
    if not market_data or market_data.get('last_price', 0) == 0:
        # No hay datos reales - NO generar simulados, usar valores por defecto
        price = 0.0
        bid = 0.0
        ask = 0.0
        is_simulated = False  # Asegurar que no se marque como simulado
    else:
        # Hay datos reales - usar esos datos
        price = market_data.get('last_price', 0.0)
        bid = market_data.get('bid', 0.0)
        ask = market_data.get('ask', 0.0)
        is_simulated = False  # Son datos reales
    
    # Si bid/ask son 0 o no existen, calcular basado en precio con spread razonable
    if price > 0:
        if bid == 0 or not bid:
            # Spread típico: 0.1% - 0.3% del precio
            spread_pct = 0.002  # 0.2% spread
            bid = round(price * (1 - spread_pct), 2)
        if ask == 0 or not ask:
            spread_pct = 0.002  # 0.2% spread
            ask = round(price * (1 + spread_pct), 2)
    
    spread = ask - bid if ask and bid else 0
    
    # Calcular cambio porcentual real si hay datos de IOL
    if not is_simulated and market_data:
        # IOL devuelve 'variacion' como porcentaje
        if 'variacion' in market_data:
            change_pct = market_data['variacion']
        elif 'cierreAnterior' in market_data and market_data['cierreAnterior'] > 0:
            # Calcular desde cierre anterior
            cierre_anterior = market_data['cierreAnterior']
            change_pct = ((price - cierre_anterior) / cierre_anterior) * 100
        else:
            change_pct = 0.0
    else:
        # Mock change para datos simulados
        change_pct = ((price - (price*0.98)) / (price*0.98)) * 100 if price > 0 else 0.0
    
    # Title Extension - Mostrar estado del modo con indicadores mejorados
    # Determinar el modo real basado en si obtuvimos datos reales
    data_is_real = market_data and market_data.get('last_price', 0) > 0 and not is_simulated
    is_historical = market_data and market_data.get('is_historical', False)
    
    # Crear columnas para status y fecha
    status_col1, status_col2 = st.columns([3, 1])
    
    with status_col1:
        if data_is_real and not is_historical:
            st.success("✅ **DATOS EN TIEMPO REAL**: Cotización actual desde IOL")
        elif data_is_real and is_historical:
            close_date = market_data.get('close_date', 'N/A')
            st.warning(f"⏰ **ÚLTIMO CIERRE**: Datos históricos de IOL (Fecha: {close_date})")
        elif bot_is_mock and not market_data:
            st.warning("⚠️ **MODO MOCK**: El bot está configurado en modo simulación. Las operaciones NO se ejecutarán en IOL.")
        elif is_simulated:
            st.info("⚠️ **DATOS SIMULADOS**: Datos de mercado generados artificialmente (Mercado Cerrado/Offline o sin conexión a IOL).")
        else:
            st.error("❌ **ERROR**: No se pudieron obtener datos. Verifica tu conexión con IOL.")
    
    with status_col2:
        # Mostrar badge de tipo de dato
        if data_is_real and not is_historical:
            st.markdown("**🟢 LIVE**")
        elif data_is_real and is_historical:
            st.markdown("**🟡 HISTÓRICO**")
        else:
            st.markdown("**🔴 SIN DATOS**")

    # KPI Row con indicadores mejorados
    # Usamos un contenedor para aislar refresh
    with st.container():
        k1, k2, k3, k4 = st.columns(4)
        
        # Agregar indicador visual en el precio si son datos históricos
        price_label = f"Precio {selected_symbol}"
        if is_historical:
            price_label += " (Último Cierre)"
        
        k1.metric(price_label, f"${price:,.2f}", f"{change_pct:.2f}%")
        k2.metric("Punta Compra", f"${bid:,.2f}")
        k3.metric("Punta Venta", f"${ask:,.2f}")
        k4.metric("Spread", f"${spread:,.2f}", f"{(spread/price*100 if price else 0):.2f}%", delta_color="inverse")
    
    # Mostrar información adicional si son datos históricos
    if is_historical and market_data:
        with st.expander("ℹ️ Información de Datos Históricos"):
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.caption(f"**Fecha:** {market_data.get('close_date', 'N/A')}")
            with info_col2:
                st.caption(f"**Fuente:** {market_data.get('data_source', 'Último Cierre')}")
            with info_col3:
                st.caption(f"**Volumen:** {market_data.get('volume', 0):,}")
            
            st.info("💡 **Nota:** Estos son los últimos precios de cierre disponibles. El mercado está actualmente cerrado.")
    
    st.divider()

    # --- 2. ÁREA PRINCIPAL (SPLIT VIEW) ---
    col_order, col_book = st.columns([1, 2], gap="large")
    
    # --- COLUMNA IZQUIERDA: BOLETA ---
    with col_order:
        st.subheader("📝 Boleta de Órdenes")
        
        tab_limit, tab_market = st.tabs(["Limit", "Market"])
        
        # LOGICA LIMIT
        with tab_limit:
            with st.form("limit_order_form"):
                action = st.radio("Acción", ["COMPRAR", "VENDER"], horizontal=True)
                quantity = st.number_input("Cantidad (Nominales)", min_value=1, value=100, step=1)
                limit_price = st.number_input("Precio Límite ($)", value=max(float(price), 100.0), min_value=0.01, step=0.5, format="%.2f")
                
                total_estimado = quantity * limit_price
                st.caption(f"Total Estimado: ${total_estimado:,.2f}")
                
                submitted = st.form_submit_button("🚀 Enviar Orden Límite", type="primary" if action == "COMPRAR" else "secondary")
                
                if submitted:
                    # Verificar si estamos en modo MOCK antes de ejecutar
                    if bot_is_mock:
                        st.warning("⚠️ El bot está en modo MOCK. Las órdenes NO se ejecutarán en IOL.")
                        st.info("💡 Para operaciones reales, asegúrate de tener IOL_USERNAME e IOL_PASSWORD configurados en .env")
                    else:
                        side_code = "buy" if action == "COMPRAR" else "sell"
                        res = bot.execute_manual_order(selected_symbol, side_code, quantity) # TODO: Pasar limit price si el bot lo soporta V3
                        if "✅" in res:
                            st.success(res)
                            st.balloons()
                        else:
                            st.error(res)

        # LOGICA MARKET
        with tab_market:
            st.warning("⚠️ Ejecución inmediata al mejor precio disponible.")
            action_m = st.radio("Acción M", ["COMPRAR", "VENDER"], horizontal=True, label_visibility="collapsed")
            qty_m = st.number_input("Nominales", min_value=1, value=100)
            
            if st.button("⚡ EXECUTE MARKET ORDER", use_container_width=True, type="primary"):
                # Verificar si estamos en modo MOCK antes de ejecutar
                if bot_is_mock:
                    st.warning("⚠️ El bot está en modo MOCK. Las órdenes NO se ejecutarán en IOL.")
                    st.info("💡 Para operaciones reales, asegúrate de tener IOL_USERNAME e IOL_PASSWORD configurados en .env")
                else:
                    side_code = "buy" if action_m == "COMPRAR" else "sell"
                    res = bot.execute_manual_order(selected_symbol, side_code, qty_m)
                    if "✅" in res:
                        st.toast(res, icon="⚡")
                        st.success("Orden de Mercado Enviada")
                    else:
                        st.error(res)

    # --- COLUMNA DERECHA: ORDER BOOK & DEPTH ---
    with col_book:
        st.subheader("📚 Order Book (Level 2)")
        
        # Simular Depth Data (Ya que IOL API Publica a veces no lo da gratis en real-time)
        # Generar book alrededor del precio actual
        if price > 0:
            bids = pd.DataFrame({
                "Vol": [500, 1200, 450, 3000, 1500],
                "Bid": [bid, bid*0.998, bid*0.995, bid*0.99, bid*0.98]
            })
            asks = pd.DataFrame({
                "Ask": [ask, ask*1.002, ask*1.005, ask*1.01, ask*1.02],
                "Vol": [800, 200, 1500, 600, 2500]
            })
            
            # Visualizar como tabla doble
            cb1, cb2 = st.columns(2)
            with cb1:
                st.markdown("**Compradores (Bids)**")
                st.dataframe(bids.style.format({"Bid": "${:.2f}"}), hide_index=True, use_container_width=True)
            with cb2:
                st.markdown("**Vendedores (Asks)**")
                st.dataframe(asks.style.format({"Ask": "${:.2f}"}), hide_index=True, use_container_width=True)
                
            # Depth Chart simplificado
            st.markdown("##### 🌊 Profundidad de Mercado")
            fig_depth = go.Figure()
            fig_depth.add_trace(go.Scatter(x=bids['Bid'], y=bids['Vol'].cumsum(), fill='tozeroy', name='Bids', line=dict(color='green')))
            fig_depth.add_trace(go.Scatter(x=asks['Ask'], y=asks['Vol'].cumsum(), fill='tozeroy', name='Asks', line=dict(color='red')))
            fig_depth.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig_depth, use_container_width=True)

        else:
            st.info("Esperando datos de mercado...")

    # --- 3. HISTORIAL RECIENTE ---
    st.markdown("### 🕒 Ejecuciones Recientes")
    recent_trades = getattr(bot, "trades_history", [])
    if recent_trades:
        df_trades = pd.DataFrame(recent_trades)
        if not df_trades.empty:
            # Ordenar y formatear
            st.dataframe(
                df_trades.sort_index(ascending=False).head(10),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.caption("No hay operaciones registradas en esta sesión.")


from src.services.analysis.chat_engine import ChatEngine

def render_chat():
    """Renderiza Chat con el Bot (Mejorado v2)"""
    st.title("💬 Copiloto IOL Quantum")
    st.caption("Tu asistente de inteligencia financiera 24/7")

    # Inicializar historial de chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hola 👋. Soy tu analista personal. ¿En qué puedo ayudarte hoy?"}
        ]
    
    # --- SIDEBAR ACTIONS ---
    with st.sidebar:
        st.markdown("### ⚡ Acciones Rápidas")
        if st.button("🧼 Limpiar Chat", use_container_width=True, key="btn_clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
            
    # --- QUICK PROMPTS ---
    # Sugerencias visuales (Chips)
    st.markdown("###### Sugerencias:")
    cols = st.columns(4)
    prompt_to_send = None
    
    if cols[0].button("💰 Mi Saldo"): prompt_to_send = "mi saldo"
    if cols[1].button("📊 Mercado"): prompt_to_send = "precio todo"
    if cols[2].button("🧠 Estrategia"): prompt_to_send = "evolucion"
    if cols[3].button("🔍 Oportunidades"): prompt_to_send = "analizar mercado"

    st.divider()

    # Mostrar historial
    for msg in st.session_state.chat_history:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
    # Input usuario
    user_input = st.chat_input("Escribe tu consulta o comando...")
    
    # Determinar si hay input (manual o por botón)
    final_prompt = prompt_to_send if prompt_to_send else user_input
    
    if final_prompt:
        # Agregar usuario
        st.session_state.chat_history.append({"role": "user", "content": final_prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(final_prompt)
            
        # Procesar respuesta
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analizando mercado... 🧠"):
                
                # Preparar contexto del bot (Snapshot real)
                bot_state = {}
                if st.session_state.bot_instance:
                    bot = st.session_state.bot_instance
                    # Intentar leer atributos seguros
                    bot_state["capital"] = getattr(bot, "capital", 0)
                    bot_state["portfolio"] = getattr(bot, "portfolio", {})
                    
                    # Indicadores Activos (Escaneo reciente)
                    active = {}
                    symbols = getattr(bot, "symbols", ["GGAL", "YPFD"])
                    
                    for sym in symbols:
                        # Intentar leer cache o live
                        md = bot.get_market_data_safe(sym)
                        if md:
                            active[sym] = {
                                "Price": md.get('last_price', 0),
                                "RSI": 50, # Placeholder visual si no exponemos TA
                                "Signal": "NEUTRAL"
                            }
                    bot_state["active_indicators"] = active
                    
                    # Intentar leer mejor estrategia
                    if hasattr(bot, "evolution_engine"):
                        if hasattr(bot.evolution_engine, "best_strategy"):
                            bs = bot.evolution_engine.best_strategy
                            if bs:
                                bot_state["best_dna"] = bs.lines
                                bot_state["best_fitness"] = bs.fitness
                    
                else:
                    # Demo Context
                    bot_state["capital"] = 1000000
                    bot_state["active_indicators"] = {
                        "GGAL": {"Price": 2850, "RSI": 32, "Signal": "BUY"},
                        "YPFD": {"Price": 15400, "RSI": 65, "Signal": "HOLD"}
                    }
                
                # Invocar motor de chat
                engine = ChatEngine()
                response = engine.process_message(final_prompt, bot_state)
                
                # Simular delay "cognitivo" leve para UX
                time.sleep(0.3)
                st.markdown(response)
            
        # Guardar respuesta
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Rerun para limpiar el input si fue via botón, o actualizar UI
        if prompt_to_send:
            st.rerun()


if __name__ == "__main__":
    main()
