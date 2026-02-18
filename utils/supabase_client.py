# utils/supabase_client.py
import os
from typing import Optional
from supabase import create_client, Client

def _get_from_env() -> tuple[Optional[str], Optional[str]]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return url, key

def _get_from_streamlit_secrets() -> tuple[Optional[str], Optional[str]]:
    # Importa streamlit apenas se existir e se secrets estiverem configurados
    try:
        import streamlit as st
        if "supabase" in st.secrets:
            url = st.secrets["supabase"].get("url")
            key = st.secrets["supabase"].get("anon_key")
            return url, key
    except Exception:
        # Se não estiver rodando via streamlit, ignore
        pass
    return None, None

def get_client() -> Client:
    # 1) Primeiro tenta ENV (.env / variáveis do sistema)
    url, key = _get_from_env()

    # 2) Se não vier, tenta st.secrets (quando rodando via streamlit)
    if not url or not key:
        s_url, s_key = _get_from_streamlit_secrets()
        url = url or s_url
        key = key or s_key

    if not url or not key:
        raise RuntimeError(
            "Supabase URL/Key não configuradas. "
            "Defina SUPABASE_URL e SUPABASE_ANON_KEY no .env "
            "ou configure [supabase] em .streamlit/secrets.toml"
        )

    client = create_client(url, key)
    if client is None:
        raise RuntimeError("Falha ao criar cliente do Supabase (create_client retornou None).")
    return client