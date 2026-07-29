"use client";

import { useMemo, useState } from "react";
import DataTable, { Column } from "@/components/DataTable";
import { PremiseInput } from "@/components/EtfPremisesControls";
import { CoverageBar } from "@/components/MetricCard";
import { EtfSummary } from "@/lib/api";
import { calculateExpectedReturn } from "@/lib/expectedReturn";
import { formatPct, regionLabel } from "@/lib/format";
import { useEtfPremises } from "@/lib/useEtfPremises";

interface Props {
  initialEtfs: EtfSummary[];
  regions: string[];
}

export default function EtfListClient({ initialEtfs, regions }: Props) {
  const [search, setSearch] = useState("");
  const [region, setRegion] = useState("");
  const [sortBy, setSortBy] = useState("ticker");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const { getPremises, setPremises } = useEtfPremises();

  const filtered = useMemo(() => {
    let rows = [...initialEtfs];
    if (search) {
      const term = search.toLowerCase();
      rows = rows.filter(
        (row) =>
          row.ticker.toLowerCase().includes(term) ||
          row.name.toLowerCase().includes(term),
      );
    }
    if (region) {
      rows = rows.filter((row) => row.region === region);
    }

    rows.sort((a, b) => {
      const getValue = (row: EtfSummary) => {
        if (sortBy === "ticker") return row.ticker;
        if (sortBy === "name") return row.name;
        if (sortBy === "region") return row.region ?? "";
        if (sortBy === "equity_positions") return row.equity_positions ?? -1;
        if (sortBy === "roe") return row.roe_pct ?? -1;
        if (sortBy === "earnings_yield") return row.earnings_yield_pct ?? -1;
        if (sortBy === "shareholder_yield") return row.shareholder_yield_pct ?? -1;
        if (sortBy === "dividend_yield") return row.dividend_yield_pct ?? -1;
        if (sortBy === "buyback_yield") return row.buyback_yield_pct ?? -1;
        if (sortBy === "coverage") return row.clean_coverage_pct ?? -1;
        if (sortBy === "inflation" || sortBy === "real_growth") {
          const premises = getPremises(row.ticker);
          return sortBy === "inflation" ? premises.inflationPct : premises.realGrowthPct;
        }
        if (sortBy === "expected_return" || sortBy === "expected_real_return") {
          const result = calculateExpectedReturn(
            row.roe_pct,
            row.earnings_yield_pct,
            getPremises(row.ticker),
          );
          return sortBy === "expected_return"
            ? (result.expectedReturnPct ?? -1)
            : (result.expectedRealReturnPct ?? -1);
        }
        return row.ticker;
      };
      const left = getValue(a);
      const right = getValue(b);
      if (typeof left === "number" && typeof right === "number") {
        return sortDir === "asc" ? left - right : right - left;
      }
      return sortDir === "asc"
        ? String(left).localeCompare(String(right))
        : String(right).localeCompare(String(left));
    });

    return rows;
  }, [getPremises, initialEtfs, region, search, sortBy, sortDir]);

  const columns: Column<EtfSummary>[] = [
    { key: "ticker", label: "Ticker", sortable: true },
    { key: "name", label: "Nome", sortable: true },
    {
      key: "region",
      label: "Geografia",
      sortable: true,
      render: (row) => regionLabel(row.region),
    },
    {
      key: "equity_positions",
      label: "Ativos",
      sortable: true,
      align: "right",
      render: (row) => (row.has_metrics ? row.equity_positions ?? "—" : "—"),
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
      key: "shareholder_yield",
      label: "Shareholder Yield",
      sortable: true,
      align: "right",
      render: (row) => formatPct(row.shareholder_yield_pct),
    },
    {
      key: "dividend_yield",
      label: "Dividend Yield",
      sortable: true,
      align: "right",
      render: (row) => formatPct(row.dividend_yield_pct),
    },
    {
      key: "buyback_yield",
      label: "Buyback Yield",
      sortable: true,
      align: "right",
      render: (row) => formatPct(row.buyback_yield_pct),
    },
    {
      key: "inflation",
      label: "Inflação",
      sortable: true,
      align: "right",
      render: (row) => (
        <PremiseInput
          value={getPremises(row.ticker).inflationPct}
          ariaLabel={`Inflação de ${row.ticker}`}
          onChange={(inflationPct) => setPremises(row.ticker, { inflationPct })}
        />
      ),
    },
    {
      key: "real_growth",
      label: "Cresc. real",
      sortable: true,
      align: "right",
      render: (row) => (
        <PremiseInput
          value={getPremises(row.ticker).realGrowthPct}
          ariaLabel={`Crescimento real de ${row.ticker}`}
          onChange={(realGrowthPct) => setPremises(row.ticker, { realGrowthPct })}
        />
      ),
    },
    {
      key: "expected_return",
      label: "Retorno esp.",
      sortable: true,
      align: "right",
      render: (row) => {
        const result = calculateExpectedReturn(
          row.roe_pct,
          row.earnings_yield_pct,
          getPremises(row.ticker),
        );
        return formatPct(result.expectedReturnPct);
      },
    },
    {
      key: "expected_real_return",
      label: "Retorno real esp.",
      sortable: true,
      align: "right",
      render: (row) => {
        const result = calculateExpectedReturn(
          row.roe_pct,
          row.earnings_yield_pct,
          getPremises(row.ticker),
        );
        return formatPct(result.expectedRealReturnPct);
      },
    },
    {
      key: "coverage",
      label: "Cobertura",
      sortable: true,
      render: (row) =>
        row.has_metrics ? <CoverageBar value={row.clean_coverage_pct} /> : "—",
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Buscar por ticker ou nome..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="min-w-64 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <select
          value={region}
          onChange={(event) => setRegion(event.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todas as geografias</option>
          {regions.map((item) => (
            <option key={item} value={item}>
              {regionLabel(item)}
            </option>
          ))}
        </select>
      </div>

      <p className="text-xs text-slate-500">
        Inflação e crescimento real padrão: 3% e 2%. Edite por ETF — o valor fica salvo neste
        navegador. Retorno esperado = (earnings yield × payout) + crescimento, com payout =
        1 − (crescimento ÷ ROE).
      </p>

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
        rowHref={(row) => `/etf/${row.ticker}`}
        emptyMessage="Nenhum ETF encontrado. Verifique se a API está rodando e se o banco foi carregado."
      />
    </div>
  );
}
