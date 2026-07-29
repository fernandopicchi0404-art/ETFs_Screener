import { getDb, pct } from "./db";
import type { AssetItem, EtfDetail, EtfSummary, HoldingItem } from "./api";
import { MIN_SITE_COVERAGE_PCT } from "./format";

type Row = Record<string, unknown>;

function asNumber(value: unknown): number | null {
  if (value === null || value === undefined) return null;
  return Number(value);
}

function asString(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  return String(value);
}

export function listEtfSummaries(options: {
  region?: string;
  priority?: string;
  search?: string;
  sortBy?: string;
  sortDir?: string;
} = {}): EtfSummary[] {
  const { region, priority, search, sortBy = "ticker", sortDir = "asc" } = options;
  let sql = `
    SELECT
      e.ticker,
      e.name,
      e.region,
      e.country,
      e.issuer,
      e.theme,
      e.priority,
      e.index_name,
      m.equity_positions,
      m.roe_aggregate,
      m.earnings_yield_aggregate,
      m.dividend_yield_aggregate,
      m.net_shareholder_yield_aggregate,
      m.net_buyback_yield_aggregate,
      m.clean_coverage_pct,
      m.composition_date,
      m.calculated_at,
      CASE WHEN m.metric_id IS NOT NULL THEN 1 ELSE 0 END AS has_metrics
    FROM etfs e
    LEFT JOIN etf_consolidated_metrics m ON m.etf_id = e.etf_id
      AND m.snapshot_id = (
        SELECT MAX(m2.snapshot_id)
        FROM etf_consolidated_metrics m2
        WHERE m2.etf_id = e.etf_id
      )
    WHERE e.status = 'active'
      AND m.clean_coverage_pct >= ?
  `;
  const params: unknown[] = [MIN_SITE_COVERAGE_PCT];

  if (region) {
    sql += " AND e.region = ?";
    params.push(region);
  }
  if (priority) {
    sql += " AND e.priority = ?";
    params.push(priority);
  }
  if (search) {
    sql += " AND (e.ticker LIKE ? OR e.name LIKE ?)";
    const term = `%${search}%`;
    params.push(term, term);
  }

  const allowedSort: Record<string, string> = {
    ticker: "e.ticker",
    name: "e.name",
    region: "e.region",
    equity_positions: "m.equity_positions",
    roe: "m.roe_aggregate",
    earnings_yield: "m.earnings_yield_aggregate",
    shareholder_yield: "m.net_shareholder_yield_aggregate",
    dividend_yield: "m.dividend_yield_aggregate",
    buyback_yield: "m.net_buyback_yield_aggregate",
    coverage: "m.clean_coverage_pct",
  };
  const sortCol = allowedSort[sortBy] ?? "e.ticker";
  const direction = sortDir.toLowerCase() === "desc" ? "DESC" : "ASC";
  sql += ` ORDER BY ${sortCol} ${direction}, e.ticker ASC`;

  const rows = getDb().prepare(sql).all(...params) as Row[];
  return rows.map((row) => ({
    ticker: String(row.ticker),
    name: String(row.name),
    region: asString(row.region),
    country: asString(row.country),
    issuer: asString(row.issuer),
    theme: asString(row.theme),
    priority: asString(row.priority),
    index_name: asString(row.index_name),
    equity_positions: asNumber(row.equity_positions),
    roe_pct: pct(asNumber(row.roe_aggregate)),
    earnings_yield_pct: pct(asNumber(row.earnings_yield_aggregate)),
    shareholder_yield_pct: pct(asNumber(row.net_shareholder_yield_aggregate)),
    dividend_yield_pct: pct(asNumber(row.dividend_yield_aggregate)),
    buyback_yield_pct: pct(asNumber(row.net_buyback_yield_aggregate)),
    clean_coverage_pct: asNumber(row.clean_coverage_pct),
    composition_date: asString(row.composition_date),
    has_metrics: Boolean(row.has_metrics),
  }));
}

export function getEtfDetail(ticker: string): EtfDetail | null {
  const row = getDb()
    .prepare(
      `
      SELECT e.ticker, e.name, e.region, e.country, e.issuer, e.theme, e.priority, e.index_name, m.*
      FROM etfs e
      LEFT JOIN etf_consolidated_metrics m ON m.etf_id = e.etf_id
        AND m.snapshot_id = (
          SELECT MAX(m2.snapshot_id) FROM etf_consolidated_metrics m2 WHERE m2.etf_id = e.etf_id
        )
      WHERE e.ticker = ?
    `,
    )
    .get(ticker.toUpperCase()) as Row | undefined;

  if (!row) return null;

  return {
    ticker: String(row.ticker),
    name: String(row.name),
    region: asString(row.region),
    country: asString(row.country),
    issuer: asString(row.issuer),
    theme: asString(row.theme),
    priority: asString(row.priority),
    index_name: asString(row.index_name),
    equity_positions: asNumber(row.equity_positions),
    roe_pct: pct(asNumber(row.roe_aggregate)),
    earnings_yield_pct: pct(asNumber(row.earnings_yield_aggregate)),
    shareholder_yield_pct: pct(asNumber(row.net_shareholder_yield_aggregate)),
    dividend_yield_pct: pct(asNumber(row.dividend_yield_aggregate)),
    buyback_yield_pct: pct(asNumber(row.net_buyback_yield_aggregate)),
    clean_coverage_pct: asNumber(row.clean_coverage_pct),
    composition_date: asString(row.composition_date),
    has_metrics: row.metric_id != null,
    equity_weight_pct: asNumber(row.equity_weight_original_pct),
    non_equity_weight_pct: asNumber(row.non_equity_weight_original_pct),
    gross_buyback_yield_pct: pct(asNumber(row.gross_buyback_yield_aggregate)),
    net_buyback_yield_pct: pct(asNumber(row.net_buyback_yield_aggregate)),
    coverage_roe_pct: asNumber(row.coverage_roe_pct),
    coverage_earnings_yield_pct: asNumber(row.coverage_earnings_yield_pct),
    coverage_dividend_yield_pct: asNumber(row.coverage_dividend_yield_pct),
    calculated_at: asString(row.calculated_at),
  };
}

export function listEtfHoldings(ticker: string, limit: number | null = 10): HoldingItem[] {
  const etf = getDb()
    .prepare("SELECT etf_id FROM etfs WHERE ticker = ?")
    .get(ticker.toUpperCase());
  if (!etf) return [];

  let sql = `
    SELECT h.position, a.canonical_name AS company_name, COALESCE(af.sector, a.sector) AS sector,
      h.country, h.weight_normalized, af.roe, af.earnings_yield, af.dividend_yield,
      af.net_shareholder_yield, af.net_buyback_yield, af.quality, af.roic_symbol
    FROM holdings h
    JOIN composition_snapshots cs ON cs.snapshot_id = h.snapshot_id
    JOIN etfs e ON e.etf_id = cs.etf_id
    LEFT JOIN assets a ON a.asset_id = h.asset_id
    LEFT JOIN asset_fundamentals af ON af.asset_id = a.asset_id
    WHERE e.ticker = ? AND h.included_in_equity_analysis = 1
      AND cs.snapshot_id = (SELECT MAX(cs2.snapshot_id) FROM composition_snapshots cs2 WHERE cs2.etf_id = e.etf_id)
    ORDER BY h.weight_normalized DESC, h.position ASC
  `;
  const params: unknown[] = [ticker.toUpperCase()];
  if (limit !== null) {
    sql += " LIMIT ?";
    params.push(limit);
  }

  const rows = getDb().prepare(sql).all(...params) as Row[];
  return rows.map((row) => ({
    position: Number(row.position),
    company_name: String(row.company_name),
    country: asString(row.country),
    sector: asString(row.sector),
    weight_pct:
      row.weight_normalized != null ? Math.round(Number(row.weight_normalized) * 100) / 100 : null,
    roe_pct: pct(asNumber(row.roe)),
    earnings_yield_pct: pct(asNumber(row.earnings_yield)),
    shareholder_yield_pct: pct(asNumber(row.net_shareholder_yield)),
    dividend_yield_pct: pct(asNumber(row.dividend_yield)),
    buyback_yield_pct: pct(asNumber(row.net_buyback_yield)),
    quality: asString(row.quality),
    roic_symbol: asString(row.roic_symbol),
  }));
}

export function listAssets(options: {
  country?: string;
  sector?: string;
  quality?: string;
  search?: string;
  sortBy?: string;
  sortDir?: string;
} = {}): AssetItem[] {
  const { country, sector, quality, search, sortBy = "name", sortDir = "asc" } = options;
  let sql = `
    SELECT a.asset_id, a.canonical_name AS company_name, a.country,
      COALESCE(af.sector, a.sector) AS sector, af.roe, af.earnings_yield, af.dividend_yield,
      af.net_shareholder_yield, af.net_buyback_yield, af.quality, af.roic_symbol,
      (SELECT COUNT(DISTINCT cs.etf_id) FROM holdings h2
        JOIN composition_snapshots cs ON cs.snapshot_id = h2.snapshot_id
        WHERE h2.asset_id = a.asset_id AND h2.included_in_equity_analysis = 1) AS etf_count
    FROM assets a
    JOIN asset_fundamentals af ON af.asset_id = a.asset_id
    WHERE 1 = 1
  `;
  const params: unknown[] = [];

  if (country) {
    sql += " AND a.country = ?";
    params.push(country);
  }
  if (sector) {
    sql += " AND COALESCE(af.sector, a.sector) = ?";
    params.push(sector);
  }
  if (quality) {
    sql += " AND af.quality = ?";
    params.push(quality);
  }
  if (search) {
    sql += " AND a.canonical_name LIKE ?";
    params.push(`%${search}%`);
  }

  const allowedSort: Record<string, string> = {
    name: "a.canonical_name",
    country: "a.country",
    sector: "sector",
    roe: "af.roe",
    earnings_yield: "af.earnings_yield",
    dividend_yield: "af.dividend_yield",
    etf_count: "etf_count",
  };
  const sortCol = allowedSort[sortBy] ?? "a.canonical_name";
  const direction = sortDir.toLowerCase() === "desc" ? "DESC" : "ASC";
  sql += ` ORDER BY ${sortCol} ${direction}, a.canonical_name ASC`;

  const rows = getDb().prepare(sql).all(...params) as Row[];
  return rows.map((row) => ({
    asset_id: Number(row.asset_id),
    company_name: String(row.company_name),
    country: asString(row.country),
    sector: asString(row.sector),
    roe_pct: pct(asNumber(row.roe)),
    earnings_yield_pct: pct(asNumber(row.earnings_yield)),
    shareholder_yield_pct: pct(asNumber(row.net_shareholder_yield)),
    dividend_yield_pct: pct(asNumber(row.dividend_yield)),
    buyback_yield_pct: pct(asNumber(row.net_buyback_yield)),
    quality: asString(row.quality),
    roic_symbol: asString(row.roic_symbol),
    etf_count: Number(row.etf_count ?? 0),
  }));
}

export function listRegions(): string[] {
  const rows = getDb()
    .prepare(
      "SELECT DISTINCT region FROM etfs WHERE region IS NOT NULL AND status = 'active' ORDER BY region",
    )
    .all() as Row[];
  return rows.map((row) => String(row.region));
}

export function listSectors(): string[] {
  const rows = getDb()
    .prepare(
      `SELECT DISTINCT COALESCE(af.sector, a.sector) AS sector
       FROM assets a JOIN asset_fundamentals af ON af.asset_id = a.asset_id
       WHERE COALESCE(af.sector, a.sector) IS NOT NULL ORDER BY sector`,
    )
    .all() as Row[];
  return rows.map((row) => String(row.sector));
}
