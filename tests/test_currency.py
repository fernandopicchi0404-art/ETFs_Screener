from etf_screener.metrics.currency import normalize_price


def test_normalize_price_same_currency():
    result = normalize_price(100.0, "USD", "USD")
    assert result.value == 100.0
    assert result.status == "same_currency"


def test_normalize_price_gbx_to_gbp():
    result = normalize_price(2823.0, "GBX", "GBP")
    assert result.value == 28.23
    assert result.status == "unit_converted"


def test_normalize_price_blocks_currency_mismatch():
    result = normalize_price(36.62, "USD", "JPY")
    assert result.value is None
    assert result.status == "currency_mismatch"
