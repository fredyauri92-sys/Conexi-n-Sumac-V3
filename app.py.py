import streamlit as st
import requests
import json
from datetime import datetime

# Configuración de página móvil premium
st.set_page_config(
    page_title="SUMAC POS Cloud V3",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo Cyber-Andino personalizado para Celulares con Colores Vivos Primarios
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #FFFFFF;
    }
    div.stButton > button:first-child {
        background-color: #1E1E1E;
        color: #FFFFFF;
        border: 1px solid #37474F;
        border-radius: 15px;
        padding: 15px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:active {
        background-color: #FFEA00 !important;
        color: #121212 !important;
        border-color: #FFEA00 !important;
    }
    .metric-box {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #37474F;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-val-green {
        color: #00FF66;
        font-size: 22px;
        font-weight: bold;
    }
    .metric-val-red {
        color: #FF0055;
        font-size: 22px;
        font-weight: bold;
    }
    .metric-val-blue {
        color: #2979FF;
        font-size: 24px;
        font-weight: bold;
    }
    .tutorial-box {
        background-color: #1A237E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2979FF;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Cabecera limpia y minimalista
st.markdown("<h1 style='text-align: center; color: #FFFFFF; margin-bottom: 0;'>🍜 CALDERÍA SUMAC</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FFEA00; font-weight: bold; font-size: 14px;'>📍 Sicuani, Canchis, Cusco</p>", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE BASE DE DATOS CENTRAL (GOOGLE SHEETS) ---
if "api_url" in st.query_params:
    st.session_state["api_url"] = st.query_params["api_url"]

# Panel de Configuración en el Sidebar para Helios
with st.sidebar:
    st.markdown("### ⚙️ Conexión Consolidada")
    url_input = st.text_input(
        "Pegar Enlace de Google Sheets (Web App):",
        value=st.session_state.get("api_url", ""),
        placeholder="https://script.google.com/macros/s/.../exec"
    )
    if url_input:
        st.session_state["api_url"] = url_input
        st.query_params["api_url"] = url_input
        st.success("¡Enlace conectado y guardado!")

# Funciones para leer y escribir en Google Sheets a través de la API de Apps Script
def cargar_datos_cloud():
    api_url = st.session_state.get("api_url", "")
    if not api_url:
        if "local_data" not in st.session_state:
            st.session_state["local_data"] = {"ventas": [], "compras": [], "planilla": []}
        return st.session_state["local_data"]
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            rows = response.json()
            datos_formateados = {"ventas": [], "compras": [], "planilla": []}
            for row in rows:
                fecha = row.get("fecha", "")
                tipo = row.get("tipo", "")
                detalle = row.get("detalle", "")
                monto = float(row.get("monto", 0))
                
                if tipo == "VENTA":
                    datos_formateados["ventas"].append({
                        "fecha": fecha,
                        "producto": detalle,
                        "total": monto
                    })
                elif tipo == "GASTO":
                    datos_formateados["compras"].append({
                        "fecha": fecha,
                        "detalle": detalle,
                        "monto": monto
                    })
            return datos_formateados
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")
    
    if "local_data" not in st.session_state:
        st.session_state["local_data"] = {"ventas": [], "compras": [], "planilla": []}
    return st.session_state["local_data"]

def guardar_movimiento_cloud(tipo, detalle, monto):
    api_url = st.session_state.get("api_url", "")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if not api_url:
        if tipo == "VENTA":
            st.session_state["local_data"]["ventas"].append({
                "fecha": fecha_hoy,
                "producto": detalle,
                "total": monto
            })
        elif tipo == "GASTO":
            st.session_state["local_data"]["compras"].append({
                "fecha": fecha_hoy,
                "detalle": detalle,
                "monto": monto
            })
        return True
    
    try:
        payload = {
            "action": "registrar",
            "fecha": fecha_hoy,
            "tipo": tipo,
            "detalle": detalle,
            "monto": monto
        }
        response = requests.post(api_url, json=payload, timeout=5)
        return response.status_code == 200
    except:
        return False

def reiniciar_caja_cloud():
    api_url = st.session_state.get("api_url", "")
    if not api_url:
        st.session_state["local_data"] = {"ventas": [], "compras": [], "planilla": []}
        return True
    try:
        payload = {"action": "reiniciar"}
        response = requests.post(api_url, json=payload, timeout=5)
        return response.status_code == 200
    except:
        return False

# Cargar los datos de forma inmediata
datos = cargar_datos_cloud()

# --- TUTORIAL SI NO ESTÁ CONECTADO ---
if not st.session_state.get("api_url", ""):
    with st.expander("🚨 ¡PASO IMPORTANTE! Haz clic aquí para conectar todos los celulares", expanded=True):
        st.markdown("""
        <div class='tutorial-box'>
        <strong>¡Hola Helios!</strong> Para que las ventas de tus mozos se unan en un solo lugar en tiempo real:<br><br>
        1. Abre el menú lateral de esta app (las 3 rayitas de arriba a la izquierda).<br>
        2. Pega el enlace de Google Sheets que termina en <strong>/exec</strong>.<br>
        3. ¡Eso es todo! El sistema quedará enlazado en este celular para siempre.
        </div>
        """, unsafe_allow_html=True)

# Menú de Productos
PRODUCTOS_INFO = [
    {"nombre": "Caldo sin presa", "precio": 5.0, "icono": "🍲"},
    {"nombre": "Caldo presa mediana", "precio": 8.0, "icono": "🍲"},
    {"nombre": "Caldo presa entera", "precio": 12.0, "icono": "🍲"},
    {"nombre": "Gaseosa personal", "precio": 2.0, "icono": "🥤"},
    {"nombre": "Gaseosa de 1 Litro", "precio": 6.0, "icono": "🍾"},
    {"nombre": "Agua mineral", "precio": 1.0, "icono": "💧"}
]

# Pestañas de navegación móvil cómoda
tab_ventas, tab_gastos, tab_caja = st.tabs(["🛒 Registrar Ventas", "💸 Anotar Gastos", "💼 Ver Caja"])

with tab_ventas:
    st.markdown("<h4 style='color: #CFD8DC;'>Selecciona para vender:</h4>", unsafe_allow_html=True)
    
    # Grid de botones grandes táctiles de 2 en 2
    for i in range(0, len(PRODUCTOS_INFO), 2):
        col1, col2 = st.columns(2)
        
        # Producto 1
        p1 = PRODUCTOS_INFO[i]
        with col1:
            if st.button(f"{p1['icono']} {p1['nombre']}\nS/. {p1['precio']:.2f}", key=f"btn_{i}"):
                if guardar_movimiento_cloud("VENTA", p1["nombre"], p1["precio"]):
                    st.toast(f"🟢 Venta registrada: {p1['nombre']}", icon="🍲")
                    st.rerun()
                else:
                    st.error("Error al conectar con la base de datos cloud.")
                
        # Producto 2
        if i + 1 < len(PRODUCTOS_INFO):
            p2 = PRODUCTOS_INFO[i+1]
            with col2:
                if st.button(f"{p2['icono']} {p2['nombre']}\nS/. {p2['precio']:.2f}", key=f"btn_{i+1}"):
                    if guardar_movimiento_cloud("VENTA", p2["nombre"], p2["precio"]):
                        st.toast(f"🟢 Venta registrada: {p2['nombre']}", icon="🥤")
                        st.rerun()
                    else:
                        st.error("Error al conectar con la base de datos cloud.")

    # Recibo digital consolidado de movimientos
    st.markdown("<br><h5 style='color: #CFD8DC;'>📝 Últimos movimientos consolidados:</h5>", unsafe_allow_html=True)
    
    movimientos = []
    for v in datos["ventas"]:
        movimientos.append((v["fecha"], f"🟢 VENTA - {v['producto']}", v["total"]))
    for c in datos["compras"]:
        movimientos.append((c["fecha"], f"🔴 GASTO - {c['detalle']}", -c["monto"]))
        
    if movimientos:
        try:
            movimientos.sort(key=lambda x: x, reverse=True)
        except:
            pass
        for m in movimientos[:8]:
            color_txt = "#00FF66" if "VENTA" in m[1] else "#FF0055"
            hora = m[0].split()[-1] if " " in m[0] else ""
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid {color_txt};'><span style='color: #FFFFFF; font-weight: bold;'>{m[1]}</span><span style='color: {color_txt}; font-weight: bold;'>S/. {abs(m[2]):.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay movimientos registrados hoy.")

with tab_gastos:
    st.markdown("<h4 style='color: #CFD8DC;'>Anotar un Gasto de Caja:</h4>", unsafe_allow_html=True)
    desc_gasto = st.text_input("¿En qué se gastó? (Ej: Gas, Gallinas, Verduras)", key="desc_gasto_web")
    monto_gasto = st.number_input("Monto gastado (S/.)", min_value=0.0, step=1.0, key="monto_gasto_web")
    
    if st.button("💾 Registrar Gasto en Caja", key="btn_registrar_gasto_web"):
        if desc_gasto and monto_gasto > 0:
            if guardar_movimiento_cloud("GASTO", desc_gasto, monto_gasto):
                st.success(f"🔴 Gasto registrado: {desc_gasto} por S/. {monto_gasto:.2f}")
                st.rerun()
            else:
                st.error("Error al conectar con la base de datos cloud.")
        else:
            st.error("Por favor ingresa una descripción y un monto válido.")

    # Lista de gastos consolidados
    st.markdown("<br><h5 style='color: #CFD8DC;'>📋 Gastos de hoy registrados:</h5>", unsafe_allow_html=True)
    if datos["compras"]:
        gastos_hoy = datos["compras"]
        for g in gastos_hoy[:5]:
            st.markdown(f"<div style='background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #FF0055;'><span style='color: #FFEA00; font-weight: bold;'>• {g['detalle']}</span> -> <span style='color: #FF0055; font-weight: bold;'>S/. {g['monto']:.2f}</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay gastos registrados hoy.")

with tab_caja:
    st.markdown("<h4 style='text-align: center; color: #CFD8DC;'>💼 Finanzas Consolidadas del Turno</h4>", unsafe_allow_html=True)
    
    total_v = sum(v["total"] for v in datos["ventas"])
    total_g = sum(c["monto"] for c in datos["compras"])
    egresos = total_g
    ganancia = total_v - egresos
    
    # 1. METRICAS NUMÉRICAS VISIBLES ARRIBA AL 100%
    col_v, col_g = st.columns(2)
    with col_v:
        st.markdown(f"<div class='metric-box'>Ingresos<br><span class='metric-val-green'>S/. {total_v:.2f}</span></div>", unsafe_allow_html=True)
    with col_g:
        st.markdown(f"<div class='metric-box'>Gastos<br><span class='metric-val-red'>S/. {egresos:.2f}</span></div>", unsafe_allow_html=True)
        
    st.markdown(f"<div class='metric-box' style='background: #252525;'>GANANCIA NETA<br><span class='metric-val-blue' style='color: {'#00FF66' if ganancia >= 0 else '#FF0055'}'>S/. {ganancia:.2f}</span></div>", unsafe_allow_html=True)

    # 2. GRÁFICO DE TORTA DE DONA ADAPTADO UBICADO DEBAJO DE LAS CIFRAS
    if total_v > 0:
        st.markdown("<br><h5 style='text-align: center; color: #CFD8DC;'>📊 Distribución de Rendimiento Financiero:</h5>", unsafe_allow_html=True)
        porcentaje_gasto = min(1.0, (egresos / total_v))
        porcentaje_rentabilidad = max(0.0, 1.0 - porcentaje_gasto)
        
        st.write(f"🟢 Rentabilidad Neta ({porcentaje_rentabilidad*100:.0f}%)")
        st.progress(porcentaje_rentabilidad)
        
        st.write(f"🔴 Costos y Gastos ({porcentaje_gasto*100:.0f}%)")
        st.progress(porcentaje_gasto)
    else:
        st.info("Registra ventas para ver el análisis de rentabilidad.")
        
    # 3. ZONA DE SEGURIDAD PROTEGIDA PARA REINICIO MAESTRO
    st.markdown("<br><br><hr style='border: 1px solid #37474F;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #FF0055;'>🧹 ZONA DE SEGURIDAD MAESTRA (Administrador):</h5>", unsafe_allow_html=True)
    
    pass_input = st.text_input("Ingresa contraseña maestra para reiniciar turno:", type="password", key="master_pass")
    
    if pass_input == "1992":
        st.warning("⚠️ ¡Atención! Esta acción borrará todas las ventas y gastos de la base de datos de Google Sheets.")
        if st.button("🚨 CONFIRMAR REINICIO COMPLETO DE CAJA"):
            if reiniciar_caja_cloud():
                st.success("¡Caja de Google Sheets borrada por completo con éxito!")
                st.rerun()
            else:
                st.error("Error al borrar la base de datos en la nube.")
