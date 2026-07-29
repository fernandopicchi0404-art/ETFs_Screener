from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from etf_screener.models import CompanyFundamentals
from etf_screener.metrics.fundamentals import extract_fundamentals
from etf_screener.holdings.coverage import asset_ids_for_weight_coverage
from etf_screener.roic.client import RoicClient
from etf_screener.roic.symbols import resolve_fetch_symbol, roic_symbol_path
from etf_screener.roic.identity_resolver import APPROVED_STATUSES


@dataclass(frozen=True)
class AssetWorkItem:
    asset_id: int
    canonical_name: str
    country: str
    roic_symbol: str
    mapping_status: str
    max_weight: float


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_verified_assets(
    db: Database,
    priority: str = "P1",
    tickers: list[str] | None = None,
    coverage_target: float | None = None,
) -> list[AssetWorkItem]:
    placeholders = ",".join("?" for _ in APPROVED_STATUSES)
    sql = f"""
        SELECT
            a.asset_id,
            a.canonical_name,
            a.country,
            ai.roic_symbol,
            ai.mapping_status,
            MAX(h.weight_normalized) AS max_weight
        FROM asset_identities ai
        JOIN assets a ON a.asset_id = ai.asset_id
        JOIN holdings h ON h.asset_id = a.asset_id
        JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
        JOIN etfs e ON e.etf_id = cs.etf_id
        WHERE e.priority = ?
          AND h.included_in_equity_analysis = 1
          AND ai.mapping_status IN ({placeholders})
          AND ai.roic_symbol IS NOT NULL
          AND cs.snapshot_id = (
              SELECT MAX(cs2.snapshot_id)
              FROM composition_snapshots cs2
              WHERE cs2.etf_id = e.etf_id
          )
    """
    params: list[Any] = [priority, *APPROVED_STATUSES]
    if tickers:
        ticker_ph = ",".join("?" for _ in tickers)
        sql += f" AND e.ticker IN ({ticker_ph})"
        params.extend(t.upper() for t in tickers)
    sql += """
        GROUP BY a.asset_id
        ORDER BY max_weight DESC, a.canonical_name
    """
    rows = db.fetchall(sql, tuple(params))
    items = [
        AssetWorkItem(
            asset_id=int(row["asset_id"]),
            canonical_name=row["canonical_name"],
            country=row["country"] or "",
            roic_symbol=row["roic_symbol"],
            mapping_status=row["mapping_status"],
            max_weight=float(row["max_weight"] or 0),
        )
        for row in rows
    ]
    if coverage_target is None:
        return items
    allowed = asset_ids_for_weight_coverage(
        db,
        priority=priority,
        tickers=tickers,
        coverage_target=coverage_target,
    )
    return [item for item in items if item.asset_id in allowed]


def pending_verified_fetches(
    db: Database,
    priority: str = "P1",
    tickers: list[str] | None = None,
    coverage_target: float | None = None,
) -> list[AssetWorkItem]:
    items = list_verified_assets(
        db, priority=priority, tickers=tickers, coverage_target=coverage_target
    )
    done = {
        int(row["asset_id"])
        for row in db.fetchall(
            "SELECT asset_id FROM asset_fundamental_fetches WHERE status = 'ok'"
        )
    }
    return [item for item in items if item.asset_id not in done]


def record_fetch(
    conn,
    asset_id: int,
    status: str,
    roic_symbol: str | None,
    mapping_status: str | None,
    fiscal_year: int | None,
    price_date: str | None,
    error_tag: str | None,
    error_message: str | None,
    requests_used: int,
    fetched_at: str,
) -> None:
    conn.execute(
        """
        INSERT INTO asset_fundamental_fetches (
            asset_id, roic_symbol, mapping_status, status, fiscal_year, price_date,
            fetched_at, error_tag, error_message, requests_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            roic_symbol = excluded.roic_symbol,
            mapping_status = excluded.mapping_status,
            status = excluded.status,
            fiscal_year = excluded.fiscal_year,
            price_date = excluded.price_date,
            fetched_at = excluded.fetched_at,
            error_tag = excluded.error_tag,
            error_message = excluded.error_message,
            requests_used = excluded.requests_used
        """,
        (
            asset_id,
            roic_symbol,
            mapping_status,
            status,
            fiscal_year,
            price_date,
            fetched_at,
            error_tag,
            error_message,
            requests_used,
        ),
    )


def pending_fetch_retries(db: Database, priority: str = "P1") -> list[AssetWorkItem]:
    rows = db.fetchall(
        """
        SELECT
            a.asset_id,
            a.canonical_name,
            a.country,
            ai.roic_symbol,
            ai.mapping_status,
            MAX(h.weight_normalized) AS max_weight
        FROM asset_fundamental_fetches aff
        JOIN assets a ON a.asset_id = aff.asset_id
        JOIN asset_identities ai ON ai.asset_id = a.asset_id
        JOIN holdings h ON h.asset_id = a.asset_id
        JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
        JOIN etfs e ON e.etf_id = cs.etf_id
        WHERE aff.status = 'fetch_error'
          AND e.priority = ?
          AND h.included_in_equity_analysis = 1
          AND ai.mapping_status IN (
              'verified_isin', 'verified_cusip', 'verified_symbol',
              'verified_name_match', 'manual_approved'
          )
        GROUP BY a.asset_id
        ORDER BY max_weight DESC, a.canonical_name
        """,
        (priority,),
    )
    return [
        AssetWorkItem(
            asset_id=int(row["asset_id"]),
            canonical_name=row["canonical_name"],
            country=row["country"] or "",
            roic_symbol=row["roic_symbol"],
            mapping_status=row["mapping_status"],
            max_weight=float(row["max_weight"] or 0),
        )
        for row in rows
    ]


def fetch_asset_fundamentals(
    client: RoicClient,
    item: AssetWorkItem,
) -> tuple[dict[str, Any] | None, str, str | None, str | None, int, str | None, CompanyFundamentals | None]:
    """Busca fundamentos apenas para identidade já aprovada."""
    requests_used = 0
    roic_symbol = resolve_fetch_symbol(item.roic_symbol)

    try:
        income = client.get(
            roic_symbol_path("/fundamental/income-statement", roic_symbol),
            {"period_type": "annual", "limit": 2, "order": "desc"},
        )
        requests_used += 1
        balance = client.get(
            roic_symbol_path("/fundamental/balance-sheet", roic_symbol),
            {"period_type": "annual", "limit": 2, "order": "desc"},
        )
        requests_used += 1
        cashflow = client.get(
            roic_symbol_path("/fundamental/cash-flow", roic_symbol),
            {"period_type": "annual", "limit": 1, "order": "desc"},
        )
        requests_used += 1
        price: dict[str, Any] = {}
        try:
            price = client.get(roic_symbol_path("/stock-prices/latest", roic_symbol))
            requests_used += 1
        except Exception:  # noqa: BLE001 — preço ausente não invalida ROE
            pass
    except Exception as exc:  # noqa: BLE001
        return None, "fetch_error", roic_symbol, item.mapping_status, requests_used, str(exc), None

    if not (income.get("data") or balance.get("data")):
        return (
            None,
            "fetch_error",
            roic_symbol,
            item.mapping_status,
            requests_used,
            "Demonstrativos financeiros vazios na ROIC.",
            None,
        )

    company = extract_fundamentals(
        etf="P1_BATCH",
        roic_symbol=roic_symbol,
        company_name=item.canonical_name,
        country=item.country,
        mapping_status=item.mapping_status,
        income_payload=income,
        balance_payload=balance,
        cashflow_payload=cashflow,
        price_payload=price,
    )

    payload = {
        "asset_id": item.asset_id,
        "canonical_name": item.canonical_name,
        "country": item.country,
        "roic_symbol": roic_symbol,
        "mapping_status": item.mapping_status,
        "fiscal_year": company.fiscal_year,
        "price_date": company.price_date,
        "price": company.price,
        "roe": company.roe,
        "earnings_yield": company.earnings_yield,
        "dividend_yield": company.dividend_yield,
        "quality": company.quality,
        "tags": company.tags,
    }
    return payload, "ok", roic_symbol, item.mapping_status, requests_used, None, company
