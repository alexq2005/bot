#!/usr/bin/env python3
"""
Dashboard de Monitoreo en Streamlit
Monitorea cambios en app.py en tiempo real a través del navegador
"""

import streamlit as st
import os
import hashlib
import subprocess
import time
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="Monitor app.py",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-ok { color: #28a745; }
    .status-error { color: #dc3545; }
    .status-warning { color: #ffc107; }
</style>
""", unsafe_allow_html=True)

def get_file_stats(filepath="src/dashboard/app.py"):
    """Obtiene estadísticas del archivo"""
    if not os.path.exists(filepath):
        return None
    
    size = os.path.getsize(filepath)
    modified = os.path.getmtime(filepath)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = len(f.readlines())
    
    # Calcular hash
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    return {
        'size': size,
        'lines': lines,
        'modified': datetime.fromtimestamp(modified),
        'hash': file_hash,
        'path': filepath
    }

def check_syntax(filepath="src/dashboard/app.py"):
    """Verifica sintaxis de Python"""
    result = subprocess.run(
        ['python', '-m', 'py_compile', filepath],
        capture_output=True,
        text=True
    )
    return {
        'valid': result.returncode == 0,
        'error': result.stderr if result.returncode != 0 else None
    }

def get_recent_lines(filepath="src/dashboard/app.py", n=10):
    """Obtiene las últimas n líneas del archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        return lines[-n:]
    except:
        return []

def main():
    st.title("📊 Monitor de app.py")
    st.markdown("Dashboard en tiempo real de cambios en el archivo principal del dashboard")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuración")
    refresh_interval = st.sidebar.slider("Intervalo de refresh (segundos)", 1, 60, 3)
    
    # Estado principal
    stats = get_file_stats()
    syntax_check = check_syntax()
    
    if stats is None:
        st.error("❌ Archivo no encontrado")
        return
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Líneas de Código", f"{stats['lines']:,}")
    
    with col2:
        st.metric("📦 Tamaño", f"{stats['size']:,} bytes")
    
    with col3:
        status = "✅ VÁLIDO" if syntax_check['valid'] else "❌ ERROR"
        st.metric("🔍 Sintaxis", status)
    
    with col4:
        st.metric("⏰ Última Mod.", stats['modified'].strftime('%H:%M:%S'))
    
    st.divider()
    
    # Información detallada
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📋 Información del Archivo")
        st.info(f"""
        **Ruta:** `{stats['path']}`
        
        **Hash MD5:** `{stats['hash'][:16]}...`
        
        **Modificado:** {stats['modified'].strftime('%Y-%m-%d %H:%M:%S')}
        
        **Estado:** {'✅ Archivo válido' if syntax_check['valid'] else '❌ Contiene errores'}
        """)
    
    with col_right:
        st.subheader("🔧 Validación")
        if syntax_check['valid']:
            st.success("✅ La sintaxis de Python es correcta")
        else:
            st.error("❌ Errores de sintaxis detectados:")
            st.code(syntax_check['error'], language="text")
    
    st.divider()
    
    # Últimas líneas
    st.subheader("📝 Últimas 15 Líneas")
    recent_lines = get_recent_lines(n=15)
    
    code_text = "".join(recent_lines)
    st.code(code_text, language="python")
    
    st.divider()
    
    # Panel de control
    st.subheader("🎮 Panel de Control")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 Refrescar Ahora", use_container_width=True):
            st.rerun()
    
    with col_btn2:
        if st.button("📂 Abrir en Editor", use_container_width=True):
            st.info("Abre el archivo en tu editor preferido (VS Code, etc.)")
    
    with col_btn3:
        if st.button("🔐 Ver en Git", use_container_width=True):
            st.info("Ver historial de cambios en git")
    
    # Información de ejecución
    st.divider()
    st.subheader("📊 Estado del Sistema")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.write("**Procesos Activos:**")
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'streamlit|monitor'],
                capture_output=True,
                text=True
            )
            count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            st.success(f"✅ {count} procesos de monitoreo activos")
        except:
            st.warning("⚠️ No se puede verificar procesos")
    
    with col_info2:
        st.write("**Dashboard Monitor:**")
        st.success("✅ Dashboard de monitoreo funcionando correctamente")
    
    # Auto-refresh
    st.sidebar.divider()
    st.sidebar.write(f"*Última actualización: {datetime.now().strftime('%H:%M:%S')}*")
    
    # Usar session state para auto-refresh
    if 'last_check' not in st.session_state:
        st.session_state.last_check = time.time()
    
    # Auto-rerun cada X segundos
    import time as time_module
    time_module.sleep(refresh_interval)
    st.rerun()

if __name__ == "__main__":
    main()
