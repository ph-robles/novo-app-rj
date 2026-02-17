import streamlit as st
import pandas as pd
from urllib.parse import urlencode

# Seus utilitários existentes
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
st.set_page_config(page_title="Site Radar", page_icon="📡", layout="wide")


# =============================================================================
# QUERY PARAMS – wrappers (compatível com st.query_params e experimental)
# =============================================================================
def _get_params_dict() -> dict:
    """
    Retorna os query params como dict[str, str] (sem listas).
    Compatível com st.query_params e experimental_get_query_params.
    """
    try:
        # Streamlit moderno (st.query_params é um mapeamento mutável)
        return dict(st.query_params)
    except Exception:
        # Fallback para versões mais antigas
        raw = st.experimental_get_query_params()
        return {k: (v[-1] if isinstance(v, list) and v else v) for k, v in raw.items()}


def _set_params_dict(params: dict):
    """
    Seta os query params a partir de um dict[str, str].
    Compatível com st.query_params e experimental_set_query_params.
    """
    try:
        st.query_params.clear()
        st.query_params.from_dict(params)
    except Exception:
        st.experimental_set_query_params(**params)


def build_href(new_items: dict) -> str:
    """
    Constrói um href "?" com base nos params atuais + novos pares em `new_items`.
    - Preserva outros parâmetros
    - Sobrescreve os informados em new_items
    """
    params = _get_params_dict()
    params.update(new_items or {})
    return f"?{urlencode(params, doseq=True)}"


def go_home():
    """Vai para a Home via query params e dá rerun."""
    params = _get_params_dict()
    params["page"] = "home"
    _set_params_dict(params)
    st.rerun()


# =============================================================================
# ESTILOS (Sidebar + Chips + FAB)
# =============================================================================
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
   MODO MOBILE (mais confortável)
----------------------------- */
@media (max-width: 760px) {

    /* Sidebar um pouco mais larga para toque confortável */
    [data-testid="stSidebar"] {
        width: 112px !important;      /* ajuste entre 104–128px conforme seu gosto */
        min-width: 112px !important;
        padding-top: 20px;
        padding-left: 8px;
        padding-right: 8px;
    }

    /* Logo um pouco menor, mas com área de toque boa */
    .sidebar-logo img {
        width: 70px !important;
    }

    /* Oculte só textos longos; mantenha ícones/botões principais */
    .sidebar-text {
        display: none !important;
    }

    /* Alvos de toque maiores para links/botões da sidebar */
    .sidebar-item,
    .sidebar-link,
    .home-link,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] button {
        min-height: 44px;    /* guideline de toque */
        padding: 10px 8px;
        font-size: 0.95rem;
        border-radius: 10px;
    }

    /* Botão/Link Home estilizado */
    .home-link {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        font-weight: 600;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        transition: all .15s ease-in-out;
        color: inherit !important;
        text-decoration: none !important;
    }
    .home-link:hover {
        background: rgba(255,255,255,0.18);
        border-color: rgba(255,255,255,0.28);
        transform: translateY(-1px);
    }
}

/* ---------------------------------
   ESTILO DOS "CHIPS" DE SUGESTÕES
---------------------------------- */
#chips-scope { margin-top: .25rem; }
#chips-scope div[data-testid="stHorizontalBlock"] { row-gap: .5rem; }
#chips-scope div[data-testid="stButton"] > button {
  border-radius: 9999px;
  padding: .35rem .9rem;
  font-size: 0.92rem;
  line-height: 1rem;
  border: 1px solid rgba(49,51,63,0.25);
  background: rgba(49,51,63,0.04);
  color: inherit;
  cursor: pointer;
  transition: all .15s ease-in-out;
}
#chips-scope div[data-testid="stButton"] > button:hover {
  background: rgba(49,51,63,0.08);
  border-color: rgba(49,51,63,0.4);
  transform: translateY(-1px);
}
#chips-scope div[data-testid="stButton"] > button:active {
  transform: translateY(0px) scale(.98);
}
/* dark mode */
:root .st-dark #chips-scope div[data-testid="stButton"] > button {
  border-color: rgba(250, 250, 250, 0.18);
  background: rgba(250, 250, 250, 0.06);
}
:root .st-dark #chips-scope div[data-testid="stButton"] > button:hover {
  border-color: rgba(250, 250, 250, 0.35);
  background: rgba(250, 250, 250, 0.12);
}

/* Opcional: tornar uma área da sidebar “grudada” no topo */
.sticky-top { position: sticky; top: 8px; z-index: 2; }
</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

fab_style = """
<style>
.fab-home {
    position: fixed;
    right: 16px;
    bottom: 18px;
    z-index: 9999;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #2563eb;               /* azul */
    color: #fff !important;
    font-size: 22px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.28);
    border: none;
    text-decoration: none !important;
    transition: transform .12s ease, box-shadow .12s ease, opacity .2s ease;
}
.fab-home:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.32); }
.fab-home:active { transform: translateY(0) scale(.98); }

/* Em telas muito pequenas, dá um respiro nas margens */
@media (max-width: 420px) {
  .fab-home { right: 12px; bottom: 14px; }
}
</style>
"""
st.markdown(fab_style, unsafe_allow_html=True)


# =============================================================================
# SIDEBAR (logo + botão Home por query params)
# =============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        # Ajuste o caminho/arquivo da sua logo conforme o seu projeto
        st.image("logo.png", width=130)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sticky-top">', unsafe_allow_html=True)
        st.markdown(
            f'<a class="home-link" href="{build_href({"page": "home"})}">🏠 Home</a>',
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# BOTÃO FLUTUANTE (FAB) – Home por query params
# =============================================================================
def render_fab_home():
    st.markdown(
        f'<a class="fab-home" href="{build_href({"page": "home"})}" title="Ir para Home">🏠</a>',
        unsafe_allow_html=True
    )


# =============================================================================
# FUNÇÕES AUXILIARES DA PÁGINA DE BUSCA
# =============================================================================
def _format_coord(x):
    try:
        if pd.isna(x):
            return "—"
        return f"{float(x):.6f}"
    except Exception:
        return "—"


def _gerar_sugestoes(busca_raw: str, candidatos: list[str], limite: int = 8) -> list[str]:
    """
    Gera sugestões "parecidas" para a sigla digitada:
      1) Começa com...
      2) Contém...
      3) Fuzzy (Levenshtein <= 1)
    """
    if not busca_raw:
        return []

    bnorm = normalizar_sigla(busca_raw)
    pares = [(s, normalizar_sigla(s)) for s in candidatos]

    # 1) Começa com...
    pref = [s for s, n in pares if n.startswith(bnorm)]
    seen = set(pref)

    # 2) Contém...
    if len(pref) < limite:
        cont = [s for s, n in pares if (bnorm in n) and (s not in seen)]
        pref.extend(cont)
        seen.update(cont)

    # 3) Fuzzy leve (<= 1 edição)
    if len(pref) < limite:
        fuzzy = []
        for s, n in pares:
            if s in seen:
                continue
            d = levenshtein(n, bnorm)
            if d <= 1:
                fuzzy.append((d, s))
        fuzzy = [s for _, s in sorted(fuzzy, key=lambda x: (x[0], x[1]))]
        pref.extend(fuzzy)

    # Limita e mantém ordem
    return pref[:limite]


def _select_sugestao(value: str):
    # Callback dos chips: salva em session_state e sinaliza auto-busca
    st.session_state["busca_sigla_pending"] = value
    st.session_state["do_busca_sigla"] = True
    # O clique no botão já dispara um rerun automaticamente.


# =============================================================================
# PÁGINA: HOME (placeholder – substitua pelo seu conteúdo real)
# =============================================================================
def render_home():
    st.title("🏠 Home")
    st.write("Bem-vindo ao **Site Radar**. Selecione uma função no menu lateral.")
    # Acesso rápido para a página de busca por sigla:
    st.link_button("🔎 Ir para Buscar por SIGLA", build_href({"page": "buscar_sigla"}), type="primary")


# =============================================================================
# PÁGINA: BUSCAR POR SIGLA
# =============================================================================
def render_busca_sigla():
    st.title("🔍 Buscar por SIGLA")

    df = carregar_dados()
    acessos = carregar_acessos()

    # Lista de siglas únicas (UPPER) para facilitar match
    lista_siglas = sorted(df["sigla"].dropna().astype(str).str.upper().unique().tolist())

    # ---------- Estado inicial & hidratação ----------
    if "busca_sigla_input" not in st.session_state:
        st.session_state["busca_sigla_input"] = ""

    # Se um chip foi clicado, no ciclo anterior guardamos em 'pending':
    if "busca_sigla_pending" in st.session_state:
        st.session_state["busca_sigla_input"] = st.session_state.pop("busca_sigla_pending")

    # Se foi solicitado auto-executar a busca (por clique no chip), consome o flag aqui
    auto_trigger = st.session_state.pop("do_busca_sigla", False)

    # ---------- Container para resultados ----------
    result_ct = st.container()

    # ---------- Formulário com botão OK logo abaixo ----------
    with st.form("form_sigla", clear_on_submit=False):
        st.session_state["busca_sigla_input"] = st.text_input(
            "Digite a SIGLA do site/ERB",
            value=st.session_state.get("busca_sigla_input", "")
        )
        submitted = st.form_submit_button("OK")  # <= Botão OK

    busca_val = st.session_state.get("busca_sigla_input", "").strip()

    # ---------- Sugestões (chips) ----------
    if busca_val:
        sugestoes = _gerar_sugestoes(busca_val, lista_siglas, limite=8)
        if sugestoes:
            st.markdown("### 🔎 Sugestões (clique para buscar)")
            st.markdown('<div id="chips-scope">', unsafe_allow_html=True)
            cols = st.columns(max(2, min(6, len(sugestoes))))
            for i, s in enumerate(sugestoes):
                with cols[i % len(cols)]:
                    st.button(
                        s,
                        key=f"sug_{s}",
                        on_click=_select_sugestao,
                        args=(s,),
                    )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("Nenhuma sugestão encontrada para a sigla digitada.")

    # ---------- Executa busca se OK foi clicado OU se veio de um chip ----------
    do_search = (submitted or auto_trigger) and bool(busca_val)

    if do_search:
        busca_norm = normalizar_sigla(busca_val)

        # 1) Match exato (normalizado)
        achada = None
        for s in lista_siglas:
            if normalizar_sigla(s) == busca_norm:
                achada = s
                break

        # 2) Fuzzy leve (menor distância; <=1 geralmente cobre "faltando 1 letra")
        if not achada and lista_siglas:
            dists = [(s, levenshtein(normalizar_sigla(s), busca_norm)) for s in lista_siglas]
            # Ordena por distância e depois por ordem alfabética
            dists.sort(key=lambda x: (x[1], x[0]))
            achada = dists[0][0] if dists else None

        with result_ct:
            if achada:
                st.success(f"SIGLA encontrada: **{achada}**")

                dados = df[df["sigla"].astype(str).str.upper() == achada].copy()

                # Tabela resumida
                cols_show = [c for c in ["sigla", "nome", "detentora", "endereco", "lat", "lon", "capacitado"] if c in dados.columns]
                if cols_show:
                    st.dataframe(dados[cols_show], use_container_width=True)
                else:
                    st.dataframe(dados, use_container_width=True)

                # Cartões de detalhes (um por linha)
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

                    # Botão Google Maps (se coordenadas válidas)
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
    else:
        st.caption("Dica: digite parte da sigla e use as sugestões para agilizar a busca.")


# =============================================================================
# ROTEAMENTO POR QUERY PARAM: page
# =============================================================================
def main():
    render_sidebar()
    render_fab_home()

    # Lê o 'page' dos query params (default: 'buscar_sigla')
    page = _get_params_dict().get("page", "buscar_sigla")

    if page == "home":
        render_home()
    elif page == "buscar_sigla":
        render_busca_sigla()
    else:
        # Fallback caso venha um valor inesperado
        st.title("📄 Página")
        st.write("Parâmetro 'page' não reconhecido. Voltando para Home.")
        go_home()


if __name__ == "__main__":
    main()
