"""Espelho da fórmula de retorno esperado do painel (frontend/lib/expectedReturn.ts)."""

from __future__ import annotations


def calculate_expected_return(
    roe_pct: float | None,
    earnings_yield_pct: float | None,
    inflation_pct: float,
    real_growth_pct: float,
) -> dict[str, float | None]:
    growth_pct = inflation_pct + real_growth_pct
    if (
        roe_pct is None
        or earnings_yield_pct is None
        or roe_pct <= 0
        or growth_pct >= roe_pct
    ):
        return {
            "growth_pct": growth_pct,
            "payout_pct": None,
            "expected_return_pct": None,
            "expected_real_return_pct": None,
        }

    payout_fraction = 1 - growth_pct / roe_pct
    expected_return_pct = earnings_yield_pct * payout_fraction + growth_pct
    return {
        "growth_pct": growth_pct,
        "payout_pct": payout_fraction * 100,
        "expected_return_pct": expected_return_pct,
        "expected_real_return_pct": expected_return_pct - inflation_pct,
    }


def test_exemplo_confirmado_pelo_usuario() -> None:
    # ROE 15%, EY 5%, inflação 3%, cresc. real 2% → ~8,3% e ~5,3%
    result = calculate_expected_return(15.0, 5.0, 3.0, 2.0)
    assert result["growth_pct"] == 5.0
    assert result["payout_pct"] is not None
    assert abs(result["payout_pct"] - (100 * 2 / 3)) < 1e-9
    assert abs(result["expected_return_pct"] - (5 * (2 / 3) + 5)) < 1e-9
    assert abs(result["expected_real_return_pct"] - (5 * (2 / 3) + 2)) < 1e-9


def test_crescimento_maior_que_roe_invalida() -> None:
    result = calculate_expected_return(4.0, 5.0, 3.0, 2.0)
    assert result["expected_return_pct"] is None
    assert result["expected_real_return_pct"] is None


def test_sem_metricas() -> None:
    result = calculate_expected_return(None, 5.0, 3.0, 2.0)
    assert result["expected_return_pct"] is None
