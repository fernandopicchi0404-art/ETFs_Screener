from __future__ import annotations

from pathlib import Path

from etf_screener.holdings.nport_metadata import parse_nport_metadata


def test_parse_nport_metadata_schy_sample():
    xml_path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "schy_nport.xml"
    metadata = parse_nport_metadata(xml_path)
    assert metadata.series_name == "Schwab International Dividend Equity ETF"
    assert metadata.registrant_name == "SCHWAB STRATEGIC TRUST"
    assert metadata.report_period_end == "2026-08-31"
    assert metadata.report_date == "2026-02-28"
