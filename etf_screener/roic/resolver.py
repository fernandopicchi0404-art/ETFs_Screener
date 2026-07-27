from __future__ import annotations

import re
from typing import Any

from etf_screener.roic.client import RoicClient

LEGAL_SUFFIXES = re.compile(
    r"\b(Ltd\.?|Limited|PLC|PL|SA|S\.A\.|AG|Inc\.?|Corp\.?|Co\.?|PJSC|NV|SE|SpA)\b",
    re.IGNORECASE,
)

MANUAL_ROIC_SYMBOLS = {
    "BOC Hong Kong Holdings Ltd": "HKEX:2388",
    "Imperial Brands PLC": "LSE:IMB",
    "Kone Oyj": "HEL:KNEBV",
    "Tung Ho Steel Enterprise Corp": "TWSE:2006",
    "Saudi Telecom Co": "TADAWUL:7010",
    "Schroders PLC": "LSE:SDR",
    "Kuehne + Nagel International AG": "SIX:KNIN",
    "TMBThanachart Bank PCL": "SET:TTB",
    "Gjensidige Forsikring ASA": "OSL:GJF",
    "Japan Tobacco Inc": "TSE:2914",
    "Roche Holding AG": "SIX:RO",
    "Roche Holding AG Ordinary Shares new": "SIX:RO",
    "Ono Pharmaceutical Co Ltd": "TSE:4528",
    "Vinci SA": "EURONEXT:DG",
    "Insurance Australia Group Ltd": "ASX:IAG",
    "Singapore Exchange Ltd": "SGX:S68",
    "DBS Group Holdings Ltd": "SGX:D05",
    "Wesfarmers Ltd": "ASX:WES",
    "Rio Tinto Ltd": "ASX:RIO",
    "KT&G Corp": "KRX:033780",
    "Daito Trust Construction Co Ltd": "TSE:1878",
    "Industries Qatar QSC": "QSE:IQCD",
    "Telkom Indonesia Persero Tbk PT": "IDX:TLKM",
    "Medibank Pvt Ltd": "ASX:MPL",
    "LG Uplus Corp": "KRX:032640",
    "Bank Rakyat Indonesia Persero Tbk PT": "IDX:BBRI",
    "Bank Central Asia Tbk PT": "IDX:BBCA",
    "Jarir Marketing Co": "TADAWUL:4190",
    "Chipbond Technology Corp": "TPEX:6147",
    "Radiant Opto-Electronics Corp": "TWSE:6176",
    "Cheil Worldwide Inc": "KRX:030000",
    "Koninklijke Ahold Delhaize NV": "EURONEXT:AD",
    "Jardine Cycle & Carriage Ltd": "SGX:C07",
    "Coca-Cola HBC AG": "LSE:CCH",
    "Cie Generale des Etablissements Michelin SCA": "EURONEXT:ML",
    "United Overseas Bank Ltd": "SGX:U11",
    "Severstal PAO": "MOEX:CHMF",
    "Genting Singapore Ltd": "SGX:G13",
    "China Construction Bank Corp": "HKEX:939",
    "Swisscom AG": "SIX:SCMN",
    "Quebecor Inc": "TSX:QBR.A",
    "Telekom Malaysia Bhd": "MYX:TM",
    "Abu Dhabi Islamic Bank PJSC": "ADX:ADIB",
    "Arca Continental SAB de CV": "BMV:AC",
    "Kimberly-Clark de Mexico SAB de CV": "BMV:KIMBER/A",
    "Neoenergia SA": "B3:NEOE3",
    "Sanlam Ltd": "JSE:SLM",
    "Generali": "MIL:G",
    "Coca-Cola Femsa SAB de CV": "BMV:KOF/UBL",
    # Correções de ticker errado (tipo 1) ou empresa errada (tipo 2)
    "Telstra Group Ltd": "ASX:TLS",
    "AXA SA": "EPA:CS",
    "Bank of Nova Scotia/The": "TSX:BNS",
    "Endesa SA": "BME:ELE",
    "Manulife Financial Corp": "TSX:MFC",
    "PTT Exploration & Production PCL": "SET:PTTEP",
    "Sun Life Financial Inc": "TSX:SLF",
    "Naturgy Energy Group SA": "BME:NTGY",
    "Bidvest Group Ltd": "JSE:BVT",
    "Central Pattana PCL": "SET:CPN",
    "Chicony Electronics Co Ltd": "TWSE:2385",
    "Spark New Zealand Ltd": "NZX:SPK",
    "Ooredoo QPSC": "QSE:ORDS",
    "Great-West Lifeco Inc": "TSX:GWO",
    "iA Financial Corp Inc": "TSX:IAG",
    "Hyundai Motor Co": "KRX:005380",
    # Ticker certo, mas validação de nome falhava
    "Koninklijke KPN NV": "EURONEXT:KPN",
    "TIM SA/Brazil": "B3:TIMS3",
    "Engie Brasil Energia SA": "B3:ENGI3",
}

KNOWN_NAME_QUERIES = {
    "HCL Technologies Ltd": ["HCLTECH"],
    "Vodacom Group Ltd": ["Vodacom"],
    "Emirates NBD Bank PJSC": ["Emirates NBD"],
    "Banco do Brasil SA": ["BBAS3", "Banco do Brasil"],
    "BOC Hong Kong Holdings Ltd": ["HKEX:2388", "2388"],
    "Imperial Brands PLC": ["IMB", "Imperial Brands"],
    "Kone Oyj": ["KNEBV", "KONE"],
    "Tung Ho Steel Enterprise Corp": ["TWSE:2006", "Tung Ho Steel"],
    "Saudi Telecom Co": ["TADAWUL:7010", "7010", "Saudi Telecom"],
    "Deutsche Post AG": ["Deutsche Post", "DHL"],
    "Roche Holding AG Ordinary Shares new": ["Roche"],
    "British American Tobacco PLC": ["British American Tobacco", "BATS"],
    "Koninklijke KPN NV": ["KPN"],
    "Japan Tobacco Inc": ["Japan Tobacco"],
    "China Construction Bank Corp H": ["China Construction Bank", "939"],
    "Unilever PLC": ["Unilever", "ULVR"],
    "Wesfarmers Ltd": ["Wesfarmers", "WES"],
    "Enel SpA": ["Enel"],
    "Eni SpA": ["Eni"],
    "TotalEnergies SE": ["TotalEnergies", "TTE"],
    "BHP Group Ltd": ["BHP"],
    "Allianz SE": ["Allianz", "ALV"],
    "Infosys Ltd": ["Infosys", "INFY"],
    "GSK PLC": ["GSK", "GlaxoSmithKline"],
    "Michelin": ["Michelin", "ML"],
    "Publicis Groupe SA": ["Publicis"],
    "Endesa SA": ["Endesa"],
    "Itau Unibanco Holding SA": ["ITUB4", "Itau Unibanco"],
    "Klabin SA": ["Klabin", "KLBN11"],
    "Ambev SA": ["Ambev", "ABEV3"],
    "TIM SA": ["TIM", "TIMS3"],
    "BB Seguridade Participacoes SA": ["BBSE3"],
    "Schroders PLC": ["SDR", "Schroders"],
    "Kuehne + Nagel International AG": ["KNIN", "Kuehne Nagel"],
    "TMBThanachart Bank PCL": ["TTB", "TMBThanachart"],
    "Gjensidige Forsikring ASA": ["GJF", "Gjensidige"],
}


def _candidate_queries(company_name: str, known_symbol: str | None = None) -> list[str]:
    queries: list[str] = []
    if known_symbol:
        queries.append(known_symbol)

    queries.extend(KNOWN_NAME_QUERIES.get(company_name, []))
    queries.append(company_name)

    cleaned = LEGAL_SUFFIXES.sub("", company_name).strip(" ,")
    if cleaned and cleaned not in queries:
        queries.append(cleaned)

    words = [word for word in re.split(r"\s+", cleaned) if word]
    if len(words) >= 2:
        queries.append(" ".join(words[:2]))
    if len(words) >= 1:
        queries.append(words[0])

    deduped: list[str] = []
    for query in queries:
        if query and query not in deduped:
            deduped.append(query)
    return deduped


def _score_candidate(candidate: dict[str, Any], company_name: str, country: str) -> int:
    name = (candidate.get("name") or "").lower()
    target = company_name.lower()
    score = 0

    if candidate.get("listing_country_code") == country:
        score += 12
    elif candidate.get("listing_country_code"):
        score -= 20
    if candidate.get("type") == "stock":
        score += 4
    if candidate.get("is_primary"):
        score += 2
    if target in name or name in target:
        score += 8
    if any(token.lower() in name for token in target.split()[:2]):
        score += 3
    if candidate.get("type") in {"dr", "fund"}:
        score -= 6
    return score


def resolve_roic_symbol(
    client: RoicClient,
    company_name: str,
    country: str,
    known_symbol: str | None = None,
    known_roic_symbol: str | None = None,
) -> tuple[str | None, str, list[dict[str, Any]]]:
    manual_symbol = MANUAL_ROIC_SYMBOLS.get(company_name)
    if manual_symbol:
        return manual_symbol, "manual", []

    if known_roic_symbol:
        return known_roic_symbol, "mapped", []

    if known_symbol and ":" in known_symbol:
        return known_symbol, "mapped", []

    all_candidates: list[dict[str, Any]] = []
    best_symbol: str | None = None
    best_score = -1
    best_status = "not_found"

    for query in _candidate_queries(company_name, known_symbol):
        payload = client.get("/tickers/search", {"query": query, "limit": 25})
        candidates = payload.get("data", [])
        for candidate in candidates:
            score = _score_candidate(candidate, company_name, country)
            all_candidates.append({**candidate, "_score": score, "_query": query})
            if score > best_score:
                best_score = score
                best_symbol = candidate.get("symbol")
                best_status = "search_match"

    if best_symbol is None:
        return None, "not_found", all_candidates[:10]

    if best_score < 15:
        return best_symbol, "ambiguous", all_candidates[:10]

    return best_symbol, best_status, all_candidates[:10]


def fetch_ticker_metadata(client: RoicClient, roic_symbol: str) -> dict[str, Any] | None:
    payload = client.get("/tickers/search", {"query": roic_symbol, "limit": 10})
    for candidate in payload.get("data", []):
        if candidate.get("symbol") == roic_symbol:
            return candidate
    return None
