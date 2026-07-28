import Link from "next/link";
import DataTable, { Column } from "@/components/DataTable";
import { MetricCard } from "@/components/MetricCard";
import { getEtfDetail, listEtfHoldings } from "@/lib/queries";
import { formatPct, qualityBadge, regionLabel } from "@/lib/format";
import { HoldingItem } from "@/lib/api";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

interface Props {
  params: Promise<{ ticker: string }>;
}

export default async function EtfDetailPage({ params }: Props) {
  const { ticker } = await params;
  const etf = getEtfDetail(ticker.toUpperCase());
  if (!etf) notFound();

  const holdings = listEtfHoldings(ticker.toUpperCase(), 10);

  const columns: Column<HoldingItem>[] = [
    { key: "position", label: "#", align: "right" },
    { key: "company_name", label: "Empresa" },
    { key: "country", label: "País" },
    { key: "sector", label: "Setor", render: (row) => row.sector ?? "—" },
    {
      key: "weight_pct",
      label: "Peso",
      align: "right",
      render: (row) => formatPct(row.weight_pct),
    },
    {
      key: "roe_pct",
      label: "ROE",
      align: "right",
      render: (row) => formatPct(row.roe_pct),
    },
    {
      key: "earnings_yield_pct",
      label: "Earnings Yield",
      align: "right",
      render: (row) => formatPct(row.earnings_yield_pct),
    },
    {
      key: "dividend_yield_pct",
      label: "Dividend Yield",
      align: "right",
      render: (row) => formatPct(row.dividend_yield_pct),
    },
    {
      key: "quality",
      label: "Qualidade",
      render: (row) => (
        <span className={`rounded-full px-2 py-1 text-xs font-medium ${qualityBadge(row.quality)}`}>
          {row.quality ?? "—"}
        </span>
      ),
    },
  ];

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
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="ROE agregado" value={formatPct(etf.roe_pct)} />
          <MetricCard label="Earnings yield" value={formatPct(etf.earnings_yield_pct)} />
          <MetricCard label="Dividend yield" value={formatPct(etf.dividend_yield_pct)} />
          <MetricCard
            label="Shareholder yield"
            value={formatPct(etf.shareholder_yield_pct)}
            hint={`Cobertura limpa: ${formatPct(etf.clean_coverage_pct, 0)}`}
          />
        </div>
      ) : (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
          Este ETF ainda não tem métricas calculadas no banco.
        </div>
      )}

      <div>
        <h3 className="mb-3 text-lg font-semibold text-slate-900">Top 10 ativos</h3>
        <DataTable
          columns={columns}
          rows={holdings}
          emptyMessage="Nenhum ativo com dados para este ETF."
        />
      </div>
    </div>
  );
}
