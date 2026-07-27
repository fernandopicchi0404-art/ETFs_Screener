from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedPrice:
    """Preço convertido para a unidade monetária dos demonstrativos."""

    value: float | None
    currency: str
    factor: float | None
    status: str


# Algumas bolsas informam preços em centavos da moeda usada nos demonstrativos.
# Manter essa tabela explícita evita conversões implícitas difíceis de auditar.
SUBUNIT_CONVERSIONS = {
    ("GBX", "GBP"): 0.01,
    ("ZAC", "ZAR"): 0.01,
    ("KWF", "KWD"): 0.001,
}


def normalize_price(
    price: float | None,
    price_currency: str,
    fundamental_currency: str,
) -> NormalizedPrice:
    """Normaliza o preço ou o bloqueia quando as moedas são incompatíveis."""
    if price is None:
        return NormalizedPrice(None, price_currency, None, "missing_price")
    if not price_currency or not fundamental_currency:
        return NormalizedPrice(None, price_currency, None, "missing_currency")
    if price_currency == fundamental_currency:
        return NormalizedPrice(price, fundamental_currency, 1.0, "same_currency")

    factor = SUBUNIT_CONVERSIONS.get((price_currency, fundamental_currency))
    if factor is None:
        return NormalizedPrice(None, price_currency, None, "currency_mismatch")
    return NormalizedPrice(price * factor, fundamental_currency, factor, "unit_converted")
