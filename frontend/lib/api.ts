export interface EtfSummary {
  ticker: string;
  name: string;
  region: string | null;
  country: string | null;
  issuer: string | null;
  theme: string | null;
  priority: string | null;
  index_name: string | null;
  equity_positions: number | null;
  roe_pct: number | null;
  earnings_yield_pct: number | null;
  dividend_yield_pct: number | null;
  shareholder_yield_pct: number | null;
  clean_coverage_pct: number | null;
  composition_date: string | null;
  has_metrics: boolean;
}

export interface EtfDetail extends EtfSummary {
  equity_weight_pct: number | null;
  non_equity_weight_pct: number | null;
  gross_buyback_yield_pct: number | null;
  net_buyback_yield_pct: number | null;
  coverage_roe_pct: number | null;
  coverage_earnings_yield_pct: number | null;
  coverage_dividend_yield_pct: number | null;
  calculated_at: string | null;
}

export interface HoldingItem {
  position: number;
  company_name: string;
  country: string | null;
  sector: string | null;
  weight_pct: number | null;
  roe_pct: number | null;
  earnings_yield_pct: number | null;
  dividend_yield_pct: number | null;
  shareholder_yield_pct: number | null;
  quality: string | null;
  roic_symbol: string | null;
}

export interface AssetItem {
  asset_id: number;
  company_name: string;
  country: string | null;
  sector: string | null;
  roe_pct: number | null;
  earnings_yield_pct: number | null;
  dividend_yield_pct: number | null;
  shareholder_yield_pct: number | null;
  quality: string | null;
  roic_symbol: string | null;
  etf_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Erro na API: ${response.status}`);
  }
  return response.json();
}

export function getEtfs(params: Record<string, string> = {}) {
  const query = new URLSearchParams(params).toString();
  return fetchJson<EtfSummary[]>(`/api/etfs?${query}`);
}

export function getEtf(ticker: string) {
  return fetchJson<EtfDetail>(`/api/etfs/${ticker}`);
}

export function getHoldings(ticker: string, limit = 10) {
  return fetchJson<HoldingItem[]>(`/api/etfs/${ticker}/holdings?limit=${limit}`);
}

export function getAssets(params: Record<string, string> = {}) {
  const query = new URLSearchParams(params).toString();
  return fetchJson<AssetItem[]>(`/api/assets?${query}`);
}

export function getRegions() {
  return fetchJson<{ regions: string[] }>("/api/meta/regions");
}

export function getSectors() {
  return fetchJson<{ sectors: string[] }>("/api/meta/sectors");
}
