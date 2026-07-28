#!/usr/bin/env python3
"""Pipeline P1: reprocessar composição → identidade → fundamentos."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> None:
    print(">>", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa pipeline P1 completo.")
    parser.add_argument("--priority", default="P1")
    parser.add_argument("--time-limit-seconds", type=int, default=7200)
    parser.add_argument("--skip-holdings", action="store_true")
    parser.add_argument("--skip-identity", action="store_true")
    parser.add_argument("--skip-fundamentals", action="store_true")
    args = parser.parse_args()

    py = sys.executable
    if not args.skip_holdings:
        _run([py, "scripts/sync_etf_registry.py"])
        _run([py, "scripts/update_holdings.py", "--priority", args.priority])
        _run([py, "scripts/reprocess_compositions.py", "--priority", args.priority])

    if not args.skip_identity:
        _run(
            [
                py,
                "scripts/resolve_asset_identities.py",
                "--priority",
                args.priority,
                "--time-limit-seconds",
                str(args.time_limit_seconds),
                "--reset",
            ]
        )

    if not args.skip_fundamentals:
        _run(
            [
                py,
                "scripts/fetch_p1_assets.py",
                "--priority",
                args.priority,
                "--time-limit-seconds",
                str(args.time_limit_seconds),
            ]
        )

    print(json.dumps({"status": "completed", "priority": args.priority}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
