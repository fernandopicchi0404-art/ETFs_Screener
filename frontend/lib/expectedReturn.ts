/**
 * Premissas e retorno esperado por ETF.
 *
 * Fórmula (estudo 03/04):
 *   g = inflação + crescimento real
 *   payout = 1 − (g ÷ ROE)
 *   retorno esperado = (earnings yield × payout) + g
 *   retorno real esperado = retorno esperado − inflação
 *
 * Valores de ROE / EY entram como percentual (ex.: 15 = 15%).
 */

export const DEFAULT_INFLATION_PCT = 3;
export const DEFAULT_REAL_GROWTH_PCT = 2;

export interface EtfPremises {
  inflationPct: number;
  realGrowthPct: number;
}

export interface ExpectedReturnResult {
  growthPct: number;
  payoutPct: number | null;
  expectedReturnPct: number | null;
  expectedRealReturnPct: number | null;
}

export function defaultPremises(): EtfPremises {
  return {
    inflationPct: DEFAULT_INFLATION_PCT,
    realGrowthPct: DEFAULT_REAL_GROWTH_PCT,
  };
}

/**
 * Calcula retorno esperado a partir de ROE, earnings yield e premissas.
 * Retorna null nos campos derivados quando ROE/EY faltam ou g ≥ ROE
 * (payout sem sentido econômico).
 */
export function calculateExpectedReturn(
  roePct: number | null | undefined,
  earningsYieldPct: number | null | undefined,
  premises: EtfPremises,
): ExpectedReturnResult {
  const growthPct = premises.inflationPct + premises.realGrowthPct;

  if (
    roePct == null ||
    earningsYieldPct == null ||
    !Number.isFinite(roePct) ||
    !Number.isFinite(earningsYieldPct) ||
    roePct <= 0 ||
    growthPct >= roePct
  ) {
    return {
      growthPct,
      payoutPct: null,
      expectedReturnPct: null,
      expectedRealReturnPct: null,
    };
  }

  const payoutFraction = 1 - growthPct / roePct;
  const expectedReturnPct = earningsYieldPct * payoutFraction + growthPct;

  return {
    growthPct,
    payoutPct: payoutFraction * 100,
    expectedReturnPct,
    expectedRealReturnPct: expectedReturnPct - premises.inflationPct,
  };
}
