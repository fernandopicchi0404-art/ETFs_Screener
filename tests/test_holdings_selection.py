from etf_screener.holdings.selection import consolidate_equity_holdings, renormalize_consolidated_holdings
from etf_screener.models import Holding


def _holding(name: str, weight: float, position: int) -> Holding:
    return Holding(
        etf="SCHY",
        position=position,
        name=name,
        asset_category="EC",
        asset_type="equity",
        country="BR",
        weight_original=weight,
        included_in_equity_analysis=True,
        weight_normalized=weight,
    )


def test_consolidate_duplicate_company():
    holdings = [
        _holding("Klabin SA", 0.29, 1),
        _holding("Klabin SA", 0.0001, 2),
        _holding("Ambev SA", 0.41, 3),
    ]
    consolidated = consolidate_equity_holdings(holdings)
    assert len(consolidated) == 2
    klabin = next(item for item in consolidated if item.name == "Klabin SA")
    assert round(klabin.weight_original, 4) == 0.2901


def test_renormalize_consolidated_holdings():
    holdings = [
        _holding("Klabin SA", 1.0, 1),
        _holding("Ambev SA", 3.0, 2),
    ]
    consolidated = renormalize_consolidated_holdings(holdings)
    weights = {item.name: item.weight_normalized for item in consolidated}
    assert round(weights["Klabin SA"], 2) == 25.0
    assert round(weights["Ambev SA"], 2) == 75.0
