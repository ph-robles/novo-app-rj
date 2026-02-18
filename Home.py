import streamlit as st
import pandas as pd
import numpy as np

# === Integração com dados reais ===
from utils.data_loader import carregar_dados, carregar_capacitados_lista

# =============================================================================
# CONFIG
# =============================================================================
st.set_page_config(page_title="Home • Site Radar", page_icon="📡", layout="wide")

# =============================================================================
# ESTILOS GERAIS (Topbar, Hero, Cards, Botões) + Ocultar sidebar só na Home
# =============================================================================
STYLES = """
<style>
/* Empurra conteúdo por causa da topbar fixa */
.main .block-container { padding-top: 86px; }

/* ===== Topbar fixa técnica ===== */
.topbar {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 64px;
    background: linear-gradient(90deg, rgba(15,18,26,0.85) 0%, rgba(22,27,37,0.85) 100%);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px; z-index: 9999;
}
/* Branding da topbar: apenas a logo */
.topbar .brand { display: inline-flex; align-items: center; gap: 10px; }
.topbar .brand img {
    height: 32px; width: auto; object-fit: contain;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,.25));
}
.topbar .actions { color: #C7D0DD; font-size: 14px; opacity: .75; }

/* ===== Ocultar Sidebar SÓ na Home ===== */
[data-testid="stSidebar"] {display: none;}
[data-testid="stSidebarNav"] {display: none;}
[data-testid="stAppViewContainer"] {margin-left: 0;}
[data-testid="stHeader"] {margin-left: 0;}

/* ===== Hero ===== */
.hero {
    display: grid; grid-template-columns: 1.2fr .8fr; gap: 18px; align-items: center; margin-top: 4px;
}
@media (max-width: 900px) { .hero { grid-template-columns: 1fr; } }
.hero-card {
    background: linear-gradient(180deg, rgba(28,34,48,0.75) 0%, rgba(24,30,43,0.65) 100%);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 22px 20px; color: #E6ECF3;
}
.hero h1 { font-size: 30px; font-weight: 800; margin: 0 0 8px 0; }
.hero p { font-size: 15px; color: #B8C3D1; margin: 0; }
.hero-right {
    background: radial-gradient(1200px 400px at 30% -20%, rgba(31,111,235,0.18), rgba(0,0,0,0) 60%),
                linear-gradient(180deg, rgba(22,28,41,0.8) 0%, rgba(18,22,33,0.8) 100%);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px 18px;
}

/* ===== Cards Técnicos (métricas) ===== */
.tech-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 18px; }
@media (max-width: 900px) { .tech-grid { grid-template-columns: 1fr; } }
.tech-card {
    background: rgba(30,35,45,0.65); backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.08); padding: 16px 18px; border-radius: 14px; color: #E6ECF3;
}
.tech-card h3 { margin: 0; font-size: 15px; font-weight: 700; color: #C9D3E0; }
.tech-number { font-size: 32px; font-weight: 800; margin-top: 6px; letter-spacing: .2px; }
.tech-sub { color: #9EABBB; font-size: 12.5px; margin-top: 4px; }

/* ===== Seções ===== */
.section-title { font-size: 18px; font-weight: 800; margin: 14px 0 10px 0; }

/* ===== Cartões clicáveis ===== */
a.card-link { text-decoration: none; }
a.card-link .action-card {
    background: linear-gradient(180deg, rgba(31,111,235,0.10) 0%, rgba(31,111,235,0.08) 100%);
    border: 1px solid rgba(31,111,235,0.25); border-radius: 14px; padding: 16px; color: #E6ECF3;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease, background .15s ease;
    display: block;
}
a.card-link .action-card:hover {
    transform: translateY(-2px);
    background: linear-gradient(180deg, rgba(31,111,235,0.14) 0%, rgba(31,111,235,0.12) 100%);
    border-color: rgba(31,111,235,0.4);
    box-shadow: 0 10px 22px rgba(31,111,235,.22);
}
.action-card p { color: #BFD2F6; font-size: 13.5px; margin: 4px 0 0 0; }

/* ===== Rodapé ===== */
.footer { color: #9EABBB; font-size: 12.5px; text-align: center; margin-top: 16px; }
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

# =============================================================================
# TOPBAR (apenas logo 'logo.png')
# =============================================================================
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <img src="logo.png" alt="logo">
        </div>
        <div class="actions">v1.0 • Ambiente de Produção</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# INTEGRAÇÃO COM DADOS REAIS
# =============================================================================
df = carregar_dados()

# Detecta colunas de coordenadas e padroniza
lat_col, lon_col = None, None
for cand in (("lat", "lon"), ("latitude", "longitude"), ("Lat", "Lon"), ("LAT", "LON")):
    if all(c in df.columns for c in cand):
        lat_col, lon_col = cand
        break

# Contadores básicos
total_erbs = int(len(df))

if lat_col and lon_col:
    df_coords = df.dropna(subset=[lat_col, lon_col]).copy()
    com_coord = int(len(df_coords))
else:
    df_coords = pd.DataFrame(columns=["lat", "lon"])
    com_coord = 0

# Capacitados: coluna 'capacitado' (sim/não) OU presença na lista auxiliar
YES = {"sim","s","yes","y","1","true","verdadeiro","ok","ativo","habilitado","cap","capacitado"}
def _is_yes(v) -> bool:
    try: return str(v).strip().lower() in YES
    except Exception: return False

cap_lista = carregar_capacitados_lista() or set()
if not isinstance(cap_lista, (set, list, tuple)):
    cap_lista = set(cap_lista)

sigla_upper  = df["sigla"].astype(str).str.upper() if "sigla" in df.columns else pd.Series([""]*len(df))
col_cap_bool = df["capacitado"].apply(_is_yes) if "capacitado" in df.columns else pd.Series([False]*len(df))
in_list_bool = sigla_upper.isin(cap_lista) if len(cap_lista) > 0 else pd.Series([False]*len(df))
cap_total    = int((col_cap_bool | in_list_bool).sum())

# Helper de formatação (pt-BR: milhar com ponto)
fmt = lambda n: f"{n:,}".replace(",", ".")

# =============================================================================
# HERO (com “Acesso rápido” — CARDS CLICÁVEIS)
# =============================================================================
# Importante: use os títulos exatos das páginas no href de ?page=...
#   - 🔍 Busca por SIGLA
#   - 🧭 Buscar por ENDEREÇO
st.markdown(
    """
    <div class="hero">
        <div class="hero-card">
            <h1>📡 Site Radar</h1>
            <p>Localize ERBs por <b>SIGLA</b> ou por <b>ENDEREÇO</b>, gere links do Google Maps e visualize
            dados relevantes em segundos. Interface otimizada para campo e mobile.</p>
        </div>
        <div class="hero-right">
            <div class="section-title">⚙️ Acesso rápido</div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <a class="card-link" href="?page=%F0%9F%94%8D%20Busca%20por%20SIGLA">
                    <div class="action-card">
                        <b>🔍 Buscar por SIGLA</b>
                        <p>Encontre rapidamente a ERB pelo identificador.</p>
                    </div>
                </a>
                <a class="card-link" href="?page=%F0%9F%A7%AD%20Buscar%20por%20ENDERE%C3%87O">
                    <div class="action-card">
                        <b>🧭 Buscar por ENDEREÇO</b>
                        <p>Retorne as ERBs mais próximas via geocodificação.</p>
                    </div>
                </a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# CARDS TÉCNICOS (com dados reais)
# =============================================================================
st.markdown('<div class="section-title">📊 Visão geral</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="tech-grid">
        <div class="tech-card">
            <h3>Total de ERBs</h3>
            <div class="tech-number">{fmt(total_erbs)}</div>
            <div class="tech-sub">Registros carregados</div>
        </div>
        <div class="tech-card">
            <h3>Com coordenadas</h3>
            <div class="tech-number">{fmt(com_coord)}</div>
            <div class="tech-sub">Lat/Lon válidos</div>
        </div>
        <div class="tech-card">
            <h3>Capacitados</h3>
            <div class="tech-number">{fmt(cap_total)}</div>
            <div class="tech-sub">Coluna <code>capacitado</code> + lista auxiliar</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# Gráfico por detentora (Top 8) — se existir a coluna
# =============================================================================
if "detentora" in df.columns and not df["detentora"].dropna().empty:
    st.markdown('<div class="section-title">🏢 ERBs por detentora (Top 8)</div>', unsafe_allow_html=True)
    top_det = (
        df["detentora"]
        .astype(str).str.strip().replace({"": "—"})
        .value_counts().head(8).sort_values(ascending=True)
    )
    st.bar_chart(top_det, use_container_width=True, height=260)
else:
    st.caption("Sem coluna **detentora** na base para gerar o gráfico.")

# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("---")
st.markdown(
    '<div class="footer">❤️ Desenvolvido por Raphael Robles — © 2026 • Todos os direitos reservados 🚀</div>',
    unsafe_allow_html=True
)
