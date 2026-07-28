from etf_screener.validation.ticker import names_are_compatible, validate_ticker_match


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


def test_rejects_wrong_country_by_default():
    candidate = {"name": "AXA SA", "listing_country_code": "DE", "type": "stock"}
    ok, message = validate_ticker_match(
        "AXA SA",
        "FR",
        candidate,
        "STU:AXA",
    )
    assert not ok
    assert "País" in message


def test_isin_match_ignores_country_mismatch():
    candidate = {"name": "Royal Bank Of Canada", "listing_country_code": "US", "type": "stock"}
    ok, message = validate_ticker_match(
        "Royal Bank of Canada",
        "CA",
        candidate,
        "NYSE:RY",
        match_source="isin",
    )
    assert ok, message


def test_coca_cola_name_variants():
    candidate = {"name": "Coca-Cola Company (The)", "listing_country_code": "US", "type": "stock"}
    ok, message = validate_ticker_match(
        "Coca-Cola Co/The",
        "US",
        candidate,
        "NYSE:KO",
        match_source="isin",
    )
    assert ok, message


def test_names_are_compatible_munich_re():
    assert names_are_compatible(
        "Muenchener Rueckversicherungs-Gesellschaft AG in Muenchen",
        "Munchener Ruckversicherungs-Gesellschaft AG",
    )
