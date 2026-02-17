import streamlit as st
from utils.data_loader import carregar_dados
from utils.geocode import geocode_address
from utils.helpers import haversine_km
from utils.osrm_tools import osrm_table

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

/* Conteúdo */
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

st.title("🧭 Buscar por ENDEREÇO")

df = carregar_dados()

end = st.text_input("Digite o endereço do cliente:")

if end:
    geo = geocode_address(end)
    if not geo:
        st.error("Endereço não encontrado.")
    else:
        lat, lon, form = geo
        st.success(f"Endereço encontrado: **{form}**")

        base = df.dropna(subset=["lat", "lon"]).copy()
        base["dist_km"] = haversine_km(lat, lon, base["lat"], base["lon"])

        top3 = base.nsmallest(3, "dist_km").copy()

        destinos = [(r["lat"], r["lon"]) for _, r in top3.iterrows()]
        osrm_out = osrm_table(lat, lon, destinos)

        top3["dist_rota_km"]   = [x["distance_km"] for x in osrm_out]
        top3["tempo_min"]      = [x["duration_min"] for x in osrm_out]

        st.dataframe(top3)

        for _, r in top3.iterrows():
            maps = f"https://www.google.com/maps/search/?api=1&query={r['lat']},{r['lon']}"
            st.link_button(f"📍 Ver {r['sigla']} no Google Maps", maps)