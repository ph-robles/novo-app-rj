import streamlit as st
from utils.data_loader import carregar_dados
from utils.geocode import geocode_address
from utils.helpers import haversine_km
from utils.osrm_tools import osrm_table

st.set_page_config(page_title="Buscar por ENDEREÇO • Site Radar", page_icon="📡", layout="wide")

# ==============================
#   SIDEBAR PREMIUM COMPACTA (BLUR + MOBILE SAFE)
# ==============================
sidebar_style = """
<style>

/* Sidebar geral */
[data-testid="stSidebar"] {
    background: rgba(20, 25, 35, 0.55) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 40px;
    width: 240px !important;
}

/* Logo centralizada */
.sidebar-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
}

/* ----------------------------
   SIDEBAR COMPACTA MOBILE
----------------------------- */
@media (max-width: 760px) {

    [data-testid="stSidebar"] {
        width: 80px !important;
        min-width: 80px !important;
        padding-top: 24px;
        padding-left: 6px;
        padding-right: 6px;
    }

    .sidebar-logo img {
        width: 60px !important;
    }

    .sidebar-content, .sidebar-text, .sidebar-extra {
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
st.title("🧭 Buscar por ENDEREÇO")

df = carregar_dados()

end = st.text_input("Digite o endereço do cliente:")

if end:
    geo = geocode_address(end)
    if not geo:
        st.error("Endereço não encontrado. Tente incluir número, bairro e cidade (RJ).")
    else:
        lat, lon, form = geo
        st.success(f"Endereço localizado: **{form}**")

        base = df.dropna(subset=["lat", "lon"]).copy()
        base["dist_km"] = haversine_km(lat, lon, base["lat"], base["lon"])
        top3 = base.nsmallest(3, "dist_km").copy()

        destinos = [(r["lat"], r["lon"]) for _, r in top3.iterrows()]
        osrm_out = osrm_table(lat, lon, destinos)

        if osrm_out and len(osrm_out) == len(top3):
            top3["dist_rota_km"] = [x["distance_km"] for x in osrm_out]
            top3["tempo_min"]    = [x["duration_min"] for x in osrm_out]

        st.dataframe(top3, use_container_width=True)

        for _, r in top3.iterrows():
            maps = f"https://www.google.com/maps/search/?api=1&query={r['lat']},{r['lon']}"
            rota = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={r['lat']},{r['lon']}"
            st.link_button(f"📍 Ver {r['sigla']} no Maps", maps)
            st.link_button("🚗 Traçar rota", rota)
            st.markdown("---")