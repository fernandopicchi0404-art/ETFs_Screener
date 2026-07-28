"use client";

import DataTable, { Column } from "@/components/DataTable";
import { HoldingItem } from "@/lib/api";
import { formatPct, qualityBadge } from "@/lib/format";

interface Props {
  holdings: HoldingItem[];
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

export default function EtfHoldingsTable({ holdings }: Props) {
  return (
    <DataTable
      columns={columns}
      rows={holdings}
      emptyMessage="Nenhum ativo com dados para este ETF."
    />
  );
}
