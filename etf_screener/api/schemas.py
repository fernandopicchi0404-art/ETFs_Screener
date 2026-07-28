"""Schemas Pydantic para a API REST."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EtfSummary(BaseModel):
    ticker: str
    name: str
    region: str | None = None
    country: str | None = None
    issuer: str | None = None
    theme: str | None = None
    priority: str | None = None
    index_name: str | None = None
    equity_positions: int | None = None
    roe_pct: float | None = Field(None, description="ROE agregado em percentual (ex.: 16.9)")
    earnings_yield_pct: float | None = None
    dividend_yield_pct: float | None = None
    shareholder_yield_pct: float | None = None
    clean_coverage_pct: float | None = None
    composition_date: str | None = None
    has_metrics: bool = False


class EtfDetail(EtfSummary):
    equity_weight_pct: float | None = None
    non_equity_weight_pct: float | None = None
    gross_buyback_yield_pct: float | None = None
    net_buyback_yield_pct: float | None = None
    coverage_roe_pct: float | None = None
    coverage_earnings_yield_pct: float | None = None
    coverage_dividend_yield_pct: float | None = None
    calculated_at: str | None = None


class HoldingItem(BaseModel):
    position: int
    company_name: str
    country: str | None = None
    sector: str | None = None
    weight_pct: float | None = None
    roe_pct: float | None = None
    earnings_yield_pct: float | None = None
    dividend_yield_pct: float | None = None
    shareholder_yield_pct: float | None = None
    quality: str | None = None
    roic_symbol: str | None = None


class AssetItem(BaseModel):
    asset_id: int
    company_name: str
    country: str | None = None
    sector: str | None = None
    roe_pct: float | None = None
    earnings_yield_pct: float | None = None
    dividend_yield_pct: float | None = None
    shareholder_yield_pct: float | None = None
    quality: str | None = None
    roic_symbol: str | None = None
    etf_count: int = 0


class MetaList(BaseModel):
    regions: list[str]
    sectors: list[str]
