from __future__ import annotations

# Bolsa principal por país (código ISO do N-PORT). Usado quando a SEC traz ticker sem bolsa.
COUNTRY_PRIMARY_EXCHANGE: dict[str, str] = {
    "US": "NASDAQ",
    "GB": "LSE",
    "CH": "SIX",
    "DE": "XETRA",
    "FR": "EURONEXT",
    "NL": "EURONEXT",
    "BE": "EURONEXT",
    "IT": "MIL",
    "ES": "BME",
    "PT": "EURONEXT",
    "AU": "ASX",
    "HK": "HKEX",
    "JP": "TSE",
    "KR": "KRX",
    "TW": "TWSE",
    "SG": "SGX",
    "CA": "TSX",
    "BR": "B3",
    "MX": "BMV",
    "SA": "TADAWUL",
    "AE": "ADX",
    "QA": "QSE",
    "IL": "TASE",
    "NO": "OSL",
    "SE": "STO",
    "DK": "CPH",
    "FI": "HEL",
    "NZ": "NZX",
    "MY": "MYX",
    "ID": "IDX",
    "TH": "SET",
    "ZA": "JSE",
    "IN": "NSE",
    "PL": "WSE",
    "AT": "VIE",
    "IE": "LSE",
    "LU": "EURONEXT",
    "PH": "PSE",
    "CL": "BCS",
    "CO": "BVC",
    "PE": "BVL",
    "TR": "BIST",
    "GR": "ATH",
    "HU": "BUD",
    "CZ": "PRA",
}


def infer_roic_symbol(country: str | None, sec_ticker: str | None) -> str | None:
    """Monta EXCHANGE:TICKER a partir do país e ticker bruto da SEC."""
    if not sec_ticker:
        return None
    ticker = sec_ticker.strip().upper()
    if not ticker:
        return None
    if ":" in ticker:
        return ticker
    exchange = COUNTRY_PRIMARY_EXCHANGE.get((country or "").upper())
    if not exchange:
        return None
    return f"{exchange}:{ticker}"
