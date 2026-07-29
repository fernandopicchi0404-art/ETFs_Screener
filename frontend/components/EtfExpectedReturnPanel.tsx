"use client";

import { PremisesControls } from "@/components/EtfPremisesControls";
import { MetricCard } from "@/components/MetricCard";
import { calculateExpectedReturn } from "@/lib/expectedReturn";
import { formatPct } from "@/lib/format";
import { useEtfPremises } from "@/lib/useEtfPremises";

interface Props {
  ticker: string;
  roePct: number | null;
  earningsYieldPct: number | null;
}

/**
 * Premissas editáveis + retorno esperado na ficha do ETF.
 * Valores salvos no mesmo localStorage da lista.
 */
export default function EtfExpectedReturnPanel({
  ticker,
  roePct,
  earningsYieldPct,
}: Props) {
  const { getPremises, setPremises } = useEtfPremises();
  const premises = getPremises(ticker);
  const result = calculateExpectedReturn(roePct, earningsYieldPct, premises);

  return (
    <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div>
        <h3 className="text-sm font-medium text-slate-800">Projeção de retorno</h3>
        <p className="mt-1 text-xs text-slate-500">
          Premissas padrão: inflação 3% e crescimento real 2%. Editáveis por ETF e salvas
          neste navegador. Crescimento = inflação + real; payout = 1 − (crescimento ÷ ROE);
          retorno esperado = (earnings yield × payout) + crescimento.
        </p>
      </div>

      <PremisesControls
        ticker={ticker}
        premises={premises}
        onChange={(next) => setPremises(ticker, next)}
        layout="inline"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Crescimento nominal"
          value={formatPct(result.growthPct)}
          hint="Inflação + crescimento real"
        />
        <MetricCard
          label="Payout implícito"
          value={formatPct(result.payoutPct)}
          hint="1 − (crescimento ÷ ROE)"
        />
        <MetricCard
          label="Retorno esperado"
          value={formatPct(result.expectedReturnPct)}
          hint="(EY × payout) + crescimento"
        />
        <MetricCard
          label="Retorno real esperado"
          value={formatPct(result.expectedRealReturnPct)}
          hint="Retorno esperado − inflação"
        />
      </div>
    </div>
  );
}
