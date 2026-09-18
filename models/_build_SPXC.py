#!/usr/bin/env python3
"""Build the six-sheet SPXC valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


AS_OF = "2026-09-18"
PRICE = 179.70
SHARES_MM = 50.09
MARKET_CAP_MM = 9000.0
REPORTED_EV_MM = 9450.0
REPORTED_DEBT_MM = 614.7
CASH_MM = 166.4
NET_DEBT_MM = REPORTED_DEBT_MM - CASH_MM
TTM_REVENUE_MM = 2476.0
TTM_FCF_MM = 303.4
TTM_EBITDA_MM = 521.8

RF = 0.04943
ERP = 0.05
BETA = 1.27
TAX_RATE = 0.2211
PRETAX_COST_DEBT = 41.7 / REPORTED_DEBT_MM
COST_EQUITY = RF + BETA * ERP
AFTER_TAX_COST_DEBT = PRETAX_COST_DEBT * (1 - TAX_RATE)
EQUITY_WEIGHT = MARKET_CAP_MM / (MARKET_CAP_MM + REPORTED_DEBT_MM)
DEBT_WEIGHT = 1 - EQUITY_WEIGHT
WACC = EQUITY_WEIGHT * COST_EQUITY + DEBT_WEIGHT * AFTER_TAX_COST_DEBT

SCENARIOS = {
    "Bear": {"eps": 8.20, "pe": 19.0, "weight": 0.20, "rev_cagr": 0.06, "fcf_margin": 0.10, "fcf_multiple": 20.0},
    "Base": {"eps": 9.72, "pe": 24.0, "weight": 0.50, "rev_cagr": 0.11, "fcf_margin": 0.12, "fcf_multiple": 24.0},
    "Bull": {"eps": 11.20, "pe": 27.0, "weight": 0.30, "rev_cagr": 0.15, "fcf_margin": 0.14, "fcf_multiple": 27.0},
}
for case in SCENARIOS.values():
    case["target"] = case["eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1
    case["terminal_revenue"] = 2740.0 * (1 + case["rev_cagr"]) ** 5
    case["terminal_fcf"] = case["terminal_revenue"] * case["fcf_margin"]
    case["fcf_value"] = (case["terminal_fcf"] * case["fcf_multiple"] - NET_DEBT_MM) / SHARES_MM
FAIR_VALUE = sum(case["target"] * case["weight"] for case in SCENARIOS.values())

wb = Workbook()
title_font = Font(name="Aptos Display", size=15, bold=True, color="FFFFFF")
section_font = Font(name="Aptos", size=11, bold=True, color="FFFFFF")
header_font = Font(name="Aptos", size=10, bold=True)
body_font = Font(name="Aptos", size=10)
title_fill = PatternFill("solid", fgColor="17365D")
section_fill = PatternFill("solid", fgColor="366092")
header_fill = PatternFill("solid", fgColor="D9EAF7")
input_fill = PatternFill("solid", fgColor="FFF2CC")
output_fill = PatternFill("solid", fgColor="E2F0D9")
thin = Side(style="thin", color="B7B7B7")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def set_cell(ws, row, col, value, *, font=None, fill=None, fmt=None, wrap=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = font or body_font
    cell.border = border
    cell.alignment = Alignment(vertical="top", wrap_text=wrap)
    if fill:
        cell.fill = fill
    if fmt:
        cell.number_format = fmt
    return cell


def title(ws, text, last_col=5):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    cell = ws.cell(1, 1, text)
    cell.font = title_font
    cell.fill = title_fill
    cell.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 25
    ws.freeze_panes = "A3"


def section(ws, row, text, last_col=5):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row, 1, text)
    cell.font = section_font
    cell.fill = section_fill


def table(ws, row, headers, rows, widths=None):
    for col, value in enumerate(headers, 1):
        set_cell(ws, row, col, value, font=header_font, fill=header_fill, wrap=True)
    for r, values in enumerate(rows, row + 1):
        for col, value in enumerate(values, 1):
            set_cell(ws, r, col, value, wrap=True)
    if widths:
        for col, width in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width


# Valuation
ws = wb.active
ws.title = "Valuation"
title(ws, "SPX Technologies (NYSE: SPXC) — Valuation Summary", 5)
summary = [
    ("As of", AS_OF, "Price close", PRICE),
    ("Shares outstanding (M)", SHARES_MM, "Market capitalization ($M)", MARKET_CAP_MM),
    ("Reported enterprise value ($M)", REPORTED_EV_MM, "Reported net debt ($M)", NET_DEBT_MM),
    ("Primary valuation lens", "Forward P/E", "Current stance", "Watch / favorable risk-reward"),
    ("Probability-weighted fair value", FAIR_VALUE, "Upside from current", FAIR_VALUE / PRICE - 1),
]
for row, values in enumerate(summary, 3):
    for col, value in enumerate(values, 1):
        fill = input_fill if col in (2, 4) else None
        fmt = "$0.00" if (row == 3 and col == 4) or (row == 7 and col == 2) else None
        if row == 7 and col == 4:
            fmt = "0.0%"
        set_cell(ws, row, col, value, font=header_font if col in (1, 3) else None, fill=fill, fmt=fmt, wrap=True)
section(ws, 10, "Current Valuation Metrics", 5)
valuation_rows = [
    ("Trailing P/E", 32.36, "x", "GAAP TTM EPS $5.55; acquisition amortization depresses comparability"),
    ("Forward P/E", 19.64, "x", "Based on non-GAAP adjusted consensus"),
    ("Price / Sales", 3.64, "x", "Premium reflects HVAC/data-center growth and margin expansion"),
    ("Price / FCF", 29.67, "x", "TTM FCF $303.4M"),
    ("EV / Sales", 3.82, "x", "Reported EV may not yet capture post-June acquisition financing"),
    ("EV / EBITDA", 18.11, "x", "TTM EBITDA $521.8M"),
    ("EV / FCF", 31.14, "x", "Useful cross-check, not primary lens"),
    ("FCF yield", 0.0337, "%", "Modest current yield; thesis requires compounding"),
    ("Analyst average target", 272.17, "$", "12 analysts; 51.5% above current price"),
]
table(ws, 11, ["Metric", "Value", "Unit", "Interpretation"], valuation_rows, [28, 18, 12, 70])
for row in range(12, 21):
    ws.cell(row, 2).number_format = "0.00"
ws.cell(19, 2).number_format = "0.00%"
ws.cell(20, 2).number_format = "$0.00"
section(ws, 23, "Capital Structure Caveat", 5)
set_cell(ws, 24, 1, "SPX reported $614.7M debt and $166.4M cash at June 27, 2026. The company then borrowed $340M for Neptronic in July and paid $410M cash for FIS Water in September. Because the September financing mix has not been fully disclosed, reported EV and net debt are stale; forward P/E is the cleanest primary lens until Q3 reporting.", wrap=True)
ws.merge_cells("A24:E26")

# WACC
ws = wb.create_sheet("WACC")
title(ws, "SPX Technologies — WACC", 4)
wacc_rows = [
    ("Risk-free rate", RF, "CNBC US10Y, Sep. 18, 2026"),
    ("Equity risk premium", ERP, "Standard U.S. assumption"),
    ("Levered beta", BETA, "StockAnalysis, Sep. 17, 2026"),
    ("Cost of equity", COST_EQUITY, "Risk-free rate + beta × ERP"),
    ("Pre-tax cost of debt", PRETAX_COST_DEBT, "$41.7M cash interest / $614.7M reported debt"),
    ("Effective tax rate", TAX_RATE, "TTM effective rate"),
    ("After-tax cost of debt", AFTER_TAX_COST_DEBT, "Pre-tax cost × (1 − tax rate)"),
    ("Market capitalization ($M)", MARKET_CAP_MM, "Sep. 17 close"),
    ("Reported debt ($M)", REPORTED_DEBT_MM, "June 27 balance sheet; pre-Neptronic/FIS Water"),
    ("Equity weight", EQUITY_WEIGHT, "Reported capital structure"),
    ("Debt weight", DEBT_WEIGHT, "Reported capital structure"),
    ("Calculated WACC", WACC, "Close to StockAnalysis stated 10.82%"),
]
table(ws, 3, ["Component", "Value", "Source / Calculation"], wacc_rows, [34, 20, 62])
for row in range(4, 16):
    if row not in (11, 12):
        ws.cell(row, 2).number_format = "0.00%"
    else:
        ws.cell(row, 2).number_format = "$#,##0.0"
ws.cell(15, 2).fill = output_fill
ws.cell(15, 2).font = header_font

# Scenarios
ws = wb.create_sheet("Scenarios")
title(ws, "SPX Technologies — Forward P/E Scenario Analysis", 5)
set_cell(ws, 3, 1, "Primary framework: forward P/E on adjusted EPS. Bear must show downside; base is calibrated within 20% of the $272.17 analyst average target. FCF multiple is a secondary cross-check because acquisition financing is not yet fully disclosed.", wrap=True)
ws.merge_cells("A3:E3")
scenario_rows = []
metrics = [
    ("Adjusted EPS anchor", "eps", "$0.00"),
    ("Exit P/E", "pe", "0.0x"),
    ("Target price", "target", "$0.00"),
    ("Upside / (downside)", "upside", "0.0%"),
    ("Probability weight", "weight", "0%"),
    ("Weighted value / share", None, "$0.00"),
    ("Revenue CAGR (5Y)", "rev_cagr", "0.0%"),
    ("Terminal revenue ($M)", "terminal_revenue", "$#,##0"),
    ("Terminal FCF margin", "fcf_margin", "0.0%"),
    ("Terminal FCF ($M)", "terminal_fcf", "$#,##0"),
    ("Exit FCF multiple", "fcf_multiple", "0.0x"),
    ("FCF cross-check / share", "fcf_value", "$0.00"),
]
for label, key, _ in metrics:
    values = []
    for case_name in ("Bear", "Base", "Bull"):
        case = SCENARIOS[case_name]
        values.append(case["target"] * case["weight"] if key is None else case[key])
    scenario_rows.append((label, *values))
scenario_rows.extend([
    ("Probability-weighted fair value", "", "", FAIR_VALUE),
    ("Current price", "", "", PRICE),
    ("Weighted upside", "", "", FAIR_VALUE / PRICE - 1),
])
table(ws, 5, ["Metric", "Bear", "Base", "Bull", "Notes"], [row + ("" if len(row) == 4 else "",) for row in scenario_rows], [34, 18, 18, 18, 50])
for row, (_, _, fmt) in enumerate(metrics, 6):
    for col in range(2, 5):
        ws.cell(row, col).number_format = fmt
for row in range(18, 21):
    ws.cell(row, 4).fill = output_fill
ws.cell(18, 4).number_format = "$0.00"
ws.cell(19, 4).number_format = "$0.00"
ws.cell(20, 4).number_format = "0.0%"
set_cell(ws, 22, 1, "Bear: guidance low end and multiple compression after integration disappointments. Base: FY2027 consensus EPS and a 24x multiple. Bull: data-center cooling capacity fills, D&M margins hold, acquisitions integrate cleanly, and EPS reaches $11.20.", wrap=True)
ws.merge_cells("A22:E23")

# Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "SPX Technologies — Actuals Source Audit", 5)
audit_rows = [
    ("Price", "$179.70", "2026-09-17", "https://stockanalysis.com/stocks/spxc/", "Closing price"),
    ("Market cap / EV", "$9.00B / $9.45B", "2026-09-17", "https://stockanalysis.com/stocks/spxc/statistics/", "EV likely stale after recent acquisitions"),
    ("Shares outstanding", "50.09M", "2026-09-17", "https://stockanalysis.com/stocks/spxc/statistics/", "+6.19% YoY after 2025 issuance"),
    ("TTM revenue", "$2.476B", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/", "+20.63%"),
    ("TTM gross profit", "$997.5M", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/", "40.29% margin"),
    ("TTM operating income", "$391.6M", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/", "15.82% margin"),
    ("TTM net income / EPS", "$278.9M / $5.55", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/", "GAAP"),
    ("TTM OCF / capex / FCF", "$421.9M / $118.5M / $303.4M", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/cash-flow-statement/", "12.25% FCF margin"),
    ("Cash / debt", "$166.4M / $614.7M", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/balance-sheet/", "Pre-Neptronic and FIS Water financing"),
    ("Goodwill / intangibles", "$1.234B / $1.015B", "2026-06-27", "https://stockanalysis.com/stocks/spxc/financials/balance-sheet/", "96% of common equity combined"),
    ("Backlog", "$934.8M", "2025-12-31", "https://stockanalysis.com/stocks/spxc/financials/balance-sheet/", "Up from $657.7M in FY2024"),
    ("FY2026 revenue consensus", "$2.74B", "2026-09-16", "https://stockanalysis.com/stocks/spxc/forecast/", "+21.09%"),
    ("FY2026 adjusted EPS consensus", "$8.48", "2026-09-16", "https://stockanalysis.com/stocks/spxc/forecast/", "Non-GAAP; 11 analysts"),
    ("FY2027 revenue / EPS", "$3.05B / $9.72", "2026-09-16", "https://stockanalysis.com/stocks/spxc/forecast/", "+11.17% revenue, +14.61% EPS"),
    ("Analyst target", "$272.17", "2026-09-16", "https://stockanalysis.com/stocks/spxc/forecast/", "Low $225; high $310; 12 analysts"),
    ("Beta", "1.27", "2026-09-17", "https://stockanalysis.com/stocks/spxc/statistics/", "5-year beta"),
    ("Next earnings", "2026-10-29", "2026-09-17", "https://stockanalysis.com/stocks/spxc/statistics/", "Estimated, after market close"),
    ("Q2 guidance", "$2.705-$2.765B revenue; $8.20-$8.60 adj. EPS", "2026-07-30", "https://www.globenewswire.com/news-release/2026/07/30/3336435/0/en/spx-reports-second-quarter-2026-results.html", "Excludes later FIS Water impact"),
    ("FIS Water acquisition", "$410M cash; ~$105M 2026 revenue", "2026-09-15", "https://www.globenewswire.com/news-release/2026/09/15/3362650/0/en/spx-technologies-announces-acquisition-of-fis-water.html", "Financing mix not fully disclosed"),
    ("10Y Treasury", "4.943%", "2026-09-18", "https://www.cnbc.com/quotes/US10Y", "10:01 PM EDT quote"),
]
table(ws, 3, ["Data Point", "Value", "Source Date", "Source URL", "Notes"], audit_rows, [30, 35, 16, 75, 58])

# Questions
ws = wb.create_sheet("Questions")
title(ws, "SPX Technologies — Open Underwriting Questions", 4)
questions = [
    (1, "What portion of the $410M FIS Water purchase is debt-funded, and what will pro forma net leverage be after both Neptronic and FIS Water?", "Capital structure"),
    (2, "What revenue and EBITDA contribution should investors expect from FIS Water in 2027, and what synergies are embedded?", "Acquisition economics"),
    (3, "How much of the 2026 HVAC growth is organic versus acquired, and what is the sustainable organic rate after data-center capacity normalizes?", "Growth quality"),
    (4, "When will start-up inefficiencies at expanded cooling capacity fade, and can HVAC segment margin return above 25%?", "Margins"),
    (5, "How concentrated is cooling demand among hyperscale data-center customers, OEMs, and engineering channels?", "Customer concentration"),
    (6, "What percentage of backlog is cancellable, fixed price, and exposed to tariffs or raw-material inflation?", "Backlog quality"),
    (7, "Why did goodwill and intangibles rise to $2.25B, and what impairment sensitivity exists if acquired growth slows?", "Balance sheet"),
    (8, "What drove the 2025 common-share issuance of $575M and the 6.2% YoY increase in shares?", "Dilution"),
    (9, "How should investors reconcile GAAP EPS of $5.55 TTM with adjusted FY2026 EPS guidance of $8.20-$8.60?", "Earnings quality"),
    (10, "What is normalized maintenance capex after the current capacity expansion, versus growth capex?", "Cash conversion"),
    (11, "Can D&M sustain its Q2 28.9% segment margin after favorable mix and optimization benefits normalize?", "Segment durability"),
    (12, "How exposed are communication technologies and navigation products to U.S. government funding and fixed-price contract risk?", "End-market risk"),
    (13, "Will management prioritize deleveraging over additional acquisitions and buybacks through 2027?", "Capital allocation"),
    (14, "What revenue, margin, and leverage update will management provide on October 29 after closing FIS Water?", "Next catalyst"),
]
table(ws, 3, ["#", "Question", "Topic"], questions, [8, 105, 28])

# Sources
ws = wb.create_sheet("Sources")
title(ws, "SPX Technologies — Sources", 4)
sources = [
    (1, "StockAnalysis overview", "https://stockanalysis.com/stocks/spxc/", "Price, profile, earnings date"),
    (2, "StockAnalysis financials", "https://stockanalysis.com/stocks/spxc/financials/", "Historical and TTM financials"),
    (3, "StockAnalysis balance sheet", "https://stockanalysis.com/stocks/spxc/financials/balance-sheet/", "Cash, debt, goodwill, equity, backlog"),
    (4, "StockAnalysis cash flow", "https://stockanalysis.com/stocks/spxc/financials/cash-flow-statement/", "OCF, capex, FCF, acquisitions"),
    (5, "StockAnalysis statistics", "https://stockanalysis.com/stocks/spxc/statistics/", "Valuation, beta, capital structure, ratios"),
    (6, "StockAnalysis forecast", "https://stockanalysis.com/stocks/spxc/forecast/", "Consensus estimates and price targets"),
    (7, "StockAnalysis company profile", "https://stockanalysis.com/stocks/spxc/company/", "Segments, brands, management"),
    (8, "SPX Q2 2026 results", "https://www.globenewswire.com/news-release/2026/07/30/3336435/0/en/spx-reports-second-quarter-2026-results.html", "Guidance, segments, reconciliation"),
    (9, "FIS Water acquisition", "https://www.globenewswire.com/news-release/2026/09/15/3362650/0/en/spx-technologies-announces-acquisition-of-fis-water.html", "Purchase price and strategic rationale"),
    (10, "CNBC U.S. 10-year Treasury", "https://www.cnbc.com/quotes/US10Y", "Risk-free rate"),
]
table(ws, 3, ["#", "Source", "URL", "Use"], sources, [8, 34, 90, 48])

for ws in wb.worksheets:
    ws.sheet_view.showGridLines = False
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is not None and cell.alignment.wrap_text:
                ws.row_dimensions[cell.row].height = max(ws.row_dimensions[cell.row].height or 15, 30)

output = Path(__file__).with_name("[2026-09-18] SPX Technologies Model.xlsx")
wb.save(output)

check = load_workbook(output, data_only=False)
assert check.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert abs(check["Scenarios"]["D18"].value - FAIR_VALUE) < 0.01
print(f"WACC: {WACC:.2%}")
for name, case in SCENARIOS.items():
    print(f"{name}: ${case['target']:.2f} ({case['upside']:.1%}); FCF cross-check ${case['fcf_value']:.2f}")
print(f"Probability-weighted FV: ${FAIR_VALUE:.2f} ({FAIR_VALUE / PRICE - 1:.1%})")
print(f"Created {output}")
