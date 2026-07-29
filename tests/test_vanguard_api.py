from __future__ import annotations

import json
from pathlib import Path

from etf_screener.holdings.sources import source_chain_for_ticker
from etf_screener.holdings.vanguard_api import (
    _entity_to_holding,
    fetch_vanguard_composition,
    fetch_vanguard_stock_holdings,
)


SAMPLE_ENTITY = {
    "type": "portfolioHolding",
    "asOfDate": "2026-06-30T00:00:00-04:00",
    "longName": "NVIDIA Corp.",
    "shortName": "NVIDIA CORP",
    "sharesHeld": "629128862",
    "marketValue": 125882393997.58,
    "ticker": "NVDA",
    "isin": "US67066G1040",
    "percentWeight": "7.51",
    "cusip": "67066G104",
    "sedol": "2379504",
}


def test_source_chain_prefers_vanguard_for_voo():
    chain = source_chain_for_ticker("VOO", issuer="Vanguard")
    assert chain[0] == "vanguard_api"
    assert "sec_nport" in chain


def test_entity_to_holding_maps_identifiers():
    holding = _entity_to_holding("VOO", 1, SAMPLE_ENTITY)
    assert holding.isin == "US67066G1040"
    assert holding.cusip == "67066G104"
    assert holding.sec_ticker == "NVDA"
    assert holding.symbol == "NVDA"
    assert holding.country == "US"
    assert holding.weight_original == 7.51
    assert holding.included_in_equity_analysis is True
    assert holding.other_id == "2379504"


def test_fetch_vanguard_composition_paginates(monkeypatch, tmp_path: Path):
    pages = {
        1: {
            "size": 3,
            "asOfDate": "2026-06-30T00:00:00-04:00",
            "next": {"href": "next"},
            "fund": {
                "entity": [
                    SAMPLE_ENTITY,
                    {**SAMPLE_ENTITY, "ticker": "AAPL", "isin": "US0378331005", "percentWeight": "6.00"},
                ]
            },
        },
        2: {
            "size": 3,
            "asOfDate": "2026-06-30T00:00:00-04:00",
            "fund": {
                "entity": [
                    {**SAMPLE_ENTITY, "ticker": "MSFT", "isin": "US5949181045", "percentWeight": "4.00"},
                ]
            },
        },
    }

    def fake_request(url: str):
        if "start=1" in url:
            return pages[1]
        if "start=501" in url:
            return pages[2]
        raise AssertionError(url)

    monkeypatch.setattr(
        "etf_screener.holdings.vanguard_api._request_json",
        fake_request,
    )
    monkeypatch.setattr(
        "etf_screener.holdings.vanguard_api.VANGUARD_RAW_DIR",
        tmp_path / "vanguard",
    )
    monkeypatch.setattr(
        "etf_screener.holdings.vanguard_api.REQUEST_PAUSE_SECONDS",
        0,
    )

    entities, as_of, _url = fetch_vanguard_stock_holdings("VOO")
    assert len(entities) == 3
    assert as_of == "2026-06-30"

    payload = fetch_vanguard_composition("VOO")
    assert payload.source_type == "vanguard_api"
    assert payload.accession_number == "vanguard:VOO:2026-06-30"
    assert len(payload.holdings) == 3
    assert Path(payload.raw_path).exists()
    saved = json.loads(Path(payload.raw_path).read_text(encoding="utf-8"))
    assert saved["size"] == 3
