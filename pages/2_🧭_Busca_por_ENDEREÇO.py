import streamlit as st
import pandas as pd
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

/* Sidebar compacta no celular */
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
#   CONTEÚDO — BUSCA POR ENDEREÇO
# ==============================

st.title("🧭 Buscar por ENDEREÇO")

df = carregar_dados()

# Criamos um container para os resultados
result_ct = st.container()

# ============= FORMULÁRIO COM BOTÃO OK =============
with st.form("form_endereco", clear_on_submit=False):
    endereco_cliente = st.text_input(
        "Digite o endereço completo (rua, número, bairro, cidade)"
    )
    submitted = st.form_submit_button("OK")  # <= Botão OK

# Se não clicou OK, não faz nada ainda
if not submitted:
    st.caption("Dica: digite um endereço e clique em **OK**.")
    st.stop()

# ==============================
#   PROCESSAR BUSCA APÓS OK
# ==============================

with result_ct:
    if not endereco_cliente.strip():
        st.error("❌ Digite um endereço válido antes de continuar.")
        st.stop()

    with st.spinner("🔎 Localizando endereço..."):
        geo = geocode_address(endereco_cliente)

    if not geo:
        st.error("❌ Não foi possível localizar o endereço informado.")
        st.stop()

    lat_cli, lon_cli, form = geo
    st.success(f"Endereço encontrado:\n\n**{form}**")
    st.write(f"🧭 **Coordenadas:** {lat_cli:.6f}, {lon_cli:.6f}")

    # Garantir que existam ERBs válidas
    base = df.dropna(subset=["lat", "lon"]).copy()
    if base.empty:
        st.error("⚠ Nenhuma ERB possui coordenadas válidas na planilha.")
        st.stop()

    # Calcular distâncias em linha reta
    base["dist_km"] = haversine_km(lat_cli, lon_cli, base["lat"], base["lon"])

    # Top 3 por linha reta
    top3 = base.nsmallest(3, "dist_km").copy()

    # Distância via rota (OSRM)
    destinos = [(float(r["lat"]), float(r["lon"])) for _, r in top3.iterrows()]
    osrm_out = osrm_table(lat_cli, lon_cli, destinos)

    if osrm_out and len(osrm_out) == len(top3):
        top3["dist_rota_km"] = [x["distance_km"] for x in osrm_out]
        top3["tempo_min"]    = [x["duration_min"] for x in osrm_out]
    else:
        top3["dist_rota_km"] = None
        top3["tempo_min"]    = None

    st.markdown("### 📌 3 Sites mais próximos")
    st.dataframe(top3, use_container_width=True)

    # ======= CARTÕES DETALHADOS =======
    for _, row in top3.iterrows():
        erb_lat = float(row["lat"])
        erb_lon = float(row["lon"])
        sigla   = row["sigla"]
        nome    = row["nome"]
        rota    = f"https://www.google.com/maps/dir/?api=1&origin={lat_cli},{lon_cli}&destination={erb_lat},{erb_lon}&travelmode=driving"
        maps    = f"https://www.google.com/maps/search/?api=1&query={erb_lat},{erb_lon}"

        st.markdown(f"### **{sigla} — {nome}**")
        st.markdown(
            f"🗺️ **Linha reta:** {row['dist_km']:.3f} km  \n"
            f"🚗 **Distância por rota:** {row.get('dist_rota_km', '—')} km  \n"
            f"⏱ **Tempo estimado:** {row.get('tempo_min', '—')} min  \n"
        )

        col1, col2 = st.columns(2)
        with col1:
            st.link_button("🗺️ Ver no Maps", maps)
        with col2:
            st.link_button("🚗 Traçar rota", rota)

        st.markdown("---")
