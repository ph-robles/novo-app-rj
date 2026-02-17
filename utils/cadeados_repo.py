import uuid
import io
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from .supabase_client import get_supabase, get_supabase_service, get_bucket_name, bucket_publico

TABLE = "cadeados"

def _nome_arquivo(sigla: str, filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rnd = str(uuid.uuid4())[:8]
    return f"{sigla.upper().strip()}/{ts}-{rnd}.{ext}"

def salvar_ou_atualizar_cadeado(sigla: str, tipo: str, foto_bytes: Optional[bytes], filename: Optional[str], observacao: str = "") -> Dict[str, Any]:
    """
    - Faz upload da foto (se enviada).
    - Upsert do registro em 'cadeados'.
    """
    supabase = get_supabase()
    bucket = get_bucket_name()
    foto_path = None

    # 1) Upload (se houver imagem)
    if foto_bytes and filename:
        path = _nome_arquivo(sigla, filename)
        # Upload
        supabase.storage.from_(bucket).upload(
            path=path,
            file=io.BytesIO(foto_bytes),
            file_options={"content-type": f"image/{filename.split('.')[-1].lower()}"}
        )
        foto_path = path

    # 2) Buscar registro existente
    existing = supabase.table(TABLE).select("*").eq("sigla", sigla.upper()).maybe_single().execute()
    if existing.data:
        payload = {"tipo": tipo, "observacao": observacao}
        if foto_path:
            payload["foto_path"] = foto_path
        res = supabase.table(TABLE).update(payload).eq("sigla", sigla.upper()).execute()
        return res.data[0] if res.data else {}
    else:
        payload = {"sigla": sigla.upper(), "tipo": tipo, "observacao": observacao, "foto_path": foto_path}
        res = supabase.table(TABLE).insert(payload).execute()
        return res.data[0] if res.data else {}

def buscar_cadeado(sigla: str) -> Optional[Dict[str, Any]]:
    supabase = get_supabase()
    res = supabase.table(TABLE).select("*").eq("sigla", sigla.upper()).maybe_single().execute()
    return res.data if res.data else None

def url_da_foto(foto_path: str) -> Optional[str]:
    """
    Retorna a URL para exibir a imagem:
    - Se bucket for público: public URL
    - Se bucket for privado: signed URL (precisa SERVICE ROLE no backend)
    """
    if not foto_path:
        return None
    supabase = get_supabase()
    bucket = get_bucket_name()

    if bucket_publico():
        # Público: public URL simples
        public_url = supabase.storage.from_(bucket).get_public_url(foto_path)
        # SDK v2 pode retornar dict/string, então normalizamos:
        if isinstance(public_url, dict):
            # pode vir como {"publicUrl": "..."} ou {"public_url": "..."}
            return public_url.get("publicUrl") or public_url.get("public_url")
        return public_url

    # Privado: signed URL (gera com service role)
    svc = get_supabase_service()
    if not svc:
        return None  # sem service role, não dá pra gerar signed url
    signed = svc.storage.from_(bucket).create_signed_url(foto_path, 3600)  # 1h
    if isinstance(signed, dict):
        return signed.get("signedUrl") or signed.get("signed_url")
    return signed