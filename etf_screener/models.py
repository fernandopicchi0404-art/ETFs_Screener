from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Holding:
    etf: str
    position: int
    name: str
    asset_category: str
    asset_type: str
    country: str
    weight_original: float
    market_value_usd: float | None = None
    cusip: str | None = None
    symbol: str | None = None
    isin: str | None = None
    lei: str | None = None
    sec_ticker: str | None = None
    other_id: str | None = None
    included_in_equity_analysis: bool = False
    weight_normalized: float | None = None
    exclusion_reason: str | None = None


@dataclass
class ValidationResult:
    etf: str
    symbol: str
    period: str
    test_name: str
    calculated: float | None
    reference: float | None
    abs_diff: float | None
    pct_diff: float | None
    tolerance: float | None
    result: str
    source: str
    source_url: str
    comment: str


@dataclass
class ExceptionRecord:
    etf: str
    symbol: str
    date: str
    severity: str
    tag: str
    stage: str
    message: str
    metric_impact: str
    recommended_action: str
    status: str
    resolved_at: str = ""


@dataclass
class CompanyFundamentals:
    etf: str
    roic_symbol: str
    company_name: str
    exchange: str
    country: str
    mapping_status: str
    fundamental_currency: str
    price_currency: str
    weight_normalized: float | None = None
    fiscal_year: int | None = None
    fiscal_year_end: str | None = None
    price_date: str | None = None
    price: float | None = None
    net_income: float | None = None
    minority_interest: float | None = None
    preferred_dividends: float | None = None
    earnings_for_common: float | None = None
    diluted_shares: float | None = None
    diluted_eps: float | None = None
    equity_total: float | None = None
    minority_equity: float | None = None
    preferred_equity: float | None = None
    common_equity: float | None = None
    common_equity_prior: float | None = None
    common_equity_average: float | None = None
    dividends_paid: float | None = None
    buybacks_gross: float | None = None
    share_issuance: float | None = None
    buybacks_net: float | None = None
    dividend_adjustment: float = 0.0
    buyback_adjustment: float = 0.0
    dividends_final: float | None = None
    buybacks_final: float | None = None
    dividend_per_share: float | None = None
    buyback_gross_per_share: float | None = None
    buyback_net_per_share: float | None = None
    roe: float | None = None
    roe_method: str = ""
    earnings_yield: float | None = None
    dividend_yield: float | None = None
    gross_buyback_yield: float | None = None
    net_buyback_yield: float | None = None
    gross_shareholder_yield: float | None = None
    net_shareholder_yield: float | None = None
    quality: str = "OK"
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
