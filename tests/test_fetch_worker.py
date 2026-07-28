from __future__ import annotations

from pathlib import Path

from etf_screener.fundamentals.fetch_worker import pending_verified_fetches
from etf_screener.database.db import Database


def test_pending_assets_excludes_completed(tmp_path: Path):
    db_path = tmp_path / "test.sqlite"
    db = Database(db_path)
    db.init_schema()
    now = "2026-07-27T00:00:00+00:00"
    with db.connect() as conn:
        conn.execute(
            """
            INSERT INTO etfs (
                ticker, name, issuer, region, country, theme, priority, index_name,
                sec_registrant_cik, sec_series_match, status, created_at, updated_at
            ) VALUES ('SCHY', 'Schwab International Dividend Equity ETF', 'Schwab',
                'international', NULL, 'dividend', 'P1', 'test', NULL, 'SCHY', 'active', ?, ?)
            """,
            (now, now),
        )
        etf_id = conn.execute("SELECT etf_id FROM etfs WHERE ticker='SCHY'").fetchone()[0]
        conn.execute(
            """
            INSERT INTO composition_snapshots (
                etf_id, composition_date, report_period_end, filing_date, accession_number,
                source_url, raw_path, methodology_version, extracted_at, status,
                total_positions, equity_positions, total_weight_pct, equity_weight_pct
            ) VALUES (?, '2026-05-31', '2026-08-31', '2026-07-24', 'acc-test', NULL, NULL,
                '1.0', ?, 'ok', 2, 2, 100, 100)
            """,
            (etf_id, now),
        )
        snapshot_id = conn.execute(
            "SELECT snapshot_id FROM composition_snapshots WHERE accession_number='acc-test'"
        ).fetchone()[0]
        conn.execute(
            """
            INSERT INTO assets (asset_key, canonical_name, isin, cusip, country, roic_symbol, created_at, updated_at)
            VALUES ('ISIN:CH1', 'Nestle SA', 'CH1', NULL, 'CH', NULL, ?, ?)
            """,
            (now, now),
        )
        asset_id = conn.execute("SELECT asset_id FROM assets WHERE asset_key='ISIN:CH1'").fetchone()[0]
        conn.execute(
            """
            INSERT INTO holdings (
                snapshot_id, asset_id, position, name_raw, asset_category, asset_type, country,
                cusip, isin, weight_original, weight_normalized, market_value_usd,
                included_in_equity_analysis, exclusion_reason
            ) VALUES (?, ?, 1, 'Nestle SA', 'EC', 'equity', 'CH', NULL, 'CH1', 5.0, 5.0, 1000, 1, NULL)
            """,
            (snapshot_id, asset_id),
        )
        conn.execute(
            """
            INSERT INTO asset_identities (
                asset_id, roic_symbol, mapping_method, mapping_status, validated_at,
                methodology_version, match_isin, match_cusip, match_country, candidate_name,
                error_message, requests_used
            ) VALUES (?, 'SIX:NESN', 'isin', 'verified_isin', ?, '1.0', 'CH1', NULL, 'CH', 'Nestle SA', NULL, 1)
            """,
            (asset_id, now),
        )
        conn.execute(
            """
            INSERT INTO asset_fundamental_fetches (
                asset_id, roic_symbol, mapping_status, status, fiscal_year, price_date,
                fetched_at, error_tag, error_message, requests_used
            ) VALUES (?, 'SIX:NESN', 'verified_isin', 'ok', 2025, '2026-07-01', ?, NULL, NULL, 4)
            """,
            (asset_id, now),
        )
        conn.commit()

    pending = pending_verified_fetches(db, priority="P1")
    assert pending == []
