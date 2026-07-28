#!/usr/bin/env python3
"""Sincroniza asset_fundamentals a partir dos fetches OK (usa cache ROIC)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.database.db import Database
from etf_screener.fundamentals.fetch_worker import AssetWorkItem, fetch_asset_fundamentals
from etf_screener.metrics.persistence import upsert_asset_fundamentals
from etf_screener.roic.auth import load_roic_api_key
from etf_screener.roic.client import RoicClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Popula asset_fundamentals dos fetches OK.")
    parser.add_argument("--priority", default="P1")
    args = parser.parse_args()

    db = Database()
    db.init_schema()
    client = RoicClient(load_roic_api_key())

    rows = db.fetchall(
        """
        SELECT
            aff.asset_id,
            a.canonical_name,
            a.country,
            ai.roic_symbol,
            ai.mapping_status
        FROM asset_fundamental_fetches aff
        JOIN assets a ON a.asset_id = aff.asset_id
        JOIN asset_identities ai ON ai.asset_id = aff.asset_id
        WHERE aff.status = 'ok'
        ORDER BY aff.asset_id
        """
    )

    synced = 0
    failed = 0
    for row in rows:
        item = AssetWorkItem(
            asset_id=int(row["asset_id"]),
            canonical_name=row["canonical_name"],
            country=row["country"] or "",
            roic_symbol=row["roic_symbol"],
            mapping_status=row["mapping_status"],
            max_weight=0.0,
        )
        _, status, _, _, _, error_message, company = fetch_asset_fundamentals(client, item)
        if status != "ok" or company is None:
            failed += 1
            continue
        with db.connect() as conn:
            upsert_asset_fundamentals(conn, item.asset_id, company)
            conn.commit()
        synced += 1

    summary = {"synced": synced, "failed": failed, "total": len(rows)}
    print(json.dumps(summary, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
