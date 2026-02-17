import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Set

EXCEL_PATH = Path("enderecos.xlsx")

# =========================================================
#  Helpers
# =========================================================

def _coerce_float_series(s: pd.Series) -> pd.Series:
    """
    Converte série para float, ignorando valores inválidos.
    Qualquer texto não numérico vira NaN em vez de erro.
    """
    if s is None:
        return pd.Series(dtype=float)

    # Converte para string, limpa vírgula e tenta float
    return (
        s.astype(str)
         .str.strip()
         .str.replace(",", ".", regex=False)
         .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "-": pd.NA, "—": pd.NA})
         .apply(lambda x: float(x) if _is_float(x) else pd.NA)
         .astype(float)
    )

def _is_float(x) -> bool:
    """Retorna True se x puder ser convertido para float."""
    try:
        float(x)
        return True
    except:
        return False

def _find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Acha coluna por nome ou similaridade (case-insensitive)."""
    cols = {c.lower(): c for c in df.columns}
    # Match exato primeiro
    for cand in candidates:
        lc = cand.lower()
        if lc in cols:
            return cols[lc]

    # Senão busca por "contém"
    for col in df.columns:
        lc = col.lower()
        for cand in candidates:
            if cand.lower() in lc:
                return col

    return None


# =========================================================
#  Carregador principal — Aba ENDERECOS
# =========================================================

@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    """
    Lê 'enderecos.xlsx' > aba 'enderecos'
    Normaliza colunas para:
      sigla, nome, endereco, detentora, lat, lon, capacitado
    Trata coordenadas inválidas (viram NaN).
    """

    # ---------- Arquivo existe? ----------
    if not EXCEL_PATH.exists():
        st.error("❌ Arquivo `enderecos.xlsx` não foi encontrado na raiz do projeto.")
        st.stop()

    # ---------- Ler aba principal ----------
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="enderecos", engine="openpyxl")
    except ValueError:
        st.error("❌ A aba **enderecos** não existe no arquivo.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro ao ler o Excel: {e}")
        st.stop()

    df.columns = df.columns.astype(str).str.strip().str.lower()

    # ---------- Detectar colunas ----------
    col_sig = _find_col(df, ["sigla", "sigla_da_torre"])
    col_nome = _find_col(df, ["nome", "nome_da_torre"])
    col_end  = _find_col(df, ["endereco", "endereço"])
    col_det  = _find_col(df, ["detentora"])
    col_lat  = _find_col(df, ["lat", "latitude"])
    col_lon  = _find_col(df, ["lon", "longitude"])
    col_cap  = _find_col(df, ["capacitado", "habilitado", "ativo"])

    missing = []
    if not col_sig: missing.append("sigla")
    if not col_nome: missing.append("nome")
    if not col_end: missing.append("endereco")
    if not col_lat: missing.append("lat")
    if not col_lon: missing.append("lon")

    if missing:
        st.error("❌ Colunas essenciais faltando na aba `enderecos`:\n" +
                 "\n".join(f"- {m}" for m in missing))
        st.write("Colunas detectadas:", df.columns.tolist())
        st.stop()

    # ---------- Construção final ----------
    out = pd.DataFrame()
    out["sigla"]     = df[col_sig].astype("string").str.strip()
    out["nome"]      = df[col_nome].astype("string").str.strip()
    out["endereco"]  = df[col_end].astype("string").str.strip()
    out["detentora"] = df[col_det].astype("string").str.strip() if col_det else pd.NA
    out["capacitado"] = df[col_cap].astype("string").str.strip() if col_cap else pd.NA

    # ---------- Coordenadas seguras ----------
    out["lat"] = _coerce_float_series(df[col_lat])
    out["lon"] = _coerce_float_series(df[col_lon])

    return out


# =========================================================
#  Carregar acessos (se existir)
# =========================================================

@st.cache_data(show_spinner=False)
def carregar_acessos() -> Optional[pd.DataFrame]:
    """
    Lê aba 'acessos', detecta colunas e filtra status 'ok'.
    """
    if not EXCEL_PATH.exists():
        return None

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="acessos", engine="openpyxl")
    except:
        return None

    df.columns = df.columns.astype(str).str.strip().str.lower()

    col_sig = _find_col(df, ["sigla", "sigla_da_torre"])
    col_tec = _find_col(df, ["tecnico", "técnico", "colaborador"])
    col_sta = _find_col(df, ["status", "situacao", "situação"])

    if not col_sig or not col_tec:
        return None

    df_out = pd.DataFrame()
    df_out["sigla"] = df[col_sig].astype("string").str.strip()
    df_out["tecnico"] = df[col_tec].astype("string").str.strip()

    if col_sta:
        mask_ok = df[col_sta].astype(str).str.strip().str.lower().isin(["ok", "liberado", "ativo"])
        df_out = df_out[mask_ok]

    df_out = df_out.dropna(subset=["sigla", "tecnico"]).reset_index(drop=True)
    return df_out if not df_out.empty else None
