#!/usr/bin/env python3
"""Testa se a ROIC aceita a taxa configurada (ex.: 300 req/min)."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.roic.auth import load_roic_api_key
from etf_screener.roic.client import RoicClient
from etf_screener.roic.settings import load_requests_per_minute, request_interval_seconds


def main() -> int:
    parser = argparse.ArgumentParser(description="Testa taxa de requisições ROIC.")
    parser.add_argument(
        "--requests",
        type=int,
        default=60,
        help="Quantidade de chamadas leves (padrão: 60).",
    )
    args = parser.parse_args()

    rpm = load_requests_per_minute()
    interval = request_interval_seconds(rpm)
    client = RoicClient(load_roic_api_key(), requests_per_minute=rpm)

    print(
        f"Plano configurado: {rpm} req/min "
        f"(intervalo {interval:.3f}s entre chamadas)",
        flush=True,
    )
    print(f"Enviando {args.requests} buscas leves...", flush=True)

    started = time.monotonic()
    ok = 0
    rate_limited = 0
    errors: list[str] = []

    for index in range(1, args.requests + 1):
        try:
            client.get(
                "/tickers/search",
                {"query": "Apple", "limit": 1},
                use_cache=False,
            )
            ok += 1
        except RuntimeError as exc:
            message = str(exc)
            if "HTTP 429" in message:
                rate_limited += 1
            else:
                errors.append(message)
        if index % 10 == 0:
            elapsed = time.monotonic() - started
            current_rpm = round(index / elapsed * 60, 1) if elapsed > 0 else 0
            print(f"  {index}/{args.requests} — ~{current_rpm} req/min até agora", flush=True)

    elapsed = time.monotonic() - started
    achieved_rpm = round(ok / elapsed * 60, 1) if elapsed > 0 else 0
    result = {
        "configured_rpm": rpm,
        "interval_seconds": round(interval, 4),
        "requests_attempted": args.requests,
        "requests_ok": ok,
        "rate_limited_429": rate_limited,
        "other_errors": len(errors),
        "elapsed_seconds": round(elapsed, 2),
        "achieved_rpm": achieved_rpm,
        "passed": rate_limited == 0 and ok >= args.requests * 0.95,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if errors:
        print("Primeiros erros:", errors[:3], file=sys.stderr)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
