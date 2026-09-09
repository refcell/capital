#!/usr/bin/env python3
"""Build the 2026-09-09 DiamondRock Hospitality (DRH) valuation workbook."""

from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


OUT = Path(__file__).with_name("2026-09-09 DiamondRock Hospitality Model.xlsx")
PRICE = 11.97
SHARES = 205.30  # millions
MARKET_CAP = 2457.0  # $ millions
DEBT = 1196.0
CASH = 105.98
EV = 3548.0

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
title(ws, "DiamondRock Hospitality Company (NASDAQ: DRH) — REIT Valuation", 4)

summary = [
    ("Company", "DiamondRock Hospitality Company", "Portfolio", "34 hotels / 9,400 rooms"),
    ("Model date", "2026-09-09", "Quote", "$11.97 at Sep. 8, 2026 close"),
    ("Shares outstanding", "205.30M", "Market capitalization", "$2.457B"),
    ("Enterprise value", "$3.548B", "Net debt", "$1.090B"),
    ("Primary lens", "P/FFO with EV/EBITDA cross-check", "Stance", "Watch"),
]
for r, row in enumerate(summary, 3):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, bold=c in (1, 3), fill=YELLOW if c in (1, 3) else None)

headers(ws, 10, ["Metric", "Current / Forward", "Interpretation", "Source date"])
metrics = [
    ("Trailing P/E", "16.65x", "Secondary only; real-estate depreciation distorts GAAP earnings", "2026-09-09"),
    ("FY2026E P/FFO", "9.81x", "$11.97 / $1.22 consensus FFO per share", "2026-08-27"),
    ("P/S", "2.16x", "Equity value relative to $1.136B TTM revenue", "2026-09-09"),
    ("P/FCF", "15.04x", "Based on conventional $163.44M FCF", "2026-09-09"),
    ("EV/FCF", "21.71x", "Debt makes the enterprise claim materially dearer", "2026-09-09"),
    ("EV/Sales", "3.12x", "Lodging-cycle and asset-quality cross-check", "2026-09-08"),
    ("EV/EBITDA", "11.84x", "$3.548B EV / $299.53M TTM EBITDA", "2026-09-09"),
    ("P/B", "1.61x", "Book value understates replacement value but is not the primary lens", "2026-09-09"),
    ("Net debt / EBITDA", "3.64x", "Manageable, but cyclical lodging cash flows warrant a buffer", "2026-09-09"),
    ("Dividend yield", "3.01%", "$0.36 annualized; approximately 30% of FY2026E FFO/share", "2026-09-09"),
    ("Probability-weighted FV", "$14.51", "25% bear / 50% base / 25% bull; 21.2% upside", "2026-09-09"),
]
for r, row in enumerate(metrics, 11):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 25
ws.column_dimensions["B"].width = 24
ws.column_dimensions["C"].width = 62
ws.column_dimensions["D"].width = 16
ws.freeze_panes = "A11"

ws = wb.create_sheet("WACC")
title(ws, "DRH Weighted Average Cost of Capital", 4)
headers(ws, 3, ["Component", "Value", "Calculation / Source", "Comment"])
ke = 0.0479 + 0.99 * 0.05
equity_weight = MARKET_CAP / (MARKET_CAP + DEBT)
debt_weight = 1 - equity_weight
cost_debt = 58.12 / DEBT
wacc = equity_weight * ke + debt_weight * cost_debt
wacc_rows = [
    ("Risk-free rate", 0.0479, "CNBC US10Y yield open", "Sep. 9, 2026 snapshot"),
    ("Equity risk premium", 0.05, "Model assumption", "Standard US ERP"),
    ("Levered beta", 0.99, "StockAnalysis statistics", "Five-year beta"),
    ("Cost of equity", ke, "Rf + beta × ERP", "CAPM"),
    ("Pre-tax cost of debt", cost_debt, "$58.12M cash interest / $1,196M debt", "Observed cash cost proxy"),
    ("Tax rate", 0.0, "REIT structure", "No corporate tax shield assumed"),
    ("Market capitalization", MARKET_CAP, "StockAnalysis", "$ millions"),
    ("Total debt", DEBT, "StockAnalysis", "$ millions, leases included"),
    ("Equity weight", equity_weight, "MC / (MC + debt)", ""),
    ("Debt weight", debt_weight, "Debt / (MC + debt)", ""),
    ("Computed WACC", wacc, "E/V × Ke + D/V × Kd", "About 8.1%; close to provider 8.21%"),
]
for r, row in enumerate(wacc_rows, 4):
    for c, value in enumerate(row, 1):
        fmt = "0.00%" if c == 2 and r not in (10, 11) else None
        put(ws, r, c, value, bold=r == 14, fill=GREEN if r == 14 else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 28
ws.column_dimensions["B"].width = 18
ws.column_dimensions["C"].width = 38
ws.column_dimensions["D"].width = 45

ws = wb.create_sheet("Scenarios")
title(ws, "DRH Five-Year P/FFO Scenario Analysis", 6)
ws.merge_cells("A2:F2")
ws["A2"] = "REIT framework: terminal FFO/share × exit P/FFO; conventional FCF and EV/EBITDA are cross-checks."
ws["A2"].alignment = Alignment(wrap_text=True)
headers(ws, 4, ["Metric", "Bear", "Base", "Bull", "Units / Formula", "Interpretation"])
scenario_rows = [
    ("Revenue CAGR (5Y)", 0.00, 0.025, 0.045, "%", "Lodging demand and portfolio productivity"),
    ("Terminal revenue", 1136.0, 1286.6, 1415.7, "$mm", "TTM revenue compounded for five years"),
    ("Terminal FFO / share", 1.15, 1.45, 1.75, "$ / share", "Normalized funds from operations"),
    ("Exit P/FFO", 8.5, 10.0, 11.0, "x", "Cyclical lodging REIT range"),
    ("Target price", 9.775, 14.50, 19.25, "$ / share", "FFO/share × P/FFO"),
    ("Upside / (downside)", 9.775 / PRICE - 1, 14.50 / PRICE - 1, 19.25 / PRICE - 1, "%", "Versus $11.97 close"),
    ("Probability", 0.25, 0.50, 0.25, "%", "Weights sum to 100%"),
    ("Weighted value / share", 2.44375, 7.25, 4.8125, "$ / share", "Target × probability"),
    ("Probability-weighted FV", None, 14.50625, None, "$ / share", "Sum of weighted scenario values"),
    ("Upside from current", None, 14.50625 / PRICE - 1, None, "%", "Weighted FV / current price − 1"),
    ("Dividend / FY2026E FFO", None, 0.36 / 1.22, None, "%", "Conservative coverage before maintenance capex"),
    ("Current net debt / EBITDA", None, 3.64, None, "x", "Balance-sheet risk cross-check"),
]
for r, row in enumerate(scenario_rows, 5):
    for c, value in enumerate(row, 1):
        fmt = None
        if c in (2, 3, 4) and row[4] == "%":
            fmt = "0.0%"
        elif c in (2, 3, 4) and row[4] in ("$ / share", "$mm"):
            fmt = "$#,##0.00"
        put(ws, r, c, value, bold=r in (9, 13, 14), fill=GREEN if r in (13, 14) else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 29
for col in "BCD":
    ws.column_dimensions[col].width = 16
ws.column_dimensions["E"].width = 18
ws.column_dimensions["F"].width = 48
ws.freeze_panes = "A5"

ws = wb.create_sheet("Actuals Source Audit")
title(ws, "DRH Actuals Source Audit", 5)
headers(ws, 3, ["Data point", "Value", "Source URL", "As of", "Notes"])
urls = {
    "overview": "https://stockanalysis.com/stocks/drh/",
    "financials": "https://stockanalysis.com/stocks/drh/financials/",
    "balance": "https://stockanalysis.com/stocks/drh/financials/balance-sheet/",
    "cashflow": "https://stockanalysis.com/stocks/drh/financials/cash-flow-statement/",
    "statistics": "https://stockanalysis.com/stocks/drh/statistics/",
    "forecast": "https://stockanalysis.com/stocks/drh/forecast/",
    "ratios": "https://stockanalysis.com/stocks/drh/financials/ratios/",
    "profile": "https://stockanalysis.com/stocks/drh/company/",
}
audit = [
    ("Close price", "$11.97", urls["overview"], "2026-09-08", "Regular-session close"),
    ("Market cap", "$2.457B", urls["ratios"], "2026-09-08", "Price-based"),
    ("Enterprise value", "$3.548B", urls["ratios"], "2026-09-08", "Includes debt less cash"),
    ("Shares outstanding", "205.30M", urls["statistics"], "2026-09-09", "Down 1.45% YoY"),
    ("Beta", "0.99", urls["statistics"], "2026-09-09", "Five-year beta"),
    ("TTM revenue", "$1.136B", urls["financials"], "2026-06-30", "S&P Global data"),
    ("FY2025 / FY2024 revenue", "$1.120B / $1.130B", urls["financials"], "2025 / 2024", "FY2025 declined 0.83%"),
    ("TTM operating income", "$186.54M", urls["statistics"], "2026-06-30", "16.42% margin"),
    ("TTM net income", "$148.78M", urls["statistics"], "2026-06-30", "GAAP common income"),
    ("TTM EBITDA", "$299.53M", urls["statistics"], "2026-06-30", "26.36% margin"),
    ("TTM D&A", "$114.44M", urls["statistics"], "2026-06-30", "Primary GAAP-vs-FFO bridge"),
    ("TTM OCF / capex / FCF", "$243.99M / $80.55M / $163.44M", urls["statistics"], "2026-06-30", "Conventional FCF; property spending is capex"),
    ("Cash / debt / net debt", "$105.98M / $1.196B / $1.090B", urls["balance"], "2026-06-30", "Debt includes leases"),
    ("Common equity / BVPS", "$1.523B / $7.45", urls["balance"], "2026-06-30", "Tangible book equals common equity"),
    ("FY2026E revenue", "$1.14B", urls["forecast"], "2026-08-27", "+1.98%; public later years gated"),
    ("FY2026E adjusted EPS", "$0.54", urls["forecast"], "2026-08-27", "Non-GAAP adjusted; 11 analysts"),
    ("FY2026E FFO / share", "$254.62M / $1.22", urls["forecast"], "2026-08-27", "REIT valuation anchor"),
    ("Analyst target", "$13.71 avg; $11–$16", urls["forecast"], "2026-08-27", "14 analysts; Buy"),
    ("Valuation ratios", "9.78x FY26E P/FFO; 11.84x EV/EBITDA", urls["forecast"], "2026-09-09", "P/FFO shown on forecast; EV/EBITDA on statistics"),
    ("Last earnings", "2026-07-30", urls["overview"], "2026-09-09", "Q2 already released; next date not posted"),
    ("Dividend", "$0.36 / 3.01%", urls["statistics"], "2026-09-09", "Ex-dividend Sep. 30, 2026"),
]
for r, row in enumerate(audit, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 29
ws.column_dimensions["B"].width = 31
ws.column_dimensions["C"].width = 56
ws.column_dimensions["D"].width = 16
ws.column_dimensions["E"].width = 50
ws.freeze_panes = "A4"

ws = wb.create_sheet("Questions")
title(ws, "DRH Open Diligence Questions", 4)
headers(ws, 3, ["#", "Question", "Why it matters", "Evidence needed"])
questions = [
    (1, "What share of the $80.55M TTM property spend was maintenance versus growth capex?", "AFFO and dividend coverage depend on recurring maintenance needs.", "Hotel-level capex plan and reserve requirements"),
    (2, "What are fixed/variable debt proportions and the 2027–2030 maturity ladder?", "3.64x net debt/EBITDA creates refinancing sensitivity.", "Debt schedule, swaps, weighted coupon"),
    (3, "How durable was Q2's 7% RevPAR growth across leisure, group, and business transient demand?", "Mix determines whether the beat repeats.", "Comparable RevPAR by demand segment"),
    (4, "What occupancy and ADR assumptions underpin raised 2026 guidance?", "Price-led RevPAR is higher quality than occupancy-led discounting.", "Guidance bridge and hotel KPIs"),
    (5, "Which hotels account for the largest EBITDA and how concentrated is property-level risk?", "Thirty-four assets are diversified but not immune to local shocks.", "Top-ten hotel EBITDA contribution"),
    (6, "What is the weighted-average remaining franchise/management agreement term?", "Brand and operator economics constrain margins and flexibility.", "Agreement terms and termination rights"),
    (7, "How much of portfolio revenue comes from gateway versus leisure resorts?", "The two demand pools have different cyclicality.", "Property-level revenue segmentation"),
    (8, "What is the lease rollover or ground-lease exposure across the portfolio?", "Ground rent can behave like senior fixed debt.", "Lease maturity and escalation schedule"),
    (9, "Are buybacks still accretive after the stock's 39.5% one-year advance?", "Capital allocation at 9.8x forward FFO is less obvious than at the lows.", "Repurchase authorization and average price"),
    (10, "Why did preferred share repurchases total $119M TTM and what obligations remain?", "The retirement changes fixed charges and common claims.", "Preferred terms and final redemption accounting"),
    (11, "What normalized tax rate should investors use given the 0.22% TTM rate?", "REIT structure explains low tax, but taxable subsidiaries may vary.", "TRS income and tax reconciliation"),
    (12, "What does the $86.47M long-term unearned revenue balance represent?", "It may indicate key-money, deposits, or contractual obligations.", "Contract composition and recognition schedule"),
    (13, "How exposed are insurance, labor, utilities, and property taxes to above-RevPAR inflation?", "Hotel REIT margins have high operating leverage in both directions.", "Cost guidance by category"),
    (14, "Which acquisitions or dispositions are likely over the next twelve months?", "Portfolio recycling can change earnings quality and leverage.", "Acquisition pipeline and disposition cap rates"),
    (15, "When is the next earnings release and what KPI would falsify raised guidance?", "Q2 is already public; the next quarter is the confirmation test.", "Company IR calendar and consensus RevPAR"),
]
for r, row in enumerate(questions, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 62
ws.column_dimensions["C"].width = 56
ws.column_dimensions["D"].width = 46

ws = wb.create_sheet("Sources")
title(ws, "DRH Sources", 4)
headers(ws, 3, ["#", "Source", "URL", "Use"])
source_rows = [
    (1, "StockAnalysis overview", urls["overview"], "Price, identity, portfolio, news"),
    (2, "StockAnalysis financials", urls["financials"], "Historical income and margins"),
    (3, "StockAnalysis balance sheet", urls["balance"], "Debt, cash, equity and assets"),
    (4, "StockAnalysis cash flow", urls["cashflow"], "OCF, property investment and financing"),
    (5, "StockAnalysis statistics", urls["statistics"], "Current valuation, leverage and return ratios"),
    (6, "StockAnalysis forecast", urls["forecast"], "Consensus revenue, adjusted EPS, FFO and targets"),
    (7, "StockAnalysis ratios", urls["ratios"], "Historical valuation and capital efficiency"),
    (8, "StockAnalysis profile", urls["profile"], "Company description, leadership and filings"),
    (9, "DRH Q2 2026 release", "https://www.prnewswire.com/news-releases/diamondrock-hospitality-company-reports-second-quarter-2026-results-302839311.html", "Q2 FFO, RevPAR and raised guidance"),
    (10, "CNBC US 10-Year Treasury", "https://www.cnbc.com/quotes/US10Y", "WACC risk-free rate"),
]
for r, row in enumerate(source_rows, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 32
ws.column_dimensions["C"].width = 100
ws.column_dimensions["D"].width = 48

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False
    sheet.auto_filter.ref = sheet.dimensions

wb.save(OUT)

# Re-open verification catches corrupt output and checks the required contract.
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert check["Scenarios"]["C13"].value == 14.50625
assert check["Valuation"]["B7"].value == "P/FFO with EV/EBITDA cross-check"
print(f"WACC: {wacc:.2%}")
print("Targets: bear $9.78, base $14.50, bull $19.25")
print(f"Probability-weighted fair value: $14.51 ({14.50625 / PRICE - 1:.1%})")
print(f"Created {OUT}")
