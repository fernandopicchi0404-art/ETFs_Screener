from __future__ import annotations

from etf_screener.holdings.nport_identifiers import parse_identifiers
import xml.etree.ElementTree as ET

NS = {"n": "http://www.sec.gov/edgar/nport"}


def test_parse_identifiers_isin_attribute():
    xml = """
    <identifiers xmlns="http://www.sec.gov/edgar/nport">
      <isin value="INE860A01027"/>
      <ticker value="HCLTECH"/>
    </identifiers>
    """
    node = ET.fromstring(xml)
    parsed = parse_identifiers(node)
    assert parsed["isin"] == "INE860A01027"
    assert parsed["ticker"] == "HCLTECH"


def test_parse_nport_holdings_reads_isin_from_fixture():
    from pathlib import Path
    from etf_screener.holdings.sec_nport import parse_nport_holdings

    path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "schy_nport.xml"
    holdings = parse_nport_holdings(path, "SCHY")
    hcl = next(h for h in holdings if "HCL" in h.name)
    assert hcl.isin == "INE860A01027"
