"use client";

import { useMemo, useState } from "react";
import DataTable, { Column } from "@/components/DataTable";
import { AssetItem } from "@/lib/api";
import { formatPct, qualityBadge } from "@/lib/format";

interface Props {
  initialAssets: AssetItem[];
  sectors: string[];
}

export default function AssetListClient({ initialAssets, sectors }: Props) {
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const filtered = useMemo(() => {
    let rows = [...initialAssets];
    if (search) {
      const term = search.toLowerCase();
      rows = rows.filter((row) => row.company_name.toLowerCase().includes(term));
    }
    if (sector) {
      rows = rows.filter((row) => row.sector === sector);
    }

    rows.sort((a, b) => {
      const getValue = (row: AssetItem) => {
        if (sortBy === "name") return row.company_name;
        if (sortBy === "country") return row.country ?? "";
        if (sortBy === "sector") return row.sector ?? "";
        if (sortBy === "roe") return row.roe_pct ?? -1;
        if (sortBy === "earnings_yield") return row.earnings_yield_pct ?? -1;
        if (sortBy === "dividend_yield") return row.dividend_yield_pct ?? -1;
        if (sortBy === "etf_count") return row.etf_count;
        return row.company_name;
      };
      const left = getValue(a);
      const right = getValue(b);
      if (typeof left === "number" && typeof right === "number") {
        return sortDir === "asc" ? left - right : right - left;
      }
      return sortDir === "asc"
        ? String(left).localeCompare(String(right), "pt-BR")
        : String(right).localeCompare(String(left), "pt-BR");
    });

    return rows;
  }, [initialAssets, search, sector, sortBy, sortDir]);

  const columns: Column<AssetItem>[] = [
    { key: "company_name", label: "Empresa", sortable: true },
    { key: "country", label: "País", sortable: true },
    {
      key: "sector",
      label: "Setor",
      sortable: true,
      render: (row) => row.sector ?? "—",
    },
    {
      key: "roe",
      label: "ROE",
      sortable: true,
      align: "right",
      render: (row) => formatPct(row.roe_pct),
    },
    {
      key: "earnings_yield",
      label: "Earnings Yield",
      sortable: true,
      align: "right",
      render: (row) => formatPct(row.earnings_yield_pct),
    },
    {
      key: "dividend_yield",
      label: "Dividend Yield",
      sortable: true,
      align: "right",
      render: (row) => formatPct(row.dividend_yield_pct),
    },
    {
      key: "shareholder_yield_pct",
      label: "Shareholder Yield",
      align: "right",
      render: (row) => formatPct(row.shareholder_yield_pct),
    },
    {
      key: "etf_count",
      label: "ETFs",
      sortable: true,
      align: "right",
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
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Buscar empresa..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="min-w-64 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <select
          value={sector}
          onChange={(event) => setSector(event.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todos os setores</option>
          {sectors.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <DataTable
        columns={columns}
        rows={filtered}
        sortBy={sortBy}
        sortDir={sortDir}
        onSort={(key) => {
          if (sortBy === key) {
            setSortDir(sortDir === "asc" ? "desc" : "asc");
          } else {
            setSortBy(key);
            setSortDir("asc");
          }
        }}
        emptyMessage="Nenhum ativo encontrado. Rode o seed do piloto SCHY e a API."
      />
    </div>
  );
}
