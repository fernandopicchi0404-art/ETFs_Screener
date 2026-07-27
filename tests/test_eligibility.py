from etf_screener.metrics.eligibility import apply_eligibility, is_clean_for_coverage
from tests.conftest import make_company


def test_currency_mismatch_blocks_yields():
    company = make_company(
        fundamental_currency="JPY",
        price_currency="USD",
        earnings_yield=7.8,
        dividend_yield=5.4,
        raw={"price_normalization": {"status": "currency_mismatch"}},
    )
    apply_eligibility(company, "manual")
    assert company.quality == "BLOCKER"
    assert company.earnings_yield is None
    assert company.dividend_yield is None
    assert is_clean_for_coverage(company) is False


def test_implausible_dividend_yield_is_removed():
    company = make_company(dividend_yield=5.48, raw={"price_normalization": {"status": "same_currency"}})
    apply_eligibility(company, "manual")
    assert company.dividend_yield is None
    assert "IMPLAUSIBLE_DIVIDEND_YIELD" in company.tags
