# utils/helpers.py
import re

def normalizar_sigla(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().upper()
    # remove caracteres não alfanuméricos (opcional)
    s = re.sub(r"[^0-9A-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]", "", s)
    # normaliza acentos simples
    TR = str.maketrans("ÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ", "AAAAEEEIIIOOOOUUUC")
    return s.translate(TR)

def levenshtein(a: str, b: str) -> int:
    # DP simples, suficiente para strings curtas
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    dp = list(range(len(b)+1))
    for i, ca in enumerate(a, start=1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, start=1):
            cur = dp[j]
            cost = 0 if ca == cb else 1
            dp[j] = min(
                dp[j] + 1,       # deleção
                dp[j-1] + 1,     # inserção
                prev + cost      # substituição
            )
            prev = cur
    return dp[-1]
