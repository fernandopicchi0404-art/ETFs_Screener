from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

from etf_screener.config import EXPORTS_DIR, METHODOLOGY_VERSION, RUNS_DIR
from etf_screener.database.db import Database
from etf_screener.roic.auth import load_roic_api_key
from etf_screener.roic.client import RoicClient
from etf_screener.roic.identity_resolver import APPROVED_STATUSES, IdentityResult, resolve_asset_identity


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_assets_for_identity(db: Database, priority: str = "P1") -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in db.fetchall(
            """
            SELECT
                a.asset_id,
                a.canonical_name,
                a.country,
                a.isin,
                a.cusip,
                a.roic_symbol,
                MAX(h.sec_ticker) AS sec_ticker,
                MAX(h.weight_normalized) AS max_weight
            FROM assets a
            JOIN holdings h ON h.asset_id = a.asset_id
            JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
            JOIN etfs e ON e.etf_id = cs.etf_id
            WHERE e.priority = ?
              AND h.included_in_equity_analysis = 1
              AND cs.snapshot_id = (
                  SELECT MAX(cs2.snapshot_id)
                  FROM composition_snapshots cs2
                  WHERE cs2.etf_id = e.etf_id
              )
            GROUP BY a.asset_id
            ORDER BY max_weight DESC, a.canonical_name
            """,
            (priority,),
        )
    ]


def pending_identity_assets(db: Database, priority: str = "P1") -> list[dict[str, Any]]:
    approved = {
        int(row["asset_id"])
        for row in db.fetchall(
            f"""
            SELECT asset_id FROM asset_identities
            WHERE mapping_status IN ({",".join("?" for _ in APPROVED_STATUSES)})
            """,
            tuple(APPROVED_STATUSES),
        )
    }
    return [row for row in list_assets_for_identity(db, priority) if int(row["asset_id"]) not in approved]


def excluded_identity_assets(db: Database, priority: str = "P1") -> list[dict[str, Any]]:
    excluded_ids = {
        int(row["asset_id"])
        for row in db.fetchall(
            """
            SELECT asset_id FROM asset_identities
            WHERE mapping_status IN ('rejected', 'review_required', 'not_found')
            """
        )
    }
    return [
        row
        for row in list_assets_for_identity(db, priority)
        if int(row["asset_id"]) in excluded_ids
    ]


def save_identity(conn, asset_id: int, result: IdentityResult, country: str | None = None) -> None:
    conn.execute(
        """
        INSERT INTO asset_identities (
            asset_id, roic_symbol, mapping_method, mapping_status, validated_at,
            methodology_version, match_isin, match_cusip, match_country,
            candidate_name, error_message, requests_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            roic_symbol = excluded.roic_symbol,
            mapping_method = excluded.mapping_method,
            mapping_status = excluded.mapping_status,
            validated_at = excluded.validated_at,
            methodology_version = excluded.methodology_version,
            match_isin = excluded.match_isin,
            match_cusip = excluded.match_cusip,
            match_country = excluded.match_country,
            candidate_name = excluded.candidate_name,
            error_message = excluded.error_message,
            requests_used = excluded.requests_used
        """,
        (
            asset_id,
            result.roic_symbol,
            result.mapping_method,
            result.mapping_status,
            _now(),
            METHODOLOGY_VERSION,
            result.match_isin,
            result.match_cusip,
            country,
            result.candidate_name,
            result.error_message,
            result.requests_used,
        ),
    )
    if result.roic_symbol and result.mapping_status in APPROVED_STATUSES:
        updates = ["roic_symbol = ?", "updated_at = ?"]
        params: list[Any] = [result.roic_symbol, _now()]
        if result.candidate_name:
            updates.insert(1, "canonical_name = ?")
            params.insert(1, result.candidate_name)
        params.append(asset_id)
        conn.execute(
            f"UPDATE assets SET {', '.join(updates)} WHERE asset_id = ?",
            tuple(params),
        )


def run_identity_resolution(
    db: Database,
    priority: str = "P1",
    time_limit_seconds: int = 7200,
    limit: int | None = None,
    reset: bool = False,
    retry_excluded: bool = False,
) -> dict[str, Any]:
    if reset:
        db.execute("DELETE FROM asset_identities")
        db.execute("DELETE FROM asset_fundamental_fetches")

    api_key = load_roic_api_key()
    client = RoicClient(api_key)
    if retry_excluded:
        queue = excluded_identity_assets(db, priority)
    else:
        queue = pending_identity_assets(db, priority)
    if limit is not None:
        queue = queue[:limit]

    started = time.monotonic()
    deadline = started + time_limit_seconds
    run_id = _now().replace(":", "-")
    run_dir = RUNS_DIR / f"identity_{priority.lower()}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "priority": priority,
        "started_at": _now(),
        "time_limit_seconds": time_limit_seconds,
        "queue_size": len(queue),
        "processed": 0,
        "approved": 0,
        "review_required": 0,
        "not_found": 0,
        "rejected": 0,
        "retry_excluded": retry_excluded,
        "requests_used": 0,
        "stopped_reason": None,
    }

    for index, row in enumerate(queue, start=1):
        if time.monotonic() >= deadline:
            summary["stopped_reason"] = "time_limit"
            break

        result = resolve_asset_identity(
            client,
            company_name=row["canonical_name"],
            country=row["country"] or "",
            isin=row.get("isin"),
            cusip=row.get("cusip"),
            sec_ticker=row.get("sec_ticker"),
            known_roic_symbol=None,
        )

        summary["processed"] += 1
        summary["requests_used"] += result.requests_used
        if result.mapping_status in APPROVED_STATUSES:
            summary["approved"] += 1
        elif result.mapping_status == "review_required":
            summary["review_required"] += 1
        elif result.mapping_status == "not_found":
            summary["not_found"] += 1
        else:
            summary["rejected"] += 1

        with db.connect() as conn:
            save_identity(conn, int(row["asset_id"]), result, country=row.get("country"))
            conn.commit()

        if index % 25 == 0:
            (run_dir / "progress.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    if summary["stopped_reason"] is None:
        summary["stopped_reason"] = "queue_completed" if summary["processed"] == len(queue) else "partial"

    summary["finished_at"] = _now()
    summary["elapsed_seconds"] = round(time.monotonic() - started, 1)
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    summary["summary_path"] = str(summary_path)

    export_path = EXPORTS_DIR / "identities" / priority.lower() / "identity_summary.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
