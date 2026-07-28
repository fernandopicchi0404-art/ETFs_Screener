from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from etf_screener.config import EQUITY_ASSET_CATEGORIES
from etf_screener.holdings.nport_identifiers import parse_identifiers
from etf_screener.models import Holding

NS = {"n": "http://www.sec.gov/edgar/nport"}

ASSET_TYPE_LABELS = {
    "EC": "equity",
    "EP": "preferred_equity",
    "DE": "derivative",
    "STIV": "cash",
}

INVALID_CUSIP = "000000000"


def _asset_type(asset_category: str) -> str:
    return ASSET_TYPE_LABELS.get(asset_category, "other")


def parse_nport_holdings(xml_path: Path, etf: str) -> list[Holding]:
    root = ET.parse(xml_path).getroot()
    holdings: list[Holding] = []

    for index, node in enumerate(root.findall(".//n:invstOrSec", NS), start=1):
        asset_category = node.findtext("n:assetCat", default="", namespaces=NS) or ""
        name = node.findtext("n:name", default="", namespaces=NS) or ""
        weight = float(node.findtext("n:pctVal", default="0", namespaces=NS) or 0)
        market_value = node.findtext("n:valUSD", default=None, namespaces=NS)
        country = node.findtext("n:invCountry", default="", namespaces=NS) or ""
        cusip_raw = node.findtext("n:cusip", default=None, namespaces=NS)
        cusip = cusip_raw if cusip_raw and cusip_raw != INVALID_CUSIP else None
        lei = node.findtext("n:lei", default=None, namespaces=NS)
        identifiers = parse_identifiers(node.find("n:identifiers", NS))
        isin = identifiers["isin"]
        sec_ticker = identifiers["ticker"]

        included = asset_category in EQUITY_ASSET_CATEGORIES
        holding = Holding(
            etf=etf,
            position=index,
            name=name,
            asset_category=asset_category,
            asset_type=_asset_type(asset_category),
            country=country,
            weight_original=weight,
            market_value_usd=float(market_value) if market_value else None,
            cusip=cusip,
            isin=isin,
            lei=lei,
            sec_ticker=sec_ticker,
            other_id=identifiers["other_id"],
            included_in_equity_analysis=included,
            exclusion_reason=None if included else f"asset_category={asset_category}",
        )
        holdings.append(holding)

    return holdings


def normalize_equity_weights(holdings: list[Holding]) -> list[Holding]:
    equities = [holding for holding in holdings if holding.included_in_equity_analysis]
    total_weight = sum(holding.weight_original for holding in equities)
    if total_weight <= 0:
        raise ValueError("Nenhuma posição em ações encontrada para normalização.")

    for holding in holdings:
        if holding.included_in_equity_analysis:
            holding.weight_normalized = holding.weight_original / total_weight * 100
        else:
            holding.weight_normalized = None

    return holdings
