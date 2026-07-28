#!/usr/bin/env python3
"""Calcula e persiste métricas consolidadas de ETFs no banco."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.catalog.registry import get_etf_by_ticker, list_etfs
from etf_screener.database.db import Database
from etf_screener.holdings.selection import consolidate_equity_holdings, renormalize_consolidated_holdings
from etf_screener.metrics.fundamentals import aggregate_etf
from etf_screener.metrics.persistence import (
    assign_consolidated_weights,
    load_companies_for_etf,
    upsert_etf_consolidated_metrics,
)

DEFAULT_REFERENCE_CSV = PROJECT_ROOT / "exports" / "schy_piloto_2026-07-27" / "etf_consolidado.csv"
COMPARE_FIELDS = [
    "roe_aggregate",
    "earnings_yield_aggregate",
    "dividend_yield_aggregate",
    "gross_shareholder_yield_aggregate",
    "clean_coverage_pct",
    "equity_positions",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def calculate_etf_metrics(
    db: Database,
    ticker: str,
    *,
    target_clean_coverage: float = 0.90,
    snapshot_id: int | None = None,
) -> dict:
    """Calcula agregados a partir do banco e grava em etf_consolidated_metrics."""
    etf_row = get_etf_by_ticker(db, ticker)
    if not etf_row:
        raise ValueError(f"ETF não encontrado: {ticker}")

    companies, holdings, snapshot = load_companies_for_etf(
        db,
        ticker,
        snapshot_id=snapshot_id,
    )
    equities = renormalize_consolidated_holdings(consolidate_equity_holdings(holdings))
    companies = assign_consolidated_weights(companies, equities)
    aggregate = aggregate_etf(companies, equities, target_clean_coverage=target_clean_coverage)
    aggregate["etf"] = ticker.upper()
    aggregate["composition_date"] = snapshot.get("composition_date")
    aggregate["run_date"] = _now()[:10]

    with db.connect() as conn:
        upsert_etf_consolidated_metrics(
            conn,
            int(etf_row["etf_id"]),
            int(snapshot["snapshot_id"]),
            aggregate,
            composition_date=snapshot.get("composition_date"),
            calculated_at=_now(),
        )
        conn.commit()

    return aggregate


def validate_against_csv(aggregate: dict, reference_csv: Path, tolerance: float = 1e-6) -> dict:
    """Compara agregados calculados com CSV de referência do piloto."""
    with reference_csv.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))

    mismatches: list[dict] = []
    for field in COMPARE_FIELDS:
        expected = row.get(field)
        actual = aggregate.get(field)
        if expected in (None, ""):
            continue
        expected_f = float(expected)
        actual_f = float(actual) if actual is not None else None
        if actual_f is None or abs(actual_f - expected_f) > tolerance:
            mismatches.append(
                {
                    "field": field,
                    "expected": expected_f,
                    "actual": actual_f,
                    "diff": None if actual_f is None else actual_f - expected_f,
                }
            )

    return {
        "reference_csv": str(reference_csv),
        "fields_checked": len(COMPARE_FIELDS),
        "mismatches": mismatches,
        "ok": not mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calcula métricas consolidadas de ETFs.")
    parser.add_argument("--etf", help="Ticker do ETF (ex.: SCHY).")
    parser.add_argument("--priority", help="Calcula todos os ETFs da prioridade (ex.: P1).")
    parser.add_argument("--all", action="store_true", help="Calcula todos os ETFs ativos com snapshot.")
    parser.add_argument(
        "--target-clean-coverage",
        type=float,
        default=0.90,
        help="Meta de cobertura limpa (0-1). Padrão: 0.90",
    )
    parser.add_argument(
        "--validate",
        type=Path,
        default=None,
        help="CSV de referência para validar os agregados.",
    )
    parser.add_argument(
        "--auto-validate-schy",
        action="store_true",
        help="Valida automaticamente contra o CSV do piloto SCHY, se existir.",
    )
    args = parser.parse_args()

    if not args.etf and not args.priority and not args.all:
        parser.error("Use --etf, --priority ou --all.")

    db = Database()
    db.init_schema()

    if args.all:
        etf_rows = list_etfs(db)
    elif args.priority:
        etf_rows = list_etfs(db, priority=args.priority)
    else:
        etf_rows = [{"ticker": args.etf.upper()}]

    results: list[dict] = []
    errors: list[dict] = []
    for row in etf_rows:
        ticker = row["ticker"]
        try:
            aggregate = calculate_etf_metrics(
                db,
                ticker,
                target_clean_coverage=args.target_clean_coverage,
            )
            results.append(aggregate)
            print(json.dumps(aggregate, indent=2, default=str))

            reference = args.validate
            if args.auto_validate_schy and reference is None and ticker.upper() == "SCHY":
                reference = DEFAULT_REFERENCE_CSV
            if reference is not None:
                if not reference.exists():
                    print(f"Arquivo de referência não encontrado: {reference}", file=sys.stderr)
                    return 1
                validation = validate_against_csv(aggregate, reference)
                print(json.dumps(validation, indent=2))
                if not validation["ok"]:
                    return 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"ticker": ticker, "error": str(exc)})

    export_dir = PROJECT_ROOT / "data" / "exports" / "etf_metrics"
    export_dir.mkdir(parents=True, exist_ok=True)
    summary_path = export_dir / "p1_consolidated.json"
    summary_path.write_text(
        json.dumps({"ok": results, "errors": errors}, indent=2, default=str),
        encoding="utf-8",
    )
    print(json.dumps({"calculated": len(results), "errors": len(errors), "export": str(summary_path)}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
