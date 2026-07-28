#!/usr/bin/env python3
"""Reprocessa composições a partir dos XMLs locais (corrige ISIN e identificadores)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.database.db import Database
from etf_screener.holdings.reprocess import run_reprocess


def main() -> int:
    parser = argparse.ArgumentParser(description="Reprocessa snapshots N-PORT já baixados.")
    parser.add_argument("--priority", help="Prioridade (P1, P2).")
    parser.add_argument("--etf", action="append", help="Ticker específico.")
    args = parser.parse_args()

    db = Database()
    summary = run_reprocess(db, priority=args.priority, tickers=args.etf)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
