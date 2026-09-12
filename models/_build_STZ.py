#!/usr/bin/env python3
"""Build Constellation Brands' six-sheet valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).with_name("2026-09-12 Constellation Brands Model.xlsx")
PRICE, SHARES = 122.45, 170.75
MARKET_CAP, ENTERPRISE_VALUE = 20_909.0, 31_346.0
NET_DEBT = ENTERPRISE_VALUE - MARKET_CAP
TTM_REVENUE, TTM_FCF, TTM_EBITDA = 9_057.0, 1_834.0, 3_460.0
FY27_REVENUE, FY27_EPS, FY28_REVENUE, FY28_EPS = 9_100.0, 11.83, 9_270.0, 12.39
ANALYST_TARGET = 170.83

SCENARIOS = {
    "Bear": {"cagr": -0.005, "terminal_eps": 10.00, "pe": 9.0, "weight": 0.25},
    "Base": {"cagr": 0.015, "terminal_eps": 14.20, "pe": 12.0, "weight": 0.50},
    "Bull": {"cagr": 0.030, "terminal_eps": 17.00, "pe": 14.0, "weight": 0.25},
}
for case in SCENARIOS.values():
    case["terminal_revenue"] = FY28_REVENUE * (1 + case["cagr"]) ** 4
    case["target"] = case["terminal_eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1
weighted = sum(c["target"] * c["weight"] for c in SCENARIOS.values())
assert SCENARIOS["Bear"]["target"] < PRICE
assert abs(SCENARIOS["Base"]["target"] / ANALYST_TARGET - 1) < 0.20

rf, erp, beta = 0.0495, 0.05, 0.40
ke = rf + beta * erp
debt, kd, tax = 10_534.0, 346.2 / 10_534.0, 0.246
ew = MARKET_CAP / (MARKET_CAP + debt)
dw = 1 - ew
wacc = ew * ke + dw * kd * (1 - tax)

wb = Workbook()
navy, blue, gold, white = "17365D", "D9EAF7", "D8B34B", "FFFFFF"
thin = Side(style="thin", color="A6A6A6")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, row, col, value, bold=False, fill=None, color="000000", size=10):
    cell = ws.cell(row, col, value)
    cell.font = Font(name="Aptos", size=size, bold=bold, color=color)
    cell.fill = PatternFill("solid", fgColor=fill) if fill else PatternFill(fill_type=None)
    cell.border = border
    cell.alignment = Alignment(vertical="top", wrap_text=True)
    return cell


def title(ws, text, cols, subtitle):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=cols)
    put(ws, 1, 1, text, True, navy, white, 15)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cols)
    put(ws, 2, 1, subtitle, True, blue)


def header(ws, row, values):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, True, navy, white)


def finish(ws, widths):
    for col, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.freeze_panes = "A4"
    ws.sheet_view.showGridLines = False
    ws.auto_filter.ref = ws.dimensions


ws = wb.active
ws.title = "Valuation"
title(ws, "Constellation Brands, Inc. (STZ) — Valuation", 4,
      "Quote: September 11, 2026 close | Model date: September 12, 2026 | USD")
header(ws, 3, ["Field", "Value", "Comment"])
facts = [
    ("Company", "Constellation Brands, Inc.", "U.S. beverage-alcohol company; Modelo and Corona anchor beer"),
    ("Ticker", "NYSE: STZ", "Class A common stock"),
    ("Price", PRICE, "September 11 regular close"),
    ("Shares outstanding (M)", SHARES, "Current filing count"),
    ("Market capitalization ($M)", MARKET_CAP, "StockAnalysis"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "StockAnalysis"),
    ("Net debt proxy ($M)", NET_DEBT, "EV less market capitalization"),
    ("Primary lens", "Forward P/E", "Net debt / TTM FCF is 5.7x; P/E avoids EV-to-equity amplification"),
    ("Stance", "Watch / contrarian value", "Low multiple and strong cash returns offset weak demand visibility"),
]
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
header(ws, 14, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E", 11.69, "GAAP EPS includes portfolio and investment noise"),
    ("Forward P/E", 10.34, "FY2027 adjusted non-GAAP consensus"),
    ("P/S", 2.31, "Equity value / TTM revenue"),
    ("P/FCF", 11.40, "8.77% FCF yield"),
    ("EV/FCF", 17.09, "Debt-adjusted cross-check"),
    ("EV/Sales", 3.46, "Premium beer economics support a higher sales multiple"),
    ("EV/EBITDA", 9.07, "Below recent historical levels"),
    ("Debt/EBITDA", 2.89, "Meaningful but serviceable leverage"),
    ("Interest coverage", 8.73, "Healthy debt-service capacity"),
    ("Analyst average target", ANALYST_TARGET, "Low $115; median $173; high $209"),
]
for row, values in enumerate(metrics, 15):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [34, 28, 100, 14])

ws = wb.create_sheet("WACC")
title(ws, "Constellation Brands — Weighted Average Cost of Capital", 4,
      "CAPM using market-value weights and September 2026 inputs")
header(ws, 3, ["Component", "Value", "Source / formula"])
rows = [
    ("Risk-free rate", rf, "FRED DGS10, September 10, 2026"),
    ("Equity risk premium", erp, "Model assumption"),
    ("Levered beta", beta, "StockAnalysis five-year beta"),
    ("Cost of equity", ke, "Rf + beta × ERP"),
    ("Pre-tax cost of debt", kd, "$346.2M cash interest / $10.534B debt"),
    ("Tax rate", tax, "TTM effective tax rate"),
    ("Market cap ($M)", MARKET_CAP, "September 11, 2026"),
    ("Debt ($M)", debt, "May 31, 2026"),
    ("Equity weight", ew, "E/(D+E)"),
    ("Debt weight", dw, "D/(D+E)"),
    ("WACC", wacc, "E/V×Ke + D/V×Kd×(1−T)"),
]
for row, values in enumerate(rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, col == 1 or values[0] == "WACC",
                   gold if values[0] == "WACC" else None)
        if col == 2 and values[0] not in {"Levered beta", "Market cap ($M)", "Debt ($M)"}:
            cell.number_format = "0.00%"
finish(ws, [34, 24, 100, 14])

ws = wb.create_sheet("Scenarios")
title(ws, "Constellation Brands — Five-Year Forward P/E Scenarios", 6,
      "Forward P/E primary; FCF and EV/EBITDA are cross-checks")
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Units / formula", "Interpretation"])
order = ("Bear", "Base", "Bull")
rows = [
    ("FY2027 revenue consensus", FY27_REVENUE, FY27_REVENUE, FY27_REVENUE, "$M", "Visible public estimate"),
    ("FY2028 revenue anchor", FY28_REVENUE, FY28_REVENUE, FY28_REVENUE, "$M", "Visible headline estimate"),
    ("Revenue CAGR (4Y)", *(SCENARIOS[k]["cagr"] for k in order), "%", "After FY2028"),
    ("Terminal revenue", *(SCENARIOS[k]["terminal_revenue"] for k in order), "$M", "FY2028 compounded four years"),
    ("Terminal adjusted EPS", *(SCENARIOS[k]["terminal_eps"] for k in order), "$ / share", "Beer demand, margins, buybacks and interest"),
    ("Exit forward P/E", *(SCENARIOS[k]["pe"] for k in order), "x", "Branded-consumer range"),
    ("Target price", *(SCENARIOS[k]["target"] for k in order), "$ / share", "EPS × P/E"),
    ("Upside / downside", *(SCENARIOS[k]["upside"] for k in order), "%", "Versus $122.45"),
    ("Probability", *(SCENARIOS[k]["weight"] for k in order), "%", "25% / 50% / 25%"),
    ("Weighted value/share", *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in order), "$ / share", "Probability contribution"),
]
for row, values in enumerate(rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, col == 1)
        if col in (2, 3, 4) and values[0] in {"Revenue CAGR (4Y)", "Upside / downside", "Probability"}:
            cell.number_format = "0.0%"
        elif col in (2, 3, 4) and values[0] in {"Terminal adjusted EPS", "Target price", "Weighted value/share"}:
            cell.number_format = "$0.00"
put(ws, 15, 1, "Probability-weighted fair value", True, gold)
put(ws, 15, 2, weighted, True, gold).number_format = "$0.00"
put(ws, 16, 1, "Upside from current price", True, gold)
put(ws, 16, 2, weighted / PRICE - 1, True, gold).number_format = "0.0%"
put(ws, 18, 1, "Leverage warning", True, blue)
put(ws, 18, 2, NET_DEBT / TTM_FCF, False, blue).number_format = "0.00x"
put(ws, 18, 5, "Net debt / TTM FCF; reason forward P/E is primary")
finish(ws, [34, 18, 18, 18, 35, 76])

ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Constellation Brands — Actuals Source Audit", 5,
      "Financial statement amounts in USD millions")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/stz"
audit = [
    ("Price", "$122.45", f"{sa}/", "2026-09-11", "Regular close"),
    ("Market cap / EV", "$20.91B / $31.35B", f"{sa}/statistics/", "2026-09-11", "EV-MC implies $10.44B net debt"),
    ("Shares outstanding", "170.75M", f"{sa}/statistics/", "2026-09-11", "Down 3.36% YoY"),
    ("TTM revenue", "$9.057B", f"{sa}/financials/", "2026-05-31", "Down 10.0%, largely portfolio divestitures"),
    ("TTM gross profit", "$4.775B", f"{sa}/financials/", "2026-05-31", "52.72% margin"),
    ("TTM operating income", "$3.043B", f"{sa}/financials/", "2026-05-31", "33.60% margin"),
    ("TTM net income", "$1.824B", f"{sa}/financials/", "2026-05-31", "20.14% margin; GAAP"),
    ("TTM OCF / capex / FCF", "$2.694B / $859M / $1.834B", f"{sa}/financials/cash-flow-statement/", "2026-05-31", "20.25% FCF margin"),
    ("Cash / debt", "$96.6M / $10.534B", f"{sa}/financials/balance-sheet/", "2026-05-31", "Net debt $10.437B"),
    ("Goodwill / intangibles", "$5.249B / $2.537B", f"{sa}/financials/balance-sheet/", "2026-05-31", "Tangible book only $470M"),
    ("Beer / wine & spirits revenue", "$8.364B / $693M TTM", f"{sa}/financials/", "2026-05-31", "Beer is 92% of revenue after divestitures"),
    ("FY2027 revenue / adjusted EPS", "$9.10B / $11.83", f"{sa}/forecast/", "2026-09-11", "22 analysts; EPS provider-labelled non-GAAP"),
    ("FY2028 headline revenue / EPS", "$9.27B / $12.39", f"{sa}/forecast/", "2026-09-11", "Later detailed forecast rows gated"),
    ("Analyst targets", "$115 / $170.83 / $209", f"{sa}/forecast/", "2026-09-11", "Low / average / high; 24 analysts"),
    ("Beta", "0.40", f"{sa}/statistics/", "2026-09-11", "Five-year"),
    ("Earnings date", "2026-10-06 AMC", f"{sa}/statistics/", "2026-09-11", "Confirmed by company release"),
    ("Share repurchases", "$852M TTM", f"{sa}/financials/cash-flow-statement/", "2026-05-31", "$2.752B authorization remaining at June 26"),
    ("Debt redemption", "$600M of 4.350% notes", "https://ir.cbrands.com/news-events/press-releases/detail/344/", "2026-09-08", "Redemption effective September 18, 2026"),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [38, 32, 100, 18, 88])

ws = wb.create_sheet("Questions")
title(ws, "Constellation Brands — Open Diligence Questions", 4,
      "Items capable of changing conviction or valuation")
header(ws, 3, ["#", "Question", "Why it matters", "Best next evidence"])
questions = [
    (1, "Can Modelo and Pacifico sustain share gains if high-end beer demand remains weak?", "Beer is now 92% of revenue and carries the valuation.", "Q2 depletion, shipment and Circana share data."),
    (2, "Is August's lackluster off-premise demand cyclical or structural?", "A prolonged volume decline would overwhelm pricing and cost savings.", "Monthly consumer cohorts and regional velocity."),
    (3, "How durable is Hispanic-consumer demand across Texas, Florida, California and New York?", "The portfolio has outsized exposure to this consumer group.", "Regional depletion and buy-rate data."),
    (4, "How much tariff pressure remains after hedges and pricing?", "Mexican production makes imported beer economics policy-sensitive.", "Tariff bridge, sourcing and gross-margin sensitivity."),
    (5, "Can Corona Extra stabilize without cannibalizing Modelo or Pacifico?", "A repaired Corona franchise would broaden growth beyond one flagship.", "Brand-level depletions and distribution."),
    (6, "What is normalized Wine and Spirits margin after divestitures?", "The remaining premium portfolio has only a 5%-6% margin today.", "Quarterly segment margin and inventory normalization."),
    (7, "Are mainstream wine divestitures substantially complete?", "Further sales could reduce revenue but improve mix and fund debt reduction.", "Remaining brand review and pro-forma revenue."),
    (8, "Could $7.8B of goodwill and intangibles face impairment?", "Tangible book is thin relative to acquisition assets.", "Reporting-unit headroom and sensitivity analysis."),
    (9, "Why did FY2025 include $3.276B of writedown and restructuring costs?", "GAAP earnings history is noisy and normalization must be explicit.", "Impairment and divestiture reconciliation."),
    (10, "Can leverage fall while buybacks and dividends continue?", "Net debt is 5.7x FCF despite healthy 2.9x debt/EBITDA.", "Debt targets, maturities and capital-allocation waterfall."),
    (11, "Will the $600M note redemption use cash, new borrowing or divestiture proceeds?", "Funding choice determines whether leverage truly declines.", "Q2 debt schedule and financing cash flows."),
    (12, "Are repurchases below $150 creating durable per-share value?", "The company spent $324M around $140-$159 before the stock fell further.", "Updated authorization use and intrinsic-value framework."),
    (13, "What is the sustainable capex level after Mexican brewery expansion?", "FCF rises materially if capacity build spending normalizes.", "Maintenance versus growth capex disclosure."),
    (14, "How sensitive are margins to aluminum, corn, diesel, gas and peso movements?", "Commodity and FX hedges roll off over time.", "FY2028 hedge coverage and sensitivity."),
    (15, "Will the new 16%-18% FY2027 tax-rate outlook persist?", "Tax normalization affects EPS and cash conversion.", "OB3 and foreign-income tax bridge."),
    (16, "What exactly must Q2 on October 6 show to preserve guidance?", "The next report is the decisive near-term catalyst.", "Beer volume, operating margin and FY2027 outlook."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [7, 88, 78, 78])

ws = wb.create_sheet("Sources")
title(ws, "Constellation Brands — Sources", 4,
      "Public sources accessed September 12, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Identity, price, profile and news"),
    (2, "StockAnalysis financial overview", f"{sa}/financials/", "History, segments and margins"),
    (3, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, goodwill and equity"),
    (4, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, buybacks and divestitures"),
    (5, "StockAnalysis ratios", f"{sa}/financials/ratios/", "Historical valuation and returns"),
    (6, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation, shares, leverage, beta and dates"),
    (7, "StockAnalysis forecast", f"{sa}/forecast/", "Consensus, ratings, targets and FY2027/FY2028 headlines"),
    (8, "Constellation Q1 FY2027 10-Q", "https://ir.cbrands.com/sec-filings/all-sec-filings/content/0000016918-26-000029/stz-20260531.htm", "Official operations, tax, debt and repurchases"),
    (9, "Constellation debt redemption", "https://ir.cbrands.com/news-events/press-releases/detail/344/", "September 2026 debt action"),
    (10, "Barclays conference transcript", "https://www.investing.com/news/transcripts/constellation-brands-at-barclays-consumer-conference-shift-to-margins-93CH-4892087", "Latest demand and strategy commentary"),
    (11, "FRED DGS10", "https://fred.stlouisfed.org/series/DGS10", "Risk-free rate"),
]
for row, values in enumerate(sources, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [7, 44, 112, 80])

for sheet in wb.worksheets:
    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, (int, float)) and cell.number_format == "General":
                cell.number_format = "#,##0.00"
wb.save(OUT)

check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected
assert all(check[name].max_row >= 10 for name in expected)
print(f"WACC: {wacc:.2%}")
print("Targets:", ", ".join(f"{name} ${case['target']:.2f}" for name, case in SCENARIOS.items()))
print(f"Weighted FV: ${weighted:.2f} ({weighted / PRICE - 1:+.1%})")
print(f"Wrote {OUT}")
