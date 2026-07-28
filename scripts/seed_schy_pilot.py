#!/usr/bin/env python3
"""Importa dados do piloto SCHY (CSV) para o banco SQLite."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.catalog.registry import get_etf_by_ticker, sync_etf_registry
from etf_screener.config import METHODOLOGY_VERSION
from etf_screener.database.db import Database
from etf_screener.holdings.asset_registry import link_holdings_to_assets
from etf_screener.metrics.persistence import (
    company_from_csv_row,
    holding_from_csv_row,
    upsert_asset_fundamentals,
)

DEFAULT_EXPORT_DIR = PROJECT_ROOT / "exports" / "schy_piloto_2026-07-27"
ETF = "SCHY"
COMPOSITION_DATE = "2026-02-28"
ACCESSION_NUMBER = "schy-pilot-2026-02-28"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def seed_schy_pilot(db: Database, export_dir: Path) -> dict[str, int]:
    """Carrega composição e fundamentos do piloto SCHY no banco."""
    composicao_path = export_dir / "composicao_etf.csv"
    ativos_path = export_dir / "ativos.csv"
    if not composicao_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {composicao_path}")
    if not ativos_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ativos_path}")

    sync_etf_registry(db)
    etf_row = get_etf_by_ticker(db, ETF)
    if not etf_row:
        raise RuntimeError(f"ETF {ETF} não encontrado após sincronização do cadastro.")

    etf_id = int(etf_row["etf_id"])
    holdings_rows = _read_csv(composicao_path)
    companies_rows = _read_csv(ativos_path)
    now = _now()

    with db.connect() as conn:
        conn.execute(
            """
            INSERT INTO composition_snapshots (
                etf_id, composition_date, report_period_end, filing_date, accession_number,
                source_url, raw_path, methodology_version, extracted_at, status,
                total_positions, equity_positions, total_weight_pct, equity_weight_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(etf_id, accession_number) DO UPDATE SET
                composition_date = excluded.composition_date,
                extracted_at = excluded.extracted_at,
                status = excluded.status,
                total_positions = excluded.total_positions,
                equity_positions = excluded.equity_positions,
                total_weight_pct = excluded.total_weight_pct,
                equity_weight_pct = excluded.equity_weight_pct
            """,
            (
                etf_id,
                COMPOSITION_DATE,
                COMPOSITION_DATE,
                COMPOSITION_DATE,
                ACCESSION_NUMBER,
                None,
                str(composicao_path),
                METHODOLOGY_VERSION,
                now,
                "ok",
                len(holdings_rows),
                sum(
                    1
                    for row in holdings_rows
                    if str(row.get("included_in_equity_analysis", "")).lower() in {"true", "1"}
                ),
                sum(float(row.get("weight_original") or 0) for row in holdings_rows),
                sum(
                    float(row.get("weight_original") or 0)
                    for row in holdings_rows
                    if str(row.get("included_in_equity_analysis", "")).lower() in {"true", "1"}
                ),
            ),
        )
        snapshot_id = int(
            conn.execute(
                "SELECT snapshot_id FROM composition_snapshots WHERE etf_id = ? AND accession_number = ?",
                (etf_id, ACCESSION_NUMBER),
            ).fetchone()[0]
        )

        conn.execute("DELETE FROM holdings WHERE snapshot_id = ?", (snapshot_id,))

        for row in holdings_rows:
            holding = holding_from_csv_row(row, ETF)
            conn.execute(
                """
                INSERT INTO holdings (
                    snapshot_id, asset_id, position, name_raw, asset_category, asset_type, country,
                    cusip, isin, weight_original, weight_normalized, market_value_usd,
                    included_in_equity_analysis, exclusion_reason
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    holding.weight_original,
                    holding.weight_normalized,
                    holding.market_value_usd,
                    1 if holding.included_in_equity_analysis else 0,
                    holding.exclusion_reason,
                ),
            )

        linked = link_holdings_to_assets(conn, snapshot_id, now)

        fundamentals_saved = 0
        for row in companies_rows:
            company = company_from_csv_row(row, ETF)
            asset_row = conn.execute(
                """
                SELECT a.asset_id
                FROM assets a
                JOIN holdings h ON h.asset_id = a.asset_id
                WHERE h.snapshot_id = ?
                  AND a.canonical_name = ?
                LIMIT 1
                """,
                (snapshot_id, company.company_name),
            ).fetchone()
            if not asset_row:
                continue
            upsert_asset_fundamentals(conn, int(asset_row[0]), company, calculated_at=now)
            fundamentals_saved += 1

        conn.commit()

    return {
        "etf_id": etf_id,
        "snapshot_id": snapshot_id,
        "holdings": len(holdings_rows),
        "assets_linked": linked,
        "fundamentals_saved": fundamentals_saved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa piloto SCHY para o banco SQLite.")
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=DEFAULT_EXPORT_DIR,
        help="Pasta com os CSVs do piloto SCHY.",
    )
    args = parser.parse_args()

    db = Database()
    db.init_schema()
    summary = seed_schy_pilot(db, args.export_dir)
    print(f"Piloto SCHY importado: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
