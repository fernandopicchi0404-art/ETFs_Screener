export function formatPct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined) return "—";
  return `${value.toFixed(digits)}%`;
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString("pt-BR");
}

export function regionLabel(region: string | null): string {
  const labels: Record<string, string> = {
    global: "Global",
    international: "Internacional",
    developed_ex_us: "Desenvolvidos (ex-EUA)",
    emerging: "Emergentes",
    europe: "Europa",
    asia_pacific: "Ásia-Pacífico",
    us: "EUA",
    dividend: "Dividendos",
    value: "Valor",
    quality: "Qualidade",
    small_cap: "Small Cap",
  };
  if (!region) return "—";
  return labels[region] ?? region;
}

export function coverageColor(pct: number | null): string {
  if (pct === null) return "bg-slate-200";
  if (pct >= 90) return "bg-emerald-500";
  if (pct >= 70) return "bg-amber-400";
  return "bg-rose-500";
}

export function qualityBadge(quality: string | null): string {
  if (quality === "OK") return "bg-emerald-100 text-emerald-800";
  if (quality === "WARNING") return "bg-amber-100 text-amber-800";
  if (quality === "BLOCKER") return "bg-rose-100 text-rose-800";
  return "bg-slate-100 text-slate-600";
}
