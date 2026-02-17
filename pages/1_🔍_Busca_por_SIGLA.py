import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein

# ==============================
#   SIDEBAR PREMIUM
# ==============================
sidebar_style = """
<style>

/* Fundo da sidebar */
[data-testid="stSidebar"] {
    background-color: #0e1117 !important;
    padding-top: 40px;
}

/* Logo centralizada */
.sidebar-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 25px;
}

/* Ajustes de conteúdo */
.sidebar-content {
    padding-left: 15px;
    padding-right: 15px;
}

</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("logo.png", width=140)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
#   PÁGINA PRINCIPAL
# ==============================

st.title("🔍 Buscar por SIGLA")

df = carregar_dados()
acessos = carregar_acessos()

lista_siglas = sorted(df["sigla"].dropna().str.upper().unique().tolist())

sig = st.text_input("Digite a SIGLA")

if sig:
    sig_n = normalizar_sigla(sig)

    # 1) Match exato
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # 2) Fuzzy
    if not achada:
        dists = [(s, levenshtein(normalizar_sigla(s), sig_n)) for s in lista_siglas]
        achada = min(dists, key=lambda x: x[1])[0] if dists else None

    if achada:
        st.success(f"SIGLA encontrada: **{achada}**")
        dados = df[df["sigla"].str.upper() == achada]
        st.dataframe(dados)

        if acessos is not None:
            tecs = acessos[acessos["sigla"].str.upper() == achada]["tecnico"].unique().tolist()
            st.info("👷 Técnicos liberados:\n" + "\n".join(f"- {t}" for t in tecs))
    else:
        st.error("Nenhuma SIGLA compatível encontrada.")