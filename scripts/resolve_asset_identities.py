#!/usr/bin/env python3
"""Resolve identidades ROIC (ISIN/CUSIP/ticker+bolsa) antes dos fundamentos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.database.db import Database
from etf_screener.identity.pipeline import run_identity_resolution


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve identidades ROIC para ativos P1.")
    parser.add_argument("--priority", default="P1")
    parser.add_argument("--etf", action="append", help="Limita a ticker(s), ex.: --etf VOO")
    parser.add_argument("--time-limit-seconds", type=int, default=7200)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--coverage-target",
        type=float,
        default=0.90,
        help="Processa só ativos necessários para esta cobertura de peso (padrão 0.90). Use 0 para todos.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Apaga identidades e fetches anteriores antes de recomeçar.",
    )
    parser.add_argument(
        "--retry-excluded",
        action="store_true",
        help="Reprocessa apenas ativos rejeitados, em revisão ou não encontrados.",
    )
    args = parser.parse_args()

    coverage = None if args.coverage_target == 0 else args.coverage_target
    db = Database()
    db.init_schema()
    summary = run_identity_resolution(
        db,
        priority=args.priority,
        time_limit_seconds=args.time_limit_seconds,
        limit=args.limit,
        reset=args.reset,
        retry_excluded=args.retry_excluded,
        tickers=args.etf,
        coverage_target=coverage,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
