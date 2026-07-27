from etf_screener.validation.ticker import validate_ticker_match


def test_kpn_accepts_royal_alias():
    candidate = {"name": "Royal KPN NV", "listing_country_code": "NL", "type": "stock"}
    ok, message = validate_ticker_match(
        "Koninklijke KPN NV",
        "NL",
        candidate,
        "EURONEXT:KPN",
    )
    assert ok, message


def test_tim_accepts_short_name():
    candidate = {"name": "TIM S.A.", "listing_country_code": "BR", "type": "stock"}
    ok, message = validate_ticker_match(
        "TIM SA/Brazil",
        "BR",
        candidate,
        "B3:TIMS3",
    )
    assert ok, message


def test_rejects_wrong_country():
    candidate = {"name": "AXA SA", "listing_country_code": "DE", "type": "stock"}
    ok, message = validate_ticker_match(
        "AXA SA",
        "FR",
        candidate,
        "STU:AXA",
    )
    assert not ok
    assert "País" in message
