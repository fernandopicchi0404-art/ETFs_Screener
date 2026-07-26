#!/usr/bin/env python3
"""Teste pontual: extrai métricas da Lojas Renner (B3:LREN3) via ROIC.ai."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://api.roic.ai/v3.0.0"
TICKER = "B3:LREN3"
# Plano gratuito: 5 requisições/minuto. Intervalo seguro entre chamadas.
REQUEST_INTERVAL_SECONDS = 13


def load_api_key() -> str:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ROIC_API_KEY="):
                return line.split("=", 1)[1].strip()

    key = os.getenv("ROIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ROIC_API_KEY não encontrada. Configure no arquivo .env.")
    return key


def api_get(path: str, api_key: str) -> dict:
    url = f"{BASE_URL}{path}"
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} em {path}: {body}") from exc


def first_period(payload: dict) -> dict:
    data = payload.get("data")
    if not data:
        raise RuntimeError(f"Resposta sem dados: {json.dumps(payload, ensure_ascii=False)}")
    return data[0]


def format_millions(value: float | int | None, currency: str) -> str:
    if value is None:
        return "n/d"
    return f"{currency} {value:,.0f} (milhões, conforme API)"


def main() -> int:
    api_key = load_api_key()
    started = time.time()

    steps = [
        ("Preço mais recente", f"/stock-prices/latest/{TICKER}"),
        ("DRE anual", f"/fundamental/income-statement/{TICKER}?period_type=annual&limit=1"),
        ("Balanço anual", f"/fundamental/balance-sheet/{TICKER}?period_type=annual&limit=1"),
        ("Dados por ação", f"/fundamental/per-share/{TICKER}?period_type=annual&limit=1"),
    ]

    results: dict[str, dict] = {}
    for index, (label, path) in enumerate(steps):
        if index > 0:
            time.sleep(REQUEST_INTERVAL_SECONDS)
        print(f"[{index + 1}/{len(steps)}] Consultando {label}...")
        results[label] = api_get(path, api_key)

    price = results["Preço mais recente"]
    income = first_period(results["DRE anual"])
    balance = first_period(results["Balanço anual"])
    per_share = first_period(results["Dados por ação"])

    elapsed = time.time() - started

    print("\n=== Lojas Renner (B3:LREN3) ===\n")
    print(f"Preço por ação: {price['currency']} {price['close']:.2f} (data: {price['date']})")
    print(
        "Ações diluídas: "
        f"{income.get('is_sh_for_diluted_eps', per_share.get('is_sh_for_diluted_eps')):,.0f} "
        f"(exercício {income['fiscal_year']})"
    )
    print(
        "Lucro líquido (anual mais recente, não TTM): "
        f"{format_millions(income.get('is_net_income'), income['currency'])} "
        f"(exercício {income['fiscal_year']}, encerrado em {income['period_end_date']})"
    )
    print(
        "Patrimônio líquido (total): "
        f"{format_millions(balance.get('bs_total_equity'), balance['currency'])} "
        f"(exercício {balance['fiscal_year']}, encerrado em {balance['period_end_date']})"
    )
    print(
        "Valor patrimonial por ação: "
        f"{per_share['currency']} {per_share.get('book_val_per_sh', 0):.2f} "
        f"(exercício {per_share['fiscal_year']})"
    )
    print(f"\nTempo total: {elapsed:.0f}s ({len(steps)} requisições)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - script de teste com erro explícito
        print(f"Erro: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
