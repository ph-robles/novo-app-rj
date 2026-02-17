# utils/data_loader.py
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Set

EXCEL_PATH = Path("enderecos.xlsx")

# =========================
# Helpers internos
# =========================
def _coerce_float_series(s: pd.Series) -> pd.Series:
    """Converte série para float com segurança (troca vírgula por ponto)."""
    if s is None:
        return pd.Series(dtype=float)
    return (
        s.astype(str)
         .str.strip()
         .str.replace(",", ".", regex=False)
         .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
         .astype(float)
    )

def _find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Retorna o nome da primeira coluna existente no DF que casa com a lista de candidatos (case-insensitive)."""
    cols = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in cols:
            return cols[key]
    # tenta por 'in' (contains) quando não achar exato
    for c in df.columns:
        lc = c.strip().lower()
        for cand in candidates:
            key = cand.strip().lower()
            if key in lc:
                return c
    return None

# =========================
# Carregadores principais
# =========================
@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    """
    Lê a aba 'enderecos' do Excel e normaliza colunas para:
      - sigla
      - nome
      - endereco
      - detentora
      - lat
      - lon
      - capacitado (opcional)
    Faz autodetecção de nomes alternativos e converte lat/lon para float.
    """
    if not EXCEL_PATH.exists():
        st.error("❌ Arquivo `enderecos.xlsx` não foi encontrado na raiz do projeto.")
        st.stop()

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="enderecos", engine="openpyxl")
    except ValueError:
        st.error("❌ A aba **enderecos** não foi encontrada no arquivo `enderecos.xlsx`.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro ao ler o Excel: {e}")
        st.stop()

    # Normaliza cabeçalhos
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # Detecta colunas
    col_sigla = _find_col(df, ["sigla", "sigla_da_torre", "site", "torre"])
    col_nome  = _find_col(df, ["nome", "nome_da_torre", "descricao", "descrição"])
    col_end   = _find_col(df, ["endereco", "endereço", "address", "end"])
    col_det   = _find_col(df, ["detentora", "operadora", "donodosite"])
    col_lat   = _find_col(df, ["lat", "latitude"])
    col_lon   = _find_col(df, ["lon", "long", "longitude"])
    col_cap   = _find_col(df, ["capacitado", "capacitacao", "habilitado", "ativo"])

    # Valida essenciais
    missing = []
    if not col_sigla: missing.append("sigla (ex.: sigla / sigla_da_torre)")
    if not col_nome:  missing.append("nome (ex.: nome / nome_da_torre)")
    if not col_end:   missing.append("endereco (ex.: endereço / endereco)")
    if not col_lat:   missing.append("lat (ex.: lat / latitude)")
    if not col_lon:   missing.append("lon (ex.: lon / longitude)")

    if missing:
        st.error(
            "❌ Colunas essenciais ausentes na aba `enderecos`:\n\n"
            + "\n".join([f"- {m}" for m in missing])
            + "\n\n👉 Verifique os nomes das colunas na planilha."
        )
        st.write("Colunas detectadas no arquivo:", list(df.columns))
        st.stop()

    # Monta DF normalizado
    out = pd.DataFrame()
    out["sigla"]     = df[col_sigla].astype("string").str.strip()
    out["nome"]      = df[col_nome].astype("string").str.strip()
    out["endereco"]  = df[col_end].astype("string").str.strip()
    out["detentora"] = df[col_det].astype("string").str.strip() if col_det else pd.NA

    # lat/lon seguros
    out["lat"] = _coerce_float_series(df[col_lat])
    out["lon"] = _coerce_float_series(df[col_lon])

    # capacitado é opcional
    out["capacitado"] = df[col_cap].astype("string").str.strip() if col_cap else pd.NA

    return out


@st.cache_data(show_spinner=False)
def carregar_acessos() -> Optional[pd.DataFrame]:
    """
    Lê a aba 'acessos' (opcional).
    Esperado:
      - sigla (ou variantes)
      - tecnico (ou variantes: técnico, colaborador)
      - status (filtra 'ok', case-insensitive)
    Retorna DataFrame filtrado ou None.
    """
    if not EXCEL_PATH.exists():
        return None

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="acessos", engine="openpyxl")
    except ValueError:
        return None
    except Exception:
        return None

    if df is None or df.empty:
        return None

    df.columns = df.columns.astype(str).str.strip().str.lower()

    col_sig = _find_col(df, ["sigla", "sigla_da_torre", "site", "torre"])
    col_tec = _find_col(df, ["tecnico", "técnico", "colaborador", "nome_tecnico"])
    col_sta = _find_col(df, ["status", "situacao", "situação"])

    if not col_sig or not col_tec:
        return None

    df_out = pd.DataFrame()
    df_out["sigla"]   = df[col_sig].astype("string").str.strip()
    df_out["tecnico"] = df[col_tec].astype("string").str.strip()

    if col_sta:
        # filtra 'ok'
        mask_ok = (
            df[col_sta]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["ok", "liberado", "aprovado", "ativo"])
        )
        df_out = df_out[mask_ok]

    df_out = df_out.dropna(subset=["sigla", "tecnico"]).reset_index(drop=True)
    return df_out if not df_out.empty else None


@st.cache_data(show_spinner=False)
def carregar_capacitados_lista() -> Optional[Set[str]]:
    """
    (Opcional) Lê uma aba com SIGLAs capacitados (se existir).
    Nomes aceitos de aba: 'capacitados', 'capacitacao', 'cap_ativos'
    Colunas aceitas: 'sigla' e opcional 'status/capacitado/ativo'
    Retorna set de SIGLAs em upper() ou None.
    """
    if not EXCEL_PATH.exists():
        return None

    candidate_sheets = ["capacitados", "capacitacao", "cap_ativos"]
    for sh in candidate_sheets:
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sh, engine="openpyxl")
        except ValueError:
            continue
        except Exception:
            continue

        if df is None or df.empty:
            continue

        df.columns = df.columns.astype(str).str.strip().str.lower()
        col_sig = _find_col(df, ["sigla", "sigla_da_torre", "site", "torre"])
        col_sta = _find_col(df, ["status", "capacitado", "ativo", "habilitado"])

        if not col_sig:
            continue

        df = df.dropna(subset=[col_sig]).copy()
        df[col_sig] = df[col_sig].astype(str).str.strip()

        if col_sta:
            mask = df[col_sta].astype(str).str.strip().str.lower().isin(
                ["sim", "yes", "y", "true", "ok", "ativo", "habilitado", "cap", "capacitad", "1"]
            )
            sigs = df.loc[mask, col_sig].str.upper().unique().tolist()
        else:
            sigs = df[col_sig].str.upper().unique().tolist()

        if sigs:
            return set(sigs)

    return None