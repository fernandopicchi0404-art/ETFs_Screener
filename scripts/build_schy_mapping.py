#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.config import RAW_DIR
from etf_screener.holdings.sec_nport import parse_nport_holdings
from etf_screener.holdings.symbol_map import load_symbol_map, save_symbol_map
from etf_screener.roic.client import RoicClient
from etf_screener.roic.resolver import resolve_roic_symbol
from scripts.run_schy_pilot import NPORT_PATH, ensure_nport_file, load_api_key


def build_mapping(limit: int | None = None) -> None:
    ensure_nport_file()
    holdings = [h for h in parse_nport_holdings(NPORT_PATH, "SCHY") if h.included_in_equity_analysis]
    if limit is not None:
        holdings = holdings[:limit]

    client = RoicClient(load_api_key())
    mapping = load_symbol_map("SCHY")
    results = []

    for index, holding in enumerate(holdings, start=1):
        print(f"[{index}/{len(holdings)}] Mapeando {holding.name}...")
        existing = mapping.get(holding.name, {})
        if existing.get("roic_symbol"):
            results.append({**existing, "name": holding.name, "status": "cached"})
            continue

        symbol, status, candidates = resolve_roic_symbol(
            client,
            company_name=holding.name,
            country=holding.country,
            known_symbol=existing.get("symbol"),
            known_roic_symbol=existing.get("roic_symbol"),
        )
        entry = {
            "name": holding.name,
            "country": holding.country,
            "symbol": existing.get("symbol", ""),
            "cusip": holding.cusip or "",
            "roic_symbol": symbol or "",
            "status": status,
            "top_candidates": [
                {
                    "symbol": candidate.get("symbol"),
                    "name": candidate.get("name"),
                    "country": candidate.get("listing_country_code"),
                    "score": candidate.get("_score"),
                }
                for candidate in candidates[:3]
            ],
        }
        results.append(entry)
        if symbol:
            mapping[holding.name] = {
                "symbol": entry["symbol"],
                "cusip": entry["cusip"],
                "country": holding.country,
                "roic_symbol": symbol,
                "status": status,
            }
            save_symbol_map("SCHY", mapping)

    output = PROJECT_ROOT / "data" / "mappings" / "schy_mapping_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    mapped = sum(1 for item in results if item.get("roic_symbol"))
    print(json.dumps({"mapped": mapped, "total": len(results), "report": str(output)}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Constrói mapeamento SCHY -> ROIC.")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    build_mapping(limit=args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
