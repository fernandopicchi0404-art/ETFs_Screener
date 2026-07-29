"""Adapter de composição via API pública do site da Vanguard."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from etf_screener.config import VANGUARD_RAW_DIR
from etf_screener.holdings.composition import CompositionPayload
from etf_screener.models import Holding

PAGE_SIZE = 500
REQUEST_PAUSE_SECONDS = 0.35
USER_AGENT = "ETFs_Screener research contact@example.com"
EMPTY_MARKERS = {"", "—", "-", "–", "n/a", "na", "null", "none"}

STOCK_URL = (
    "https://investor.vanguard.com/investment-products/etfs/profile/api/"
    "{ticker}/portfolio-holding/stock?start={start}&count={count}"
)


class VanguardHoldingsError(RuntimeError):
    """Falha ao baixar ou interpretar holdings da Vanguard."""


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.casefold() in EMPTY_MARKERS:
        return None
    return text


def _country_from_isin(isin: str | None) -> str:
    if not isin or len(isin) < 2:
        return ""
    return isin[:2].upper()


def _as_of_date(raw: str | None) -> str | None:
    if not raw:
        return None
    # Ex.: 2026-06-30T00:00:00-04:00 → 2026-06-30
    return raw[:10]


def _request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise VanguardHoldingsError(
            f"HTTP {exc.code} ao consultar Vanguard ({url}): {body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise VanguardHoldingsError(f"Falha de rede na Vanguard ({url}): {exc}") from exc
    except json.JSONDecodeError as exc:
        raise VanguardHoldingsError(f"JSON inválido da Vanguard ({url}): {exc}") from exc

    if not isinstance(payload, dict):
        raise VanguardHoldingsError(f"Resposta inesperada da Vanguard ({url}).")
    return payload


def fetch_vanguard_stock_holdings(ticker: str) -> tuple[list[dict[str, Any]], str | None, str]:
    """Baixa todas as páginas de equity holdings. Retorna (entities, as_of, first_url)."""
    ticker_lower = ticker.lower()
    start = 1
    entities: list[dict[str, Any]] = []
    as_of: str | None = None
    first_url = STOCK_URL.format(ticker=ticker_lower, start=1, count=PAGE_SIZE)
    reported_size: int | None = None

    while True:
        url = STOCK_URL.format(ticker=ticker_lower, start=start, count=PAGE_SIZE)
        payload = _request_json(url)
        as_of = as_of or _as_of_date(payload.get("asOfDate"))
        if reported_size is None:
            size_raw = payload.get("size")
            reported_size = int(size_raw) if size_raw is not None else None

        page_entities = (payload.get("fund") or {}).get("entity") or []
        if not isinstance(page_entities, list):
            raise VanguardHoldingsError(f"Campo fund.entity inválido para {ticker}.")
        entities.extend(page_entities)

        has_next = bool(payload.get("next"))
        if not page_entities or not has_next:
            break
        if reported_size is not None and len(entities) >= reported_size:
            break

        start += PAGE_SIZE
        time.sleep(REQUEST_PAUSE_SECONDS)

    if not entities:
        raise VanguardHoldingsError(f"Vanguard não retornou holdings de ações para {ticker}.")
    return entities, as_of, first_url


def _entity_to_holding(etf: str, position: int, entity: dict[str, Any]) -> Holding:
    isin = _clean(entity.get("isin"))
    cusip = _clean(entity.get("cusip"))
    ticker = _clean(entity.get("ticker"))
    sedol = _clean(entity.get("sedol"))
    name = _clean(entity.get("longName")) or _clean(entity.get("shortName")) or ""
    weight_raw = _clean(entity.get("percentWeight")) or "0"
    market_raw = entity.get("marketValue")

    try:
        weight = float(weight_raw)
    except ValueError as exc:
        raise VanguardHoldingsError(
            f"Peso inválido na posição {position} de {etf}: {weight_raw!r}"
        ) from exc

    market_value: float | None
    try:
        market_value = float(market_raw) if market_raw is not None else None
    except (TypeError, ValueError):
        market_value = None

    return Holding(
        etf=etf,
        position=position,
        name=name,
        asset_category="EC",
        asset_type="equity",
        country=_country_from_isin(isin),
        weight_original=weight,
        market_value_usd=market_value,
        cusip=cusip,
        symbol=ticker,
        isin=isin,
        sec_ticker=ticker,
        other_id=sedol,
        included_in_equity_analysis=True,
        exclusion_reason=None,
    )


def save_vanguard_raw(
    ticker: str,
    as_of: str | None,
    entities: list[dict[str, Any]],
) -> Path:
    date_key = as_of or "unknown"
    out_dir = VANGUARD_RAW_DIR / ticker.upper() / date_key
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "stock_holdings.json"
    path.write_text(
        json.dumps(
            {"ticker": ticker.upper(), "asOfDate": as_of, "size": len(entities), "entities": entities},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def fetch_vanguard_composition(ticker: str) -> CompositionPayload:
    """Baixa holdings Vanguard e devolve payload no formato do pipeline."""
    entities, as_of, source_url = fetch_vanguard_stock_holdings(ticker)
    raw_path = save_vanguard_raw(ticker, as_of, entities)
    holdings = [
        _entity_to_holding(ticker.upper(), index, entity)
        for index, entity in enumerate(entities, start=1)
    ]
    accession = f"vanguard:{ticker.upper()}:{as_of or 'unknown'}"
    return CompositionPayload(
        source_type="vanguard_api",
        accession_number=accession,
        source_url=source_url,
        raw_path=str(raw_path),
        holdings=holdings,
        composition_date=as_of,
        report_period_end=as_of,
        filing_date=as_of,
        series_name=ticker.upper(),
    )
