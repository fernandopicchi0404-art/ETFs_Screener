from etf_screener.metrics.fundamentals import aggregate_etf
from tests.conftest import make_company, make_holding


def test_aggregate_excludes_blockers_from_weighted_metrics():
    clean = make_company(
        company_name="Clean Co",
        roe=0.20,
        earnings_yield=0.10,
        dividend_yield=0.05,
        quality="OK",
        weight_normalized=60.0,
    )
    blocked = make_company(
        company_name="Blocked Co",
        roic_symbol="OTC:BAD",
        roe=None,
        earnings_yield=None,
        dividend_yield=9.99,
        quality="BLOCKER",
        tags=["CURRENCY_MISMATCH"],
        weight_normalized=40.0,
    )
    holdings = [
        make_holding(60.0, "Clean Co"),
        make_holding(40.0, "Blocked Co"),
    ]
    result = aggregate_etf([clean, blocked], holdings, target_clean_coverage=0.90)
    assert result["dividend_yield_aggregate"] == 0.05 * 0.60
    assert result["clean_coverage_pct"] == 60.0
