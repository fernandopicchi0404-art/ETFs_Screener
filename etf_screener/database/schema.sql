-- Schema v1: composição de ETFs (fase 1). Fundamentos e preços entram em migrações futuras.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS etfs (
    etf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    issuer TEXT,
    region TEXT,
    country TEXT,
    theme TEXT,
    priority TEXT,
    index_name TEXT,
    sec_registrant_cik TEXT,
    sec_series_match TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_key TEXT NOT NULL UNIQUE,
    canonical_name TEXT NOT NULL,
    isin TEXT,
    cusip TEXT,
    country TEXT,
    roic_symbol TEXT,
    sector TEXT,
    exchange TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_isin ON assets(isin) WHERE isin IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_cusip ON assets(cusip) WHERE cusip IS NOT NULL;

CREATE TABLE IF NOT EXISTS composition_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    etf_id INTEGER NOT NULL REFERENCES etfs(etf_id),
    composition_date TEXT,
    report_period_end TEXT,
    filing_date TEXT,
    accession_number TEXT NOT NULL,
    source_url TEXT,
    raw_path TEXT,
    methodology_version TEXT NOT NULL,
    extracted_at TEXT NOT NULL,
    status TEXT NOT NULL,
    total_positions INTEGER NOT NULL DEFAULT 0,
    equity_positions INTEGER NOT NULL DEFAULT 0,
    total_weight_pct REAL,
    equity_weight_pct REAL,
    UNIQUE(etf_id, accession_number)
);

CREATE TABLE IF NOT EXISTS holdings (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL REFERENCES composition_snapshots(snapshot_id),
    asset_id INTEGER REFERENCES assets(asset_id),
    position INTEGER NOT NULL,
    name_raw TEXT NOT NULL,
    asset_category TEXT,
    asset_type TEXT,
    country TEXT,
    cusip TEXT,
    isin TEXT,
    weight_original REAL NOT NULL,
    weight_normalized REAL,
    market_value_usd REAL,
    included_in_equity_analysis INTEGER NOT NULL DEFAULT 0,
    exclusion_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_holdings_snapshot ON holdings(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_holdings_asset ON holdings(asset_id);

CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    etf_tickers TEXT NOT NULL,
    summary_json TEXT,
    notes TEXT
);

-- Preparado para fase 2: preços históricos independentes dos fundamentos.
CREATE TABLE IF NOT EXISTS prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL REFERENCES assets(asset_id),
    price_date TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    UNIQUE(asset_id, price_date, source)
);

CREATE INDEX IF NOT EXISTS idx_prices_asset_date ON prices(asset_id, price_date);

-- Fase 2: status de levantamento ROIC por ativo (fundamentos + preço latest).
CREATE TABLE IF NOT EXISTS asset_fundamental_fetches (
    fetch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL UNIQUE REFERENCES assets(asset_id),
    roic_symbol TEXT,
    mapping_status TEXT,
    status TEXT NOT NULL,
    fiscal_year INTEGER,
    price_date TEXT,
    fetched_at TEXT NOT NULL,
    error_tag TEXT,
    error_message TEXT,
    requests_used INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_asset_fetches_status ON asset_fundamental_fetches(status);

-- Identidade ROIC validada (global por ativo).
CREATE TABLE IF NOT EXISTS asset_identities (
    identity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL UNIQUE REFERENCES assets(asset_id),
    roic_symbol TEXT,
    mapping_method TEXT NOT NULL,
    mapping_status TEXT NOT NULL,
    validated_at TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    match_isin TEXT,
    match_cusip TEXT,
    match_country TEXT,
    candidate_name TEXT,
    error_message TEXT,
    requests_used INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_asset_identities_status ON asset_identities(mapping_status);

-- Fase 3: métricas calculadas por ativo (global, reutilizável entre ETFs).
CREATE TABLE IF NOT EXISTS asset_fundamentals (
    fundamental_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL UNIQUE REFERENCES assets(asset_id),
    roic_symbol TEXT,
    exchange TEXT,
    sector TEXT,
    industry TEXT,
    mapping_status TEXT,
    fundamental_currency TEXT,
    price_currency TEXT,
    fiscal_year INTEGER,
    fiscal_year_end TEXT,
    price_date TEXT,
    price REAL,
    earnings_for_common REAL,
    diluted_shares REAL,
    diluted_eps REAL,
    common_equity_average REAL,
    roe REAL,
    roe_method TEXT,
    earnings_yield REAL,
    dividend_yield REAL,
    gross_buyback_yield REAL,
    net_buyback_yield REAL,
    gross_shareholder_yield REAL,
    net_shareholder_yield REAL,
    quality TEXT NOT NULL DEFAULT 'OK',
    tags TEXT,
    notes TEXT,
    methodology_version TEXT NOT NULL,
    calculated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_asset_fundamentals_quality ON asset_fundamentals(quality);

-- Fase 3: métricas consolidadas por ETF e snapshot de composição.
CREATE TABLE IF NOT EXISTS etf_consolidated_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    etf_id INTEGER NOT NULL REFERENCES etfs(etf_id),
    snapshot_id INTEGER NOT NULL REFERENCES composition_snapshots(snapshot_id),
    equity_positions INTEGER NOT NULL DEFAULT 0,
    equity_weight_original_pct REAL,
    non_equity_weight_original_pct REAL,
    target_clean_coverage_pct REAL,
    clean_coverage_pct REAL,
    target_clean_coverage_met INTEGER NOT NULL DEFAULT 0,
    roe_aggregate REAL,
    earnings_yield_aggregate REAL,
    dividend_yield_aggregate REAL,
    gross_buyback_yield_aggregate REAL,
    net_buyback_yield_aggregate REAL,
    gross_shareholder_yield_aggregate REAL,
    net_shareholder_yield_aggregate REAL,
    earnings_yield_mean_covered REAL,
    dividend_yield_mean_covered REAL,
    gross_buyback_yield_mean_covered REAL,
    gross_shareholder_yield_mean_covered REAL,
    coverage_roe_pct REAL,
    coverage_earnings_yield_pct REAL,
    coverage_dividend_yield_pct REAL,
    coverage_buyback_yield_pct REAL,
    coverage_shareholder_yield_pct REAL,
    composition_date TEXT,
    calculated_at TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    UNIQUE(etf_id, snapshot_id)
);

CREATE INDEX IF NOT EXISTS idx_etf_metrics_etf ON etf_consolidated_metrics(etf_id);

