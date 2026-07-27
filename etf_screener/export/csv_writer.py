from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


COMPANY_FIELDS = [
    "etf",
    "roic_symbol",
    "company_name",
    "weight_normalized",
    "exchange",
    "country",
    "mapping_status",
    "fundamental_currency",
    "price_currency",
    "fiscal_year",
    "fiscal_year_end",
    "price_date",
    "price",
    "net_income",
    "minority_interest",
    "preferred_dividends",
    "earnings_for_common",
    "diluted_shares",
    "diluted_eps",
    "equity_total",
    "minority_equity",
    "preferred_equity",
    "common_equity",
    "common_equity_prior",
    "common_equity_average",
    "dividends_paid",
    "buybacks_gross",
    "share_issuance",
    "buybacks_net",
    "dividend_adjustment",
    "buyback_adjustment",
    "dividends_final",
    "buybacks_final",
    "dividend_per_share",
    "buyback_gross_per_share",
    "buyback_net_per_share",
    "roe",
    "roe_method",
    "earnings_yield",
    "dividend_yield",
    "gross_buyback_yield",
    "net_buyback_yield",
    "gross_shareholder_yield",
    "net_shareholder_yield",
    "quality",
    "tags",
    "notes",
]

HOLDING_FIELDS = [
    "etf",
    "position",
    "name",
    "asset_category",
    "asset_type",
    "country",
    "weight_original",
    "weight_normalized",
    "market_value_usd",
    "cusip",
    "symbol",
    "isin",
    "included_in_equity_analysis",
    "exclusion_reason",
]

VALIDATION_FIELDS = [
    "etf",
    "symbol",
    "period",
    "test_name",
    "calculated",
    "reference",
    "abs_diff",
    "pct_diff",
    "tolerance",
    "result",
    "source",
    "source_url",
    "comment",
]

EXCEPTION_FIELDS = [
    "etf",
    "symbol",
    "date",
    "severity",
    "tag",
    "stage",
    "message",
    "metric_impact",
    "recommended_action",
    "status",
    "resolved_at",
]
