from __future__ import annotations

from dataclasses import dataclass

from etf_screener.models import CompanyFundamentals, Holding


def make_company(**kwargs) -> CompanyFundamentals:
    defaults = {
        "etf": "SCHY",
        "roic_symbol": "LSE:TEST",
        "company_name": "Test Co",
        "exchange": "LSE",
        "country": "GB",
        "mapping_status": "manual",
        "fundamental_currency": "GBP",
        "price_currency": "GBP",
        "roe": 0.15,
        "earnings_yield": 0.08,
        "dividend_yield": 0.04,
        "quality": "OK",
        "tags": [],
    }
    defaults.update(kwargs)
    return CompanyFundamentals(**defaults)


def make_holding(weight: float, name: str = "Test Co") -> Holding:
    return Holding(
        etf="SCHY",
        position=1,
        name=name,
        asset_category="EC",
        asset_type="equity",
        country="GB",
        weight_original=weight,
        included_in_equity_analysis=True,
        weight_normalized=weight,
    )
