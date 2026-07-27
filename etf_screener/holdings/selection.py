from __future__ import annotations

from dataclasses import replace

from etf_screener.models import Holding


def consolidate_equity_holdings(holdings: list[Holding]) -> list[Holding]:
    """Consolida posições repetidas da mesma empresa antes da análise."""
    consolidated: dict[tuple[str, str], Holding] = {}
    order: list[tuple[str, str]] = []

    for holding in holdings:
        if not holding.included_in_equity_analysis:
            continue
        key = (holding.name.casefold().strip(), holding.country)
        if key not in consolidated:
            consolidated[key] = replace(holding)
            order.append(key)
            continue

        current = consolidated[key]
        current.weight_original += holding.weight_original
        current.market_value_usd = (current.market_value_usd or 0) + (holding.market_value_usd or 0)
        if current.weight_normalized is not None and holding.weight_normalized is not None:
            current.weight_normalized += holding.weight_normalized

    return sorted(
        (consolidated[key] for key in order),
        key=lambda holding: holding.weight_normalized or 0,
        reverse=True,
    )


def renormalize_consolidated_holdings(holdings: list[Holding]) -> list[Holding]:
    """Recalcula pesos normalizados após consolidar empresas duplicadas."""
    total_weight = sum(holding.weight_original for holding in holdings)
    if total_weight <= 0:
        raise ValueError("Nenhuma posição em ações encontrada para normalização.")

    for holding in holdings:
        holding.weight_normalized = holding.weight_original / total_weight * 100
    return holdings


def clean_company_weight(company, holding: Holding) -> float:
    """Retorna peso limpo apenas quando as métricas centrais são elegíveis."""
    from etf_screener.metrics.eligibility import is_clean_for_coverage

    if not is_clean_for_coverage(company):
        return 0.0
    return holding.weight_normalized or 0.0
