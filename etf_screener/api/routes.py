"""Rotas REST do ETF Screener."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from etf_screener.api.queries import (
    get_etf_detail,
    list_assets,
    list_etf_holdings,
    list_etf_summaries,
    list_regions,
    list_sectors,
)
from etf_screener.api.schemas import AssetItem, EtfDetail, EtfSummary, HoldingItem, MetaList
from etf_screener.database.db import Database

router = APIRouter(prefix="/api")


def _db() -> Database:
    return Database()


@router.get("/etfs", response_model=list[EtfSummary])
def get_etfs(
    region: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    sort_by: str = Query("ticker", pattern="^(ticker|name|region|equity_positions|roe|earnings_yield|shareholder_yield|dividend_yield|buyback_yield|coverage)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[dict]:
    return list_etf_summaries(
        _db(),
        region=region,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/etfs/{ticker}", response_model=EtfDetail)
def get_etf(ticker: str) -> dict:
    item = get_etf_detail(_db(), ticker)
    if not item:
        raise HTTPException(status_code=404, detail=f"ETF não encontrado: {ticker}")
    return item


@router.get("/etfs/{ticker}/holdings", response_model=list[HoldingItem])
def get_holdings(
    ticker: str,
    limit: int | None = Query(10, ge=1, le=500),
    all: bool = Query(False, alias="all"),
) -> list[dict]:
    if not get_etf_detail(_db(), ticker):
        raise HTTPException(status_code=404, detail=f"ETF não encontrado: {ticker}")
    return list_etf_holdings(_db(), ticker, limit=None if all else limit)


@router.get("/assets", response_model=list[AssetItem])
def get_assets(
    country: str | None = None,
    sector: str | None = None,
    quality: str | None = None,
    search: str | None = None,
    sort_by: str = Query("name", pattern="^(name|country|sector|roe|earnings_yield|dividend_yield|etf_count)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[dict]:
    return list_assets(
        _db(),
        country=country,
        sector=sector,
        quality=quality,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/meta/regions", response_model=MetaList)
def get_meta_regions() -> dict:
    return {"regions": list_regions(_db()), "sectors": []}


@router.get("/meta/sectors", response_model=MetaList)
def get_meta_sectors() -> dict:
    return {"regions": [], "sectors": list_sectors(_db())}
