from __future__ import annotations

import re
from typing import Any

LEGAL_SUFFIXES = re.compile(
    r"\b(Ltd\.?|Limited|PLC|PL|SA|S\.A\.|AG|Inc\.?|Corp\.?|Co\.?|PJSC|NV|SE|SpA)\b",
    re.IGNORECASE,
)


def _normalize_name(name: str) -> str:
    cleaned = LEGAL_SUFFIXES.sub("", name).strip(" ,")
    return re.sub(r"\s+", " ", cleaned).casefold()


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

    if candidate.get("type") in {"dr", "fund"}:
        return False, f"Ticker {roic_symbol} não é ação ordinária."

    return False, f"Nome do ticker ({candidate.get('name')}) não combina com {company_name}."
