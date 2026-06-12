"""
Pre validador para legalizar
Autor: Juan Salgado 
Pwr Automate
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from difflib import get_close_matches

# Configuración de página inicial
st.set_page_config(page_title="Pre validador Siscomp - ", page_icon="🛃", layout="wide")

# Estilos personalizados en Dark Mode
st.markdown("""
<style>
    .stApp { background: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
    .main-header { font-family: monospace; font-size: 1.8rem; color: #58a6ff; border-bottom: 2px solid #21262d; padding-bottom: 10px; margin-bottom: 20px; }
    .table-title { text-align: center; font-weight: bold; margin-bottom: 5px; color: #58a6ff; }
    div[data-baseweb="select"] { cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# ─── 1. INICIALIZACIÓN DE LA GRILLA HISTÓRICA ──────────────────────────
if "historial_legalizaciones" not in st.session_state:
    st.session_state.historial_legalizaciones = pd.DataFrame(columns=[
        "Fecha de pago", "numeral", "Valor", "Texto legalizacion", "saldo", "estado"
    ])

# ─── 2. NÚCLEO DE BASE DE DATOS Y LÓGICA CAMBIARIA ─────────────────────
@st.cache_data
def cargar_maestro_proveedores():
    raw_data = [
        {"NOMBRE": "ADISSEO FRANCE S A S", "CIUDAD": "PARIS", "PAÍS": "FRANCIA"},
        {"NOMBRE": "ADM AMERICAS S DE RL", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "AHB HK LIMITED", "CIUDAD": "HONG KONG", "PAÍS": "CHINA"},
        {"NOMBRE": "ALFRIO CORP", "CIUDAD": "BEVERLY HILLS", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "AOLLEN BIOTECH CO., LTD.", "CIUDAD": "SHENZHEN", "PAÍS": "CHINA"},
        {"NOMBRE": "AMERICAN UNION CHEMICAL - AMUCO", "CIUDAD": "BLAIRSVILLE", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "AMERICAS PROTEIN SUPPLY AMERIPRO S.A.", "CIUDAD": "CIUDAD DE PANAMA", "PAÍS": "PANAMA"},
        {"NOMBRE": "BDV BEHRENS GMBH", "CIUDAD": "HAMBURGO", "PAÍS": "ALEMANIA"},
        {"NOMBRE": "B-DUTCHMAN AGRICULTURE DE MEXICO S.A DE CV", "CIUDAD": "MONTERREY", "PAÍS": "MEXICO"},
        {"NOMBRE": "BIG DUTCHMAN INC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "BUNGE NORTH AMERICA CAPITAL INC", "CIUDAD": "PITTSBURGH", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "CAI TRADING LLC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "CHONGQING CHUANDONG CHEMICAL, GROUP CO., LTD.", "CIUDAD": "CHONGQING", "PAÍS": "CHINA"},
        {"NOMBRE": "CJ CHEILJEDANG CORPORATION", "CIUDAD": "SEUL", "PAÍS": "COREA DEL SUR"},
        {"NOMBRE": "CLEAN WATER TECHNOLOGY COLOMBIA S", "CIUDAD": "MIAMI", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "CLEAN WATER TECHNOLOGY INC", "CIUDAD": "DETROIT", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "COFCO RESOURCES S.A", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "DACK TRADING LLC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "DALIAN PLATINUM CHEMICALS CO. LIMITED CORP", "CIUDAD": "MIAMI", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "DENKAVIT INGREDIENTS BV", "CIUDAD": "AMSTERDAM", "PAÍS": "NETHERLANDS"},
        {"NOMBRE": "DONGXIAO BIOTECHNOLOGY CO., LTD", "CIUDAD": "JINAN", "PAÍS": "CHINA"},
        {"NOMBRE": "DSI DANTECH", "CIUDAD": "COPENHAGUE", "PAÍS": "DINAMARCA"},
        {"NOMBRE": "ECO NUTRITION HONGKONG LIMITED", "CIUDAD": "PASADENA", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "EVONIK COLOMBIA S.A.S", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "FNF INGREDIENTS LA LLC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "FUFENG HONG KONG IMPORT EXP", "CIUDAD": "SHANGHAI", "PAÍS": "CHINA"},
        {"NOMBRE": "HENAN FUFA BIOTECHNOLOGY CO., LTD.", "CIUDAD": "HANGZHOU", "PAÍS": "CHINA"},
        {"NOMBRE": "HURTADO Y ASOCIADOS CPA, S.A", "CIUDAD": "CIUDAD DE PANAMA", "PAÍS": "PANAMA"},
        {"NOMBRE": "ICAZA, GONZALEZ - RUIZ Y ALEMAN", "CIUDAD": "CIUDAD DE PANAMA", "PAÍS": "PANAMA"},
        {"NOMBRE": "INNOPHOS INC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "JAMESWAY INCUBATOR COMPANY INC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "JEBSEN & JESSEN CHEMICALS", "CIUDAD": "HAMBURGO", "PAÍS": "ALEMANIA"},
        {"NOMBRE": "JIANGSU HUALI CO., LTDA", "CIUDAD": "CHANGZHOU", "PAÍS": "CHINA"},
        {"NOMBRE": "JINKO SOLAR CO., LTD", "CIUDAD": "SHANGHAI", "PAÍS": "CHINA"},
        {"NOMBRE": "KEMIEX AG", "CIUDAD": "ZURICH", "PAÍS": "SUIZA"},
        {"NOMBRE": "KUHL CORPORATION", "CIUDAD": "CHERRY HILL", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "LOIF REFRIGERATION INC", "CIUDAD": "PARRISH", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "MAREL INC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "MATPRIMA IMPORT INC", "CIUDAD": "CIUDAD DE PANAMA", "PAÍS": "PANAMA"},
        {"NOMBRE": "MEYN FOOD PROCESSING TECHNOLOGY DE MEXICO", "CIUDAD": "CIUDAD DE MEXICO", "PAÍS": "MEXICO"},
        {"NOMBRE": "MULTI COMMODITIES DE CENTROAMERICA", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "MEDINA GARNES ABOGADOS SRL", "CIUDAD": "SANTO DOMINGO", "PAÍS": "REPUBLICA DOMINICANA"},
        {"NOMBRE": "NHU CHR. OLESEN LATIN AMERICA", "CIUDAD": "AABENRAA", "PAÍS": "DINAMARCA"},
        {"NOMBRE": "POULTRY AND INDUSTRIAL SUPPLIERS INC", "CIUDAD": "MIAMI", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "PRAYON SA", "CIUDAD": "BRUSELAS", "PAÍS": "BELGICA"},
        {"NOMBRE": "PRINCE INDUSTRIES INC", "CIUDAD": "CHARLOTTE", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "RULAND PHARMA CO., LIMITED", "CIUDAD": "NANJING", "PAÍS": "CHINA"},
        {"NOMBRE": "SAFE FOODS CHEMICAL INNOVATIONS", "CIUDAD": "PINE BLUFF", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "SEABOARD OVERSEAS LIMITED", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "SHANDONG AOCTER FEED ADDITIVES CO., LTD.", "CIUDAD": "LIAOCHENG", "PAÍS": "CHINA"},
        {"NOMBRE": "SHANDONG YINFENG BIOLOGICAL TECHNOLOGY CO., LTD", "CIUDAD": "JINAN", "PAÍS": "CHINA"},
        {"NOMBRE": "SINOPHARM JIANGSU CO., LTD", "CIUDAD": "NANJING", "PAÍS": "CHINA"},
        {"NOMBRE": "STAR GRACE MINING CO., LTD", "CIUDAD": "DALIAN", "PAÍS": "CHINA"},
        {"NOMBRE": "STONEX FINANCIAL INC.", "CIUDAD": "CHICAGO", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "XINJIANG FUNFENG BIOTECHNOLOGIES ., LTD.", "CIUDAD": "LINYI", "PAÍS": "CHINA"},
        {"NOMBRE": "THOR MAQUINAS E MONTAGENS LTDA", "CIUDAD": "SAO PAULO", "PAÍS": "BRAZIL"},
        {"NOMBRE": "TITAN INJECTION PARTS AND SERVICE INC", "CIUDAD": "AURORA", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "TRIENERGY S.A.S", "CIUDAD": "MIAMI", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "TUNIFEED S.A.R.L", "CIUDAD": "RENNES", "PAÍS": "FRANCIA"},
        {"NOMBRE": "UNIVERSAL EQUIPMENT SUPPLIERS INC", "CIUDAD": "NEW YORK", "PAÍS": "ESTADOS UNIDOS"},
        {"NOMBRE": "VEGA PHARMA LIMITED", "CIUDAD": "SHANGHAI", "PAÍS": "CHINA"},
        {"NOMBRE": "WELDING GMBH & CO. KG", "CIUDAD": "HAMBURGO", "PAÍS": "ALEMANIA"},
        {"NOMBRE": "SCANICO A/S", "CIUDAD": "AABENRAA", "PAÍS": "DINAMARCA"}
    ]
    df = pd.DataFrame(raw_data)
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()
    return df

def buscar_en_base_datos(nombre_digitado, df_base, modo_exacto=False):
    if pd.isna(nombre_digitado) or str(nombre_digitado).strip() == "" or df_base.empty:
        return "N/A", "N/A", "N/A"
        
    termino = str(nombre_digitado).upper().strip()
    lista_proveedores = df_base["NOMBRE"].tolist()
    
    if modo_exacto:
        coincidencias = df_base[df_base["NOMBRE"] == termino]
        if not coincidencias.empty:
            fila = coincidencias.iloc[0]
            return fila["NOMBRE"], fila.get("CIUDAD", "N/A"), fila.get("PAÍS", "N/A")
    else:
        mejores_match = get_close_matches(termino, lista_proveedores, n=1, cutoff=0.50)
        if mejores_match:
            nombre_exacto = mejores_match[0]
            fila = df_base[df_base["NOMBRE"] == nombre_exacto].iloc[0]
            return nombre_exacto, fila.get("CIUDAD", "N/A"), fila.get("PAÍS", "N/A")
            
    return termino, "NO ENCONTRADO", "NO ENCONTRADO"

def calcular_numeral_fob(bl_text: str, fecha_bl: date, fecha_pago: date) -> str:
    if not bl_text or str(bl_text).upper() == "NAN":
        return "2017" # Anticipo
    dias = (fecha_pago - fecha_bl).days
    if dias < 0:
        return "2017"
    elif dias <= 30:
        return "2015"
    else:
        return "2022"

def format_moneda_co(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ─── 3. INTERFAZ VISUAL ────────────────────────────────────────────────
st.markdown('<div class="main-header">🛃 SICOMP IA — Clasificación y Ordenamiento Cambiario</div>', unsafe_allow_html=True)
df_proveedores = cargar_maestro_proveedores()

tab_manual, tab_masivo = st.tabs(["📝 Generador de Operación Individual", "📂 Cargue Masivo en Lote"])

# =======================================================================
# PESTAÑA 1: MÓDULO MANUAL
# =======================================================================
with tab_manual:
    col_f, col_r = st.columns([1.1, 1.8])
    with col_f:
        st.markdown("### 📥 Parámetros de la Operación")
        
        lista_opciones = df_proveedores["NOMBRE"].tolist()
        
        prov_in = st.selectbox(
            "🏭 Proveedor Exterior (Escribe para buscar)",
            options=lista_opciones,
            index=None,
            placeholder="Escribe o selecciona el nombre..."
        )
        
        prov_m, ciu_m, pais_m = buscar_en_base_datos(prov_in, df_proveedores, modo_exacto=True)
        
        fac = st.text_input("🧾 Factura Comercial (FV)", placeholder="Ej: INV-2024").upper().strip()
        bl = st.text_input("🚢 Documento de Transporte (BL)", placeholder="Ej: HLCU123456").upper().strip()
        prod = st.text_input("📦 Descripción IMPO", placeholder="Ej: REPUESTOS").upper().strip()
        mn = st.text_input("⛴️ Motonave", placeholder="Ej: MSC GAYANE").upper().strip()
        
        c1, c2 = st.columns(2)
        with c1: 
            # Calendario bloqueado dinámicamente si no hay BL escrito
            f_bl_in = st.date_input(
                "📅 Fecha Embarque (BL)", 
                value=date.today(), 
                disabled=not bool(bl)
            )
        with c2: 
            f_pago_in = st.date_input("📅 Fecha Pago", value=date.today())
            
        st.markdown("---")
        st.markdown("#### Ingreso de Valores (USD)")
        v1, v2 = st.columns(2)
        with v1: v_fob = st.number_input("💵 Valor FOB", min_value=0.0, format="%.2f", step=100.0)
        with v2: v_gas = st.number_input("🚚 Gastos (Flete/Seguro)", min_value=0.0, format="%.2f", step=50.0)

    with col_r:
        if prov_in and (v_fob > 0 or v_gas > 0):
            st.markdown("### 📊 Previsualización y Ordenamiento Automático")
            
            st.markdown("<div class='table-title'>Datos pago (Automático)</div>", unsafe_allow_html=True)
            df_datos_pago = pd.DataFrame([{
                "Nombre del beneficiario o Girador": prov_m,
                "CIUDAD": ciu_m,
                "PAÍS": pais_m
            }])
            st.dataframe(df_datos_pago, hide_index=True, use_container_width=True)
            
            n_fob = calcular_numeral_fob(bl, f_bl_in, f_pago_in)
            mn_txt = f" MN {mn}" if mn else ""
            f_bl_fmt = f_bl_in.strftime('%d/%m/%Y')
            f_pago_fmt = f_pago_in.strftime('%d/%m/%Y')
            
            total_pago = v_fob + v_gas
            total_fmt = format_moneda_co(total_pago)
            
            filas_generadas = []

            # ─── Glosa FOB ───
            if v_fob > 0:
                prefijo_fob = "ANTICIPO" if n_fob == "2017" else "PAGO"
                txt_bl = f" BL N° {bl} DEL {f_bl_fmt}" if bl else " (SIN EMBARCAR)"
                txt_fob = f"{prefijo_fob} X USD {total_fmt} CORRESPONDIENTE A FV N° {fac} IMPO {prod}{mn_txt}{txt_bl} PROVEEDOR {prov_m}"
                
                filas_generadas.append({
                    "Fecha de pago": f_pago_fmt, "numeral": n_fob, "Valor": v_fob,
                    "Texto legalizacion": txt_fob, "saldo": "", "estado": "CREADA"
                })
                
            # ─── Glosa Gastos ───
            if v_gas > 0:
                txt_bl_gas = f" BL N° {bl} DEL {f_bl_fmt}" if bl else " (SIN EMBARCAR)"
                txt_gas = f"PAGO X USD {total_fmt} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {fac} IMPO {prod}{mn_txt}{txt_bl_gas} PROVEEDOR {prov_m}"
                
                filas_generadas.append({
                    "Fecha de pago": f_pago_fmt, "numeral": "2016", "Valor": v_gas,
                    "Texto legalizacion": txt_gas, "saldo": "", "estado": "CREADA"
                })
                
            df_preview = pd.DataFrame(filas_generadas)
            df_preview["num_int"] = df_preview["numeral"].astype(int)
            df_preview = df_preview.sort_values("num_int").drop(columns=["num_int"])
            
            st.markdown("#### Cuadro de Numerales a Procesar")
            st.dataframe(df_preview[["numeral", "Valor", "Texto legalizacion"]], use_container_width=True, hide_index=True)

            if st.button("🚀 Guardar Operación en Grilla", use_container_width=True, type="primary"):
                st.session_state.historial_legalizaciones = pd.concat(
                    [st.session_state.historial_legalizaciones, df_preview], 
                    ignore_index=True
                )
                st.success("✓ Registros agregados exitosamente en la grilla inferior.")

# =======================================================================
# PESTAÑA 2: MÓDULO MASIVO
# =======================================================================
with tab_masivo:
    st.info("💡 Plantilla CSV (`Separador Coma ','`): `Proveedor`, `Factura`, `BL`, `Producto`, `Motonave`, `Fecha BL (YYYY-MM-DD)`, `Fecha Pago (YYYY-MM-DD)`, `Valor FOB`, `Valor Gastos`.")
    archivo_masivo = st.file_uploader("Selecciona el archivo CSV para procesar en lote", type=["csv"])
    
    if archivo_masivo:
        try:
            df_lote = pd.read_csv(archivo_masivo, sep=",", encoding="utf-8")
            st.success(f"📊 Archivo cargado correctamente. Registros detectados: {len(df_lote)}")
            
            if st.button("🚀 Procesar Lote y Generar Glosas Automáticas", use_container_width=True, type="primary"):
                nuevas_filas = []
                barra_progreso = st.progress(0)
                
                for idx, row in df_lote.iterrows():
                    f_bl = pd.to_datetime(row['Fecha BL (YYYY-MM-DD)']).date()
                    f_pago = pd.to_datetime(row['Fecha Pago (YYYY-MM-DD)']).date()
                    
                    v_fob = float(row.get('Valor FOB', 0.0))
                    v_gas = float(row.get('Valor Gastos', 0.0))
                    
                    prov_map, _, _ = buscar_en_base_datos(row['Proveedor'], df_proveedores, modo_exacto=False)
                    
                    bl_val = str(row['BL']).upper().strip() if pd.notna(row['BL']) else ""
                    if bl_val == "NAN": bl_val = ""
                    
                    n_fob = calcular_numeral_fob(bl_val, f_bl, f_pago)
                    
                    mn_txt = f" MN {str(row['Motonave']).upper()}" if pd.notna(row['Motonave']) else ""
                    f_bl_fmt = f_bl.strftime("%d/%m/%Y")
                    f_pago_fmt = f_pago.strftime("%d/%m/%Y")
                    
                    total_pago = v_fob + v_gas
                    total_fmt = format_moneda_co(total_pago)
                    
                    filas_temp = []
                    if v_fob > 0:
                        prefijo_fob = "ANTICIPO" if n_fob == "2017" else "PAGO"
                        txt_bl_lote = f" BL N° {bl_val} DEL {f_bl_fmt}" if bl_val else " (SIN EMBARCAR)"
                        glosa_fob = f"{prefijo_fob} X USD {total_fmt} CORRESPONDIENTE A FV N° {row['Factura']} IMPO {str(row['Producto']).upper()}{mn_txt}{txt_bl_lote} PROVEEDOR {prov_map}"
                        
                        filas_temp.append({
                            "Fecha de pago": f_pago_fmt, "numeral": n_fob, "Valor": v_fob,
                            "Texto legalizacion": glosa_fob, "saldo": "", "estado": "CREADA"
                        })
                    
                    if v_gas > 0:
                        txt_bl_lote_gas = f" BL N° {bl_val} DEL {f_bl_fmt}" if bl_val else " (SIN EMBARCAR)"
                        glosa_gas = f"PAGO X USD {total_fmt} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO FV N° {row['Factura']} IMPO {str(row['Producto']).upper()}{mn_txt}{txt_bl_lote_gas} PROVEEDOR {prov_map}"
                        
                        filas_temp.append({
                            "Fecha de pago": f_pago_fmt, "numeral": "2016", "Valor": v_gas,
                            "Texto legalizacion": glosa_gas, "saldo": "", "estado": "CREADA"
                        })
                    
                    filas_temp.sort(key=lambda x: int(x["numeral"]))
                    nuevas_filas.extend(filas_temp)
                    
                    barra_progreso.progress((idx + 1) / len(df_lote))
                
                if nuevas_filas:
                    st.session_state.historial_legalizaciones = pd.concat(
                        [st.session_state.historial_legalizaciones, pd.DataFrame(nuevas_filas)], 
                        ignore_index=True
                    )
                    st.success("🏁 Lote procesado con éxito. Revisa la grilla en la parte inferior.")
                else:
                    st.warning("⚠️ No se generaron registros. Verifica que los montos FOB o Gastos sean mayores a 0.")
                    
        except Exception as e:
            st.error(f"❌ Error procesando el archivo. Verifica las columnas de fechas y el separador. Detalle: {e}")

# =======================================================================
# 🗃️ 4. GRILLA GLOBAL DE SALIDA Y EXPORTACIÓN
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
    
    col_dl, col_cl = st.columns([1, 1])
    with col_dl:
        csv_data = st.session_state.historial_legalizaciones.to_csv(sep=";", index=False, encoding="latin-1")
        st.download_button(
            label="📥 Descargar Reporte Final (CSV para SICOMP)",
            data=csv_data,
            file_name=f"Legalizaciones_SICOMP_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_cl:
        if st.button("🗑️ Limpiar Grilla Actual", use_container_width=True):
            st.session_state.historial_legalizaciones = pd.DataFrame(columns=[
                "Fecha de pago", "numeral", "Valor", "Texto legalizacion", "saldo", "estado"
            ])
            st.rerun()
else:
    st.caption("🔍 Aún no hay registros procesados en la sesión actual.")
