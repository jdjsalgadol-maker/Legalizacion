import streamlit as st
import pandas as pd
from datetime import date
from difflib import get_close_matches
import io

st.set_page_config(
    page_title="SICOMP — Legalización de Pagos",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0a0e17;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1f2d45;
    --accent: #0ea5e9;
    --accent2: #38bdf8;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --text: #e2e8f0;
    --text-muted: #64748b;
    --text-dim: #94a3b8;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
}

* { font-family: var(--sans) !important; }
code, .mono { font-family: var(--mono) !important; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem !important; max-width: 1400px !important; }

/* Header bar */
.app-header {
    background: linear-gradient(135deg, #0a0e17 0%, #111827 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.2rem 2rem;
    margin: 0 -2rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.app-header .logo {
    font-family: var(--mono) !important;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.1em;
}
.app-header .tagline {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
    margin-left: auto;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* Section labels */
.section-label {
    font-family: var(--mono) !important;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* Form panel */
.form-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
}

/* Inputs */
.stTextInput > label, .stNumberInput > label, .stDateInput > label,
.stSelectbox > label, .stTextArea > label {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 4px !important;
}

.stTextInput input, .stNumberInput input, .stDateInput input,
.stSelectbox select, .stTextArea textarea {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 0.75rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] span { color: var(--text) !important; }

/* Result cards */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.result-card.highlighted { border-color: var(--accent); background: rgba(14,165,233,0.05); }

/* Numeral badge */
.numeral-badge {
    display: inline-block;
    background: var(--accent);
    color: #000;
    font-family: var(--mono) !important;
    font-weight: 600;
    font-size: 1.1rem;
    padding: 0.35rem 0.9rem;
    border-radius: 6px;
    margin-right: 0.5rem;
}
.numeral-badge.secondary { background: var(--warning); }
.numeral-badge.anticipo { background: var(--danger); }

/* Glosa box */
.glosa-container {
    background: #060a12;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-top: 0.75rem;
}
.glosa-container.gastos { border-left-color: var(--warning); }
.glosa-text {
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    color: #93c5fd;
    line-height: 1.7;
    word-break: break-word;
    white-space: pre-wrap;
}
.glosa-text.gastos { color: #fcd34d; }

/* Provider match */
.provider-match {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-top: 0.5rem;
    font-size: 0.82rem;
    color: var(--success);
    font-family: var(--mono) !important;
}
.provider-nomatch {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-top: 0.5rem;
    font-size: 0.82rem;
    color: var(--danger);
    font-family: var(--mono) !important;
}

/* Metrics row */
.metrics-row { display: flex; gap: 1rem; margin: 1rem 0; }
.metric-box {
    flex: 1;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-box .metric-val {
    font-family: var(--mono) !important;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--accent);
}
.metric-box .metric-lbl {
    font-size: 0.68rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.2rem;
}

/* Status pill */
.status-pill {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.status-pill.ok { background: rgba(16,185,129,0.15); color: var(--success); border: 1px solid rgba(16,185,129,0.3); }
.status-pill.warn { background: rgba(245,158,11,0.15); color: var(--warning); border: 1px solid rgba(245,158,11,0.3); }
.status-pill.danger { background: rgba(239,68,68,0.15); color: var(--danger); border: 1px solid rgba(239,68,68,0.3); }

/* Button */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.35) !important;
    transform: translateY(-1px) !important;
}

/* Dataframe */
.stDataFrame { background: var(--surface) !important; border-radius: 10px !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; overflow: hidden; }

/* Divider */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* Toast alerts */
.stAlert {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* Copy button area */
.copy-hint {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-family: var(--mono) !important;
    margin-top: 0.4rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    padding: 0.3rem !important;
    gap: 0.25rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #000 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1.5rem 0 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <div class="logo">◈ SICOMP IA</div>
        <div class="tagline">Sistema de Legalización de Pagos al Exterior · Avidesa de Occidente</div>
    </div>
    <div class="status-dot"></div>
</div>
""", unsafe_allow_html=True)

# ─── Session state ──────────────────────────────────────────────────────────────
if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=[
        "Fecha de pago", "numeral", "Valor", "Texto legalizacion",
        "iddeclarante", "declarante", "saldo", "estado"
    ])

# ─── Load provider base ─────────────────────────────────────────────────────────
@st.cache_data
def cargar_proveedores():
    try:
        df = pd.read_excel("Base_proveedores.xlsx")
        df = df.dropna(subset=["Nombre del beneficiario o Girador"])
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
        df = df[df["Nombre del beneficiario o Girador"] != "NAN"]
        return df
    except Exception as e:
        st.error(f"Error cargando base de proveedores: {e}")
        return pd.DataFrame(columns=["Nombre del beneficiario o Girador", "CIUDAD", "PAÍS"])

df_prov = cargar_proveedores()

# ─── Helper functions ───────────────────────────────────────────────────────────
def buscar_proveedor(nombre_in, df):
    if df.empty or not nombre_in.strip():
        return None, None, None
    col = "Nombre del beneficiario o Girador"
    lista = df[col].tolist()
    matches = get_close_matches(nombre_in.upper(), lista, n=1, cutoff=0.45)
    if matches:
        nombre_exacto = matches[0]
        fila = df[df[col] == nombre_exacto].iloc[0]
        ciudad = fila.get("CIUDAD", "N/A")
        pais = fila.get("PAÍS", "N/A")
        return nombre_exacto, ciudad if ciudad != "NAN" else "N/A", pais if pais != "NAN" else "N/A"
    return None, None, None

def calcular_numeral(fecha_bl: date, fecha_pago: date, tiene_gastos: bool):
    dias = (fecha_pago - fecha_bl).days
    if dias < 0:
        tipo = "ANTICIPO"
        num_fob = "2017"
        num_gastos = ""
        concepto = "Giro previo al embarque (Anticipo)"
    elif dias <= 30:
        tipo = "CORTO PLAZO"
        num_fob = "2015"
        num_gastos = "2016" if tiene_gastos else ""
        concepto = "Importación a Corto Plazo (≤ 30 días)"
    else:
        tipo = "FINANCIADO"
        num_fob = "2022"
        num_gastos = "2016" if tiene_gastos else ""
        concepto = "Operación Financiada (> 30 días)"
    return num_fob, num_gastos, dias, tipo, concepto

def fmt_usd(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def construir_texto(valor, factura, producto, motonave, bl, fecha_bl, proveedor, tipo_pago="FOB"):
    val_fmt = fmt_usd(valor)
    mn_txt = f" MN {motonave}" if motonave and motonave.strip() else ""
    fecha_fmt = fecha_bl.strftime("%d/%m/%Y")
    if tipo_pago == "GASTOS":
        return (f"PAGO X USD {val_fmt} CORRESPONDIENTE A GASTOS DE FLETE Y SEGURO "
                f"FV N° {factura} IMPO {producto}{mn_txt} "
                f"BL N° {bl} DEL {fecha_fmt} PROVEEDOR {proveedor}")
    else:
        return (f"PAGO X USD {val_fmt} CORRESPONDIENTE A FV N° {factura} "
                f"IMPO {producto}{mn_txt} "
                f"BL N° {bl} DEL {fecha_fmt} PROVEEDOR {proveedor}")

# ─── Layout ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["✦  Nueva Legalización", "◈  Historial de Registros"])

with tab1:
    col_form, col_gap, col_result = st.columns([1.05, 0.05, 1.4])

    # ── LEFT: Input form ────────────────────────────────────────────────────────
    with col_form:
        st.markdown('<div class="section-label">◦ Identificación</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            id_decl = st.text_input("NIT Declarante", value="815000863", key="nit")
        with c2:
            declarante = st.text_input("Nombre Declarante", value="AVIDESA DE OCCIDENTE SA", key="decl").upper()

        st.markdown('<div class="section-label" style="margin-top:1.5rem">◦ Datos del Proveedor</div>', unsafe_allow_html=True)

        prov_input = st.text_input(
            "Proveedor Exterior (búsqueda inteligente)",
            placeholder="Ej: Aollen, Seaboard, ADM Americas…",
            key="prov_input"
        )

        # Provider match result
        nombre_mapeado = ciudad_mapeada = pais_mapeado = None
        if prov_input.strip():
            nombre_mapeado, ciudad_mapeada, pais_mapeado = buscar_proveedor(prov_input, df_prov)
            if nombre_mapeado:
                st.markdown(f"""
                <div class="provider-match">
                    ✓ &nbsp;<strong>{nombre_mapeado}</strong><br>
                    <span style="opacity:.7">📍 {ciudad_mapeada} · {pais_mapeado}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="provider-nomatch">
                    ✕ &nbsp;No encontrado — se usará tal como se digitó<br>
                    <span style="opacity:.7">{prov_input.upper()}</span>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:1.5rem">◦ Documentos de la Operación</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            factura = st.text_input("N° Factura Comercial", placeholder="Ej: FV-101749", key="fv").upper()
        with c4:
            bl = st.text_input("BL / Guía Aérea", placeholder="Ej: COSU6435517900", key="bl").upper()

        producto = st.text_input("Mercancía IMPO", placeholder="Ej: METHIONINA, LYSINE, FRIJOL AMERICANO", key="prod").upper()
        motonave = st.text_input("Motonave (MN) — opcional", placeholder="Ej: TIAN XIANG", key="mn").upper()

        st.markdown('<div class="section-label" style="margin-top:1.5rem">◦ Fechas y Valores</div>', unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            fecha_bl = st.date_input("Fecha Embarque (BL)", value=date.today(), key="fbl")
        with c6:
            fecha_pago = st.date_input("Fecha de Pago", value=date.today(), key="fpago")

        c7, c8 = st.columns(2)
        with c7:
            valor_fob = st.number_input("Valor FOB (USD)", min_value=0.0, format="%.2f", key="vfob")
        with c8:
            valor_gastos = st.number_input("Gastos Flete/Seguro (USD)", min_value=0.0, format="%.2f", key="vgas")

        st.markdown("<br>", unsafe_allow_html=True)
        procesar = st.button("⟶  Generar Texto de Legalización", use_container_width=True)

    # ── RIGHT: Results ──────────────────────────────────────────────────────────
    with col_result:
        st.markdown('<div class="section-label">◦ Panel de Resultados</div>', unsafe_allow_html=True)

        proveedor_final = nombre_mapeado if nombre_mapeado else (prov_input.upper() if prov_input.strip() else None)

        if valor_fob > 0 and proveedor_final:
            num_fob, num_gastos, dias, tipo, concepto = calcular_numeral(
                fecha_bl, fecha_pago, valor_gastos > 0
            )

            # Status badge
            if tipo == "ANTICIPO":
                pill_cls = "danger"
            elif tipo == "FINANCIADO":
                pill_cls = "warn"
            else:
                pill_cls = "ok"

            st.markdown(f"""
            <div style="margin-bottom:1rem">
                <span class="status-pill {pill_cls}">{tipo}</span>
                <span style="font-size:0.8rem; color:var(--text-muted); margin-left:.5rem">{concepto}</span>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            st.markdown(f"""
            <div class="metrics-row">
                <div class="metric-box">
                    <div class="metric-val">{dias}</div>
                    <div class="metric-lbl">Días operación</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{num_fob}</div>
                    <div class="metric-lbl">Numeral FOB</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{num_gastos if valor_gastos > 0 else "—"}</div>
                    <div class="metric-lbl">Numeral Gastos</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">USD {fmt_usd(valor_fob + valor_gastos)}</div>
                    <div class="metric-lbl">Total operación</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Build texts
            texto_fob = construir_texto(valor_fob, factura, producto, motonave, bl, fecha_bl, proveedor_final, "FOB")

            st.markdown(f"""
            <div class="result-card highlighted">
                <div style="display:flex; align-items:center; gap:.5rem; margin-bottom:.5rem">
                    <span class="numeral-badge">{num_fob}</span>
                    <span style="font-size:0.78rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:.1em">Texto Legalización · FOB</span>
                </div>
                <div class="glosa-container">
                    <div class="glosa-text">{texto_fob}</div>
                </div>
                <div class="copy-hint">▴ Seleccionar todo el texto y copiar (Ctrl+A, Ctrl+C)</div>
            </div>
            """, unsafe_allow_html=True)

            texto_gastos = None
            if valor_gastos > 0:
                texto_gastos = construir_texto(valor_gastos, factura, producto, motonave, bl, fecha_bl, proveedor_final, "GASTOS")
                st.markdown(f"""
                <div class="result-card">
                    <div style="display:flex; align-items:center; gap:.5rem; margin-bottom:.5rem">
                        <span class="numeral-badge secondary">{num_gastos}</span>
                        <span style="font-size:0.78rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:.1em">Texto Legalización · Gastos</span>
                    </div>
                    <div class="glosa-container gastos">
                        <div class="glosa-text gastos">{texto_gastos}</div>
                    </div>
                    <div class="copy-hint">▴ Seleccionar todo el texto y copiar (Ctrl+A, Ctrl+C)</div>
                </div>
                """, unsafe_allow_html=True)

            if procesar:
                f_pago_fmt = fecha_pago.strftime("%d/%m/%Y")
                numerales = num_fob + ("," + num_gastos if valor_gastos > 0 and num_gastos else "")
                fila_fob = {
                    "Fecha de pago": f_pago_fmt,
                    "numeral": numerales,
                    "Valor": valor_fob,
                    "Texto legalizacion": texto_fob,
                    "iddeclarante": id_decl,
                    "declarante": declarante,
                    "saldo": "",
                    "estado": "CREADA"
                }
                st.session_state.historial = pd.concat(
                    [st.session_state.historial, pd.DataFrame([fila_fob])],
                    ignore_index=True
                )
                if valor_gastos > 0 and texto_gastos:
                    fila_gas = {
                        "Fecha de pago": f_pago_fmt,
                        "numeral": num_gastos,
                        "Valor": valor_gastos,
                        "Texto legalizacion": texto_gastos,
                        "iddeclarante": id_decl,
                        "declarante": declarante,
                        "saldo": "",
                        "estado": "CREADA"
                    }
                    st.session_state.historial = pd.concat(
                        [st.session_state.historial, pd.DataFrame([fila_gas])],
                        ignore_index=True
                    )
                st.success(f"✓ {'2 registros guardados' if valor_gastos > 0 else '1 registro guardado'} en el historial de sesión.")

        elif procesar:
            st.warning("⚠ Complete el valor FOB y el nombre del proveedor para generar el texto.")
        else:
            st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; color:var(--text-muted)">
                <div style="font-size:2.5rem; margin-bottom:1rem; opacity:.3">◈</div>
                <div style="font-family:var(--mono); font-size:0.8rem; letter-spacing:.15em; text-transform:uppercase">
                    Complete el formulario para<br>generar los textos de legalización
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── Tab 2: History ─────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.historial.empty:
        st.markdown('<div class="section-label">◦ Registros de la Sesión</div>', unsafe_allow_html=True)

        df_hist = st.session_state.historial.copy()
        st.dataframe(df_hist, use_container_width=True, height=400)

        col_dl1, col_dl2, col_cl = st.columns([1, 1, 2])
        with col_dl1:
            # Excel download
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_hist.to_excel(writer, index=False, sheet_name="Legalizaciones")
            buf.seek(0)
            st.download_button(
                "⬇ Descargar Excel",
                data=buf.getvalue(),
                file_name="legalizaciones_sicomp.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col_dl2:
            # CSV download
            csv = df_hist.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button(
                "⬇ Descargar CSV",
                data=csv,
                file_name="legalizaciones_sicomp.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_cl:
            if st.button("✕  Limpiar Historial", use_container_width=True):
                st.session_state.historial = pd.DataFrame(columns=df_hist.columns)
                st.rerun()

        st.markdown(f"""
        <div style="margin-top:1rem; font-family:var(--mono); font-size:0.75rem; color:var(--text-muted)">
            {len(df_hist)} registro(s) · Total USD {fmt_usd(df_hist['Valor'].sum())}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:4rem 1rem; color:var(--text-muted)">
            <div style="font-family:var(--mono); font-size:0.8rem; letter-spacing:.15em; text-transform:uppercase">
                El historial está vacío.<br>Procese registros en la pestaña Nueva Legalización.
            </div>
        </div>
        """, unsafe_allow_html=True)
