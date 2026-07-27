from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

NS = {"n": "http://www.sec.gov/edgar/nport"}


@dataclass(frozen=True)
class NportMetadata:
    registrant_name: str | None
    series_name: str | None
    report_period_end: str | None
    report_date: str | None


def parse_nport_metadata(xml_source: bytes | Path | str) -> NportMetadata:
    if isinstance(xml_source, Path):
        content = xml_source.read_bytes()
    elif isinstance(xml_source, bytes):
        content = xml_source
    else:
        content = xml_source.encode("utf-8")

    root = ET.fromstring(content)
    return NportMetadata(
        registrant_name=_find_text(root, "regName"),
        series_name=_find_text(root, "seriesName"),
        report_period_end=_find_text(root, "repPdEnd"),
        report_date=_find_text(root, "repPdDate"),
    )


def _find_text(root: ET.Element, tag: str) -> str | None:
    element = root.find(f".//n:{tag}", NS)
    if element is None or not element.text:
        return None
    return element.text.strip()
