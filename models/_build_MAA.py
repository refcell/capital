#!/usr/bin/env python3
"""Build the 2026-09-24 Mid-America Apartment Communities valuation workbook."""

from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


OUT = Path(__file__).with_name("2026-09-24 Mid-America Apartment Communities Model.xlsx")
PRICE = 117.78
SHARES = 118.95  # millions, common shares plus operating partnership units
MARKET_CAP = 14010.0  # $ millions
EV = 19670.0
DEBT = 5715.0
CASH = 51.84
NET_DEBT = 5640.07
FFO_2026 = 8.53
AFFO_2026 = 7.50
DIVIDEND = 6.12

NAVY = "17365D"
BLUE = "D9EAF7"
GREEN = "E2F0D9"
YELLOW = "FFF2CC"
WHITE = "FFFFFF"
thin = Side(style="thin", color="B7B7B7")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, row, col, value, *, bold=False, fill=None, fmt=None, wrap=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.border = border
    cell.font = Font(bold=bold, color=WHITE if fill == NAVY else "000000")
    cell.alignment = Alignment(vertical="top", wrap_text=wrap)
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    if fmt:
        cell.number_format = fmt
    return cell


def title(ws, text, end_col):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    cell = ws.cell(1, 1, text)
    cell.font = Font(size=15, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 24


def headers(ws, row, values):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=True, fill=BLUE, wrap=True)


wb = Workbook()
ws = wb.active
ws.title = "Valuation"
title(ws, "Mid-America Apartment Communities (NYSE: MAA) — Residential REIT Valuation", 4)
summary = [
    ("Company", "Mid-America Apartment Communities", "Model date", "2026-09-24"),
    ("Quote", "$117.78 at Sep. 23 close", "Shares / OP units", "118.95M"),
    ("Market capitalization", "$14.01B", "Enterprise value", "$19.67B"),
    ("Net debt", "$5.64B", "Portfolio", "104,698 units / 16 states + DC"),
    ("Primary lens", "P/FFO with AFFO cross-check", "Stance", "Watch"),
]
for r, row in enumerate(summary, 3):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, bold=c in (1, 3), fill=YELLOW if c in (1, 3) else None, wrap=True)

headers(ws, 10, ["Metric", "Current / Forward", "Interpretation", "Source date"])
metrics = [
    ("Trailing P/E", "34.43x", "Not primary: real-estate depreciation suppresses GAAP earnings", "2026-09-23"),
    ("FY2026E P/FFO", f"{PRICE / FFO_2026:.2f}x", "$117.78 / $8.53 company guidance midpoint", "2026-09-23"),
    ("FY2026E P/AFFO", f"{PRICE / AFFO_2026:.2f}x", "$117.78 / $7.50 guidance midpoint after recurring capex", "2026-09-23"),
    ("P/S", "6.31x", "Equity value relative to $2.22B TTM revenue", "2026-09-23"),
    ("P/OCF", "13.86x", "Useful cash cross-check, but OCF precedes real-estate investment", "2026-09-23"),
    ("EV/Sales", "8.87x", "High because apartments carry durable asset value and leverage", "2026-09-23"),
    ("EV/EBITDA", "15.89x", "Secondary enterprise cross-check", "2026-09-23"),
    ("P/B", "2.51x", "Historical-cost depreciation limits book-value usefulness", "2026-09-23"),
    ("Net debt / adjusted EBITDAre", "4.50x", "Company-reconciled leverage; investment-grade but meaningful", "2026-06-30"),
    ("Dividend yield", "5.20%", "$6.12 annualized; 81.6% of FY2026E Core AFFO", "2026-09-23"),
    ("Probability-weighted FV", "$143.30", "25% bear / 50% base / 25% bull; 21.7% price upside", "2026-09-24"),
]
for r, row in enumerate(metrics, 11):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 30
ws.column_dimensions["B"].width = 25
ws.column_dimensions["C"].width = 65
ws.column_dimensions["D"].width = 16
ws.freeze_panes = "A11"

ws = wb.create_sheet("WACC")
title(ws, "MAA Weighted Average Cost of Capital", 4)
headers(ws, 3, ["Component", "Value", "Calculation / Source", "Comment"])
rf = 0.05121
erp = 0.05
beta = 0.71
ke = rf + beta * erp
cost_debt = 195.47 / DEBT
equity_weight = MARKET_CAP / (MARKET_CAP + DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * ke + debt_weight * cost_debt
wacc_rows = [
    ("Risk-free rate", rf, "CNBC US10Y / Tradeweb", "Sep. 24, 2026 page snapshot"),
    ("Equity risk premium", erp, "Model assumption", "Standard US ERP"),
    ("Levered beta", beta, "StockAnalysis statistics", "Five-year beta"),
    ("Cost of equity", ke, "Rf + beta × ERP", "CAPM"),
    ("Pre-tax cost of debt", cost_debt, "$195.47M cash interest / $5,715M debt", "Observed TTM cash-cost proxy"),
    ("Tax rate", 0.0, "REIT structure", "No corporate tax shield assumed"),
    ("Market capitalization", MARKET_CAP, "StockAnalysis", "$ millions"),
    ("Total debt", DEBT, "StockAnalysis", "$ millions"),
    ("Equity weight", equity_weight, "MC / (MC + debt)", ""),
    ("Debt weight", debt_weight, "Debt / (MC + debt)", ""),
    ("Computed WACC", wacc, "E/V × Ke + D/V × Kd", "About 7.2%; provider estimate is 6.8%"),
]
for r, row in enumerate(wacc_rows, 4):
    for c, value in enumerate(row, 1):
        fmt = "0.00%" if c == 2 and r not in (10, 11) else None
        put(ws, r, c, value, bold=r == 14, fill=GREEN if r == 14 else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 28
ws.column_dimensions["B"].width = 18
ws.column_dimensions["C"].width = 42
ws.column_dimensions["D"].width = 48

ws = wb.create_sheet("Scenarios")
title(ws, "MAA Five-Year P/FFO Scenario Analysis", 6)
ws.merge_cells("A2:F2")
ws["A2"] = "REIT framework: terminal Core FFO/share × exit P/FFO. Core AFFO, dividend coverage and leverage are cross-checks."
ws["A2"].alignment = Alignment(wrap_text=True)
headers(ws, 4, ["Metric", "Bear", "Base", "Bull", "Units / Formula", "Interpretation"])
targets = {"Bear": 8.40 * 12.0, "Base": 10.00 * 14.5, "Bull": 11.40 * 16.0}
weights = {"Bear": 0.25, "Base": 0.50, "Bull": 0.25}
weighted_fv = sum(targets[k] * weights[k] for k in targets)
scenario_rows = [
    ("Revenue CAGR (5Y)", 0.010, 0.025, 0.040, "%", "Rent, occupancy, development and dispositions"),
    ("Terminal revenue", 2344.0, 2523.0, 2713.0, "$mm", "$2.23B FY2026E compounded five years"),
    ("Terminal Core FFO / share", 8.40, 10.00, 11.40, "$ / share", "Per-share result after financing and capital allocation"),
    ("Exit P/FFO", 12.0, 14.5, 16.0, "x", "Residential REIT range; bear reflects prolonged oversupply"),
    ("Target price", targets["Bear"], targets["Base"], targets["Bull"], "$ / share", "Core FFO/share × P/FFO"),
    ("Upside / (downside)", targets["Bear"] / PRICE - 1, targets["Base"] / PRICE - 1, targets["Bull"] / PRICE - 1, "%", "Versus $117.78 close"),
    ("Probability", weights["Bear"], weights["Base"], weights["Bull"], "%", "Weights sum to 100%"),
    ("Weighted value / share", targets["Bear"] * weights["Bear"], targets["Base"] * weights["Base"], targets["Bull"] * weights["Bull"], "$ / share", "Target × probability"),
    ("Probability-weighted FV", None, weighted_fv, None, "$ / share", "Sum of weighted values"),
    ("Upside from current", None, weighted_fv / PRICE - 1, None, "%", "Excludes dividends"),
    ("FY2026E dividend / Core AFFO", None, DIVIDEND / AFFO_2026, None, "%", "Current payout after recurring capex"),
    ("Current net debt / EBITDAre", None, 4.5, None, "x", "Company-reconciled leverage"),
]
for r, row in enumerate(scenario_rows, 5):
    for c, value in enumerate(row, 1):
        fmt = None
        if c in (2, 3, 4) and row[4] == "%":
            fmt = "0.0%"
        elif c in (2, 3, 4) and row[4] in ("$ / share", "$mm"):
            fmt = "$#,##0.00"
        put(ws, r, c, value, bold=r in (9, 13, 14), fill=GREEN if r in (13, 14) else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 31
for col in "BCD":
    ws.column_dimensions[col].width = 17
ws.column_dimensions["E"].width = 20
ws.column_dimensions["F"].width = 54
ws.freeze_panes = "A5"

urls = {
    "overview": "https://stockanalysis.com/stocks/maa/",
    "income": "https://stockanalysis.com/stocks/maa/financials/income-statement/",
    "balance": "https://stockanalysis.com/stocks/maa/financials/balance-sheet/",
    "cashflow": "https://stockanalysis.com/stocks/maa/financials/cash-flow-statement/",
    "statistics": "https://stockanalysis.com/stocks/maa/statistics/",
    "forecast": "https://stockanalysis.com/stocks/maa/forecast/",
    "metrics": "https://stockanalysis.com/stocks/maa/financials/metrics/",
    "profile": "https://stockanalysis.com/stocks/maa/company/",
    "release": "https://www.prnewswire.com/news-releases/maa-reports-second-quarter-2026-results-302838251.html",
    "transcript": "https://stockanalysis.com/stocks/maa/transcripts/658049-q2-2026/",
    "treasury": "https://www.cnbc.com/quotes/US10Y",
}
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "MAA Actuals Source Audit", 5)
headers(ws, 3, ["Data point", "Value", "Source URL", "As of", "Notes"])
audit = [
    ("Close price", "$117.78", urls["overview"], "2026-09-23", "Regular-session close"),
    ("Market cap / EV", "$14.01B / $19.67B", urls["statistics"], "2026-09-23", "Live market snapshot"),
    ("Shares / OP units", "118.95M", urls["statistics"], "2026-09-23", "116.02M common share class plus OP units"),
    ("Beta", "0.71", urls["statistics"], "2026-09-23", "Five-year beta"),
    ("TTM / FY2025 revenue", "$2.219B / $2.209B", urls["income"], "2026-06-30 / FY2025", "+0.85% TTM growth"),
    ("TTM operating income", "$596.50M", urls["income"], "2026-06-30", "26.88% margin"),
    ("TTM net income / D&A", "$399.29M / $640.84M", urls["income"], "2026-06-30", "D&A is primary GAAP-to-FFO bridge"),
    ("TTM FFO / share", "$987.22M / $8.25", urls["income"], "2026-06-30", "NAREIT-style provider data"),
    ("FY2025 AFFO / share", "$913.01M / $7.61", urls["income"], "FY2025", "After recurring capex"),
    ("Cash / debt / net debt", "$51.84M / $5.715B / $5.640B", urls["balance"], "2026-06-30", "Net debt reconciled by company"),
    ("OCF / real estate spend", "$1.011B / $804.52M", urls["cashflow"], "TTM 2026-06-30", "Spend includes development and acquisitions, not maintenance only"),
    ("Core FFO / AFFO guidance", "$8.53 / $7.50 midpoint", urls["release"], "FY2026", "Company non-GAAP diluted per-share guidance"),
    ("Consensus revenue / FFO", "$2.23B / $1.02B", urls["forecast"], "FY2026", "18 FFO analysts; $8.50/share"),
    ("Price target", "$141.44 avg; $121-$160", urls["forecast"], "2026-09-21", "26 analysts; Hold"),
    ("Q2 same-store growth", "Revenue -0.3%; expense +0.8%; NOI -1.0%", urls["release"], "2026-Q2", "Supply pressure remains visible"),
    ("Occupancy / turnover", "95.3% / 39.6%", urls["release"], "2026-Q2", "Historically low turnover"),
    ("Lease pricing", "New -5.3%; renewal +5.2%; blended +0.7%", urls["release"], "2026-Q2", "Renewals offset weak new-lease pricing"),
    ("Debt profile", "4.5x net debt/EBITDAre; 86.6% fixed; 6.0 years", urls["release"], "2026-06-30", "Average effective rate 3.9%"),
    ("Dividend", "$6.12 / 5.20%", urls["statistics"], "2026-09-23", "81.6% of Core AFFO midpoint"),
    ("Next earnings", "Oct. 28, 2026 AMC", urls["statistics"], "2026-09-23", "Q3 confirmation catalyst"),
    ("US 10Y Treasury", "5.121%", urls["treasury"], "2026-09-24", "Tradeweb yield displayed by CNBC"),
]
for r, row in enumerate(audit, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 31
ws.column_dimensions["B"].width = 34
ws.column_dimensions["C"].width = 67
ws.column_dimensions["D"].width = 18
ws.column_dimensions["E"].width = 55
ws.freeze_panes = "A4"

ws = wb.create_sheet("Questions")
title(ws, "MAA Open Diligence Questions", 4)
headers(ws, 3, ["#", "Question", "Why it matters", "Evidence needed"])
questions = [
    (1, "When do Charlotte, Phoenix, Raleigh, Savannah and Nashville new-lease rates turn positive?", "These high-supply markets determine the speed of same-store NOI recovery.", "Monthly new-lease pricing and concessions by market"),
    (2, "How much of the 4-5 weeks of concessions is embedded in effective-rent guidance?", "Headline asking-rent stability can mask economic rent pressure.", "Gross-to-net rent bridge and concession burn-off"),
    (3, "Can 5%+ renewal pricing persist without increasing turnover?", "Renewals currently offset negative new-lease pricing.", "Renewal acceptance, move-outs and turnover"),
    (4, "What fixed and floating debt matures in 2027-2030, and at what coupons?", "Refinancing above the 3.9% portfolio rate can dilute FFO.", "Debt maturity and hedge schedule"),
    (5, "What share of the $804.5M TTM real-estate spend is maintenance, redevelopment, development and acquisitions?", "AFFO and FAD require a clean recurring-capex bridge.", "Project-level capital classification"),
    (6, "Will the $800M development pipeline achieve 6.25%-6.5% stabilized yields after concessions?", "Current lease-up yields are near 5%, so timing and rent recovery matter.", "Project cost, yield and lease-up schedule"),
    (7, "How much incremental NOI will the five lease-up communities deliver in 2027?", "Non-same-store growth is offsetting same-store contraction.", "Quarterly lease-up NOI bridge"),
    (8, "Is the 25% unit-renovation cash return repeatable at larger scale?", "This is MAA's highest-return disclosed internal investment.", "Renovated-unit volume, spend, rent lift and retention"),
    (9, "What is the recurring margin benefit from centralization, specialization and property Wi-Fi?", "Technology is a stated margin lever but disclosure remains early.", "Cost savings and incremental revenue by initiative"),
    (10, "Why repurchase shares at $130.54 while issuing ATM equity to redeem preferred stock?", "Cross-currents in common issuance and buybacks can destroy per-share value.", "Net share issuance and all-in preferred refinancing economics"),
    (11, "What are the Series I preferred redemption's final dilution and interest/dividend savings?", "The $43.4M redemption is funded through forward common equity issuance.", "Settlement shares, issue price and annual savings"),
    (12, "What tenant-income and delinquency stress appears if unemployment rises?", "Current 18% rent-to-income and 0.3% delinquency are unusually strong.", "Collections, bad debt and rent-to-income by market"),
    (13, "What is the portfolio's insurance exposure after three years of premium declines?", "Sun Belt weather risk may return abruptly despite a 12% renewal reduction.", "Deductibles, limits and catastrophe exposure"),
    (14, "Which communities drive geographic concentration and climate risk?", "Atlanta, Dallas and other large markets can dominate marginal results.", "Top market NOI, unit count and insured values"),
    (15, "How much future supply is directly competitive by submarket and price point?", "Metro-level deliveries can overstate or understate actual competition.", "Submarket deliveries, absorption and concessions"),
    (16, "Will October 28 guidance preserve the $8.53 Core FFO midpoint?", "Recent analyst target and estimate cuts suggest recovery timing is slipping.", "Q3 Core FFO, leasing trends and FY2027 bridge"),
]
for r, row in enumerate(questions, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 65
ws.column_dimensions["C"].width = 58
ws.column_dimensions["D"].width = 50

ws = wb.create_sheet("Sources")
title(ws, "MAA Sources", 4)
headers(ws, 3, ["#", "Source", "URL", "Use"])
source_rows = [
    (1, "StockAnalysis overview", urls["overview"], "Price, identity, earnings date and news"),
    (2, "StockAnalysis statistics", urls["statistics"], "Market value, ratios, shares, leverage and dividend"),
    (3, "StockAnalysis forecast", urls["forecast"], "Consensus revenue, FFO and targets"),
    (4, "StockAnalysis income statement", urls["income"], "Historical revenue, earnings, D&A, FFO and AFFO"),
    (5, "StockAnalysis balance sheet", urls["balance"], "Real estate, debt, cash and equity"),
    (6, "StockAnalysis cash flow", urls["cashflow"], "OCF, real-estate spend, dividends and buybacks"),
    (7, "StockAnalysis KPIs", urls["metrics"], "Communities, units, occupancy and same-store NOI"),
    (8, "StockAnalysis profile", urls["profile"], "Company description, management and filings"),
    (9, "MAA Q2 2026 release", urls["release"], "Guidance, leasing, projects, leverage and FFO/AFFO reconciliation"),
    (10, "MAA Q2 2026 transcript", urls["transcript"], "Market, supply, concessions, development and capital-allocation commentary"),
    (11, "CNBC US 10-Year Treasury", urls["treasury"], "WACC risk-free rate"),
]
for r, row in enumerate(source_rows, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 34
ws.column_dimensions["C"].width = 105
ws.column_dimensions["D"].width = 55

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False
    sheet.auto_filter.ref = sheet.dimensions

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert check["Scenarios"]["C13"].value == weighted_fv
assert check["Valuation"]["B7"].value == "P/FFO with AFFO cross-check"
assert targets["Bear"] < PRICE < targets["Base"] < targets["Bull"]
print(f"WACC: {wacc:.2%}")
print(f"Targets: bear ${targets['Bear']:.2f}, base ${targets['Base']:.2f}, bull ${targets['Bull']:.2f}")
print(f"Probability-weighted fair value: ${weighted_fv:.2f} ({weighted_fv / PRICE - 1:.1%})")
print(f"Analyst target cross-check: $141.44; model base difference {(targets['Base'] / 141.44 - 1):.1%}")
print(f"Created {OUT}")
