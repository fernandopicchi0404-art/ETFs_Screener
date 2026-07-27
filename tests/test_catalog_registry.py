from __future__ import annotations

from pathlib import Path

from etf_screener.catalog.registry import sync_etf_registry
from etf_screener.database.db import Database


def test_sync_etf_registry_loads_universe(tmp_path: Path):
    db_path = tmp_path / "test.sqlite"
    db = Database(db_path)
    count = sync_etf_registry(db)
    assert count == 50
    row = db.fetchone("SELECT COUNT(*) AS total FROM etfs")
    assert row["total"] == 50
