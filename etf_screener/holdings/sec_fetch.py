from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

from etf_screener.config import SEC_RAW_DIR, SEC_USER_AGENT
from etf_screener.holdings.sec_discovery import NportFilingRef


def download_nport_xml(filing: NportFilingRef, ticker: str) -> Path:
    """Baixa o XML bruto e preserva o arquivo para auditoria."""
    accession_nodash = filing.accession_number.replace("-", "")
    target_dir = SEC_RAW_DIR / ticker.lower() / accession_nodash
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "primary_doc.xml"

    if target_path.exists() and target_path.stat().st_size > 0:
        return target_path

    request = urllib.request.Request(filing.filing_url, headers={"User-Agent": SEC_USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            target_path.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Falha ao baixar N-PORT de {filing.filing_url}: HTTP {exc.code}") from exc

    return target_path
