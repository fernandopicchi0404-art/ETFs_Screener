from __future__ import annotations

from pathlib import Path

from etf_screener.holdings.sec_discovery import _series_matches


def test_series_matches_ishares_country():
    assert _series_matches("iShares MSCI Germany ETF", "iShares MSCI Germany ETF")


def test_series_matches_schy():
    assert _series_matches(
        "Schwab International Dividend Equity ETF",
        "Schwab International Dividend Equity ETF",
    )
