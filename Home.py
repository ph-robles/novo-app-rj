import streamlit as st

st.set_page_config(page_title="Sites RJ", page_icon="📡")

st.image("logo.png", width=220)  # ajuste o tamanho que quiser

st.title("📡 Endereços dos Sites RJ — Novo App")

st.markdown("""
## Escolha uma opção no menu lateral 👇

### 🔍 Buscar por SIGLA  
Encontre informações completas sobre um site/ERB.

### 🧭 Buscar por ENDEREÇO  
Digite o endereço do cliente e veja os 3 sites mais próximos.
""")

st.caption("❤️ Desenvolvido por Raphael Robles")