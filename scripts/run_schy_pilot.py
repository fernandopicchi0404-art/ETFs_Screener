#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etf_screener.config import OUTPUT_DIR, RAW_DIR
from etf_screener.export.csv_writer import (
    COMPANY_FIELDS,
    EXCEPTION_FIELDS,
    HOLDING_FIELDS,
    VALIDATION_FIELDS,
    write_csv,
)
from etf_screener.holdings.sec_nport import normalize_equity_weights, parse_nport_holdings
from etf_screener.holdings.symbol_map import load_symbol_map, save_symbol_map
from etf_screener.metrics.fundamentals import aggregate_etf, extract_fundamentals, validate_company
from etf_screener.models import ExceptionRecord
from etf_screener.roic.client import RoicClient
from etf_screener.roic.resolver import resolve_roic_symbol


ETF = "SCHY"
NPORT_URL = "https://www.sec.gov/Archives/edgar/data/1454889/000141036826039962/primary_doc.xml"
NPORT_PATH = RAW_DIR / "schy_nport_2026-02-28.xml"


def load_api_key() -> str:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("ROIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    key = os.getenv("ROIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ROIC_API_KEY não encontrada no .env.")
    return key


def ensure_nport_file() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not NPORT_PATH.exists():
        subprocess.run(
            [
                "curl",
                "-sS",
                "-A",
                "ETFs_Screener research contact@example.com",
                NPORT_URL,
                "-o",
                str(NPORT_PATH),
            ],
            check=True,
        )
    return NPORT_PATH


def company_to_row(company) -> dict:
    row = {field: getattr(company, field) for field in COMPANY_FIELDS}
    row["tags"] = ";".join(company.tags)
    return row


def holding_to_row(holding) -> dict:
    return {field: getattr(holding, field) for field in HOLDING_FIELDS}


def exception_to_row(record: ExceptionRecord) -> dict:
    return {
        "etf": record.etf,
        "symbol": record.symbol,
        "date": record.date,
        "severity": record.severity,
        "tag": record.tag,
        "stage": record.stage,
        "message": record.message,
        "metric_impact": record.metric_impact,
        "recommended_action": record.recommended_action,
        "status": record.status,
        "resolved_at": record.resolved_at,
    }


def validation_to_row(result) -> dict:
    return {
        "etf": result.etf,
        "symbol": result.symbol,
        "period": result.period,
        "test_name": result.test_name,
        "calculated": result.calculated,
        "reference": result.reference,
        "abs_diff": result.abs_diff,
        "pct_diff": result.pct_diff,
        "tolerance": result.tolerance,
        "result": result.result,
        "source": result.source,
        "source_url": result.source_url,
        "comment": result.comment,
    }


def run(limit: int | None = None) -> None:
    api_key = load_api_key()
    client = RoicClient(api_key)
    nport_path = ensure_nport_file()

    holdings = normalize_equity_weights(parse_nport_holdings(nport_path, ETF))
    equities = [holding for holding in holdings if holding.included_in_equity_analysis]
    if limit is not None:
        equities = equities[:limit]

    symbol_map = load_symbol_map(ETF)
    companies = []
    validations = []
    exceptions: list[ExceptionRecord] = []
    run_date = datetime.now(timezone.utc).date().isoformat()

    for index, holding in enumerate(equities, start=1):
        print(f"[{index}/{len(equities)}] Processando {holding.name}...", flush=True)
        mapped = symbol_map.get(holding.name, {})
        roic_symbol, mapping_status, _ = resolve_roic_symbol(
            client,
            company_name=holding.name,
            country=holding.country,
            known_symbol=mapped.get("symbol"),
            known_roic_symbol=mapped.get("roic_symbol"),
        )

        if not roic_symbol:
            exceptions.append(
                ExceptionRecord(
                    etf=ETF,
                    symbol=holding.name,
                    date=run_date,
                    severity="BLOCKER",
                    tag="MAPPING_NOT_FOUND",
                    stage="resolver",
                    message=f"Não foi possível mapear {holding.name} para um identificador ROIC.",
                    metric_impact="todas",
                    recommended_action="Revisar mapeamento manual em data/mappings/schy_symbols.json",
                    status="pending",
                )
            )
            continue

        if mapping_status == "ambiguous":
            exceptions.append(
                ExceptionRecord(
                    etf=ETF,
                    symbol=roic_symbol,
                    date=run_date,
                    severity="WARNING",
                    tag="MAPPING_AMBIGUOUS",
                    stage="resolver",
                    message=f"Mapeamento ambíguo para {holding.name} -> {roic_symbol}.",
                    metric_impact="todas",
                    recommended_action="Validar manualmente o identificador ROIC.",
                    status="pending",
                )
            )

        symbol_map[holding.name] = {
            "symbol": mapped.get("symbol", ""),
            "cusip": holding.cusip or mapped.get("cusip", ""),
            "country": holding.country,
            "roic_symbol": roic_symbol,
        }
        save_symbol_map(ETF, symbol_map)

        try:
            income = client.get(
                f"/fundamental/income-statement/{roic_symbol}",
                {"period_type": "annual", "limit": 2, "order": "desc"},
            )
            balance = client.get(
                f"/fundamental/balance-sheet/{roic_symbol}",
                {"period_type": "annual", "limit": 2, "order": "desc"},
            )
            cashflow = client.get(
                f"/fundamental/cash-flow/{roic_symbol}",
                {"period_type": "annual", "limit": 1, "order": "desc"},
            )
            price = client.get(f"/stock-prices/latest/{roic_symbol}")
        except Exception as exc:  # noqa: BLE001
            exceptions.append(
                ExceptionRecord(
                    etf=ETF,
                    symbol=roic_symbol,
                    date=run_date,
                    severity="BLOCKER",
                    tag="API_TEMPORARY_FAILURE",
                    stage="fetch",
                    message=str(exc),
                    metric_impact="todas",
                    recommended_action="Reexecutar o piloto; o cache evitará chamadas repetidas.",
                    status="pending",
                )
            )
            continue

        company = extract_fundamentals(
            etf=ETF,
            roic_symbol=roic_symbol,
            company_name=holding.name,
            country=holding.country,
            mapping_status=mapping_status,
            income_payload=income,
            balance_payload=balance,
            cashflow_payload=cashflow,
            price_payload=price,
        )
        companies.append(company)
        validations.extend(validate_company(company))

    output_dir = OUTPUT_DIR / ETF.lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "composicao_etf.csv", [holding_to_row(h) for h in holdings], HOLDING_FIELDS)
    write_csv(output_dir / "ativos.csv", [company_to_row(c) for c in companies], COMPANY_FIELDS)
    write_csv(output_dir / "validacoes.csv", [validation_to_row(v) for v in validations], VALIDATION_FIELDS)
    write_csv(output_dir / "excecoes.csv", [exception_to_row(e) for e in exceptions], EXCEPTION_FIELDS)
    write_csv(output_dir / "ajustes.csv", [], [
        "etf",
        "symbol",
        "period",
        "field_adjusted",
        "original_value",
        "adjustment_value",
        "final_value",
        "currency",
        "source",
        "source_url",
        "justification",
        "validation_date",
        "review_status",
    ])

    aggregate = aggregate_etf(companies, holdings)
    aggregate["composition_date"] = "2026-02-28"
    aggregate["run_date"] = run_date
    write_csv(output_dir / "etf_consolidado.csv", [aggregate], list(aggregate.keys()))

    summary = {
        "etf": ETF,
        "holdings_total": len(holdings),
        "equities_processed": len(equities),
        "companies_with_data": len(companies),
        "exceptions": len(exceptions),
        "output_dir": str(output_dir),
    }
    (output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa o piloto SCHY.")
    parser.add_argument("--limit", type=int, default=None, help="Limita o número de ações processadas.")
    args = parser.parse_args()
    run(limit=args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
