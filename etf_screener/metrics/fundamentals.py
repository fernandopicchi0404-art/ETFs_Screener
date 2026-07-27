from __future__ import annotations

from typing import Any

from etf_screener.metrics.currency import normalize_price
from etf_screener.metrics.eligibility import apply_eligibility, currencies_compatible
from etf_screener.models import CompanyFundamentals, ExceptionRecord, ValidationResult


def _first(payload: dict[str, Any]) -> dict[str, Any] | None:
    data = payload.get("data")
    if isinstance(data, list) and data:
        return data[0]
    return None


def _nth(payload: dict[str, Any], index: int) -> dict[str, Any]:
    data = payload.get("data")
    if isinstance(data, list) and len(data) > index:
        return data[index] or {}
    return {}


def _safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def _pick(*values: float | None) -> float | None:
    for value in values:
        if value is not None:
            return value
    return None


def extract_fundamentals(
    etf: str,
    roic_symbol: str,
    company_name: str,
    country: str,
    mapping_status: str,
    income_payload: dict[str, Any],
    balance_payload: dict[str, Any],
    cashflow_payload: dict[str, Any],
    price_payload: dict[str, Any],
) -> CompanyFundamentals:
    income = _first(income_payload) or {}
    balance = _first(balance_payload) or {}
    balance_prior = _nth(balance_payload, 1)
    cashflow = _first(cashflow_payload) or {}

    earnings_for_common = _pick(
        income.get("is_earn_for_common"),
        income.get("is_net_income"),
    )
    diluted_shares = income.get("is_sh_for_diluted_eps") or income.get("is_avg_num_sh_for_eps")
    diluted_eps = income.get("diluted_eps") or income.get("eps")

    equity_total = balance.get("bs_total_equity")
    minority_equity = balance.get("bs_minority_noncontrolling_interest")
    preferred_equity = balance.get("bs_pfd_eqty_and_hybrid_cptl")
    common_equity = _pick(
        balance.get("bs_eqty_bef_minority_int_detailed"),
        equity_total,
    )
    if common_equity is not None and minority_equity:
        common_equity = common_equity - minority_equity
    if common_equity is not None and preferred_equity:
        common_equity = common_equity - preferred_equity

    common_equity_prior = _pick(
        balance_prior.get("bs_eqty_bef_minority_int_detailed"),
        balance_prior.get("bs_total_equity"),
    )
    prior_minority = balance_prior.get("bs_minority_noncontrolling_interest")
    prior_preferred = balance_prior.get("bs_pfd_eqty_and_hybrid_cptl")
    if common_equity_prior is not None and prior_minority:
        common_equity_prior = common_equity_prior - prior_minority
    if common_equity_prior is not None and prior_preferred:
        common_equity_prior = common_equity_prior - prior_preferred

    if common_equity is not None and common_equity_prior is not None:
        common_equity_average = (common_equity + common_equity_prior) / 2
        roe_method = "average_common_equity"
    else:
        common_equity_average = common_equity
        roe_method = "ending_common_equity_fallback"

    dividends_paid = cashflow.get("cf_dvd_paid")
    if dividends_paid is not None:
        dividends_paid = abs(dividends_paid)
    elif income.get("div_per_shr") is not None and diluted_shares:
        dividends_paid = abs(income["div_per_shr"] * diluted_shares)

    buybacks_gross = _pick(
        cashflow.get("cf_decr_cap_stock"),
        cashflow.get("cf_proc_fr_repurch_eqty_detailed"),
    )
    if buybacks_gross is not None:
        buybacks_gross = abs(buybacks_gross)

    share_issuance = cashflow.get("cf_incr_cap_stock")
    if share_issuance is not None:
        share_issuance = abs(share_issuance)

    buybacks_net = None
    if buybacks_gross is not None or share_issuance is not None:
        buybacks_net = (buybacks_gross or 0) - (share_issuance or 0)

    price_raw = price_payload.get("close")
    fundamental_currency = income.get("currency") or balance.get("currency") or ""
    price_currency = price_payload.get("currency") or ""
    normalized_price = normalize_price(price_raw, price_currency, fundamental_currency)
    price = normalized_price.value
    market_cap = price * diluted_shares if price and diluted_shares else None

    dividend_per_share = _safe_div(dividends_paid, diluted_shares)
    buyback_gross_per_share = _safe_div(buybacks_gross, diluted_shares)
    buyback_net_per_share = _safe_div(buybacks_net, diluted_shares)

    roe = _safe_div(earnings_for_common, common_equity_average)
    earnings_yield = _safe_div(diluted_eps, price) if price is not None else None
    dividend_yield = _safe_div(dividend_per_share, price) if price is not None else None
    gross_buyback_yield = _safe_div(buyback_gross_per_share, price) if price is not None else None
    net_buyback_yield = _safe_div(buyback_net_per_share, price) if price is not None else None
    gross_shareholder_yield = None
    net_shareholder_yield = None
    if dividend_yield is not None or gross_buyback_yield is not None:
        gross_shareholder_yield = (dividend_yield or 0) + (gross_buyback_yield or 0)
    if dividend_yield is not None or net_buyback_yield is not None:
        net_shareholder_yield = (dividend_yield or 0) + (net_buyback_yield or 0)

    tags: list[str] = []
    quality = "OK"
    if mapping_status == "ambiguous":
        tags.append("MAPPING_AMBIGUOUS")
        quality = "WARNING"
    if roe_method.endswith("fallback"):
        tags.append("ENDING_EQUITY_FALLBACK")
        quality = "WARNING"
    if dividends_paid is None:
        tags.append("MISSING_DIVIDEND")
    if buybacks_gross is None:
        tags.append("MISSING_BUYBACK")
    if earnings_for_common is not None and earnings_for_common < 0:
        tags.append("NEGATIVE_EARNINGS")
    if common_equity_average is not None and common_equity_average <= 0:
        tags.append("NEGATIVE_EQUITY")

    if normalized_price.status == "currency_mismatch":
        tags.append("CURRENCY_MISMATCH")
        quality = "BLOCKER"
    elif normalized_price.status == "unit_converted":
        tags.append("PRICE_UNIT_CONVERTED")

    company = CompanyFundamentals(
        etf=etf,
        roic_symbol=roic_symbol,
        company_name=company_name,
        exchange=roic_symbol.split(":")[0] if ":" in roic_symbol else "",
        country=country,
        mapping_status=mapping_status,
        fundamental_currency=fundamental_currency,
        price_currency=price_currency,
        fiscal_year=income.get("fiscal_year"),
        fiscal_year_end=income.get("period_end_date"),
        price_date=price_payload.get("date"),
        price=price,
        net_income=income.get("is_net_income"),
        minority_interest=income.get("is_min_noncontrol_interest_credits"),
        preferred_dividends=income.get("is_tot_cash_pfd_dvd"),
        earnings_for_common=earnings_for_common,
        diluted_shares=diluted_shares,
        diluted_eps=diluted_eps,
        equity_total=equity_total,
        minority_equity=minority_equity,
        preferred_equity=preferred_equity,
        common_equity=common_equity,
        common_equity_prior=common_equity_prior,
        common_equity_average=common_equity_average,
        dividends_paid=dividends_paid,
        buybacks_gross=buybacks_gross,
        share_issuance=share_issuance,
        buybacks_net=buybacks_net,
        dividends_final=dividends_paid,
        buybacks_final=buybacks_gross,
        dividend_per_share=dividend_per_share,
        buyback_gross_per_share=buyback_gross_per_share,
        buyback_net_per_share=buyback_net_per_share,
        roe=roe,
        roe_method=roe_method,
        earnings_yield=earnings_yield,
        dividend_yield=dividend_yield,
        gross_buyback_yield=gross_buyback_yield,
        net_buyback_yield=net_buyback_yield,
        gross_shareholder_yield=gross_shareholder_yield,
        net_shareholder_yield=net_shareholder_yield,
        quality=quality,
        tags=tags,
        raw={
            "market_cap": market_cap,
            "income": income,
            "balance": balance,
            "balance_prior": balance_prior,
            "cashflow": cashflow,
            "price": price_payload,
            "price_normalization": {
                "status": normalized_price.status,
                "factor": normalized_price.factor,
                "price_raw": price_raw,
            },
        },
    )
    apply_eligibility(company, mapping_status)
    return company


def validate_company(company: CompanyFundamentals) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    income = company.raw.get("income", {})
    recalculated_eps = _safe_div(company.earnings_for_common, company.diluted_shares)
    if recalculated_eps is not None and company.diluted_eps is not None:
        diff = abs(recalculated_eps - company.diluted_eps)
        pct = diff / abs(company.diluted_eps) if company.diluted_eps else None
        status = "PASS" if pct is not None and pct <= 0.05 else "WARNING"
        results.append(
            ValidationResult(
                etf=company.etf,
                symbol=company.roic_symbol,
                period=str(company.fiscal_year or ""),
                test_name="eps_reconciliation",
                calculated=recalculated_eps,
                reference=company.diluted_eps,
                abs_diff=diff,
                pct_diff=pct,
                tolerance=0.05,
                result=status,
                source="internal",
                source_url="",
                comment="Lucro ordinário dividido por ações diluídas versus EPS reportado.",
            )
        )

    assets = company.raw.get("balance", {}).get("bs_tot_asset")
    liabilities = company.raw.get("balance", {}).get("bs_tot_liab")
    equity = company.raw.get("balance", {}).get("bs_total_equity")
    if None not in (assets, liabilities, equity):
        lhs = assets
        rhs = liabilities + equity
        diff = abs(lhs - rhs)
        pct = diff / abs(assets) if assets else None
        status = "PASS" if pct is not None and pct <= 0.02 else "WARNING"
        results.append(
            ValidationResult(
                etf=company.etf,
                symbol=company.roic_symbol,
                period=str(company.fiscal_year or ""),
                test_name="balance_sheet_identity",
                calculated=lhs,
                reference=rhs,
                abs_diff=diff,
                pct_diff=pct,
                tolerance=0.02,
                result=status,
                source="internal",
                source_url="",
                comment="Ativos devem ser aproximadamente iguais a passivos + patrimônio.",
            )
        )

    if company.fundamental_currency and company.price_currency:
        compatible = currencies_compatible(company.fundamental_currency, company.price_currency)
        converted = company.raw.get("price_normalization", {}).get("status") == "unit_converted"
        passed = compatible or converted
        results.append(
            ValidationResult(
                etf=company.etf,
                symbol=company.roic_symbol,
                period=str(company.fiscal_year or ""),
                test_name="currency_match",
                calculated=1.0 if passed else 0.0,
                reference=1.0,
                abs_diff=0.0 if passed else 1.0,
                pct_diff=0.0 if passed else 1.0,
                tolerance=0.0,
                result="PASS" if passed else "BLOCKER",
                source="internal",
                source_url="",
                comment="Moeda do demonstrativo versus moeda do preço, com conversão de subunidade quando aplicável.",
            )
        )

    if company.dividends_paid is None and income.get("div_per_shr") is None:
        results.append(
            ValidationResult(
                etf=company.etf,
                symbol=company.roic_symbol,
                period=str(company.fiscal_year or ""),
                test_name="dividend_presence",
                calculated=None,
                reference=None,
                abs_diff=None,
                pct_diff=None,
                tolerance=None,
                result="WARNING",
                source="internal",
                source_url="",
                comment="Nenhum campo de dividendos encontrado na ROIC para este ativo.",
            )
        )

    return results


def aggregate_etf(
    companies: list[CompanyFundamentals],
    holdings: list,
    target_clean_coverage: float = 0.90,
) -> dict[str, float | int | str | None]:
    equities = [holding for holding in holdings if holding.included_in_equity_analysis]
    equity_weight_total = sum(holding.weight_original for holding in equities)
    non_equity_weight = 100 - equity_weight_total
    weight_by_name = {holding.name: holding.weight_normalized for holding in equities}

    def weighted(metric_name: str, require_clean: bool = False) -> tuple[float | None, float, float | None]:
        covered = 0.0
        total = 0.0
        simple_values: list[float] = []
        for company in companies:
            weight = weight_by_name.get(company.company_name)
            value = getattr(company, metric_name)
            if weight is None or value is None:
                continue
            if require_clean and company.quality == "BLOCKER":
                continue
            total += (weight / 100) * value
            covered += weight
            simple_values.append(value)
        mean_covered = sum(simple_values) / len(simple_values) if simple_values else None
        return (total if covered else None, covered, mean_covered)

    earnings_yield, earnings_cov, earnings_mean = weighted("earnings_yield", require_clean=True)
    dividend_yield, dividend_cov, dividend_mean = weighted("dividend_yield", require_clean=True)
    gross_buyback_yield, buyback_cov, buyback_mean = weighted("gross_buyback_yield", require_clean=True)
    net_buyback_yield, _, _ = weighted("net_buyback_yield", require_clean=True)
    gross_shareholder_yield, shareholder_cov, shareholder_mean = weighted(
        "gross_shareholder_yield",
        require_clean=True,
    )
    net_shareholder_yield, _, _ = weighted("net_shareholder_yield", require_clean=True)

    proportional_earnings = 0.0
    proportional_equity = 0.0
    roe_cov = 0.0
    for company in companies:
        weight = weight_by_name.get(company.company_name)
        if (
            weight is None
            or company.quality == "BLOCKER"
            or company.earnings_for_common is None
            or company.common_equity_average is None
        ):
            continue
        factor = weight / 100
        proportional_earnings += company.earnings_for_common * factor
        proportional_equity += company.common_equity_average * factor
        roe_cov += weight

    roe_aggregate = _safe_div(proportional_earnings, proportional_equity)
    from etf_screener.holdings.selection import clean_company_weight

    clean_coverage = 0.0
    for company in companies:
        holding = next((item for item in equities if item.name == company.company_name), None)
        if holding is None:
            continue
        clean_coverage += clean_company_weight(company, holding)

    return {
        "etf": companies[0].etf if companies else "SCHY",
        "equity_positions": len(equities),
        "equity_weight_original_pct": equity_weight_total,
        "non_equity_weight_original_pct": non_equity_weight,
        "target_clean_coverage_pct": target_clean_coverage * 100,
        "clean_coverage_pct": clean_coverage,
        "target_clean_coverage_met": clean_coverage >= target_clean_coverage * 100,
        "roe_aggregate": roe_aggregate,
        "earnings_yield_aggregate": earnings_yield,
        "dividend_yield_aggregate": dividend_yield,
        "gross_buyback_yield_aggregate": gross_buyback_yield,
        "net_buyback_yield_aggregate": net_buyback_yield,
        "gross_shareholder_yield_aggregate": gross_shareholder_yield,
        "net_shareholder_yield_aggregate": net_shareholder_yield,
        "earnings_yield_mean_covered": earnings_mean,
        "dividend_yield_mean_covered": dividend_mean,
        "gross_buyback_yield_mean_covered": buyback_mean,
        "gross_shareholder_yield_mean_covered": shareholder_mean,
        "coverage_roe_pct": roe_cov,
        "coverage_earnings_yield_pct": earnings_cov,
        "coverage_dividend_yield_pct": dividend_cov,
        "coverage_buyback_yield_pct": buyback_cov,
        "coverage_shareholder_yield_pct": shareholder_cov,
    }
