from __future__ import annotations

from etf_screener.holdings.ishares_csv import parse_ishares_csv


SAMPLE_CSV = """iShares MSCI Japan ETF
Fund Holdings as of,"Jul 27, 2026"
Inception Date,"Mar 12, 1996"

Ticker,Name,Sector,Asset Class,Market Value,Weight (%),Notional Value,Quantity,Price,Location,Exchange,Currency,FX Rate,Market Currency,Accrual Date
"8306","MITSUBISHI UFJ FINANCIAL GROUP INC","Financials","Equity","1,065,877,465.38","4.89","1,065,877,465.38","45,935,980.00","23.20","Japan","Tokyo Stock Exchange","USD","163.73","JPY","-"
"XTSLA","BLK CSH FND TREASURY SL AGENCY","Cash and/or Derivatives","Cash","10,000.00","0.05","10,000.00","10,000.00","1.00","United States","-","USD","1.00","USD","-"
"""


def test_parse_ishares_csv_marks_equity_and_cash():
    holdings, as_of = parse_ishares_csv(SAMPLE_CSV, "EWJ")
    assert as_of == "2026-07-27"
    assert len(holdings) == 2
    equity = holdings[0]
    cash = holdings[1]
    assert equity.included_in_equity_analysis is True
    assert equity.weight_original == 4.89
    assert equity.country == "Japan"
    assert equity.sec_ticker == "8306"
    assert equity.other_id == "Tokyo Stock Exchange"
    assert cash.included_in_equity_analysis is False
    assert cash.exclusion_reason.startswith("asset_class=")
