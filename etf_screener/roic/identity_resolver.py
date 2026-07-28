from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from etf_screener.roic.client import RoicClient
from etf_screener.roic.exchange_map import infer_roic_symbol
from etf_screener.roic.resolver import MANUAL_ROIC_SYMBOLS, _candidate_queries, _score_candidate
from etf_screener.validation.ticker import names_are_compatible, validate_ticker_match

APPROVED_STATUSES = {
    "verified_isin",
    "verified_cusip",
    "verified_symbol",
    "verified_name_match",
    "manual_approved",
}

MIN_NAME_SCORE = 15
HIGH_CONFIDENCE_NAME_SCORE = 25
AMBIGUITY_GAP = 3


@dataclass(frozen=True)
class IdentityResult:
    roic_symbol: str | None
    mapping_method: str
    mapping_status: str
    candidate_name: str | None
    requests_used: int
    error_message: str | None
    match_isin: str | None = None
    match_cusip: str | None = None


def _normalize_id(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().upper()
    return cleaned or None


def _search_exact(
    client: RoicClient,
    query: str,
    search_by: str,
) -> tuple[list[dict[str, Any]], int]:
    payload = client.get(
        "/tickers/search",
        {"query": query, "search_by": search_by, "limit": 10},
    )
    return payload.get("data", []), 1


def _pick_exact_isin(candidates: list[dict[str, Any]], isin: str) -> dict[str, Any] | None:
    target = _normalize_id(isin)
    for candidate in candidates:
        if _normalize_id(candidate.get("isin")) == target:
            return candidate
    return None


def _pick_exact_cusip(candidates: list[dict[str, Any]], cusip: str) -> dict[str, Any] | None:
    target = _normalize_id(cusip)
    for candidate in candidates:
        if _normalize_id(candidate.get("cusip")) == target:
            return candidate
    return None


def _validate_candidate(
    company_name: str,
    country: str,
    candidate: dict[str, Any],
    roic_symbol: str,
    *,
    match_source: str = "default",
) -> tuple[bool, str]:
    return validate_ticker_match(
        company_name,
        country,
        candidate,
        roic_symbol,
        match_source=match_source,
    )


def _verify_symbol(
    client: RoicClient,
    *,
    company_name: str,
    country: str,
    symbol: str,
    mapping_method: str,
    mapping_status: str,
    requests_used: int,
    isin: str | None,
    cusip: str | None,
    trust_identifier: bool = False,
) -> IdentityResult:
    candidates, used = _search_exact(client, symbol, "symbol")
    requests_used += used
    match_source = "manual" if trust_identifier or mapping_status == "manual_approved" else "default"
    for candidate in candidates:
        if candidate.get("symbol") == symbol:
            ok, message = _validate_candidate(
                company_name, country, candidate, symbol, match_source=match_source
            )
            if ok:
                return IdentityResult(
                    roic_symbol=symbol,
                    mapping_method=mapping_method,
                    mapping_status=mapping_status,
                    candidate_name=candidate.get("name"),
                    requests_used=requests_used,
                    error_message=None,
                    match_isin=_normalize_id(isin),
                    match_cusip=_normalize_id(cusip),
                )
            return IdentityResult(
                roic_symbol=None,
                mapping_method="rejected",
                mapping_status="rejected",
                candidate_name=candidate.get("name"),
                requests_used=requests_used,
                error_message=message,
                match_isin=_normalize_id(isin),
                match_cusip=_normalize_id(cusip),
            )
    return IdentityResult(
        roic_symbol=None,
        mapping_method="not_found",
        mapping_status="not_found",
        candidate_name=None,
        requests_used=requests_used,
        error_message=f"Símbolo {symbol} não encontrado na ROIC.",
        match_isin=_normalize_id(isin),
        match_cusip=_normalize_id(cusip),
    )


def resolve_asset_identity(
    client: RoicClient,
    *,
    company_name: str,
    country: str,
    isin: str | None,
    cusip: str | None,
    sec_ticker: str | None,
    known_roic_symbol: str | None = None,
) -> IdentityResult:
    requests_used = 0

    manual_symbol = MANUAL_ROIC_SYMBOLS.get(company_name)
    if manual_symbol:
        return _verify_symbol(
            client,
            company_name=company_name,
            country=country,
            symbol=manual_symbol,
            mapping_method="manual_approved",
            mapping_status="manual_approved",
            requests_used=requests_used,
            isin=isin,
            cusip=cusip,
        )

    if known_roic_symbol:
        candidates, used = _search_exact(client, known_roic_symbol, "symbol")
        requests_used += used
        for candidate in candidates:
            if candidate.get("symbol") == known_roic_symbol:
                ok, message = _validate_candidate(company_name, country, candidate, known_roic_symbol)
                if ok:
                    return IdentityResult(
                        roic_symbol=known_roic_symbol,
                        mapping_method="manual_approved",
                        mapping_status="manual_approved",
                        candidate_name=candidate.get("name"),
                        requests_used=requests_used,
                        error_message=None,
                        match_isin=_normalize_id(isin),
                        match_cusip=_normalize_id(cusip),
                    )
                return IdentityResult(
                    roic_symbol=None,
                    mapping_method="rejected",
                    mapping_status="rejected",
                    candidate_name=candidate.get("name"),
                    requests_used=requests_used,
                    error_message=message,
                    match_isin=_normalize_id(isin),
                    match_cusip=_normalize_id(cusip),
                )

    if isin:
        candidates, used = _search_exact(client, isin, "isin")
        requests_used += used
        match = _pick_exact_isin(candidates, isin)
        if match:
            symbol = match.get("symbol")
            if symbol:
                ok, message = _validate_candidate(
                    company_name, country, match, symbol, match_source="isin"
                )
                if ok:
                    return IdentityResult(
                        roic_symbol=symbol,
                        mapping_method="verified_isin",
                        mapping_status="verified_isin",
                        candidate_name=match.get("name"),
                        requests_used=requests_used,
                        error_message=None,
                        match_isin=_normalize_id(isin),
                        match_cusip=_normalize_id(cusip),
                    )
                return IdentityResult(
                    roic_symbol=None,
                    mapping_method="rejected",
                    mapping_status="rejected",
                    candidate_name=match.get("name"),
                    requests_used=requests_used,
                    error_message=message,
                    match_isin=_normalize_id(isin),
                    match_cusip=_normalize_id(cusip),
                )

    if cusip:
        candidates, used = _search_exact(client, cusip, "cusip")
        requests_used += used
        match = _pick_exact_cusip(candidates, cusip)
        if match:
            symbol = match.get("symbol")
            if symbol:
                ok, message = _validate_candidate(
                    company_name, country, match, symbol, match_source="cusip"
                )
                if ok:
                    return IdentityResult(
                        roic_symbol=symbol,
                        mapping_method="verified_cusip",
                        mapping_status="verified_cusip",
                        candidate_name=match.get("name"),
                        requests_used=requests_used,
                        error_message=None,
                        match_isin=_normalize_id(isin),
                        match_cusip=_normalize_id(cusip),
                    )
                return IdentityResult(
                    roic_symbol=None,
                    mapping_method="rejected",
                    mapping_status="rejected",
                    candidate_name=match.get("name"),
                    requests_used=requests_used,
                    error_message=message,
                    match_isin=_normalize_id(isin),
                    match_cusip=_normalize_id(cusip),
                )

    inferred_symbol = infer_roic_symbol(country, sec_ticker)
    if inferred_symbol:
        return _verify_symbol(
            client,
            company_name=company_name,
            country=country,
            symbol=inferred_symbol,
            mapping_method="verified_symbol",
            mapping_status="verified_symbol",
            requests_used=requests_used,
            isin=isin,
            cusip=cusip,
            trust_identifier=bool(isin or cusip),
        )

    if sec_ticker and ":" in sec_ticker:
        symbol = sec_ticker.strip().upper()
        return _verify_symbol(
            client,
            company_name=company_name,
            country=country,
            symbol=symbol,
            mapping_method="verified_symbol",
            mapping_status="verified_symbol",
            requests_used=requests_used,
            isin=isin,
            cusip=cusip,
            trust_identifier=bool(isin or cusip),
        )

    # Nome: apenas candidato para revisão — nunca aprova automaticamente.
    best_symbol: str | None = None
    best_score = -1
    second_score = -1
    best_name: str | None = None
    extra_requests = 0

    for query in _candidate_queries(company_name):
        payload = client.get("/tickers/search", {"query": query, "limit": 25})
        extra_requests += 1
        for candidate in payload.get("data", []):
            score = _score_candidate(candidate, company_name, country)
            if score > best_score:
                second_score = best_score
                best_score = score
                best_symbol = candidate.get("symbol")
                best_name = candidate.get("name")
            elif score > second_score:
                second_score = score

    requests_used += extra_requests

    if best_symbol is None:
        return IdentityResult(
            roic_symbol=None,
            mapping_method="not_found",
            mapping_status="not_found",
            candidate_name=None,
            requests_used=requests_used,
            error_message="Nenhum candidato ROIC encontrado.",
            match_isin=_normalize_id(isin),
            match_cusip=_normalize_id(cusip),
        )

    if best_score < MIN_NAME_SCORE or (best_score - second_score) < AMBIGUITY_GAP:
        return IdentityResult(
            roic_symbol=None,
            mapping_method="name_search",
            mapping_status="review_required",
            candidate_name=best_name,
            requests_used=requests_used,
            error_message=f"Candidato ambíguo ou fraco (score={best_score}).",
            match_isin=_normalize_id(isin),
            match_cusip=_normalize_id(cusip),
        )

    if (
        isin
        and best_score >= HIGH_CONFIDENCE_NAME_SCORE
        and best_name
        and names_are_compatible(company_name, best_name)
    ):
        return IdentityResult(
            roic_symbol=best_symbol,
            mapping_method="verified_name_match",
            mapping_status="verified_name_match",
            candidate_name=best_name,
            requests_used=requests_used,
            error_message=None,
            match_isin=_normalize_id(isin),
            match_cusip=_normalize_id(cusip),
        )

    return IdentityResult(
        roic_symbol=None,
        mapping_method="name_search",
        mapping_status="review_required",
        candidate_name=best_name,
        requests_used=requests_used,
        error_message=f"Candidato plausível ({best_symbol}) aguarda revisão manual.",
        match_isin=_normalize_id(isin),
        match_cusip=_normalize_id(cusip),
    )
