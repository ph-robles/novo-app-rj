import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein

with st.sidebar:
    st.image("logo.png", width=160)

# --- CSS PREMIUM PARA A SIDEBAR ---
sidebar_style = """
<style>

/* Fundo da sidebar */
[data-testid="stSidebar"] {
    background-color: #0e1117 !important;
    padding-top: 40px;
}

/* Logo centralizada e com padding */
.sidebar-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 25px;
}

/* Espacamento padrao */
.sidebar-content {
    padding-left: 15px;
    padding-right: 15px;
}

/* Remover borda superior chata do Streamlit */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Hover suave nos links (se você quiser futuramente adicionar menu) */
.sidebar-link:hover {
    opacity: 0.85;
}

</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("logo.png", width=140)
    st.markdown("</div>", unsafe_allow_html=True)


st.title("🔍 Busca por SIGLA")

df = carregar_dados()
acessos = carregar_acessos()

lista_siglas = sorted(df["sigla"].dropna().str.upper().unique().tolist())

sig = st.text_input("Digite a SIGLA")

if sig:
    sig_n = normalizar_sigla(sig)

    # match exato
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # fuzzy
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