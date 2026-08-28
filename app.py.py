import streamlit as st
import requests
import json
import threading
import os
import re
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

# --- ENCABEZADO INTEGRADO PREMIUM (LOGO "YAURI CLOUD" MINI AL 40% EN LA ESQUINA SUPERIOR IZQUIERDA) ---
col_logo, col_titulo = st.columns([0.45, 3.55])

with col_logo:
    try:
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
                    # Si es un gasto de planilla encubierto (compatibilidad hacia atrás)
                    if "PLANILLA" in detalle or "🧑‍🍳 PLANILLA" in detalle:
                        datos_formateados["planilla"].append({
                            "fecha": fecha,
                            "detalle": detalle,
                            "monto": monto
                        })
                    else:
                        datos_formateados["compras"].append({
                            "fecha": fecha,
                            "detalle": detalle,
                            "monto": monto
                        })
                elif tipo == "PLANILLA":
                    datos_formateados["planilla"].append({
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
    # Obtener la hora actual de Sicuani (Perú) que es UTC-5 de forma 100% segura
    fecha_hoy = (datetime.now(timezone.utc) - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
    
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
    elif tipo == "PLANILLA":
        st.session_state["datos_cache"]["planilla"].append({
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

# Sincronización de caché
if "datos_cache" not in st.session_state:
    with st.spinner("🔌 Conectando con la Caja Consolidada..."):
        st.session_state["datos_cache"] = cargar_datos_cloud()

datos = st.session_state["datos_cache"]

# Inicializar estado de sonido de forma segura para evitar KeyErrors
if "reproducir_sonido" not in st.session_state:
    st.session_state["reproducir_sonido"] = False

# Menú de Productos de Caldería Sumac con rutas de imagen reales
PRODUCTOS_INFO = [
    {"nombre": "Caldo sin presa", "precio": 5.0, "icono": "🍲", "imagen": "caldo_sin_presa.png", "lleva_taper": True},
    {"nombre": "Caldo presa mediana", "precio": 8.0, "icono": "🍲", "imagen": "caldo_sicuani.png", "lleva_taper": True},
    {"nombre": "Caldo presa entera", "precio": 12.0, "icono": "🍲", "imagen": "caldo_presa_grande.png", "lleva_taper": True},
    {"nombre": "Gaseosa personal", "precio": 2.0, "icono": "🥤", "imagen": "gaseosas_personales.png", "lleva_taper": False},
    {"nombre": "Gaseosa de 1 Litro", "precio": 6.0, "icono": "🍾", "imagen": "gaseosas_litro.png", "lleva_taper": False},
    {"nombre": "Agua mineral", "precio": 1.0, "icono": "💧", "imagen": "agua_san_luis.png", "lleva_taper": False}
]

# Helper para contar ventas consolidadas hoy por producto o detalle
def contar_vendidos_hoy(nombre_base):
    total = 0
    for v in datos["ventas"]:
        if nombre_base in v.get("producto", ""):
            total += 1
    return total

# Función súper robusta para convertir cualquier formato de fecha a objeto datetime real
def obtener_datetime_sort(fecha_str):
    if not fecha_str:
        return datetime.min
    try:
        # Limpiar caracteres ISO y offset de zona horaria (Z, +00:00, etc.)
        clean_str = fecha_str.replace("T", " ").replace("Z", "").strip()
        clean_str = re.sub(r"([+-]\d{2}:?\d{2})$", "", clean_str)
        
        # Intentar múltiples formatos comunes de fecha
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
                # Recortar cadena de texto al tamaño esperado por el formato
                return datetime.strptime(clean_str[:len(datetime.now().strftime(fmt))], fmt)
            except ValueError:
                pass
                
        # Regex de emergencia para buscar bloques numéricos
        numbers = re.findall(r"\d+", clean_str)
        if len(numbers) >= 5:
            if len(numbers) == 4: # Año primero (YYYY-MM-DD)
                return datetime(int(numbers), int(numbers), int(numbers), int(numbers), int(numbers))
            else: # Día primero (DD-MM-YYYY)
                return datetime(int(numbers), int(numbers), int(numbers), int(numbers), int(numbers))
    except Exception:
        pass
    return datetime.min

# Función súper robusta para extraer la hora (HH:MM AM/PM) de cualquier formato de fecha
def extraer_hora(fecha_str):
    if not fecha_str:
        return "--:--"
    try:
        # Limpiar caracteres ISO y offset de zona horaria (Z, +00:00, etc.)
        clean_str = fecha_str.replace("T", " ").replace("Z", "")
        clean_str = re.sub(r"([+-]\d{2}:?\d{2})$", "", clean_str)
        
        if len(clean_str) > 16:
            dt = datetime.strptime(clean_str[:19], "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(clean_str[:16], "%Y-%m-%d %H:%M")
            
        # Determinar si está en UTC
        is_utc = False
        if "Z" in fecha_str or "+00" in fecha_str or "GMT" in fecha_str:
            is_utc = True
        else:
            # Si no tiene etiqueta pero la hora está en el futuro en comparación con Perú (UTC-5),
            # entonces la fecha de Sheets viene en formato UTC naive.
            # Sicuani (Perú) es UTC-5:
            ahora_peru = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=5)
            if dt > ahora_peru + timedelta(hours=1):
                is_utc = True
                
        if is_utc:
            dt = dt - timedelta(hours=5)
    except Exception:
        # Fallback de emergencia por regex con formato AM/PM
        match = re.search(r"(\d{1,2}):(\d{2})", fecha_str)
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
tab_ventas, tab_gastos, tab_personal, tab_caja = st.tabs([
    "🛒 Registrar Ventas", 
    "💸 Anotar Gastos", 
    "🧑‍🍳 Pago Personal", 
    "💼 Ver Caja"
])

with tab_ventas:
    st.markdown("<h4 style='color: #CFD8DC;'>Selecciona para vender:</h4>", unsafe_allow_html=True)
    
    # Grid de imágenes de producto y botones de venta de 2 en 2
    for i in range(0, len(PRODUCTOS_INFO), 2):
        col1, col2 = st.columns(2)
        
        # ---- PRODUCTO 1 ----
        p1 = PRODUCTOS_INFO[i]
        with col1:
            # 1. Imagen del Producto
            if "imagen" in p1 and os.path.exists(p1["imagen"]):
                st.image(p1["imagen"], width=110)
                
            cant1 = contar_vendidos_hoy(p1["nombre"])
            es_caldo1 = p1.get("lleva_taper", False)
            
            # 2. Descripción del Caldo y su Valor (Limpio de Horas molestas)
            st.markdown(f"**🍲 {p1['nombre']}**")
            st.markdown(f"<p style='color: #FFEA00; font-weight: bold; font-size: 13px; margin: 0; padding-bottom: 5px;'>S/. {p1['precio']:.2f}</p>", unsafe_allow_html=True)
            
            # 3. Botón de Caldo Base (Registra de manera independiente al instante)
            label_p1 = f"🛒 Registrar Caldo\n[ S/. {p1['precio']:.2f} | Hoy: {cant1} ]"
            if st.button(label_p1, key=f"btn_sell_caldo_{i}"):
                if registrar_movimiento_instantaneo("VENTA", p1["nombre"], p1["precio"]):
                    st.toast(f"🟢 Venta registrada: {p1['nombre']}", icon="🍲")
                    st.session_state["reproducir_sonido"] = True
                    st.rerun()
            
            # 4. Botones de Modificadores (Registro directo y asociado exactamente al caldo correspondiente)
            if es_caldo1:
                st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                
                # Botón independiente de Huevo Extra (Registra directamente al tocar la ➕)
                col_btn_h, col_txt_h = st.columns([0.4, 0.6])
                with col_btn_h:
                    if st.button("➕", key=f"btn_h_indep_{i}"):
                        nombre_huevo = f"{p1['nombre']} (+1 huevo)"
                        if registrar_movimiento_instantaneo("VENTA", nombre_huevo, 1.0):
                            st.toast(f"🥚 +1 Huevo registrado", icon="🥚")
                            st.session_state["reproducir_sonido"] = True
                            st.rerun()
                with col_txt_h:
                    st.markdown("<span style='font-size: 26px; vertical-align: middle;'>🥚</span> <span style='font-size: 13px; color: #00FF66; font-weight: bold; vertical-align: middle;'>Huevo S/. 1.00</span>", unsafe_allow_html=True)
                
                # Botón independiente de Táper de Litro (Asociado al Caldo actual)
                col_btn_t, col_txt_t = st.columns([0.4, 0.6])
                with col_btn_t:
                    if st.button("➕", key=f"btn_t_indep_{i}"):
                        nombre_taper = f"{p1['nombre']} (en táper)"
                        if registrar_movimiento_instantaneo("VENTA", nombre_taper, 1.0):
                            st.toast(f"🛍️ +1 Táper registrado", icon="🛍️")
                            st.session_state["reproducir_sonido"] = True
                            st.rerun()
                with col_txt_t:
                    st.markdown("<span style='font-size: 24px; vertical-align: middle;'>🛍️</span> <span style='font-size: 13px; color: #00FF66; font-weight: bold; vertical-align: middle;'>Táper S/. 1.00</span>", unsafe_allow_html=True)
                
        # ---- PRODUCTO 2 ----
        if i + 1 < len(PRODUCTOS_INFO):
            p2 = PRODUCTOS_INFO[i+1]
            with col2:
                if "imagen" in p2 and os.path.exists(p2["imagen"]):
                    st.image(p2["imagen"], width=110)
                    
                cant2 = contar_vendidos_hoy(p2["nombre"])
                es_caldo2 = p2.get("lleva_taper", False)
                
                # Descripción del Producto
                icono_p2 = p2.get("icono", "🥤")
                st.markdown(f"**{icono_p2} {p2['nombre']}**")
                st.markdown(f"<p style='color: #FFEA00; font-weight: bold; font-size: 13px; margin: 0; padding-bottom: 5px;'>S/. {p2['precio']:.2f}</p>", unsafe_allow_html=True)
                
                # Botón Base
                if es_caldo2:
                    label_p2 = f"🛒 Registrar Caldo\n[ S/. {p2['precio']:.2f} | Hoy: {cant2} ]"
                else:
                    label_p2 = f"🛒 Registrar {icono_p2}\n[ S/. {p2['precio']:.2f} | Hoy: {cant2} ]"
                    
                if st.button(label_p2, key=f"btn_sell_caldo_{i+1}"):
                    if registrar_movimiento_instantaneo("VENTA", p2["nombre"], p2["precio"]):
                        st.toast(f"🟢 Venta registrada: {p2['nombre']}", icon=icono_p2)
                        st.session_state["reproducir_sonido"] = True
                        st.rerun()
                
                # Botones de Modificadores (Asociados al Caldo correspondiente)
                if es_caldo2:
                    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                    
                    # Botón independiente de Huevo Extra
                    col_btn_h2, col_txt_h2 = st.columns([0.4, 0.6])
                    with col_btn_h2:
                        if st.button("➕", key=f"btn_h_indep_{i+1}"):
                            nombre_huevo = f"{p2['nombre']} (+1 huevo)"
                            if registrar_movimiento_instantaneo("VENTA", nombre_huevo, 1.0):
                                st.toast(f"🥚 +1 Huevo registrado", icon="🥚")
                                st.session_state["reproducir_sonido"] = True
                                st.rerun()
                    with col_txt_h2:
                        st.markdown("<span style='font-size: 24px; vertical-align: middle;'>🥚</span> <span style='font-size: 13px; color: #00FF66; font-weight: bold; vertical-align: middle;'>Huevo S/. 1.00</span>", unsafe_allow_html=True)
                    
                    # Botón independiente de Táper de Litro
                    col_btn_t2, col_txt_t2 = st.columns([0.4, 0.6])
                    with col_btn_t2:
                        if st.button("➕", key=f"btn_t_indep_{i+1}"):
                            nombre_taper = f"{p2['nombre']} (en táper)"
                            if registrar_movimiento_instantaneo("VENTA", nombre_taper, 1.0):
                                st.toast(f"🛍️ +1 Táper registrado", icon="🛍️")
                                st.session_state["reproducir_sonido"] = True
                                st.rerun()
                    with col_txt_t2:
                        st.markdown("<span style='font-size: 24px; vertical-align: middle;'>🛍️</span> <span style='font-size: 13px; color: #00FF66; font-weight: bold; vertical-align: middle;'>Táper S/. 1.00</span>", unsafe_allow_html=True)

    # Lanzador de sonido
    if st.session_state["reproducir_sonido"]:
        reproducir_sonido()
        st.session_state["reproducir_sonido"] = False

    st.markdown("<br><h5 style='color: #CFD8DC;'>📝 Últimos movimientos del turno (Lista de registro):</h5>", unsafe_allow_html=True)
    
    movimientos = []
    for v in datos["ventas"]:
        movimientos.append((v["fecha"], f"🟢 VENTA - {v['producto']}", v["total"]))
    for c in datos["compras"]:
        movimientos.append((c["fecha"], f"🔴 GASTO - {c['detalle']}", -c["monto"]))
    for p in datos.get("planilla", []):
        movimientos.append((p["fecha"], f"👤 PLANILLA - {p['detalle']}", -p["monto"]))
        
    if movimientos:
        try:
            # Ordenamos cronológicamente de fin a inicio (el más nuevo primero) usando datetime real
            movimientos.sort(key=lambda x: obtener_datetime_sort(x[0]), reverse=True)
        except Exception:
            # Si falla, simplemente revertimos el orden de registro original (Sheets los entrega de inicio a fin)
            movimientos.reverse()
            
        for fecha, detalle, monto in movimientos[:6]:
            if "VENTA" in detalle:
                color_txt = "#00FF66"
            elif "PLANILLA" in detalle:
                color_txt = "#FFEA00"
            else:
                color_txt = "#FF0055"
            hora = extraer_hora(fecha)
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid {color_txt};'><span style='color: #FFFFFF; font-weight: bold;'>{detalle}</span><span style='color: {color_txt}; font-weight: bold;'>S/. {abs(monto):.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay movimientos registrados hoy.")

with tab_gastos:
    st.markdown("<h4 style='color: #CFD8DC;'>Anotar un Gasto de Caja:</h4>", unsafe_allow_html=True)
    
    # Formulario inteligente con autolimpieza nativa segura y campo vaciado por defecto (value=None)
    with st.form("formulario_gastos_sumac", clear_on_submit=True):
        desc_gasto = st.text_input("¿En qué se gastó? (Ej: Gas, Verduras, Limpieza)")
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

    # --- SECCIÓN DE COMPRA DE STOCK (MAYORISTA) ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📦 Registrar Compra de Stock (Mayorista - Almacén)"):
        st.markdown("<p style='font-size: 12px; color: #CFD8DC;'>Registra las gallinas o paquetes de fideo que ingresan al depósito:</p>", unsafe_allow_html=True)
        insumo_tipo = st.selectbox("Seleccionar insumo de Stock:", ["Gallinas (Caja/Unidades)", "Fideos (Paquetes)"])
        
        if insumo_tipo == "Gallinas (Caja/Unidades)":
            cant_gallinas = st.number_input("Cantidad de gallinas (unidades)", min_value=1, step=1, value=10)
            costo_unidad = st.number_input("Costo promedio por unidad (S/.)", min_value=1.0, value=40.0)
            costo_g_total = cant_gallinas * costo_unidad
            st.markdown(f"**Costo Total de Inversión: S/. {costo_g_total:.2f}**")
            
            if st.button("💾 Registrar Ingreso de Gallinas", key="btn_comprar_gallinas"):
                detalle_compra = f"📦 COMPRA STOCK - Gallinas: {cant_gallinas} unidades"
                if registrar_movimiento_instantaneo("GASTO", detalle_compra, costo_g_total):
                    st.success(f"¡Ingresadas {cant_gallinas} Gallinas al almacén por S/. {costo_g_total:.2f}!")
                    st.session_state["reproducir_sonido"] = True
                    st.rerun()
                    
        else:
            cant_fideos = st.number_input("Cantidad de paquetes de fideo", min_value=1, step=1, value=5)
            costo_paquete = st.number_input("Costo por paquete (S/.)", min_value=1.0, value=15.0)
            costo_f_total = cant_fideos * costo_paquete
            # Cada paquete rinde aproximadamente 20 porciones individuales de caldo
            porciones_estimadas = cant_fideos * 20
            st.markdown(f"**Costo Total de Inversión: S/. {costo_f_total:.2f}**")
            st.markdown(f"<span style='color: #00FF66; font-size: 12px;'>Rendimiento estimado: ~{porciones_estimadas} porciones de caldo</span>", unsafe_allow_html=True)
            
            if st.button("💾 Registrar Ingreso de Fideos", key="btn_comprar_fideos"):
                detalle_compra = f"📦 COMPRA STOCK - Fideos: {cant_fideos} paquetes"
                if registrar_movimiento_instantaneo("GASTO", detalle_compra, costo_f_total):
                    st.success(f"¡Ingresados {cant_fideos} Paquetes de fideo al almacén por S/. {costo_f_total:.2f}!")
                    st.session_state["reproducir_sonido"] = True
                    st.rerun()

    st.markdown("<br><h5 style='color: #CFD8DC;'>📋 Gastos de hoy registrados:</h5>", unsafe_allow_html=True)
    if datos["compras"]:
        gastos_hoy = datos["compras"]
        try:
            # Ordenar los gastos de más reciente a más antiguo
            gastos_hoy_sorted = sorted(gastos_hoy, key=lambda x: obtener_datetime_sort(x["fecha"]), reverse=True)
        except:
            gastos_hoy_sorted = gastos_hoy
            
        for g in gastos_hoy_sorted[:6]:
            fecha = g.get("fecha", "")
            hora = extraer_hora(fecha)
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #FF0055;'><span style='color: #FFEA00; font-weight: bold;'>• {g['detalle']}</span><span style='color: #FF0055; font-weight: bold;'>S/. {g['monto']:.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay gastos registrados hoy.")

with tab_personal:
    st.markdown("<h4 style='color: #CFD8DC;'>🧑‍🍳 Registro de Planilla y Jornales</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; color: #888;'>Administra el pago diario y adelantos de tu equipo de trabajo según las tarifas locales de Cusco:</p>", unsafe_allow_html=True)
    
    # Selector de roles con valores sugeridos de mercado de Sicuani
    rol_seleccionado = st.selectbox("Seleccione el rol del personal:", [
        "Cocinera Principal",
        "Ayudante de Cocina",
        "Mozo",
        "Personal de Limpieza",
        "Otro (Personalizado)"
    ])
    
    # Establecer sueldos sugeridos en base a la investigación de Sicuani
    if rol_seleccionado == "Cocinera Principal":
        sueldo_sugerido = 55.0
        rango_texto = "Sueldo diario promedio sugerido en Cusco: S/. 50.00 a S/. 60.00"
    elif rol_seleccionado == "Ayudante de Cocina":
        sueldo_sugerido = 40.0
        rango_texto = "Sueldo diario promedio sugerido en Cusco: S/. 35.00 a S/. 45.00"
    elif rol_seleccionado == "Mozo":
        sueldo_sugerido = 40.0
        rango_texto = "Sueldo diario promedio sugerido en Cusco: S/. 35.00 a S/. 45.00"
    elif rol_seleccionado == "Personal de Limpieza":
        sueldo_sugerido = 35.0
        rango_texto = "Sueldo diario promedio sugerido en Cusco: S/. 35.00 a S/. 40.00"
    else:
        sueldo_sugerido = 40.0
        rango_texto = ""
        
    st.markdown(f"<span style='color: #FFEA00; font-size: 12px; font-weight: bold;'>💡 {rango_texto}</span>", unsafe_allow_html=True)
    
    with st.form("formulario_planilla_sumac", clear_on_submit=True):
        nombre_personal = st.text_input("Nombre del trabajador:", placeholder="Ej: Juana Quispe")
        monto_pago = st.number_input("Monto pagado (S/.)", min_value=0.0, step=5.0, value=sueldo_sugerido)
        tipo_pago = st.selectbox("Tipo de Pago:", ["Pago Diario (Jornal Completo)", "Adelanto de Sueldo", "Pago de Turno Medio", "Sueldo Semanal/Mensual"])
        
        btn_registrar_personal = st.form_submit_button("💾 Registrar Pago de Personal")
        
        if btn_registrar_personal:
            if nombre_personal and monto_pago > 0:
                detalle_pago = f"🧑‍🍳 PAGO: {rol_seleccionado} ({nombre_personal}) - {tipo_pago}"
                if registrar_movimiento_instantaneo("PLANILLA", detalle_pago, monto_pago):
                    st.toast(f"👤 Pago registrado: {nombre_personal} (S/. {monto_pago:.2f})", icon="👤")
                    st.session_state["reproducir_sonido"] = True
                    st.rerun()
            else:
                st.error("Por favor ingresa el nombre del trabajador y un monto de pago válido.")

    st.markdown("<br><h5 style='color: #CFD8DC;'>📋 Sueldos y adelantos pagados hoy:</h5>", unsafe_allow_html=True)
    if datos.get("planilla", []):
        planilla_hoy = datos["planilla"]
        try:
            planilla_hoy_sorted = sorted(planilla_hoy, key=lambda x: obtener_datetime_sort(x["fecha"]), reverse=True)
        except:
            planilla_hoy_sorted = planilla_hoy
            
        for p in planilla_hoy_sorted:
            fecha = p.get("fecha", "")
            hora = extraer_hora(fecha)
            st.markdown(f"<div style='display: flex; justify-content: space-between; background: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #FFEA00;'><span style='color: #FFFFFF; font-weight: bold;'>{p['detalle']}</span><span style='color: #FFEA00; font-weight: bold;'>S/. {p['monto']:.2f} ({hora})</span></div>", unsafe_allow_html=True)
    else:
        st.info("No se han registrado pagos a personal el día de hoy.")

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
    total_p = sum(p["monto"] for p in datos.get("planilla", []))
    egresos = total_g + total_p
    ganancia = total_v - egresos
    
    col_v, col_g, col_p = st.columns(3)
    with col_v:
        st.markdown(f"<div class='metric-box'>Ingresos<br><span class='metric-val-green'>S/. {total_v:.2f}</span></div>", unsafe_allow_html=True)
    with col_g:
        st.markdown(f"<div class='metric-box'>Gastos<br><span class='metric-val-red'>S/. {total_g:.2f}</span></div>", unsafe_allow_html=True)
    with col_p:
        st.markdown(f"<div class='metric-box'>Planilla<br><span class='metric-val-red' style='color: #FFEA00;'>S/. {total_p:.2f}</span></div>", unsafe_allow_html=True)
        
    st.markdown(f"<div class='metric-box' style='background: #252525;'>GANANCIA NETA REAL<br><span class='metric-val-blue' style='color: {'#00FF66' if ganancia >= 0 else '#FF0055'}'>S/. {ganancia:.2f}</span></div>", unsafe_allow_html=True)

    # --- CONTROL AUTOMÁTICO DE INVENTARIO Y STOCK ---
    st.markdown("---")
    st.markdown("<h4 style='color: #CFD8DC;'>📦 Estado del Almacén (Descuento Automático)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; color: #888;'>Calculado en tiempo real en base a compras registradas y porciones vendidas:</p>", unsafe_allow_html=True)
    
    # 1. Calcular compras totales de Stock registradas en Google Sheets
    gallinas_compradas = 0
    fideos_comprados_porciones = 0
    for g in datos["compras"]:
        detalle = g.get("detalle", "")
        if "📦 COMPRA STOCK - Gallinas:" in detalle:
            match = re.search(r"Gallinas: (\d+)", detalle)
            if match:
                gallinas_compradas += int(match.group(1))
        elif "📦 COMPRA STOCK - Fideos:" in detalle:
            match = re.search(r"Fideos: (\d+)", detalle)
            if match:
                # Cada paquete de fideos rinde unas 20 porciones de caldo
                fideos_comprados_porciones += int(match.group(1)) * 20
                
    # 2. Calcular mermas y consumos automáticos según ventas
    gallinas_consumidas = 0.0
    fideos_consumidos = 0
    for v in datos["ventas"]:
        producto = v.get("producto", "")
        if "Caldo sin presa" in producto:
            # Consume consomé base (equivalente a 0.05 gallinas de chacra por el caldo)
            gallinas_consumidas += 0.05
            fideos_consumidos += 1
        elif "Caldo presa mediana" in producto:
            # Consume 1 porción de fideo y 1/8 (0.125) de gallina
            gallinas_consumidas += 0.125
            fideos_consumidos += 1
        elif "Caldo presa entera" in producto:
            # Consume 1 porción de fideo y 1/4 (0.25) de gallina
            gallinas_consumidas += 0.25
            fideos_consumidos += 1
            
    # Stock resultante no menor a 0
    stock_gallinas = max(0.0, gallinas_compradas - gallinas_consumidas)
    stock_fideos = max(0, fideos_comprados_porciones - fideos_consumidos)
    
    col_st_g, col_st_f = st.columns(2)
    with col_st_g:
        estado_g = "🟢 Suficiente" if stock_gallinas > 3.0 else "🚨 Crítico (Reabastecer)"
        color_g = "#00FF66" if stock_gallinas > 3.0 else "#FF0055"
        st.markdown(f"""
            <div class='metric-box' style='border-left: 5px solid {color_g};'>
                🐔 Gallinas en Stock<br>
                <span style='font-size: 24px; font-weight: bold; color: {color_g};'>{stock_gallinas:.2f} uds</span><br>
                <span style='font-size: 11px; color: #888;'>Compradas: {gallinas_compradas} | Mermas: {gallinas_consumidas:.2f}</span><br>
                <span style='font-weight: bold; color: {color_g}; font-size: 12px;'>{estado_g}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col_st_f:
        estado_f = "🟢 Suficiente" if stock_fideos > 15 else "🚨 Crítico (Reabastecer)"
        color_f = "#00FF66" if stock_fideos > 15 else "#FF0055"
        st.markdown(f"""
            <div class='metric-box' style='border-left: 5px solid {color_f};'>
                🍝 Fideos (Porciones)<br>
                <span style='font-size: 24px; font-weight: bold; color: {color_f};'>{stock_fideos} platos</span><br>
                <span style='font-size: 11px; color: #888;'>Ingresadas: {fideos_comprados_porciones} | Servidas: {fideos_consumidos}</span><br>
                <span style='font-weight: bold; color: {color_f}; font-size: 12px;'>{estado_f}</span>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico de progreso de rentabilidad
    if total_v > 0:
        st.markdown("<br><h5 style='text-align: center; color: #CFD8DC;'>📊 Distribución Financiera:</h5>", unsafe_allow_html=True)
        porcentaje_gasto = (egresos / total_v)
        porcentaje_rentabilidad = max(0.0, 1.0 - porcentaje_gasto)
        
        st.write(f"🟢 Ganancia Neta Real ({porcentaje_rentabilidad*100:.0f}%)")
        st.progress(porcentaje_rentabilidad)
        
        st.write(f"🔴 Gastos y Planilla ({porcentaje_gasto*100:.0f}%)")
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
