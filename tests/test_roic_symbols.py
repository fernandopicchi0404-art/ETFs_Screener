from etf_screener.roic.symbols import encode_roic_identifier, resolve_fetch_symbol, roic_symbol_path


def test_encode_mexican_share_class():
    assert encode_roic_identifier("BMV:KOF/UBL") == "BMV:KOF%2FUBL"
    assert encode_roic_identifier("NYSE:AAPL") == "NYSE:AAPL"


def test_roic_symbol_path():
    assert roic_symbol_path("/fundamental/income-statement", "BMV:AMX/B") == (
        "/fundamental/income-statement/BMV:AMX%2FB"
    )


def test_fetch_symbol_aliases():
    assert resolve_fetch_symbol("SIX:ROG") == "SIX:RO"
    assert resolve_fetch_symbol("BMV:AC") == "BMV:AC"
