from __future__ import annotations

from etf_screener.roic.exchange_map import infer_roic_symbol


def test_infer_roic_symbol_from_country_and_ticker():
    assert infer_roic_symbol("US", "AAPL") == "NASDAQ:AAPL"
    assert infer_roic_symbol("GB", "imb") == "LSE:IMB"
    assert infer_roic_symbol("CH", "NESN") == "SIX:NESN"


def test_infer_roic_symbol_keeps_existing_exchange():
    assert infer_roic_symbol("US", "NASDAQ:AAPL") == "NASDAQ:AAPL"


def test_infer_roic_symbol_unknown_country():
    assert infer_roic_symbol("ZZ", "FOO") is None
