from __future__ import annotations

import re
import unicodedata
from typing import Any

LEGAL_SUFFIXES = re.compile(
    r"\b(Ltd\.?|Limited|PLC|PL|SA|S\.A\.|AG|Inc\.?|Corp\.?|Co\.?|PJSC|NV|SE|SpA|"
    r"Pvt\.?|Private|JSC|QPSC|Bhd|Tbk|PCL|KGaA|AB|ASA|Oyj|SAB|de CV)\b",
    re.IGNORECASE,
)

CLASS_SHARE_SUFFIX = re.compile(
    r"\b(class [a-z0-9]+|ordinary shares?|common stock|unsponsored adr|adr)\b",
    re.IGNORECASE,
)

LEGAL_NAME_EQUIVALENTS = {
    "koninklijke": "royal",
    "societe": "company",
    "compagnie": "company",
    "cie": "company",
    "muenchen": "munchen",
    "private": "pvt",
    "companies": "cos",
    "giga device": "gigadevice",
    "hon precision": "honprecision",
}


def _normalize_name(name: str) -> str:
    """Normaliza nomes legais para comparar SEC vs ROIC."""
    cleaned = unicodedata.normalize("NFKD", name)
    cleaned = cleaned.encode("ascii", "ignore").decode("ascii")
    cleaned = cleaned.casefold()
    cleaned = cleaned.replace("&", " and ")
    cleaned = re.sub(r"\bthe\b", " ", cleaned)
    cleaned = CLASS_SHARE_SUFFIX.sub(" ", cleaned)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = LEGAL_SUFFIXES.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for source, target in LEGAL_NAME_EQUIVALENTS.items():
        cleaned = re.sub(rf"\b{source}\b", target, cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def names_are_compatible(company_name: str, candidate_name: str) -> bool:
    target = _normalize_name(company_name)
    candidate = _normalize_name(candidate_name)
    if not target or not candidate:
        return False
    if target in candidate or candidate in target:
        return True

    target_tokens = [token for token in target.split() if len(token) > 2]
    if not target_tokens:
        return False

    overlap = sum(1 for token in target_tokens[:4] if token in candidate)
    if overlap >= 2:
        return True

    distinctive_tokens = [
        token
        for token in target_tokens
        if token.isalpha() and (len(token) <= 4 or token.isupper())
    ]
    return any(token in candidate for token in distinctive_tokens)


def validate_ticker_match(
    company_name: str,
    country: str,
    candidate: dict[str, Any] | None,
    roic_symbol: str,
    *,
    match_source: str = "default",
) -> tuple[bool, str]:
    """Valida se o ticker ROIC parece ser a empresa correta."""
    if not roic_symbol:
        return False, "Ticker ROIC vazio."

    if candidate is None:
        return True, ""

    # ISIN/CUSIP exato é prova mais forte que invCountry da SEC (muitas vezes sede legal).
    if match_source not in {"isin", "cusip"}:
        listing_country = candidate.get("listing_country_code") or ""
        if listing_country and listing_country != country:
            return False, (
                f"País do ticker ({listing_country}) diferente do país do ETF ({country})."
            )

    if names_are_compatible(company_name, candidate.get("name") or ""):
        if candidate.get("type") == "fund":
            return False, f"Ticker {roic_symbol} não é ação ordinária."
        return True, ""

    if candidate.get("type") == "fund":
        return False, f"Ticker {roic_symbol} não é ação ordinária."

    # ISIN exato: aceita ADR/DR; rejeita só fundos e nomes incompatíveis.
    if match_source in {"isin", "cusip", "manual"}:
        return False, (
            f"Nome do ticker ({candidate.get('name')}) não combina com {company_name}."
        )

    if candidate.get("type") in {"dr", "fund"}:
        return False, f"Ticker {roic_symbol} não é ação ordinária."

    return False, (
        f"Nome do ticker ({candidate.get('name')}) não combina com {company_name}."
    )
