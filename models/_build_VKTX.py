#!/usr/bin/env python3
"""Build the six-sheet Viking Therapeutics (VKTX) clinical-biotech model."""

from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


AS_OF = date(2026, 9, 25)
OUT = Path(__file__).with_name("2026-09-25 Viking Therapeutics Model.xlsx")
PRICE = 36.75
SHARES_PRE = 116.65
NEW_SHARES = 7.857143
SHARES_PRO_FORMA = SHARES_PRE + NEW_SHARES
CASH_JUNE = 501.66
DEBT_JUNE = 4.09
EQUITY_NET_PROCEEDS = 258.2
NOTE_NET_PROCEEDS = 218.0
NOTE_PRINCIPAL = 225.0
CASH_PRO_FORMA = CASH_JUNE + EQUITY_NET_PROCEEDS + NOTE_NET_PROCEEDS
DEBT_PRO_FORMA = DEBT_JUNE + NOTE_PRINCIPAL
NET_CASH_PRO_FORMA = CASH_PRO_FORMA - DEBT_PRO_FORMA
MARKET_CAP_PRO_FORMA = PRICE * SHARES_PRO_FORMA
RISK_FREE = 0.0410
ERP = 0.05
BETA = 0.68
COST_OF_EQUITY = RISK_FREE + BETA * ERP

BLUE = "1F4E78"
LIGHT_BLUE = "D9EAF7"
LIGHT_GREEN = "E2F0D9"
LIGHT_RED = "FCE4D6"
WHITE = "FFFFFF"
thin = Side(style="thin", color="B7B7B7")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def title(ws, text, end_col=5):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    cell = ws.cell(1, 1, text)
    cell.font = Font(size=15, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=BLUE)
    cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 24


def header(ws, row, values):
    for col, value in enumerate(values, 1):
        cell = ws.cell(row, col, value)
        cell.font = Font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.border = border
        cell.alignment = Alignment(horizontal="center", wrap_text=True)


def table(ws, start_row, headers, rows):
    header(ws, start_row, headers)
    for r, values in enumerate(rows, start_row + 1):
        for c, value in enumerate(values, 1):
            cell = ws.cell(r, c, value)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if r % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F3F6F8")


def widths(ws, values):
    for col, width in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(col)].width = width


wb = Workbook()

# 1. Valuation
ws = wb.active
ws.title = "Valuation"
title(ws, "Viking Therapeutics, Inc. (NASDAQ: VKTX) — Valuation Summary", 4)
table(ws, 3, ["Field", "Value", "As of / Comment"], [
    ("Model date", str(AS_OF), "Public information through September 24, 2026"),
    ("Price", PRICE, "September 24 close; StockAnalysis"),
    ("Shares outstanding", SHARES_PRE, "June 30 actual, millions"),
    ("New common shares", NEW_SHARES, "$275M gross offering at $35; excludes 1.179M greenshoe"),
    ("Pro-forma basic shares", SHARES_PRO_FORMA, "Millions; excludes potential note conversion"),
    ("Quoted market cap", 4290.0, "$mm, pre-offering quote basis"),
    ("Pro-forma market cap", MARKET_CAP_PRO_FORMA, "$mm at current price and issued offering shares"),
    ("June cash and investments", CASH_JUNE, "$mm"),
    ("Pro-forma cash", CASH_PRO_FORMA, "$mm; adds estimated equity and note net proceeds"),
    ("Pro-forma debt", DEBT_PRO_FORMA, "$mm; includes $225M 2.00% notes due 2032"),
    ("Pro-forma net cash", NET_CASH_PRO_FORMA, "$mm"),
    ("Primary lens", "Cash NAV + risk-adjusted pipeline NPV", "Pre-revenue biotech; P/E and FCF multiples are not meaningful"),
    ("Stance", "Watch / Speculative", "Phase 3 execution and dilution remain decisive despite strong VK2735 data"),
])
ws["A18"] = "Key Valuation Metrics"
ws["A18"].font = Font(size=12, bold=True)
table(ws, 19, ["Metric", "Value", "Interpretation"], [
    ("P/E / Forward P/E", "N/A", "Negative earnings and no product revenue"),
    ("P/S / EV/Sales", "N/A", "No revenue"),
    ("P/FCF / EV/FCF", "N/A", "TTM FCF is negative by design"),
    ("P/B", 11.90, "Backward-looking and diluted by R&D burn; not primary"),
    ("June net cash/share", CASH_JUNE / SHARES_PRE, "Before September financing"),
    ("Pro-forma net cash/share", NET_CASH_PRO_FORMA / SHARES_PRO_FORMA, "After common stock and note offerings"),
    ("Optionality premium/share", PRICE - NET_CASH_PRO_FORMA / SHARES_PRO_FORMA, "Price less pro-forma net cash/share"),
    ("Analyst target", 94.61, "20 analysts; range $38-$125"),
    ("Short interest", "19.0% of shares", "High event-driven positioning"),
    ("TTM operating cash flow", -418.44, "$mm; cash burn, not owner earnings"),
    ("Runway before financing", CASH_JUNE / 418.44, "Years at unchanged TTM OCF burn"),
    ("Runway pro forma", CASH_PRO_FORMA / 418.44, "Years at unchanged TTM OCF burn, before interest"),
])
widths(ws, [31, 28, 74, 2])

# 2. WACC
ws = wb.create_sheet("WACC")
title(ws, "VKTX — Cost of Capital", 4)
table(ws, 3, ["Component", "Value", "Source / Formula", "Comment"], [
    ("Risk-free rate", RISK_FREE, "10Y U.S. Treasury rounded market anchor", "Model input"),
    ("Equity risk premium", ERP, "House assumption", "Model input"),
    ("Levered beta", BETA, "StockAnalysis, September 24, 2026", "Five-year beta"),
    ("CAPM cost of equity", COST_OF_EQUITY, "Rf + beta × ERP", "Relevant corporate finance WACC"),
    ("Pre-tax cost of debt", 0.02, "Convertible coupon", "Economic cost is higher because of conversion option"),
    ("Tax rate", 0.0, "Persistent losses / NOLs", "No current tax shield assumed"),
    ("Equity value", MARKET_CAP_PRO_FORMA, "$mm pro forma", "Current price × pro-forma basic shares"),
    ("Debt", DEBT_PRO_FORMA, "$mm pro forma", "Lease debt plus notes"),
    ("Equity weight", MARKET_CAP_PRO_FORMA / (MARKET_CAP_PRO_FORMA + DEBT_PRO_FORMA), "E / (D + E)", ""),
    ("Debt weight", DEBT_PRO_FORMA / (MARKET_CAP_PRO_FORMA + DEBT_PRO_FORMA), "D / (D + E)", ""),
    ("Computed WACC", (MARKET_CAP_PRO_FORMA * COST_OF_EQUITY + DEBT_PRO_FORMA * 0.02) / (MARKET_CAP_PRO_FORMA + DEBT_PRO_FORMA), "Weighted CAPM and coupon", "Not the pipeline discount rate"),
    ("Pipeline discount rate", 0.12, "Biotech risk adjustment", "Used conceptually for pipeline NPV; clinical failure risk dominates WACC"),
])
for cell in ("B4", "B5", "B7", "B8", "B11", "B12", "B13", "B14", "B15"):
    ws[cell].number_format = "0.0%"
widths(ws, [29, 22, 38, 62])

# 3. Scenarios
ws = wb.create_sheet("Scenarios")
title(ws, "VKTX — Clinical Biotech Scenario Analysis", 5)
ws["A2"] = "Framework: cash NAV plus probability-adjusted pipeline value. Standard DCF/FCF multiples are inapplicable before product revenue."
ws.merge_cells("A2:E2")
ws["A2"].font = Font(italic=True)
table(ws, 4, ["Driver", "Bear", "Base", "Bull", "Notes"], [
    ("Clinical outcome", "Phase 3 delay/failure", "One formulation succeeds", "SC + oral franchise succeeds", "VK2735 is the dominant value driver"),
    ("Annual cash burn ($mm)", 600, 500, 450, "Includes larger Phase 3/commercial preparation"),
    ("Future dilution factor", 1.35, 1.18, 1.08, "Beyond September offering and before note conversion"),
    ("Diluted shares ($mm)", SHARES_PRO_FORMA * 1.35, SHARES_PRO_FORMA * 1.18, SHARES_PRO_FORMA * 1.08, "Scenario share denominator"),
    ("Residual cash NAV/share", 2.00, 4.00, 5.50, "After trial spending and scenario dilution"),
    ("VK2735 rNPV/share", 4.00, 42.00, 95.00, "Risk-adjusted product optionality"),
    ("Other pipeline rNPV/share", 2.00, 6.00, 9.50, "VK3019, VK2809, VK0214 and other programs"),
    ("Target price", 8.00, 52.00, 110.00, "Sum of NAV and pipeline components"),
    ("Upside / (downside)", 8.00 / PRICE - 1, 52.00 / PRICE - 1, 110.00 / PRICE - 1, "Versus $36.75"),
    ("Probability weight", 0.30, 0.45, 0.25, "Clinical binary retains a substantial failure weight"),
    ("Weighted value/share", 2.40, 23.40, 27.50, "Target × probability"),
])
for row in (13, 14):
    for col in range(2, 5):
        ws.cell(row, col).number_format = "0.0%"
ws["A17"] = "Probability-weighted fair value"
ws["B17"] = "=SUM(B15:D15)"
ws["A18"] = "Upside from current price"
ws["B18"] = "=B17/36.75-1"
ws["B18"].number_format = "0.0%"
for cell in ("A17", "A18", "B17", "B18"):
    ws[cell].font = Font(bold=True)
    ws[cell].fill = PatternFill("solid", fgColor=LIGHT_GREEN)
    ws[cell].border = border
ws["A20"] = "Sanity checks"
ws["A20"].font = Font(size=12, bold=True)
table(ws, 21, ["Check", "Result", "Read"], [
    ("Bear below current price", "PASS", "$8 bear value is 78% below $36.75"),
    ("Base vs analyst average target", "DIVERGES", "$52 base is 45% below $94.61; reflects financing and Phase 3 risk"),
    ("Cash/runway", "PASS", "Pro-forma gross liquidity supports about 2.3 years at TTM burn"),
    ("Unit consistency", "PASS", "All cash, debt and share figures use $mm / mm shares"),
])
widths(ws, [31, 23, 23, 23, 70])

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "VKTX — Actuals Source Audit", 5)
table(ws, 3, ["Data Point", "Value", "Source URL", "Source Date", "Notes"], [
    ("Price", "$36.75", "https://stockanalysis.com/stocks/vktx/", "2026-09-24", "Closing price"),
    ("Market cap / EV", "$4.29B / $3.79B", "https://stockanalysis.com/stocks/vktx/statistics/", "2026-09-24", "Pre-financing quote basis"),
    ("Shares outstanding", "116.65M", "https://stockanalysis.com/stocks/vktx/statistics/", "2026-09-24", "June balance-sheet count"),
    ("Beta", "0.68", "https://stockanalysis.com/stocks/vktx/statistics/", "2026-09-24", "Five-year beta"),
    ("52-week range", "$24.78-$43.15", "https://stockanalysis.com/stocks/vktx/", "2026-09-24", ""),
    ("TTM revenue", "$0", "https://stockanalysis.com/stocks/vktx/financials/", "2026-06-30", "Clinical-stage company"),
    ("TTM operating income", "-$560.02M", "https://stockanalysis.com/stocks/vktx/financials/", "2026-06-30", "R&D and G&A spending"),
    ("TTM net income / EPS", "-$534.80M / -$4.67", "https://stockanalysis.com/stocks/vktx/financials/", "2026-06-30", ""),
    ("Cash and investments", "$501.66M", "https://stockanalysis.com/stocks/vktx/financials/balance-sheet/", "2026-06-30", "Before September offering"),
    ("Debt", "$4.09M", "https://stockanalysis.com/stocks/vktx/financials/balance-sheet/", "2026-06-30", "Primarily leases"),
    ("TTM operating / free cash flow", "-$418.44M / -$418.44M", "https://stockanalysis.com/stocks/vktx/financials/cash-flow-statement/", "2026-06-30", "No meaningful capex"),
    ("FY25 OCF", "-$278.69M", "https://stockanalysis.com/stocks/vktx/financials/cash-flow-statement/", "2025-12-31", "Burn accelerated sharply in 2026"),
    ("FY25 stock compensation", "$40.82M", "https://stockanalysis.com/stocks/vktx/financials/cash-flow-statement/", "2025-12-31", "Non-cash but dilutive"),
    ("FY26 EPS consensus", "-$4.61", "https://stockanalysis.com/stocks/vktx/forecast/", "2026-09-23", "17 analysts; non-GAAP adjusted basis per provider"),
    ("Price target", "$38 / $94.61 / $125", "https://stockanalysis.com/stocks/vktx/forecast/", "2026-09-23", "Low / average / high; 20 analysts"),
    ("Next earnings", "October 21, 2026", "https://stockanalysis.com/stocks/vktx/statistics/", "2026-09-24", "Estimated, after market close"),
    ("VK2735 maintenance", "22% placebo-adjusted at week 33", "https://stockanalysis.com/stocks/vktx/transcripts/758817-study-result/", "2026-09-22", "Small study; not head-to-head"),
    ("Maintenance retention", "83%-97% Q2W; 82%-90% monthly", "https://stockanalysis.com/stocks/vktx/transcripts/758817-study-result/", "2026-09-22", "Versus 61% after placebo transition"),
    ("Common stock offering", "7.857M shares at $35", "https://www.prnewswire.com/news-releases/viking-therapeutics-prices-upsized-500-million-offering-of-common-stock-and-convertible-senior-notes-302888812.html", "2026-09-24", "$258.2M estimated net proceeds"),
    ("Convertible notes", "$225M, 2.00%, due 2032", "https://www.prnewswire.com/news-releases/viking-therapeutics-prices-upsized-500-million-offering-of-common-stock-and-convertible-senior-notes-302888812.html", "2026-09-24", "$50.75 conversion price; $218M net proceeds"),
])
widths(ws, [31, 28, 78, 17, 54])

# 5. Questions
ws = wb.create_sheet("Questions")
title(ws, "VKTX — Open Questions", 4)
questions = [
    "What exact efficacy and tolerability thresholds must VANQUISH-1 and VANQUISH-2 meet for FDA approval and competitive labeling?",
    "Will the 22% maintenance-study result replicate in the much larger Phase 3 population with a slower titration schedule?",
    "When will full maintenance-study data be presented, and do missing-data handling or discontinuations change the topline read?",
    "Which every-other-week and monthly maintenance doses will the FDA permit in the Phase 3 extensions?",
    "Can oral VK2735 reproduce subcutaneous efficacy without unacceptable GI events or adherence constraints?",
    "What is the precise timing, size and statistical design for the two planned oral Phase 3 studies?",
    "How should cross-trial comparisons with tirzepatide, semaglutide and retatrutide be adjusted for trial size, duration and titration?",
    "Does rapid weight loss produce disproportionate lean-mass loss, and what body-composition data will Phase 3 collect?",
    "How much of the roughly $476M net financing proceeds is earmarked for Phase 3 versus commercial buildout?",
    "Will the $225M convertible notes be settled in cash or shares if VKTX exceeds the $50.75 conversion price?",
    "How should investors model the 1.179M common greenshoe and $33.75M note over-allotment if exercised?",
    "At the current TTM cash burn, is the pro-forma runway sufficient through all subcutaneous and oral pivotal readouts?",
    "How quickly will Phase 3 enrollment and manufacturing commitments push annual burn above the current $418M OCF deficit?",
    "What scale-up, fill-finish and device partnerships are required for commercial GLP-1 production?",
    "Can Viking secure supply economics competitive with Lilly and Novo without owning large-scale manufacturing?",
    "Would management commercialize alone, partner VK2735, or pursue a sale after pivotal data?",
    "What payer evidence will be generated for less-frequent maintenance dosing and persistence benefits?",
    "What is VK3019's differentiated profile, development timeline and incremental value beyond VK2735?",
    "Is VK2809 still strategically funded, and what clinical/regulatory milestone would unlock value?",
    "How should the 19% short interest be interpreted around binary Phase 3 readouts and financing-related hedges?",
    "What is the expected quarterly stock-based compensation and resulting baseline dilution independent of financings?",
    "What safety events, including gallbladder, pancreatitis, cardiovascular or psychiatric signals, appeared outside common GI events?",
    "What is the next confirmed earnings date after October 21, and will guidance include a detailed cash runway?",
]
table(ws, 3, ["#", "Question", "Why It Matters"], [(i, q, "Required diligence before underwriting pivotal-stage value") for i, q in enumerate(questions, 1)])
widths(ws, [7, 105, 50, 2])

# 6. Sources
ws = wb.create_sheet("Sources")
title(ws, "VKTX — Sources", 3)
sources = [
    (1, "StockAnalysis overview", "https://stockanalysis.com/stocks/vktx/"),
    (2, "StockAnalysis financial overview", "https://stockanalysis.com/stocks/vktx/financials/"),
    (3, "StockAnalysis balance sheet", "https://stockanalysis.com/stocks/vktx/financials/balance-sheet/"),
    (4, "StockAnalysis cash flow", "https://stockanalysis.com/stocks/vktx/financials/cash-flow-statement/"),
    (5, "StockAnalysis statistics", "https://stockanalysis.com/stocks/vktx/statistics/"),
    (6, "StockAnalysis forecast", "https://stockanalysis.com/stocks/vktx/forecast/"),
    (7, "StockAnalysis company profile", "https://stockanalysis.com/stocks/vktx/company/"),
    (8, "VK2735 maintenance-study transcript", "https://stockanalysis.com/stocks/vktx/transcripts/758817-study-result/"),
    (9, "September 2026 offering release", "https://www.prnewswire.com/news-releases/viking-therapeutics-prices-upsized-500-million-offering-of-common-stock-and-convertible-senior-notes-302888812.html"),
]
table(ws, 3, ["#", "Source", "URL"], sources)
widths(ws, [7, 42, 120])

for sheet in wb.worksheets:
    sheet.freeze_panes = "A4"
    sheet.sheet_view.showGridLines = False
    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, float):
                cell.number_format = "0.00"

wb.save(OUT)

# Re-open and verify the workbook contract.
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert all(check[name].max_row >= 10 for name in expected)
assert check["Scenarios"]["B17"].value == "=SUM(B15:D15)"
print(f"WACC: {check['WACC']['B14'].value:.2%}")
print("Scenario targets: bear $8.00 / base $52.00 / bull $110.00")
print("Probability-weighted FV: $53.30; upside: 45.0%")
print(f"Created and verified: {OUT}")
