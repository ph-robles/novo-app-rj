"""
utils/helpers.py
-----------------
Funções utilitárias usadas nas páginas do app:
  - normalizar_sigla: normaliza texto de sigla para comparação (upper, remove sinais, normaliza acentos)
  - levenshtein: distância de edição para fuzzy match
  - safe_str: conversão segura para string exibível
  - strip_accents: utilitário de normalização de acentos
  - slugify: cria um identificador amigável para URLs/keys
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable


_ACCENT_TRANSLATION = str.maketrans(
    {
        # Mapeamento manual rápido para maiúsculas acentuadas comuns em PT-BR
        "Á": "A", "À": "A", "Â": "A", "Ã": "A",
        "É": "E", "È": "E", "Ê": "E",
        "Í": "I", "Ì": "I", "Î": "I",
        "Ó": "O", "Ò": "O", "Ô": "O", "Õ": "O",
        "Ú": "U", "Ù": "U", "Û": "U",
        "Ç": "C",
        # e minúsculas
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "è": "e", "ê": "e",
        "í": "i", "ì": "i", "î": "i",
        "ó": "o", "ò": "o", "ô": "o", "õ": "o",
        "ú": "u", "ù": "u", "û": "u",
        "ç": "c",
    }
)


def strip_accents(text: str) -> str:
    """Remove acentos usando unicodedata (fallback ao mapa manual)."""
    if text is None:
        return ""
    try:
        # Normaliza para NFKD e remove marcas de combinação
        normalized = unicodedata.normalize("NFKD", str(text))
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))
    except Exception:
        return str(text).translate(_ACCENT_TRANSLATION)


def normalizar_sigla(s: str) -> str:
    """
    Normaliza uma sigla para comparação:
      - converte para string
      - remove espaços laterais
      - upper()
      - remove acentos
      - remove caracteres não alfanuméricos (mantém 0-9 e A-Z)
    """
    if s is None:
        return ""
    s = str(s).strip()
    if not s:
        return ""
    s = strip_accents(s).upper()
    # Mantém apenas [A-Z0-9]
    s = re.sub(r"[^0-9A-Z]", "", s)
    return s


def levenshtein(a: str, b: str) -> int:
    """
    Distância de Levenshtein (custo unitário) usando DP iterativa.
    Otimizado em memória (usa apenas a linha anterior).
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # Certifica a e b como strings simples
    a = str(a)
    b = str(b)

    # Garante que b é a menor para usar menos memória (opcional)
    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (0 if ca == cb else 1)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def safe_str(x) -> str:
    """Converte valor qualquer para string amigável, substitui None/NaN por '—'."""
    try:
        if x is None:
            return "—"
        # Suporte leve a pandas sem import direto
        try:
            import math
            if isinstance(x, float) and math.isnan(x):
                return "—"
        except Exception:
            pass
        s = str(x).strip()
        return s if s else "—"
    except Exception:
        return "—"


def slugify(text: str, sep: str = "-") -> str:
    """
    Gera um slug simples: sem acentos, minúsculo, separadores colapsados.
    """
    if text is None:
        return ""
    text = strip_accents(str(text)).lower().strip()
    text = re.sub(r"[^a-z0-9]+", sep, text)
    text = re.sub(rf"{re.escape(sep)}+", sep, text)
    return text.strip(sep)


# Pequeno utilitário para ranking por similaridade
def rank_by_levenshtein(query: str, candidates: Iterable[str], limit: int = 10) -> list[tuple[str, int]]:
    """
    Retorna lista de (item, distancia) ordenada por menor distância, depois alfabética.
    Útil para gerar sugestões.
    """
    qn = normalizar_sigla(query)
    pairs = []
    for c in candidates or []:
        dn = normalizar_sigla(c)
        d = levenshtein(dn, qn)
        pairs.append((c, d))
    pairs.sort(key=lambda x: (x[1], x[0]))
    return pairs[: max(0, int(limit))]
