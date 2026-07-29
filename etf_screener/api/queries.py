"""Consultas SQL reutilizadas pela API."""

from __future__ import annotations

from typing import Any

from etf_screener.database.db import Database

# Cobertura limpa mínima para o ETF aparecer no site (barra amarela ou verde).
# Manter alinhado com frontend/lib/format.ts → MIN_SITE_COVERAGE_PCT.
MIN_SITE_COVERAGE_PCT = 70


def _pct(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value * 100, 2)


def list_etf_summaries(
    db: Database,
    *,
    region: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    sort_by: str = "ticker",
    sort_dir: str = "asc",
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            e.ticker,
            e.name,
            e.region,
            e.country,
            e.issuer,
            e.theme,
            e.priority,
            e.index_name,
            m.equity_positions,
            m.roe_aggregate,
            m.earnings_yield_aggregate,
            m.dividend_yield_aggregate,
            m.gross_shareholder_yield_aggregate,
            m.clean_coverage_pct,
            m.composition_date,
            m.calculated_at,
            CASE WHEN m.metric_id IS NOT NULL THEN 1 ELSE 0 END AS has_metrics
        FROM etfs e
        LEFT JOIN etf_consolidated_metrics m ON m.etf_id = e.etf_id
            AND m.snapshot_id = (
                SELECT MAX(m2.snapshot_id)
                FROM etf_consolidated_metrics m2
                WHERE m2.etf_id = e.etf_id
            )
        WHERE e.status = 'active'
          AND m.clean_coverage_pct >= ?
    """
    params: list[Any] = [MIN_SITE_COVERAGE_PCT]

    if region:
        sql += " AND e.region = ?"
        params.append(region)
    if priority:
        sql += " AND e.priority = ?"
        params.append(priority)
    if search:
        sql += " AND (e.ticker LIKE ? OR e.name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])

    allowed_sort = {
        "ticker": "e.ticker",
        "name": "e.name",
        "region": "e.region",
        "equity_positions": "m.equity_positions",
        "roe": "m.roe_aggregate",
        "earnings_yield": "m.earnings_yield_aggregate",
        "dividend_yield": "m.dividend_yield_aggregate",
        "coverage": "m.clean_coverage_pct",
    }
    sort_col = allowed_sort.get(sort_by, "e.ticker")
    direction = "DESC" if sort_dir.lower() == "desc" else "ASC"
    sql += f" ORDER BY {sort_col} {direction}, e.ticker ASC"

    rows = db.fetchall(sql, params)
    result = []
    for row in rows:
        item = dict(row)
        item["roe_pct"] = _pct(row["roe_aggregate"])
        item["earnings_yield_pct"] = _pct(row["earnings_yield_aggregate"])
        item["dividend_yield_pct"] = _pct(row["dividend_yield_aggregate"])
        item["shareholder_yield_pct"] = _pct(row["gross_shareholder_yield_aggregate"])
        item["has_metrics"] = bool(row["has_metrics"])
        result.append(item)
    return result


def get_etf_detail(db: Database, ticker: str) -> dict[str, Any] | None:
    row = db.fetchone(
        """
        SELECT
            e.ticker,
            e.name,
            e.region,
            e.country,
            e.issuer,
            e.theme,
            e.priority,
            e.index_name,
            m.*
        FROM etfs e
        LEFT JOIN etf_consolidated_metrics m ON m.etf_id = e.etf_id
            AND m.snapshot_id = (
                SELECT MAX(m2.snapshot_id)
                FROM etf_consolidated_metrics m2
                WHERE m2.etf_id = e.etf_id
            )
        WHERE e.ticker = ?
        """,
        (ticker.upper(),),
    )
    if not row:
        return None

    item = dict(row)
    item["roe_pct"] = _pct(item.get("roe_aggregate"))
    item["earnings_yield_pct"] = _pct(item.get("earnings_yield_aggregate"))
    item["dividend_yield_pct"] = _pct(item.get("dividend_yield_aggregate"))
    item["shareholder_yield_pct"] = _pct(item.get("gross_shareholder_yield_aggregate"))
    item["gross_buyback_yield_pct"] = _pct(item.get("gross_buyback_yield_aggregate"))
    item["net_buyback_yield_pct"] = _pct(item.get("net_buyback_yield_aggregate"))
    item["equity_weight_pct"] = item.get("equity_weight_original_pct")
    item["non_equity_weight_pct"] = item.get("non_equity_weight_original_pct")
    item["has_metrics"] = item.get("metric_id") is not None
    return item


def list_etf_holdings(
    db: Database,
    ticker: str,
    *,
    limit: int | None = 10,
) -> list[dict[str, Any]]:
    etf_row = db.fetchone("SELECT etf_id FROM etfs WHERE ticker = ?", (ticker.upper(),))
    if not etf_row:
        return []

    sql = """
        SELECT
            h.position,
            a.canonical_name AS company_name,
            COALESCE(af.sector, a.sector) AS sector,
            h.country,
            h.weight_normalized,
            af.roe,
            af.earnings_yield,
            af.dividend_yield,
            af.gross_shareholder_yield,
            af.quality,
            af.roic_symbol
        FROM holdings h
        JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
        JOIN etfs e ON e.etf_id = cs.etf_id
        LEFT JOIN assets a ON a.asset_id = h.asset_id
        LEFT JOIN asset_fundamentals af ON af.asset_id = a.asset_id
        WHERE e.ticker = ?
          AND h.included_in_equity_analysis = 1
          AND cs.snapshot_id = (
              SELECT MAX(cs2.snapshot_id)
              FROM composition_snapshots cs2
              WHERE cs2.etf_id = e.etf_id
          )
        ORDER BY h.weight_normalized DESC, h.position ASC
    """
    params: list[Any] = [ticker.upper()]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    rows = db.fetchall(sql, params)
    result = []
    for row in rows:
        item = dict(row)
        item["weight_pct"] = round(row["weight_normalized"], 2) if row["weight_normalized"] is not None else None
        item["roe_pct"] = _pct(row["roe"])
        item["earnings_yield_pct"] = _pct(row["earnings_yield"])
        item["dividend_yield_pct"] = _pct(row["dividend_yield"])
        item["shareholder_yield_pct"] = _pct(row["gross_shareholder_yield"])
        result.append(item)
    return result


def list_assets(
    db: Database,
    *,
    country: str | None = None,
    sector: str | None = None,
    quality: str | None = None,
    search: str | None = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            a.asset_id,
            a.canonical_name AS company_name,
            a.country,
            COALESCE(af.sector, a.sector) AS sector,
            af.roe,
            af.earnings_yield,
            af.dividend_yield,
            af.gross_shareholder_yield,
            af.quality,
            af.roic_symbol,
            (
                SELECT COUNT(DISTINCT cs.etf_id)
                FROM holdings h2
                JOIN composition_snapshots cs ON cs.snapshot_id = h2.snapshot_id
                WHERE h2.asset_id = a.asset_id
                  AND h2.included_in_equity_analysis = 1
            ) AS etf_count
        FROM assets a
        JOIN asset_fundamentals af ON af.asset_id = a.asset_id
        WHERE 1 = 1
    """
    params: list[Any] = []

    if country:
        sql += " AND a.country = ?"
        params.append(country)
    if sector:
        sql += " AND COALESCE(af.sector, a.sector) = ?"
        params.append(sector)
    if quality:
        sql += " AND af.quality = ?"
        params.append(quality)
    if search:
        sql += " AND a.canonical_name LIKE ?"
        params.append(f"%{search}%")

    allowed_sort = {
        "name": "a.canonical_name",
        "country": "a.country",
        "sector": "sector",
        "roe": "af.roe",
        "earnings_yield": "af.earnings_yield",
        "dividend_yield": "af.dividend_yield",
        "etf_count": "etf_count",
    }
    sort_col = allowed_sort.get(sort_by, "a.canonical_name")
    direction = "DESC" if sort_dir.lower() == "desc" else "ASC"
    sql += f" ORDER BY {sort_col} {direction}, a.canonical_name ASC"

    rows = db.fetchall(sql, params)
    result = []
    for row in rows:
        item = dict(row)
        item["roe_pct"] = _pct(row["roe"])
        item["earnings_yield_pct"] = _pct(row["earnings_yield"])
        item["dividend_yield_pct"] = _pct(row["dividend_yield"])
        item["shareholder_yield_pct"] = _pct(row["gross_shareholder_yield"])
        result.append(item)
    return result


def list_regions(db: Database) -> list[str]:
    rows = db.fetchall(
        "SELECT DISTINCT region FROM etfs WHERE region IS NOT NULL AND status = 'active' ORDER BY region"
    )
    return [row["region"] for row in rows]


def list_sectors(db: Database) -> list[str]:
    rows = db.fetchall(
        """
        SELECT DISTINCT COALESCE(af.sector, a.sector) AS sector
        FROM assets a
        JOIN asset_fundamentals af ON af.asset_id = a.asset_id
        WHERE COALESCE(af.sector, a.sector) IS NOT NULL
        ORDER BY sector
        """
    )
    return [row["sector"] for row in rows]
