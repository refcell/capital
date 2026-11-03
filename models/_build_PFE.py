#!/usr/bin/env python3
"""Build the Pfizer Inc. six-sheet valuation workbook."""
from math import isclose
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


OUT = Path(__file__).with_name("2026-11-03 Pfizer Model.xlsx")

# Quote: StockAnalysis close October 30, 2026. Model date November 3, 2026
# (Q3 FY2026 earnings date). Figures in USD millions unless noted.
PRICE = 30.52
SHARES = 5700.0  # millions, StockAnalysis shares outstanding
MARKET_CAP = PRICE * SHARES  # 173,964
CASH = 11704.0  # cash & short-term investments, Jun 28, 2026
TOTAL_DEBT = 63480.0  # StockAnalysis standardized total debt, Jun 28, 2026
ENTERPRISE_VALUE = MARKET_CAP + TOTAL_DEBT - CASH  # 225,740
NET_DEBT = TOTAL_DEBT - CASH  # 51,776
BOOK_EQUITY = 85490.0

TTM_REVENUE = 63696.0
TTM_GP = 47591.0
TTM_EBIT = 18844.0
TTM_EBITDA = 25383.0
TTM_NI = 4334.0
TTM_EPS = 0.76  # GAAP diluted
TTM_OCF = 13401.0
TTM_CAPEX = 2416.0
TTM_FCF = 10985.0
TTM_SBC = 947.0
TTM_DA = 6539.0
TTM_INTEREST = 2699.0
TTM_ACQUISITIONS = 6927.0
TTM_DIVIDENDS = 9785.0
TTM_WRITEDOWN = 8948.0
TTM_RESTRUCTURING = 3271.0
TTM_LEGAL = 1526.0

FY26_REV = 62220.0  # StockAnalysis / Yahoo consensus, 25 analysts
FY26_REV_GUIDE_MID = 61500.0  # company guide $60.5-62.5B, midpoint $61.5B
FY26_EPS = 2.96  # non-GAAP adjusted, 24 analysts
FY26_EPS_GUIDE_MID = 2.90  # company $2.80-$3.00
FY27_REV = 59890.0  # Yahoo, 23 analysts (StockAnalysis 59.86B)
FY27_EPS = 2.88  # non-GAAP adjusted, 22 analysts
FY26_FCF_CONS = 19170.0  # StockAnalysis forecast page, gated years after
ANALYST_AVG_PT = 29.26
ANALYST_LOW_PT = 25.00
ANALYST_HIGH_PT = 36.00
DIVIDEND = 1.72

# Primary lens: FY2031 adjusted EPS x exit P/E. FCF multiples are a
# cross-check only: net debt is 4.7x TTM FCF, so compressed FCF multiples
# produce equity values near or below zero (gray-zone leverage).
SCENARIOS = {
    "Bear": {
        "rev_cagr": -0.040,
        "eps": 2.15,
        "pe": 8.0,
        "fcf_margin": 0.12,
        "fcf_mult": 8.0,
        "weight": 0.30,
    },
    "Base": {
        "rev_cagr": -0.010,
        "eps": 3.00,
        "pe": 10.0,
        "fcf_margin": 0.16,
        "fcf_mult": 11.0,
        "weight": 0.50,
    },
    "Bull": {
        "rev_cagr": 0.025,
        "eps": 3.50,
        "pe": 12.0,
        "fcf_margin": 0.18,
        "fcf_mult": 13.0,
        "weight": 0.20,
    },
}
for case in SCENARIOS.values():
    case["term_rev"] = TTM_REVENUE * (1 + case["rev_cagr"]) ** 5
    case["term_fcf"] = case["term_rev"] * case["fcf_margin"]
    case["fcf_ev"] = case["term_fcf"] * case["fcf_mult"]
    case["fcf_equity"] = case["fcf_ev"] - NET_DEBT
    case["fcf_price"] = case["fcf_equity"] / SHARES
    case["target"] = case["eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1

weighted_value = sum(case["target"] * case["weight"] for case in SCENARIOS.values())

assert SCENARIOS["Bear"]["target"] < PRICE * 0.9
assert SCENARIOS["Bear"]["target"] > 5
assert weighted_value > 0

rf = 4.915  # CNBC US10Y, Nov 3, 2026
erp = 5.00
beta = 0.28  # StockAnalysis 5Y
cost_equity = rf + beta * erp
pretax_debt_cost = TTM_INTEREST / TOTAL_DEBT * 100  # 4.25
tax_rate = 15.0  # company adjusted ETR guidance
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
    "Pfizer Inc. (PFE) — Valuation",
    4,
    "Quote date: October 30, 2026 close | Model date: November 3, 2026 | Fiscal year ends December 31",
)
facts = [
    ("Company", "Pfizer Inc.", "Discovers, develops and sells biopharmaceuticals; HQ New York; founded 1849; 75,000 employees; CEO Albert Bourla"),
    ("Ticker", "NYSE: PFE", "Drug Manufacturers - General / Healthcare"),
    ("Price", PRICE, "StockAnalysis close October 30, 2026 (+1.90%); 52-week range $23.62-$30.67"),
    ("Shares outstanding (M)", SHARES, "StockAnalysis 5.70B; +0.34% YoY; TTM diluted average 5,726M"),
    ("Market capitalization ($M)", MARKET_CAP, "Price x shares; StockAnalysis $173.95B"),
    ("Total debt ($M)", TOTAL_DEBT, "StockAnalysis standardized total debt, June 28, 2026; matches Yahoo Key Stats"),
    ("Cash & STI ($M)", CASH, "Cash $976M + short-term investments $10,723M, June 28, 2026"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "Market cap + debt - cash; matches StockAnalysis $225.73B"),
    ("Net debt ($M)", NET_DEBT, "EV - MC; 4.7x TTM FCF"),
    ("Dividend / yield", DIVIDEND, "$1.72 annualized (5.64%); 351st consecutive quarterly dividend; ex-div Nov 6, 2026"),
    ("Primary valuation lens", "FY2031 adjusted EPS x exit P/E", "Trailing GAAP P/E is distorted by $8.9B TTM writedowns; FCF multiples are a cross-check only because net debt is 4.7x FCF"),
    ("Stance", "Watch", "Probability-weighted FV slightly below the October 30 close; 5.6% yield is ballast, not a Buy signal. Q3 results due November 3, 2026."),
]
header(ws, 3, ["Field", "Value", "Comment"])
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            cell.number_format = "$0.00" if values[0] == "Price" else "#,##0.0"

metric_start = 4 + len(facts) + 1
header(ws, metric_start, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E (GAAP)", PRICE / TTM_EPS, "TTM GAAP EPS $0.76 after $8.9B writedowns, $3.3B restructuring, $1.5B legal; not a earnings denominator"),
    ("Forward P/E (FY2026 adj.)", PRICE / FY26_EPS, "Consensus non-GAAP EPS $2.96 (24 analysts); company guide $2.80-$3.00"),
    ("Forward P/E (FY2027 adj.)", PRICE / FY27_EPS, "Consensus $2.88 (22 analysts); street sees another year of EPS decline"),
    ("P/S (TTM)", MARKET_CAP / TTM_REVENUE, "TTM revenue $63.70B, -0.2% YoY"),
    ("P/S (FY2026 consensus)", MARKET_CAP / FY26_REV, "Consensus $62.22B vs company midpoint $61.5B"),
    ("P/FCF (TTM)", MARKET_CAP / TTM_FCF, "FCF $10.99B; 89% paid out as dividends"),
    ("FCF yield (TTM)", TTM_FCF / MARKET_CAP, "6.3%; dividend yield 5.64%"),
    ("EV/FCF (TTM)", ENTERPRISE_VALUE / TTM_FCF, "20.5x; leverage inflates EV/FCF vs P/FCF"),
    ("EV/Sales (TTM)", ENTERPRISE_VALUE / TTM_REVENUE, "3.54x"),
    ("EV/EBITDA (TTM)", ENTERPRISE_VALUE / TTM_EBITDA, "8.89x; StockAnalysis 8.89x. Yahoo shows 17.1x on a different EBITDA definition — use StockAnalysis / S&P $25.38B"),
    ("P/B", MARKET_CAP / BOOK_EQUITY, "Book $85.49B, $14.95/share; tangible book -$33.3B after $71.4B goodwill + $47.1B intangibles"),
    ("P/OCF (TTM)", MARKET_CAP / TTM_OCF, "OCF $13.40B"),
    ("Dividend yield", DIVIDEND / PRICE, "15 years of increases; GAAP payout 226%, FCF payout 89%"),
    ("Net debt / TTM FCF", NET_DEBT / TTM_FCF, "4.7x — FCF-multiple gray zone; do not use FCF as primary scenario lens"),
    ("Interest coverage (EBIT)", TTM_EBIT / TTM_INTEREST, "7.0x; StockAnalysis 6.98x"),
]
for row, values in enumerate(metrics, metric_start + 1):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            if "yield" in values[0] or values[0] == "Dividend yield":
                cell.number_format = "0.0%"
            elif values[0] in {"Interest coverage (EBIT)", "Net debt / TTM FCF"}:
                cell.number_format = "0.00"
            else:
                cell.number_format = "0.00x"
widths(ws, [36, 28, 110, 14])

# 2. WACC
ws = wb.create_sheet("WACC")
title(ws, "Pfizer — WACC", 4, "CAPM and debt-weighted cost of capital")
header(ws, 3, ["Component", "Value", "Source / formula"])
wacc_rows = [
    ("Risk-free rate", rf / 100, "CNBC US10Y 10-year Treasury, November 3, 2026 (4.915%)"),
    ("Equity risk premium", erp / 100, "Model assumption"),
    ("Levered beta (5Y)", beta, "StockAnalysis; Pfizer is a low-vol yield stock"),
    ("Cost of equity", cost_equity / 100, "Risk-free rate + beta x ERP"),
    ("Pre-tax cost of debt", pretax_debt_cost / 100, "TTM interest expense $2,699M / total debt $63,480M"),
    ("Tax rate", tax_rate / 100, "Company adjusted ETR guidance ~15%; TTM statutory rate is a tax benefit from impairments and is not used"),
    ("Market cap ($M)", MARKET_CAP, "Price x shares"),
    ("Total debt ($M)", TOTAL_DEBT, "StockAnalysis, June 28, 2026"),
    ("Equity weight", equity_weight, "Market cap / (market cap + debt)"),
    ("Debt weight", debt_weight, "Debt / (market cap + debt)"),
    ("After-tax debt cost", pretax_debt_cost / 100 * (1 - tax_rate / 100), "Kd x (1 - tax rate)"),
    ("WACC", wacc / 100, "E/V x Ke + D/V x Kd x (1 - t); StockAnalysis shows 5.13%"),
    ("Scenario discount rates", "n/a — P/E framework", "Scenarios capitalize FY2031 adjusted EPS at an exit P/E rather than discounting a terminal equity value"),
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
widths(ws, [30, 22, 110, 14])

# 3. Scenarios
ws = wb.create_sheet("Scenarios")
title(
    ws,
    "Pfizer — FY2031 Adjusted EPS x Exit P/E Scenarios",
    5,
    "Primary lens is non-GAAP EPS because TTM GAAP is impairment-distorted and FCF multiples fail the 4.7x net-debt/FCF gray-zone test. USD millions except per-share figures.",
)
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Notes"])
keys = ("Bear", "Base", "Bull")
scenario_rows = [
    (
        "Revenue CAGR (5Y from TTM)",
        *(SCENARIOS[k]["rev_cagr"] for k in keys),
        "From TTM $63.70B. Street 3Y revenue growth forecast is -4.2%; FY2026e $62.22B, FY2027e $59.89B",
    ),
    (
        "FY2031 revenue ($M)",
        *(SCENARIOS[k]["term_rev"] for k in keys),
        "TTM x (1+CAGR)^5. Bear: cliffs without replacement. Base: Seagen/Vyndaqel/cost saves offset. Bull: obesity + ADC scale",
    ),
    (
        "FY2031 adj. EPS",
        *(SCENARIOS[k]["eps"] for k in keys),
        "Non-GAAP. FY2026e $2.96, FY2027e $2.88. Bear assumes cliffs without pipeline offset; bull assumes berobenatide plus ADC growth",
    ),
    (
        "Exit P/E",
        *(SCENARIOS[k]["pe"] for k in keys),
        "Current FY2026 fwd P/E is 10.3x. Bear 8x is a no-growth big-pharma floor; bull 12x is a modest re-rate if growth returns",
    ),
    (
        "Target price",
        *(SCENARIOS[k]["target"] for k in keys),
        "FY2031 adj. EPS x exit P/E, undiscounted. Near-term cash is returned as a 5.6% dividend rather than modeled as a PV residual",
    ),
    (
        "Upside / (downside)",
        *(SCENARIOS[k]["upside"] for k in keys),
        "Versus $30.52 close",
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
        "FCF margin (cross-check)",
        *(SCENARIOS[k]["fcf_margin"] for k in keys),
        "TTM FCF margin 17.3%. Bear assumes mix shift and pricing pressure; base holds near mid-teens",
    ),
    (
        "FY2031 FCF ($M)",
        *(SCENARIOS[k]["term_fcf"] for k in keys),
        "Terminal revenue x FCF margin",
    ),
    (
        "Exit FCF multiple",
        *(SCENARIOS[k]["fcf_mult"] for k in keys),
        "Cross-check only",
    ),
    (
        "Implied EV ($M)",
        *(SCENARIOS[k]["fcf_ev"] for k in keys),
        "FCF x multiple",
    ),
    (
        "Less net debt ($M)",
        *(-NET_DEBT for _k in keys),
        "Held at today's $51.8B; de-levering is a bull/base assumption not credited here",
    ),
    (
        "FCF-implied equity ($M)",
        *(SCENARIOS[k]["fcf_equity"] for k in keys),
        "Bear equity is slightly negative — this is why FCF is not the primary lens",
    ),
    (
        "FCF-implied price",
        *(SCENARIOS[k]["fcf_price"] for k in keys),
        "Shown to document the gray-zone failure, not as a target",
    ),
]
pct_rows = {
    "Revenue CAGR (5Y from TTM)",
    "Upside / (downside)",
    "Probability",
    "FCF margin (cross-check)",
}
usd_rows = {"Target price", "Weighted value/share", "FY2031 adj. EPS", "FCF-implied price"}
mult_rows = {"Exit P/E", "Exit FCF multiple"}
for row, values in enumerate(scenario_rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col in (2, 3, 4) and values[0] in pct_rows and isinstance(value, float):
            cell.number_format = "0.0%"
        elif col in (2, 3, 4) and values[0] in usd_rows and isinstance(value, float):
            cell.number_format = "$0.00"
        elif col in (2, 3, 4) and values[0] in mult_rows and isinstance(value, float):
            cell.number_format = "0.0x"
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
        "28 analysts, average PT $29.26 (median $28.50, low $25, high $36). "
        "StockAnalysis consensus rating Hold on the overview, Buy on the forecast page; "
        "the rating mix is 8 Strong Buy / 2 Buy / 16 Hold / 1 Sell / 1 Strong Sell. "
        f"Base ${SCENARIOS['Base']['target']:.2f} is {SCENARIOS['Base']['target'] / ANALYST_AVG_PT - 1:+.1%} vs the average target. "
        f"Probability-weighted FV ${weighted_value:.2f} is {weighted_value / ANALYST_AVG_PT - 1:+.1%} vs the average target."
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
        "Primary lens is FY2031 adjusted EPS x exit P/E. Trailing GAAP EPS of $0.76 is not usable: "
        "TTM pretax of $4.21B sits $14.9B below EBIT excluding unusual items because of $8.95B writedowns, "
        "$3.27B merger/restructuring and $1.53B legal settlements. FCF of $10.99B is real, but net debt of "
        "$51.8B is 4.7x FCF. At an 8x bear FCF multiple the implied EV is below net debt, so the FCF "
        "framework produces a negative bear equity value. That is a framework failure, not a forecast of insolvency. "
        "Dividend yield of 5.64% is ballast; FCF payout is 89% and GAAP payout is 226%."
    ),
    fill=gray,
)
ws.merge_cells(start_row=fv_row + 3, start_column=2, end_row=fv_row + 3, end_column=5)
ws.row_dimensions[fv_row + 2].height = 72
ws.row_dimensions[fv_row + 3].height = 88
widths(ws, [36, 16, 16, 16, 100])

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Pfizer — Actuals Source Audit", 5, "Financial statement figures in USD millions unless noted; fiscal year ends December 31")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/pfe"
q2 = "https://s206.q4cdn.com/795948973/files/doc_financials/2026/q2/Q2-2026-PFE-Earnings-Release-FINAL.pdf"
audit = [
    ("Stock price", "$30.52", f"{sa}/", "2026-10-30", "Close +1.90%; after-hours $30.45; 52-week $23.62-$30.67"),
    ("Market cap", "$173.95B", f"{sa}/statistics/", "2026-10-30", "5.70B shares"),
    ("Enterprise value", "$225.73B", f"{sa}/statistics/", "2026-10-30", "MC + debt - cash"),
    ("Shares outstanding", "5.70B", f"{sa}/statistics/", "2026-10-30", "+0.34% YoY; -0.56% QoQ; filing-date count 5,700M at Jun-26"),
    ("TTM diluted shares", "5,726M", f"{sa}/financials/income-statement/", "2026-06-28", "FY2025 diluted 5,713M"),
    ("Revenue TTM", "$63,696M", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $62,579; FY24 $63,627; FY23 $59,554; FY22 $101,175"),
    ("Revenue FY2022", "$101,175M", f"{sa}/financials/income-statement/", "2022-12-31", "COVID peak; not an organic baseline"),
    ("Gross profit TTM", "$47,591M (74.7%)", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 75.8%; FY23 59.7% (COVID mix)"),
    ("SG&A TTM", "$12,915M", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $12,964M"),
    ("R&D TTM", "$11,011M", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $10,437M; company invested $10.4B internal R&D in FY25"),
    ("Amortization of intangibles TTM", "$4,821M", f"{sa}/financials/income-statement/", "2026-06-28", "Seagen and other acquired intangibles"),
    ("Operating income TTM", "$18,844M (29.6%)", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $19,164M; FY23 $6,317M"),
    ("Interest expense TTM", "$2,699M", f"{sa}/financials/income-statement/", "2026-06-28", "Cash interest paid $2,797M"),
    ("EBT excluding unusual TTM", "$19,119M", f"{sa}/financials/income-statement/", "2026-06-28", "Clean operating earnings before charges"),
    ("Asset writedown TTM", "$8,948M", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $4,940M; Q2'26 alone $4.3B non-cash impairments"),
    ("Merger & restructuring TTM", "$3,271M", f"{sa}/financials/income-statement/", "2026-06-28", "Cost-realignment program"),
    ("Legal settlements TTM", "$1,526M", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $1,057M"),
    ("Pretax income TTM", "$4,211M", f"{sa}/financials/income-statement/", "2026-06-28", "Gap vs EBIT-ex-unusual is the quality issue"),
    ("Income tax TTM", "-$164M", f"{sa}/financials/income-statement/", "2026-06-28", "Tax benefit; adjusted ETR guided ~15%"),
    ("Net income TTM", "$4,334M", f"{sa}/financials/income-statement/", "2026-06-28", "GAAP; -59.7% YoY"),
    ("GAAP EPS TTM", "$0.76", f"{sa}/financials/income-statement/", "2026-06-28", "FY25 $1.36; FY22 $5.47"),
    ("EBITDA TTM", "$25,383M", f"{sa}/statistics/", "2026-06-28", "D&A $6,539M"),
    ("Cash & STI", "$11,704M", f"{sa}/financials/balance-sheet/", "2026-06-28", "Cash $976M + STI $10,723M"),
    ("Total debt", "$63,480M", f"{sa}/financials/balance-sheet/", "2026-06-28", "ST $94 + CPLTD $2,614 + LT $60,772; Yahoo Key Stats matches"),
    ("Net cash (debt)", "-$51,776M", f"{sa}/financials/balance-sheet/", "2026-06-28", "-$9.04/share"),
    ("Goodwill", "$71,419M", f"{sa}/financials/balance-sheet/", "2026-06-28", "FY22 $51,375M; Seagen and subsequent deals"),
    ("Other intangibles", "$47,053M", f"{sa}/financials/balance-sheet/", "2026-06-28", "Down from $64,900M FY23 as amortization and impairments run"),
    ("Total assets", "$201,131M", f"{sa}/financials/balance-sheet/", "2026-06-28", "FY23 peak $226,501M"),
    ("Common equity", "$85,190M", f"{sa}/financials/balance-sheet/", "2026-06-28", "Treasury stock -$115,194M; BVPS $14.95"),
    ("Tangible book", "-$33,282M", f"{sa}/financials/balance-sheet/", "2026-06-28", "-$5.84/share"),
    ("Preferred stock", "None reported", f"{sa}/financials/balance-sheet/", "2026-06-28", "No preferred equity line"),
    ("OCF TTM", "$13,401M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "FY25 $11,704M; FY22 $29,267M"),
    ("Capex TTM", "$2,416M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "FY25 $2,629M"),
    ("FCF TTM", "$10,985M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "OCF - capex; margin 17.25%"),
    ("Cash acquisitions TTM", "$6,927M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "Metsera $8.0B consideration (Nov 2025); investing CF - capex gap $3.3B"),
    ("Investing CF TTM", "-$5,685M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "Gap vs capex is acquisitions, not maintenance capex"),
    ("Dividends TTM", "$9,785M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "$1.72/share; FCF payout 89%"),
    ("Buybacks TTM", "$0", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "None in 2026 YTD; $3.3B authorization remains; guidance assumes none in 2026"),
    ("SBC TTM", "$947M", f"{sa}/financials/cash-flow-statement/", "2026-06-28", "1.5% of revenue"),
    ("Q2'26 revenue", "$15,034M", q2, "2026-08-04", "+3% reported / +1% operational; ex-COVID +5% operational"),
    ("Q2'26 reported EPS", "-$0.04", q2, "2026-08-04", "$4.3B non-cash intangible impairments"),
    ("Q2'26 adjusted EPS", "$0.77", q2, "2026-08-04", "Beat $0.68 consensus; four straight beats"),
    ("Q2'26 Eliquis", "$2,425M", q2, "2026-08-04", "+19% operational; 1H $4,591M"),
    ("Q2'26 Vyndaqel family", "$1,762M", q2, "2026-08-04", "+8% operational; 1H $3,364M"),
    ("Q2'26 Prevnar family", "$1,337M", q2, "2026-08-04", "-4% operational; 1H $3,027M"),
    ("Q2'26 Ibrance", "$1,058M", q2, "2026-08-04", "Flat operational; 1H $2,066M"),
    ("Q2'26 Padcev", "$667M", q2, "2026-08-04", "+23% operational; 1H $1,258M"),
    ("Q2'26 Xtandi", "$534M", q2, "2026-08-04", "-6%; alliance revenue; 1H $978M"),
    ("Q2'26 Nurtec", "$421M", q2, "2026-08-04", "+17% operational; 1H $774M"),
    ("Q2'26 Lorbrena", "$354M", q2, "2026-08-04", "+37% operational; 1H $659M"),
    ("Q2'26 Comirnaty", "$261M", q2, "2026-08-04", "-34% operational; 1H $493M"),
    ("Q2'26 Paxlovid", "$21M", q2, "2026-08-04", "-95% operational; 1H $207M"),
    ("FY2026 revenue guide", "$60.5-62.5B", q2, "2026-08-04", "Raised $500M at midpoint; COVID products now ~$4B vs ~$5B prior"),
    ("FY2026 adj. EPS guide", "$2.80-$3.00", q2, "2026-08-04", "Reaffirmed; absorbs $0.10 Innovent IPR&D"),
    ("Cost savings", "$5.7B by 2026; +$3.0B through 2029", q2, "2026-08-04", "Additional $2.5B from 2027-2029 announced Q2"),
    ("FY2026 consensus rev", "$62.22B", f"{sa}/forecast/", "2026-10-17", "25 analysts; range $61.2-$63.3B"),
    ("FY2026 consensus EPS", "$2.96", f"{sa}/forecast/", "2026-10-17", "Non-GAAP; 24 analysts; range $2.88-$3.07"),
    ("FY2027 consensus rev", "$59.89B", "https://finance.yahoo.com/quote/PFE/analysis/", "2026-11-03", "23 analysts; -3.75%; StockAnalysis FY2027 gated on the table, visible in the header as $59.86B"),
    ("FY2027 consensus EPS", "$2.88", "https://finance.yahoo.com/quote/PFE/analysis/", "2026-11-03", "22 analysts; range $2.52-$3.15"),
    ("Q3'26 consensus", "Rev $15.88B / EPS $0.73", "https://finance.yahoo.com/quote/PFE/analysis/", "2026-11-03", "17/19 analysts; results due Nov 3, 2026"),
    ("EPS revisions 30d", "FY26 1 up / 4 down; FY27 2 up / 3 down", "https://finance.yahoo.com/quote/PFE/analysis/", "2026-11-03", "FY26 $2.97 to $2.96; FY27 $2.90 to $2.88"),
    ("Analyst PT", "$29.26 avg / $28.50 med / $25-$36", f"{sa}/forecast/", "2026-10-17", "28 analysts"),
    ("Beta", "0.28", f"{sa}/statistics/", "2026-10-30", "Five-year"),
    ("U.S. 10Y Treasury", "4.915%", "https://www.cnbc.com/quotes/US10Y", "2026-11-03", "Risk-free rate"),
    ("Next earnings", "Nov 3, 2026", f"{sa}/", "2026-10-30", "Q3 FY2026; already-released Q2 is not a remaining catalyst"),
    ("Ex-dividend", "Nov 6, 2026", f"{sa}/", "2026-10-30", "$0.43 quarterly"),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [36, 42, 92, 14, 78])

# 5. Questions
ws = wb.create_sheet("Questions")
title(ws, "Pfizer — Open Questions", 4, "Items that can change valuation or conviction")
header(ws, 3, ["#", "Question", "Why it matters", "Best evidence / next check"])
questions = [
    (1, "What does Q3 FY2026 (due November 3) show for Eliquis net price, Padcev share, Vyndaqel diagnosis rates, and COVID run-rate versus the $4B full-year COVID assumption?", "Q3 is the last print before the 2026 guide is locked. A miss on Eliquis price or a further COVID cut would pull FY2026 EPS toward the $2.80 floor.", "Q3 release and call, November 3, 2026."),
    (2, "What is the remaining U.S. and ex-U.S. exclusivity timeline for Eliquis, Ibrance and Xtandi, and how much of 2027-2031 revenue is already contractually lost to IRA negotiation or generic entry?", "Street FY2027 revenue is already -3.8%. If cliffs are steeper than that, the base-case $3.00 FY2031 EPS does not hold.", "10-K patent table; IRA selected-drug list; Q3 commentary."),
    (3, "Will berobenatide (PF'3944 / Metsera monthly GLP-1) start the planned 10 Phase 3 studies in 2026, and what is the injectable-combination CVR probability?", "Metsera cost $8.0B plus up to $2.3B CVR. Obesity is the only path to a bull-case re-rate. A delay or a GI-tolerability miss versus Lilly/Novo weekly injectables kills the bull case.", "Phase 3 start 8-Ks; CVR milestone disclosures."),
    (4, "Which assets drove the $4.3B Q2 and $8.9B TTM intangible impairments, and is another charge coming as Seagen, Biohaven or Metsera purchase-accounting is finalized?", "Impairments are why GAAP EPS is $0.76. Another large charge would not change cash but would keep trailing P/E unusable and could signal pipeline write-offs.", "Q2 10-Q footnote; Q3 impairment line."),
    (5, "Is the $5.7B 2026 cost-realignment plus $3.0B 2027-2029 program dropping to the bottom line or being reinvested in obesity and oncology R&D?", "Adjusted SI&A is already guided $12.5-13.5B. If savings are reinvested, FY2027 EPS stays at $2.88 rather than recovering.", "Adjusted SI&A and R&D vs guide; 2027 guide on the Q3 call."),
    (6, "What is the cash tax rate once impairments roll off? TTM tax is a $164M benefit; adjusted ETR is guided at ~15%.", "A 15% vs 21% cash tax rate is ~$0.20 of FY2031 EPS.", "Cash taxes paid $4.73B TTM vs pretax $4.21B — the cash tax line needs reconciling at Q3."),
    (7, "How much of Seagen's ADC pipeline (beyond Padcev, Adcetris, Tivdak, Tukysa) is still live, and what is Padcev's duration in 1L la/mUC and MIBC?", "Padcev is the cleanest growth product (+23% in Q2). Duration and competitive ADCs (Daiichi/Astra, Gilead) set the oncology growth rate.", "Pipeline page update with Q3; EV-304 / EV-302 follow-up."),
    (8, "What is the Vyndamax U.S. patent-settlement cash-flow timing after 2028, and how much of the $3.36B 1H franchise is U.S. vs international?", "Management said post-2028 cash flow benefits from the settlement. If U.S. generic entry is earlier, Specialty Care growth stalls.", "10-K patent/settlement footnote; geographic split."),
    (9, "Does the Innovent licensing IPR&D charge of ~$0.10 in Q3 change 2026 adjusted EPS guide, or is it already absorbed in the $2.80-$3.00 range?", "Guide was reaffirmed in August as absorbing the $0.10. Confirm on the Q3 print.", "Q3 acquired IPR&D line vs $650M."),
    (10, "When does Pfizer resume buybacks? Authorization is $3.3B and 2026 guidance assumes zero. De-levering is the stated precondition.", "At 4.7x FCF net debt, buybacks are a 2028+ option, not a 2026 EPS lever. A surprise resume would be bullish for per-share value.", "Q3 capital-allocation remarks; net-debt trajectory."),
    (11, "What is customer/wholesaler concentration, and how much of U.S. net price for Eliquis is IRA, 340B, or channel mix rather than list price?", "Q2 Eliquis growth was 'lower rebates and channel mix.' That is not volume and can reverse.", "10-K major-customer note; IRA negotiation status for apixaban."),
    (12, "How will TrumpRx.gov, MFN pricing talk, and the voluntary U.S. government pricing agreements hit 2027 net price?", "Big-pharma net-price risk is the political overlay on every cliff. A 200-300 bps net-price cut is a bear-case input.", "Q3 political/pricing Q&A; 2027 guide."),
    (13, "Is Cecile Guegan remaining interim CFO, and does the finance-leadership gap change capital-allocation discipline?", "Interim CFO through a patent-cliff window is a governance flag, not a thesis-breaker.", "Q3 call; any permanent CFO 8-K."),
    (14, "What remains of the Biohaven migraine franchise beyond Nurtec ($421M in Q2), and is Vydura ex-U.S. material?", "Migraine was pitched as a 1.2 billion-patient market. Current revenue is still a small fraction of that.", "Nurtec geographic split; pipeline CGRP follow-ons."),
    (15, "Investing CF of -$5.7B vs capex of -$2.4B left a $3.3B gap. After Metsera, is 2027 a harvest year for FCF or another BD year?", "StockAnalysis shows FY2026e FCF of $19.2B, more than double TTM. That only happens if acquisitions stop. Confirm BD pipeline.", "Q3 BD commentary; 2027 FCF if guided."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 88, 72, 52])

# 6. Sources
ws = wb.create_sheet("Sources")
title(ws, "Pfizer — Sources", 4, "Public sources accessed November 3, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Price, range, market cap, EV, dividend, earnings date"),
    (2, "StockAnalysis financials overview", f"{sa}/financials/", "Revenue, margins, FCF history"),
    (3, "StockAnalysis income statement", f"{sa}/financials/income-statement/", "P&L lines including unusual items"),
    (4, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, goodwill, equity, shares"),
    (5, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, dividends, acquisitions"),
    (6, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation ratios, beta, EV/EBITDA, payout"),
    (7, "StockAnalysis forecast", f"{sa}/forecast/", "FY2026 consensus, price targets, rating mix"),
    (8, "StockAnalysis ratings", f"{sa}/ratings/", "Individual analyst targets, Oct 2026"),
    (9, "StockAnalysis company profile", f"{sa}/company/", "Identity, segments, executives, HQ"),
    (10, "Yahoo Finance analysis", "https://finance.yahoo.com/quote/PFE/analysis/", "FY2027 estimates, Q3 consensus, revisions, earnings history"),
    (11, "Yahoo Finance key statistics", "https://finance.yahoo.com/quote/PFE/key-statistics/", "EV, cash, debt, beta cross-check"),
    (12, "Pfizer Q2 2026 earnings release", q2, "Guide, product revenues, impairments, cost saves, capital allocation"),
    (13, "Pfizer Q2 2026 prepared remarks", "https://s206.q4cdn.com/795948973/files/doc_financials/2026/q2/Q2-2026-Earnings-Conference-Call-Prepared-Remarks-FINAL.pdf", "Seagen, Metsera, Biohaven framing; dividend commitment"),
    (14, "Pfizer 2026 proxy", "https://s206.q4cdn.com/795948973/files/doc_financials/2026/sr/interactive_proxy/HTML1/ceoletter.htm", "FY2025 capital allocation, Metsera, 3SBio, pipeline counts"),
    (15, "CNBC US10Y", "https://www.cnbc.com/quotes/US10Y", "Risk-free rate 4.915%"),
    (16, "Pfizer dividend release", "https://www.pfizer.com/news/press-release/press-release-detail/pfizer-declares-third-quarter-2026-dividend", "351st consecutive quarterly dividend"),
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
print(f"Beta: {beta:.2f} | Cost of equity: {cost_equity:.2f}% | WACC: {wacc:.2f}%")
print(f"Net debt / FCF: {NET_DEBT / TTM_FCF:.2f}x | Fwd P/E FY26: {PRICE / FY26_EPS:.2f}x | FY27: {PRICE / FY27_EPS:.2f}x")
for name, case in SCENARIOS.items():
    print(
        f"{name}: CAGR {case['rev_cagr']:.1%}, EPS ${case['eps']:.2f}, P/E {case['pe']:.1f}x, "
        f"target ${case['target']:.2f} ({case['upside']:+.1%}), FCF-implied ${case['fcf_price']:.2f}"
    )
print(f"Probability-weighted fair value: ${weighted_value:.2f} ({weighted_value / PRICE - 1:+.1%})")
print(f"Analyst avg PT ${ANALYST_AVG_PT:.2f} | bear < 90% of price: {SCENARIOS['Bear']['target'] < PRICE * 0.9}")
print(f"Wrote and verified {OUT}")
