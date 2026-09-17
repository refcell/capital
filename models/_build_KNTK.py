#!/usr/bin/env python3
"""Build the Kinetik Holdings six-sheet valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


OUT = Path(__file__).with_name("2026-09-17 Kinetik Holdings Model.xlsx")
PRICE = 53.84
SHARES = 162.38  # millions; Class A plus Class C economic interests
MARKET_CAP = 8.74  # billions
DEBT = 3.977  # billions
CASH = 0.0113  # billions
NET_DEBT = DEBT - CASH
ENTERPRISE_VALUE = MARKET_CAP + NET_DEBT
TTM_REVENUE = 1.886  # billions
TTM_GAAP_EBITDA = 0.627  # billions
FY26_ADJ_EBITDA = 1.07  # midpoint of company guidance, billions
TTM_OCF = 0.640  # billions
TTM_STANDARD_FCF = 0.157  # billions
ANNUALIZED_DCF = 0.752  # 1H26 distributable cash flow x 2, billions
FY26_REVENUE = 2.06  # S&P Global consensus, billions
FY26_ADJ_EPS = 1.47

SCENARIOS = {
    "Bear": {"rev_cagr": 0.02, "ebitda_margin": 0.38, "multiple": 8.0, "weight": 0.20},
    "Base": {"rev_cagr": 0.08, "ebitda_margin": 0.45, "multiple": 10.5, "weight": 0.55},
    "Bull": {"rev_cagr": 0.12, "ebitda_margin": 0.50, "multiple": 12.0, "weight": 0.25},
}
for case in SCENARIOS.values():
    case["terminal_revenue"] = FY26_REVENUE * (1 + case["rev_cagr"]) ** 5
    case["terminal_ebitda"] = case["terminal_revenue"] * case["ebitda_margin"]
    case["implied_ev"] = case["terminal_ebitda"] * case["multiple"]
    case["target"] = (case["implied_ev"] - NET_DEBT) * 1000 / SHARES
weighted_value = sum(case["target"] * case["weight"] for case in SCENARIOS.values())

assert SCENARIOS["Bear"]["target"] < PRICE
assert abs(SCENARIOS["Base"]["target"] - 57.31) / 57.31 < 0.20
assert 10 < weighted_value < 150

rf, erp, beta = 4.996, 5.0, 0.78
cost_equity = rf + beta * erp
pretax_debt_cost = 5.47
tax_rate = 10.0
equity_weight = MARKET_CAP / (MARKET_CAP + DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * cost_equity + debt_weight * pretax_debt_cost * (1 - tax_rate / 100)

wb = Workbook()
navy, blue, gold, white = "17365D", "D9EAF7", "D8B34B", "FFFFFF"
thin = Side(style="thin", color="A6A6A6")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, row, col, value, *, bold=False, fill=None, color="000000", size=10):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Aptos", size=size, bold=bold, color=color)
    cell.fill = PatternFill("solid", fgColor=fill) if fill else PatternFill(fill_type=None)
    cell.border = border
    cell.alignment = Alignment(vertical="top", wrap_text=True)
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
title(ws, "Kinetik Holdings (KNTK) — Valuation", 4, "Quote date: September 16, 2026 | Model date: September 17, 2026")
facts = [
    ("Company", "Kinetik Holdings Inc.", "Integrated Delaware Basin midstream and Permian-to-Gulf Coast pipeline platform"),
    ("Ticker", "NYSE: KNTK", "Energy / Oil & Gas Midstream"),
    ("Price", PRICE, "September 16 close"),
    ("Economic shares (M)", SHARES, "78.94M Class A plus 83.4M Class C interests at June 30"),
    ("Market capitalization ($B)", MARKET_CAP, "StockAnalysis current value"),
    ("Enterprise value ($B)", ENTERPRISE_VALUE, "Market cap plus debt less cash"),
    ("Net debt ($B)", NET_DEBT, "June 30 debt less cash"),
    ("Primary valuation lens", "EV / adjusted EBITDA", "Standardized FCF is depressed by a deliberate processing-capacity build cycle"),
    ("Stance", "Watch", "Strong operating momentum and 6% yield, but sale speculation and a full current multiple limit margin of safety"),
]
header(ws, 3, ["Field", "Value", "Comment"])
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))

header(ws, 15, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E", 19.66, "GAAP earnings attributable to common; noncontrolling interests complicate comparisons"),
    ("Forward P/E", 34.03, "FY2026 adjusted EPS consensus is unusually low relative to total enterprise cash generation"),
    ("P/S", MARKET_CAP / TTM_REVENUE, "Product-revenue gross presentation makes sales a weak primary denominator"),
    ("P/standardized FCF", MARKET_CAP / TTM_STANDARD_FCF, "Punitive during the KLII and system-expansion capital cycle"),
    ("P/annualized DCF", MARKET_CAP / ANNUALIZED_DCF, "1H26 distributable cash flow annualized; before growth capital"),
    ("EV/Sales", ENTERPRISE_VALUE / TTM_REVENUE, "High because pipeline affiliate economics are partly outside consolidated revenue"),
    ("EV/GAAP EBITDA", ENTERPRISE_VALUE / TTM_GAAP_EBITDA, "Provider standardized EBITDA excludes proportionate affiliate EBITDA"),
    ("EV/FY26 adjusted EBITDA", ENTERPRISE_VALUE / FY26_ADJ_EBITDA, "Primary current cross-check using company guidance midpoint"),
    ("Net debt/adjusted EBITDA", 3.84, "Company-reported June 30 leverage; meaningful but currently covered"),
    ("Dividend yield", 0.0602, "$3.24 annualized dividend"),
    ("Dividend coverage", 1.41, "1H26 distributable cash flow / declared dividends"),
]
for row, values in enumerate(metrics, 16):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if values[0] == "Dividend yield" and col == 2:
            cell.number_format = "0.0%"
widths(ws, [31, 24, 82, 14])

# 2. WACC
ws = wb.create_sheet("WACC")
title(ws, "Kinetik Holdings — WACC", 4, "CAPM cross-check; EV/adjusted EBITDA remains the primary valuation method")
header(ws, 3, ["Component", "Value", "Source / formula"])
wacc_rows = [
    ("Risk-free rate", rf / 100, "CNBC U.S. 10-year Treasury quote, September 17, 2026"),
    ("Equity risk premium", erp / 100, "Standard model assumption"),
    ("Levered beta", beta, "StockAnalysis five-year beta"),
    ("Cost of equity", cost_equity / 100, "Risk-free + beta × ERP"),
    ("Pre-tax cost of debt", pretax_debt_cost / 100, "TTM cash interest / June debt"),
    ("Tax rate", tax_rate / 100, "Normalized near Q2 reported 10.5%; TTM data-provider rate is distorted"),
    ("Market cap ($B)", MARKET_CAP, "September 16 quote"),
    ("Total debt ($B)", DEBT, "June 30 standardized balance sheet"),
    ("Equity weight", equity_weight, "Market cap / (market cap + debt)"),
    ("Debt weight", debt_weight, "Debt / (market cap + debt)"),
    ("After-tax debt cost", pretax_debt_cost / 100 * (1 - tax_rate / 100), "Kd × (1 − tax rate)"),
    ("WACC", wacc / 100, "E/V × Ke + D/V × Kd × (1 − t)"),
]
for row, values in enumerate(wacc_rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1 or values[0] == "WACC"), fill=(gold if values[0] == "WACC" else None))
        if col == 2 and values[0] not in {"Levered beta", "Market cap ($B)", "Total debt ($B)"}:
            cell.number_format = "0.00%"
widths(ws, [30, 20, 78, 14])

# 3. Scenarios
ws = wb.create_sheet("Scenarios")
title(ws, "Kinetik Holdings — EV / Adjusted EBITDA Scenarios", 6, "Five-year infrastructure build-out framework; financial figures in $B except per-share values")
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Notes"])
scenario_rows = [
    ("Revenue CAGR (5Y)", *(SCENARIOS[k]["rev_cagr"] for k in ("Bear", "Base", "Bull")), "From FY2026 consensus; product prices can move revenue without equal EBITDA change"),
    ("Terminal revenue ($B)", *(SCENARIOS[k]["terminal_revenue"] for k in ("Bear", "Base", "Bull")), "FY2026 consensus compounded five years"),
    ("Adjusted EBITDA margin", *(SCENARIOS[k]["ebitda_margin"] for k in ("Bear", "Base", "Bull")), "Includes proportionate economics of unconsolidated pipelines"),
    ("Terminal adjusted EBITDA ($B)", *(SCENARIOS[k]["terminal_ebitda"] for k in ("Bear", "Base", "Bull")), "Terminal revenue × adjusted EBITDA margin"),
    ("Exit EV/EBITDA multiple", *(SCENARIOS[k]["multiple"] for k in ("Bear", "Base", "Bull")), "8x stress / 10.5x execution / 12x premium growth"),
    ("Implied EV ($B)", *(SCENARIOS[k]["implied_ev"] for k in ("Bear", "Base", "Bull")), "Terminal adjusted EBITDA × exit multiple"),
    ("Less net debt ($B)", *(NET_DEBT for _ in range(3)), "No assumed deleveraging despite retained cash generation"),
    ("Economic shares (M)", *(SHARES for _ in range(3)), "Class A plus Class C interests; no assumed buybacks"),
    ("Target price", *(SCENARIOS[k]["target"] for k in ("Bear", "Base", "Bull")), "(Implied EV − net debt) / shares"),
    ("Upside / (downside)", *((SCENARIOS[k]["target"] / PRICE - 1) for k in ("Bear", "Base", "Bull")), "Versus $53.84"),
    ("Probability", *(SCENARIOS[k]["weight"] for k in ("Bear", "Base", "Bull")), "20% / 55% / 25%"),
    ("Weighted value/share", *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in ("Bear", "Base", "Bull")), "Contribution to fair value"),
]
for row, values in enumerate(scenario_rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col in (2, 3, 4) and values[0] in {"Revenue CAGR (5Y)", "Adjusted EBITDA margin", "Upside / (downside)", "Probability"}:
            cell.number_format = "0.0%"
        elif col in (2, 3, 4) and values[0] not in {"Exit EV/EBITDA multiple", "Economic shares (M)"}:
            cell.number_format = "$0.00"
put(ws, 17, 1, "Probability-weighted fair value", bold=True, fill=gold)
put(ws, 17, 2, weighted_value, bold=True, fill=gold).number_format = "$0.00"
put(ws, 18, 1, "Upside from current price", bold=True, fill=gold)
put(ws, 18, 2, weighted_value / PRICE - 1, bold=True, fill=gold).number_format = "0.0%"
widths(ws, [33, 18, 18, 18, 84, 14])

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Kinetik Holdings — Actuals Source Audit", 5, "Dollar figures are USD; GAAP and company-defined non-GAAP measures are labeled")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/kntk"
release = "https://www.businesswire.com/news/home/20260805695706/en/Kinetik-Reports-Record-Second-Quarter-2026-Results-and-Raises-Full-Year-2026-Guidance/"
audit = [
    ("Stock price", "$53.84", f"{sa}/", "2026-09-16", "Official close"),
    ("Market cap", "$8.74B", f"{sa}/", "2026-09-16", "Economic value includes Class C interests"),
    ("Enterprise value", "$12.71B", f"{sa}/statistics/", "2026-09-17", "Provider value"),
    ("Economic shares outstanding", "162.38M", f"{sa}/statistics/", "2026-09-17", "Class A plus Class C; current quoted class is 80.44M"),
    ("Revenue TTM", "$1.886B", f"{sa}/financials/", "2026-06-30", "GAAP; product sales dominate reported revenue"),
    ("Gross profit TTM", "$776.81M", f"{sa}/financials/", "2026-06-30", "GAAP standardized"),
    ("Operating income TTM", "$225.30M", f"{sa}/financials/", "2026-06-30", "GAAP standardized"),
    ("Net income attributable to common TTM", "$185.44M", f"{sa}/", "2026-06-30", "Provider headline common earnings"),
    ("EPS TTM", "$2.74", f"{sa}/", "2026-06-30", "Provider diluted EPS"),
    ("GAAP EBITDA TTM", "$626.68M", f"{sa}/statistics/", "2026-06-30", "Does not capture all proportionate affiliate EBITDA"),
    ("Operating cash flow TTM", "$639.73M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "GAAP standardized"),
    ("Capital expenditures TTM", "$482.90M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "Growth plus maintenance"),
    ("Standardized FCF TTM", "$156.84M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "OCF less all capex"),
    ("Cash and investments", "$11.28M", f"{sa}/financials/balance-sheet/", "2026-06-30", "Very low cash balance is normal with revolver liquidity"),
    ("Total debt", "$3.977B", f"{sa}/financials/balance-sheet/", "2026-06-30", "Short- and long-term debt plus leases in standardized figure"),
    ("Common equity", "-$1.185B", f"{sa}/financials/balance-sheet/", "2026-06-30", "Offset by $4.097B minority interest; common P/B is not meaningful"),
    ("Q2 revenue", "$581.44M", release, "2026-06-30", "GAAP; $490.8M product revenue"),
    ("Q2 net income incl. NCI", "$123.11M", release, "2026-06-30", "Only $49.54M attributable to Class A holders"),
    ("Q2 adjusted EBITDA", "$280.78M", release, "2026-06-30", "Company-defined non-GAAP"),
    ("1H26 distributable cash flow", "$375.76M", release, "2026-06-30", "Company-defined non-GAAP; 1.41x dividend coverage"),
    ("Q2 free cash flow", "$105.20M", release, "2026-06-30", "Company definition after growth capital"),
    ("FY2026 adjusted EBITDA guidance", "$1.04B-$1.10B", release, "2026-08-05", "Raised 7%; midpoint $1.07B"),
    ("FY2026 capex guidance", "~$560M", release, "2026-08-05", "Includes maintenance and accelerated expansion"),
    ("FY2026 revenue consensus", "$2.06B", f"{sa}/forecast/", "2026-09-10", "Nine analysts; visible range $1.8B-$2.2B"),
    ("FY2026 adjusted EPS consensus", "$1.47", f"{sa}/forecast/", "2026-09-10", "Non-GAAP diluted; visible range $0.62-$2.09"),
    ("FY2027 headline revenue", "$2.35B", f"{sa}/forecast/", "2026-09-10", "Detailed analyst table gated"),
    ("FY2027 headline EPS", "$2.18", f"{sa}/forecast/", "2026-09-10", "Adjusted diluted; detailed analyst table gated"),
    ("Average analyst target", "$57.31", f"{sa}/forecast/", "2026-09-10", "17 analysts; range $48-$70"),
    ("Beta", "0.78", f"{sa}/", "2026-09-16", "Five-year beta"),
    ("10Y Treasury", "4.996%", "https://www.cnbc.com/quotes/US10Y", "2026-09-17", "Latest displayed yield"),
    ("Next earnings", "November 4, 2026", f"{sa}/", "2026-09-16", "Estimated after market close"),
    ("Potential sale report", "Early-stage exploration", "https://www.reuters.com/business/energy/us-pipeline-operator-kinetik-exploring-potential-sale-sources-say-2026-09-10/", "2026-09-10", "Reuters report; no announced transaction or confirmed valuation"),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [34, 22, 92, 16, 72])

# 5. Questions
ws = wb.create_sheet("Questions")
title(ws, "Kinetik Holdings — Open Questions", 4, "Items that can materially change cash coverage, leverage or the terminal multiple")
header(ws, 3, ["#", "Question", "Why it matters", "Best evidence / next check"])
questions = [
    (1, "Is the reported sale exploration active, and what price would compensate holders for the 6% yield and KLII growth runway?", "Sale speculation appears embedded in the recent re-rating.", "Board disclosure, strategic-review announcement or transaction filing."),
    (2, "How much of record Q2 commodity-margin outperformance is repeatable?", "Fee cash flow is higher quality than spread- and commodity-linked earnings.", "Commodity margin bridge and hedge disclosure."),
    (3, "Can Kinetik complete KLII for approximately $260M and by mid-2028?", "Cost or schedule slippage would reduce FCF and delay deleveraging.", "Quarterly project spend, commitments and construction milestones."),
    (4, "What return and contract coverage support the processing expansion beyond KLII?", "Long-lead procurement precedes a final disclosed project budget.", "Customer commitments, minimum volumes and FID economics."),
    (5, "Why are current liabilities above current assets, and how much revolver liquidity is structurally required?", "A 0.68 current ratio increases dependence on capital-market access.", "$1.07B liquidity bridge and debt-maturity schedule."),
    (6, "How quickly can net debt/adjusted EBITDA fall below 3.5x while capex remains elevated?", "At 3.84x, debt limits optionality and magnifies multiple compression.", "2027-2028 leverage targets and retained DCF after dividends."),
    (7, "Does 1.41x first-half dividend coverage persist through the expansion cycle?", "The 6.0% yield is central to total return and the payout already exceeds common GAAP EPS.", "Quarterly DCF, declared dividends and maintenance capex."),
    (8, "How should Class A and Class C interests convert over time?", "Economic shares are twice the quoted Class A count, creating frequent per-share errors.", "Exchange agreement, tax receivable agreement and conversion schedule."),
    (9, "What explains negative common equity alongside $4.10B of minority interest?", "The Up-C and affiliate structure makes conventional P/B and ROE misleading.", "NCI ownership roll-forward and redemption rights."),
    (10, "How much customer concentration exists among Delaware Basin producers?", "Producer distress or acreage consolidation can change volumes and contract bargaining power.", "Top-ten customer revenue, acreage dedication and credit quality."),
    (11, "What percentage of revenue and EBITDA is fee-based versus commodity-sensitive?", "Revenue growth can overstate economic growth when product prices and gross presentation move.", "Fee/commodity margin disclosure and hedge book."),
    (12, "Can processed gas reach the nearly 2.2 Bcf/d Q4 exit rate after 2026 curtailments?", "Volume execution is the bridge into 2027 consensus growth.", "Monthly Waha conditions and Q3/Q4 throughput."),
    (13, "What does the EPIC Crude divestiture imply for pipeline segment durability?", "Pipeline EBITDA fell 14% YoY in Q2 after the sale.", "Pro-forma segment EBITDA and proceeds deployment."),
    (14, "Will Diamond Volt and ECCC expansion earn returns above the 7.6% WACC?", "Small projects accumulate into meaningful growth capital and execution risk.", "Project-level contracted EBITDA and payback."),
    (15, "Why have shares increased 10.35% YoY, and will future projects require more equity?", "Dilution can absorb enterprise growth before it reaches per-share value.", "Class conversions, compensation, acquisition issuance and financing plan."),
    (16, "What will November 4 earnings prove?", "The next release should test Q2 margin repeatability, volume acceleration and 2027 confidence.", "Q3 adjusted EBITDA, DCF coverage, capex and 2027 commentary."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 82, 70, 64])

# 6. Sources
ws = wb.create_sheet("Sources")
title(ws, "Kinetik Holdings — Sources", 4, "Public sources accessed September 17, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Quote, company identity, current market data and earnings date"),
    (2, "StockAnalysis financial overview", f"{sa}/financials/", "Historical revenue, profit, cash, debt, cash flow and margins"),
    (3, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, assets, common equity and minority interest"),
    (4, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, acquisitions, dividends, buybacks and FCF"),
    (5, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation, leverage, shares, profitability and standardized TTM data"),
    (6, "StockAnalysis forecast", f"{sa}/forecast/", "S&P Global revenue/EPS forecasts and analyst targets"),
    (7, "StockAnalysis company profile", f"{sa}/company/", "Business description, executives and listing details"),
    (8, "Kinetik Q2 2026 release", release, "Primary financials, segment results, guidance, liquidity and projects"),
    (9, "Kinetik investor relations", "https://ir.kinetik.com/", "Future releases, presentations and filings"),
    (10, "Reuters sale report", "https://www.reuters.com/business/energy/us-pipeline-operator-kinetik-exploring-potential-sale-sources-say-2026-09-10/", "Potential strategic sale context; headline independently surfaced by StockAnalysis"),
    (11, "CNBC U.S. 10-year Treasury", "https://www.cnbc.com/quotes/US10Y", "Risk-free rate"),
]
for row, values in enumerate(sources, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 38, 104, 72])

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False
    sheet.auto_filter.ref = sheet.dimensions

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
assert check.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check["Scenarios"]["B17"].value == weighted_value
print(f"WACC: {wacc:.2f}%")
for name, case in SCENARIOS.items():
    print(f"{name}: ${case['target']:.2f}")
print(f"Probability-weighted fair value: ${weighted_value:.2f}")
print(f"Workbook: {OUT}")
