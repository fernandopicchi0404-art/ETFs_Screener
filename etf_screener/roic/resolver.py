from __future__ import annotations

import re
from typing import Any

from etf_screener.roic.client import RoicClient

LEGAL_SUFFIXES = re.compile(
    r"\b(Ltd\.?|Limited|PLC|PL|SA|S\.A\.|AG|Inc\.?|Corp\.?|Co\.?|PJSC|NV|SE|SpA)\b",
    re.IGNORECASE,
)

KNOWN_NAME_QUERIES = {
    "HCL Technologies Ltd": ["HCLTECH"],
    "Vodacom Group Ltd": ["Vodacom"],
    "Emirates NBD Bank PJSC": ["Emirates NBD"],
    "Banco do Brasil SA": ["BBAS3", "Banco do Brasil"],
    "BOC Hong Kong Holdings Ltd": ["2388", "BOC Hong Kong"],
    "Deutsche Post AG": ["Deutsche Post", "DHL"],
    "Roche Holding AG Ordinary Shares new": ["Roche"],
    "British American Tobacco PLC": ["British American Tobacco", "BATS"],
    "Koninklijke KPN NV": ["KPN"],
    "Japan Tobacco Inc": ["Japan Tobacco"],
    "China Construction Bank Corp H": ["China Construction Bank", "939"],
    "Unilever PLC": ["Unilever", "ULVR"],
    "Wesfarmers Ltd": ["Wesfarmers", "WES"],
    "Enel SpA": ["Enel"],
    "Eni SpA": ["Eni"],
    "TotalEnergies SE": ["TotalEnergies", "TTE"],
    "BHP Group Ltd": ["BHP"],
    "Allianz SE": ["Allianz", "ALV"],
    "Infosys Ltd": ["Infosys", "INFY"],
    "GSK PLC": ["GSK", "GlaxoSmithKline"],
    "Michelin": ["Michelin", "ML"],
    "Publicis Groupe SA": ["Publicis"],
    "Endesa SA": ["Endesa"],
    "Itau Unibanco Holding SA": ["ITUB4", "Itau Unibanco"],
    "Klabin SA": ["Klabin", "KLBN11"],
    "Ambev SA": ["Ambev", "ABEV3"],
    "TIM SA": ["TIM", "TIMS3"],
    "BB Seguridade Participacoes SA": ["BBSE3"],
}


def _candidate_queries(company_name: str, known_symbol: str | None = None) -> list[str]:
    queries: list[str] = []
    if known_symbol:
        queries.append(known_symbol)

    queries.extend(KNOWN_NAME_QUERIES.get(company_name, []))
    queries.append(company_name)

    cleaned = LEGAL_SUFFIXES.sub("", company_name).strip(" ,")
    if cleaned and cleaned not in queries:
        queries.append(cleaned)

    words = [word for word in re.split(r"\s+", cleaned) if word]
    if len(words) >= 2:
        queries.append(" ".join(words[:2]))
    if len(words) >= 1:
        queries.append(words[0])

    deduped: list[str] = []
    for query in queries:
        if query and query not in deduped:
            deduped.append(query)
    return deduped


def _score_candidate(candidate: dict[str, Any], company_name: str, country: str) -> int:
    name = (candidate.get("name") or "").lower()
    target = company_name.lower()
    score = 0

    if candidate.get("listing_country_code") == country:
        score += 12
    if candidate.get("type") == "stock":
        score += 4
    if candidate.get("is_primary"):
        score += 2
    if target in name or name in target:
        score += 8
    if any(token.lower() in name for token in target.split()[:2]):
        score += 3
    if candidate.get("type") in {"dr", "fund"}:
        score -= 6
    return score


def resolve_roic_symbol(
    client: RoicClient,
    company_name: str,
    country: str,
    known_symbol: str | None = None,
    known_roic_symbol: str | None = None,
) -> tuple[str | None, str, list[dict[str, Any]]]:
    if known_roic_symbol:
        return known_roic_symbol, "mapped", []

    if known_symbol and ":" in known_symbol:
        return known_symbol, "mapped", []

    all_candidates: list[dict[str, Any]] = []
    best_symbol: str | None = None
    best_score = -1
    best_status = "not_found"

    for query in _candidate_queries(company_name, known_symbol):
        payload = client.get("/tickers/search", {"query": query, "limit": 25})
        candidates = payload.get("data", [])
        for candidate in candidates:
            score = _score_candidate(candidate, company_name, country)
            all_candidates.append({**candidate, "_score": score, "_query": query})
            if score > best_score:
                best_score = score
                best_symbol = candidate.get("symbol")
                best_status = "search_match"

    if best_symbol is None:
        return None, "not_found", all_candidates[:10]

    if best_score < 10:
        return best_symbol, "ambiguous", all_candidates[:10]

    return best_symbol, best_status, all_candidates[:10]
