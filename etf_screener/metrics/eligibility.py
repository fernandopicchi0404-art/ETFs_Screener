from __future__ import annotations

from etf_screener.metrics.currency import SUBUNIT_CONVERSIONS
from etf_screener.models import CompanyFundamentals

YIELD_METRICS = (
    "earnings_yield",
    "dividend_yield",
    "gross_buyback_yield",
    "net_buyback_yield",
    "gross_shareholder_yield",
    "net_shareholder_yield",
)

MAX_DIVIDEND_YIELD = 0.20
MAX_EARNINGS_YIELD = 1.0
MIN_EARNINGS_YIELD = -1.0
MAX_ROE = 2.0


def currencies_compatible(fundamental_currency: str, price_currency: str) -> bool:
    if not fundamental_currency or not price_currency:
        return False
    if fundamental_currency == price_currency:
        return True
    return (price_currency, fundamental_currency) in SUBUNIT_CONVERSIONS


def _null_metric(company: CompanyFundamentals, metric_name: str) -> None:
    setattr(company, metric_name, None)


def _block_yields(company: CompanyFundamentals, tag: str) -> None:
    if tag not in company.tags:
        company.tags.append(tag)
    for metric_name in YIELD_METRICS:
        _null_metric(company, metric_name)


def apply_eligibility(company: CompanyFundamentals, mapping_status: str) -> None:
    """Aplica regras de bloqueio e remove métricas não confiáveis."""
    if mapping_status == "ambiguous":
        company.quality = "BLOCKER"
        company.tags.append("MAPPING_AMBIGUOUS")
        for metric_name in ("roe", *YIELD_METRICS):
            _null_metric(company, metric_name)
        return

    price_status = company.raw.get("price_normalization", {}).get("status")
    if price_status == "currency_mismatch":
        company.quality = "BLOCKER"
        company.tags.append("CURRENCY_MISMATCH")
        _block_yields(company, "CURRENCY_MISMATCH")
        _null_metric(company, "roe")
        return

    if company.earnings_yield is not None:
        if company.earnings_yield > MAX_EARNINGS_YIELD or company.earnings_yield < MIN_EARNINGS_YIELD:
            company.tags.append("IMPLAUSIBLE_EARNINGS_YIELD")
            _null_metric(company, "earnings_yield")

    if company.dividend_yield is not None and company.dividend_yield > MAX_DIVIDEND_YIELD:
        company.tags.append("IMPLAUSIBLE_DIVIDEND_YIELD")
        _null_metric(company, "dividend_yield")
        _null_metric(company, "gross_shareholder_yield")
        _null_metric(company, "net_shareholder_yield")

    if company.roe is not None and abs(company.roe) > MAX_ROE:
        company.tags.append("IMPLAUSIBLE_ROE")
        _null_metric(company, "roe")

    if "IMPLAUSIBLE_EARNINGS_YIELD" in company.tags and company.earnings_yield is None:
        if company.quality == "OK":
            company.quality = "WARNING"

    if company.quality != "BLOCKER" and company.roe is None and company.earnings_yield is None:
        company.quality = "BLOCKER"
        company.tags.append("MISSING_CORE_METRICS")


def is_clean_for_coverage(company: CompanyFundamentals) -> bool:
    """Ativo conta para a meta de cobertura limpa de 90%."""
    if company.quality == "BLOCKER":
        return False
    if company.roe is None or company.earnings_yield is None:
        return False
    if "CURRENCY_MISMATCH" in company.tags:
        return False
    if "MAPPING_AMBIGUOUS" in company.tags:
        return False
    return True
