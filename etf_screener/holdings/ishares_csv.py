"""Adapter de composição via CSV público latest-holdings da iShares."""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from etf_screener.config import ISHARES_RAW_DIR
from etf_screener.holdings.composition import CompositionPayload
from etf_screener.holdings.sources import etf_source_config
from etf_screener.models import Holding

USER_AGENT = "ETFs_Screener research contact@example.com"
CSV_URL = "https://www.ishares.com/us/products/{product_id}/{slug}/latest-holdings.csv"
EMPTY_MARKERS = {"", "—", "-", "–", "n/a", "na", "null", "none"}
EQUITY_CLASSES = {"equity", "preferred equity", "preferred_equity"}


class ISharesHoldingsError(RuntimeError):
    """Falha ao baixar ou interpretar holdings da iShares."""


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().strip('"')
    if text.casefold() in EMPTY_MARKERS:
        return None
    return text


def _parse_weight(raw: str | None) -> float:
    text = (_clean(raw) or "0").replace(",", "")
    try:
        return float(text)
    except ValueError as exc:
        raise ISharesHoldingsError(f"Peso inválido no CSV iShares: {raw!r}") from exc


def _parse_money(raw: str | None) -> float | None:
    text = _clean(raw)
    if text is None:
        return None
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _parse_as_of(meta_lines: list[str]) -> str | None:
    for line in meta_lines:
        if "Fund Holdings as of" not in line:
            continue
        # Fund Holdings as of,"Jul 27, 2026"
        match = re.search(r'as of,"?([^"\n]+)"?', line, flags=re.IGNORECASE)
        if not match:
            continue
        raw_date = match.group(1).strip()
        for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw_date, fmt).date().isoformat()
            except ValueError:
                continue
        return raw_date
    return None


def resolve_ishares_product(ticker: str) -> tuple[str, str]:
    cfg = etf_source_config(ticker).get("ishares") or {}
    product_id = cfg.get("product_id")
    slug = cfg.get("slug")
    if not product_id or not slug:
        raise ISharesHoldingsError(
            f"iShares product_id/slug não configurados para {ticker} "
            f"em data/catalog/holdings_sources.json"
        )
    return str(product_id), str(slug)


def download_ishares_csv(ticker: str) -> tuple[str, str, str]:
    product_id, slug = resolve_ishares_product(ticker)
    url = CSV_URL.format(product_id=product_id, slug=slug)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/csv,*/*"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8-sig")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise ISharesHoldingsError(f"HTTP {exc.code} iShares ({url}): {body}") from exc
    except urllib.error.URLError as exc:
        raise ISharesHoldingsError(f"Falha de rede iShares ({url}): {exc}") from exc

    if not text.lstrip().startswith("iShares") and "Ticker,Name" not in text:
        raise ISharesHoldingsError(f"Resposta iShares não parece CSV de holdings ({url}).")
    return text, url, f"{product_id}/{slug}"


def parse_ishares_csv(text: str, etf: str) -> tuple[list[Holding], str | None]:
    # Metadados no topo, depois linha em branco, depois cabeçalho Ticker,...
    parts = text.split("\n\n", 1)
    meta_lines = parts[0].splitlines()
    as_of = _parse_as_of(meta_lines)
    table_text = parts[1] if len(parts) > 1 else text
    reader = csv.DictReader(io.StringIO(table_text))
    if not reader.fieldnames or "Ticker" not in reader.fieldnames:
        raise ISharesHoldingsError("CSV iShares sem coluna Ticker.")

    holdings: list[Holding] = []
    for index, row in enumerate(reader, start=1):
        asset_class = (_clean(row.get("Asset Class")) or "").casefold()
        name = _clean(row.get("Name")) or ""
        ticker_local = _clean(row.get("Ticker"))
        location = _clean(row.get("Location")) or ""
        exchange = _clean(row.get("Exchange"))
        weight = _parse_weight(row.get("Weight (%)"))
        market_value = _parse_money(row.get("Market Value"))
        is_equity = asset_class in EQUITY_CLASSES
        holding = Holding(
            etf=etf,
            position=index,
            name=name,
            asset_category="EC" if is_equity else "OTHER",
            asset_type="equity" if is_equity else (asset_class or "other"),
            country=location,
            weight_original=weight,
            market_value_usd=market_value,
            symbol=ticker_local,
            sec_ticker=ticker_local,
            other_id=exchange,
            included_in_equity_analysis=is_equity,
            exclusion_reason=None if is_equity else f"asset_class={asset_class or 'unknown'}",
        )
        holdings.append(holding)

    if not any(item.included_in_equity_analysis for item in holdings):
        raise ISharesHoldingsError(f"CSV iShares de {etf} sem posições Equity.")
    return holdings, as_of


def save_ishares_raw(ticker: str, as_of: str | None, text: str, meta: dict[str, Any]) -> Path:
    date_key = as_of or "unknown"
    out_dir = ISHARES_RAW_DIR / ticker.upper() / date_key
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "latest-holdings.csv"
    csv_path.write_text(text, encoding="utf-8")
    (out_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return csv_path


def fetch_ishares_composition(ticker: str) -> CompositionPayload:
    text, url, product_ref = download_ishares_csv(ticker)
    holdings, as_of = parse_ishares_csv(text, ticker.upper())
    raw_path = save_ishares_raw(
        ticker,
        as_of,
        text,
        {"ticker": ticker.upper(), "asOfDate": as_of, "product": product_ref, "source_url": url},
    )
    accession = f"ishares:{ticker.upper()}:{as_of or 'unknown'}"
    return CompositionPayload(
        source_type="ishares_csv",
        accession_number=accession,
        source_url=url,
        raw_path=str(raw_path),
        holdings=holdings,
        composition_date=as_of,
        report_period_end=as_of,
        filing_date=as_of,
        series_name=ticker.upper(),
    )
