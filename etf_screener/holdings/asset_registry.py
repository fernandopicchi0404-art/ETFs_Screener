from __future__ import annotations

import re

from etf_screener.models import Holding

INVALID_CUSIP = "000000000"


def build_asset_key(holding: Holding) -> str:
    """Chave estável para deduplicar empresas entre ETFs."""
    if holding.isin:
        return f"ISIN:{holding.isin.upper()}"
    if holding.cusip and holding.cusip != INVALID_CUSIP:
        return f"CUSIP:{holding.cusip.upper()}"
    country = (holding.country or "XX").upper()
    name = re.sub(r"\s+", " ", holding.name.casefold().strip())
    return f"NAME:{country}:{name}"


def upsert_asset(conn, holding: Holding, now: str) -> int:
    asset_key = build_asset_key(holding)
    cusip = holding.cusip if holding.cusip != INVALID_CUSIP else None

    row = conn.execute("SELECT asset_id FROM assets WHERE asset_key = ?", (asset_key,)).fetchone()
    if row:
        asset_id = int(row[0])
        conn.execute(
            """
            UPDATE assets
            SET canonical_name = ?, isin = COALESCE(?, isin), cusip = COALESCE(?, cusip),
                country = COALESCE(?, country), lei = COALESCE(?, lei), updated_at = ?
            WHERE asset_id = ?
            """,
            (
                holding.name,
                holding.isin,
                cusip,
                holding.country or None,
                holding.lei,
                now,
                asset_id,
            ),
        )
        return asset_id

    # Mesmo CUSIP/ISIN pode chegar com chaves diferentes (ex.: NAME antes de ISIN corrigido).
    if cusip:
        row = conn.execute("SELECT asset_id FROM assets WHERE cusip = ?", (cusip,)).fetchone()
        if row:
            asset_id = int(row[0])
            conn.execute(
                """
                UPDATE assets
                SET asset_key = ?, canonical_name = ?, isin = COALESCE(?, isin),
                    country = COALESCE(?, country), lei = COALESCE(?, lei), updated_at = ?
                WHERE asset_id = ?
                """,
                (
                    asset_key,
                    holding.name,
                    holding.isin,
                    holding.country or None,
                    holding.lei,
                    now,
                    asset_id,
                ),
            )
            return asset_id

    if holding.isin:
        row = conn.execute("SELECT asset_id FROM assets WHERE isin = ?", (holding.isin,)).fetchone()
        if row:
            asset_id = int(row[0])
            conn.execute(
                """
                UPDATE assets
                SET asset_key = ?, canonical_name = ?, cusip = COALESCE(?, cusip),
                    country = COALESCE(?, country), lei = COALESCE(?, lei), updated_at = ?
                WHERE asset_id = ?
                """,
                (
                    asset_key,
                    holding.name,
                    cusip,
                    holding.country or None,
                    holding.lei,
                    now,
                    asset_id,
                ),
            )
            return asset_id

    cursor = conn.execute(
        """
        INSERT INTO assets (asset_key, canonical_name, isin, cusip, country, lei, roic_symbol, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
        """,
        (
            asset_key,
            holding.name,
            holding.isin,
            cusip,
            holding.country or None,
            holding.lei,
            now,
            now,
        ),
    )
    return int(cursor.lastrowid)


def link_holdings_to_assets(conn, snapshot_id: int, now: str) -> int:
    rows = conn.execute(
        "SELECT holding_id, name_raw, country, cusip, isin, lei, sec_ticker, other_id FROM holdings WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchall()
    linked = 0
    for row in rows:
        holding = Holding(
            etf="",
            position=0,
            name=row["name_raw"],
            asset_category="EC",
            asset_type="equity",
            country=row["country"] or "",
            weight_original=0.0,
            cusip=row["cusip"],
            isin=row["isin"],
            lei=row["lei"],
            sec_ticker=row["sec_ticker"],
            other_id=row["other_id"],
            included_in_equity_analysis=True,
        )
        asset_id = upsert_asset(conn, holding, now)
        conn.execute("UPDATE holdings SET asset_id = ? WHERE holding_id = ?", (asset_id, row["holding_id"]))
        linked += 1
    return linked
