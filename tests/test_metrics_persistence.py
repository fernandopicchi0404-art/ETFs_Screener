from __future__ import annotations

import csv
from pathlib import Path

import pytest

from etf_screener.database.db import Database
from etf_screener.metrics.persistence import (
    company_from_csv_row,
    upsert_asset_fundamentals,
    upsert_etf_consolidated_metrics,
)
from tests.conftest import make_company


def test_upsert_asset_fundamentals_roundtrip(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.sqlite")
    db.init_schema()

    with db.connect() as conn:
        conn.execute(
            """
            INSERT INTO assets (asset_key, canonical_name, country, created_at, updated_at)
            VALUES ('NAME:GB:Test Co', 'Test Co', 'GB', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00')
            """
        )
        asset_id = int(conn.execute("SELECT asset_id FROM assets").fetchone()[0])
        company = make_company(company_name="Test Co", roe=0.20, earnings_yield=0.10)
        upsert_asset_fundamentals(conn, asset_id, company, sector="Healthcare")
        conn.commit()

    row = db.fetchone("SELECT roe, sector FROM asset_fundamentals WHERE asset_id = ?", (asset_id,))
    assert row is not None
    assert row["roe"] == pytest.approx(0.20)
    assert row["sector"] == "Healthcare"


def test_calculate_etf_metrics_matches_schy_reference() -> None:
  project_root = Path(__file__).resolve().parents[1]
  export_dir = project_root / "exports" / "schy_piloto_2026-07-27"
  if not export_dir.exists():
      pytest.skip("Export do piloto SCHY não disponível.")

  from scripts.calculate_etf_metrics import calculate_etf_metrics, validate_against_csv
  from scripts.seed_schy_pilot import seed_schy_pilot

  db = Database(project_root / "data" / "database" / "test_schy_metrics.sqlite")
  if db.path.exists():
      db.path.unlink()
  db.init_schema()
  seed_schy_pilot(db, export_dir)

  aggregate = calculate_etf_metrics(db, "SCHY")
  validation = validate_against_csv(aggregate, export_dir / "etf_consolidado.csv")
  assert validation["ok"], validation["mismatches"]


def test_company_from_csv_row_parses_percentages() -> None:
    row = {
        "roic_symbol": "LSE:TEST",
        "company_name": "Test Co",
        "exchange": "LSE",
        "country": "GB",
        "mapping_status": "manual",
        "fundamental_currency": "GBP",
        "price_currency": "GBP",
        "weight_normalized": "5.5",
        "roe": "0.15",
        "earnings_yield": "0.08",
        "dividend_yield": "0.04",
        "quality": "OK",
        "tags": "TAG_A;TAG_B",
    }
    company = company_from_csv_row(row, "SCHY")
    assert company.roe == pytest.approx(0.15)
    assert company.weight_normalized == pytest.approx(5.5)
    assert company.tags == ["TAG_A", "TAG_B"]
