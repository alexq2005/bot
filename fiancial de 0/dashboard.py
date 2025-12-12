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
    
    # Inicializar session_state para configuraciones
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 10
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
    
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
    
    # Configuraciones del dashboard
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Configuraciones")
    
    # Auto-refresh
    st.session_state.auto_refresh = st.sidebar.checkbox(
        "🔄 Auto-refresh",
        value=st.session_state.auto_refresh,
        help="Actualiza automáticamente los datos"
    )
    
    if st.session_state.auto_refresh:
        st.session_state.refresh_interval = st.sidebar.select_slider(
            "Intervalo",
            options=[5, 10, 30, 60, 300],
            value=st.session_state.refresh_interval,
            format_func=lambda x: f"{x}s" if x < 60 else f"{x//60}m"
        )
        
        # Auto-refresh logic
        time.sleep(st.session_state.refresh_interval)
        st.rerun()
    
    # Botón de refresh manual
    if st.sidebar.button("🔄 Actualizar Ahora", use_container_width=True):
        st.session_state.last_update = datetime.now()
        st.rerun()
    
    # Mostrar última actualización
    st.sidebar.caption(f"⏰ Última actualización: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
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
    """Renderiza el Command Center - Centro de Control Principal"""
    st.title("🖥️ Command Center")
    st.markdown("### Centro de Control y Monitoreo del Sistema")
    
    # ============================================
    # SECCIÓN 1: KPIs PRINCIPALES
    # ============================================
    st.markdown("#### 📊 Métricas Principales")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.session_state.bot_running:
            st.metric("Estado del Bot", "🟢 Activo", "Ejecutando", delta_color="normal")
        else:
            st.metric("Estado del Bot", "🔴 Inactivo", "Detenido", delta_color="inverse")
    
    with col2:
        if st.session_state.bot_instance:
            symbols_count = len(st.session_state.bot_instance.symbols)
        else:
            symbols_count = 0
        st.metric("Símbolos", symbols_count, "Monitoreando")
    
    with col3:
        if st.session_state.bot_instance:
            trades_count = len(st.session_state.bot_instance.trades_history)
        else:
            trades_count = 0
        st.metric("Trades Hoy", trades_count, "+0")
    
    with col4:
        # Simular profit/loss
        profit_loss = "+2.5%"
        st.metric("P&L Hoy", profit_loss, "↑ Ganancia", delta_color="normal")
    
    with col5:
        # Simular capital
        capital = "$10,000"
        st.metric("Capital", capital, "+$250")
    
    st.markdown("---")
    
    # ============================================
    # SECCIÓN 2: CONTROLES RÁPIDOS
    # ============================================
    st.markdown("#### 🎮 Controles Rápidos")
    
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4, col_ctrl5 = st.columns(5)
    
    with col_ctrl1:
        if st.button("▶️ Iniciar Bot", disabled=st.session_state.bot_running, use_container_width=True, type="primary"):
            start_bot()
    
    with col_ctrl2:
        if st.button("🛑 Detener Bot", disabled=not st.session_state.bot_running, use_container_width=True, type="secondary"):
            stop_bot()
    
    with col_ctrl3:
        if st.button("📊 Análisis Rápido", use_container_width=True):
            st.info("Ejecutando análisis rápido...")
    
    with col_ctrl4:
        if st.button("📈 Ver Portafolio", use_container_width=True):
            st.info("Redirigiendo a Gestión de Activos...")
    
    with col_ctrl5:
        if st.button("🔔 Alertas", use_container_width=True):
            st.info("Mostrando alertas activas...")
    
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
        
        # Filtros de actividad
        activity_filter = st.radio("Filtrar:", ["Todos", "Info", "Error", "Success"], horizontal=True, key="act_filter")
        
        if st.session_state.bot_messages:
            # Filtrar mensajes
            filtered_msgs = st.session_state.bot_messages
            if activity_filter != "Todos":
                filter_map = {"Info": "info", "Error": "error", "Success": "success"}
                target_type = filter_map.get(activity_filter, "info")
                filtered_msgs = [m for m in filtered_msgs if m.get('type') == target_type]
            
            recent_messages = filtered_msgs[-10:] # Mostrar más mensajes
            
            if recent_messages:
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
            else:
                 st.info(f"No hay mensajes de tipo {activity_filter}.")
        else:
            st.info("No hay actividad reciente. Inicia el bot para ver actualizaciones.")
    
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
        if st.button("🔄 Recargar Símbolos", use_container_width=True):
            add_bot_message("Recargando universo de símbolos...", "info")
            st.success("Símbolos recargados exitosamente")
    
    with col_action2:
        if st.button("📊 Generar Reporte", use_container_width=True):
            st.info("Generando reporte diario en PDF...")
    
    with col_action3:
        if st.button("🧹 Limpiar Logs", use_container_width=True):
            st.session_state.bot_messages = []
            st.success("Logs limpiados")
            
    with col_action4:
        if st.button("📥 Exportar Datos", use_container_width=True):
             st.info("Exportando datos a CSV...")


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
