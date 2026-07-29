"""Resolve a fonte preferencial de composição por ticker."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from etf_screener.config import HOLDINGS_SOURCES_PATH


@lru_cache(maxsize=1)
def load_holdings_sources() -> dict[str, Any]:
    if not HOLDINGS_SOURCES_PATH.exists():
        return {"source_priority_default": ["sec_nport"], "etfs": {}}
    return json.loads(HOLDINGS_SOURCES_PATH.read_text(encoding="utf-8"))


def source_chain_for_ticker(ticker: str, issuer: str | None = None) -> list[str]:
    """Ordem de tentativa: catálogo por ticker → padrão por gestora → SEC."""
    payload = load_holdings_sources()
    etf_cfg = (payload.get("etfs") or {}).get(ticker.upper()) or {}

    chain: list[str] = []
    preferred = etf_cfg.get("preferred_source")
    if preferred:
        chain.append(preferred)
    for source in etf_cfg.get("fallback_sources") or []:
        if source not in chain:
            chain.append(source)

    if not chain and issuer and issuer.casefold() == "vanguard":
        chain = ["vanguard_api", "sec_nport"]

    if not chain:
        chain = list(payload.get("source_priority_default") or ["sec_nport"])

    if "sec_nport" not in chain:
        chain.append("sec_nport")
    return chain


def etf_source_config(ticker: str) -> dict[str, Any]:
    payload = load_holdings_sources()
    return dict((payload.get("etfs") or {}).get(ticker.upper()) or {})
