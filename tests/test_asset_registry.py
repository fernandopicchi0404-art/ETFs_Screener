from __future__ import annotations

import pytest

from etf_screener.holdings.asset_registry import build_asset_key
from etf_screener.models import Holding


def test_build_asset_key_prefers_isin():
    holding = Holding(
        etf="VEA",
        position=1,
        name="Nestle SA",
        asset_category="EC",
        asset_type="equity",
        country="CH",
        weight_original=1.0,
        isin="CH0038863350",
        cusip="641069406",
    )
    assert build_asset_key(holding) == "ISIN:CH0038863350"


def test_build_asset_key_falls_back_to_name_country():
    holding = Holding(
        etf="VEA",
        position=1,
        name="Nestle SA",
        asset_category="EC",
        asset_type="equity",
        country="CH",
        weight_original=1.0,
    )
    assert build_asset_key(holding) == "NAME:CH:nestle sa"
