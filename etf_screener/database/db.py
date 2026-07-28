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
        ]:
            if col not in asset_cols:
                conn.execute(ddl)

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
