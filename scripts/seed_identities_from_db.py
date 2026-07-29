#!/usr/bin/env python3
"""Semeia identidades/fundamentos por ISIN a partir do SQLite do dashboard.

Útil para reaproveitar trabalho já feito (ex.: frontend/data) sem gastar cota ROIC.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.config import METHODOLOGY_VERSION, PROJECT_ROOT as ROOT
from etf_screener.database.db import Database
from etf_screener.holdings.coverage import asset_ids_for_weight_coverage
from etf_screener.roic.identity_resolver import APPROVED_STATUSES


DEFAULT_SOURCE = ROOT / "frontend" / "data" / "etf_screener.sqlite"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def seed_from_source(
    db: Database,
    source_path: Path,
    *,
    priority: str = "P1",
    tickers: list[str] | None = None,
    coverage_target: float | None = 0.90,
) -> dict:
    if not source_path.exists():
        raise FileNotFoundError(f"Banco fonte não encontrado: {source_path}")

    allowed = None
    if coverage_target is not None:
        allowed = asset_ids_for_weight_coverage(
            db,
            priority=priority,
            tickers=tickers,
            coverage_target=coverage_target,
        )

    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row

    identity_rows = source.execute(
        f"""
        SELECT fa.isin, ai.roic_symbol, ai.mapping_method, ai.mapping_status,
               ai.match_isin, ai.match_cusip, ai.match_country, ai.candidate_name,
               ai.error_message, ai.requests_used
        FROM asset_identities ai
        JOIN assets fa ON fa.asset_id = ai.asset_id
        WHERE fa.isin IS NOT NULL AND fa.isin != ''
          AND ai.roic_symbol IS NOT NULL
          AND ai.mapping_status IN ({",".join("?" for _ in APPROVED_STATUSES)})
        """,
        tuple(APPROVED_STATUSES),
    ).fetchall()

    fund_rows = {
        row["isin"].upper(): row
        for row in source.execute(
            """
            SELECT fa.isin, af.*
            FROM asset_fundamentals af
            JOIN assets fa ON fa.asset_id = af.asset_id
            WHERE fa.isin IS NOT NULL AND fa.isin != ''
            """
        ).fetchall()
        if row["isin"]
    }

    seeded_identities = 0
    seeded_funds = 0
    skipped = 0
    now = _now()

    with db.connect() as conn:
        for row in identity_rows:
            isin = (row["isin"] or "").upper()
            targets = conn.execute(
                "SELECT asset_id, roic_symbol FROM assets WHERE UPPER(isin) = ?",
                (isin,),
            ).fetchall()
            if not targets:
                continue
            for target in targets:
                asset_id = int(target["asset_id"])
                if allowed is not None and asset_id not in allowed:
                    skipped += 1
                    continue
                existing = conn.execute(
                    "SELECT mapping_status FROM asset_identities WHERE asset_id = ?",
                    (asset_id,),
                ).fetchone()
                if existing and existing["mapping_status"] in APPROVED_STATUSES:
                    skipped += 1
                else:
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
                            row["roic_symbol"],
                            row["mapping_method"] or "verified_isin",
                            row["mapping_status"],
                            now,
                            METHODOLOGY_VERSION,
                            row["match_isin"] or isin,
                            row["match_cusip"],
                            row["match_country"],
                            row["candidate_name"],
                            row["error_message"],
                            int(row["requests_used"] or 0),
                        ),
                    )
                    conn.execute(
                        "UPDATE assets SET roic_symbol = ?, updated_at = ? WHERE asset_id = ?",
                        (row["roic_symbol"], now, asset_id),
                    )
                    seeded_identities += 1

                fund = fund_rows.get(isin)
                if fund is None:
                    continue
                already = conn.execute(
                    "SELECT 1 FROM asset_fundamentals WHERE asset_id = ?",
                    (asset_id,),
                ).fetchone()
                if already:
                    continue
                cols = [
                    "roic_symbol",
                    "exchange",
                    "sector",
                    "industry",
                    "mapping_status",
                    "fundamental_currency",
                    "price_currency",
                    "fiscal_year",
                    "fiscal_year_end",
                    "price_date",
                    "price",
                    "earnings_for_common",
                    "diluted_shares",
                    "diluted_eps",
                    "common_equity_average",
                    "roe",
                    "roe_method",
                    "earnings_yield",
                    "dividend_yield",
                    "gross_buyback_yield",
                    "net_buyback_yield",
                    "gross_shareholder_yield",
                    "net_shareholder_yield",
                    "quality",
                    "tags",
                    "notes",
                ]
                values = [fund[c] for c in cols]
                conn.execute(
                    f"""
                    INSERT INTO asset_fundamentals (
                        asset_id, {", ".join(cols)}, methodology_version, calculated_at
                    ) VALUES (?, {", ".join("?" for _ in cols)}, ?, ?)
                    """,
                    (asset_id, *values, METHODOLOGY_VERSION, now),
                )
                conn.execute(
                    """
                    INSERT INTO asset_fundamental_fetches (
                        asset_id, roic_symbol, mapping_status, status, fiscal_year, price_date,
                        fetched_at, error_tag, error_message, requests_used
                    ) VALUES (?, ?, ?, 'ok', ?, ?, ?, NULL, NULL, 0)
                    ON CONFLICT(asset_id) DO UPDATE SET
                        roic_symbol = excluded.roic_symbol,
                        mapping_status = excluded.mapping_status,
                        status = 'ok',
                        fiscal_year = excluded.fiscal_year,
                        price_date = excluded.price_date,
                        fetched_at = excluded.fetched_at
                    """,
                    (
                        asset_id,
                        fund["roic_symbol"],
                        fund["mapping_status"],
                        fund["fiscal_year"],
                        fund["price_date"],
                        now,
                    ),
                )
                seeded_funds += 1
        conn.commit()

    source.close()
    return {
        "source": str(source_path),
        "priority": priority,
        "tickers": tickers,
        "coverage_target": coverage_target,
        "allowed_assets": len(allowed) if allowed is not None else None,
        "seeded_identities": seeded_identities,
        "seeded_fundamentals": seeded_funds,
        "skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Semeia identidades/fundamentos por ISIN.")
    parser.add_argument("--source-db", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--priority", default="P1")
    parser.add_argument("--etf", action="append")
    parser.add_argument("--coverage-target", type=float, default=0.90)
    args = parser.parse_args()
    coverage = None if args.coverage_target == 0 else args.coverage_target
    db = Database()
    db.init_schema()
    summary = seed_from_source(
        db,
        args.source_db,
        priority=args.priority,
        tickers=args.etf,
        coverage_target=coverage,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
