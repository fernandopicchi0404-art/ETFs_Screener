from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = DATA_DIR / "output"
MAPPING_DIR = DATA_DIR / "mappings"

ROIC_BASE_URL = "https://api.roic.ai/v3.0.0"
REQUEST_INTERVAL_SECONDS = 13
MAX_RETRIES = 4

EQUITY_ASSET_CATEGORIES = {"EC", "EP"}
