import streamlit as st

st.set_page_config(page_title="Site Radar", page_icon="📡", layout="wide")

# OCULTAR SIDEBAR SÓ NA HOME
hide_menu_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stAppViewContainer"] {margin-left: 0;}
        [data-testid="stHeader"] {margin-left: 0;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# LOGO (opcional)
st.image("logo.png", width=220)

st.title("📡 Site Radar")
st.markdown("### Selecione uma opção abaixo:")

# CSS PREMIUM PARA BOTÕES DA HOME
button_style = """
<style>

div.stButton > button {
    background-color: #0084ff;
    color: white;
    border-radius: 14px;
    padding: 14px 24px;
    font-size: 1.2rem;
    font-weight: 600;
    border: none;
    width: 100%;
    transition: all 0.2s ease-in-out;
    box-shadow: 0px 3px 10px rgba(0, 132, 255, 0.3);
}

div.stButton > button:hover {
    background-color: #006ddb;
    transform: translateY(-3px);
    box-shadow: 0px 5px 18px rgba(0, 132, 255, 0.45);
}

div.stButton > button:active {
    transform: scale(0.97);
    background-color: #005bb8;
}

</style>
"""
st.markdown(button_style, unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Buscar por SIGLA", use_container_width=True):
        st.switch_page("pages/1_🔍_Busca_por_SIGLA.py")

with col2:
    if st.button("🧭 Buscar por ENDEREÇO", use_container_width=True):
        st.switch_page("pages/2_🧭_Busca_por_ENDEREÇO.py")

=============================================================================
# INTEGRAÇÃO COM DADOS REAIS
# =============================================================================
df = carregar_dados()

# Detecta colunas de coordenadas e padroniza
lat_col, lon_col = None, None
for cand in (("lat", "lon"), ("latitude", "longitude"), ("Lat", "Lon"), ("LAT", "LON")):
    if all(c in df.columns for c in cand):
        lat_col, lon_col = cand
        break

total_erbs = int(len(df))
if lat_col and lon_col:
    df_coords = df.dropna(subset=[lat_col, lon_col]).copy()
    com_coord = int(len(df_coords))
else:
    df_coords = pd.DataFrame(columns=["lat", "lon"])
    com_coord = 0

YES = {"sim","s","yes","y","1","true","verdadeiro","ok","ativo","habilitado","cap","capacitado"}
def _is_yes(v) -> bool:
    try: return str(v).strip().lower() in YES
    except Exception: return False

cap_lista = carregar_capacitados_lista() or set()
if not isinstance(cap_lista, (set, list, tuple)): cap_lista = set(cap_lista)

sigla_upper  = df["sigla"].astype(str).str.upper() if "sigla" in df.columns else pd.Series([""]*len(df))
col_cap_bool = df["capacitado"].apply(_is_yes) if "capacitado" in df.columns else pd.Series([False]*len(df))
in_list_bool = sigla_upper.isin(cap_lista) if len(cap_lista) > 0 else pd.Series([False]*len(df))
cap_total    = int((col_cap_bool | in_list_bool).sum())

fmt = lambda n: f"{n:,}".replace(",", ".")



=============================================================================
# CARDS TÉCNICOS (dados reais)
# =============================================================================
st.markdown('<div class="section-title">📊 Visão geral</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="tech-grid">
        <div class="tech-card">
            <h3>Total de ERBs</h3>
            <div class="tech-number">{fmt(total_erbs)}</div>
            <div class="tech-sub">Registros carregados</div>
        </div>
        <div class="tech-card">
            <h3>Com coordenadas</h3>
            <div class="tech-number">{fmt(com_coord)}</div>
            <div class="tech-sub">Lat/Lon válidos</div>
        </div>
        <div class="tech-card">
            <h3>Capacitados</h3>
            <div class="tech-number">{fmt(cap_total)}</div>
            <div class="tech-sub">Coluna <code>capacitado</code> + lista auxiliar</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



st.markdown(
    '<div class="footer">❤️ Desenvolvido por Raphael Robles — © 2026 • Todos os direitos reservados 🚀</div>',
    unsafe_allow_html=True
)


