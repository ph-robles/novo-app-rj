import pandas as pd
from pathlib import Path
from utils.helpers import strip_accents, normalizar_sigla
import streamlit as st

EXCEL_PATH = Path("enderecos.xlsx")

@st.cache_data
def carregar_dados():
    df = pd.read_excel(EXCEL_PATH, sheet_name="enderecos", engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()

    df = df.rename(columns={
        "sigla_da_torre": "sigla",
        "nome_da_torre": "nome",
        "endereço": "endereco",
    })

    for col in ["sigla", "nome", "endereco", "detentora"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)

    return df

@st.cache_data
def carregar_acessos():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="acessos", engine="openpyxl")
    except:
        return None
    df.columns = df.columns.str.strip().str.lower()
    if "sigla" in df.columns and "tecnico" in df.columns:
        df = df[df["status"].str.lower() == "ok"]
        return df
    return None