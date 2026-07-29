from __future__ import annotations

from etf_screener.catalog.registry import sync_etf_registry
from etf_screener.database.db import Database
from etf_screener.holdings.coverage import asset_ids_for_weight_coverage


def test_coverage_selects_fewer_than_all_for_voo(tmp_path, monkeypatch):
    # Usa o banco real se VOO existir; senão pula via dados mínimos.
    db = Database()
    db.init_schema()
    sync_etf_registry(db)
    row = db.fetchone("SELECT etf_id FROM etfs WHERE ticker='VOO'")
    snap = db.fetchone(
        "SELECT snapshot_id, total_positions FROM composition_snapshots WHERE etf_id=? ORDER BY snapshot_id DESC",
        (row["etf_id"],),
    )
    if snap is None:
        return
    selected = asset_ids_for_weight_coverage(
        db, priority="P1", tickers=["VOO"], coverage_target=0.90
    )
    assert 0 < len(selected) < int(snap["total_positions"])
