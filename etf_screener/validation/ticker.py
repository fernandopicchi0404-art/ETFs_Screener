from __future__ import annotations

import re
from typing import Any

LEGAL_SUFFIXES = re.compile(
    r"\b(Ltd\.?|Limited|PLC|PL|SA|S\.A\.|AG|Inc\.?|Corp\.?|Co\.?|PJSC|NV|SE|SpA)\b",
    re.IGNORECASE,
)

# Nomes legais equivalentes entre países (ex.: Koninklijke = Royal em holandês).
LEGAL_NAME_EQUIVALENTS = {
    "koninklijke": "royal",
    "societe": "company",
    "compagnie": "company",
}


def _normalize_name(name: str) -> str:
    cleaned = LEGAL_SUFFIXES.sub("", name).strip(" ,")
    normalized = re.sub(r"\s+", " ", cleaned).casefold()
    for source, target in LEGAL_NAME_EQUIVALENTS.items():
        normalized = re.sub(rf"\b{source}\b", target, normalized)
    return normalized


def validate_ticker_match(
    company_name: str,
    country: str,
    candidate: dict[str, Any] | None,
    roic_symbol: str,
) -> tuple[bool, str]:
    """Valida se o ticker ROIC parece ser a empresa correta."""
    if not roic_symbol:
        return False, "Ticker ROIC vazio."

    if candidate is None:
        return True, ""

    listing_country = candidate.get("listing_country_code") or ""
    if listing_country and listing_country != country:
        return False, (
            f"País do ticker ({listing_country}) diferente do país do ETF ({country})."
        )

    candidate_name = _normalize_name(candidate.get("name") or "")
    target_name = _normalize_name(company_name)
    if not candidate_name or not target_name:
        return True, ""

    if target_name in candidate_name or candidate_name in target_name:
        return True, ""

    target_tokens = [token for token in target_name.split() if len(token) > 2]
    overlap = sum(1 for token in target_tokens[:3] if token in candidate_name)
    if overlap >= 2:
        return True, ""

    # Aceita siglas distintivas compartilhadas (ex.: KPN, TIM).
    distinctive_tokens = [
        token
        for token in target_tokens
        if token.isalpha() and (token.isupper() or len(token) <= 4)
    ]
    if any(token in candidate_name for token in distinctive_tokens):
        return True, ""

    if candidate.get("type") in {"dr", "fund"}:
        return False, f"Ticker {roic_symbol} não é ação ordinária."

    return False, f"Nome do ticker ({candidate.get('name')}) não combina com {company_name}."
