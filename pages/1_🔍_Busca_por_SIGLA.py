import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein

st.set_page_config(page_title="Buscar por SIGLA • Site Radar", page_icon="📡", layout="wide")

# ==============================
#   SIDEBAR PREMIUM (BLUR + MOBILE)
# ==============================
sidebar_style = """
<style>

/* Sidebar com efeito vidro fosco (BLUR) */
[data-testid="stSidebar"] {
    background: rgba(20, 25, 35, 0.55) !important;  /* cor translúcida */
    backdrop-filter: blur(12px);                    /* efeito blur macOS */
    -webkit-backdrop-filter: blur(12px);            /* suporte Safari */
    border-right: 1px solid rgba(255, 255, 255, 0.12);
    padding-top: 50px;
    transition: left 0.35s ease-in-out, background 0.3s ease;
}

/* Logo centralizada */
.sidebar-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
}

/* Conteúdo com respiro */
.sidebar-content {
    padding-left: 18px;
    padding-right: 18px;
}

/* ----------------------------
   SIDEBAR RESPONSIVA MOBILE
   Some em telas pequenas (< 760px)
----------------------------- */
@media (max-width: 760px) {
    /* Esconde a sidebar à esquerda (off-canvas) */
    [data-testid="stSidebar"] {
        position: fixed;
        left: -300px;
        top: 0;
        height: 100vh;
        width: 260px;
        z-index: 999;
    }

    /* Quando estiver 'aberta' (classe via botão JS) */
    [data-testid="stSidebar"].sidebar-open {
        left: 0;
    }

    /* Botão flutuante para abrir/fechar a sidebar */
    .open-sidebar-btn {
        position: fixed;
        top: 14px;
        left: 14px;
        background: #0084ff;
        color: #ffffff;
        border-radius: 50%;
        padding: 8px 12px;
        font-size: 22px;
        z-index: 1000;
        border: none;
        box-shadow: 0 6px 16px rgba(0, 132, 255, .45);
        transition: transform .15s ease-in-out, box-shadow .15s ease-in-out;
    }
    .open-sidebar-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0, 132, 255, .55);
        cursor: pointer;
    }
}

</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

# Botão flutuante (aparece apenas no mobile pelo @media)
# Obs: usamos um botão HTML com JS inline para alternar a classe .sidebar-open na sidebar.
st.markdown(
    """
    <button class="open-sidebar-btn" onclick="
        var sb = window.parent.document.querySelector('[data-testid=stSidebar]');
        if (sb) { sb.classList.toggle('sidebar-open'); }
    ">☰</button>
    """,
    unsafe_allow_html=True
)

# Sidebar com LOGO
with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("logo.png", width=140)
    st.markdown("</div>", unsafe_allow_html=True)
    # (Opcional) bloco de conteúdo
    # st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    # st.markdown("### 🔎 Busca por SIGLA")
    # st.markdown('</div>', unsafe_allow_html=True)

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

    # 1) Match exato
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # 2) Fuzzy (menor distância de edição)
    if not achada and lista_siglas:
        dists = [(s, levenshtein(normalizar_sigla(s), sig_n)) for s in lista_siglas]
        dists.sort(key=lambda x: x[1])
        achada = dists[0][0] if dists else None

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
                st.info("Nenhum técnico com acesso cadastrado para esta SIGLA.")
    else:
        st.error("Nenhuma SIGLA compatível encontrada.")