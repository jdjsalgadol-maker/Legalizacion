"""
SICOMP IA — Motor Cambiario (Tabla de Datos Pago Integrada)
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
</style>
""", unsafe_allow_html=True)

# ─── INICIALIZACIÓN DE LA GRILLA HISTÓRICA ─────────────────────────────
if "historial_legalizaciones" not in st.session_state:
    st.session_state.historial_legalizaciones = pd.DataFrame(columns=[
        "Fecha de pago", "numeral", "Valor", "Texto legalizacion", "saldo", "estado"
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
    """Calcula el numeral FOB según la diferencia de días."""
    dias = (fecha_pago - fecha_bl).days
    if dias < 0:
        return "2017" # Anticipo
    elif dias <= 30:
        return "2015" # Corto Plazo
    else:
        return "2022" # Financiado

def format_moneda_co(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ─── INTERFAZ VISUAL ───────────────────────────────────────────────────
st.markdown('<div class="main-header">🛃 SICOMP IA — Clasificación y Ordenamiento Cambiario</div>', unsafe_allow_html=True)
df_proveedores = cargar_maestro_proveedores()

tab_manual, tab_masivo = st.tabs(["📝 Generador de Operación Individual", "📂 Cargue Masivo en Lote"])

# =======================================================================
# PESTAÑA 1: MÓDULO MANUAL (FOB, GASTOS Y TABLA DE DATOS PAGO)
# =======================================================================
with tab_manual:
    col_f, col_r = st.columns([1.1, 1.8])
    with col_f:
        st.markdown("### 📥 Parámetros de la Operación")
        prov_in = st.text_input("🏭 Proveedor Exterior", placeholder="ej: MEYN FOOD PROCESSING")
        prov_m, ciu_m, pais_m = buscar_en_base_datos(prov_in, df_proveedores)
        
        fac = st.text_input("🧾 Factura Comercial (FV)").upper()
        bl = st.text_input("🚢 Documento de Transporte (BL)").upper()
        prod = st.text_input("📦 Descripción IMPO").upper()
        mn = st.text_input("⛴️ Motonave").upper()
        
        c1, c2 = st.columns(2)
        with c1: f_bl_in = st.date_input("📅 Fecha de Embarque (BL)", value=date.today())
        with c2: f_pago_in = st.date_input("📅 Fecha de Pago", value=date.today())
            
        st.markdown("---")
        st.markdown("#### Ingreso de Valores (USD)")
        v1, v2 = st.columns(2)
        with v1: v_fob = st.number_input("💵 Valor FOB", min_value=0.0, format="%.2f")
        with v2: v_gas = st.number_input("🚚 Gastos (Flete/Seguro)", min_value=0.0, format="%.2f")

    with col_r:
        if prov_in and (v_fob > 0 or v_gas > 0):
            st.markdown("### 📊 Previsualización y Ordenamiento Automático")
            
            # --- TABLA DE DATOS PAGO (Diseño exacto de la imagen) ---
            st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px;'>Datos pago</div>", unsafe_allow_html=True)
            df_datos_pago = pd.DataFrame([{
                "Nombre del beneficiario o Girador": prov_m,
                "CIUDAD": ciu_m,
                "PAÍS": pais_m
            }])
            st.dataframe(df_datos_pago, hide_index=True, use_container_width=True)
            
            n_fob = calcular_numeral_fob(f_bl_in, f_pago_in)
            mn_txt = f" MN {mn}" if mn else ""
            f_bl_fmt = f_bl_in.strftime('%d/%m/%Y')
            f_pago_fmt = f_pago_in.strftime('%d/%m/%Y')
            
            total_pago = v_fob + v_gas
            total_fmt = format_moneda_co(total_pago)
            
            filas_generadas = []

            # 1. Glosa FOB (Mantiene el valor individual, texto sumado)
            if v_fob > 0:
                prefijo_fob = "ANTICIPO" if n_fob == "2017" else "PAGO"
                txt_fob = f"{prefijo_fob} X USD {total_fmt} CORRESPONDIENTE A FV N° {fac} IMPO {prod}{mn_txt} BL N° {bl} DEL {f_bl_fmt} PROVEEDOR {prov_m}"
                filas_generadas.append({
                    "Fecha de pago": f_pago_fmt, "numeral": n_fob, "Valor": v_fob,
                    "Texto legalizacion": txt_fob, "saldo": "", "estado": "CREADA"
                })
                
            # 2. Glosa Gastos (Mantiene el valor individual, texto sumado)
            if v_gas > 0:
                txt_gas = f"PAGO X USD {total_fmt} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {fac} IMPO {prod}{mn_txt} BL N° {bl} DEL {f_bl_fmt} PROVEEDOR {prov_m}"
                filas_generadas.append({
                    "Fecha de pago": f_pago_fmt, "numeral": "2016", "Valor": v_gas,
                    "Texto legalizacion": txt_gas, "saldo": "", "estado": "CREADA"
                })
                
            # --- ORDENAMIENTO ASCENDENTE POR NUMERAL ---
            filas_generadas.sort(key=lambda x: int(x["numeral"]))
            
            # --- MOSTRAR CUADRO DE NUMERALES ---
            st.markdown("#### Cuadro de Numerales a Procesar")
            df_preview = pd.DataFrame(filas_generadas)[["numeral", "Valor", "Texto legalizacion"]]
            st.dataframe(df_preview, use_container_width=True, hide_index=True)

            if st.button("🚀 Guardar Operación en Grilla Histórica", use_container_width=True):
                st.session_state.historial_legalizaciones = pd.concat(
                    [st.session_state.historial_legalizaciones, pd.DataFrame(filas_generadas)], 
                    ignore_index=True
                )
                st.success("✓ Registros agregados y ordenados exitosamente en la grilla inferior.")

# =======================================================================
# PESTAÑA 2: MÓDULO MASIVO
# =======================================================================
with tab_masivo:
    st.info("💡 Plantilla CSV: `Proveedor`, `Factura`, `BL`, `Producto`, `Motonave`, `Fecha BL (YYYY-MM-DD)`, `Fecha Pago (YYYY-MM-DD)`, `Valor FOB`, `Valor Gastos`.")
    archivo_masivo = st.file_uploader("Selecciona el archivo CSV para procesar en lote", type=["csv"])
    
    if archivo_masivo:
        try:
            df_lote = pd.read_csv(archivo_masivo, sep=";")
            st.success(f"Archivo cargado correctamente. Registros detectados: {len(df_lote)}")
            
            if st.button("🚀 Procesar Lote y Generar Glosas Automáticas", use_container_width=True):
                nuevas_filas = []
                barra_progreso = st.progress(0)
                
                for idx, row in df_lote.iterrows():
                    f_bl = datetime.strptime(str(row['Fecha BL (YYYY-MM-DD)']).strip(), "%Y-%m-%d").date()
                    f_pago = datetime.strptime(str(row['Fecha Pago (YYYY-MM-DD)']).strip(), "%Y-%m-%d").date()
                    v_fob = float(row.get('Valor FOB', 0.0))
                    v_gas = float(row.get('Valor Gastos', 0.0))
                    
                    prov_map, ciu, pais = buscar_en_base_datos(row['Proveedor'], df_proveedores)
                    n_fob = calcular_numeral_fob(f_bl, f_pago)
                    
                    mn_txt = f" MN {str(row['Motonave']).upper()}" if pd.notna(row['Motonave']) else ""
                    f_bl_fmt = f_bl.strftime("%d/%m/%Y")
                    f_pago_fmt = f_pago.strftime("%d/%m/%Y")
                    
                    total_pago = v_fob + v_gas
                    total_fmt = format_moneda_co(total_pago)
                    
                    filas_temp = []
                    if v_fob > 0:
                        prefijo_fob = "ANTICIPO" if n_fob == "2017" else "PAGO"
                        glosa_fob = f"{prefijo_fob} X USD {total_fmt} CORRESPONDIENTE A FV N° {row['Factura']} IMPO {str(row['Producto']).upper()}{mn_txt} BL N° {row['BL']} DEL {f_bl_fmt} PROVEEDOR {prov_map}"
                        filas_temp.append({
                            "Fecha de pago": f_pago_fmt, "numeral": n_fob, "Valor": v_fob,
                            "Texto legalizacion": glosa_fob, "saldo": "", "estado": "CREADA"
                        })
                    
                    if v_gas > 0:
                        glosa_gas = f"PAGO X USD {total_fmt} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {row['Factura']} IMPO {str(row['Producto']).upper()}{mn_txt} BL N° {row['BL']} DEL {f_bl_fmt} PROVEEDOR {prov_map}"
                        filas_temp.append({
                            "Fecha de pago": f_pago_fmt, "numeral": "2016", "Valor": v_gas,
                            "Texto legalizacion": glosa_gas, "saldo": "", "estado": "CREADA"
                        })
                    
                    filas_temp.sort(key=lambda x: int(x["numeral"]))
                    nuevas_filas.extend(filas_temp)
                    
                    barra_progreso.progress((idx + 1) / len(df_lote))
                
                st.session_state.historial_legalizaciones = pd.concat(
                    [st.session_state.historial_legalizaciones, pd.DataFrame(nuevas_filas)], 
                    ignore_index=True
                )
                st.success("Lote procesado. Revisa la grilla en la parte inferior.")
                
        except Exception as e:
            st.error(f"Error procesando el archivo. Verifica las columnas de fechas. Detalle: {e}")

# =======================================================================
# 🗃️ GRILLA GLOBAL DE SALIDA Y EXPORTACIÓN
# =======================================================================
st.markdown("---")
st.markdown("### 📑 Grilla Consolidada para SICOMP")

if not st.session_state.historial_legalizaciones.empty:
    st.dataframe(
        st.session_state.historial_legalizaciones,
        use_container_width=True,
        column_config={
            "Valor": st.column_config.NumberColumn(format="$ %.2f"),
            "Texto legalizacion": st.column_config.TextColumn(width="large")
        },
        hide_index=True
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
