"""
SICOMP  — Carga Masiva y Motor Cambiario
Autor: Juan Salgado
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from difflib import get_close_matches

st.set_page_config(page_title="SICOMP IA - Bulk Engine", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
    .main-header { font-family: monospace; font-size: 1.8rem; color: #58a6ff; border-bottom: 2px solid #21262d; padding-bottom: 10px; margin-bottom: 20px; }
    .glosa-box { background: #161b22; border: 1px solid #388bfd; border-left: 4px solid #388bfd; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 0.85rem; color: #79c0ff; word-break: break-all; }
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
        ciudad = fila.get(col_ciudad, "N/A")
        pais = fila.get(col_pais, "N/A")
        return nombre_exacto, ciudad, pais
    return str(nombre_digitado).upper(), "NO ENCONTRADO", "NO ENCONTRADO"

def calcular_operacion(fecha_bl: date, fecha_pago: date, tiene_gastos: bool) -> tuple[str, str, int]:
    dias = (fecha_pago - fecha_bl).days
    num_gastos = "2016" if tiene_gastos else ""
    if dias < 0:
        return "2017", "", dias
    elif dias <= 30:
        return "2015", num_gastos, dias
    else:
        return "2022", num_gastos, dias

def format_moneda_co(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ─── INTERFAZ VISUAL: TABS DE NAVEGACIÓN ───────────────────────────────
st.markdown('<div class="main-header">🛃 SICOMP IA — Motor de Carga Masiva y Validación</div>', unsafe_allow_html=True)
df_proveedores = cargar_maestro_proveedores()

# Implementamos Pestañas para separar el ingreso manual del ingreso por lotes
tab_masivo, tab_manual = st.tabs(["📂 Cargue de Legalizaciones Masivas", "📝 Creación Manual Individual"])

# =======================================================================
# PESTAÑA 1: MÓDULO DE CARGA MASIVA (BASADO EN TU IMAGEN)
# =======================================================================
with tab_masivo:
    st.markdown("### 📥 Panel de Integración en Lote")
    st.info("💡 Sube una plantilla en CSV con las columnas: `Proveedor`, `Factura`, `BL`, `Producto`, `Motonave`, `Fecha BL (YYYY-MM-DD)`, `Fecha Pago (YYYY-MM-DD)`, `Valor FOB`, `Valor Gastos`.")
    
    archivo_masivo = st.file_uploader("Selecciona el archivo CSV de legalizaciones pendientes", type=["csv"])
    
    # Datos genéricos del declarante (Cumpliendo regla de privacidad)
    st.markdown("#### Datos Organizacionales para este lote")
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        id_dec_lote = st.text_input("ID / NIT Declarante (Lote):", value="900000000")
    with col_id2:
        nom_dec_lote = st.text_input("Razón Social Declarante (Lote):", value="EMPRESA IMPORTADORA S.A.").upper()

    if archivo_masivo:
        try:
            df_lote = pd.read_csv(archivo_masivo, sep=";")
            st.success(f"Archivo cargado correctamente. Registros detectados: {len(df_lote)}")
            
            if st.button("🚀 Procesar Lote y Generar Glosas Automáticas", use_container_width=True):
                nuevas_filas = []
                barra_progreso = st.progress(0)
                
                for idx, row in df_lote.iterrows():
                    # Parsear fechas
                    f_bl = datetime.strptime(str(row['Fecha BL (YYYY-MM-DD)']), "%Y-%m-%d").date()
                    f_pago = datetime.strptime(str(row['Fecha Pago (YYYY-MM-DD)']), "%Y-%m-%d").date()
                    v_fob = float(row['Valor FOB'])
                    v_gastos = float(row.get('Valor Gastos', 0.0))
                    
                    # Motor de búsqueda y cálculo
                    prov_map, ciu, pais = buscar_en_base_datos(row['Proveedor'], df_proveedores)
                    n_fob, n_gas, dias = calcular_operacion(f_bl, f_pago, v_gastos > 0)
                    
                    # Formateo de textos
                    mn_txt = f" MN {str(row['Motonave']).upper()}" if pd.notna(row['Motonave']) else ""
                    f_bl_fmt = f_bl.strftime("%d/%m/%Y")
                    f_pago_fmt = f_pago.strftime("%d/%m/%Y")
                    
                    # Creación Fila FOB
                    if v_fob > 0:
                        glosa_fob = f"PAGO X USD {format_moneda_co(v_fob)} CORRESPONDIENTE A FV N° {row['Factura']} IMPO {str(row['Producto']).upper()}{mn_txt} BL N° {row['BL']} DEL {f_bl_fmt} PROVEEDOR {prov_map}"
                        nuevas_filas.append({
                            "Fecha de pago": f_pago_fmt, "numeral": n_fob, "Valor": v_fob,
                            "Texto legalizacion": glosa_fob, "iddeclarante": id_dec_lote,
                            "declarante": nom_dec_lote, "saldo": "", "estado": "CREADA"
                        })
                    
                    # Creación Fila Gastos
                    if v_gastos > 0:
                        glosa_gas = f"PAGO X USD {format_moneda_co(v_gastos)} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {row['Factura']} IMPO {str(row['Producto']).upper()}{mn_txt} BL N° {row['BL']} DEL {f_bl_fmt} PROVEEDOR {prov_map}"
                        nuevas_filas.append({
                            "Fecha de pago": f_pago_fmt, "numeral": n_gas, "Valor": v_gastos,
                            "Texto legalizacion": glosa_gas, "iddeclarante": id_dec_lote,
                            "declarante": nom_dec_lote, "saldo": "", "estado": "CREADA"
                        })
                    
                    barra_progreso.progress((idx + 1) / len(df_lote))
                
                # Inyección al historial global
                st.session_state.historial_legalizaciones = pd.concat([st.session_state.historial_legalizaciones, pd.DataFrame(nuevas_filas)], ignore_index=True)
                st.success("Lote procesado. Revisa la grilla en la parte inferior de la pantalla.")
                
        except Exception as e:
            st.error(f"Error procesando el archivo: Verifica que los separadores sean ';' y las columnas estén correctas. Detalle: {e}")

# =======================================================================
# PESTAÑA 2: MÓDULO MANUAL (TU FORMULARIO TRADICIONAL)
# =======================================================================
with tab_manual:
    col_f, col_r = st.columns([1.1, 1.8])
    with col_f:
        id_dec_man = st.text_input("🆔 NIT Declarante:", value="900000000", key="id_man")
        nom_dec_man = st.text_input("🏢 Razón Social:", value="EMPRESA IMPORTADORA S.A.", key="nom_man").upper()
        st.markdown("---")
        prov_in = st.text_input("🏭 Proveedor Exterior", placeholder="ej: Aollen o Seaboard")
        prov_m, ciu_m, pais_m = buscar_en_base_datos(prov_in, df_proveedores)
        
        fac = st.text_input("🧾 Factura Comercial (FV)")
        bl = st.text_input("🚢 Documento de Transporte (BL)")
        prod = st.text_input("📦 Descripción")
        mn = st.text_input("⛴️ Motonave")
        
        c1, c2 = st.columns(2)
        with c1: f_bl_in = st.date_input("📅 Fecha de Embarque", value=date.today())
        with c2: f_pago_in = st.date_input("📅 Fecha de Pago", value=date.today())
            
        c3, c4 = st.columns(2)
        with c3: v_fob = st.number_input("💵 Valor FOB", min_value=0.0, format="%.2f")
        with c4: v_gas = st.number_input("🚚 Valor Gastos", min_value=0.0, format="%.2f")

    with col_r:
        if v_fob > 0 and prov_in:
            n_f, n_g, d = calcular_operacion(f_bl_in, f_pago_in, v_gas > 0)
            st.markdown(f"**Tercero Homologado:** `{prov_m}` | `{ciu_m} - {pais_m}`")
            
            # --- Textos generados ---
            glosa_f = f"PAGO X USD {format_moneda_co(v_fob)} CORRESPONDIENTE A FV N° {fac.upper()} IMPO {prod.upper()} MN {mn.upper()} BL N° {bl.upper()} DEL {f_bl_in.strftime('%d/%m/%Y')} PROVEEDOR {prov_m}"
            st.markdown(f"**Glosa Mercancía (Num {n_f}):**")
            st.markdown(f'<div class="glosa-box">{glosa_f}</div>', unsafe_allow_html=True)
            
            glosa_g = ""
            if v_gas > 0:
                glosa_g = f"PAGO X USD {format_moneda_co(v_gas)} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {fac.upper()} IMPO {prod.upper()} MN {mn.upper()} BL N° {bl.upper()} DEL {f_bl_in.strftime('%d/%m/%Y')} PROVEEDOR {prov_m}"
                st.markdown(f"<br>**Glosa Gastos (Num {n_g}):**", unsafe_allow_html=True)
                st.markdown(f'<div class="glosa-box">{glosa_g}</div>', unsafe_allow_html=True)

            if st.button("🚀 Guardar en Grilla", use_container_width=True):
                st.session_state.historial_legalizaciones = pd.concat([st.session_state.historial_legalizaciones, pd.DataFrame([{
                    "Fecha de pago": f_pago_in.strftime('%d/%m/%Y'), "numeral": n_f, "Valor": v_fob,
                    "Texto legalizacion": glosa_f, "iddeclarante": id_dec_man, "declarante": nom_dec_man, "saldo": "", "estado": "CREADA"
                }])], ignore_index=True)
                if v_gas > 0:
                    st.session_state.historial_legalizaciones = pd.concat([st.session_state.historial_legalizaciones, pd.DataFrame([{
                        "Fecha de pago": f_pago_in.strftime('%d/%m/%Y'), "numeral": n_g, "Valor": v_gas,
                        "Texto legalizacion": glosa_g, "iddeclarante": id_dec_man, "declarante": nom_dec_man, "saldo": "", "estado": "CREADA"
                    }])], ignore_index=True)
                st.success("Guardado exitoso.")

# =======================================================================
# 🗃️ BORRADOR GLOBAL DE SALIDA Y EXPORTACIÓN
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
        label="📥 Descargar Reporte Final (CSV para Excel)",
        data=st.session_state.historial_legalizaciones.to_csv(sep=";", index=False, encoding="latin-1"),
        file_name=f"Cargue_Masivo_SICOMP_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    if st.button("🗑️ Limpiar Grilla Actual"):
        st.session_state.historial_legalizaciones = pd.DataFrame(columns=st.session_state.historial_legalizaciones.columns)
        st.rerun()
else:
    st.caption("Aún no hay registros procesados en la sesión actual.")
