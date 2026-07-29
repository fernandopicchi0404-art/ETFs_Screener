"""Modelo comum de composição, independente da fonte (SEC, Vanguard, etc.)."""

from __future__ import annotations

from dataclasses import dataclass

from etf_screener.models import Holding


@dataclass
class CompositionPayload:
    """Snapshot de holdings pronto para gravar no banco e exportar CSV."""

    source_type: str
    accession_number: str
    source_url: str
    raw_path: str
    holdings: list[Holding]
    composition_date: str | None = None
    report_period_end: str | None = None
    filing_date: str | None = None
    series_name: str | None = None
