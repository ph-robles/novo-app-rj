import streamlit as st
from utils.data_loader import carregar_dados, carregar_acessos
from utils.helpers import normalizar_sigla, levenshtein
from utils.cadeados_repo import buscar_cadeado, url_da_foto

st.set_page_config(page_title="Buscar por SIGLA • Site Radar", page_icon="📡", layout="wide")

# ... (seu CSS e sidebar iguais)

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