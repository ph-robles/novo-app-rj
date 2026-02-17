import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein

st.set_page_config(page_title="Buscar por SIGLA • Site Radar", page_icon="📡", layout="wide")

# ==============================
#   SIDEBAR PREMIUM COMPACTA (BLUR + MOBILE SAFE)
# ==============================
sidebar_style = """
<style>

/* Sidebar geral (desktop) */
[data-testid="stSidebar"] {
    background: rgba(20, 25, 35, 0.55) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 40px;
    width: 240px !important;
}

/* LOGO centralizada */
.sidebar-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
}

/* ----------------------------
   MODO COMPACTO PARA CELULAR
----------------------------- */
@media (max-width: 760px) {

    /* Sidebar fica estreita */
    [data-testid="stSidebar"] {
        width: 80px !important;
        min-width: 80px !important;
        padding-top: 24px;
        padding-left: 6px;
        padding-right: 6px;
    }

    /* A logo se ajusta */
    .sidebar-logo img {
        width: 60px !important;
    }

    /* Conteúdo oculto na sidebar compacta */
    .sidebar-content, .sidebar-text {
        display: none !important;
    }
}

</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

# Sidebar com logo
with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("logo.png", width=130)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
#   CONTEÚDO DA PÁGINA
# ==============================
st.title("🔍 Buscar por SIGLA")

df = carregar_dados()
acessos = carregar_acessos()

lista_siglas = sorted(df["sigla"].dropna().str.upper().unique().tolist())

sig = st.text_input("Digite a SIGLA")

if sig:
    sig_n = normalizar_sigla(sig)

    # Match exato
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # Fuzzy
    if not achada and lista_siglas:
        achada = min(lista_siglas, key=lambda x: levenshtein(normalizar_sigla(x), sig_n))

    if achada:
        st.success(f"SIGLA encontrada: **{achada}**")
        dados = df[df["sigla"].str.upper() == achada]
        st.dataframe(dados, use_container_width=True)

        if acessos is not None and not acessos.empty:
            tecs = (
                acessos[acessos["sigla"].str.upper() == achada]["tecnico"]
                .dropna().unique().tolist()
            )
            if tecs:
                st.info("👷 Técnicos liberados:\n" + "\n".join(f"- {t}" for t in tecs))
            else:
                st.info("Nenhum técnico cadastrado para esta SIGLA.")
    else:
        st.error("Nenhuma SIGLA compatível encontrada.")