from __future__ import annotations

from urllib.parse import quote

# Símbolo ROIC alternativo quando identidade está certa mas outro listing tem preço/fundamentos.
FETCH_SYMBOL_ALIASES: dict[str, str] = {
    "SIX:ROG": "SIX:RO",
    "EURONEXT:ENI": "MIL:ENI",
    "B3:JBSS3": "NYSE:JBS",
    "EURONEXT:STM": "NYSE:STM",
}


def encode_roic_identifier(symbol: str) -> str:
    """Codifica '/' em tickers mexicanos (ex.: BMV:KOF/UBL) sem quebrar o path da API."""
    return quote(symbol, safe=":")


def roic_symbol_path(prefix: str, symbol: str) -> str:
    return f"{prefix}/{encode_roic_identifier(symbol)}"


def resolve_fetch_symbol(roic_symbol: str) -> str:
    return FETCH_SYMBOL_ALIASES.get(roic_symbol, roic_symbol)
