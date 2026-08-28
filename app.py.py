import base64
import streamlit as st
import requests
import json
import threading
import os
import re
import time
from datetime import datetime, timedelta, timezone

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
        padding: 10px;
        font-size: 13px;
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

    /* =========================================================================
       SÚPER RE-DISEÑO COMPACTO Y SIMÉTRICO PARA CELULARES (100% COMPATIBLE)
       ========================================================================= */
    /* Forzar que todos los bloques horizontales se mantengan en fila (no colapsen) en celulares */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        align-items: center !important;
    }
    /* Impedir el colapso vertical de las columnas dentro de los bloques horizontales */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 0% !important;
        width: 100% !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Centrar perfectamente cada contenedor de elemento (imagen, descripción, precio) en la recta vertical */
    div[data-testid="column"] div.element-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        width: 100% !important;
    }

    /* Forzar que el Markdown llene todo el ancho y se centre */
    div[data-testid="column"] .stMarkdown {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
    }
    div[data-testid="column"] .stMarkdown > div {
        width: 100% !important;
        text-align: center !important;
    }

    /* Asegurar que el stButton dentro de la columna esté centrado */
    div[data-testid="column"] div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Estilo premium para los botones unificados de modificadores (Huevo / Táper) */
    div.element-container:has(div[id*="egg-anchor-"]) + div.element-container div[data-testid="stButton"] button {
        background-color: #1E1E1E !important;
        color: #00FF66 !important;
        border: 2px solid #00FF66 !important;
        border-radius: 20px !important;
        font-size: 11px !important;
        font-weight: bold !important;
        height: 34px !important;
        line-height: 1 !important;
        padding: 0px 8px !important;
        width: 100% !important;
        box-shadow: 0px 4px 8px rgba(0, 255, 102, 0.15) !important;
        transition: transform 0.1s !important;
    }
    div.element-container:has(div[id*="egg-anchor-"]) + div.element-container div[data-testid="stButton"] button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 6px 12px rgba(0, 255, 102, 0.3) !important;
    }
    div.element-container:has(div[id*="egg-anchor-"]) + div.element-container div[data-testid="stButton"] button:active {
        transform: scale(0.95) !important;
    }

    div.element-container:has(div[id*="taper-anchor-"]) + div.element-container div[data-testid="stButton"] button {
        background-color: #1E1E1E !important;
        color: #2979FF !important;
        border: 2px solid #2979FF !important;
        border-radius: 20px !important;
        font-size: 11px !important;
        font-weight: bold !important;
        height: 34px !important;
        line-height: 1 !important;
        padding: 0px 8px !important;
        width: 100% !important;
        box-shadow: 0px 4px 8px rgba(41, 121, 255, 0.15) !important;
        transition: transform 0.1s !important;
    }
    div.element-container:has(div[id*="taper-anchor-"]) + div.element-container div[data-testid="stButton"] button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 6px 12px rgba(41, 121, 255, 0.3) !important;
    }
    div.element-container:has(div[id*="taper-anchor-"]) + div.element-container div[data-testid="stButton"] button:active {
        transform: scale(0.95) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- REPRODUCTOR DE SONIDO DIGITAL WEB AUDIO API (CHA-CHING) ---
def reproducir_sonido():
    js_sonido = """
    <script>
    try {
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Tono 1 (Monedita de caja registradora)
        var osc1 = audioCtx.createOscillator();
        var gain1 = audioCtx.createGain();
        osc1.type = 'triangle';
        osc1.frequency.setValueAtTime(880, audioCtx.currentTime); // Nota A5
        gain1.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain1.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
        osc1.connect(gain1);
        gain1.connect(audioCtx.destination);
        osc1.start();
        osc1.stop(audioCtx.currentTime + 0.15);
        
        // Tono 2 (Campanazo agudo "ching")
        var osc2 = audioCtx.createOscillator();
        var gain2 = audioCtx.createGain();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(1480, audioCtx.currentTime + 0.08); // Nota aguda brillante
        gain2.gain.setValueAtTime(0.12, audioCtx.currentTime + 0.08);
        gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.38);
        osc2.connect(gain2);
        gain2.connect(audioCtx.destination);
        osc2.start(audioCtx.currentTime + 0.08);
        osc2.stop(audioCtx.currentTime + 0.38);
    } catch(e) {
        console.log("AudioContext bloqueado o no soportado:", e);
    }
    </script>
    """
    st.components.v1.html(js_sonido, height=0, width=0)

# --- ENCABEZADO INTEGRADO PREMIUM (LOGO EN CACHÉ DE SESIÓN PARA MÁXIMA VELOCIDAD) ---
if "logo_path" not in st.session_state:
    logo_path = None
    for l in ["yauri_cloud_logo_final.png", "yauri_cloud_logo_rectangular.png", "yauri_cloud_logo_futuristic_1.png"]:
        if os.path.exists(l):
            logo_path = l
            break
        elif os.path.exists(os.path.join("/workspace/artifacts", l)):
            logo_path = os.path.join("/workspace/artifacts", l)
            break
    st.session_state["logo_path"] = logo_path

col_logo, col_titulo = st.columns([0.45, 3.55])

with col_logo:
    if st.session_state.get("logo_path"):
        try:
            st.image(st.session_state["logo_path"], width=64)
        except Exception:
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

# --- FUNCIÓN DE CONVERSIÓN DE FECHA OPTIMIZADA ---
def obtener_datetime_sort(fecha_str):
    if not fecha_str:
        return datetime.min
    try:
        clean_str = fecha_str.replace("T", " ").replace("Z", "").strip()
        clean_str = re.sub(r"([+-]\d{2}:?\\d{2})\$", "", clean_str)
        
        formatos = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M"
        ]
        for fmt in formatos:
            try:
                return datetime.strptime(clean_str, fmt)
            except ValueError:
                pass
            try:
                return datetime.strptime(clean_str[:len(datetime.now().strftime(fmt))], fmt)
            except ValueError:
                pass
                
        numbers = re.findall(r"\d+", clean_str)
        if len(numbers) >= 5:
            if len(numbers) == 4:
                return datetime(int(numbers), int(numbers), int(numbers), int(numbers), int(numbers))
            else:
                return datetime(int(numbers), int(numbers), int(numbers), int(numbers), int(numbers))
    except Exception:
        pass
    return datetime.min

# --- SISTEMA DE BASES DE DATOS CLOUD CON CACHÉ INTELIGENTE Y PRE-PARSEO DE FECHAS ---
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
                parsed_dt = obtener_datetime_sort(fecha)
                
                if tipo == "VENTA":
                    datos_formateados["ventas"].append({
                        "fecha": fecha,
                        "producto": detalle,
                        "total": monto,
                        "dt": parsed_dt
                    })
                elif tipo == "GASTO":
                    datos_formateados["compras"].append({
                        "fecha": fecha,
                        "detalle": detalle,
                        "monto": monto,
                        "dt": parsed_dt
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
    # ... Sicuani (Perú) UTC-5
    ahora = datetime.now(timezone.utc) - timedelta(hours=5)
    fecha_hoy = ahora.strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Registrar LOCALMENTE en la memoria (caché)
    if tipo == "VENTA":
        st.session_state["datos_cache"]["ventas"].append({
            "fecha": fecha_hoy,
            "producto": detalle,
            "total": monto,
            "dt": ahora
        })
    elif tipo == "GASTO":
        st.session_state["datos_cache"]["compras"].append({
            "fecha": fecha_hoy,
            "detalle": detalle,
            "monto": monto,
            "dt": ahora
        })
        
    # 2. Disparar el envío a Google Sheets asíncronamente
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

# Sincronización de caché
if "datos_cache" not in st.session_state:
    with st.spinner("🔌 Conectando con la Caja Consolidada..."):
        st.session_state["datos_cache"] = cargar_datos_cloud()

datos = st.session_state["datos_cache"]

# Menú de Productos de Caldería Sumac con rutas de imagen reales
PRODUCTOS_INFO = [
    {"nombre": "Caldo sin presa", "precio": 5.0, "icono": "🍲", "imagen": "caldo_sin_presa.png", "lleva_taper": True},
    {"nombre": "Caldo presa mediana", "precio": 8.0, "icono": "🍲", "imagen": "caldo_sicuani.png", "lleva_taper": True},
    {"nombre": "Caldo presa entera", "precio": 12.0, "icono": "🍲", "imagen": "caldo_presa_grande.png", "lleva_taper": True},
    {"nombre": "Gaseosa personal", "precio": 2.0, "icono": "🥤", "imagen": "gaseosas_personales.png", "lleva_taper": False},
    {"nombre": "Gaseosa de 1 Litro", "precio": 6.0, "icono": "🍾", "imagen": "gaseosas_litro.png", "lleva_taper": False},
    {"nombre": "Agua mineral", "precio": 1.0, "icono": "💧", "imagen": "agua_san_luis.png", "lleva_taper": False}
]

# Inicializar estado de sonido
if "reproducir_sonido" not in st.session_state:
    st.session_state["reproducir_sonido"] = False

# Helper para contar ventas consolidadas hoy por producto o detalle
def contar_vendidos_hoy(nombre_base):
    total = 0
    for v in datos["ventas"]:
        if nombre_base in v.get("producto", ""):
            total += 1
    return total

# --- FUNCIÓN SUPER ROBUSTA Y OPTIMIZADA PARA OBTENER BASE64 DE IMAGEN EN CUALQUIER ENTORNO ---
@st.cache_data
def get_image_base64(img_path):
    import base64
    import os
    from PIL import Image
    import io
    
    if not img_path:
        return ""
    
    posibles_rutas = [
        img_path,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), img_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", img_path),
        os.path.join("/workspace/artifacts", img_path),
        os.path.join("/workspace/scratch", img_path),
        os.path.join("/mount/src/conexi-n-sumac-v3", img_path)
    ]
    
    ruta_encontrada = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            ruta_encontrada = ruta
            break
            
    if not ruta_encontrada:
        fallback_map = {
            "caldo_sin_presa.png": "caldo_presa_grande.png",
            "caldo_sicuani.png": "caldo_presa_grande.png",
            "agua_san_luis.png": "gaseosas_personales.png"
        }
        fallback_name = fallback_map.get(os.path.basename(img_path))
        if fallback_name:
            for ruta in posibles_rutas:
                ruta_dir = os.path.dirname(ruta)
                ruta_fallback = os.path.join(ruta_dir, fallback_name) if ruta_dir else fallback_name
                if os.path.exists(ruta_fallback):
                    ruta_encontrada = ruta_fallback
                    break

    if not ruta_encontrada:
        return ""
        
    try:
        img = Image.open(ruta_encontrada)
        img.thumbnail((120, 120), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        try:
            with open(ruta_encontrada, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return "" 


# --- ESTADO INICIAL DEL SPLASH SCREEN (CONFIGURADO A 3 SEGUNDOS EXACTOS) ---
if "splash_done" not in st.session_state:
    st.session_state["splash_done"] = False

def render_splash():
    import base64
    from PIL import Image
    import io
    
    b64_logo = ""
    logo_path = st.session_state.get("logo_path")
    if logo_path:
        try:
            img = Image.open(logo_path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64_logo = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception:
            pass
            
    splash_html = f"""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #121212;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999999;
    ">
        <div style="text-align: center; animation: pulse 1.5s infinite alternate;">
            {f'<img src="data:image/png;base64,{b64_logo}" style="width: 180px; height: auto; border-radius: 20px; box-shadow: 0px 8px 25px rgba(255, 234, 0, 0.35); border: 2px solid #37474F;" />' if b64_logo else '<h1 style="color: #FFEA00; font-family: sans-serif; font-size: 28px;">⚡ YAURI CLOUD</h1>'}
            <div style="margin-top: 25px; color: #FFFFFF; font-family: sans-serif; font-size: 18px; font-weight: bold; letter-spacing: 2px;">
                YAURI CLOUD
            </div>
            <div style="margin-top: 5px; color: #888888; font-family: sans-serif; font-size: 12px; letter-spacing: 1px;">
                Cargando Caldería Sumac...
            </div>
            <div style="margin-top: 20px; display: inline-block; width: 40px; height: 40px; border: 3px solid rgba(255, 234, 0, 0.2); border-radius: 50%; border-top-color: #FFEA00; animation: spin 0.8s linear infinite;"></div>
        </div>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.98); }}
        100% {{ transform: scale(1.02); }}
    }}
    body {{
        overflow: hidden !important;
    }}
    </style>
    """
    st.markdown(splash_html, unsafe_allow_html=True)

if not st.session_state["splash_done"]:
    render_splash()
    
    # Pre-cache de imágenes base64 para acelerar al máximo el renderizado
    if "imagenes_base64" not in st.session_state:
        st.session_state["imagenes_base64"] = {}
    for p in PRODUCTOS_INFO:
        img_n = p["imagen"]
        if img_n not in st.session_state["imagenes_base64"]:
            st.session_state["imagenes_base64"][img_n] = get_image_base64(img_n)
            
    # Duración de 3 segundos reales solicitados por el usuario
    time.sleep(3.0)
    st.session_state["splash_done"] = True
    st.rerun()

# Asegurar que el cache esté cargado
if "imagenes_base64" not in st.session_state or len(st.session_state["imagenes_base64"]) == 0:
    st.session_state["imagenes_base64"] = {}
    for p in PRODUCTOS_INFO:
        img_n = p["imagen"]
        st.session_state["imagenes_base64"][img_n] = get_image_base64(img_n)

# Función súper robusta para extraer la hora (HH:MM AM/PM) de cualquier formato de fecha
def extraer_hora(fecha_str):
    if not fecha_str:
        return "--:--"
    try:
        clean_str = fecha_str.replace("T", " ").replace("Z", "")
        clean_str = re.sub(r"([+-]\\d{2}:?\\\\d{2})$", "", clean_str)
        
        if len(clean_str) > 16:
            dt = datetime.strptime(clean_str[:19], "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(clean_str[:16], "%Y-%m-%d %H:%M")
            
        is_utc = False
        if "Z" in fecha_str or "+00" in fecha_str or "GMT" in fecha_str:
            is_utc = True
        else:
            ahora_peru = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=5)
            if dt > ahora_peru + timedelta(hours=1):
                is_utc = True
                
        if is_utc:
            dt = dt - timedelta(hours=5)
    except Exception:
        match = re.search(r"(\\d{1,2}):(\\d{2})", fecha_str)
        if match:
            hh = int(match.group(1))
            mm = match.group(2)
            ampm = "PM" if hh >= 12 else "AM"
            hh_12 = hh % 12
            if hh_12 == 0:
                hh_12 = 12
            return f"{hh_12:02d}:{mm} {ampm}"
        return fecha_str
    
    return dt.strftime("%I:%M %p")

# Pestañas de navegación móvil cómoda en la parte superior
tab_ventas, tab_gastos, tab_caja = st.tabs(["🛒 Registrar Ventas", "💸 Anotar Gastos", "💼 Ver Caja"])

with tab_ventas:
    st.markdown("<h4 style='color: #CFD8DC;'>Selecciona para vender:</h4>", unsafe_allow_html=True)
    
    # Cada producto ocupa una fila completa para evitar colapsos y amontonamientos en móvil
    for i, p in enumerate(PRODUCTOS_INFO):
        cant = contar_vendidos_hoy(p["nombre"])
        es_caldo = p.get("lleva_taper", False)
        icono = p.get("icono", "🍲")
        
        # Siempre dividimos horizontalmente usando la proporción exacta [0.65, 0.35]
        st.markdown(f'<div id="sub-anchor-{i}"></div>', unsafe_allow_html=True)
        sub_left, sub_right = st.columns([0.65, 0.35])
            
        with sub_left:
            b64_img = st.session_state.get("imagenes_base64", {}).get(p["imagen"], "")
            if not b64_img:
                b64_img = get_image_base64(p["imagen"])
                
            st.markdown(f"""
            <div id="target-anchor-{i}"></div>
            <style>
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] {{
                display: flex !important;
                justify-content: center !important;
            }}
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button {{
                background-image: url(data:image/png;base64,{b64_img}) !important;
                background-color: transparent !important;
                background-repeat: no-repeat !important;
                background-size: cover !important;
                background-position: center !important;
                width: 95px !important;
                height: 95px !important;
                border-radius: 15px !important;
                border: 1px solid #37474F !important;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5) !important;
                color: transparent !important;
                overflow: hidden !important;
                transition: transform 0.2s, box-shadow 0.2s !important;
                display: block !important;
                margin: 0 auto 3px auto !important;
            }}
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button:hover {{
                transform: scale(1.05) !important;
                box-shadow: 0px 6px 15px rgba(255, 234, 0, 0.4) !important;
                border-color: #FFEA00 !important;
            }}
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button:active {{
                transform: scale(0.98) !important;
            }}
            div.element-container:has(#target-anchor-{i}) + div.element-container div[data-testid="stButton"] button * {{
                display: none !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            # Botón nativo clickable de Caldo o Bebida
            if st.button("", key=f"btn_sell_caldo_{i}"):
                if registrar_movimiento_instantaneo("VENTA", p["nombre"], p["precio"]):
                    st.toast(f"🟢 Venta registrada: {p['nombre']}", icon=icono)
                    st.session_state["reproducir_sonido"] = True
                    st.rerun()
            
            # Descripción centrada súper compacta en la misma recta del botón
            st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 12px; line-height: 1.1; margin-top: -2px;'>{icono} {p['nombre']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #FFEA00; font-weight: bold; font-size: 11px; margin: 0; padding-bottom: 2px;'>S/. {p['precio']:.2f} <span style='color: #888888; font-weight: normal; margin-left: 3px;'>• Hoy: {cant}</span></p>", unsafe_allow_html=True)
            
        with sub_right:
            if es_caldo:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # --- MODIFICADOR HUEVO EXTRA (🥚 S/.1.0) ---
                st.markdown(f'<div id="egg-anchor-{i}"></div>', unsafe_allow_html=True)
                if st.button("🥚 S/.1.0", key=f"btn_h_indep_{i}"):
                    nombre_huevo = f"{p['nombre']} (+1 huevo)"
                    if registrar_movimiento_instantaneo("VENTA", nombre_huevo, 1.0):
                        st.toast(f"🥚 +1 Huevo registrado", icon="🥚")
                        st.session_state["reproducir_sonido"] = True
                        st.rerun()
                        
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # --- MODIFICADOR TÁPER (🥃 S/.1.0) ---
                st.markdown(f'<div id="taper-anchor-{i}"></div>', unsafe_allow_html=True)
                if st.button("🥃 S/.1.0", key=f"btn_t_indep_{i}"):
                    nombre_taper = f"{p['nombre']} (en táper)"
                    if registrar_movimiento_instantaneo("VENTA", nombre_taper, 1.0):
                        st.toast(f"🥃 +1 Táper registrado", icon="🥃")
                        st.session_state["reproducir_sonido"] = True
                        st.rerun()
            else:
                st.write("")
                
        # Una pequeña línea separadora sutil para diferenciar filas
        st.markdown("<div style='border-bottom: 1px solid #222222; margin: 10px 0;'></div>", unsafe_allow_html=True)

    # Lanzador de sonido
    if st.session_state["reproducir_sonido"]:
        reproducir_sonido()
        st.session_state["reproducir_sonido"] = False

    st.markdown("<br><h5 style='color: #CFD8DC;'>📝 Últimos movimientos del turno (Lista de registro):</h5>", unsafe_allow_html=True)
    
    movimientos = []
    for v in datos["ventas"]:
        movimientos.append((v.get("dt", datetime.min), v["fecha"], f"🟢 VENTA - {v['producto']}", v["total"]))
    for c in datos["compras"]:
        movimientos.append((c.get("dt", datetime.min), c["fecha"], f"🔴 GASTO - {c['detalle']}", -c["monto"]))
        
    if movimientos:
        try:
            # Ordenamos cronológicamente en memoria ultra-rápida (dt pre-parseado, cero delay)
            movimientos.sort(key=lambda x: x, reverse=True)
        except Exception:
            movimientos.reverse()
        for dt_obj, fecha, detalle, monto in movimientos:
            color_txt = "#00FF66" if "VENTA" in detalle else "#FF0055"
            hora = extraer_hora(fecha)
            st.markdown(f"<!-- {fecha} --><div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid {color_txt};'><span style='color: #FFFFFF; font-weight: bold;'>{detalle}</span><span style='color: {color_txt}; font-weight: bold;'>S/. {abs(monto):.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay movimientos registrados hoy.")

with tab_gastos:
    st.markdown("<h4 style='color: #CFD8DC;'>Anotar un Gasto de Caja:</h4>", unsafe_allow_html=True)
    
    with st.form("formulario_gastos_sumac", clear_on_submit=True):
        desc_gasto = st.text_input("¿En qué se gastó? (Ej: Gas, Gallinas, Verduras)")
        monto_gasto = st.number_input("Monto gastado (S/.)", min_value=0.0, step=1.0, value=None)
        
        btn_registrar = st.form_submit_button("💾 Registrar Gasto en Caja")
        
        if btn_registrar:
            if desc_gasto and monto_gasto is not None and monto_gasto > 0:
                if registrar_movimiento_instantaneo("GASTO", desc_gasto, monto_gasto):
                    st.toast(f"🔴 Gasto registrado: {desc_gasto} (S/. {monto_gasto:.2f})", icon="💸")
                    st.session_state["reproducir_sonido"] = True
                    st.rerun()
            else:
                st.error("Por favor ingresa una descripción y un monto válido.")

    st.markdown("<br><h5 style='color: #CFD8DC;'>📋 Gastos de hoy registrados:</h5>", unsafe_allow_html=True)
    if datos["compras"]:
        gastos_hoy = datos["compras"]
        try:
            gastos_hoy_sorted = sorted(gastos_hoy, key=lambda x: x.get("dt", datetime.min), reverse=True)
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
