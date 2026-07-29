from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CATALOG_DIR = DATA_DIR / "catalog"
RAW_DIR = DATA_DIR / "raw"
SEC_RAW_DIR = RAW_DIR / "sec"
VANGUARD_RAW_DIR = RAW_DIR / "vanguard"
CACHE_DIR = DATA_DIR / "cache"
DATABASE_DIR = DATA_DIR / "database"
DB_PATH = DATABASE_DIR / "etf_screener.sqlite"
OUTPUT_DIR = DATA_DIR / "output"
EXPORTS_DIR = DATA_DIR / "exports"
RUNS_DIR = DATA_DIR / "runs"
MAPPING_DIR = DATA_DIR / "mappings"

ETF_UNIVERSE_PATH = DATA_DIR / "etf_universe.json"
SEC_ISSUER_DEFAULTS_PATH = CATALOG_DIR / "sec_issuer_defaults.json"
HOLDINGS_SOURCES_PATH = CATALOG_DIR / "holdings_sources.json"
METHODOLOGY_PATH = CATALOG_DIR / "methodology.json"

ROIC_BASE_URL = "https://api.roic.ai/v3.0.0"
# Intervalo padrão legado (plano gratuito). Produção usa roic/settings.py + .env.
REQUEST_INTERVAL_SECONDS = 13
MAX_RETRIES = 4

SEC_DATA_API_BASE = "https://data.sec.gov"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"
SEC_EFTS_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_USER_AGENT = "ETFs_Screener research contact@example.com"

EQUITY_ASSET_CATEGORIES = {"EC", "EP"}
METHODOLOGY_VERSION = "1.0"
