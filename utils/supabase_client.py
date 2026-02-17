import os
from supabase import create_client, Client

def get_supabase() -> Client:
    # Primeiro tenta pegar das variáveis do ambiente; no Streamlit, pode vir de st.secrets
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")  # para operações padrão
    return create_client(url, key)

def get_supabase_service() -> Client | None:
    # Para operações que precisem do service role (ex.: signed URL em bucket privado)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if key:
        return create_client(url, key)
    return None

def get_bucket_name() -> str:
    return os.getenv("SUPABASE_BUCKET_CADEADOS", "cadeados")

def bucket_publico() -> bool:
    return os.getenv("BUCKET_PUBLICO", "true").lower() == "true"