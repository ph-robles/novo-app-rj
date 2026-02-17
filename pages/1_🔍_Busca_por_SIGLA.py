import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein

st.title("🔍 Busca por SIGLA")

df = carregar_dados()
acessos = carregar_acessos()

lista_siglas = sorted(df["sigla"].dropna().str.upper().unique().tolist())

sig = st.text_input("Digite a SIGLA")

if sig:
    sig_n = normalizar_sigla(sig)

    # match exato
    achada = None
    for s in lista_siglas:
        if normalizar_sigla(s) == sig_n:
            achada = s
            break

    # fuzzy
    if not achada:
        dists = [(s, levenshtein(normalizar_sigla(s), sig_n)) for s in lista_siglas]
        achada = min(dists, key=lambda x: x[1])[0] if dists else None

    if achada:
        st.success(f"SIGLA encontrada: **{achada}**")
        dados = df[df["sigla"].str.upper() == achada]
        st.dataframe(dados)

        if acessos is not None:
            tecs = acessos[acessos["sigla"].str.upper() == achada]["tecnico"].unique().tolist()
            st.info("👷 Técnicos liberados:\n" + "\n".join(f"- {t}" for t in tecs))
    else:
        st.error("Nenhuma SIGLA compatível encontrada.")