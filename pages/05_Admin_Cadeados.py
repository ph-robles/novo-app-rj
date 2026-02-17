import streamlit as st
from utils.cadeados_repo import salvar_ou_atualizar_cadeado, buscar_cadeado, url_da_foto

st.set_page_config(page_title="Cadeados • Admin", page_icon="🔒", layout="wide")

st.title("🔒 Cadastro de Cadeado por SIGLA")

sigla = st.text_input("SIGLA (ex.: ARC)")
tipo = st.selectbox("Tipo de cadeado", ["Bluetooth", "Segredo", "Outro"], index=0)
observacao = st.text_area("Observações (opcional)")
foto = st.file_uploader("Foto do cadeado", type=["jpg", "jpeg", "png", "webp"])

col1, col2 = st.columns(2)
with col1:
    if st.button("Salvar/Atualizar"):
        if not sigla.strip():
            st.error("Informe a SIGLA.")
        else:
            foto_bytes, filename = (foto.read(), foto.name) if foto else (None, None)
            rec = salvar_ou_atualizar_cadeado(sigla, tipo, foto_bytes, filename, observacao)
            if rec:
                st.success("Cadeado salvo com sucesso!")
            else:
                st.warning("Não foi possível salvar. Revise os dados.")

with col2:
    if st.button("Ver registro atual"):
        if not sigla.strip():
            st.error("Informe a SIGLA.")
        else:
            rec = buscar_cadeado(sigla)
            if not rec:
                st.info("Nenhum registro para esta SIGLA.")
            else:
                st.json(rec)
                if rec.get("foto_path"):
                    url = url_da_foto(rec["foto_path"])
                    if url:
                        st.image(url, caption=f"Cadeado - {sigla}", use_container_width=True)
                    else:
                        st.caption("Não foi possível gerar a URL da imagem.")