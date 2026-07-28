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

