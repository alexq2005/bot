# 🚀 Dashboard Unificado - Guía de Uso

## ✅ NUEVO DASHBOARD CREADO

**Archivo:** `src/dashboard/dashboard_unified.py`

---

## 🎯 CARACTERÍSTICAS

### **Arquitectura Modular:**

- ✅ Importa funciones de `app.py` (no duplica código)
- ✅ Reutiliza componentes existentes
- ✅ Mantiene `app.py` intacto como backup
- ✅ Código limpio y organizado

### **6 Tabs Integrados:**

1. **🏠 Overview**
   - Métricas principales
   - Gráfico de P&L acumulado
   - Resumen del día

2. **📊 Análisis & Señales**
   - Recomendaciones del bot
   - Filtros por acción y confianza
   - Razón del análisis

3. **💼 Mi Portfolio**
   - Portfolio real desde IOL
   - P&L total y por posición
   - Gráfico de distribución

4. **🎯 Operar**
   - Panel de operación manual
   - Formulario de orden
   - Ejecución directa

5. **⚙️ Configuración**
   - Configuración avanzada
   - (Por implementar)

6. **📈 Rendimiento**
   - Métricas de performance
   - Win rate, avg P&L

### **Sidebar Unificado:**

- 🕐 Estado del Mercado
- 🤖 Control del Bot (Iniciar/Detener/Reiniciar)
- 📱 Control de Telegram (Iniciar/Detener)
- 🌐 Selector de Universo IOL
- 💾 Guardar configuración

---

## 🚀 CÓMO USAR

### **Iniciar Dashboard Unificado:**

```bash
streamlit run src/dashboard/dashboard_unified.py --server.port 8501
```

**URL:** <http://localhost:8501>

---

## 📊 COMPARACIÓN

| Característica | app.py (Original) | dashboard_unified.py (Nuevo) |
|----------------|-------------------|------------------------------|
| **Tabs** | 4 | 6 |
| **Portfolio IOL** | ❌ | ✅ |
| **Operar Manual** | ❌ | ✅ |
| **Control Telegram** | ❌ | ✅ |
| **Señales Bot** | ❌ | ✅ |
| **Modular** | ❌ | ✅ |

---

## 🔄 MIGRACIÓN

### **Opción 1: Usar Dashboard Unificado (Recomendado)**

```bash
# Detener dashboard actual
# Ctrl+C en la terminal

# Iniciar dashboard unificado
streamlit run src/dashboard/dashboard_unified.py --server.port 8501
```

### **Opción 2: Mantener Ambos**

```bash
# Terminal 1: Dashboard original
streamlit run src/dashboard/app.py --server.port 8501

# Terminal 2: Dashboard unificado
streamlit run src/dashboard/dashboard_unified.py --server.port 8502
```

---

## ✅ VENTAJAS

1. **Modular** - Reutiliza código existente
2. **Seguro** - No modifica `app.py`
3. **Completo** - Todas las funcionalidades en un lugar
4. **Limpio** - Código organizado y mantenible
5. **Extensible** - Fácil agregar nuevas funcionalidades

---

## 🎯 PRÓXIMOS PASOS

1. **Probar dashboard unificado**
2. **Verificar que todo funciona**
3. **Si todo OK, usar como dashboard principal**
4. **Mantener `app.py` como backup**

---

## 🔧 PERSONALIZACIÓN

Para agregar nuevas funcionalidades:

1. Crear función `render_nueva_tab()`
2. Agregar tab en `main()`
3. Implementar lógica

**Ejemplo:**

```python
def render_nueva_tab():
    st.header("Nueva Funcionalidad")
    # Tu código aquí

# En main()
tab7 = st.tabs(["...", "Nueva"])
with tab7:
    render_nueva_tab()
```

---

**¡Dashboard Unificado Listo!** 🎉
