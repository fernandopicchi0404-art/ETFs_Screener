from __future__ import annotations

import csv
import json
from pathlib import Path

from etf_screener.config import MAPPING_DIR


def load_symbol_map(etf: str) -> dict[str, dict[str, str]]:
    path = MAPPING_DIR / f"{etf.lower()}_symbols.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_symbol_map(etf: str, mapping: dict[str, dict[str, str]]) -> None:
    MAPPING_DIR.mkdir(parents=True, exist_ok=True)
    path = MAPPING_DIR / f"{etf.lower()}_symbols.json"
    path.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")


def load_symbol_map_csv(path: Path) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    if not path.exists():
        return mapping

    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = row["name"].strip()
            mapping[name] = {
                "symbol": row.get("symbol", "").strip(),
                "cusip": row.get("cusip", "").strip(),
                "country": row.get("country", "").strip(),
                "roic_symbol": row.get("roic_symbol", "").strip(),
            }
    return mapping
