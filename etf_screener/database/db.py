from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from etf_screener.config import DB_PATH


class Database:
    """Acesso ao SQLite central do projeto."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DB_PATH

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_schema(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        with self.connect() as conn:
            conn.executescript(schema_path.read_text(encoding="utf-8"))
            self._migrate(conn)
            conn.commit()

    def _migrate(self, conn: sqlite3.Connection) -> None:
        """Adiciona colunas novas em bancos já existentes."""
        holding_cols = {row[1] for row in conn.execute("PRAGMA table_info(holdings)").fetchall()}
        for col, ddl in [
            ("lei", "ALTER TABLE holdings ADD COLUMN lei TEXT"),
            ("sec_ticker", "ALTER TABLE holdings ADD COLUMN sec_ticker TEXT"),
            ("other_id", "ALTER TABLE holdings ADD COLUMN other_id TEXT"),
        ]:
            if col not in holding_cols:
                conn.execute(ddl)

        asset_cols = {row[1] for row in conn.execute("PRAGMA table_info(assets)").fetchall()}
        for col, ddl in [
            ("lei", "ALTER TABLE assets ADD COLUMN lei TEXT"),
            ("sector", "ALTER TABLE assets ADD COLUMN sector TEXT"),
            ("exchange", "ALTER TABLE assets ADD COLUMN exchange TEXT"),
        ]:
            if col not in asset_cols:
                conn.execute(ddl)

        conn.executescript(
            """
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
            """
        )

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> None:
        with self.connect() as conn:
            conn.execute(sql, params)
            conn.commit()

    def fetchone(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchall()
