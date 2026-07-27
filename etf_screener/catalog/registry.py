"""Catálogo de ETFs e sincronização com o banco."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from etf_screener.config import ETF_UNIVERSE_PATH, SEC_ISSUER_DEFAULTS_PATH
from etf_screener.database.db import Database


def _now() -> str:
  return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_etf_universe(path: Path | None = None) -> list[dict[str, Any]]:
  payload = json.loads((path or ETF_UNIVERSE_PATH).read_text(encoding="utf-8"))
  return payload["etfs"]


def load_sec_issuer_defaults() -> dict[str, Any]:
  if not SEC_ISSUER_DEFAULTS_PATH.exists():
    return {}
  payload = json.loads(SEC_ISSUER_DEFAULTS_PATH.read_text(encoding="utf-8"))
  return payload.get("issuers", {})


def resolve_sec_registrant_cik(issuer: str | None) -> str | None:
  if not issuer:
    return None
  defaults = load_sec_issuer_defaults()
  entry = defaults.get(issuer)
  if not entry:
    return None
  return entry.get("sec_registrant_cik")


def sync_etf_registry(db: Database | None = None) -> int:
  """Carrega o universo curado (50 ETFs) na tabela etfs."""
  database = db or Database()
  database.init_schema()
  now = _now()
  count = 0

  with database.connect() as conn:
    for item in load_etf_universe():
      ticker = item["ticker"].upper()
      sec_cik = resolve_sec_registrant_cik(item.get("issuer"))
      conn.execute(
        """
        INSERT INTO etfs (
          ticker, name, issuer, region, country, theme, priority, index_name,
          sec_registrant_cik, sec_series_match, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
          name = excluded.name,
          issuer = excluded.issuer,
          region = excluded.region,
          country = excluded.country,
          theme = excluded.theme,
          priority = excluded.priority,
          index_name = excluded.index_name,
          sec_registrant_cik = COALESCE(excluded.sec_registrant_cik, etfs.sec_registrant_cik),
          sec_series_match = excluded.sec_series_match,
          status = 'active',
          updated_at = excluded.updated_at
        """,
        (
          ticker,
          item["name"],
          item.get("issuer"),
          item.get("region"),
          item.get("country"),
          item.get("theme"),
          item.get("priority"),
          item.get("index"),
          sec_cik,
          item["name"],
          now,
          now,
        ),
      )
      count += 1
    conn.commit()

  return count


def get_etf_by_ticker(db: Database, ticker: str) -> dict[str, Any] | None:
  row = db.fetchone("SELECT * FROM etfs WHERE ticker = ?", (ticker.upper(),))
  return dict(row) if row else None


def list_etfs(
  db: Database,
  priority: str | None = None,
  tickers: list[str] | None = None,
) -> list[dict[str, Any]]:
  sql = "SELECT * FROM etfs WHERE status = 'active'"
  params: list[Any] = []
  if priority:
    sql += " AND priority = ?"
    params.append(priority)
  if tickers:
    placeholders = ",".join("?" for _ in tickers)
    sql += f" AND ticker IN ({placeholders})"
    params.extend(t.upper() for t in tickers)
  sql += " ORDER BY ticker"
  return [dict(row) for row in db.fetchall(sql, params)]
