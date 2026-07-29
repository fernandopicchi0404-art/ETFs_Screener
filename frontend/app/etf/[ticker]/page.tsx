import Link from "next/link";
import EtfHoldingsTable from "@/components/EtfHoldingsTable";
import { MetricCard } from "@/components/MetricCard";
import { getEtfDetail, listEtfHoldings } from "@/lib/queries";
import { formatPct, MIN_SITE_COVERAGE_PCT, regionLabel } from "@/lib/format";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

interface Props {
  params: Promise<{ ticker: string }>;
}

export default async function EtfDetailPage({ params }: Props) {
  const { ticker } = await params;
  const normalized = ticker.toUpperCase();
  const etf = getEtfDetail(normalized);
  if (!etf) notFound();
  // Esconde fichas com cobertura abaixo do mínimo do site.
  if ((etf.clean_coverage_pct ?? 0) < MIN_SITE_COVERAGE_PCT) notFound();

  const holdings = listEtfHoldings(normalized, 10);
  const totalCount = etf.equity_positions ?? holdings.length;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link href="/" className="text-sm text-brand-600 hover:underline">
            ← Voltar ao resumo
          </Link>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">
            {etf.ticker} — {etf.name}
          </h2>
          <p className="mt-1 text-slate-600">
            {regionLabel(etf.region)} · {etf.issuer ?? "—"} · {etf.index_name ?? "—"}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Composição de {etf.composition_date ?? "—"}
            {etf.calculated_at ? ` · Atualizado em ${etf.calculated_at.slice(0, 10)}` : ""}
          </p>
        </div>
      </div>

      {etf.has_metrics ? (
        <div className="space-y-4">
          {/* Shareholder yield líquido em destaque; dividend e buyback líquido ao lado. */}
          <div className="grid gap-4 md:grid-cols-3">
            <MetricCard
              label="Shareholder yield"
              value={formatPct(etf.shareholder_yield_pct)}
              hint={`Líquido · Cobertura: ${formatPct(etf.clean_coverage_pct, 0)}`}
            />
            <MetricCard label="Dividend yield" value={formatPct(etf.dividend_yield_pct)} />
            <MetricCard
              label="Buyback yield"
              value={formatPct(etf.buyback_yield_pct)}
              hint="Recompra líquida"
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <MetricCard label="ROE agregado" value={formatPct(etf.roe_pct)} />
            <MetricCard label="Earnings yield" value={formatPct(etf.earnings_yield_pct)} />
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
          Este ETF ainda não tem métricas calculadas no banco.
        </div>
      )}

      <EtfHoldingsTable
        ticker={normalized}
        initialHoldings={holdings}
        totalCount={totalCount}
      />
    </div>
  );
}
