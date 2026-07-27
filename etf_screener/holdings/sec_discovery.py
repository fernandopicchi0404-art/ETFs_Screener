from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from etf_screener.config import (
    SEC_ARCHIVES_BASE,
    SEC_DATA_API_BASE,
    SEC_EFTS_SEARCH_URL,
    SEC_USER_AGENT,
)
from etf_screener.holdings.nport_metadata import parse_nport_metadata


@dataclass(frozen=True)
class NportFilingRef:
    cik: str
    accession_number: str
    primary_document: str
    filing_date: str
    filing_url: str
    series_name: str | None = None
    report_period_end: str | None = None
    report_date: str | None = None


def _request_json(url: str, params: dict[str, str] | None = None) -> Any:
    query = urllib.parse.urlencode(params or {})
    full_url = f"{url}?{query}" if query else url
    request = urllib.request.Request(full_url, headers={"User-Agent": SEC_USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _request_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": SEC_USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def _normalize_cik(cik: str) -> str:
    return str(int(cik))


def _build_filing_url(cik: str, accession_number: str, primary_document: str) -> str:
    accession_nodash = accession_number.replace("-", "")
    return f"{SEC_ARCHIVES_BASE}/{int(cik)}/{accession_nodash}/{primary_document}"


def _series_matches(etf_name: str, series_name: str) -> bool:
    left = etf_name.casefold().strip()
    right = series_name.casefold().strip()
    if left == right or left in right or right in left:
        return True

    skip = {"ishares", "vanguard", "schwab", "spdr", "etf", "fund", "index", "the", "inc", "trust"}
    tokens = [token for token in re.split(r"[^A-Za-z0-9]+", etf_name) if len(token) > 2]
    tokens = [token for token in tokens if token.casefold() not in skip]
    if len(tokens) < 2:
        return False
    return all(token.casefold() in right for token in tokens[-4:])


def list_recent_nport_filings(cik: str, limit: int = 40) -> list[dict[str, str]]:
    cik10 = f"{int(cik):010d}"
    payload = _request_json(f"{SEC_DATA_API_BASE}/submissions/CIK{cik10}.json")
    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    documents = recent.get("primaryDocument", [])
    filing_dates = recent.get("filingDate", [])

    filings: list[dict[str, str]] = []
    for form, accession, document, filing_date in zip(forms, accessions, documents, filing_dates):
        if not form.startswith("NPORT"):
            continue
        filings.append(
            {
                "cik": _normalize_cik(cik),
                "form": form,
                "accession_number": accession,
                "primary_document": document,
                "filing_date": filing_date,
            }
        )
        if len(filings) >= limit:
            break
    return filings


def search_nport_filings_by_name(etf_name: str, limit: int = 20) -> list[dict[str, str]]:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=540)
    params = {
        "q": f'"{etf_name}"',
        "forms": "NPORT-P",
        "dateRange": "custom",
        "startdt": start.isoformat(),
        "enddt": end.isoformat(),
    }
    payload = _request_json(SEC_EFTS_SEARCH_URL, params)
    hits = payload.get("hits", {}).get("hits", [])
    results: list[dict[str, str]] = []
    for hit in hits[:limit]:
        source = hit.get("_source", {})
        ciks = source.get("ciks") or []
        if not ciks:
            continue
        adsh = source.get("adsh", "")
        results.append(
            {
                "cik": ciks[0],
                "accession_number": adsh,
                "primary_document": "primary_doc.xml",
                "filing_date": source.get("file_date", ""),
            }
        )
    return results


def _resolve_primary_document(cik: str, accession_number: str, primary_document: str) -> str:
    if primary_document and not primary_document.startswith("xsl"):
        return primary_document

    accession_nodash = accession_number.replace("-", "")
    index_url = f"{SEC_ARCHIVES_BASE}/{int(cik)}/{accession_nodash}/index.json"
    try:
        payload = _request_json(index_url)
    except urllib.error.HTTPError:
        return primary_document or "primary_doc.xml"

    for item in payload.get("directory", {}).get("item", []):
        name = item.get("name", "")
        if name == "primary_doc.xml":
            return name
    return primary_document or "primary_doc.xml"


def _inspect_filing(
    cik: str,
    accession_number: str,
    primary_document: str,
    filing_date: str,
) -> NportFilingRef | None:
    document = _resolve_primary_document(cik, accession_number, primary_document)
    url = _build_filing_url(cik, accession_number, document)
    try:
        xml_bytes = _request_bytes(url)
    except urllib.error.HTTPError:
        return None

    metadata = parse_nport_metadata(xml_bytes)
    if not metadata.series_name:
        return None

    return NportFilingRef(
        cik=_normalize_cik(cik),
        accession_number=accession_number,
        primary_document=document,
        filing_date=filing_date,
        filing_url=url,
        series_name=metadata.series_name,
        report_period_end=metadata.report_period_end,
        report_date=metadata.report_date,
    )


def find_latest_nport_filing(
    etf_name: str,
    sec_registrant_cik: str | None = None,
    series_match: str | None = None,
    search_efts: bool = False,
) -> NportFilingRef | None:
    """Localiza o N-PORT mais recente cujo seriesName corresponde ao ETF."""
    match_name = series_match or etf_name
    candidates: list[dict[str, str]] = []
    candidates.extend(search_nport_filings_by_name(etf_name, limit=20))
    if sec_registrant_cik:
        candidates.extend(list_recent_nport_filings(sec_registrant_cik, limit=30))

    seen: set[str] = set()
    for candidate in candidates:
        accession = candidate["accession_number"]
        if accession in seen:
            continue
        seen.add(accession)

        filing = _inspect_filing(
            candidate["cik"],
            accession,
            candidate.get("primary_document", "primary_doc.xml"),
            candidate.get("filing_date", ""),
        )
        if filing is None:
            continue
        if _series_matches(match_name, filing.series_name or ""):
            return filing

    return None
