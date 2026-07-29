"use client";

import { useState } from "react";
import DataTable, { Column } from "@/components/DataTable";
import { getHoldings, HoldingItem } from "@/lib/api";
import { formatPct, qualityBadge } from "@/lib/format";

const INITIAL_LIMIT = 10;
const EXPAND_STEP = 50;

interface Props {
  ticker: string;
  initialHoldings: HoldingItem[];
  totalCount: number;
}

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
    key: "shareholder_yield_pct",
    label: "Shareholder Yield",
    align: "right",
    render: (row) => formatPct(row.shareholder_yield_pct),
  },
  {
    key: "dividend_yield_pct",
    label: "Dividend Yield",
    align: "right",
    render: (row) => formatPct(row.dividend_yield_pct),
  },
  {
    key: "buyback_yield_pct",
    label: "Buyback Yield",
    align: "right",
    render: (row) => formatPct(row.buyback_yield_pct),
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

export default function EtfHoldingsTable({ ticker, initialHoldings, totalCount }: Props) {
  const [holdings, setHoldings] = useState(initialHoldings);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [hasMore, setHasMore] = useState(initialHoldings.length < totalCount);
  const visible = holdings.length;

  async function handleExpand() {
    const nextLimit = Math.min(visible + EXPAND_STEP, totalCount);
    setLoading(true);
    setError(null);
    try {
      const next = await getHoldings(ticker, nextLimit);
      setHoldings(next);
      // Para se já mostrou tudo ou a API devolveu menos que o pedido.
      setHasMore(next.length < totalCount && next.length >= nextLimit);
    } catch {
      setError("Não foi possível carregar mais ativos. Tente de novo.");
    } finally {
      setLoading(false);
    }
  }

  const title =
    totalCount <= INITIAL_LIMIT
      ? `Ativos (${visible})`
      : `Ativos (${visible} de ${totalCount})`;

  return (
    <div>
      <h3 className="mb-3 text-lg font-semibold text-slate-900">{title}</h3>
      <DataTable
        columns={columns}
        rows={holdings}
        emptyMessage="Nenhum ativo com dados para este ETF."
      />
      {hasMore && (
        <div className="mt-4 flex flex-col items-start gap-2">
          <button
            type="button"
            onClick={handleExpand}
            disabled={loading}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Carregando…" : "Mostrar mais 50"}
          </button>
          {error && <p className="text-sm text-rose-600">{error}</p>}
        </div>
      )}
    </div>
  );
}
