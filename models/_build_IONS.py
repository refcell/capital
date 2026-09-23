#!/usr/bin/env python3
"""Build the six-sheet IONS commercial-stage biotech valuation workbook."""
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AS_OF = date(2026, 9, 22)
OUT = Path(__file__).with_name("2026-09-22 Ionis Pharmaceuticals Model.xlsx")
PRICE = 45.75
SHARES = 166.18
MARKET_CAP = 7600.0
DEBT = 2189.0
CASH = 2102.0
NET_DEBT = DEBT - CASH
RISK_FREE = 0.0496
ERP = 0.05
BETA = 0.42
COST_EQUITY = RISK_FREE + BETA * ERP
COST_DEBT = 0.045
EQUITY_WEIGHT = MARKET_CAP / (MARKET_CAP + DEBT)
DEBT_WEIGHT = 1 - EQUITY_WEIGHT
WACC = COST_EQUITY * EQUITY_WEIGHT + COST_DEBT * DEBT_WEIGHT

BLUE = "1F4E78"
LIGHT = "D9EAF7"
WHITE = "FFFFFF"
GRAY = "E7E6E6"
GREEN = "E2F0D9"
RED = "FCE4D6"
thin = Side(style="thin", color="B7B7B7")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def setup(ws, title, columns):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=columns)
    cell = ws.cell(1, 1, title)
    cell.font = Font(size=15, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=BLUE)
    cell.alignment = Alignment(horizontal="center")
    ws.freeze_panes = "A3"
    ws.sheet_view.showGridLines = False


def header(ws, row, values):
    for col, value in enumerate(values, 1):
        cell = ws.cell(row, col, value)
        cell.font = Font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border


def rows(ws, start, data):
    for r, values in enumerate(data, start):
        for c, value in enumerate(values, 1):
            cell = ws.cell(r, c, value)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def widths(ws, values):
    for col, width in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(col)].width = width


wb = Workbook()

# Valuation
ws = wb.active
ws.title = "Valuation"
setup(ws, "Ionis Pharmaceuticals, Inc. (IONS) — Valuation", 4)
header(ws, 3, ["Field", "Value", "Source / Calculation", "Interpretation"])
valuation = [
    ("As of", AS_OF.isoformat(), "Market close", "All market values use the same quote date."),
    ("Price", PRICE, "StockAnalysis", "$ / share"),
    ("Shares outstanding", SHARES, "StockAnalysis statistics", "Millions; +4.49% YoY"),
    ("Market capitalization", MARKET_CAP, "StockAnalysis", "$ millions"),
    ("Enterprise value", 7690.0, "StockAnalysis", "$ millions"),
    ("Cash & investments", CASH, "Jun. 30, 2026 balance sheet", "$ millions"),
    ("Total debt", DEBT, "Jun. 30, 2026 balance sheet", "$ millions"),
    ("Net debt", NET_DEBT, "Debt less cash", "Near-neutral net cash/debt, but gross debt matters."),
    ("Primary valuation lens", "Forward EV/Sales + pipeline optionality", "Commercial-stage, loss-making biotech", "P/E and FCF multiples are not meaningful."),
    ("Stance", "Watch", "Research conclusion", "Launch execution and pipeline are attractive; burn and trial failures remain material."),
]
rows(ws, 4, valuation)
ws.cell(15, 1, "Key valuation metrics").font = Font(bold=True, size=12)
header(ws, 16, ["Metric", "Value", "Basis", "Comment"])
metrics = [
    ("P/E", "N/A", "Negative TTM EPS", "TTM GAAP EPS was -$3.46."),
    ("Forward P/E", "N/A", "FY27 adjusted EPS remains negative", "Do not force an earnings multiple before profitability."),
    ("P/S", 8.70, "Current market cap / TTM revenue", "Elevated and milestone-sensitive."),
    ("Forward P/S", 7.92, "Provider estimate", "FY26 consensus revenue is $921M."),
    ("P/FCF", "N/A", "TTM FCF -$561M", "Negative by design during launch and pipeline investment."),
    ("EV/FCF", "N/A", "Negative FCF", "Not economically meaningful."),
    ("EV/Sales", 8.80, "EV / TTM revenue", "Current valuation embeds launch and pipeline success."),
    ("EV/EBITDA", "N/A", "TTM EBITDA -$579M", "Not meaningful."),
    ("Analyst target", 83.82, "23 analysts", "Range $54-$105; targets were cut after pelacarsen."),
]
rows(ws, 17, metrics)
for r in range(4, 14):
    ws.cell(r, 2).fill = PatternFill("solid", fgColor=LIGHT)
widths(ws, [29, 24, 37, 58])

# WACC
ws = wb.create_sheet("WACC")
setup(ws, "IONS — WACC", 4)
header(ws, 3, ["Component", "Value", "Source / Formula", "Comment"])
wacc_rows = [
    ("Risk-free rate", RISK_FREE, "FRED DGS10, Sep. 21, 2026", "Latest available observation at valuation date."),
    ("Equity risk premium", ERP, "House assumption", "5.0%"),
    ("Levered beta", BETA, "StockAnalysis 5Y beta", "Low historical beta understates binary clinical risk."),
    ("Cost of equity", COST_EQUITY, "Rf + beta × ERP", "CAPM output; scenario probabilities capture asset-specific risk."),
    ("Pre-tax cost of debt", COST_DEBT, "Model assumption", "Blended proxy for convertible/lease obligations."),
    ("Tax rate", 0.0, "Persistent losses / NOLs", "No modeled tax shield."),
    ("Market cap", MARKET_CAP, "StockAnalysis", "$ millions"),
    ("Debt", DEBT, "Balance sheet", "$ millions"),
    ("Equity weight", EQUITY_WEIGHT, "MC / (MC + debt)", "Capital weights use gross debt."),
    ("Debt weight", DEBT_WEIGHT, "Debt / (MC + debt)", "Capital weights use gross debt."),
    ("Computed WACC", WACC, "Ke×E/V + Kd×D/V", "Used as a reference, not as false precision for pipeline NPV."),
]
rows(ws, 4, wacc_rows)
for r in [4, 5, 7, 8, 12, 13, 14]:
    ws.cell(r, 2).number_format = "0.00%"
ws.cell(14, 2).fill = PatternFill("solid", fgColor=GREEN)
widths(ws, [29, 20, 36, 56])

# Scenarios
ws = wb.create_sheet("Scenarios")
setup(ws, "IONS — Forward EV/Sales Scenario Analysis", 6)
header(ws, 3, ["Driver", "Bear", "Base", "Bull", "Units / Formula", "Why it differs"])
terminal_revenue = [1400.0, 2175.0, 3170.0]
exit_multiple = [3.5, 5.0, 6.0]
terminal_shares = [190.0, 185.0, 180.0]
targets = [(r * m - NET_DEBT) / s for r, m, s in zip(terminal_revenue, exit_multiple, terminal_shares)]
weights_ = [0.25, 0.50, 0.25]
weighted = [t * w for t, w in zip(targets, weights_)]
fair_value = sum(weighted)
scenario_rows = [
    ("2026 revenue anchor", 921.42, 921.42, 921.42, "$M; public consensus", "Visible consensus anchor"),
    ("5-year revenue CAGR", 0.087, 0.187, 0.280, "Implied from terminal revenue", "Launch/pipeline conversion"),
    ("Terminal revenue", *terminal_revenue, "$M", "Rounded scenario outcome"),
    ("Terminal operating margin", -0.05, 0.15, 0.25, "%", "Commercial scale and R&D discipline"),
    ("Terminal FCF", -70.0, 261.0, 792.5, "$M", "Directional cross-check; not primary lens"),
    ("Exit EV/Sales", *exit_multiple, "x", "Compression versus today's 8.8x"),
    ("Implied enterprise value", *(r*m for r, m in zip(terminal_revenue, exit_multiple)), "$M", "Revenue × exit multiple"),
    ("Less net debt", NET_DEBT, NET_DEBT, NET_DEBT, "$M", "Jun. 2026 debt less cash"),
    ("Terminal diluted shares", *terminal_shares, "M", "Models continued dilution"),
    ("Target price", *targets, "$ / share", "(EV - net debt) / shares"),
    ("Upside / (downside)", *((t / PRICE) - 1 for t in targets), "%", "Versus $45.75"),
    ("Probability weight", *weights_, "%", "25% / 50% / 25%"),
    ("Weighted value / share", *weighted, "$ / share", "Target × probability"),
    ("Probability-weighted fair value", fair_value, "", "", "$ / share", "Sum of weighted values"),
    ("Upside from current", fair_value / PRICE - 1, "", "", "%", "Fair value / price - 1"),
]
rows(ws, 4, scenario_rows)
for r in [5, 7, 14, 15, 18]:
    for c in range(2, 5):
        ws.cell(r, c).number_format = "0.0%"
for c in range(2, 5):
    ws.cell(13, c).number_format = "$0.00"
ws.cell(17, 2).number_format = "$0.00"
ws.cell(18, 2).number_format = "0.0%"
ws.cell(17, 2).fill = PatternFill("solid", fgColor=GREEN)
widths(ws, [29, 18, 18, 18, 31, 55])

# Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
setup(ws, "IONS — Actuals Source Audit", 5)
header(ws, 3, ["Data point", "Value", "Source URL", "As of", "Notes"])
audit = [
    ("Stock price", "$45.75", "https://stockanalysis.com/stocks/ions/", "2026-09-22", "Close"),
    ("Market cap / EV", "$7.60B / $7.69B", "https://stockanalysis.com/stocks/ions/statistics/", "2026-09-22", "Daily market data"),
    ("Shares / beta", "166.18M / 0.42", "https://stockanalysis.com/stocks/ions/statistics/", "2026-09-22", "+4.49% shares YoY"),
    ("TTM revenue", "$874.09M", "https://stockanalysis.com/stocks/ions/financials/income-statement/", "2026-06-30", "Milestone-sensitive revenue"),
    ("TTM operating income", "-$594.35M", "https://stockanalysis.com/stocks/ions/financials/income-statement/", "2026-06-30", "Launch and R&D investment"),
    ("TTM net income / EPS", "-$565.17M / -$3.46", "https://stockanalysis.com/stocks/ions/financials/income-statement/", "2026-06-30", "GAAP"),
    ("FY21-FY25 income statement", "See source", "https://stockanalysis.com/stocks/ions/financials/income-statement/", "2021-2025", "Revenue, GP, operating income, net income, shares"),
    ("Cash & investments", "$2.102B", "https://stockanalysis.com/stocks/ions/financials/balance-sheet/", "2026-06-30", "Cash plus short-term investments"),
    ("Total debt", "$2.189B", "https://stockanalysis.com/stocks/ions/financials/balance-sheet/", "2026-06-30", "Gross debt"),
    ("Common equity", "$439.74M", "https://stockanalysis.com/stocks/ions/financials/balance-sheet/", "2026-06-30", "Book value $2.65/share"),
    ("TTM OCF / FCF", "-$496.43M / -$560.84M", "https://stockanalysis.com/stocks/ions/financials/cash-flow-statement/", "2026-06-30", "Capex $64.41M"),
    ("TTM SBC", "$163.34M", "https://stockanalysis.com/stocks/ions/financials/cash-flow-statement/", "2026-06-30", "29% of GAAP loss; dilution signal"),
    ("FY26 revenue consensus", "$921.42M", "https://stockanalysis.com/stocks/ions/forecast/", "2026-09-22", "23 analysts; range $783M-$1.2B"),
    ("FY27 revenue headline", "$1.38B", "https://stockanalysis.com/stocks/ions/forecast/", "2026-09-22", "Later detailed table is paywalled"),
    ("FY26/FY27 adjusted EPS", "-$2.70 / -$1.11", "https://stockanalysis.com/stocks/ions/forecast/", "2026-09-22", "Provider-specific non-GAAP"),
    ("Price target", "$83.82 avg; $54-$105", "https://stockanalysis.com/stocks/ions/forecast/", "2026-09-22", "23 analysts"),
    ("Commercial products", "TRYNGOLZA, DAWNZERA, WAINUA, SPINRAZA", "https://stockanalysis.com/stocks/ions/company/", "2026-09-21", "Wholly owned launches plus royalties"),
    ("FUSION Phase 3", "Primary endpoint met", "https://ir.ionis.com/news-releases/news-release-details/ionis-announces-positive-topline-results-phase-3-fusion-study", "2026-09-22", "Otsuka-partnered ulefnersen; FUS-ALS"),
    ("Pelacarsen Phase 3", "Primary endpoint missed", "https://www.reuters.com/business/healthcare-pharmaceuticals/ionis-novartis-key-experimental-heart-drug-fails-late-stage-trial-2026-09-04/", "2026-09-04", "Removed a major royalty option"),
    ("Risk-free rate", "4.96%", "https://fred.stlouisfed.org/series/DGS10", "2026-09-21", "Latest observation available Sep. 22"),
    ("Next earnings", "2026-10-28 BMO", "https://stockanalysis.com/stocks/ions/statistics/", "2026-09-22", "Estimated"),
]
rows(ws, 4, audit)
widths(ws, [28, 24, 72, 17, 52])

# Questions
ws = wb.create_sheet("Questions")
setup(ws, "IONS — Open Questions", 4)
header(ws, 3, ["#", "Question", "Why it matters", "Evidence needed"])
questions = [
    (1, "How much of FY2025's $466M 'other' revenue was non-recurring milestone or license revenue?", "Reported growth does not equal product demand.", "Contract-level revenue bridge."),
    (2, "What are TRYNGOLZA and DAWNZERA new-patient starts, persistence and net pricing?", "Launch productivity determines the path to 2028 breakeven.", "Quarterly prescriptions, discontinuations, gross-to-net."),
    (3, "How should ulefnersen economics be split with Otsuka after the positive FUSION result?", "Clinical success only creates shareholder value through retained economics.", "Milestones, royalty tiers and remaining development obligations."),
    (4, "What residual pelacarsen costs or write-downs remain after Lp(a)HORIZON failed?", "The program lost option value, but cash consequences may continue.", "Partner termination and cost-sharing details."),
    (5, "Why did CARDIO-TTRansform fail, and does it alter WAINUA's neuropathy franchise?", "A partner-program miss may constrain label expansion without damaging current royalties.", "Subgroup and endpoint analysis."),
    (6, "Can management still reach cash-flow breakeven in 2028 after the two cardiovascular failures?", "This is the central dilution and solvency milestone.", "Updated annual revenue, opex and cash guidance."),
    (7, "What comprises $2.19B of gross debt, and what are maturity and conversion terms?", "Gross leverage is high even though net debt is near zero.", "Instrument-by-instrument schedule."),
    (8, "How much of the $2.10B liquidity is contractually restricted?", "Cash runway depends on usable, not headline, cash.", "Restricted cash and collateral disclosures."),
    (9, "Can annual SBC below $163M while launches scale?", "SBC and equity issuance are producing persistent dilution.", "Three-year dilution and compensation plan."),
    (10, "Does ZANVASTRO's Alexander disease launch justify the commercial infrastructure?", "Ultra-rare revenue may be valuable but small.", "Diagnosed population, pricing, uptake and access."),
    (11, "What is the competitive response to olezarsen in severe hypertriglyceridemia?", "Broader-market expansion could be much larger than FCS but more competitive.", "Market share, safety and payer criteria."),
    (12, "Which pipeline programs are funded through pivotal data, and which require partners?", "Capital allocation should concentrate on highest retained NPV.", "Program-level spend and partnership strategy."),
    (13, "Are royalty streams durable as SPINRAZA matures?", "SPINRAZA still contributed $207M TTM and may decline.", "Patient starts, competition and geographic mix."),
    (14, "How concentrated are partner receivables and milestone assumptions?", "Revenue is lumpy and counterparty-dependent.", "Top partner exposure and contract schedules."),
    (15, "Why did inventory rise to $50.8M from $10.1M at FY2025?", "Could be launch preparation or weak sell-through.", "Units, expiry risk and channel inventory."),
    (16, "What guidance will accompany Oct. 28 earnings?", "The first update after FUSION and pelacarsen should reset expectations.", "FY26 guidance and 2027 launch outlook."),
]
rows(ws, 4, questions)
widths(ws, [7, 61, 55, 50])

# Sources
ws = wb.create_sheet("Sources")
setup(ws, "IONS — Sources", 4)
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", "https://stockanalysis.com/stocks/ions/", "Quote, identity, headline metrics, news"),
    (2, "StockAnalysis company profile", "https://stockanalysis.com/stocks/ions/company/", "Products, pipeline, management, filings"),
    (3, "Income statement", "https://stockanalysis.com/stocks/ions/financials/income-statement/", "Historical and TTM financials"),
    (4, "Balance sheet", "https://stockanalysis.com/stocks/ions/financials/balance-sheet/", "Cash, debt, equity, shares"),
    (5, "Cash flow", "https://stockanalysis.com/stocks/ions/financials/cash-flow-statement/", "OCF, FCF, capex, SBC, financing"),
    (6, "Statistics", "https://stockanalysis.com/stocks/ions/statistics/", "Valuation, share count, beta, earnings date"),
    (7, "Forecast", "https://stockanalysis.com/stocks/ions/forecast/", "Consensus, targets and ratings"),
    (8, "Ionis Q2 release", "https://ir.ionis.com/news-releases/news-release-details/ionis-reports-second-quarter-2026-financial-results-and", "Guidance and pipeline status"),
    (9, "Ionis FUSION release", "https://ir.ionis.com/news-releases/news-release-details/ionis-announces-positive-topline-results-phase-3-fusion-study", "Ulefnersen Phase 3 result"),
    (10, "Reuters pelacarsen", "https://www.reuters.com/business/healthcare-pharmaceuticals/ionis-novartis-key-experimental-heart-drug-fails-late-stage-trial-2026-09-04/", "Lp(a)HORIZON failure"),
    (11, "FRED DGS10", "https://fred.stlouisfed.org/series/DGS10", "Risk-free rate"),
]
rows(ws, 4, sources)
widths(ws, [7, 31, 92, 52])

for ws in wb.worksheets:
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[1].height = 24

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
assert check.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert all(sheet.max_row >= 14 for sheet in check.worksheets)
print(f"WACC: {WACC:.2%}")
print("Targets:", ", ".join(f"${x:.2f}" for x in targets))
print(f"Probability-weighted fair value: ${fair_value:.2f} ({fair_value / PRICE - 1:.1%})")
print(f"Created: {OUT}")
