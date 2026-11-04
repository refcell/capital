#!/usr/bin/env python3
"""Build the TORM plc six-sheet valuation workbook."""
from math import isclose
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


OUT = Path(__file__).with_name("2026-11-04 TORM Model.xlsx")

# Quote: StockAnalysis October 29, 2026 10:05 AM EDT. Model date November 4, 2026
# (Q3 FY2026 earnings date; results not yet public at build time). USD millions.
PRICE = 41.73
SHARES = 102.40  # millions, StockAnalysis shares outstanding
MARKET_CAP = PRICE * SHARES  # 4,273.2
CASH = 377.2  # cash & short-term investments, Jun 30, 2026
TOTAL_DEBT = 1076.0  # StockAnalysis standardized total debt, Jun 30, 2026
ENTERPRISE_VALUE = MARKET_CAP + TOTAL_DEBT - CASH
NET_DEBT = TOTAL_DEBT - CASH
BOOK_EQUITY = 2550.0
NAV_PS = 36.50  # broker NAV/share, Jun 30, 2026
NAV = 3737.0
FLEET_MV = 4056.0

TTM_REVENUE = 1760.0
TTM_GP = 1027.0
TTM_EBIT = 687.6
TTM_EBITDA = 913.8
TTM_NI = 625.1
TTM_EPS = 6.14  # GAAP diluted, income statement
TTM_OCF = 709.9
TTM_CAPEX = 509.7
TTM_FCF = 200.2
TTM_SBC = 34.1
TTM_DA = 226.2
TTM_INTEREST = 71.1
TTM_DIVIDENDS_PAID = 245.0
DPS_TRAIL = 4.42
TTM_TAX = 4.4

# Company Oct 12 guide is TCE/EBITDA. Street revenue $1.63B is below TCE guide
# of $1.7-1.9B and is treated as stale relative to the October raise.
FY26_REV_CONS = 1630.0
FY26_EPS = 9.21  # 3 analysts, StockAnalysis forecast
FY26_NI = 947.39
FY26_EBIT_CONS = 1000.0
FY26_FCF_CONS = 795.33
FY26_TCE_LO, FY26_TCE_HI = 1700.0, 1900.0
FY26_EBITDA_LO, FY26_EBITDA_HI = 1300.0, 1500.0
FY27_REV_CONS = 1540.0
FY27_EPS = 6.15
ANALYST_AVG_PT = 45.00
DIVIDEND = 4.42

# Primary lens: FY2031 mid-cycle EPS x exit P/E. Reported FCF is capex-cycle
# compressed (net debt 3.5x TTM FCF) and tanker NAV is the balance-sheet anchor.
# Do not use FCF multiples as the scenario engine.
SCENARIOS = {
    "Bear": {
        "rev_cagr": -0.080,
        "eps": 2.80,
        "pe": 7.0,
        "nav_ps": 24.00,
        "p_nav": 0.85,
        "weight": 0.30,
    },
    "Base": {
        "rev_cagr": -0.030,
        "eps": 4.50,
        "pe": 8.5,
        "nav_ps": 36.50,
        "p_nav": 1.05,
        "weight": 0.50,
    },
    "Bull": {
        "rev_cagr": 0.020,
        "eps": 5.80,
        "pe": 9.0,
        "nav_ps": 45.00,
        "p_nav": 1.15,
        "weight": 0.20,
    },
}
for case in SCENARIOS.values():
    case["term_rev"] = TTM_REVENUE * (1 + case["rev_cagr"]) ** 5
    case["target"] = case["eps"] * case["pe"]
    case["nav_price"] = case["nav_ps"] * case["p_nav"]
    case["upside"] = case["target"] / PRICE - 1

weighted_value = sum(case["target"] * case["weight"] for case in SCENARIOS.values())

assert SCENARIOS["Bear"]["target"] < PRICE * 0.9
assert SCENARIOS["Bear"]["target"] > 5
assert weighted_value > 0
assert NET_DEBT / TTM_FCF < 10

rf = 4.898  # CNBC US10Y, November 3, 2026
erp = 5.00
beta_reported = -0.02  # StockAnalysis 5Y; not used as selected beta
beta = 0.75  # selected product-tanker peer beta (INSW/STNG/FRO range)
cost_equity = rf + beta * erp
pretax_debt_cost = TTM_INTEREST / TOTAL_DEBT * 100  # 6.61
tax_rate = 3.0  # shipping tonnage tax; FY2025 ETR 3.12%, TTM 0.70%
equity_weight = MARKET_CAP / (MARKET_CAP + TOTAL_DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * cost_equity + debt_weight * pretax_debt_cost * (1 - tax_rate / 100)

wb = Workbook()
navy, blue, gold, gray, white = "17365D", "D9EAF7", "D8B34B", "E7E6E6", "FFFFFF"
thin = Side(style="thin", color="A6A6A6")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, row, col, value, *, bold=False, fill=None, color="000000", size=10, wrap=True):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Aptos", size=size, bold=bold, color=color)
    cell.fill = PatternFill("solid", fgColor=fill) if fill else PatternFill(fill_type=None)
    cell.border = border
    cell.alignment = Alignment(vertical="top", wrap_text=wrap)
    return cell


def title(ws, text, end_col=5, subtitle=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    put(ws, 1, 1, text, bold=True, fill=navy, color=white, size=15)
    ws.row_dimensions[1].height = 28
    if subtitle:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=end_col)
        put(ws, 2, 1, subtitle, bold=True, fill=blue)


def header(ws, row, values):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=True, fill=navy, color=white)


def widths(ws, values):
    for col, width in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.freeze_panes = "A3"


# 1. Valuation
ws = wb.active
ws.title = "Valuation"
title(
    ws,
    "TORM plc (TRMD) — Valuation",
    4,
    "Quote date: October 29, 2026 (StockAnalysis 10:05 AM EDT) | Model date: November 4, 2026 | Fiscal year ends December 31",
)
facts = [
    ("Company", "TORM plc", "Product tanker owner-operator; HQ London / Hellerup; founded 1889; 605 employees; CEO Jacob Meldgaard; ~97 vessels at Jun 30, 2026"),
    ("Ticker", "NASDAQ: TRMD", "Also Nasdaq Copenhagen TRMD A; Energy / Oil & Gas Midstream; ISIN GB00BZ3CNK81"),
    ("Price", PRICE, "StockAnalysis October 29, 2026 10:05 AM EDT $41.73; 52-week range $19.30-$42.64; +101% in 52 weeks"),
    ("Shares outstanding (M)", SHARES, "StockAnalysis 102.40M; +2.42% YoY; TTM diluted average 102M; float 82.23M"),
    ("Market capitalization ($M)", MARKET_CAP, "Price x shares $4,273M; StockAnalysis overview printed $4.31B at this quote"),
    ("Total debt ($M)", TOTAL_DEBT, "StockAnalysis standardized total debt June 30, 2026; current $237M + long-term $830M + leases"),
    ("Cash & STI ($M)", CASH, "Cash $365.7M + short-term investments, June 30, 2026"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "Market cap + debt - cash"),
    ("Net debt ($M)", NET_DEBT, "EV - MC; $6.82/share; 3.5x TTM FCF, 0.77x TTM EBITDA"),
    ("Broker NAV / share", NAV_PS, "Q2 report: fleet MV $4,056M, consolidated NAV $3,737M, $36.50/share at June 30, 2026"),
    ("P / NAV", PRICE / NAV_PS, "14% premium to June broker NAV; vessel values have likely moved with the rate spike since June"),
    ("Dividend / yield", DIVIDEND, "$4.42 trailing (10.59%); Q2 2026 interim $2.40/share ($246M, 73% of NI) paid Sep 24; policy is excess liquidity quarterly"),
    ("Primary valuation lens", "FY2031 mid-cycle EPS x exit P/E", "NAV is the balance-sheet cross-check. Reported FCF is compressed by growth capex (12 MR resales/newbuilds 2027-2029) and fails as a primary multiple"),
    ("Stance", "Watch", "Cycle-peak print: stock doubled, trades above June NAV, FY2026 guide is a record. Probability-weighted FV is below the quote. Q3 due November 4, 2026."),
]
header(ws, 3, ["Field", "Value", "Comment"])
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            if values[0] in {"Price", "Broker NAV / share"}:
                cell.number_format = "$0.00"
            elif values[0] == "P / NAV":
                cell.number_format = "0.00x"
            else:
                cell.number_format = "#,##0.0"

metric_start = 4 + len(facts) + 1
header(ws, metric_start, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E (GAAP)", PRICE / TTM_EPS, "TTM diluted EPS $6.14 through June 30, 2026; cycle-peak earnings, not mid-cycle"),
    ("Forward P/E (FY2026 cons.)", PRICE / FY26_EPS, "Consensus EPS $9.21 (3 analysts). Company TCE/EBITDA guide implies ~$10 if midpoint holds"),
    ("Forward P/E (FY2027 cons.)", PRICE / FY27_EPS, "Consensus $6.15; street already mean-reverts ~33% from 2026"),
    ("P/S (TTM)", MARKET_CAP / TTM_REVENUE, "TTM revenue $1.76B, +33% YoY; FY2025 was $1.34B"),
    ("P/B", MARKET_CAP / BOOK_EQUITY, "Book $2.55B, $24.91/share; P/B 1.68x vs P/NAV 1.14x because book lags vessel values"),
    ("P / NAV (Jun 30)", PRICE / NAV_PS, "Primary asset multiple. Premium can unwind if Q3 broker values do not keep up with the stock"),
    ("P/FCF (TTM)", MARKET_CAP / TTM_FCF, "FCF $200M after $510M capex; not the earnings power of the fleet"),
    ("P/OCF (TTM)", MARKET_CAP / TTM_OCF, "OCF $710M is the cash engine; 6.0x"),
    ("FCF yield (TTM)", TTM_FCF / MARKET_CAP, "4.7%; dividend yield 10.6% — coverage is on OCF, not FCF"),
    ("EV/FCF (TTM)", ENTERPRISE_VALUE / TTM_FCF, "Distorted by growth capex"),
    ("EV/Sales (TTM)", ENTERPRISE_VALUE / TTM_REVENUE, "2.82x"),
    ("EV/EBITDA (TTM)", ENTERPRISE_VALUE / TTM_EBITDA, "5.44x; StockAnalysis snapshot 5.22x on a slightly lower EV"),
    ("EV/EBIT (TTM)", ENTERPRISE_VALUE / TTM_EBIT, "7.23x"),
    ("Dividend yield", DIVIDEND / PRICE, "Trailing DPS $4.42; FCF payout 226% on statistics, OCF payout ~64% on $4.42 x 102.4M / $710M"),
    ("Net debt / TTM FCF", NET_DEBT / TTM_FCF, "3.5x — FCF-multiple gray zone; do not use FCF as primary scenario lens"),
    ("Net debt / TTM EBITDA", NET_DEBT / TTM_EBITDA, "0.76x; balance sheet is not the constraint"),
    ("Interest coverage (EBIT)", TTM_EBIT / TTM_INTEREST, "9.67x; StockAnalysis 9.67x"),
]
for row, values in enumerate(metrics, metric_start + 1):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            if "yield" in values[0] or values[0] == "Dividend yield":
                cell.number_format = "0.0%"
            elif values[0] in {"Interest coverage (EBIT)", "Net debt / TTM FCF", "Net debt / TTM EBITDA"}:
                cell.number_format = "0.00"
            else:
                cell.number_format = "0.00x"
widths(ws, [36, 28, 110, 14])

# 2. WACC
ws = wb.create_sheet("WACC")
title(ws, "TORM — WACC", 4, "CAPM with selected peer beta; reported 5Y beta is -0.02 and is not used as the cost of equity")
header(ws, 3, ["Component", "Value", "Source / formula"])
wacc_rows = [
    ("Risk-free rate", rf / 100, "CNBC US10Y 10-year Treasury, November 3, 2026 (4.898%)"),
    ("Equity risk premium", erp / 100, "Model assumption"),
    ("Reported levered beta (5Y)", beta_reported, "StockAnalysis; negative beta is a 5Y artifact, not a shipping cost of equity"),
    ("Selected levered beta", beta, "0.75 product-tanker peer (INSW, STNG, FRO typically 0.6-1.0). Cyclical freight risk is real"),
    ("Cost of equity", cost_equity / 100, "Risk-free rate + selected beta x ERP"),
    ("Pre-tax cost of debt", pretax_debt_cost / 100, "TTM interest expense $71.1M / total debt $1,076M"),
    ("Tax rate", tax_rate / 100, "Tonnage-tax regime. FY2025 ETR 3.12%; TTM 0.70% is not used"),
    ("Market cap ($M)", MARKET_CAP, "Price x shares"),
    ("Total debt ($M)", TOTAL_DEBT, "StockAnalysis, June 30, 2026"),
    ("Equity weight", equity_weight, "Market cap / (market cap + debt)"),
    ("Debt weight", debt_weight, "Debt / (market cap + debt)"),
    ("After-tax debt cost", pretax_debt_cost / 100 * (1 - tax_rate / 100), "Kd x (1 - tax rate)"),
    ("WACC", wacc / 100, "E/V x Ke + D/V x Kd x (1 - t); StockAnalysis prints 4.64% on the -0.02 beta, which is not used here"),
    ("Scenario discount rates", "n/a — P/E framework", "Scenarios capitalize FY2031 mid-cycle EPS at an exit P/E; NAV is the asset cross-check"),
]
for row, values in enumerate(wacc_rows, 4):
    for col, value in enumerate(values, 1):
        is_wacc = values[0] == "WACC"
        cell = put(ws, row, col, value, bold=(col == 1 or is_wacc), fill=(gold if is_wacc else None))
        if col == 2 and values[0] in {"Market cap ($M)", "Total debt ($M)"}:
            cell.number_format = "#,##0.0"
        elif col == 2 and "beta" in values[0]:
            cell.number_format = "0.00"
        elif col == 2 and isinstance(value, float):
            cell.number_format = "0.00%"
widths(ws, [32, 22, 110, 14])

# 3. Scenarios
ws = wb.create_sheet("Scenarios")
title(
    ws,
    "TORM — FY2031 Mid-Cycle EPS x Exit P/E Scenarios",
    5,
    "Primary lens is mid-cycle EPS because TTM/FY2026 earnings are cycle-peak and TTM FCF is growth-capex compressed. NAV is the asset cross-check. USD millions except per-share figures.",
)
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Notes"])
keys = ("Bear", "Base", "Bull")
scenario_rows = [
    (
        "Revenue CAGR (5Y from TTM)",
        *(SCENARIOS[k]["rev_cagr"] for k in keys),
        "From TTM $1.76B. Street FY2026e revenue $1.63B is below TCE guide $1.7-1.9B and is treated as stale. FY2027e $1.54B is the first visible mean-reversion print",
    ),
    (
        "FY2031 revenue ($M)",
        *(SCENARIOS[k]["term_rev"] for k in keys),
        "TTM x (1+CAGR)^5. Bear: rates collapse toward FY2021-type utilization. Base: mid-cycle after 2027 fade. Bull: fleet growth to 103-109 vessels keeps revenue up even as rates cool",
    ),
    (
        "FY2031 mid-cycle EPS",
        *(SCENARIOS[k]["eps"] for k in keys),
        "GAAP. FY2025 was $2.85, TTM $6.14, FY2026e $9.21, FY2027e $6.15. Bear is a FY2025-like trough; base is below FY2027 consensus; bull holds a high-cycle residual",
    ),
    (
        "Exit P/E",
        *(SCENARIOS[k]["pe"] for k in keys),
        "Current TTM P/E 6.8x, FY2026e 4.5x. Tanker trough multiples are 6-8x; 9x is a scarce-fleet premium, not a growth multiple",
    ),
    (
        "Target price",
        *(SCENARIOS[k]["target"] for k in keys),
        "FY2031 EPS x exit P/E, undiscounted. Near-term cash is returned as a variable dividend rather than modeled as a PV residual",
    ),
    (
        "Upside / (downside)",
        *(SCENARIOS[k]["upside"] for k in keys),
        "Versus $41.73 quote",
    ),
    (
        "Probability",
        *(SCENARIOS[k]["weight"] for k in keys),
        "30% / 50% / 20%",
    ),
    (
        "Weighted value/share",
        *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in keys),
        "Contribution to fair value",
    ),
    ("", "", "", "", ""),
    (
        "FY2031 NAV / share (cross-check)",
        *(SCENARIOS[k]["nav_ps"] for k in keys),
        "June 30 broker NAV $36.50. Bear: second-hand values give back ~34%. Base: NAV holds. Bull: newbuild/resale book plus firm values",
    ),
    (
        "Exit P / NAV",
        *(SCENARIOS[k]["p_nav"] for k in keys),
        "Spot trades at 1.14x June NAV. Bear 0.85x is a cycle-trough shipping discount; bull 1.15x is today's premium on a higher NAV",
    ),
    (
        "NAV-implied price",
        *(SCENARIOS[k]["nav_price"] for k in keys),
        "NAV/share x exit P/NAV. Cross-check only; primary targets are the EPS x P/E row",
    ),
]
pct_rows = {
    "Revenue CAGR (5Y from TTM)",
    "Upside / (downside)",
    "Probability",
}
usd_rows = {"Target price", "Weighted value/share", "FY2031 mid-cycle EPS", "NAV-implied price", "FY2031 NAV / share (cross-check)"}
mult_rows = {"Exit P/E", "Exit P / NAV"}
for row, values in enumerate(scenario_rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col in (2, 3, 4) and values[0] in pct_rows and isinstance(value, float):
            cell.number_format = "0.0%"
        elif col in (2, 3, 4) and values[0] in usd_rows and isinstance(value, float):
            cell.number_format = "$0.00"
        elif col in (2, 3, 4) and values[0] in mult_rows and isinstance(value, float):
            cell.number_format = "0.00x"
        elif col in (2, 3, 4) and isinstance(value, float):
            cell.number_format = "#,##0.0"
fv_row = 4 + len(scenario_rows) + 1
put(ws, fv_row, 1, "Probability-weighted fair value", bold=True, fill=gold)
put(ws, fv_row, 2, weighted_value, bold=True, fill=gold).number_format = "$0.00"
put(ws, fv_row + 1, 1, "Upside from current price", bold=True, fill=gold)
put(ws, fv_row + 1, 2, weighted_value / PRICE - 1, bold=True, fill=gold).number_format = "0.0%"
put(ws, fv_row + 2, 1, "Analyst cross-check", bold=True, fill=gray)
put(
    ws,
    fv_row + 2,
    2,
    (
        "StockAnalysis: 2 analysts, average/median/high PT $45 (Evercore ISI $38 → $45 on Oct 27, 2026, Buy). "
        "Kepler Capital $21 Sell (May 14, 2026) and Pareto $33 Hold (May 13, 2026) are stale versus the October guide raise. "
        f"Base ${SCENARIOS['Base']['target']:.2f} is {SCENARIOS['Base']['target'] / ANALYST_AVG_PT - 1:+.1%} vs the $45 average. "
        f"Probability-weighted FV ${weighted_value:.2f} is {weighted_value / ANALYST_AVG_PT - 1:+.1%} vs the average target. "
        "Coverage is thin (2-3 analysts); do not treat $45 as a deep consensus."
    ),
    fill=gray,
)
ws.merge_cells(start_row=fv_row + 2, start_column=2, end_row=fv_row + 2, end_column=5)
put(ws, fv_row + 3, 1, "Framework note", bold=True, fill=gray)
put(
    ws,
    fv_row + 3,
    2,
    (
        "Primary lens is FY2031 mid-cycle EPS x exit P/E. TTM EPS of $6.14 and FY2026e $9.21 are cycle-peak, not a run-rate. "
        "Q2 TCE/day was $59,301 versus $26,672 a year earlier; FY2025 EPS was only $2.85. "
        f"TTM FCF of $200M after $510M capex is 3.5x net debt (${NET_DEBT:.0f}M). At an 8x FCF multiple implied equity is far below the $4.3B market cap, "
        "which is a framework failure (growth-capex trough plus gray-zone leverage), not insolvency. "
        "OCF of $710M covers the dividend. NAV of $36.50 at June 30 is the asset floor; the stock at $41.73 is a 14% premium to that print. "
        "FCF multiples are not used as targets."
    ),
    fill=gray,
)
ws.merge_cells(start_row=fv_row + 3, start_column=2, end_row=fv_row + 3, end_column=5)
ws.row_dimensions[fv_row + 2].height = 78
ws.row_dimensions[fv_row + 3].height = 96
widths(ws, [40, 16, 16, 16, 100])

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(
    ws,
    "TORM — Actuals Source Audit",
    5,
    "Financial statement figures in USD millions unless noted; fiscal year ends December 31; TTM through June 30, 2026",
)
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/trmd"
q2 = "https://s202.q4cdn.com/126069760/files/doc_financials/2026/q2/TORM-Q2-2026-Report.pdf"
guide = "https://www.prnewswire.com/news-releases/torm-plc-upgrades-full-year-guidance-302905622.html"
audit = [
    ("Stock price", "$41.73", f"{sa}/", "2026-10-29", "StockAnalysis 10:05 AM EDT; previous close $41.71; 52-week $19.30-$42.64"),
    ("Market cap", "$4.31B printed / $4.27B calc", f"{sa}/", "2026-10-29", "102.40M x $41.73 = $4,273M; overview printed $4.31B"),
    ("Enterprise value", "$4.97B calc", f"{sa}/statistics/", "2026-10-29", "MC $4,273 + debt $1,076 - cash $377; statistics printed $4.77B on a lower MC snapshot"),
    ("Shares outstanding", "102.40M", f"{sa}/statistics/", "2026-10-29", "+2.42% YoY; +0.87% QoQ; current share class 102.71M; float 82.23M"),
    ("TTM diluted shares", "102M", f"{sa}/financials/income-statement/", "2026-06-30", "FY2025 diluted 100M; FY2024 96M"),
    ("Revenue TTM", "$1,760M", f"{sa}/financials/income-statement/", "2026-06-30", "FY25 $1,340; FY24 $1,559; FY23 $1,520; FY22 $1,443; FY21 $620"),
    ("Revenue FY2025", "$1,340M", f"{sa}/financials/income-statement/", "2025-12-31", "-14.1% YoY; trough year inside the current cycle"),
    ("Gross profit TTM", "$1,027M (58.4%)", f"{sa}/financials/income-statement/", "2026-06-30", "FY25 49.7%; FY24 57.4%"),
    ("SG&A TTM", "$110.5M", f"{sa}/financials/income-statement/", "2026-06-30", "FY25 $113.8M"),
    ("Operating income TTM", "$687.6M (39.1%)", f"{sa}/financials/income-statement/", "2026-06-30", "FY25 $337.3M; FY24 $607.5M"),
    ("Interest expense TTM", "$71.1M", f"{sa}/financials/income-statement/", "2026-06-30", "Cash interest paid $69.0M"),
    ("Gain on sale of assets TTM", "$8.1M", f"{sa}/financials/income-statement/", "2026-06-30", "FY25 $19.0M; FY24 $51.3M; FY23 $50.4M"),
    ("Pretax income TTM", "$629.5M", f"{sa}/financials/income-statement/", "2026-06-30", "EBT ex-unusual $621.4M"),
    ("Income tax TTM", "$4.4M (0.70%)", f"{sa}/financials/income-statement/", "2026-06-30", "Tonnage tax; FY25 $9.2M / 3.12%"),
    ("Net income TTM", "$625.1M", f"{sa}/financials/income-statement/", "2026-06-30", "+89.9% YoY; FY25 $285.3M"),
    ("GAAP EPS TTM diluted", "$6.14", f"{sa}/financials/income-statement/", "2026-06-30", "Basic $6.23; FY25 $2.85; overview EPS $5.99 uses a different share base"),
    ("EBITDA TTM", "$913.8M (51.9%)", f"{sa}/financials/income-statement/", "2026-06-30", "D&A for EBITDA $226.2M"),
    ("Cash & STI", "$377.2M", f"{sa}/financials/balance-sheet/", "2026-06-30", "Cash $365.7M; FY25 year-end cash $158.1M"),
    ("Total debt", "$1,076M", f"{sa}/financials/balance-sheet/", "2026-06-30", "CPLTD $237M + LT debt $830M + LT leases $9.3M; FY25 $1,003M"),
    ("Net cash (debt)", "-$699M", f"{sa}/financials/balance-sheet/", "2026-06-30", "-$6.87/share; matches statistics"),
    ("PP&E", "$2,934M", f"{sa}/financials/balance-sheet/", "2026-06-30", "Machinery $3,781M; fleet carrying value vs broker MV $4,056M"),
    ("Goodwill / intangibles", "$1.9M / $4.2M", f"{sa}/financials/balance-sheet/", "2026-06-30", "Immaterial; this is a hard-asset shipping book"),
    ("Total assets", "$3,823M", f"{sa}/financials/balance-sheet/", "2026-06-30", "FY25 $3,367M"),
    ("Common equity", "$2,550M", f"{sa}/financials/balance-sheet/", "2026-06-30", "BVPS $24.91; retained earnings $2,258M"),
    ("Preferred stock", "None reported", f"{sa}/financials/balance-sheet/", "2026-06-30", "No preferred equity line"),
    ("Working capital", "$473.9M", f"{sa}/financials/balance-sheet/", "2026-06-30", "Current ratio 2.27; FY25 was 1.33"),
    ("OCF TTM", "$709.9M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "FY25 $498.9M; FY24 $826.8M"),
    ("Capex TTM", "$509.7M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "FY25 $308.5M; FY24 $582.4M — vessel purchases, not maintenance only"),
    ("Sale of PP&E TTM", "$77.8M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "FY25 $143.8M"),
    ("Investing CF TTM", "-$427.3M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "Gap vs capex is vessel sales and other investing inflows, not extra acquisitions"),
    ("FCF TTM", "$200.2M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "OCF - capex; margin 11.4%; FY25 $190.4M"),
    ("Net borrowing TTM", "-$55.1M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "FY25 net repay $258.8M"),
    ("Dividends paid TTM", "$245.0M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "Cash through Jun 30; Q2 $2.40 DPS / $246M was paid Sep 24 and is not in this cash figure"),
    ("Trailing DPS", "$4.42", f"{sa}/statistics/", "2026-10-29", "Yield 10.59% at $41.73; statistics FCF payout 226% uses $4.42 x shares / $200M FCF"),
    ("SBC TTM", "$34.1M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "FY25 $34.1M; RSU exercises added shares in Sep/Oct 2026"),
    ("Q2'26 revenue", "$663M", q2, "2026-08-26", "vs $315M Q2'25; StockAnalysis $662.8M"),
    ("Q2'26 TCE", "$512M", q2, "2026-08-26", "vs $208M; TCE/day $59,301 vs $26,672"),
    ("Q2'26 TCE by class", "LR2 $66,993 / LR1 $57,550 / MR $57,040 per day", q2, "2026-08-26", "8,519 available earning days vs 7,888"),
    ("Q2'26 EBITDA", "$416M", q2, "2026-08-26", "Adjusted $409M; includes $7M unrealized instrument gains"),
    ("Q2'26 net profit", "$338M", q2, "2026-08-26", "Record quarter; basic EPS $3.31; diluted $3.25"),
    ("Q2'26 dividend", "$2.40 / $246M / 73% of NI", q2, "2026-08-26", "Paid Sep 24, 2026; record Sep 10"),
    ("H1'26 TCE / EBITDA / NI", "$798M / $617M / $461M", q2, "2026-08-26", "vs H1'25 $422 / $262 / $122"),
    ("Fleet at Jun 30", "97 vessels (22 LR2 / 10 LR1 / 65 MR)", q2, "2026-08-26", "Two 2015 MRs delivered in Q2 (Dehradun, Dapitan)"),
    ("Orderbook", "6 MR resales 2027-28 + 6 MR NB 2029 (+2 option 2030)", q2, "2026-08-26", "Path to 103 vessels after 2027-28 deliveries, 109 if options exercised"),
    ("Broker fleet MV", "$4,056M", q2, "2026-06-30", "vs $2,888M a year earlier; ~39% above carrying value"),
    ("Broker NAV", "$3,737M / $36.50 per share", q2, "2026-06-30", "vs $23.50 a year earlier and $25.70 at FY2025"),
    ("Q3 coverage at Aug 18", "73% of days at $38,606/day", q2, "2026-08-26", "LR2 83% @ $49,255; LR1 61% @ $32,608; MR 71% @ $35,247"),
    ("FY2026 coverage at Aug 18", "70% of days at $45,391/day", q2, "2026-08-26", "10,271 days open; $1,000/day rate move ≈ $10M EBITDA"),
    ("Q2-time FY26 TCE guide", "$1,400-1,600M", q2, "2026-08-26", "Raised from $1,150-1,450M"),
    ("Q2-time FY26 EBITDA guide", "$1,000-1,200M", q2, "2026-08-26", "Raised from $800-1,100M"),
    ("Oct 12 FY26 TCE guide", "$1,700-1,900M", guide, "2026-10-12", "Second raise; 'record levels'; Q4 strength cited"),
    ("Oct 12 FY26 EBITDA guide", "$1,300-1,500M", guide, "2026-10-12", "Midpoint $1,400M vs TTM $914M and FY25 $549M"),
    ("FY2026 consensus rev", "$1.63B", f"{sa}/forecast/", "2026-10-27", "3 analysts; +21% vs FY25. Inconsistent with TCE guide $1.7-1.9B (TCE sits below revenue). Treat as stale"),
    ("FY2026 consensus EPS", "$9.21", f"{sa}/forecast/", "2026-10-27", "Range $8.13-$11.10; 3 analysts; NI $947M"),
    ("FY2026 consensus FCF", "$795M", f"{sa}/forecast/", "2026-10-27", "4x TTM FCF; only works if vessel capex pauses. Fragile"),
    ("FY2027 consensus rev", "$1.54B", f"{sa}/forecast/", "2026-10-27", "-5.2% vs FY26e; later years gated Pro"),
    ("FY2027 consensus EPS", "$6.15", f"{sa}/forecast/", "2026-10-27", "-33% vs FY26e $9.21 — street mean-reversion is explicit"),
    ("Analyst PT", "$45 avg / $45 med / $45 high", f"{sa}/forecast/", "2026-10-27", "2 analysts; Evercore $45 Buy Oct 27. Kepler $21 Sell and Pareto $33 Hold are May prints"),
    ("Q3'26 consensus EPS", "~$1.54", "https://www.marketbeat.com/earnings/reports/2026-11-4-torm-plc-stock", "2026-11-04", "Last year $0.77; results due Nov 4 before open / 16:00 CEST. Not in this model"),
    ("Beta", "-0.02", f"{sa}/statistics/", "2026-10-29", "Five-year; selected WACC uses 0.75"),
    ("U.S. 10Y Treasury", "4.898%", "https://www.cnbc.com/quotes/US10Y", "2026-11-03", "Risk-free rate"),
    ("Next earnings", "Nov 4, 2026", f"{sa}/", "2026-10-29", "Q3 FY2026; already-released Q2 is not a remaining catalyst"),
    ("Hafnia stake", "~19.85%", "https://www.businesswire.com/news/home/20260923401791/en/HAFNIA-LIMITED-Acquisition-of-an-Additional-1.7-Million-TORM-Shares/", "2026-09-23", "Bought 1.7M at $34.00 after 4.5M at $32.25; Oaktree/OCM Njord selling via secondaries"),
    ("Oaktree secondary Oct", "6.33M shares at $40.05", f"{sa}/", "2026-10-07", "Follows 9.0M at $32.25 in mid-September; JPMorgan sole bookrunner"),
    ("Segment mix FY25", "Tanker $1.31B / Marine Eng. $37.2M", f"{sa}/financials/metrics/", "2025-12-31", "Tanker is the business; engineering is a rounding error"),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [36, 48, 92, 14, 78])

# 5. Questions
ws = wb.create_sheet("Questions")
title(ws, "TORM — Open Questions", 4, "Items that can change valuation or conviction")
header(ws, 3, ["#", "Question", "Why it matters", "Best evidence / next check"])
questions = [
    (1, "What does Q3 FY2026 (due November 4) print for TCE/day versus the 73% coverage book at $38,606, and does the company reaffirm the October TCE $1.7-1.9B / EBITDA $1.3-1.5B guide?", "The stock is capitalizing a record year. A miss versus $38.6k on the uncovered 27% of Q3 days, or a guide trim, is the bear path starting this morning.", "Q3 release and call, November 4, 2026."),
    (2, "What is the Q3 broker fleet valuation and NAV/share versus $36.50 at June 30?", "The equity trades at 1.14x June NAV. If Q3 NAV has not risen with the share price, the premium is sentiment, not asset value.", "Q3 report NAV table."),
    (3, "What TCE/day does management treat as mid-cycle for LR2 / LR1 / MR once Red Sea / product-arbitrage dislocations fade?", "FY2025 EPS was $2.85 on much lower rates. The $4.50 base-case FY2031 EPS lives or dies on the mid-cycle rate, not on Q2's $59,301.", "Q3 market commentary; any indicative mid-cycle disclosure."),
    (4, "What is the remaining cash and debt funding for the 6 MR resales (2027-28) and 6 (+2 option) MR newbuilds (2029-30)?", "TTM capex of $510M already crushed FCF to $200M. Another heavy capex year would keep FCF below the dividend even if OCF is fine.", "Q3 capex and orderbook cash-out schedule."),
    (5, "Is the $4.42 trailing DPS a run-rate or a cycle distribution? Q2 paid $2.40 (73% of NI). What happens to the quarterly dividend if TCE/day falls back to $25-30k?", "Statistics FCF payout is 226%. OCF covers it today. A variable policy that cuts with rates is expected; a sticky high DPS would force leverage.", "Q3 dividend declaration vs net profit."),
    (6, "What is Hafnia's endgame at ~19.85% — financial stake, commercial cooperation, or a combination?", "A combination would re-rate the equity on scale. A passive 20% block can also cap the float and keep a strategic overhang.", "Hafnia 13D/major-shareholder notices; any cooperation 6-K."),
    (7, "How much of OCM Njord / Oaktree remains after the 9.0M September secondary at $32.25 and the 6.33M October secondary at $40.05?", "Sponsor sell-down is the supply that capped the stock in September and was absorbed in October. Residual overhang sets near-term technicals.", "Oct 8 major-shareholder announcement; next 6-K."),
    (8, "How much of Q2's $59k TCE/day was Red Sea rerouting, Russian product displacement, or refinery-outage tightness versus a structural ton-mile step-up?", "If Q2 was a dislocation spike, FY2026 is peak earnings and 4.5x forward P/E is a peak multiple on peak EPS.", "Q3 trading-pattern commentary; Clarksons/broker rate splits."),
    (9, "What is the debt maturity schedule 2027-2030 and the mix of floating vs fixed?", "Interest coverage is 9.7x at peak EBIT. Coverage compresses fast if EBIT goes back to FY2025's $337M against $71M of interest.", "Q3 notes; annual report debt table."),
    (10, "Customer concentration: what share of TCE sits with oil majors / traders, and are there COAs that reprice below spot?", "Spot-heavy books capture spikes and give them back. A COA mix would change both the bull and the bear.", "Q3 commercial update; 20-F customer note."),
    (11, "IMO CII, FuelEU Maritime and scrubber/dual-fuel capex: is the 2010-vintage LR2 tail a stranded-asset risk or a recycling option?", "Several LR2s are 2010-2012 builds. A regulatory step-up in 2028-2030 would hit NAV just as the cycle fades.", "Fleet list ages; Q3 ESG/capex remarks."),
    (12, "Share count: RSUs added 132k (Sep 18), 97k (Sep 24) and 61k (Oct 7). What is the fully diluted overhang from the incentive program?", "Dilution is small per grant but compounding. Per-share NAV and DPS are the compounding engine; issuance works against it.", "RSU 6-Ks; year-end diluted count."),
    (13, "Tonnage-tax durability in the UK / Denmark: is 0.7-3.1% ETR a permanent feature or a political risk?", "A shift toward standard corporate tax would take ~$0.40-0.60 off peak EPS. Not thesis-breaking, but it is a hidden multiple support.", "Q3 tax note; UK/DK shipping-tax news."),
    (14, "Marine Engineering ($37M FY25) — keep, harvest, or sell? Any related-party or capex drag on the tanker book?", "It is 3% of FY25 revenue. Only matters if it absorbs management time or capital.", "Segment note in Q3/FY report."),
    (15, "Working-capital swing: inventory -$139M TTM. Is that bunker timing or a structural build that reverses?", "OCF of $710M already includes a $171M WC drain. A reverse would juice FCF without helping the franchise.", "Q3 cash-flow bridge."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 88, 72, 52])

# 6. Sources
ws = wb.create_sheet("Sources")
title(ws, "TORM — Sources", 4, "Public sources accessed November 4, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Price, range, market cap, dividend, earnings date, news"),
    (2, "StockAnalysis income statement", f"{sa}/financials/income-statement/", "Annual and TTM P&L, margins, EPS"),
    (3, "StockAnalysis quarterly income", f"{sa}/financials/quarterly/", "Q2 2026 and prior quarters"),
    (4, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, PP&E, equity, shares"),
    (5, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, dividends, SBC"),
    (6, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation ratios, beta, EV, payout, employees"),
    (7, "StockAnalysis forecast", f"{sa}/forecast/", "FY2026-27 consensus, price targets, ratings"),
    (8, "StockAnalysis ratios", f"{sa}/financials/ratios/", "Historical multiples, ROE, leverage"),
    (9, "StockAnalysis company profile", f"{sa}/company/", "Identity, sector, executives, HQ"),
    (10, "StockAnalysis metrics / segments", f"{sa}/financials/metrics/", "Tanker vs Marine Engineering split"),
    (11, "Yahoo Finance quote", "https://finance.yahoo.com/quote/TRMD/", "Cross-check price, 52-week, related tickers; quote feed was stale vs StockAnalysis"),
    (12, "Yahoo Finance profile", "https://finance.yahoo.com/quote/TRMD/profile/", "Official identity: Energy / Oil & Gas Midstream, product tankers"),
    (13, "TORM Q2 2026 report", q2, "TCE, EBITDA, NI, dividend, NAV, fleet, coverage, Q2-time guide"),
    (14, "TORM Q2 2026 announcement", "https://www.torm.com/news/company-announcements/company-announcements-details/2026/TORM-plc-Q2-2026-Results-Dividend-Distribution-and-Financial-Outlook-2026/default.aspx", "Key figures table, TCE by class, outlook"),
    (15, "TORM Oct 12 guide upgrade", guide, "FY2026 TCE $1.7-1.9B, EBITDA $1.3-1.5B"),
    (16, "TORM fleet list", "https://www.torm.com/about/our-fleet/default.aspx", "Vessel names, classes, years, flags"),
    (17, "TORM IR / why invest", "https://www.torm.com/investor/why-invest/default.aspx", "Integrated commercial/technical model, distribution policy"),
    (18, "Hafnia additional 1.7M shares", "https://www.businesswire.com/news/home/20260923401791/en/HAFNIA-LIMITED-Acquisition-of-an-Additional-1.7-Million-TORM-Shares/", "Stake ~19.85% at $34.00"),
    (19, "CNBC US10Y", "https://www.cnbc.com/quotes/US10Y", "Risk-free rate 4.898%"),
    (20, "TORM Q3 2026 event page", "https://www.torm.com/investor/events/financial-calendar/event-details/2026/First-nine-months-and-third-quarter-2026-results/default.aspx", "Results scheduled Nov 4, 2026 16:00 CEST; not yet posted at model time"),
]
for row, values in enumerate(sources, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 42, 110, 62])

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert isclose(check["Scenarios"].cell(row=fv_row, column=2).value, weighted_value, rel_tol=1e-12)
print(f"Market cap: ${MARKET_CAP:,.1f}M | EV: ${ENTERPRISE_VALUE:,.1f}M | Net debt: ${NET_DEBT:,.1f}M")
print(f"P/NAV: {PRICE / NAV_PS:.2f}x | NAV/share: ${NAV_PS:.2f} | Book/share: ${BOOK_EQUITY / SHARES:.2f}")
print(f"Reported beta: {beta_reported:.2f} | Selected beta: {beta:.2f} | Ke: {cost_equity:.2f}% | WACC: {wacc:.2f}%")
print(f"Net debt / FCF: {NET_DEBT / TTM_FCF:.2f}x | Trailing P/E: {PRICE / TTM_EPS:.2f}x | FY26e P/E: {PRICE / FY26_EPS:.2f}x | FY27e P/E: {PRICE / FY27_EPS:.2f}x")
for name, case in SCENARIOS.items():
    print(
        f"{name}: CAGR {case['rev_cagr']:.1%}, EPS ${case['eps']:.2f}, P/E {case['pe']:.1f}x, "
        f"target ${case['target']:.2f} ({case['upside']:+.1%}), NAV-implied ${case['nav_price']:.2f}"
    )
print(f"Probability-weighted fair value: ${weighted_value:.2f} ({weighted_value / PRICE - 1:+.1%})")
print(f"Analyst avg PT ${ANALYST_AVG_PT:.2f} | bear < 90% of price: {SCENARIOS['Bear']['target'] < PRICE * 0.9}")
print(f"Wrote and verified {OUT}")
