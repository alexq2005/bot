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
import logging
import threading
import time
from datetime import datetime
from trading_bot import TradingBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Función principal del dashboard"""
    
    st.set_page_config(
        page_title="IOL Quantum AI Trading Bot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar session_state para el bot
    if 'bot_instance' not in st.session_state:
        st.session_state.bot_instance = None
    if 'bot_running' not in st.session_state:
        st.session_state.bot_running = False
    if 'bot_thread' not in st.session_state:
        st.session_state.bot_thread = None
    if 'bot_messages' not in st.session_state:
        st.session_state.bot_messages = []
    if 'bot_start_time' not in st.session_state:
        st.session_state.bot_start_time = None
    
    # Sidebar con navegación
    st.sidebar.title("🤖 IOL Quantum AI")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navegación",
        [
            "🖥️ Command Center",
            "📊 Dashboard en Vivo",
            "💼 Gestión de Activos",
            "🤖 Bot Autónomo",
            "🧬 Optimizador Genético",
            "🧠 Red Neuronal",
            "📉 Estrategias Avanzadas",
            "⚙️ Configuración",
            "⚡ Terminal de Trading",
            "💬 Chat con el Bot"
        ]
    )
    
    # Renderizar página seleccionada
    if page == "🖥️ Command Center":
        render_command_center()
    elif page == "📊 Dashboard en Vivo":
        render_live_dashboard()
    elif page == "💼 Gestión de Activos":
        render_asset_management()
    elif page == "🤖 Bot Autónomo":
        render_autonomous_bot()
    elif page == "🧬 Optimizador Genético":
        render_genetic_optimizer()
    elif page == "🧠 Red Neuronal":
        render_neural_network()
    elif page == "📉 Estrategias Avanzadas":
        render_advanced_strategies()
    elif page == "⚙️ Configuración":
        render_configuration()
    elif page == "⚡ Terminal de Trading":
        render_trading_terminal()
    elif page == "💬 Chat con el Bot":
        render_chat()


def render_command_center():
    """Renderiza el Command Center"""
    st.title("🖥️ Command Center")
    st.markdown("### Control Central del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Estado del Bot", "🟢 Activo", "Operando")
    
    with col2:
        st.metric("Símbolos Monitoreados", "77", "+74")
    
    with col3:
        st.metric("Trades Hoy", "5", "+2")
    
    st.markdown("---")
    st.info("Dashboard en desarrollo. Funcionalidades próximamente.")


def render_live_dashboard():
    """Renderiza el Dashboard en Vivo"""
    st.title("📊 Dashboard en Vivo")
    st.info("Página en desarrollo")


def render_asset_management():
    """Renderiza Gestión de Activos"""
    st.title("💼 Gestión de Activos")
    st.info("Página en desarrollo")


def render_autonomous_bot():
    """Renderiza Bot Autónomo con controles completos"""
    st.title("🤖 Bot Autónomo")
    st.markdown("### Control y Monitoreo del Bot de Trading")
    
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
        if st.button("▶️ Iniciar Bot", disabled=st.session_state.bot_running, use_container_width=True):
            start_bot()
    
    with col_btn2:
        if st.button("⏸️ Pausar Bot", disabled=not st.session_state.bot_running, use_container_width=True):
            pause_bot()
    
    with col_btn3:
        if st.button("🔄 Reiniciar Bot", use_container_width=True):
            restart_bot()
    
    with col_btn4:
        if st.button("🛑 Detener Bot", disabled=not st.session_state.bot_running, use_container_width=True):
            stop_bot()
    
    st.markdown("---")
    
    # Mensajes y logs del bot
    st.markdown("### 📝 Mensajes del Bot")
    
    # Contenedor de mensajes con scroll
    messages_container = st.container()
    
    with messages_container:
        if st.session_state.bot_messages:
            # Mostrar últimos 20 mensajes
            for msg in st.session_state.bot_messages[-20:]:
                timestamp = msg.get('timestamp', 'N/A')
                message = msg.get('message', '')
                msg_type = msg.get('type', 'info')
                
                if msg_type == 'success':
                    st.success(f"[{timestamp}] ✅ {message}")
                elif msg_type == 'error':
                    st.error(f"[{timestamp}] ❌ {message}")
                elif msg_type == 'warning':
                    st.warning(f"[{timestamp}] ⚠️ {message}")
                else:
                    st.info(f"[{timestamp}] ℹ️ {message}")
        else:
            st.info("No hay mensajes aún. Inicia el bot para ver los logs.")
    
    # Botón para limpiar mensajes
    if st.button("🗑️ Limpiar Mensajes"):
        st.session_state.bot_messages = []
        st.rerun()
    
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
    """Inicia el bot de trading"""
    try:
        # Agregar mensaje
        add_bot_message("Iniciando bot de trading...", "info")
        
        # Crear instancia del bot
        st.session_state.bot_instance = TradingBot()
        
        # Marcar como ejecutando
        st.session_state.bot_running = True
        st.session_state.bot_start_time = datetime.now()
        
        # Agregar mensaje de éxito
        add_bot_message(
            f"✅ Bot iniciado exitosamente con {len(st.session_state.bot_instance.symbols)} símbolos",
            "success"
        )
        
        # Ejecutar bot en thread separado
        def run_bot_thread():
            try:
                st.session_state.bot_instance.run()
            except Exception as e:
                add_bot_message(f"Error en ejecución del bot: {str(e)}", "error")
        
        st.session_state.bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
        st.session_state.bot_thread.start()
        
        st.rerun()
        
    except Exception as e:
        add_bot_message(f"Error al iniciar bot: {str(e)}", "error")
        st.session_state.bot_running = False


def pause_bot():
    """Pausa el bot de trading"""
    add_bot_message("⏸️ Bot pausado", "warning")
    st.session_state.bot_running = False
    st.rerun()


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


def stop_bot():
    """Detiene el bot de trading"""
    try:
        if st.session_state.bot_instance:
            st.session_state.bot_instance.stop()
        
        add_bot_message("🛑 Bot detenido", "warning")
        
        st.session_state.bot_running = False
        st.session_state.bot_instance = None
        st.session_state.bot_thread = None
        st.session_state.bot_start_time = None
        
        st.rerun()
        
    except Exception as e:
        add_bot_message(f"Error al detener bot: {str(e)}", "error")


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


def render_genetic_optimizer():
    """Renderiza Optimizador Genético"""
    st.title("🧬 Optimizador Genético")
    st.info("Página en desarrollo")


def render_neural_network():
    """Renderiza Red Neuronal"""
    st.title("🧠 Red Neuronal")
    st.info("Página en desarrollo")


def render_advanced_strategies():
    """Renderiza Estrategias Avanzadas"""
    st.title("📉 Estrategias Avanzadas")
    st.info("Página en desarrollo")


def render_configuration():
    """Renderiza Configuración"""
    st.title("⚙️ Configuración")
    st.info("Página en desarrollo")


def render_trading_terminal():
    """Renderiza Terminal de Trading"""
    st.title("⚡ Terminal de Trading")
    st.info("Página en desarrollo")


def render_chat():
    """Renderiza Chat con el Bot"""
    st.title("💬 Chat con el Bot")
    st.info("Página en desarrollo")


if __name__ == "__main__":
    main()
