from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from etf_screener.api.main import app
from etf_screener.database.db import Database

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_api_lists_schy_with_metrics() -> None:
    from scripts.calculate_etf_metrics import calculate_etf_metrics
    from scripts.seed_schy_pilot import seed_schy_pilot

    project_root = PROJECT_ROOT
    export_dir = project_root / "exports" / "schy_piloto_2026-07-27"
    if not export_dir.exists():
        return

    db_path = project_root / "data" / "database" / "test_api.sqlite"
    if db_path.exists():
        db_path.unlink()

    db = Database(db_path)
    db.init_schema()
    seed_schy_pilot(db, export_dir)
    calculate_etf_metrics(db, "SCHY")

    import etf_screener.api.routes as routes

    original_db = routes._db
    routes._db = lambda: db
    try:
        client = TestClient(app)
        response = client.get("/api/etfs?search=SCHY")
        assert response.status_code == 200
        data = response.json()
        schy = next(item for item in data if item["ticker"] == "SCHY")
        assert schy["has_metrics"] is True
        assert schy["roe_pct"] == 16.86

        detail = client.get("/api/etfs/SCHY")
        assert detail.status_code == 200
        assert detail.json()["earnings_yield_pct"] == 5.46

        holdings = client.get("/api/etfs/SCHY/holdings?limit=10")
        assert holdings.status_code == 200
        assert len(holdings.json()) == 10

        assets = client.get("/api/assets")
        assert assets.status_code == 200
        assert len(assets.json()) >= 90
    finally:
        routes._db = original_db
