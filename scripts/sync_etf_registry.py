#!/usr/bin/env python3
"""Sincroniza o universo curado de ETFs com o banco SQLite."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.catalog.registry import sync_etf_registry
from etf_screener.database.db import Database


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza ETFs do universo curado com o banco.")
    parser.parse_args()

    db = Database()
    count = sync_etf_registry(db)
    print(f"ETFs sincronizados: {count}")
    print(f"Banco: {db.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
