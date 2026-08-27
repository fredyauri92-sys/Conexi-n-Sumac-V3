import streamlit as st
import requests
import json
import threading
import os
from datetime import datetime

# Configuración de página móvil premium
st.set_page_config(
    page_title="SUMAC POS - Sicuani",
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
        padding: 12px;
        font-size: 15px;
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
    /* Estilo para las imágenes de productos (Bordes redondeados y sombra premium) */
    [data-testid="stImage"] img {
        border-radius: 15px !important;
        border: 1px solid #37474F !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5) !important;
    }
    /* Estilo para el botón de formulario */
    div.stFormSubmitButton > button {
        background-color: #FF3D00 !important;
        color: #FFFFFF !important;
        border: 1px solid #FF3D00 !important;
        border-radius: 15px !important;
        padding: 12px !important;
        font-size: 15px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    div.stFormSubmitButton > button:active {
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
    .status-badge {
        background-color: #1B5E20;
        color: #00FF66;
        padding: 8px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 15px;
        border: 1px solid #00FF66;
    }
    /* Quitar bordes feos del formulario en modo oscuro */
    [data-testid="stForm"] {
        border: 1px solid #37474F !important;
        border-radius: 15px !important;
        background-color: #1E1E1E !important;
        padding: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO INTEGRADO PREMIUM (LOGO "YAURI CLOUD" MINI AL 40% EN LA ESQUINA SUPERIOR IZQUIERDA) ---
col_logo, col_titulo = st.columns([0.45, 3.55])

with col_logo:
    try:
        # Se carga el logotipo a un ancho de 64 píxeles (scale 40%)
        if os.path.exists("yauri_cloud_logo_final.png"):
            st.image("yauri_cloud_logo_final.png", width=64)
        elif os.path.exists("yauri_cloud_logo_rectangular.png"):
            st.image("yauri_cloud_logo_rectangular.png", width=64)
        elif os.path.exists("yauri_cloud_logo_futuristic_1.png"):
            st.image("yauri_cloud_logo_futuristic_1.png", width=64)
    except Exception as e:
        pass

with col_titulo:
    st.markdown("<h2 style='color: #FFFFFF; margin: 0; padding-top: 2px; font-size: 21px; line-height: 1.1;'>🍜 CALDERÍA SUMAC</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #FFEA00; font-weight: bold; font-size: 11px; margin: 0; padding-top: 1px;'>📍 Sicuani, Canchis • ⚡</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ENLACE DE GOOGLE SHEETS COMPLETAMENTE AUTOMÁTICO ---
API_URL_DEFAULT = "https://script.google.com/macros/s/AKfycbyEtpDsa8tPJ3LKnNmca4Smm71X1XE88egDdqdPMqHkOZbATHnunENK4Ddc5zHvpZdq_A/exec"

if "api_url" not in st.session_state:
    st.session_state["api_url"] = API_URL_DEFAULT

# Indicador de conexión automática arriba
st.markdown("<div class='status-badge'>⚡ SISTEMA CONECTOR ACTIVO (REGISTRO INSTANTÁNEO HABILITADO)</div>", unsafe_allow_html=True)

# --- SISTEMA DE BASES DE DATOS CLOUD CON CACHÉ INTELIGENTE ---
def cargar_datos_cloud():
    api_url = st.session_state["api_url"]
    try:
        response = requests.get(api_url, timeout=6)
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
        pass
    
    return {"ventas": [], "compras": [], "planilla": []}

# Hilo de ejecución secundario para subir a Sheets sin congelar la pantalla del mozo
def enviar_a_sheets_bg(api_url, payload):
    try:
        requests.post(api_url, json=payload, timeout=12)
    except:
        pass

def registrar_movimiento_instantaneo(tipo, detalle, monto):
    api_url = st.session_state["api_url"]
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. Registrar LOCALMENTE en la memoria (caché) para actualizar la pantalla en MILISEGUNDOS
    if tipo == "VENTA":
        st.session_state["datos_cache"]["ventas"].append({
            "fecha": fecha_hoy,
            "producto": detalle,
            "total": monto
        })
    elif tipo == "GASTO":
        st.session_state["datos_cache"]["compras"].append({
            "fecha": fecha_hoy,
            "detalle": detalle,
            "monto": monto
        })
        
    # 2. Disparar el envío a Google Sheets de forma ASÍNCRONA (en segundo plano)
    payload = {
        "action": "registrar",
        "fecha": fecha_hoy,
        "tipo": tipo,
        "detalle": detalle,
        "monto": monto
    }
    
    hilo = threading.Thread(target=enviar_a_sheets_bg, args=(api_url, payload))
    hilo.start()
    return True

# Inicializar caché en session state
if "datos_cache" not in st.session_state:
    with st.spinner("🔌 Conectando con la Caja Consolidada..."):
        st.session_state["datos_cache"] = cargar_datos_cloud()

datos = st.session_state["datos_cache"]

# Menú de Productos de Caldería Sumac con rutas de imagen reales (como en la versión de Python)
PRODUCTOS_INFO = [
    {"nombre": "Caldo sin presa", "precio": 5.0, "icono": "🍲", "imagen": "caldo_sin_presa.png"},
    {"nombre": "Caldo presa mediana", "precio": 8.0, "icono": "🍲", "imagen": "caldo_sicuani.png"},
    {"nombre": "Caldo presa entera", "precio": 12.0, "icono": "🍲", "imagen": "caldo_presa_grande.png"},
    {"nombre": "Gaseosa personal", "precio": 2.0, "icono": "🥤", "imagen": "gaseosas_personales.png"},
    {"nombre": "Gaseosa de 1 Litro", "precio": 6.0, "icono": "🍾", "imagen": "gaseosas_litro.png"},
    {"nombre": "Agua mineral", "precio": 1.0, "icono": "💧", "imagen": "agua_san_luis.png"}
]

# Inicializar modificadores de huevos extra si no existen
for idx in range(len(PRODUCTOS_INFO)):
    key_h = f"huevos_extra_{idx}"
    if key_h not in st.session_state:
        st.session_state[key_h] = 0

# Helper para contar ventas consolidadas hoy por producto
def contar_vendidos_hoy(nombre_base):
    total = 0
    for v in datos["ventas"]:
        if nombre_base in v.get("producto", ""):
            total += 1
    return total

# Función súper robusta para extraer la hora (HH:MM) de cualquier formato de fecha (ISO, Sheets, etc.)
def extraer_hora(fecha_str):
    if not fecha_str:
        return "--:--"
    # Si viene en formato ISO (con T)
    if "T" in fecha_str:
        parts = fecha_str.split("T")
        if len(parts) > 1:
            return parts[1][:5]
    # Si viene con espacio
    if " " in fecha_str:
        parts = fecha_str.split()
        if len(parts) > 1:
            return parts[1][:5]
    # Si contiene dos puntos (ej: "13:25:00")
    if ":" in fecha_str:
        import re
        match = re.search(r'(\d{1,2}:\d{2})', fecha_str)
        if match:
            return match.group(1)
    return fecha_str[-5:] if len(fecha_str) >= 5 else fecha_str

# Pestañas de navegación móvil cómoda en la parte superior
tab_ventas, tab_gastos, tab_caja = st.tabs(["🛒 Registrar Ventas", "💸 Anotar Gastos", "💼 Ver Caja"])

with tab_ventas:
    st.markdown("<h4 style='color: #CFD8DC;'>Selecciona para vender:</h4>", unsafe_allow_html=True)
    
    # Grid de imágenes de producto y botones de venta de 2 en 2 (Como lo hicimos en Python)
    for i in range(0, len(PRODUCTOS_INFO), 2):
        col1, col2 = st.columns(2)
        
        # ---- PRODUCTO 1 ----
        p1 = PRODUCTOS_INFO[i]
        with col1:
            # Renderizar la hermosa imagen de producto con bordes redondeados y sombra
            if "imagen" in p1 and os.path.exists(p1["imagen"]):
                st.image(p1["imagen"], use_container_width=True)
                
            cant1 = contar_vendidos_hoy(p1["nombre"])
            es_caldo1 = "Caldo" in p1["nombre"]
            huevos_extra1 = st.session_state.get(f"huevos_extra_{i}", 0) if es_caldo1 else 0
            precio_final1 = p1["precio"] + (huevos_extra1 * 1.0)
            
            # Formatear etiqueta con huevos si aplica
            if huevos_extra1 > 0:
                label_p1 = f"🛒 {p1['nombre']}\nS/. {precio_final1:.2f} (+{huevos_extra1}🥚)\n[ Hoy: {cant1} ]"
            else:
                label_p1 = f"🛒 {p1['nombre']}\nS/. {precio_final1:.2f}\n[ Hoy: {cant1} ]"
                
            if st.button(label_p1, key=f"btn_{i}"):
                nombre_reg1 = p1["nombre"]
                if huevos_extra1 > 0:
                    nombre_reg1 += f" (+{huevos_extra1} huevo{'s' if huevos_extra1 > 1 else ''})"
                
                if registrar_movimiento_instantaneo("VENTA", nombre_reg1, precio_final1):
                    st.toast(f"🟢 Venta registrada: {nombre_reg1}", icon="🍲")
                    if es_caldo1:
                        st.session_state[f"huevos_extra_{i}"] = 0
                    st.rerun()
            
            # Controles +/- de huevos extra justo abajo para caldos
            if es_caldo1:
                c_dec, c_val, c_inc = st.columns([1, 1.5, 1])
                with c_dec:
                    if st.button("➖", key=f"dec_{i}", help="Quitar huevo"):
                        if st.session_state[f"huevos_extra_{i}"] > 0:
                            st.session_state[f"huevos_extra_{i}"] -= 1
                            st.rerun()
                with c_val:
                    st.markdown(f"<div style='text-align: center; font-size: 13px; font-weight: bold; padding-top: 8px; color: #FFEA00;'>🥚 +{huevos_extra1}</div>", unsafe_allow_html=True)
                with c_inc:
                    if st.button("➕", key=f"inc_{i}", help="Agregar huevo (+S/. 1.00)"):
                        if st.session_state[f"huevos_extra_{i}"] < 4:
                            st.session_state[f"huevos_extra_{i}"] += 1
                            st.rerun()
                
        # ---- PRODUCTO 2 ----
        if i + 1 < len(PRODUCTOS_INFO):
            p2 = PRODUCTOS_INFO[i+1]
            with col2:
                # Renderizar la hermosa imagen de producto con bordes redondeados y sombra
                if "imagen" in p2 and os.path.exists(p2["imagen"]):
                    st.image(p2["imagen"], use_container_width=True)
                    
                cant2 = contar_vendidos_hoy(p2["nombre"])
                es_caldo2 = "Caldo" in p2["nombre"]
                huevos_extra2 = st.session_state.get(f"huevos_extra_{i+1}", 0) if es_caldo2 else 0
                precio_final2 = p2["precio"] + (huevos_extra2 * 1.0)
                
                if huevos_extra2 > 0:
                    label_p2 = f"🛒 {p2['nombre']}\nS/. {precio_final2:.2f} (+{huevos_extra2}🥚)\n[ Hoy: {cant2} ]"
                else:
                    label_p2 = f"🛒 {p2['nombre']}\nS/. {precio_final2:.2f}\n[ Hoy: {cant2} ]"
                    
                if st.button(label_p2, key=f"btn_{i+1}"):
                    nombre_reg2 = p2["nombre"]
                    if huevos_extra2 > 0:
                        nombre_reg2 += f" (+{huevos_extra2} huevo{'s' if huevos_extra2 > 1 else ''})"
                    
                    if registrar_movimiento_instantaneo("VENTA", nombre_reg2, precio_final2):
                        st.toast(f"🟢 Venta registrada: {nombre_reg2}", icon="🥤")
                        if es_caldo2:
                            st.session_state[f"huevos_extra_{i+1}"] = 0
                        st.rerun()
                        
                if es_caldo2:
                    c_dec2, c_val2, c_inc2 = st.columns([1, 1.5, 1])
                    with c_dec2:
                        if st.button("➖", key=f"dec_{i+1}", help="Quitar huevo"):
                            if st.session_state[f"huevos_extra_{i+1}"] > 0:
                                st.session_state[f"huevos_extra_{i+1}"] -= 1
                                st.rerun()
                    with c_val2:
                        st.markdown(f"<div style='text-align: center; font-size: 13px; font-weight: bold; padding-top: 8px; color: #FFEA00;'>🥚 +{huevos_extra2}</div>", unsafe_allow_html=True)
                    with c_inc2:
                        if st.button("➕", key=f"inc_{i+1}", help="Agregar huevo (+S/. 1.00)"):
                            if st.session_state[f"huevos_extra_{i+1}"] < 4:
                                st.session_state[f"huevos_extra_{i+1}"] += 1
                                st.rerun()

    st.markdown("<br><h5 style='color: #CFD8DC;'>📝 Últimos movimientos del turno (Lista de registro):</h5>", unsafe_allow_html=True)
    
    movimientos = []
    for v in datos["ventas"]:
        movimientos.append((v["fecha"], f"🟢 VENTA - {v['producto']}", v["total"]))
    for c in datos["compras"]:
        movimientos.append((c["fecha"], f"🔴 GASTO - {c['detalle']}", -c["monto"]))
        
    if movimientos:
        try:
            # Ordenar por fecha y hora de más reciente a más antiguo
            movimientos.sort(key=lambda x: x[0], reverse=True)
        except:
            pass
        for fecha, detalle, monto in movimientos:
            color_txt = "#00FF66" if "VENTA" in detalle else "#FF0055"
            hora = extraer_hora(fecha)
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid {color_txt};'><span style='color: #FFFFFF; font-weight: bold;'>{detalle}</span><span style='color: {color_txt}; font-weight: bold;'>S/. {abs(monto):.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay movimientos registrados hoy.")

with tab_gastos:
    st.markdown("<h4 style='color: #CFD8DC;'>Anotar un Gasto de Caja:</h4>", unsafe_allow_html=True)
    
    # Formulario inteligente con autolimpieza nativa segura y campo vaciado por defecto (value=None)
    with st.form("formulario_gastos_sumac", clear_on_submit=True):
        desc_gasto = st.text_input("¿En qué se gastó? (Ej: Gas, Gallinas, Verduras)")
        monto_gasto = st.number_input("Monto gastado (S/.)", min_value=0.0, step=1.0, value=None)
        
        btn_registrar = st.form_submit_button("💾 Registrar Gasto en Caja")
        
        if btn_registrar:
            if desc_gasto and monto_gasto is not None and monto_gasto > 0:
                if registrar_movimiento_instantaneo("GASTO", desc_gasto, monto_gasto):
                    st.toast(f"🔴 Gasto registrado: {desc_gasto} (S/. {monto_gasto:.2f})", icon="💸")
                    st.rerun()
            else:
                st.error("Por favor ingresa una descripción y un monto válido.")

    st.markdown("<br><h5 style='color: #CFD8DC;'>📋 Gastos de hoy registrados:</h5>", unsafe_allow_html=True)
    if datos["compras"]:
        gastos_hoy = datos["compras"]
        try:
            # Ordenar los gastos de más reciente a más antiguo
            gastos_hoy_sorted = sorted(gastos_hoy, key=lambda x: x["fecha"], reverse=True)
        except:
            gastos_hoy_sorted = gastos_hoy
            
        for g in gastos_hoy_sorted:
            fecha = g.get("fecha", "")
            hora = extraer_hora(fecha)
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #FF0055;'><span style='color: #FFEA00; font-weight: bold;'>• {g['detalle']}</span><span style='color: #FF0055; font-weight: bold;'>S/. {g['monto']:.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay gastos registrados hoy.")

with tab_caja:
    st.markdown("<h4 style='text-align: center; color: #CFD8DC;'>💼 Finanzas del Turno</h4>", unsafe_allow_html=True)
    
    # Sincronización Manual segura
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("<span style='font-size: 13px; color: #CFD8DC;'>Sincronizar las ventas de todos los mozos:</span>", unsafe_allow_html=True)
    with col_v2:
        if st.button("🔄 Actualizar", key="btn_sync_caja"):
            with st.spinner("Conectando..."):
                st.session_state["datos_cache"] = cargar_datos_cloud()
                st.rerun()

    total_v = sum(v["total"] for v in datos["ventas"])
    total_g = sum(c["monto"] for c in datos["compras"])
    egresos = total_g
    ganancia = total_v - egresos
    
    col_v, col_g = st.columns(2)
    with col_v:
        st.markdown(f"<div class='metric-box'>Ingresos<br><span class='metric-val-green'>S/. {total_v:.2f}</span></div>", unsafe_allow_html=True)
    with col_g:
        st.markdown(f"<div class='metric-box'>Gastos<br><span class='metric-val-red'>S/. {egresos:.2f}</span></div>", unsafe_allow_html=True)
        
    st.markdown(f"<div class='metric-box' style='background: #252525;'>GANANCIA NETA<br><span class='metric-val-blue' style='color: {'#00FF66' if ganancia >= 0 else '#FF0055'}'>S/. {ganancia:.2f}</span></div>", unsafe_allow_html=True)

    if total_v > 0:
        st.markdown("<br><h5 style='text-align: center; color: #CFD8DC;'>📊 Distribución Financiera:</h5>", unsafe_allow_html=True)
        porcentaje_gasto = (egresos / total_v)
        porcentaje_rentabilidad = max(0.0, 1.0 - porcentaje_gasto)
        
        st.write(f"🟢 Ganancia Neta ({porcentaje_rentabilidad*100:.0f}%)")
        st.progress(porcentaje_rentabilidad)
        
        st.write(f"🔴 Gastos de Operación ({porcentaje_gasto*100:.0f}%)")
        st.progress(porcentaje_gasto)
    else:
        st.info("Registra ventas para ver el análisis de rentabilidad.")

    # --- SECCIÓN SEGURO DE REINICIO DE CAJA ---
    st.markdown("---")
    st.markdown("<h5 style='color: #FF0055;'>🧹 Zona de Seguridad</h5>", unsafe_allow_html=True)
    
    # Etiqueta limpia que solo dice "Contraseña:" para máxima discreción
    clave_caja = st.text_input("Contraseña:", type="password", key="clave_caja_web")
    if clave_caja == "1992":
        if st.button("⚠️ CONFIRMAR REINICIO COMPLETO DE CAJA", key="btn_reiniciar_caja_web"):
            api_url = st.session_state["api_url"]
            with st.spinner("Borrando base de datos central..."):
                try:
                    payload = {"action": "reiniciar"}
                    response = requests.post(api_url, json=payload, timeout=5)
                    if response.status_code == 200:
                        st.session_state["datos_cache"] = {"ventas": [], "compras": [], "planilla": []}
                        st.success("¡Base de datos en Google Sheets borrada con éxito!")
                        st.rerun()
                    else:
                        st.error("Error al borrar la hoja de Google Sheets. Verifica tus permisos.")
                except Exception as e:
                    st.error(f"Error de conexión con el servidor: {e}")
