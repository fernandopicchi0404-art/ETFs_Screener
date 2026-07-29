from __future__ import annotations

from etf_screener.catalog.registry import list_etfs, sync_etf_registry
from etf_screener.database.db import Database
from etf_screener.holdings.composition import CompositionPayload
from etf_screener.holdings.pipeline import extract_etf_holdings
from etf_screener.models import Holding


def _sample_holding(etf: str = "VOO") -> Holding:
    return Holding(
        etf=etf,
        position=1,
        name="NVIDIA Corp.",
        asset_category="EC",
        asset_type="equity",
        country="US",
        weight_original=7.51,
        market_value_usd=100.0,
        cusip="67066G104",
        symbol="NVDA",
        isin="US67066G1040",
        sec_ticker="NVDA",
        included_in_equity_analysis=True,
    )


def test_list_etfs_explicit_ticker_includes_paused(tmp_path, monkeypatch):
    db = Database(tmp_path / "db.sqlite")
    sync_etf_registry(db)
    # Simula ticker pausado no banco
    with db.connect() as conn:
        conn.execute("UPDATE etfs SET status = 'paused' WHERE ticker = 'SCHY'")
        conn.commit()

    rows = list_etfs(db, tickers=["SCHY"])
    assert len(rows) == 1
    assert rows[0]["ticker"] == "SCHY"


def test_extract_prefers_vanguard_when_configured(tmp_path, monkeypatch):
    db = Database(tmp_path / "db.sqlite")
    sync_etf_registry(db)
    etf = next(row for row in list_etfs(db, tickers=["VOO"]))

    payload = CompositionPayload(
        source_type="vanguard_api",
        accession_number="vanguard:VOO:2026-06-30",
        source_url="https://example.test/voo",
        raw_path=str(tmp_path / "raw.json"),
        holdings=[_sample_holding()],
        composition_date="2026-06-30",
        report_period_end="2026-06-30",
        filing_date="2026-06-30",
        series_name="VOO",
    )
    (tmp_path / "raw.json").write_text("{}", encoding="utf-8")

    def fake_fetch(etf_row, source):
        assert source == "vanguard_api"
        return payload

    monkeypatch.setattr("etf_screener.holdings.pipeline._fetch_composition", fake_fetch)
    monkeypatch.setattr("etf_screener.holdings.pipeline.EXPORTS_DIR", tmp_path / "exports")

    result = extract_etf_holdings(db, etf, force=True)
    assert result["status"] == "ok"
    assert result["source_type"] == "vanguard_api"
    assert result["equity_positions"] == 1
