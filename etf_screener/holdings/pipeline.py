from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from etf_screener.catalog.registry import load_sec_issuer_defaults
from etf_screener.config import EXPORTS_DIR, METHODOLOGY_VERSION
from etf_screener.database.db import Database
from etf_screener.export.csv_writer import HOLDING_FIELDS, write_csv
from etf_screener.holdings.asset_registry import link_holdings_to_assets
from etf_screener.holdings.composition import CompositionPayload
from etf_screener.holdings.sec_discovery import find_latest_nport_filing
from etf_screener.holdings.sec_fetch import download_nport_xml
from etf_screener.holdings.sec_nport import normalize_equity_weights, parse_nport_holdings
from etf_screener.holdings.selection import consolidate_equity_holdings, renormalize_consolidated_holdings
from etf_screener.holdings.sources import source_chain_for_ticker
from etf_screener.holdings.vanguard_api import VanguardHoldingsError, fetch_vanguard_composition


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _holding_row(holding) -> dict[str, Any]:
    return {field: getattr(holding, field) for field in HOLDING_FIELDS}


def _snapshot_exists(conn, etf_id: int, accession_number: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM composition_snapshots WHERE etf_id = ? AND accession_number = ?",
        (etf_id, accession_number),
    ).fetchone()
    return row is not None


def _fetch_sec_composition(etf_row: dict[str, Any]) -> CompositionPayload | None:
    issuer_defaults = load_sec_issuer_defaults().get(etf_row.get("issuer") or "", {})
    search_efts = bool(issuer_defaults.get("efts_search"))
    filing = find_latest_nport_filing(
        etf_name=etf_row["name"],
        sec_registrant_cik=etf_row.get("sec_registrant_cik"),
        series_match=etf_row.get("sec_series_match") or etf_row["name"],
        search_efts=search_efts,
    )
    if filing is None:
        return None

    ticker = etf_row["ticker"]
    xml_path = download_nport_xml(filing, ticker)
    holdings = parse_nport_holdings(xml_path, ticker)
    return CompositionPayload(
        source_type="sec_nport",
        accession_number=filing.accession_number,
        source_url=filing.filing_url,
        raw_path=str(xml_path),
        holdings=holdings,
        composition_date=filing.report_date or filing.report_period_end,
        report_period_end=filing.report_period_end,
        filing_date=filing.filing_date,
        series_name=filing.series_name,
    )


def _fetch_composition(
    etf_row: dict[str, Any],
    source: str,
) -> CompositionPayload | None:
    ticker = etf_row["ticker"]
    if source == "vanguard_api":
        return fetch_vanguard_composition(ticker)
    if source == "sec_nport":
        return _fetch_sec_composition(etf_row)
    # Adapters futuros (iShares/SPDR) entram aqui sem mudar o restante do pipeline.
    raise ValueError(f"Fonte de composição não implementada: {source}")


def _persist_composition(
    db: Database,
    etf_row: dict[str, Any],
    payload: CompositionPayload,
    force: bool,
) -> dict[str, Any]:
    ticker = etf_row["ticker"]
    etf_id = int(etf_row["etf_id"])
    holdings = normalize_equity_weights(payload.holdings)
    equities = renormalize_consolidated_holdings(consolidate_equity_holdings(holdings))
    total_weight = sum(item.weight_original for item in holdings)
    equity_weight = sum(item.weight_original for item in holdings if item.included_in_equity_analysis)
    now = _now()

    with db.connect() as conn:
        if not force and _snapshot_exists(conn, etf_id, payload.accession_number):
            return {
                "ticker": ticker,
                "status": "skipped",
                "accession_number": payload.accession_number,
                "source_type": payload.source_type,
                "message": "Snapshot já existente no banco.",
            }

        conn.execute(
            """
            INSERT INTO composition_snapshots (
                etf_id, composition_date, report_period_end, filing_date, accession_number,
                source_url, raw_path, methodology_version, extracted_at, status,
                total_positions, equity_positions, total_weight_pct, equity_weight_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(etf_id, accession_number) DO UPDATE SET
                composition_date = excluded.composition_date,
                report_period_end = excluded.report_period_end,
                filing_date = excluded.filing_date,
                source_url = excluded.source_url,
                raw_path = excluded.raw_path,
                methodology_version = excluded.methodology_version,
                extracted_at = excluded.extracted_at,
                status = excluded.status,
                total_positions = excluded.total_positions,
                equity_positions = excluded.equity_positions,
                total_weight_pct = excluded.total_weight_pct,
                equity_weight_pct = excluded.equity_weight_pct
            """,
            (
                etf_id,
                payload.composition_date,
                payload.report_period_end,
                payload.filing_date,
                payload.accession_number,
                payload.source_url,
                payload.raw_path,
                METHODOLOGY_VERSION,
                now,
                "ok",
                len(holdings),
                len(equities),
                total_weight,
                equity_weight,
            ),
        )
        snapshot_id = int(
            conn.execute(
                "SELECT snapshot_id FROM composition_snapshots WHERE etf_id = ? AND accession_number = ?",
                (etf_id, payload.accession_number),
            ).fetchone()[0]
        )

        if force:
            conn.execute("DELETE FROM holdings WHERE snapshot_id = ?", (snapshot_id,))

        for holding in holdings:
            conn.execute(
                """
                INSERT INTO holdings (
                    snapshot_id, asset_id, position, name_raw, asset_category, asset_type, country,
                    cusip, isin, lei, sec_ticker, other_id, weight_original, weight_normalized,
                    market_value_usd, included_in_equity_analysis, exclusion_reason
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    holding.position,
                    holding.name,
                    holding.asset_category,
                    holding.asset_type,
                    holding.country,
                    holding.cusip,
                    holding.isin,
                    holding.lei,
                    holding.sec_ticker,
                    holding.other_id,
                    holding.weight_original,
                    holding.weight_normalized,
                    holding.market_value_usd,
                    1 if holding.included_in_equity_analysis else 0,
                    holding.exclusion_reason,
                ),
            )

        linked_assets = link_holdings_to_assets(conn, snapshot_id, now)
        conn.commit()

    export_dir = EXPORTS_DIR / "compositions" / ticker.lower()
    write_csv(export_dir / "composicao_etf.csv", [_holding_row(item) for item in holdings], HOLDING_FIELDS)
    write_csv(
        export_dir / "composicao_equities.csv",
        [_holding_row(item) for item in equities],
        HOLDING_FIELDS,
    )

    return {
        "ticker": ticker,
        "status": "ok",
        "accession_number": payload.accession_number,
        "source_type": payload.source_type,
        "filing_date": payload.filing_date,
        "composition_date": payload.composition_date,
        "report_period_end": payload.report_period_end,
        "series_name": payload.series_name,
        "total_positions": len(holdings),
        "equity_positions": len(equities),
        "linked_assets": linked_assets,
        "raw_path": payload.raw_path,
        "export_dir": str(export_dir),
    }


def extract_etf_holdings(
    db: Database,
    etf_row: dict[str, Any],
    force: bool = False,
    source: str | None = None,
) -> dict[str, Any]:
    ticker = etf_row["ticker"]
    chain = [source] if source else source_chain_for_ticker(ticker, etf_row.get("issuer"))
    errors: list[str] = []

    for candidate in chain:
        try:
            payload = _fetch_composition(etf_row, candidate)
        except VanguardHoldingsError as exc:
            errors.append(f"{candidate}: {exc}")
            continue
        except ValueError as exc:
            errors.append(f"{candidate}: {exc}")
            continue

        if payload is None:
            errors.append(f"{candidate}: sem dados")
            continue

        result = _persist_composition(db, etf_row, payload, force=force)
        if errors and result.get("status") == "ok":
            result["source_fallback_notes"] = errors
        return result

    return {
        "ticker": ticker,
        "status": "not_found",
        "message": "Nenhuma fonte de composição retornou dados.",
        "tried_sources": chain,
        "errors": errors,
    }


def run_holdings_extraction(
    db: Database,
    etf_rows: list[dict[str, Any]],
    force: bool = False,
    source: str | None = None,
) -> dict[str, Any]:
    started = _now()
    results: list[dict[str, Any]] = []
    for etf_row in etf_rows:
        try:
            results.append(extract_etf_holdings(db, etf_row, force=force, source=source))
        except Exception as exc:  # noqa: BLE001 - registrar falha por ETF sem abortar lote
            results.append(
                {
                    "ticker": etf_row["ticker"],
                    "status": "error",
                    "message": str(exc),
                }
            )

    finished = _now()
    summary = {
        "started_at": started,
        "finished_at": finished,
        "total": len(results),
        "ok": sum(1 for item in results if item.get("status") == "ok"),
        "skipped": sum(1 for item in results if item.get("status") == "skipped"),
        "failed": sum(1 for item in results if item.get("status") in {"error", "not_found"}),
        "results": results,
    }

    with db.connect() as conn:
        conn.execute(
            """
            INSERT INTO extraction_runs (started_at, finished_at, status, etf_tickers, summary_json, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                started,
                finished,
                "completed",
                json.dumps([row["ticker"] for row in etf_rows]),
                json.dumps(summary, ensure_ascii=False),
                "holdings extraction",
            ),
        )
        conn.commit()

    summary_path = EXPORTS_DIR / "compositions" / f"extraction_summary_{finished.replace(':', '-')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    summary["summary_path"] = str(summary_path)
    return summary
