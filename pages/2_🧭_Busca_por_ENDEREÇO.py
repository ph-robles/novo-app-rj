import streamlit as st
from utils.data_loader import carregar_dados
from utils.geocode import geocode_address
from utils.helpers import haversine_km
from utils.osrm_tools import osrm_table

st.set_page_config(page_title="Buscar por ENDEREÇO • Site Radar", page_icon="📡", layout="wide")

# ==============================
#   SIDEBAR PREMIUM (BLUR + MOBILE)
# ==============================
sidebar_style = """
<style>

/* Sidebar com efeito vidro fosco (BLUR) */
[data-testid="stSidebar"] {
    background: rgba(20, 25, 35, 0.55) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
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
----------------------------- */
@media (max-width: 760px) {
    [data-testid="stSidebar"] {
        position: fixed;
        left: -300px;
        top: 0;
        height: 100vh;
        width: 260px;
        z-index: 999;
    }
    [data-testid="stSidebar"].sidebar-open {
        left: 0;
    }

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

# Botão hambúrguer (mobile)
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
    # st.markdown("### 🧭 Busca por ENDEREÇO")
    # st.markdown('</div>', unsafe_allow_html=True)

# ==============================
#   CONTEÚDO DA PÁGINA
# ==============================
st.title("🧭 Buscar por ENDEREÇO")

df = carregar_dados()

end = st.text_input("Digite o endereço do cliente:")

if end:
    geo = geocode_address(end)
    if not geo:
        st.error("Endereço não encontrado. Tente detalhar (rua, número, bairro, cidade).")
    else:
        lat, lon, form = geo
        st.success(f"Endereço encontrado: **{form}**")

        base = df.dropna(subset=["lat", "lon"]).copy()
        if base.empty:
            st.warning("Nenhuma ERB com coordenadas válidas na planilha.")
        else:
            base["dist_km"] = haversine_km(lat, lon, base["lat"], base["lon"])
            top3 = base.nsmallest(3, "dist_km").copy()

            # Distância/tempo por rota (OSRM)
            destinos = [(float(r["lat"]), float(r["lon"])) for _, r in top3.iterrows()]
            osrm_out = osrm_table(lat, lon, destinos)

            if osrm_out and len(osrm_out) == len(top3):
                top3["dist_rota_km"] = [x["distance_km"] for x in osrm_out]
                top3["tempo_min"]    = [x["duration_min"] for x in osrm_out]
            else:
                top3["dist_rota_km"] = None
                top3["tempo_min"]    = None

            st.dataframe(top3, use_container_width=True)

            for _, r in top3.iterrows():
                maps = f"https://www.google.com/maps/search/?api=1&query={r['lat']},{r['lon']}"
                rota = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={r['lat']},{r['lon']}&travelmode=driving"
                st.link_button(f"📍 Ver {r['sigla']} no Maps", maps, type="secondary")
                st.link_button(f"🚗 Traçar rota", rota)
                st.markdown("---")