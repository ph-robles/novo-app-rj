import streamlit as st
import pandas as pd
from utils.data_loader import carregar_dados, carregar_capacitados_lista
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

/* Badge de capacitado */
.cap-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #0b5;
    background: rgba(0,187,85,.12);
    border: 1px solid rgba(0,187,85,.35);
    margin-left: 8px;
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
#   AUXILIARES LOCAIS
# ==============================

YES = {"sim","s","yes","y","1","true","verdadeiro","ok","ativo","habilitado","cap","capacitado"}
def _is_yes(val) -> bool:
    try:
        return str(val).strip().lower() in YES
    except Exception:
        return False

def _cap_badge(is_cap: bool) -> str:
    return ' <span class="cap-badge">Capacitado</span>' if is_cap else ""

# ==============================
#   CONTEÚDO — BUSCA POR ENDEREÇO
# ==============================

st.title("🧭 Buscar por ENDEREÇO")

df = carregar_dados()

# Unifica status de capacitado:
# - Se houver coluna 'capacitado', interpreta SIM/NÃO
# - Se houver aba separada (carregar_capacitados_lista), une com OR
siglas_cap_set = carregar_capacitados_lista()  # pode ser None
siglas_upper = df["sigla"].astype(str).str.upper()
col_cap_bool = df["capacitado"].apply(_is_yes) if "capacitado" in df.columns else pd.Series([False]*len(df))
in_set_bool = siglas_upper.isin(siglas_cap_set) if siglas_cap_set else pd.Series([False]*len(df))
df["_is_capacitado"] = (col_cap_bool | in_set_bool)

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

    # 1) Top 3 por linha reta
    top3 = base.nsmallest(3, "dist_km").copy()

    # 2) Capacitado mais próximo (se houver)
    base_cap = base[base["_is_capacitado"] == True]
    forced_cap_row = None
    if not base_cap.empty:
        idx_min_cap = base_cap["dist_km"].idxmin()
        forced_cap_row = base_cap.loc[[idx_min_cap]].copy()

    # 3) Forçar inclusão do capacitado mais próximo no top3
    if forced_cap_row is not None:
        siglas_top3 = top3["sigla"].astype(str).str.upper().tolist()
        sigla_cap = str(forced_cap_row.iloc[0]["sigla"]).upper()

        if sigla_cap not in siglas_top3:
            union_df = pd.concat([top3, forced_cap_row], ignore_index=True)
            # Mantém ordem por menor distância linear
            union_df = union_df.sort_values("dist_km", ascending=True)
            # Remove duplicatas por SIGLA
            union_df = union_df.drop_duplicates(subset=["sigla"], keep="first")
            # Garante só 3
            if len(union_df) > 3:
                union_df = union_df.head(3)
            top3 = union_df.reset_index(drop=True)
        else:
            # já estava no top3, só garante ordenação por distância
            top3 = top3.sort_values("dist_km", ascending=True).reset_index(drop=True)

    # Distância via rota (OSRM)
    destinos = [(float(r["lat"]), float(r["lon"])) for _, r in top3.iterrows()]
    osrm_out = osrm_table(lat_cli, lon_cli, destinos)

    if osrm_out and len(osrm_out) == len(top3):
        top3["dist_rota_km"] = [x["distance_km"] for x in osrm_out]
        top3["tempo_min"]    = [x["duration_min"] for x in osrm_out]
    else:
        top3["dist_rota_km"] = None
        top3["tempo_min"]    = None

    # Tabela resumida com info útil
    mostrar_cols = [c for c in ["sigla","nome","detentora","endereco","lat","lon","capacitado","dist_km","dist_rota_km","tempo_min"] if c in top3.columns]
    st.markdown("### 📌 3 Sites mais próximos (com capacitado priorizado)")
    st.dataframe(top3[mostrar_cols], use_container_width=True)

    # ======= CARTÕES DETALHADOS =======
    for _, row in top3.iterrows():
        erb_lat = float(row["lat"])
        erb_lon = float(row["lon"])
        sigla   = str(row.get("sigla", "—"))
        nome    = str(row.get("nome", "—"))
        is_cap  = bool(row.get("_is_capacitado", False))
        cap_md  = _cap_badge(is_cap)

        rota    = f"https://www.google.com/maps/dir/?api=1&origin={lat_cli},{lon_cli}&destination={erb_lat},{erb_lon}&travelmode=driving"
        maps    = f"https://www.google.com/maps/search/?api=1&query={erb_lat},{erb_lon}"

        st.markdown(f"### **{sigla} — {nome}**{cap_md}", unsafe_allow_html=True)
        st.markdown(
            f"🗺️ **Linha reta:** {row['dist_km']:.3f} km  \n"
            f"🚗 **Distância por rota:** {row.get('dist_rota_km', '—')} km  \n"
            f"⏱ **Tempo estimado:** {row.get('tempo_min', '—')} min"
        )

        col1, col2 = st.columns(2)
        with col1:
            st.link_button("🗺️ Ver no Maps", maps)
        with col2:
            st.link_button("🚗 Traçar rota", rota)

        st.markdown("---")
