#!/usr/bin/env python3
"""Gera snapshot de status da coleta P1 (identidade + fundamentos)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.database.db import Database

APPROVED = ("verified_isin", "verified_cusip", "verified_symbol", "manual_approved")


def main() -> int:
    db = Database()
    identities = {
        row["mapping_status"]: row["cnt"]
        for row in db.fetchall(
            "SELECT mapping_status, COUNT(*) AS cnt FROM asset_identities GROUP BY mapping_status"
        )
    }
    fundamentals = {
        row["status"]: row["cnt"]
        for row in db.fetchall(
            "SELECT status, COUNT(*) AS cnt FROM asset_fundamental_fetches GROUP BY status"
        )
    }
    p1_assets = db.fetchone(
        """
        SELECT COUNT(DISTINCT a.asset_id) AS cnt
        FROM assets a
        JOIN holdings h ON h.asset_id = a.asset_id
        JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
        JOIN etfs e ON e.etf_id = cs.etf_id
        WHERE e.priority = 'P1' AND h.included_in_equity_analysis = 1
        """
    )["cnt"]
    approved = sum(identities.get(s, 0) for s in APPROVED)
    ok = fundamentals.get("ok", 0)
    errors = fundamentals.get("fetch_error", 0)
    done = ok + errors

    report = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "p1_unique_assets": p1_assets,
        "identity": {
            "total": sum(identities.values()),
            "approved": approved,
            "rejected": identities.get("rejected", 0),
            "review_required": identities.get("review_required", 0),
            "not_found": identities.get("not_found", 0),
            "by_status": identities,
            "complete": sum(identities.values()) >= p1_assets,
        },
        "fundamentals": {
            "queue_size": approved,
            "processed": done,
            "ok": ok,
            "fetch_error": errors,
            "pending": max(0, approved - done),
            "pct_complete": round(done / approved * 100, 1) if approved else 0,
        },
    }

    out = PROJECT_ROOT / "data" / "exports" / "status_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
