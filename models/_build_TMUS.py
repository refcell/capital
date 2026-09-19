#!/usr/bin/env python3
"""Build the six-sheet TMUS valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


AS_OF = "2026-09-19"
PRICE_DATE = "2026-09-18"
PRICE = 168.18
SHARES_MM = 1073.0
MARKET_CAP_MM = 180400.0
EV_MM = 298000.0
DEBT_MM = 120427.0
CASH_MM = 2825.0
NET_DEBT_MM = 117602.0
REVENUE_MM = 92189.0
EBITDA_MM = 34370.0
FCF_MM = 18399.0
OCF_MM = 28833.0
EPS_TTM = 9.54

RF = 0.04943
ERP = 0.05
BETA = 0.33
TAX_RATE = 0.2362
PRETAX_COST_DEBT = 4129.0 / DEBT_MM
COST_EQUITY = RF + BETA * ERP
AFTER_TAX_COST_DEBT = PRETAX_COST_DEBT * (1 - TAX_RATE)
EQUITY_WEIGHT = MARKET_CAP_MM / (MARKET_CAP_MM + DEBT_MM)
DEBT_WEIGHT = 1 - EQUITY_WEIGHT
WACC = EQUITY_WEIGHT * COST_EQUITY + DEBT_WEIGHT * AFTER_TAX_COST_DEBT

SCENARIOS = {
    "Bear": {"eps": 11.09, "pe": 12.0, "weight": 0.25, "rev_cagr": 0.025, "fcf_margin": 0.175, "fcf_multiple": 11.0},
    "Base": {"eps": 14.44, "pe": 15.0, "weight": 0.50, "rev_cagr": 0.050, "fcf_margin": 0.205, "fcf_multiple": 14.0},
    "Bull": {"eps": 16.00, "pe": 17.0, "weight": 0.25, "rev_cagr": 0.065, "fcf_margin": 0.225, "fcf_multiple": 16.0},
}
for case in SCENARIOS.values():
    case["target"] = case["eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1
    case["terminal_revenue"] = 98600.0 * (1 + case["rev_cagr"]) ** 5
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


ws = wb.active
ws.title = "Valuation"
title(ws, "T-Mobile US (NASDAQ: TMUS) — Valuation Summary", 5)
summary = [
    ("As of", AS_OF, "Price close", PRICE),
    ("Shares outstanding (M)", SHARES_MM, "Market capitalization ($M)", MARKET_CAP_MM),
    ("Enterprise value ($M)", EV_MM, "Net debt ($M)", NET_DEBT_MM),
    ("Primary valuation lens", "Forward P/E", "Current stance", "Watch / favorable asymmetry"),
    ("Probability-weighted fair value", FAIR_VALUE, "Upside from current", FAIR_VALUE / PRICE - 1),
]
for row, values in enumerate(summary, 3):
    for col, value in enumerate(values, 1):
        fmt = None
        if row == 3 and col == 4 or row == 7 and col == 2:
            fmt = "$0.00"
        elif row == 7 and col == 4:
            fmt = "0.0%"
        set_cell(ws, row, col, value, font=header_font if col in (1, 3) else None, fill=input_fill if col in (2, 4) else None, fmt=fmt, wrap=True)
section(ws, 10, "Current Valuation Metrics", 5)
valuation_rows = [
    ("Trailing P/E", 17.63, "x", "GAAP TTM EPS $9.54"),
    ("Forward P/E", 13.43, "x", "Consensus adjusted EPS; primary lens"),
    ("Price / Sales", 1.96, "x", "TTM revenue $92.19B"),
    ("Price / FCF", 9.80, "x", "TTM FCF $18.40B"),
    ("EV / Sales", 3.23, "x", "Large debt and lease obligations matter"),
    ("EV / EBITDA", 8.67, "x", "TTM EBITDA $34.37B"),
    ("EV / FCF", 16.20, "x", "Debt-aware cross-check"),
    ("Debt / FCF", 6.55, "x", "High leverage makes FCF-exit equity values sensitive"),
    ("FCF yield", 0.1020, "%", "Strong current cash yield"),
    ("Analyst average target", 243.38, "$", "27 analysts; 44.7% above current"),
]
table(ws, 11, ["Metric", "Value", "Unit", "Interpretation"], valuation_rows, [28, 18, 12, 70])
for row in range(12, 22):
    ws.cell(row, 2).number_format = "0.00"
ws.cell(20, 2).number_format = "0.00%"
ws.cell(21, 2).number_format = "$0.00"
section(ws, 24, "Framework Note", 5)
set_cell(ws, 25, 1, "Net debt equals 6.4x TTM FCF. Forward P/E is therefore the primary scenario lens: a terminal FCF multiple less net debt can amplify modest assumption changes into unstable equity values. EV/EBITDA and EV/FCF remain useful cross-checks, while the thesis centers on service-revenue growth, cash conversion, buybacks, and deleveraging.", wrap=True)
ws.merge_cells("A25:E27")

ws = wb.create_sheet("WACC")
title(ws, "T-Mobile US — WACC", 4)
wacc_rows = [
    ("Risk-free rate", RF, "CNBC US10Y, Sep. 18, 2026"),
    ("Equity risk premium", ERP, "Standard U.S. assumption"),
    ("Levered beta", BETA, "StockAnalysis, Sep. 18, 2026"),
    ("Cost of equity", COST_EQUITY, "Risk-free rate + beta × ERP"),
    ("Pre-tax cost of debt", PRETAX_COST_DEBT, "$4.129B cash interest / $120.427B debt"),
    ("Effective tax rate", TAX_RATE, "TTM effective rate"),
    ("After-tax cost of debt", AFTER_TAX_COST_DEBT, "Pre-tax cost × (1 − tax rate)"),
    ("Market capitalization ($M)", MARKET_CAP_MM, "Sep. 18 close"),
    ("Total debt ($M)", DEBT_MM, "June 30 balance sheet, including leases"),
    ("Equity weight", EQUITY_WEIGHT, "Market-value capital structure"),
    ("Debt weight", DEBT_WEIGHT, "Market-value capital structure"),
    ("Calculated WACC", WACC, "Low beta and low embedded debt cost suppress WACC"),
]
table(ws, 3, ["Component", "Value", "Source / Calculation"], wacc_rows, [34, 20, 65])
for row in range(4, 16):
    ws.cell(row, 2).number_format = "$#,##0.0" if row in (11, 12) else "0.00%"
ws.cell(15, 2).fill = output_fill
ws.cell(15, 2).font = header_font

ws = wb.create_sheet("Scenarios")
title(ws, "T-Mobile US — Forward P/E Scenario Analysis", 5)
set_cell(ws, 3, 1, "Primary framework: forward P/E on adjusted consensus earnings. The bear case uses the visible low FY2026 EPS estimate and a compressed multiple; the base uses visible FY2027 consensus. FCF multiples are secondary because $117.6B net debt amplifies equity sensitivity.", wrap=True)
ws.merge_cells("A3:E3")
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
scenario_rows = []
for label, key, _ in metrics:
    vals = []
    for name in ("Bear", "Base", "Bull"):
        case = SCENARIOS[name]
        vals.append(case["target"] * case["weight"] if key is None else case[key])
    scenario_rows.append((label, *vals, ""))
scenario_rows.extend([
    ("Probability-weighted fair value", "", "", FAIR_VALUE, ""),
    ("Current price", "", "", PRICE, ""),
    ("Weighted upside", "", "", FAIR_VALUE / PRICE - 1, ""),
])
table(ws, 5, ["Metric", "Bear", "Base", "Bull", "Notes"], scenario_rows, [34, 18, 18, 18, 54])
for row, (_, _, fmt) in enumerate(metrics, 6):
    for col in range(2, 5):
        ws.cell(row, col).number_format = fmt
for row in range(18, 21):
    ws.cell(row, 4).fill = output_fill
ws.cell(18, 4).number_format = "$0.00"
ws.cell(19, 4).number_format = "$0.00"
ws.cell(20, 4).number_format = "0.0%"
set_cell(ws, 22, 1, "Bear: pricing pressure, elevated churn, and slower broadband growth compress adjusted EPS and the multiple. Base: FY2027 adjusted EPS reaches $14.44 and the stock earns 15x. Bull: network leadership, fiber/FWA growth, cost control, and buybacks produce $16.00 of adjusted EPS at 17x.", wrap=True)
ws.merge_cells("A22:E23")

ws = wb.create_sheet("Actuals Source Audit")
title(ws, "T-Mobile US — Actuals Source Audit", 5)
audit_rows = [
    ("Price", "$168.18", PRICE_DATE, "https://stockanalysis.com/stocks/tmus/", "Closing price"),
    ("Market cap / EV", "$180.40B / $298.00B", PRICE_DATE, "https://stockanalysis.com/stocks/tmus/statistics/", "EV includes large debt and lease obligations"),
    ("Shares outstanding", "1.07B", PRICE_DATE, "https://stockanalysis.com/stocks/tmus/statistics/", "Down 3.93% YoY"),
    ("TTM revenue", "$92.189B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/", "+9.68%"),
    ("TTM gross profit", "$58.129B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/", "63.05% margin"),
    ("TTM operating income", "$20.366B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/", "22.09% margin"),
    ("TTM net income / GAAP EPS", "$10.560B / $9.54", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/", "Net income down 13.5%"),
    ("TTM OCF / capex / FCF", "$28.833B / $10.434B / $18.399B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/cash-flow-statement/", "19.96% FCF margin"),
    ("Cash / total debt / net debt", "$2.825B / $120.427B / $117.602B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/balance-sheet/", "Debt includes $35.4B current and long-term leases"),
    ("Goodwill / intangibles", "$13.667B / $101.473B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/balance-sheet/", "Spectrum and merger assets dominate capital base"),
    ("TTM buybacks / dividends", "$12.388B / $4.343B", "2026-06-30", "https://stockanalysis.com/stocks/tmus/financials/cash-flow-statement/", "Combined distributions equal 91% of FCF"),
    ("FY2026 revenue consensus", "$94.37B", "2026-09-14", "https://stockanalysis.com/stocks/tmus/forecast/", "+6.86%; 25 analysts"),
    ("FY2026 adjusted EPS consensus", "$12.18", "2026-09-14", "https://stockanalysis.com/stocks/tmus/forecast/", "Non-GAAP; range $11.09-$13.09"),
    ("FY2027 revenue / adjusted EPS", "$98.60B / $14.44", "2026-09-14", "https://stockanalysis.com/stocks/tmus/forecast/", "+4.49% revenue; +18.58% EPS"),
    ("Analyst target", "$243.38", "2026-09-14", "https://stockanalysis.com/stocks/tmus/forecast/", "Low $169; high $300; 27 analysts"),
    ("Beta", "0.33", PRICE_DATE, "https://stockanalysis.com/stocks/tmus/statistics/", "5-year beta"),
    ("Next earnings", "Oct. 22 / company call Oct. 28", PRICE_DATE, "https://stockanalysis.com/stocks/tmus/", "Provider estimate differs from company-hosted call announcement"),
    ("800 MHz spectrum sale", "Completed", "2026-08-11", "https://www.businesswire.com/news/home/20260811977813/en/", "Capital recycling; consideration should be reconciled"),
    ("CFO transition", "Jessica Uhl succeeds Peter Osvaldik Feb. 2027", "2026-09-03", "https://www.reuters.com/business/t-mobile-cfo-peter-osvaldik-step-down-february-2027-jessica-uhl-succeed-2026-09-03/", "Leadership and capital-allocation continuity"),
    ("10Y Treasury", "4.943%", PRICE_DATE, "https://www.cnbc.com/quotes/US10Y", "WACC risk-free anchor"),
]
table(ws, 3, ["Data Point", "Value", "Source Date", "Source URL", "Notes"], audit_rows, [30, 38, 17, 76, 60])

ws = wb.create_sheet("Questions")
title(ws, "T-Mobile US — Open Underwriting Questions", 4)
questions = [
    (1, "How much of the $120.4B total debt is financial debt versus lease obligations, and what is the weighted maturity/refinancing schedule through 2030?", "Leverage"),
    (2, "Can management reduce net debt while sustaining $12B-plus annual buybacks and a growing dividend?", "Capital allocation"),
    (3, "What explains TTM net income declining 13.5% while operating income and FCF continue to rise?", "Earnings quality"),
    (4, "How much of postpaid service growth is ARPA/price versus account and customer growth?", "Growth quality"),
    (5, "What churn increase would follow if Verizon or AT&T intensifies handset subsidies or price promotions?", "Competition"),
    (6, "What is the sustainable addressable market and capacity ceiling for fixed wireless access?", "Broadband"),
    (7, "How will fiber expansion economics compare with FWA on capital intensity, customer acquisition cost, and payback?", "Fiber strategy"),
    (8, "What are the remaining integration costs and synergies from Sprint and more recent acquisitions?", "Integration"),
    (9, "How should investors value $101.5B of spectrum and other intangibles, and what impairment or obsolescence risk exists?", "Balance sheet"),
    (10, "What cash proceeds and accounting gain resulted from the August 800 MHz spectrum sale, and how will proceeds be deployed?", "Spectrum"),
    (11, "Does the Starlink direct-to-device relationship strengthen T-Mobile's differentiation or create a future wholesale/competitive conflict?", "Technology"),
    (12, "What governance protections apply if Deutsche Telekom pursues a larger stake, merger, or control transaction?", "Governance"),
    (13, "What priorities will incoming CFO Jessica Uhl change, if any, in leverage, buybacks, and fiber investment?", "Leadership"),
    (14, "Why do StockAnalysis and the company announcement indicate different October earnings/call dates, and what is the confirmed reporting calendar?", "Next earnings"),
]
table(ws, 3, ["#", "Question", "Topic"], questions, [8, 108, 28])

ws = wb.create_sheet("Sources")
title(ws, "T-Mobile US — Sources", 4)
sources = [
    (1, "StockAnalysis overview", "https://stockanalysis.com/stocks/tmus/", "Price, profile, market summary, news"),
    (2, "StockAnalysis financial overview", "https://stockanalysis.com/stocks/tmus/financials/", "Historical and TTM financials, segments, margins"),
    (3, "StockAnalysis balance sheet", "https://stockanalysis.com/stocks/tmus/financials/balance-sheet/", "Cash, debt, equity, intangibles"),
    (4, "StockAnalysis cash flow", "https://stockanalysis.com/stocks/tmus/financials/cash-flow-statement/", "OCF, capex, FCF, buybacks, dividends"),
    (5, "StockAnalysis statistics", "https://stockanalysis.com/stocks/tmus/statistics/", "Valuation, beta, capital structure, returns"),
    (6, "StockAnalysis forecast", "https://stockanalysis.com/stocks/tmus/forecast/", "Consensus revenue, adjusted EPS, price targets"),
    (7, "T-Mobile Q3 call announcement", "https://www.businesswire.com/news/home/20260917015300/en/", "Company-hosted call date"),
    (8, "T-Mobile spectrum sale announcement", "https://www.businesswire.com/news/home/20260811977813/en/", "800 MHz portfolio transaction"),
    (9, "Reuters CFO transition", "https://www.reuters.com/business/t-mobile-cfo-peter-osvaldik-step-down-february-2027-jessica-uhl-succeed-2026-09-03/", "CFO succession"),
    (10, "CNBC US10Y", "https://www.cnbc.com/quotes/US10Y", "Risk-free rate"),
]
table(ws, 3, ["#", "Source", "URL", "Use"], sources, [8, 34, 86, 52])

for ws in wb.worksheets:
    ws.sheet_view.showGridLines = False
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is not None and cell.alignment.wrap_text:
                ws.row_dimensions[cell.row].height = max(ws.row_dimensions[cell.row].height or 15, 30)

output = Path(__file__).with_name("2026-09-19 T-Mobile US Model.xlsx")
wb.save(output)

check = load_workbook(output, data_only=False)
assert check.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check["Scenarios"]["B8"].value < PRICE
assert abs(sum(case["weight"] for case in SCENARIOS.values()) - 1.0) < 1e-9
print(f"WACC: {WACC:.2%}")
print("Targets:", ", ".join(f"{name} ${case['target']:.2f}" for name, case in SCENARIOS.items()))
print(f"Probability-weighted fair value: ${FAIR_VALUE:.2f} ({FAIR_VALUE / PRICE - 1:.1%})")
print(f"Workbook: {output}")
