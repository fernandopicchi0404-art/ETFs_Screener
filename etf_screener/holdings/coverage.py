"""Seleção de ativos por cobertura de peso (meta tipicamente 90%)."""

from __future__ import annotations

from typing import Any, Sequence

from etf_screener.database.db import Database


def asset_ids_for_weight_coverage(
    db: Database,
    *,
    priority: str | None = "P1",
    tickers: Sequence[str] | None = None,
    coverage_target: float = 0.90,
    active_only: bool = True,
) -> set[int]:
    """Une, por ETF, os maiores holdings até atingir coverage_target do peso equity."""
    if coverage_target <= 0:
        raise ValueError("coverage_target deve ser > 0.")
    if coverage_target > 1:
        # Aceita 90 ou 0.90
        coverage_target = coverage_target / 100.0

    sql = """
        SELECT e.ticker, e.etf_id
        FROM etfs e
        WHERE 1=1
    """
    params: list[Any] = []
    if active_only:
        sql += " AND e.status = 'active'"
    if priority:
        sql += " AND e.priority = ?"
        params.append(priority)
    if tickers:
        placeholders = ",".join("?" for _ in tickers)
        sql += f" AND e.ticker IN ({placeholders})"
        params.extend(t.upper() for t in tickers)
    sql += " ORDER BY e.ticker"

    selected: set[int] = set()
    for etf in db.fetchall(sql, tuple(params)):
        rows = db.fetchall(
            """
            SELECT h.asset_id, h.weight_normalized
            FROM holdings h
            JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
            WHERE cs.etf_id = ?
              AND h.included_in_equity_analysis = 1
              AND h.asset_id IS NOT NULL
              AND cs.snapshot_id = (
                  SELECT MAX(cs2.snapshot_id)
                  FROM composition_snapshots cs2
                  WHERE cs2.etf_id = ?
              )
            ORDER BY h.weight_normalized DESC, h.position ASC
            """,
            (etf["etf_id"], etf["etf_id"]),
        )
        total = sum(float(row["weight_normalized"] or 0) for row in rows)
        if total <= 0:
            continue
        cumulative = 0.0
        for row in rows:
            selected.add(int(row["asset_id"]))
            cumulative += float(row["weight_normalized"] or 0)
            if cumulative / total >= coverage_target:
                break
    return selected


def filter_rows_by_asset_ids(
    rows: list[dict[str, Any]],
    asset_ids: set[int] | None,
) -> list[dict[str, Any]]:
    if asset_ids is None:
        return rows
    return [row for row in rows if int(row["asset_id"]) in asset_ids]
