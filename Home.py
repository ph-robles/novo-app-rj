import streamlit as st

# =============================================================================
# CONFIG
# =============================================================================
st.set_page_config(page_title="Site Radar", page_icon="📡", layout="wide")

# =============================================================================
# ESTILOS GERAIS (Topbar, Hero, Cards, Botões)
# =============================================================================
STYLES = """
<style>
/* ===== Reset de margens principais para trabalhar com Topbar fixa ===== */
.main .block-container { padding-top: 86px; }

/* ===== Topbar fixa técnica ===== */
.topbar {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 64px;
    background: linear-gradient(90deg, rgba(15,18,26,0.85) 0%, rgba(22,27,37,0.85) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px;
    z-index: 9999;
}

/* Branding da Topbar */
.topbar .brand {
    display: inline-flex; align-items: center; gap: 12px;
    color: #E6ECF3; text-decoration: none;
}
.topbar .brand img { width: 28px; height: 28px; object-fit: contain; }
.topbar .brand .title { font-size: 18px; font-weight: 800; letter-spacing: .2px; }

/* Ações rápidas no topo (opcional) */
.topbar .actions {
    display: inline-flex; gap: 10px;
}
.topbar .actions a, .topbar .actions button {
    color: #C7D0DD; text-decoration: none; font-size: 14px;
    padding: 8px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.03);
    transition: all .15s ease;
}
.topbar .actions a:hover, .topbar .actions button:hover {
    color: #fff; background: rgba(255,255,255,0.06);
    transform: translateY(-1px);
}

/* ===== Ocultar Sidebar SÓ na Home (sua regra original) ===== */
[data-testid="stSidebar"] {display: none;}
[data-testid="stSidebarNav"] {display: none;}
[data-testid="stAppViewContainer"] {margin-left: 0;}
[data-testid="stHeader"] {margin-left: 0;}

/* ===== Hero ===== */
.hero {
    display: grid;
    grid-template-columns: 1.2fr .8fr;
    gap: 18px;
    align-items: center;
    margin-top: 4px;
}
@media (max-width: 900px) {
    .hero { grid-template-columns: 1fr; }
}
.hero-card {
    background: linear-gradient(180deg, rgba(28,34,48,0.75) 0%, rgba(24,30,43,0.65) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 22px 20px;
    color: #E6ECF3;
}
.hero h1 {
    font-size: 30px; font-weight: 800; margin: 0 0 8px 0;
}
.hero p {
    font-size: 15px; color: #B8C3D1; margin: 0;
}
.hero-right {
    background: radial-gradient(1200px 400px at 30% -20%, rgba(31,111,235,0.18), rgba(0,0,0,0) 60%),
                linear-gradient(180deg, rgba(22,28,41,0.8) 0%, rgba(18,22,33,0.8) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 18px;
}

/* ===== Cards Técnicos (métricas) ===== */
.tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 18px;
}
@media (max-width: 900px) {
    .tech-grid { grid-template-columns: 1fr; }
}
.tech-card {
    background: rgba(30,35,45,0.65);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 16px 18px;
    border-radius: 14px;
    color: #E6ECF3;
}
.tech-card h3 { margin: 0; font-size: 15px; font-weight: 700; color: #C9D3E0; }
.tech-number { font-size: 32px; font-weight: 800; margin-top: 6px; letter-spacing: .2px; }
.tech-sub { color: #9EABBB; font-size: 12.5px; margin-top: 4px; }

/* ===== Seções ===== */
.section-title {
    font-size: 18px; font-weight: 800; margin: 14px 0 10px 0;
}

/* ===== Botões de ação (override elegante do seu estilo) ===== */
div.stButton > button {
    background: #1f6feb;
    color: #fff;
    border-radius: 14px;
    padding: 14px 22px;
    font-size: 1.05rem;
    font-weight: 700;
    border: 1px solid rgba(255,255,255,0.06);
    width: 100%;
    transition: all 0.18s ease-in-out;
    box-shadow: 0px 6px 18px rgba(31, 111, 235, 0.25);
}
div.stButton > button:hover {
    background: #175bd0;
    transform: translateY(-2px);
    box-shadow: 0px 10px 22px rgba(31, 111, 235, 0.38);
}
div.stButton > button:active {
    transform: translateY(0) scale(.98);
    background: #114db7;
}

/* ===== Cards de ação ===== */
.action-card {
    background: linear-gradient(180deg, rgba(31,111,235,0.10) 0%, rgba(31,111,235,0.08) 100%);
    border: 1px solid rgba(31,111,235,0.25);
    border-radius: 14px;
    padding: 16px;
    color: #E6ECF3;
}
.action-card p { color: #BFD2F6; font-size: 13.5px; margin: 4px 0 14px 0; }

/* ===== Rodapé ===== */
.footer {
    color: #9EABBB; font-size: 12.5px; text-align: center; margin-top: 16px;
}

</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

# =============================================================================
# TOPBAR (logo + título; os itens de navegação aqui são visuais)
# =============================================================================
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <img src="logo.png" alt="logo" />
            <span class="title">Site Radar</span>
        </div>
        <div class="actions">
            <!-- Mantive botões visuais; a navegação real continua pelos botões com switch_page mais abaixo -->
            <span style="opacity:.75">v1.0 • Ambiente de Produção</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# HERO (título + descrição) — sem mexer na sua lógica de navegação
# =============================================================================
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
                <div class="action-card">
                    <b>🔍 Buscar por SIGLA</b>
                    <p>Encontre rapidamente a ERB pelo identificador.</p>
                    <div style="margin-top:8px;">__BTN_SIGLA__</div>
                </div>
                <div class="action-card">
                    <b>🧭 Buscar por ENDEREÇO</b>
                    <p>Retorne as ERBs mais próximas via geocodificação.</p>
                    <div style="margin-top:8px;">__BTN_ENDERECO__</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Renderizar os botões de ação (switch_page) exatamente como você já usa
# Usamos "st.columns" apenas para injetar os botões nos placeholders do HTML acima
c1, c2 = st.columns(2)
with c1:
    sigla_btn = st.button("🔍 Buscar por SIGLA", use_container_width=True, key="btn_sigla_top")
with c2:
    end_btn = st.button("🧭 Buscar por ENDEREÇO", use_container_width=True, key="btn_end_top")

# Injetar os botões no HTML do hero (substituição simples)
# Obs.: Streamlit não permite substituir HTML já renderizado, então repetimos os botões na seção abaixo
# e mantemos também uma área "Ações" ao final para UX consistente.

# =============================================================================
# CARDS TÉCNICOS (placeholders) — prontos para ligar em dados reais depois
# =============================================================================
st.markdown('<div class="section-title">📊 Visão geral</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="tech-grid">
        <div class="tech-card">
            <h3>Total de ERBs</h3>
            <div class="tech-number">—</div>
            <div class="tech-sub">Registros carregados</div>
        </div>
        <div class="tech-card">
            <h3>Com coordenadas</h3>
            <div class="tech-number">—</div>
            <div class="tech-sub">Lat/Lon válidos</div>
        </div>
        <div class="tech-card">
            <h3>Capacitados</h3>
            <div class="tech-number">—</div>
            <div class="tech-sub">Coluna + lista auxiliar</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# AÇÕES (repetição proposital abaixo do herói para usuários que rolem a página)
# =============================================================================
st.markdown("---")
st.markdown('<div class="section-title">⚡ Ações</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Buscar por SIGLA", use_container_width=True, key="btn_sigla_bottom") or sigla_btn:
        st.switch_page("pages/1_🔍_Busca_por_SIGLA.py")

with col2:
    if st.button("🧭 Buscar por ENDEREÇO", use_container_width=True, key="btn_end_bottom") or end_btn:
        st.switch_page("pages/2_🧭_Busca_por_ENDEREÇO.py")

# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("---")
st.markdown(
    '<div class="footer">❤️ Desenvolvido por Raphael Robles — © 2026 • Todos os direitos reservados 🚀</div>',
    unsafe_allow_html=True
)
