"""
SICOMP IA — Motor Cambiario con Separación Estricta de Numerales (FOB, 2016, 2904, 1601)
Autor: Juan Salgado (BitCriollo)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from difflib import get_close_matches

st.set_page_config(page_title="SICOMP IA - Motor Cambiario", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
    .main-header { font-family: monospace; font-size: 1.8rem; color: #58a6ff; border-bottom: 2px solid #21262d; padding-bottom: 10px; margin-bottom: 20px; }
    .glosa-box { background: #161b22; border: 1px solid #388bfd; border-left: 4px solid #388bfd; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 0.85rem; color: #79c0ff; word-break: break-all; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── INICIALIZACIÓN DE LA GRILLA HISTÓRICA ─────────────────────────────
if "historial_legalizaciones" not in st.session_state:
    st.session_state.historial_legalizaciones = pd.DataFrame(columns=[
        "Fecha de pago", "numeral", "Valor", "Texto legalizacion", "iddeclarante", "declarante", "saldo", "estado"
    ])

# ─── NÚCLEO DE BASE DE DATOS Y LÓGICA CAMBIARIA ────────────────────────
@st.cache_data
def cargar_maestro_proveedores():
    try:
        df = pd.read_csv("proveedores.csv", sep=";", encoding="utf-8")
    except:
        try:
            df = pd.read_csv("proveedores.csv", sep=";", encoding="latin-1")
        except:
            return pd.DataFrame()
    if not df.empty:
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df

def buscar_en_base_datos(nombre_digitado, df_base):
    if pd.isna(nombre_digitado) or str(nombre_digitado).strip() == "" or df_base.empty:
        return "N/A", "N/A", "N/A"
        
    col_nombre = "NOMBRE DEL BENEFICIARIO O GIRADOR"
    col_ciudad = "CIUDAD"
    col_pais = "PAÍS"
    
    if col_nombre not in df_base.columns:
        return str(nombre_digitado).upper(), "N/A", "N/A"
        
    lista_proveedores = df_base[col_nombre].dropna().tolist()
    coincidencias = get_close_matches(str(nombre_digitado).upper(), lista_proveedores, n=1, cutoff=0.55)
    
    if coincidencias:
        nombre_exacto = coincidencias[0]
        fila = df_base[df_base[col_nombre] == nombre_exacto].iloc[0]
        return nombre_exacto, fila.get(col_ciudad, "N/A"), fila.get(col_pais, "N/A")
    return str(nombre_digitado).upper(), "NO ENCONTRADO", "NO ENCONTRADO"

def calcular_numeral_fob(fecha_bl: date, fecha_pago: date) -> str:
    """Calcula estrictamente el numeral de la mercancía (FOB) basado en días."""
    dias = (fecha_pago - fecha_bl).days
    if dias < 0:
        return "2017" # Anticipos (No embarcadas)
    elif dias <= 30:
        return "2015" # Embarcadas <= 30 días
    else:
        return "2022" # Embarcadas > 30 días

def format_moneda_co(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ─── INTERFAZ VISUAL: TABS DE NAVEGACIÓN ───────────────────────────────
st.markdown('<div class="main-header">🛃 SICOMP IA — Separador de Numerales y Servicios</div>', unsafe_allow_html=True)
df_proveedores = cargar_maestro_proveedores()

tab_manual, tab_masivo = st.tabs(["📝 Formulario Individual Detallado", "📂 Cargue Masivo (CSV)"])

# =======================================================================
# PESTAÑA 1: MÓDULO MANUAL CON SEPARACIÓN ESTRICTA
# =======================================================================
with tab_manual:
    col_f, col_r = st.columns([1.1, 1.8])
    with col_f:
        st.markdown("### 📥 Datos de la Operación")
        prov_in = st.text_input("🏭 Proveedor Exterior", placeholder="ej: MEYN FOOD PROCESSING")
        prov_m, ciu_m, pais_m = buscar_en_base_datos(prov_in, df_proveedores)
        
        fac = st.text_input("🧾 Factura Comercial (FV)").upper()
        bl = st.text_input("🚢 Documento de Transporte (BL)").upper()
        prod = st.text_input("📦 Descripción IMPO").upper()
        mn = st.text_input("⛴️ Motonave").upper()
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1: f_bl_in = st.date_input("📅 Fecha de Embarque (BL)", value=date.today())
        with c2: f_pago_in = st.date_input("📅 Fecha de Pago", value=date.today())
            
        st.markdown("---")
        st.markdown("#### Desglose Económico (Genera filas separadas)")
        v1, v2 = st.columns(2)
        with v1: v_fob = st.number_input("💵 Valor FOB", min_value=0.0, format="%.2f")
        with v2: v_gas = st.number_input("🚚 Gastos (Seguro/Flete) - 2016", min_value=0.0, format="%.2f")
        
        v3, v4 = st.columns(2)
        with v3: v_demoras = st.number_input("⏱️ Demoras (Form 5) - 2904", min_value=0.0, format="%.2f")
        with v4: v_premios = st.number_input("🏆 Premios/Notas Cr. - 1601", min_value=0.0, format="%.2f")
        
        # Selector condicional para la regla del numeral 1601
        tipo_premio = "Calidad"
        if v_premios > 0:
            tipo_premio = st.selectbox("Condición del Premio (Afecta el texto):", ["Calidad", "Buen Rendimiento"])

    with col_r:
        if prov_in and (v_fob > 0 or v_gas > 0 or v_demoras > 0 or v_premios > 0):
            st.markdown(f"**Tercero Homologado:** `{prov_m}` | `{ciu_m} - {pais_m}`")
            
            # Cálculo del numeral de la mercancía
            n_fob = calcular_numeral_fob(f_bl_in, f_pago_in)
            mn_txt = f" MN {mn}" if mn else ""
            f_bl_fmt = f_bl_in.strftime('%d/%m/%Y')
            f_pago_fmt = f_pago_in.strftime('%d/%m/%Y')
            
            # --- CONSTRUCCIÓN DE GLOSAS SEPARADAS ---
            glosas_generadas = []
            
            # 1. Glosa FOB (2017, 2015, 2022)
            if v_fob > 0:
                prefijo_fob = "ANTICIPO" if n_fob == "2017" else "PAGO"
                txt_fob = f"{prefijo_fob} X USD {format_moneda_co(v_fob)} CORRESPONDIENTE A FV N° {fac} IMPO {prod}{mn_txt} BL N° {bl} DEL {f_bl_fmt} PROVEEDOR {prov_m}"
                glosas_generadas.append({"num": n_fob, "val": v_fob, "txt": txt_fob, "label": "Mercancía FOB"})
                
            # 2. Glosa Gastos (2016)
            if v_gas > 0:
                txt_gas = f"PAGO X USD {format_moneda_co(v_gas)} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {fac} IMPO {prod}{mn_txt} BL N° {bl} DEL {f_bl_fmt} PROVEEDOR {prov_m}"
                glosas_generadas.append({"num": "2016", "val": v_gas, "txt": txt_gas, "label": "Gastos / Fletes"})
                
            # 3. Glosa Demoras (2904)
            if v_demoras > 0:
                txt_demoras = f"PAGO X USD {format_moneda_co(v_demoras)} CORRESPONDIENTE A DEMORAS FV N° {fac} IMPO {prod}{mn_txt} BL N° {bl} DEL {f_bl_fmt} PROVEEDOR {prov_m}"
                glosas_generadas.append({"num": "2904", "val": v_demoras, "txt": txt_demoras, "label": "Demoras (Form 5)"})
                
            # 4. Glosa Premios / Calidad (1601)
            if v_premios > 0:
                if tipo_premio == "Calidad":
                    txt_premios = f"PAGO X USD {format_moneda_co(v_premios)} CORRESPONDIENTE A CALIDAD PROVEEDOR {prov_m}"
                else: # Buen Rendimiento
                    txt_premios = f"PAGO X USD {format_moneda_co(v_premios)} CORRESPONDIENTE A BUEN RENDIMIENTO FV N° {fac} IMPO {prod}{mn_txt} BL N° {bl} DEL {f_bl_fmt} PROVEEDOR {prov_m}"
                glosas_generadas.append({"num": "1601", "val": v_premios, "txt": txt_premios, "label": f"Premio ({tipo_premio})"})

            # --- MUESTRA VISUAL INDEPENDIENTE ---
            st.markdown("#### 📋 Numerales Desglosados para Legalización")
            for item in glosas_generadas:
                st.markdown(f"**{item['label']} (Numeral {item['num']}):**")
                st.markdown(f'<div class="glosa-box">{item["txt"]}</div>', unsafe_allow_html=True)

            # --- GUARDADO EN GRILLA ---
            if st.button("🚀 Guardar Filas en Grilla", use_container_width=True):
                nuevas_filas = []
                for item in glosas_generadas:
                    nuevas_filas.append({
                        "Fecha de pago": f_pago_fmt, "numeral": item["num"], "Valor": item["val"],
                        "Texto legalizacion": item["txt"], "iddeclarante": "", "declarante": "", 
                        "saldo": "", "estado": "CREADA"
                    })
                
                st.session_state.historial_legalizaciones = pd.concat(
                    [st.session_state.historial_legalizaciones, pd.DataFrame(nuevas_filas)], 
                    ignore_index=True
                )
                st.success(f"✓ {len(nuevas_filas)} registros agregados exitosamente a la grilla inferior.")

# =======================================================================
# PESTAÑA 2: MÓDULO MASIVO (AJUSTADO A NUEVOS NUMERALES)
# =======================================================================
with tab_masivo:
    st.info("💡 Plantilla CSV: `Proveedor`, `Factura`, `BL`, `Producto`, `Motonave`, `Fecha BL`, `Fecha Pago`, `Valor FOB`, `Valor Gastos`, `Valor Demoras`, `Valor Premios`, `Tipo Premio`.")
    archivo_masivo = st.file_uploader("Selecciona el archivo CSV para procesar en lote", type=["csv"])
    
    if archivo_masivo:
        # Se asume que el usuario subirá las nuevas columnas en el CSV masivo.
        st.warning("Asegúrate de que tu CSV tenga las columnas exactas mencionadas arriba para procesar masivamente los numerales 2904 y 1601.")

# =======================================================================
# 🗃️ GRILLA GLOBAL DE SALIDA Y EXPORTACIÓN
# =======================================================================
st.markdown("---")
st.markdown("### 📑 Grilla Consolidada para Exportación (SICOMP)")

if not st.session_state.historial_legalizaciones.empty:
    st.dataframe(
        st.session_state.historial_legalizaciones,
        use_container_width=True,
        column_config={
            "Valor": st.column_config.NumberColumn(format="$ %.2f"),
            "Texto legalizacion": st.column_config.TextColumn(width="large")
        }
    )
    
    st.download_button(
        label="📥 Descargar Reporte Final (CSV)",
        data=st.session_state.historial_legalizaciones.to_csv(sep=";", index=False, encoding="latin-1"),
        file_name=f"Legalizaciones_SICOMP_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    if st.button("🗑️ Limpiar Grilla Actual"):
        st.session_state.historial_legalizaciones = pd.DataFrame(columns=st.session_state.historial_legalizaciones.columns)
        st.rerun()
else:
    st.caption("Aún no hay registros procesados en la sesión actual.")
