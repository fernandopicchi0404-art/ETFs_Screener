"""Persistência de métricas calculadas no SQLite."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etf_screener.config import METHODOLOGY_VERSION
from etf_screener.database.db import Database
from etf_screener.models import CompanyFundamentals, Holding


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_tags(value: str | None) -> list[str]:
    if not value:
        return []
    return [tag for tag in value.split(";") if tag]


def _format_tags(tags: list[str]) -> str:
    return ";".join(tags)


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def upsert_asset_fundamentals(
    conn,
    asset_id: int,
    company: CompanyFundamentals,
    *,
    sector: str | None = None,
    industry: str | None = None,
    calculated_at: str | None = None,
) -> None:
    """Grava ou atualiza métricas fundamentais de um ativo."""
    ts = calculated_at or _now()
    conn.execute(
        """
        INSERT INTO asset_fundamentals (
            asset_id, roic_symbol, exchange, sector, industry, mapping_status,
            fundamental_currency, price_currency, fiscal_year, fiscal_year_end,
            price_date, price, earnings_for_common, diluted_shares, diluted_eps,
            common_equity_average, roe, roe_method, earnings_yield, dividend_yield,
            gross_buyback_yield, net_buyback_yield, gross_shareholder_yield,
            net_shareholder_yield, quality, tags, notes, methodology_version, calculated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            roic_symbol = excluded.roic_symbol,
            exchange = excluded.exchange,
            sector = COALESCE(excluded.sector, asset_fundamentals.sector),
            industry = COALESCE(excluded.industry, asset_fundamentals.industry),
            mapping_status = excluded.mapping_status,
            fundamental_currency = excluded.fundamental_currency,
            price_currency = excluded.price_currency,
            fiscal_year = excluded.fiscal_year,
            fiscal_year_end = excluded.fiscal_year_end,
            price_date = excluded.price_date,
            price = excluded.price,
            earnings_for_common = excluded.earnings_for_common,
            diluted_shares = excluded.diluted_shares,
            diluted_eps = excluded.diluted_eps,
            common_equity_average = excluded.common_equity_average,
            roe = excluded.roe,
            roe_method = excluded.roe_method,
            earnings_yield = excluded.earnings_yield,
            dividend_yield = excluded.dividend_yield,
            gross_buyback_yield = excluded.gross_buyback_yield,
            net_buyback_yield = excluded.net_buyback_yield,
            gross_shareholder_yield = excluded.gross_shareholder_yield,
            net_shareholder_yield = excluded.net_shareholder_yield,
            quality = excluded.quality,
            tags = excluded.tags,
            notes = excluded.notes,
            methodology_version = excluded.methodology_version,
            calculated_at = excluded.calculated_at
        """,
        (
            asset_id,
            company.roic_symbol,
            company.exchange or None,
            sector,
            industry,
            company.mapping_status,
            company.fundamental_currency or None,
            company.price_currency or None,
            company.fiscal_year,
            company.fiscal_year_end,
            company.price_date,
            company.price,
            company.earnings_for_common,
            company.diluted_shares,
            company.diluted_eps,
            company.common_equity_average,
            company.roe,
            company.roe_method or None,
            company.earnings_yield,
            company.dividend_yield,
            company.gross_buyback_yield,
            company.net_buyback_yield,
            company.gross_shareholder_yield,
            company.net_shareholder_yield,
            company.quality,
            _format_tags(company.tags),
            company.notes or None,
            METHODOLOGY_VERSION,
            ts,
        ),
    )
    conn.execute(
        """
        UPDATE assets
        SET roic_symbol = COALESCE(?, roic_symbol),
            sector = COALESCE(?, sector),
            exchange = COALESCE(?, exchange),
            updated_at = ?
        WHERE asset_id = ?
        """,
        (company.roic_symbol, sector, company.exchange or None, ts, asset_id),
    )


def row_to_company(
    row: dict[str, Any],
    *,
    etf: str,
    company_name: str,
    country: str,
    weight_normalized: float | None = None,
) -> CompanyFundamentals:
    """Converte linha do banco em CompanyFundamentals para agregação."""
    return CompanyFundamentals(
        etf=etf,
        roic_symbol=row["roic_symbol"] or "",
        company_name=company_name,
        exchange=row["exchange"] or "",
        country=country,
        mapping_status=row["mapping_status"] or "",
        fundamental_currency=row["fundamental_currency"] or "",
        price_currency=row["price_currency"] or "",
        weight_normalized=weight_normalized,
        fiscal_year=row["fiscal_year"],
        fiscal_year_end=row["fiscal_year_end"],
        price_date=row["price_date"],
        price=row["price"],
        earnings_for_common=row["earnings_for_common"],
        diluted_shares=row["diluted_shares"],
        diluted_eps=row["diluted_eps"],
        common_equity_average=row["common_equity_average"],
        roe=row["roe"],
        roe_method=row["roe_method"] or "",
        earnings_yield=row["earnings_yield"],
        dividend_yield=row["dividend_yield"],
        gross_buyback_yield=row["gross_buyback_yield"],
        net_buyback_yield=row["net_buyback_yield"],
        gross_shareholder_yield=row["gross_shareholder_yield"],
        net_shareholder_yield=row["net_shareholder_yield"],
        quality=row["quality"] or "OK",
        tags=_parse_tags(row.get("tags")),
        notes=row.get("notes") or "",
    )


def company_from_csv_row(row: dict[str, str], etf: str) -> CompanyFundamentals:
    """Converte linha do CSV do piloto em CompanyFundamentals."""
    tags = _parse_tags(row.get("tags"))
    return CompanyFundamentals(
        etf=etf,
        roic_symbol=row.get("roic_symbol") or "",
        company_name=row.get("company_name") or "",
        exchange=row.get("exchange") or "",
        country=row.get("country") or "",
        mapping_status=row.get("mapping_status") or "",
        fundamental_currency=row.get("fundamental_currency") or "",
        price_currency=row.get("price_currency") or "",
        weight_normalized=_float_or_none(row.get("weight_normalized")),
        fiscal_year=_int_or_none(row.get("fiscal_year")),
        fiscal_year_end=row.get("fiscal_year_end") or None,
        price_date=row.get("price_date") or None,
        price=_float_or_none(row.get("price")),
        net_income=_float_or_none(row.get("net_income")),
        minority_interest=_float_or_none(row.get("minority_interest")),
        preferred_dividends=_float_or_none(row.get("preferred_dividends")),
        earnings_for_common=_float_or_none(row.get("earnings_for_common")),
        diluted_shares=_float_or_none(row.get("diluted_shares")),
        diluted_eps=_float_or_none(row.get("diluted_eps")),
        equity_total=_float_or_none(row.get("equity_total")),
        minority_equity=_float_or_none(row.get("minority_equity")),
        preferred_equity=_float_or_none(row.get("preferred_equity")),
        common_equity=_float_or_none(row.get("common_equity")),
        common_equity_prior=_float_or_none(row.get("common_equity_prior")),
        common_equity_average=_float_or_none(row.get("common_equity_average")),
        dividends_paid=_float_or_none(row.get("dividends_paid")),
        buybacks_gross=_float_or_none(row.get("buybacks_gross")),
        share_issuance=_float_or_none(row.get("share_issuance")),
        buybacks_net=_float_or_none(row.get("buybacks_net")),
        dividends_final=_float_or_none(row.get("dividends_final")),
        buybacks_final=_float_or_none(row.get("buybacks_final")),
        dividend_per_share=_float_or_none(row.get("dividend_per_share")),
        buyback_gross_per_share=_float_or_none(row.get("buyback_gross_per_share")),
        buyback_net_per_share=_float_or_none(row.get("buyback_net_per_share")),
        roe=_float_or_none(row.get("roe")),
        roe_method=row.get("roe_method") or "",
        earnings_yield=_float_or_none(row.get("earnings_yield")),
        dividend_yield=_float_or_none(row.get("dividend_yield")),
        gross_buyback_yield=_float_or_none(row.get("gross_buyback_yield")),
        net_buyback_yield=_float_or_none(row.get("net_buyback_yield")),
        gross_shareholder_yield=_float_or_none(row.get("gross_shareholder_yield")),
        net_shareholder_yield=_float_or_none(row.get("net_shareholder_yield")),
        quality=row.get("quality") or "OK",
        tags=tags,
        notes=row.get("notes") or "",
    )


def holding_from_csv_row(row: dict[str, str], etf: str) -> Holding:
    """Converte linha de composição CSV em Holding."""
    included = str(row.get("included_in_equity_analysis", "")).lower() in {"true", "1", "yes"}
    return Holding(
        etf=etf,
        position=int(row.get("position") or 0),
        name=row.get("name") or "",
        asset_category=row.get("asset_category") or "",
        asset_type=row.get("asset_type") or "",
        country=row.get("country") or "",
        weight_original=_float_or_none(row.get("weight_original")) or 0.0,
        weight_normalized=_float_or_none(row.get("weight_normalized")),
        market_value_usd=_float_or_none(row.get("market_value_usd")),
        cusip=row.get("cusip") or None,
        symbol=row.get("symbol") or None,
        isin=row.get("isin") or None,
        included_in_equity_analysis=included,
        exclusion_reason=row.get("exclusion_reason") or None,
    )


def upsert_etf_consolidated_metrics(
    conn,
    etf_id: int,
    snapshot_id: int,
    aggregate: dict[str, Any],
    *,
    composition_date: str | None = None,
    calculated_at: str | None = None,
) -> None:
    """Grava métricas consolidadas de um ETF."""
    ts = calculated_at or _now()

    def _bool_int(value: Any) -> int:
        return 1 if bool(value) else 0

    conn.execute(
        """
        INSERT INTO etf_consolidated_metrics (
            etf_id, snapshot_id, equity_positions, equity_weight_original_pct,
            non_equity_weight_original_pct, target_clean_coverage_pct, clean_coverage_pct,
            target_clean_coverage_met, roe_aggregate, earnings_yield_aggregate,
            dividend_yield_aggregate, gross_buyback_yield_aggregate,
            net_buyback_yield_aggregate, gross_shareholder_yield_aggregate,
            net_shareholder_yield_aggregate, earnings_yield_mean_covered,
            dividend_yield_mean_covered, gross_buyback_yield_mean_covered,
            gross_shareholder_yield_mean_covered, coverage_roe_pct,
            coverage_earnings_yield_pct, coverage_dividend_yield_pct,
            coverage_buyback_yield_pct, coverage_shareholder_yield_pct,
            composition_date, calculated_at, methodology_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(etf_id, snapshot_id) DO UPDATE SET
            equity_positions = excluded.equity_positions,
            equity_weight_original_pct = excluded.equity_weight_original_pct,
            non_equity_weight_original_pct = excluded.non_equity_weight_original_pct,
            target_clean_coverage_pct = excluded.target_clean_coverage_pct,
            clean_coverage_pct = excluded.clean_coverage_pct,
            target_clean_coverage_met = excluded.target_clean_coverage_met,
            roe_aggregate = excluded.roe_aggregate,
            earnings_yield_aggregate = excluded.earnings_yield_aggregate,
            dividend_yield_aggregate = excluded.dividend_yield_aggregate,
            gross_buyback_yield_aggregate = excluded.gross_buyback_yield_aggregate,
            net_buyback_yield_aggregate = excluded.net_buyback_yield_aggregate,
            gross_shareholder_yield_aggregate = excluded.gross_shareholder_yield_aggregate,
            net_shareholder_yield_aggregate = excluded.net_shareholder_yield_aggregate,
            earnings_yield_mean_covered = excluded.earnings_yield_mean_covered,
            dividend_yield_mean_covered = excluded.dividend_yield_mean_covered,
            gross_buyback_yield_mean_covered = excluded.gross_buyback_yield_mean_covered,
            gross_shareholder_yield_mean_covered = excluded.gross_shareholder_yield_mean_covered,
            coverage_roe_pct = excluded.coverage_roe_pct,
            coverage_earnings_yield_pct = excluded.coverage_earnings_yield_pct,
            coverage_dividend_yield_pct = excluded.coverage_dividend_yield_pct,
            coverage_buyback_yield_pct = excluded.coverage_buyback_yield_pct,
            coverage_shareholder_yield_pct = excluded.coverage_shareholder_yield_pct,
            composition_date = excluded.composition_date,
            calculated_at = excluded.calculated_at,
            methodology_version = excluded.methodology_version
        """,
        (
            etf_id,
            snapshot_id,
            int(aggregate.get("equity_positions") or 0),
            aggregate.get("equity_weight_original_pct"),
            aggregate.get("non_equity_weight_original_pct"),
            aggregate.get("target_clean_coverage_pct"),
            aggregate.get("clean_coverage_pct"),
            _bool_int(aggregate.get("target_clean_coverage_met")),
            aggregate.get("roe_aggregate"),
            aggregate.get("earnings_yield_aggregate"),
            aggregate.get("dividend_yield_aggregate"),
            aggregate.get("gross_buyback_yield_aggregate"),
            aggregate.get("net_buyback_yield_aggregate"),
            aggregate.get("gross_shareholder_yield_aggregate"),
            aggregate.get("net_shareholder_yield_aggregate"),
            aggregate.get("earnings_yield_mean_covered"),
            aggregate.get("dividend_yield_mean_covered"),
            aggregate.get("gross_buyback_yield_mean_covered"),
            aggregate.get("gross_shareholder_yield_mean_covered"),
            aggregate.get("coverage_roe_pct"),
            aggregate.get("coverage_earnings_yield_pct"),
            aggregate.get("coverage_dividend_yield_pct"),
            aggregate.get("coverage_buyback_yield_pct"),
            aggregate.get("coverage_shareholder_yield_pct"),
            composition_date,
            ts,
            METHODOLOGY_VERSION,
        ),
    )


def get_latest_snapshot(db: Database, etf_id: int) -> dict[str, Any] | None:
    row = db.fetchone(
        """
        SELECT *
        FROM composition_snapshots
        WHERE etf_id = ?
        ORDER BY snapshot_id DESC
        LIMIT 1
        """,
        (etf_id,),
    )
    return dict(row) if row else None


def assign_consolidated_weights(
    companies: list[CompanyFundamentals],
    equities: list[Holding],
) -> list[CompanyFundamentals]:
    """Aplica pesos consolidados e remove duplicatas por nome de empresa."""
    weight_by_name = {holding.name: holding.weight_normalized for holding in equities}
    seen: set[str] = set()
    result: list[CompanyFundamentals] = []
    for company in companies:
        key = company.company_name.casefold().strip()
        if key in seen:
            continue
        seen.add(key)
        weight = weight_by_name.get(company.company_name)
        if weight is None:
            continue
        company.weight_normalized = weight
        result.append(company)
    return result


def load_holdings_for_snapshot(db: Database, snapshot_id: int) -> list[Holding]:
    rows = db.fetchall(
        """
        SELECT h.*, e.ticker AS etf_ticker
        FROM holdings h
        JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
        JOIN etfs e ON e.etf_id = cs.etf_id
        WHERE h.snapshot_id = ?
        ORDER BY h.position
        """,
        (snapshot_id,),
    )
    holdings: list[Holding] = []
    for row in rows:
        holdings.append(
            Holding(
                etf=row["etf_ticker"],
                position=int(row["position"]),
                name=row["name_raw"],
                asset_category=row["asset_category"] or "",
                asset_type=row["asset_type"] or "",
                country=row["country"] or "",
                weight_original=float(row["weight_original"] or 0),
                weight_normalized=row["weight_normalized"],
                market_value_usd=row["market_value_usd"],
                cusip=row["cusip"],
                isin=row["isin"],
                lei=row["lei"],
                sec_ticker=row["sec_ticker"],
                other_id=row["other_id"],
                included_in_equity_analysis=bool(row["included_in_equity_analysis"]),
                exclusion_reason=row["exclusion_reason"],
            )
        )
    return holdings


def load_companies_for_etf(
    db: Database,
    etf_ticker: str,
    snapshot_id: int | None = None,
) -> tuple[list[CompanyFundamentals], list[Holding], dict[str, Any]]:
    """Carrega empresas com fundamentos e holdings para agregação."""
    etf_row = db.fetchone("SELECT * FROM etfs WHERE ticker = ?", (etf_ticker.upper(),))
    if not etf_row:
        raise ValueError(f"ETF não encontrado: {etf_ticker}")

    etf_id = int(etf_row["etf_id"])
    if snapshot_id is None:
        snapshot = get_latest_snapshot(db, etf_id)
        if not snapshot:
            raise ValueError(f"Nenhum snapshot de composição para {etf_ticker}")
        snapshot_id = int(snapshot["snapshot_id"])
    else:
        snapshot = db.fetchone(
            "SELECT * FROM composition_snapshots WHERE snapshot_id = ? AND etf_id = ?",
            (snapshot_id, etf_id),
        )
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} não encontrado para {etf_ticker}")
        snapshot = dict(snapshot)

    holdings = load_holdings_for_snapshot(db, snapshot_id)
    rows = db.fetchall(
        """
        SELECT
            h.name_raw,
            h.country,
            h.weight_normalized,
            af.*
        FROM holdings h
        JOIN assets a ON a.asset_id = h.asset_id
        JOIN asset_fundamentals af ON af.asset_id = a.asset_id
        WHERE h.snapshot_id = ?
          AND h.included_in_equity_analysis = 1
        """,
        (snapshot_id,),
    )

    companies = [
        row_to_company(
            dict(row),
            etf=etf_ticker.upper(),
            company_name=row["name_raw"],
            country=row["country"] or "",
            weight_normalized=row["weight_normalized"],
        )
        for row in rows
    ]
    return companies, holdings, dict(snapshot)
