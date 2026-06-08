"""
SICOMP IA — Sistema de Gestión y Legalización Cambiaria
Autor: Juan Salgado
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from difflib import get_close_matches

# Configuración del entorno gráfico expandido
st.set_page_config(page_title="SICOMP IA - Panel de Control", layout="wide")

# Estilos CSS para calzar con tu paleta seria y profesional (Tema Oscuro)
st.markdown("""
<style>
    .stApp { background: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
    .main-header { font-family: monospace; font-size: 1.8rem; color: #58a6ff; border-bottom: 2px solid #21262d; padding-bottom: 10px; margin-bottom: 20px; }
    .glosa-box { background: #161b22; border: 1px solid #388bfd; border-left: 4px solid #388bfd; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 0.85rem; color: #79c0ff; word-break: break-all; }
    [data-testid="stMetric"] { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; }
    .card-output { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ─── MÓDULO 1: ESTADO E INICIALIZACIÓN DEL HISTORIAL DE TU GRILLA ─────
if "historial_legalizaciones" not in st.session_state:
    # Estructura exacta de columnas de tu diseño de grilla
    st.session_state.historial_legalizaciones = pd.DataFrame(columns=[
        "Fecha de pago", "numeral", "Valor", "Texto legalizacion", "iddeclarante", "declarante", "saldo", "estado"
    ])

# ─── MÓDULO 2: NÚCLEO DE CARGA Y CONTROL DE BASE DE DATOS ──────────────
@st.cache_data
def cargar_maestro_proveedores():
    """Lee y normaliza el archivo proveedores.csv según tus columnas reales"""
    try:
        df = pd.read_csv("proveedores.csv", sep=";", encoding="utf-8")
    except:
        try:
            df = pd.read_csv("proveedores.csv", sep=";", encoding="latin-1")
        except:
            return pd.DataFrame()
    if not df.empty:
        # Forzar mayúsculas y limpiar espacios huérfanos en los textos
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df

def buscar_en_base_datos(nombre_digitado, df_base):
    if df_base.empty or not nombre_digitado:
        return nombre_digitado.upper(), "N/A", "N/A"
        
    # Columnas exactas extraídas de tu maestro real de proveedores
    col_nombre = "NOMBRE DEL BENEFICIARIO O GIRADOR"
    col_ciudad = "CIUDAD"
    col_pais = "PAÍS"
    
    if col_nombre not in df_base.columns:
        return nombre_digitado.upper(), "N/A", "N/A"
        
    lista_proveedores = df_base[col_nombre].dropna().tolist()
    
    # Búsqueda difusa para tolerar variaciones de nombres comerciales
    coincidencias = get_close_matches(str(nombre_digitado).upper(), lista_proveedores, n=1, cutoff=0.55)
    
    if coincidencias:
        nombre_exacto = coincidencias[0]
        fila = df_base[df_base[col_nombre] == nombre_exacto].iloc[0]
        ciudad = fila.get(col_ciudad, "N/A")
        pais = fila.get(col_pais, "N/A")
        
        if ciudad == "NAN" or pd.isna(ciudad): ciudad = "N/A"
        if pais == "NAN" or pd.isna(pais): pais = "N/A"
        
        return nombre_exacto, ciudad, pais
    return nombre_digitado.upper(), "NO ENCONTRADO", "NO ENCONTRADO"

# ─── MÓDULO 3: MATRIZ DE PARAMETRIZACIÓN ADUANERA ─────────────────────
def calcular_operacion(fecha_bl: date, fecha_pago: date, tiene_gastos: bool) -> tuple[str, str, int, str]:
    dias = (fecha_pago - fecha_bl).days
    num_gastos = "2016" if tiene_gastos else ""
    if dias < 0:
        return "2017", "", dias, "Anticipo (Giro previo al embarque de mercancía)"
    elif dias <= 30:
        return "2015", num_gastos, dias, "Importación Corto Plazo (Embarque ≤ 30 días)"
    else:
        return "2022", num_gastos, dias, "Operación Financiada (Embarque > 30 días)"

def format_moneda_co(valor: float) -> str:
    # Formato numérico local colombiano: Miles con punto, decimales con coma
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ─── DESPLIEGUE DE LA INTERFAZ MAQUETADA ───────────────────────────────
st.markdown('<div class="main-header">🛃 SICOMP IA — Sistema de Gestión y Legalización Cambiaria</div>', unsafe_allow_html=True)

df_proveedores = cargar_maestro_proveedores()

# Diseño en bloques paralelos distribuidos según tu maquetación
col_formulario, col_resultados = st.columns([1.1, 1.8])

with col_formulario:
    st.markdown("### 📥 Parámetros de Entrada")
    
    # Campos fijos organizacionales de tu empresa declarante
    id_declarante = st.text_input("🆔 ID Declarante (NIT)", value="815000863")
    declarante = st.text_input("🏢 Nombre del Declarante", value="AVIDESA DE OCCIDENTE SA").upper()
    
    st.markdown("---")
    # Campos dinámicos operativos
    proveedor_in = st.text_input("🏭 Nombre del Proveedor Exterior", placeholder="ej: Aollen o Seaboard")
    prov_mapeado, ciu_mapeada, pais_mapeado = buscar_en_base_datos(proveedor_in, df_proveedores)
    
    factura = st.text_input("🧾 Número de Factura Comercial (FV)", placeholder="ej: FV-101749").upper()
    bl_doc = st.text_input("🚢 Documento de Transporte (BL / Guía)", placeholder="ej: COSU6435").upper()
    producto = st.text_input("📦 Descripción de la Mercancía IMPO", placeholder="ej: METHIONINA").upper()
    motonave = st.text_input("⛴️ Nombre de la Motonave (MN)", placeholder="ej: TIAN XIANG").upper()
    
    st.markdown("---")
    f1, f2 = st.columns(2)
    with f1:
        fecha_bl_in = st.date_input("📅 Fecha de Embarque (BL)", value=date.today())
    with f2:
        fecha_pago_in = st.date_input("📅 Fecha de Pago Real", value=date.today())
        
    st.markdown("---")
    v1, v2 = st.columns(2)
    with v1:
        valor_fob = st.number_input("💵 Valor FOB USD", min_value=0.0, format="%.2f")
    with v2:
        valor_gastos = st.number_input("🚚 Valor Gastos (Flete/Seguro)", min_value=0.0, format="%.2f")

with col_resultados:
    st.markdown("### 📊 Panel de Control y Resultados")
    
    if valor_fob > 0 and proveedor_in:
        # Ejecución del motor lógico cambiario
        num_fob, num_g, dias, concepto = calcular_operacion(fecha_bl_in, fecha_pago_in, valor_gastos > 0)
        
        # Muestra rápida del cruce con tu maestro indexado
        st.markdown(f"**🏭 Base de Datos:** Tercero Homologado: `{prov_mapeado}` | Origen: `{ciu_mapeada} - {pais_mapeado}`")
        
        # Cuadro de Métricas de Control
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Días Operación", f"{dias} días")
        with m2:
            st.metric("Numeral FOB", num_fob)
        with m3:
            st.metric("Numeral Gastos", num_g if valor_gastos > 0 else "N/A")
            
        if dias > 30:
            st.warning(f"⚠️ **Estatus:** {concepto}")
        else:
            st.success(f"✅ **Estatus:** {concepto}")
            
        # --- BLOQUE GENERADOR DE TEXTO DE LEGALIZACIÓN ---
        st.markdown("#### 📋 Estructura de Textos de Legalización")
        
        fob_fmt = format_moneda_co(valor_fob)
        mn_txt = f" MN {motonave}" if motonave else ""
        fecha_bl_fmt = fecha_bl_in.strftime("%d/%m/%Y")
        
        # Glosa 1: FOB Mercancía
        texto_legalizacion_fob = f"PAGO X USD {fob_fmt} CORRESPONDIENTE A FV N° {factura} IMPO {producto}{mn_txt} BL N° {bl_doc} DEL {fecha_bl_fmt} PROVEEDOR {prov_mapeado}"
        st.markdown(f"**Texto Legalización FOB (Numeral {num_fob}):**")
        st.markdown(f'<div class="glosa-box">{texto_legalizacion_fob}</div>', unsafe_allow_html=True)
        
        # Glosa 2: Gastos de Logística Unificados
        texto_legalizacion_gastos = ""
        if valor_gastos > 0:
            gastos_fmt = format_moneda_co(valor_gastos)
            texto_legalizacion_gastos = f"PAGO X USD {gastos_fmt} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {factura} IMPO {producto}{mn_txt} BL N° {bl_doc} DEL {fecha_bl_fmt} PROVEEDOR {prov_mapeado}"
            st.markdown(f"<br>**Texto Legalización Gastos (Numeral {num_g}):**", unsafe_allow_html=True)
            st.markdown(f'<div class="glosa-box">{texto_legalizacion_gastos}</div>', unsafe_allow_html=True)

        st.markdown("---")
        # --- ACCIÓN: PROCESAR REGISTRO ---
        if st.button("🚀 Procesar y Generar Registro", use_container_width=True):
            
            # Formatear fecha de pago a formato DD/MM/YYYY
            f_pago_fmt = fecha_pago_in.strftime("%d/%m/%Y")
            
            # Fila A: Almacenar segmento del FOB
            nueva_fila_fob = {
                "Fecha de pago": f_pago_fmt, "numeral": num_fob, "Valor": valor_fob,
                "Texto legalizacion": texto_legalizacion_fob, "iddeclarante": id_declarante,
                "declarante": declarante, "saldo": "", "estado": "CREADA"
            }
            st.session_state.historial_legalizaciones = pd.concat([
                st.session_state.historial_legalizaciones, pd.DataFrame([nueva_fila_fob])
            ], ignore_index=True)
            
            # Fila B: Almacenar segmento logístico independiente (Si aplica)
            if valor_gastos > 0:
                nueva_fila_gastos = {
                    "Fecha de pago": f_pago_fmt, "numeral": num_g, "Valor": valor_gastos,
                    "Texto legalizacion": texto_legalizacion_gastos, "iddeclarante": id_declarante,
                    "declarante": declarante, "saldo": "", "estado": "CREADA"
                }
                st.session_state.historial_legalizaciones = pd.concat([
                    st.session_state.historial_legalizaciones, pd.DataFrame([nueva_fila_gastos])
                ], ignore_index=True)
                
            st.success("✓ Registros agregados exitosamente a la grilla inferior.")
    else:
        st.info("💡 Complete el campo del Proveedor y un Valor FOB superior a cero para activar el generador de glosas.")

# =======================================================================
# 🗃️ GRILLA DE SALIDA COMPLETA (Mismo diseño de tu grilla estructurada)
# =======================================================================
st.markdown("---")
st.markdown("### 📑 Grilla de Legalizaciones Generadas (Historial de Sesión)")

if not st.session_state.historial_legalizaciones.empty:
    st.dataframe(
        st.session_state.historial_legalizaciones,
        use_container_width=True,
        column_config={
            "Valor": st.column_config.NumberColumn(format="$ %.2f"),
            "iddeclarante": st.column_config.TextColumn(label="ID Declarante"),
            "Texto legalizacion": st.column_config.TextColumn(label="Texto Legalización", width="large")
        }
    )
    
    # Descargador directo compatible al 100% con Excel Colombia (separador por punto y coma)
    csv_data = st.session_state.historial_legalizaciones.to_csv(sep=";", index=False, encoding="latin-1")
    st.download_button(
        label="📥 Descargar Grilla como CSV para Excel",
        data=csv_data,
        file_name="Grilla_SICOMP_Generada.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.caption("La grilla se encuentra vacía actualmente. Llena el formulario y presiona 'Procesar y Generar Registro' para poblar la tabla.")
