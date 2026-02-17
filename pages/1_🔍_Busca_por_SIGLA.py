import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein
import pandas as pd
import math

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
#   CONTEÚDO — BUSCA POR SIGLA
# ==============================
st.title("🔍 Buscar por SIGLA")

df = carregar_dados()
acessos = carregar_acessos()

# Lista de siglas únicas (UPPER) para facilitar match
lista_siglas = sorted(df["sigla"].dropna().astype(str).str.upper().unique().tolist())

sig = st.text_input("Digite a SIGLA")

def _format_coord(x):
    try:
        if pd.isna(x):
            return "—"
        return f"{float(x):.6f}"
    except Exception:
        return "—"

if sig:
    sig_n = normalizar_sigla(sig)

    # 1) Match exato (após normalizar)
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # 2) Fuzzy: pega a menor distância de edição
    if not achada and lista_siglas:
        achada = min(lista_siglas, key=lambda x: levenshtein(normalizar_sigla(x), sig_n))

    if achada:
        st.success(f"SIGLA encontrada: **{achada}**")
        # filtra linhas da sigla (case-insensitive)
        dados = df[df["sigla"].astype(str).str.upper() == achada].copy()

        # Mostra uma tabela resumida
        cols_show = [c for c in ["sigla", "nome", "detentora", "endereco", "lat", "lon", "capacitado"] if c in dados.columns]
        if cols_show:
            st.dataframe(dados[cols_show], use_container_width=True)
        else:
            st.dataframe(dados, use_container_width=True)

        # Cartões de detalhes por linha (caso haja mais de 1 site com a mesma sigla)
        st.markdown("### 📍 Detalhes")
        for _, row in dados.iterrows():
            sigla_row = str(row.get("sigla", "—"))
            nome_row = str(row.get("nome", "—"))
            det_row  = str(row.get("detentora", "—")) if pd.notna(row.get("detentora")) else "—"
            end_row  = str(row.get("endereco", "—"))
            lat_val  = row.get("lat")
            lon_val  = row.get("lon")
            cap_row  = str(row.get("capacitado", "—")) if pd.notna(row.get("capacitado")) else "—"

            st.markdown(f"**{sigla_row} — {nome_row}**")
            st.markdown(
                f"🏢 **Detentora:** {det_row}  \n"
                f"📌 **Endereço:** {end_row}  \n"
                f"🧰 **Capacitado:** {cap_row}  \n"
                f"🧭 **Coordenadas:** {_format_coord(lat_val)}, {_format_coord(lon_val)}"
            )

            # Botão Google Maps (só se tiver coordenadas válidas)
            try:
                if pd.notna(lat_val) and pd.notna(lon_val):
                    lat_f = float(lat_val)
                    lon_f = float(lon_val)
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}"
                    st.link_button("🗺️ Ver no Google Maps", maps_url, type="primary")
            except Exception:
                pass

            # Técnicos com acesso liberado (se houver aba acessos)
            if acessos is not None and not acessos.empty:
                tecs = (
                    acessos[acessos["sigla"].astype(str).str.upper() == sigla_row.upper()]
                    .get("tecnico", pd.Series(dtype="string"))
                    .dropna()
                    .unique()
                    .tolist()
                )
                if tecs:
                    st.info("👷 **Técnicos com acesso:**\n" + "\n".join([f"- {t}" for t in tecs]))
                else:
                    st.info("👷 Nenhum técnico com acesso cadastrado para esta SIGLA.")
            else:
                st.caption("ℹ️ Aba `acessos` não encontrada ou sem dados.")

            st.markdown("---")
    else:
        st.error("Nenhuma SIGLA compatível encontrada.")
