import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein
from utils.cadeados_repo import buscar_cadeado, url_da_foto

st.set_page_config(page_title="Buscar por SIGLA • Site Radar", page_icon="📡", layout="wide")

# ... (seu CSS e sidebar iguais)

<<<<<<< HEAD
=======
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
    margin-bottom: 250px;
}

/* ----------------------------
   MODO COMPACTO PARA CELULAR
----------------------------- */
@media (max-width: 760px) {

    /* Sidebar fica mais larga (apenas ajuste solicitado) */
    [data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 136px !important;
        padding-top: 24px;
        padding-left: 6px;
        padding-right: 6px;
    }

    /* A logo se ajusta para 250px (pedido) */
    .sidebar-logo img {
        width: 80px !important;
    }

    /* Conteúdo oculto na sidebar compacta */
    .sidebar-content, .sidebar-text {
        display: none !important;
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
</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

# Sidebar com logo
with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("logo.png", width=300)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
#   FUNÇÕES AUXILIARES (LOCAIS)
# ==============================
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

# ==============================
#   CONTEÚDO — BUSCA POR SIGLA
# ==============================
>>>>>>> 5c380e73e06b21741f6a4fe5be918825f3c53c9c
st.title("🔍 Buscar por SIGLA")

df = carregar_dados()
acessos = carregar_acessos()

lista_siglas = sorted(df["sigla"].dropna().str.upper().unique().tolist())

sig = st.text_input("Digite a SIGLA")

def _get_val(dados, col):
    try:
        return dados[col].iloc[0]
    except Exception:
        return None

if sig:
    sig_n = normalizar_sigla(sig)

    # Match exato
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # Fuzzy
    if not achada and lista_siglas:
        achada = min(lista_siglas, key=lambda x: levenshtein(normalizar_sigla(x), sig_n))

    if achada:
        st.success(f"SIGLA encontrada: **{achada}**")
        dados = df[df["sigla"].str.upper() == achada]

        # Exibe a grid original (se quiser manter)
        st.dataframe(dados, use_container_width=True)

        # ========== CARD DE DETALHES (ajuste os nomes das colunas conforme seu df) ==========
        nome_site = _get_val(dados, "nome") or _get_val(dados, "site") or ""
        cidade = _get_val(dados, "cidade") or ""
        detentora = _get_val(dados, "detentora") or _get_val(dados, "operadora") or "—"
        endereco = _get_val(dados, "endereco") or _get_val(dados, "logradouro") or "—"
        capacitado = _get_val(dados, "capacitado") or "—"
        lat = _get_val(dados, "lat") or _get_val(dados, "latitude")
        lon = _get_val(dados, "lon") or _get_val(dados, "longitude")
        coords = f"{lat}, {lon}" if lat and lon else "—"

        st.markdown("### 📍 Detalhes")
        st.markdown(
            f"""
**{achada} — {cidade} - {nome_site or ""}**

- 🏢 **Detentora:** {detentora}  
- 📌 **Endereço:** {endereco}  
- 🧰 **Capacitado:** {str(capacitado).upper()}  
- 🧭 **Coordenadas:** {coords}
"""
        )

        # Técnicos
        if acessos is not None and not acessos.empty:
            tecs = (
                acessos[acessos["sigla"].str.upper() == achada]["tecnico"]
                .dropna().unique().tolist()
            )
            if tecs:
                st.info("👷 Técnicos liberados:\n" + "\n".join(f"- {t}" for t in tecs))
            else:
                st.info("Nenhum técnico cadastrado para esta SIGLA.")

        # 🔒 CADEADO
        st.markdown("### 🔒 Cadeado")
        cadeado = buscar_cadeado(achada)
        if cadeado:
            tipo = cadeado.get("tipo", "—")
            obs = cadeado.get("observacao", "")
            st.markdown(f"**Tipo de cadeado:** {tipo}")
            if obs:
                st.caption(f"Observação: {obs}")

            if cadeado.get("foto_path"):
                url = url_da_foto(cadeado["foto_path"])
                if url:
                    # Mostra a imagem e o link
                    st.image(url, caption=f"Cadeado - {achada}", use_container_width=True)
                    st.markdown(f"[🔗 Abrir imagem]({url})")
                else:
                    st.caption("Não foi possível gerar a URL da imagem (verifique bucket/políticas).")
        else:
            st.info("Nenhum registro de cadeado para esta SIGLA ainda.")

    else:
        st.error("Nenhuma SIGLA compatível encontrada.")