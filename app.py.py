import base64
import io
import json
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from PIL import Image
import requests
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA MÓVIL Y LAPTOP ---
st.set_page_config(
    page_title="SUMAC POS - Sicuani",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DE BASE DE DATOS CENTRAL (GOOGLE SHEETS) ---
API_URL_DEFAULT = "https://script.google.com/macros/s/AKfycbzUtl0x9pMXbGK4IlQltZyccAOtnvygQSX6oFh68AzjxmJg3g1P4OEYlVu6yb57_-HNPw/exec"

if "api_url" not in st.session_state:
    st.session_state["api_url"] = API_URL_DEFAULT

# --- ESTILOS CSS CYBER-ANDINO Y BOTONES ---
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
        border-radius: 12px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: bold;
        width: 100%;
        box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.4);
    }
    div.stButton > button:first-child:active {
        background-color: #FFEA00 !important;
        color: #121212 !important;
    }
    .metric-box {
        background-color: #1E1E1E;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #37474F;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-val-green { color: #00FF66; font-size: 20px; font-weight: bold; }
    .metric-val-red { color: #FF0055; font-size: 20px; font-weight: bold; }
    .metric-val-blue { color: #2979FF; font-size: 22px; font-weight: bold; }
    .status-badge-green {
        background-color: #1B5E20;
        color: #00FF66;
        padding: 8px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 12px;
        border: 1px solid #00FF66;
    }
    .status-badge-red {
        background-color: #721C24;
        color: #F8D7DA;
        padding: 10px;
        border-radius: 10px;
        text-align: left;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 12px;
        border: 1px solid #F5C6CB;
        line-height: 1.4;
    }
    [data-testid="stForm"] {
        border: 1px solid #37474F !important;
        border-radius: 12px !important;
        background-color: #1E1E1E !important;
        padding: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO Y TÍTULO ---
st.markdown("<h2 style='color: #FFFFFF; margin: 0; padding-top: 2px; font-size: 22px;'>🍜 CALDERÍA SUMAC</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #FFEA00; font-weight: bold; font-size: 11px; margin: 0;'>📍 Sicuani, Canchis • ⚡ POS Nube Persistente</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Panel Lateral de Configuración de Conexión
with st.sidebar:
    st.markdown("### ⚙️ Conexión Nube Google Sheets")
    st.markdown("Las ventas se guardan en tu hoja de cálculo para que NUNCA se borren.")
    url_input = st.text_input(
        "URL de Google Apps Script (/exec):",
        value=st.session_state.get("api_url", ""),
        placeholder="https://script.google.com/macros/s/.../exec"
    )
    if url_input and url_input.strip() != st.session_state.get("api_url", ""):
        st.session_state["api_url"] = url_input.strip()
        if "datos_cache" in st.session_state:
            del st.session_state["datos_cache"]
        st.rerun()

    if st.button("🔌 Restablecer URL por Defecto"):
        st.session_state["api_url"] = API_URL_DEFAULT
        if "datos_cache" in st.session_state:
            del st.session_state["datos_cache"]
        st.rerun()

# --- FUNCIONES DE CONEXIÓN CON GOOGLE SHEETS ---
def post_google_sheets(api_url, payload, timeout=12):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout, allow_redirects=True)
        if response and response.status_code == 200:
            final_url = str(response.url).lower()
            if "accounts.google" in final_url or "servicelogin" in final_url:
                return None
            return response
        return None
    except Exception:
        return None

def cargar_datos_cloud():
    api_url = st.session_state.get("api_url", API_URL_DEFAULT)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(api_url, headers=headers, timeout=10, allow_redirects=True)
        final_url = str(response.url).lower()
        
        if "accounts.google" in final_url or "servicelogin" in final_url:
            st.session_state["conexion_fallida"] = True
            st.session_state["conexion_error_tipo"] = "google_login"
            return None

        if response.status_code == 200:
            content_type = str(response.headers.get("Content-Type", "")).lower()
            if "html" in content_type:
                st.session_state["conexion_fallida"] = True
                st.session_state["conexion_error_tipo"] = "google_login"
                return None
            try:
                rows = response.json()
            except Exception:
                st.session_state["conexion_fallida"] = True
                st.session_state["conexion_error_tipo"] = "json_error"
                return None

            st.session_state["conexion_fallida"] = False
            st.session_state["conexion_error_tipo"] = None
            
            datos_formateados = {"ventas": [], "compras": []}
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    fecha = str(row.get("fecha", ""))
                    type_row = str(row.get("tipo", ""))
                    detalle = str(row.get("detalle", ""))
                    try:
                        monto = float(row.get("monto", 0))
                    except (ValueError, TypeError):
                        monto = 0.0

                    item = {
                        "id": str(time.time_ns() + len(datos_formateados["ventas"]) + len(datos_formateados["compras"])),
                        "fecha": fecha,
                        "sincronizado": True
                    }
                    if type_row == "VENTA":
                        item["producto"] = detalle
                        item["total"] = monto
                        datos_formateados["ventas"].append(item)
                    elif type_row == "GASTO":
                        item["detalle"] = detalle
                        item["monto"] = monto
                        datos_formateados["compras"].append(item)
            return datos_formateados
    except Exception:
        pass

    st.session_state["conexion_fallida"] = True
    st.session_state["conexion_error_tipo"] = "network_error"
    return None

def enviar_a_sheets_bg(api_url, payload, item_id, tipo_mov):
    try:
        response = post_google_sheets(api_url, payload, timeout=12)
        if response is not None and "datos_cache" in st.session_state:
            lista = st.session_state["datos_cache"]["ventas"] if tipo_mov == "VENTA" else st.session_state["datos_cache"]["compras"]
            for item in lista:
                if item.get("id") == item_id:
                    item["sincronizado"] = True
                    break
    except Exception:
        pass

def registrar_movimiento_instantaneo(tipo, detalle, monto):
    api_url = st.session_state["api_url"]
    ahora = datetime.now(timezone.utc) - timedelta(hours=5)
    fecha_hoy = ahora.strftime("%Y-%m-%d %H:%M:%S")
    item_id = str(time.time_ns())
    
    item_nuevo = {
        "id": item_id,
        "fecha": fecha_hoy,
        "sincronizado": False
    }
    if tipo == "VENTA":
        item_nuevo["producto"] = detalle
        item_nuevo["total"] = monto
        st.session_state["datos_cache"]["ventas"].append(item_nuevo)
    elif tipo == "GASTO":
        item_nuevo["detalle"] = detalle
        item_nuevo["monto"] = monto
        st.session_state["datos_cache"]["compras"].append(item_nuevo)
        
    payload = {
        "action": "registrar",
        "fecha": fecha_hoy,
        "tipo": tipo,
        "detalle": detalle,
        "monto": monto
    }
    
    hilo = threading.Thread(target=enviar_a_sheets_bg, args=(api_url, payload, item_id, tipo))
    hilo.start()
    return True

# --- CARGAR DATOS AL INICIAR SESIÓN ---
if "datos_cache" not in st.session_state:
    datos_nuevos = cargar_datos_cloud()
    if datos_nuevos is not None:
        st.session_state["datos_cache"] = datos_nuevos
    else:
        st.session_state["datos_cache"] = {"ventas": [], "compras": []}

datos = st.session_state["datos_cache"]

# --- BARRA DE ESTADO DE CONEXIÓN ---
if st.session_state.get("conexion_fallida", False):
    error_tipo = st.session_state.get("conexion_error_tipo")
    if error_tipo == "google_login":
        st.markdown("""
            <div class='status-badge-red'>
                <strong>⚠️ ATENCIÓN: PERMISO DE GOOGLE SHEETS REQUERIDO</strong><br>
                Tu enlace requiere permisos para guardar en la nube. Para solucionarlo para siempre:<br>
                1. En Google Sheets ➡️ Extensiones ➡️ Apps Script.<br>
                2. Ve a <strong>Implementar ➡️ Administrar implementaciones ➡️ Editar (Lápiz)</strong>.<br>
                3. Cambia <strong>'Quién tiene acceso'</strong> a <strong>'Cualquier persona' (Anyone)</strong>.<br>
                4. Haz clic en Implementar y las ventas quedarán aseguradas en la nube.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-badge-red'>⚠️ MODALIDAD TEMPORAL (Configurar URL en menú lateral para guardar en nube)</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='status-badge-green'>🟢 CONECTADO A GOOGLE SHEETS (Ventas guardadas 100% en la nube)</div>", unsafe_allow_html=True)

# --- CARGADOR ROBUSTO DE IMÁGENES BASE64 ---
def get_image_base64(producto):
    lista = producto.get("alternativas", [producto["imagen"]])
    carpetas = ["", "/workspace/artifacts", "/mount/src/conexi-n-sumac-v3", os.path.dirname(os.path.abspath(__file__))]
    
    ruta_encontrada = None
    for alt in lista:
        for carp in carpetas:
            ruta = os.path.join(carp, alt) if carp else alt
            if os.path.exists(ruta):
                ruta_encontrada = ruta
                break
        if ruta_encontrada:
            break
            
    if not ruta_encontrada:
        return ""
        
    try:
        img = Image.open(ruta_encontrada)
        img.thumbnail((120, 120), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception:
        try:
            with open(ruta_encontrada, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""

# Lista de Productos
PRODUCTOS_INFO = [
    {
        "nombre": "Caldo sin presa",
        "precio": 5.0,
        "icono": "🍲",
        "imagen": "caldo_sin_presa.png",
        "alternativas": ["caldo_sin_presa.png"],
        "lleva_taper": True
    },
    {
        "nombre": "Caldo presa mediana",
        "precio": 8.0,
        "icono": "🍲",
        "imagen": "caldo_presa_mediana.png",
        "alternativas": ["caldo_sicuani.png", "caldo_presa_mediana.png"],
        "lleva_taper": True
    },
    {
        "nombre": "Caldo presa entera",
        "precio": 12.0,
        "icono": "🍲",
        "imagen": "caldo_presa_entera.png",
        "alternativas": ["caldo_presa_grande.png", "caldo_presa_entera.png"],
        "lleva_taper": True
    },
    {
        "nombre": "Gaseosa personal",
        "precio": 3.0,
        "icono": "🥤",
        "imagen": "gaseosas_personales.png",
        "alternativas": ["gaseosas_personales.png", "gaseosa_peruana.png"],
        "lleva_taper": False
    },
    {
        "nombre": "Gaseosa de 1 Litro",
        "precio": 6.0,
        "icono": "🍾",
        "imagen": "gaseosas_litro.png",
        "alternativas": ["gaseosas_litro.png", "gaseosa_litro.png"],
        "lleva_taper": False
    },
    {
        "nombre": "Agua mineral",
        "precio": 2.0,
        "icono": "💧",
        "imagen": "agua_san_luis.png",
        "alternativas": ["agua_san_luis.png"],
        "lleva_taper": False
    }
]

def contar_vendidos_hoy(nombre_base):
    total = 0
    for v in datos.get("ventas", []):
        if nombre_base in v.get("producto", ""):
            total += 1
    return total

# --- PESTAÑAS DE NAVEGACIÓN ---
tab_ventas, tab_gastos, tab_caja = st.tabs(["🛒 Registrar Ventas", "💸 Anotar Gastos", "💼 Ver Caja"])

with tab_ventas:
    st.markdown("<h4 style='color: #CFD8DC;'>Toca la foto para vender:</h4>", unsafe_allow_html=True)
    
    for i, p in enumerate(PRODUCTOS_INFO):
        cant = contar_vendidos_hoy(p["nombre"])
        es_caldo = p.get("lleva_taper", False)
        icono = p.get("icono", "🍲")
        b64_img = get_image_base64(p)
        
        c_img, c_info, c_btn = st.columns([0.30, 0.40, 0.30])
        
        with c_img:
            st.markdown(f"""
            <div id="target-anchor-{i}"></div>
            <style>
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button {{
                background-image: url(data:image/png;base64,{b64_img}) !important;
                background-color: #1E1E1E !important;
                background-repeat: no-repeat !important;
                background-size: cover !important;
                background-position: center !important;
                width: 85px !important;
                height: 85px !important;
                border-radius: 12px !important;
                border: 2px solid #FFEA00 !important;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.5) !important;
                color: transparent !important;
                transition: transform 0.15s ease !important;
                margin: 0 auto !important;
                display: block !important;
            }}
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button:hover {{
                transform: scale(1.06) !important;
                border-color: #00FF66 !important;
            }}
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button:active {{
                transform: scale(0.95) !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("", key=f"btn_img_venda_{i}"):
                if registrar_movimiento_instantaneo("VENTA", p["nombre"], p["precio"]):
                    st.toast(f"🟢 {p['nombre']} (S/. {p['precio']:.2f}) registrado", icon=icono)
                    st.rerun()
                
        with c_info:
            st.markdown(f"""
            <div style='display: flex; flex-direction: column; justify-content: center; height: 85px;'>
                <div style='font-weight: bold; font-size: 13px; color: #FFFFFF;'>{icono} {p['nombre']}</div>
                <div style='color: #FFEA00; font-weight: bold; font-size: 14px; margin-top: 3px;'>S/. {p['precio']:.2f}</div>
                <div style='color: #888888; font-size: 11px; margin-top: 2px;'>Vendido hoy: <b>{cant}</b></div>
            </div>
            """, unsafe_allow_html=True)
                    
        with c_btn:
            if es_caldo:
                if st.button("🥚 Huevo (+S/.1)", key=f"btn_huevo_{i}"):
                    if registrar_movimiento_instantaneo("VENTA", f"{p['nombre']} (+1 huevo)", 1.0):
                        st.toast("🥚 Huevo extra registrado", icon="🥚")
                        st.rerun()
                if st.button("🥃 Táper (+S/.1)", key=f"btn_taper_{i}"):
                    if registrar_movimiento_instantaneo("VENTA", f"{p['nombre']} (en táper)", 1.0):
                        st.toast("🥃 Táper registrado", icon="🥃")
                        st.rerun()

        st.markdown("<div style='border-bottom: 1px solid #222222; margin: 8px 0;'></div>", unsafe_allow_html=True)

    st.markdown("<br><h5 style='color: #CFD8DC;'>📝 Últimos movimientos del turno:</h5>", unsafe_allow_html=True)
    movimientos = []
    for v in datos.get("ventas", []):
        sinc = " ⚡" if not v.get("sincronizado", True) else ""
        movimientos.append((v.get("fecha", ""), f"🟢 VENTA - {v['producto']}{sinc}", v.get("total", 0.0)))
    for c in datos.get("compras", []):
        sinc = " ⚡" if not c.get("sincronizado", True) else ""
        movimientos.append((c.get("fecha", ""), f"🔴 GASTO - {c['detalle']}{sinc}", -c.get("monto", 0.0)))
        
    if movimientos:
        movimientos.reverse()
        for fecha, detalle, monto in movimientos[:15]:
            color_txt = "#00FF66" if "VENTA" in detalle else "#FF0055"
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 8px 12px; border-radius: 8px; margin-bottom: 4px; border-left: 4px solid {color_txt};'><span style='color: #FFFFFF; font-size: 12px; font-weight: bold;'>{detalle}</span><span style='color: {color_txt}; font-size: 12px; font-weight: bold;'>S/. {abs(monto):.2f}</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay movimientos registrados hoy.")

with tab_gastos:
    st.markdown("<h4 style='color: #CFD8DC;'>Anotar un Gasto de Caja:</h4>", unsafe_allow_html=True)
    
    with st.form("form_gastos_sumac", clear_on_submit=True):
        desc_gasto = st.text_input("¿En qué se gastó? (Ej: Gas, Gallinas, Verduras)")
        monto_gasto = st.number_input("Monto gastado (S/.)", min_value=0.0, step=1.0, value=None)
        btn_gasto = st.form_submit_button("💾 Registrar Gasto en Caja")
        
        if btn_gasto:
            if desc_gasto and monto_gasto and monto_gasto > 0:
                if registrar_movimiento_instantaneo("GASTO", desc_gasto, monto_gasto):
                    st.toast(f"🔴 Gasto registrado: {desc_gasto}", icon="💸")
                    st.rerun()
            else:
                st.error("Ingresa una descripción y monto válido.")

    st.markdown("<br><h5 style='color: #CFD8DC;'>📋 Gastos de hoy:</h5>", unsafe_allow_html=True)
    if datos.get("compras"):
        for g in reversed(datos["compras"]):
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 8px 12px; border-radius: 8px; margin-bottom: 4px; border-left: 4px solid #FF0055;'><span style='color: #FFEA00; font-size: 12px; font-weight: bold;'>• {g['detalle']}</span><span style='color: #FF0055; font-size: 12px; font-weight: bold;'>S/. {g['monto']:.2f}</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay gastos registrados hoy.")

with tab_caja:
    st.markdown("<h4 style='text-align: center; color: #CFD8DC;'>💼 Finanzas del Turno</h4>", unsafe_allow_html=True)
    
    if st.button("🔄 Actualizar y Cargar desde Google Sheets", key="btn_sync_caja"):
        datos_frescos = cargar_datos_cloud()
        if datos_frescos is not None:
            st.session_state["datos_cache"] = datos_frescos
            st.success("🔄 ¡Caja sincronizada con éxito!")
            st.rerun()
        else:
            st.error("⚠️ No se pudo conectar a Google Sheets. Verifica los permisos de Apps Script.")

    total_v = sum(v.get("total", 0.0) for v in datos.get("ventas", []))
    total_g = sum(c.get("monto", 0.0) for c in datos.get("compras", []))
    ganancia = total_v - total_g
    
    col_v, col_g = st.columns(2)
    with col_v:
        st.markdown(f"<div class='metric-box'>Ingresos<br><span class='metric-val-green'>S/. {total_v:.2f}</span></div>", unsafe_allow_html=True)
    with col_g:
        st.markdown(f"<div class='metric-box'>Gastos<br><span class='metric-val-red'>S/. {total_g:.2f}</span></div>", unsafe_allow_html=True)
        
    st.markdown(f"<div class='metric-box' style='background: #252525;'>GANANCIA NETA<br><span class='metric-val-blue' style='color: {'#00FF66' if ganancia >= 0 else '#FF0055'}'>S/. {ganancia:.2f}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h5 style='color: #FF0055;'>🧹 Zona de Seguridad</h5>", unsafe_allow_html=True)
    clave_caja = st.text_input("Contraseña:", type="password", key="clave_caja_web")
    if clave_caja == "1992":
        if st.button("⚠️ CONFIRMAR REINICIO DE CAJA"):
            api_url = st.session_state["api_url"]
            try:
                payload = {"action": "reiniciar"}
                response = post_google_sheets(api_url, payload, timeout=10)
                if response and response.status_code == 200:
                    st.session_state["datos_cache"] = {"ventas": [], "compras": []}
                    st.success("¡Base de datos borrada con éxito!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
