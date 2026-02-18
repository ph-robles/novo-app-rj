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
# ESTILOS GERAIS (Topbar, Hero, Cards) + Ocultar sidebar só na Home
# =============================================================================
STYLES = """
<style>
/* Empurra conteúdo por causa da topbar fixa */
.main .block-container { padding-top: 86px; }

/* ===== Topbar fixa ===== */
.topbar {
    position: fixed; top: 0; left: 0; width: 100%; height: 64px;
    background: linear-gradient(90deg, rgba(15,18,26,0.85) 0%, rgba(22,27,37,0.85) 100%);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px; z-index: 9999;
}
/* Branding da topbar: logo */
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

/* ===== Coluna direita do hero ===== */
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

/* ===== Paleta de sombras/glow ===== */
:root {
  --glow-blue: 0 0 0 2px rgba(31,111,235,.28), 0 10px 26px rgba(31,111,235,.30), 0 0 22px rgba(31,111,235,.45);
}

/* ===== Cartões clicáveis com st.page_link (Streamlit >= 1.33) ===== */
.page-link-card > div > a {
    display:block; width:100%; height:100%;
    background: linear-gradient(180deg, rgba(31,111,235,0.10) 0%, rgba(31,111,235,0.08) 100%) !important;
    border: 1px solid rgba(31,111,235,0.25) !important;
    color: #E6ECF3 !important;
    border-radius: 14px; padding: 16px; text-decoration:none !important;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease, background .15s ease;
    cursor: pointer;
}
.page-link-card > div > a:hover,
.page-link-card > div > a:focus-visible {
    transform: translateY(-2px);
    background: linear-gradient(180deg, rgba(31,111,235,0.14) 0%, rgba(31,111,235,0.12) 100%) !important;
    border-color: rgba(31,111,235,0.4) !important;
    box-shadow: var(--glow-blue);
    outline: none;
}
.page-link-card > div > a:active {
    transform: translateY(0) scale(.98);
}

/* ===== Fallback: botões ocultos (mantêm funcionalidade) ===== */
.fallback-actions [data-testid="stButton"] button {
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    padding: 0 !important; margin: 0 !important; border: 0 !important;
    pointer-events: none !important; overflow: hidden !important; clip: rect(0,0,0,0) !important;
}

/* ===== Visual dos cards no fallback (divs clicáveis por JS) ===== */
.fallback-card {
    background: linear-gradient(180deg, rgba(31,111,235,0.10) 0%, rgba(31,111,235,0.08) 100%);
    border: 1px solid rgba(31,111,235,0.25);
    color: #E6ECF3;
    border-radius: 14px;
    padding: 16px;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease, background .15s ease;
    cursor: pointer;
}
.fallback-card:hover,
.fallback-card:focus-visible {
    transform: translateY(-2px);
    background: linear-gradient(180deg, rgba(31,111,235,0.14) 0%, rgba(31,111,235,0.12) 100%);
    border-color: rgba(31,111,235,0.4);
    box-shadow: var(--glow-blue);
    outline: none;
}
.fallback-card:active { transform: translateY(0) scale(.98); }

/* ===== Rodapé ===== */
.footer { color: #9EABBB; font-size: 12.5px; text-align: center; margin-top: 16px; }
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

# =============================================================================
# TOPBAR (logo)
# =============================================================================
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <img src="logo.png" alt="Site Radar" />
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

total_erbs = int(len(df))
if lat_col and lon_col:
    df_coords = df.dropna(subset=[lat_col, lon_col]).copy()
    com_coord = int(len(df_coords))
else:
    df_coords = pd.DataFrame(columns=["lat", "lon"])
    com_coord = 0

YES = {"sim","s","yes","y","1","true","verdadeiro","ok","ativo","habilitado","cap","capacitado"}
def _is_yes(v) -> bool:
    try: return str(v).strip().lower() in YES
    except Exception: return False

cap_lista = carregar_capacitados_lista() or set()
if not isinstance(cap_lista, (set, list, tuple)): cap_lista = set(cap_lista)

sigla_upper  = df["sigla"].astype(str).str.upper() if "sigla" in df.columns else pd.Series([""]*len(df))
col_cap_bool = df["capacitado"].apply(_is_yes) if "capacitado" in df.columns else pd.Series([False]*len(df))
in_list_bool = sigla_upper.isin(cap_lista) if len(cap_lista) > 0 else pd.Series([False]*len(df))
cap_total    = int((col_cap_bool | in_list_bool).sum())

fmt = lambda n: f"{n:,}".replace(",", ".")

# =============================================================================
# HERO (com “Acesso rápido” — cards clicáveis via st.page_link ou fallback com JS)
# =============================================================================
left, right = st.columns([1.2, 0.8])
with left:
    st.markdown(
        """
        <div class="hero-card">
            <h1>📡 Site Radar</h1>
            <p>Localize ERBs por <b>SIGLA</b> ou por <b>ENDEREÇO</b>, gere links do Google Maps e visualize
            dados relevantes em segundos. Interface otimizada para campo e mobile.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown('<div class="hero-right"><div class="section-title">⚙️ Acesso rápido</div>', unsafe_allow_html=True)

    has_page_link = hasattr(st, "page_link")
    c1, c2 = st.columns(2)

    if has_page_link:
        # ====== CAMINHO 1: Streamlit recente — usa st.page_link (card 100% link) ======
        with c1:
            with st.container(key="card_sigla", border=False):
                st.markdown('<div class="page-link-card">', unsafe_allow_html=True)
                st.page_link(
                    "pages/1_🔍_Busca_por_SIGLA.py",
                    label="**🔍 Buscar por SIGLA**  \nEncontre rapidamente a ERB pelo identificador."
                )
                st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            with st.container(key="card_end", border=False):
                st.markdown('<div class="page-link-card">', unsafe_allow_html=True)
                st.page_link(
                    "pages/2_🧭_Busca_por_ENDEREÇO.py",
                    label="**🧭 Buscar por ENDEREÇO**  \nRetorne as ERBs mais próximas via geocodificação."
                )
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # ====== CAMINHO 2: Fallback — botões ocultos + card visual + JS para simular clique ======
        st.markdown('<div class="fallback-actions">', unsafe_allow_html=True)

        # Card SIGLA
        with c1:
            st.markdown(
                '<div class="fallback-card" id="card-sigla" tabindex="0">'
                '<strong>🔍 Buscar por SIGLA</strong><br/>Encontre rapidamente a ERB pelo identificador.'
                '</div>',
                unsafe_allow_html=True
            )
            sigla_clicked = st.button("open_sigla", key="open_sigla")  # rótulo = key para facilitar o JS
            if sigla_clicked:
                st.switch_page("pages/1_🔍_Busca_por_SIGLA.py")

        # Card ENDEREÇO
        with c2:
            st.markdown(
                '<div class="fallback-card" id="card-end" tabindex="0">'
                '<strong>🧭 Buscar por ENDEREÇO</strong><br/>Retorne as ERBs mais próximas via geocodificação.'
                '</div>',
                unsafe_allow_html=True
            )
            end_clicked = st.button("open_end", key="open_end")
            if end_clicked:
                st.switch_page("pages/2_🧭_Busca_por_ENDEREÇO.py")

        # --- Injeta JS para simular o clique no botão quando o card for pressionado ---
        import streamlit.components.v1 as components
        components.html(
            """
            <script>
            (function () {
              const map = {
                'card-sigla': 'open_sigla',
                'card-end':   'open_end'
              };

              function clickStreamlitButton(streamlitKey) {
                // Busca por botões do Streamlit e aciona o que contém o texto/label da key
                const buttons = window.parent.document.querySelectorAll('[data-testid="stButton"] button');
                for (const btn of buttons) {
                  const label = (btn.getAttribute('aria-label') || btn.textContent || '').trim();
                  if (label.includes(streamlitKey)) {
                    btn.click();
                    return true;
                  }
                }
                return false;
              }

              Object.entries(map).forEach(([cardId, key]) => {
                const el = document.getElementById(cardId);
                if (!el) return;

                const handler = (ev) => {
                  ev.preventDefault();
                  clickStreamlitButton(key);
                };
                el.addEventListener('click', handler);
                el.addEventListener('keydown', (e) => {
                  if (e.key === 'Enter' || e.key === ' ') handler(e);
                });
              });
            })();
            </script>
            """,
            height=0,
            width=0,
        )

        st.markdown('</div>', unsafe_allow_html=True)  # fecha .fallback-actions

    st.markdown('</div>', unsafe_allow_html=True)  # fecha .hero-right

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
