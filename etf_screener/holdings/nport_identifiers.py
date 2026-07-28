from __future__ import annotations

import xml.etree.ElementTree as ET


def _identifier_value(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    value = node.get("value") or (node.text or "").strip()
    return value or None


def parse_identifiers(identifiers_node: ET.Element | None) -> dict[str, str | None]:
    """Extrai identificadores do bloco N-PORT (ISIN, ticker, other)."""
    result: dict[str, str | None] = {
        "isin": None,
        "ticker": None,
        "other_id": None,
        "other_desc": None,
    }
    if identifiers_node is None:
        return result

    for child in list(identifiers_node):
        tag = child.tag.split("}")[-1].casefold()
        if tag == "isin":
            result["isin"] = _identifier_value(child)
        elif tag == "ticker":
            result["ticker"] = _identifier_value(child)
        elif tag == "other":
            result["other_id"] = _identifier_value(child)
            result["other_desc"] = child.get("otherDesc")

    return result
