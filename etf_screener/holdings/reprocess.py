from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from etf_screener.catalog.registry import list_etfs
from etf_screener.config import EXPORTS_DIR, METHODOLOGY_VERSION
from etf_screener.database.db import Database
from etf_screener.holdings.asset_registry import link_holdings_to_assets
from etf_screener.holdings.sec_nport import normalize_equity_weights, parse_nport_holdings


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def reprocess_snapshot(conn, snapshot_id: int, etf_ticker: str, raw_path: str, now: str) -> dict[str, Any]:
    path = Path(raw_path)
    if not path.exists():
        return {"snapshot_id": snapshot_id, "status": "missing_raw", "path": raw_path}

    holdings = normalize_equity_weights(parse_nport_holdings(path, etf_ticker))
    conn.execute("DELETE FROM holdings WHERE snapshot_id = ?", (snapshot_id,))

    for holding in holdings:
        conn.execute(
            """
            INSERT INTO holdings (
                snapshot_id, asset_id, position, name_raw, asset_category, asset_type, country,
                cusip, isin, lei, sec_ticker, other_id, weight_original, weight_normalized,
                market_value_usd, included_in_equity_analysis, exclusion_reason
            ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                holding.position,
                holding.name,
                holding.asset_category,
                holding.asset_type,
                holding.country,
                holding.cusip,
                holding.isin,
                holding.lei,
                holding.sec_ticker,
                holding.other_id,
                holding.weight_original,
                holding.weight_normalized,
                holding.market_value_usd,
                1 if holding.included_in_equity_analysis else 0,
                holding.exclusion_reason,
            ),
        )

    linked = link_holdings_to_assets(conn, snapshot_id, now)
    with_isin = sum(1 for h in holdings if h.isin)
    return {
        "snapshot_id": snapshot_id,
        "ticker": etf_ticker,
        "status": "ok",
        "positions": len(holdings),
        "with_isin": with_isin,
        "linked_assets": linked,
    }


def run_reprocess(db: Database, priority: str | None = None, tickers: list[str] | None = None) -> dict[str, Any]:
    db.init_schema()
    etf_rows = list_etfs(db, priority=priority, tickers=tickers)
    now = _now()
    results: list[dict[str, Any]] = []

    with db.connect() as conn:
        for etf in etf_rows:
            row = conn.execute(
                """
                SELECT cs.snapshot_id, cs.raw_path
                FROM composition_snapshots cs
                WHERE cs.etf_id = ?
                ORDER BY cs.snapshot_id DESC
                LIMIT 1
                """,
                (etf["etf_id"],),
            ).fetchone()
            if row is None or not row["raw_path"]:
                results.append({"ticker": etf["ticker"], "status": "no_snapshot"})
                continue
            results.append(
                reprocess_snapshot(conn, int(row["snapshot_id"]), etf["ticker"], row["raw_path"], now)
            )
        conn.commit()

    summary = {
        "started_at": now,
        "finished_at": _now(),
        "methodology_version": METHODOLOGY_VERSION,
        "results": results,
        "ok": sum(1 for r in results if r.get("status") == "ok"),
        "with_isin_total": sum(r.get("with_isin", 0) for r in results),
    }
    path = EXPORTS_DIR / "compositions" / "reprocess_summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    summary["summary_path"] = str(path)
    return summary
