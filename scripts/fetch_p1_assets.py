#!/usr/bin/env python3
"""Levantamento ROIC de ativos por prioridade (P1) com limite de tempo."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.config import EXPORTS_DIR, RUNS_DIR
from etf_screener.database.db import Database
from etf_screener.fundamentals.fetch_worker import (
    _now,
    fetch_asset_fundamentals,
    pending_fetch_retries,
    pending_verified_fetches,
    record_fetch,
)
from etf_screener.roic.auth import load_roic_api_key
from etf_screener.roic.client import RoicClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Levanta fundamentos ROIC para ativos P1.")
    parser.add_argument("--priority", default="P1", help="Prioridade do universo (padrão: P1).")
    parser.add_argument(
        "--time-limit-seconds",
        type=int,
        default=7200,
        help="Tempo máximo de execução (padrão: 7200 = 2 horas).",
    )
    parser.add_argument("--limit", type=int, help="Limita quantidade de ativos nesta execução.")
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="Reprocessa apenas ativos com fetch_error anterior.",
    )
    args = parser.parse_args()

    api_key = load_roic_api_key()
    db = Database()
    db.init_schema()

    if args.retry_errors:
        queue = pending_fetch_retries(db, priority=args.priority)
    else:
        queue = pending_verified_fetches(db, priority=args.priority)
    if args.limit is not None:
        queue = queue[:args.limit]

    if not queue:
        print("Nenhum ativo verificado pendente para esta prioridade.")
        return 0

    started = time.monotonic()
    deadline = started + args.time_limit_seconds
    run_id = _now().replace(":", "-")
    run_dir = RUNS_DIR / f"fetch_{args.priority.lower()}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    export_path = EXPORTS_DIR / "fundamentals" / args.priority.lower() / "ativos_verificados.jsonl"
    export_path.parent.mkdir(parents=True, exist_ok=True)

    client = RoicClient(api_key)
    summary = {
        "priority": args.priority,
        "mode": "verified_only",
        "started_at": _now(),
        "time_limit_seconds": args.time_limit_seconds,
        "queue_size": len(queue),
        "processed": 0,
        "ok": 0,
        "mapping_failed": 0,
        "fetch_error": 0,
        "stopped_reason": None,
        "requests_used": 0,
        "results": [],
    }

    print(
        f"Iniciando fundamentos {args.priority} (somente verificados): {len(queue)} ativos, "
        f"limite {args.time_limit_seconds}s (plano gratuito).",
        flush=True,
    )

    for index, item in enumerate(queue, start=1):
        if time.monotonic() >= deadline:
            summary["stopped_reason"] = "time_limit"
            print("Limite de tempo atingido.", flush=True)
            break

        print(
            f"[{index}/{len(queue)}] {item.canonical_name} "
            f"(peso max {item.max_weight:.2f}%)...",
            flush=True,
        )

        payload, status, roic_symbol, mapping_status, requests_used, error_message = (
            fetch_asset_fundamentals(client, item)
        )
        fetched_at = _now()
        summary["processed"] += 1
        summary["requests_used"] += requests_used

        fiscal_year = payload.get("fiscal_year") if payload else None
        price_date = payload.get("price_date") if payload else None
        error_tag = None
        if status == "fetch_error":
            summary["fetch_error"] += 1
            error_tag = "API_FETCH_FAILURE"
        else:
            summary["ok"] += 1
            with export_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

        with db.connect() as conn:
            if roic_symbol:
                conn.execute(
                    "UPDATE assets SET roic_symbol = ?, updated_at = ? WHERE asset_id = ?",
                    (roic_symbol, fetched_at, item.asset_id),
                )
            record_fetch(
                conn,
                asset_id=item.asset_id,
                status=status,
                roic_symbol=roic_symbol,
                mapping_status=mapping_status,
                fiscal_year=fiscal_year,
                price_date=price_date,
                error_tag=error_tag,
                error_message=error_message,
                requests_used=requests_used,
                fetched_at=fetched_at,
            )
            conn.commit()

        summary["results"].append(
            {
                "asset_id": item.asset_id,
                "name": item.canonical_name,
                "status": status,
                "roic_symbol": roic_symbol,
                "requests_used": requests_used,
            }
        )

        if index % 10 == 0:
            partial_path = run_dir / "progress.json"
            partial_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if summary["stopped_reason"] is None and summary["processed"] == len(queue):
        summary["stopped_reason"] = "queue_completed"

    summary["finished_at"] = _now()
    summary["elapsed_seconds"] = round(time.monotonic() - started, 1)
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Resumo: {summary_path}")
    print(f"Parcial JSONL: {export_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
