#!/usr/bin/env python3
"""Extrai composição dos ETFs (gestora e/ou SEC) e salva no banco central."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.catalog.registry import list_etfs, sync_etf_registry
from etf_screener.database.db import Database
from etf_screener.holdings.pipeline import run_holdings_extraction


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extrai composição dos ETFs (Vanguard API, SEC N-PORT, etc.)."
    )
    parser.add_argument("--etf", action="append", help="Ticker específico (ex.: VOO).")
    parser.add_argument("--priority", help="Filtra por prioridade (P1, P2).")
    parser.add_argument("--all", action="store_true", help="Processa todos os ETFs ativos.")
    parser.add_argument("--force", action="store_true", help="Reprocessa snapshot já existente.")
    parser.add_argument("--limit", type=int, help="Limita quantidade de ETFs no lote.")
    parser.add_argument(
        "--source",
        choices=["auto", "vanguard_api", "sec_nport"],
        default="auto",
        help="Força uma fonte (padrão: auto pelo catálogo holdings_sources.json).",
    )
    parser.add_argument(
        "--include-paused",
        action="store_true",
        help="Inclui ETFs pausados quando usar --priority ou --all.",
    )
    args = parser.parse_args()

    if not args.etf and not args.priority and not args.all:
        parser.error("Use --etf, --priority ou --all.")

    db = Database()
    db.init_schema()
    sync_etf_registry(db)

    tickers = args.etf
    if args.all:
        etf_rows = list_etfs(db, include_paused=args.include_paused)
    else:
        etf_rows = list_etfs(
            db,
            priority=args.priority,
            tickers=tickers,
            include_paused=args.include_paused,
        )

    if args.limit is not None:
        etf_rows = etf_rows[: args.limit]

    if not etf_rows:
        print("Nenhum ETF encontrado para processar.")
        return 1

    source = None if args.source == "auto" else args.source
    summary = run_holdings_extraction(db, etf_rows, force=args.force, source=source)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    hard_failures = sum(1 for item in summary["results"] if item.get("status") == "error")
    return 0 if hard_failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
