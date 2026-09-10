#!/usr/bin/env python3
"""Build Carnival Corporation's six-sheet valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).with_name("2026-09-10 Carnival Corporation Model.xlsx")
PRICE, SHARES = 22.70, 1370.0  # USD, millions
MARKET_CAP, ENTERPRISE_VALUE = 31090.0, 55020.0  # USD millions
NET_DEBT = ENTERPRISE_VALUE - MARKET_CAP
TTM_REVENUE, TTM_FCF, TTM_EBITDA = 27311.0, 3200.0, 7300.0
FY26_REVENUE, FY26_EPS, FY27_REVENUE, FY27_EPS = 27640.0, 2.24, 28620.0, 2.63

SCENARIOS = {
    "Bear": {"revenue_cagr": .005, "terminal_eps": 2.20, "pe": 8.0, "weight": .25},
    "Base": {"revenue_cagr": .035, "terminal_eps": 3.00, "pe": 11.0, "weight": .50},
    "Bull": {"revenue_cagr": .055, "terminal_eps": 3.50, "pe": 13.0, "weight": .25},
}
for case in SCENARIOS.values():
    case["terminal_revenue"] = FY27_REVENUE * (1 + case["revenue_cagr"]) ** 5
    case["target"] = case["terminal_eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1
weighted = sum(c["target"] * c["weight"] for c in SCENARIOS.values())
assert SCENARIOS["Bear"]["target"] < PRICE
assert abs(SCENARIOS["Base"]["target"] / 35.30 - 1) < .20

rf, erp, beta = .0430, .05, 2.31
ke = rf + beta * erp
debt, kd, tax = 26170.0, 1200.0 / 26170.0, .05
ew = MARKET_CAP / (MARKET_CAP + debt)
dw = 1 - ew
wacc = ew * ke + dw * kd * (1 - tax)

wb = Workbook()
navy, blue, gold, white = "17365D", "D9EAF7", "D8B34B", "FFFFFF"
thin = Side(style="thin", color="A6A6A6")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def put(ws, r, c, value, bold=False, fill=None, color="000000", size=10):
    cell = ws.cell(r, c, value)
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

def header(ws, r, values):
    for c, value in enumerate(values, 1):
        put(ws, r, c, value, True, navy, white)

def finish(ws, widths):
    for c, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = width
    ws.freeze_panes = "A4"
    ws.sheet_view.showGridLines = False
    ws.auto_filter.ref = ws.dimensions

# Valuation
ws = wb.active
ws.title = "Valuation"
title(ws, "Carnival Corporation & plc (CCL) — Valuation", 4,
      "Quote: September 9, 2026 close | Model date: September 10, 2026 | USD unless noted")
header(ws, 3, ["Field", "Value", "Comment"])
facts = [
    ("Company", "Carnival Corporation & plc", "Largest global cruise operator by multi-brand portfolio"),
    ("Ticker", "NYSE: CCL", "Dual-listed structure; this model values CCL common shares"),
    ("Price", PRICE, "September 9 close"), ("Shares outstanding (M)", SHARES, "Current share class"),
    ("Market capitalization ($M)", MARKET_CAP, "StockAnalysis"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "StockAnalysis"),
    ("Net debt proxy ($M)", NET_DEBT, "EV less market capitalization"),
    ("Primary lens", "Forward P/E", "Net debt is 7.5x TTM FCF; EV/FCF can over-amplify leverage"),
    ("Stance", "Watch / attractive with leverage risk", "Low earnings multiple and strong cash recovery offset fuel and debt sensitivity"),
]
for r, row in enumerate(facts, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
header(ws, 14, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E", 10.41, "GAAP TTM"), ("Forward P/E", 9.72, "Adjusted provider estimates"),
    ("P/S", 1.14, "Equity value / TTM revenue"), ("P/FCF", 9.72, "10.3% equity FCF yield"),
    ("EV/FCF", 17.19, "Debt-adjusted cross-check"), ("EV/Sales", 2.01, "Capital-intensive fleet"),
    ("EV/EBITDA", 7.53, "Primary enterprise-value cross-check"),
    ("Debt/EBITDA", 3.38, "Falling but still material"),
    ("Interest coverage", 3.67, "Improved, not recession-proof"),
    ("Analyst average target", 35.30, "30 analysts; low $28.70, high $43.00"),
]
for r, row in enumerate(metrics, 15):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [32, 28, 98, 14])

# WACC
ws = wb.create_sheet("WACC")
title(ws, "Carnival — Weighted Average Cost of Capital", 4, "CAPM using market-value weights")
header(ws, 3, ["Component", "Value", "Source / formula"])
rows = [
    ("Risk-free rate", rf, "U.S. 10-year normalized September 2026 reference"),
    ("Equity risk premium", erp, "Model assumption"), ("Levered beta", beta, "StockAnalysis five-year beta"),
    ("Cost of equity", ke, "Rf + beta × ERP"), ("Pre-tax cost of debt", kd, "$1.2B cash interest / $26.17B debt"),
    ("Normalized tax rate", tax, "Cruise shipping regimes make the 0.71% TTM rate unusually low"),
    ("Market cap ($M)", MARKET_CAP, "USD millions"), ("Debt ($M)", debt, "TTM balance sheet"),
    ("Equity weight", ew, "E/(D+E)"), ("Debt weight", dw, "D/(D+E)"),
    ("WACC", wacc, "E/V×Ke + D/V×Kd×(1−T)"),
]
for r, row in enumerate(rows, 4):
    for c, value in enumerate(row, 1):
        cell = put(ws, r, c, value, c == 1 or row[0] == "WACC", gold if row[0] == "WACC" else None)
        if c == 2 and row[0] not in {"Levered beta", "Market cap ($M)", "Debt ($M)"}: cell.number_format = "0.00%"
finish(ws, [32, 24, 100, 14])

# Scenarios
ws = wb.create_sheet("Scenarios")
title(ws, "Carnival — Five-Year Forward P/E Scenarios", 6,
      "Forward P/E is primary; EV/EBITDA and FCF are cross-checks because leverage amplifies EV-to-equity conversion")
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Units / formula", "Interpretation"])
order = ("Bear", "Base", "Bull")
rows = [
    ("FY2026 revenue consensus", FY26_REVENUE, FY26_REVENUE, FY26_REVENUE, "$M", "Visible public estimate"),
    ("FY2027 revenue consensus", FY27_REVENUE, FY27_REVENUE, FY27_REVENUE, "$M", "Visible headline estimate"),
    ("Revenue CAGR (5Y)", *(SCENARIOS[k]["revenue_cagr"] for k in order), "%", "After FY2027"),
    ("Terminal revenue", *(SCENARIOS[k]["terminal_revenue"] for k in order), "$M", "FY2027 compounded five years"),
    ("Terminal adjusted EPS", *(SCENARIOS[k]["terminal_eps"] for k in order), "$ / share", "Normalized earnings after fuel, interest and tax"),
    ("Exit forward P/E", *(SCENARIOS[k]["pe"] for k in order), "x", "Cyclical travel range"),
    ("Target price", *(SCENARIOS[k]["target"] for k in order), "$ / share", "Terminal EPS × exit P/E"),
    ("Upside / downside", *(SCENARIOS[k]["upside"] for k in order), "%", "Versus $22.70"),
    ("Probability", *(SCENARIOS[k]["weight"] for k in order), "%", "25% / 50% / 25%"),
    ("Weighted value/share", *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in order), "$ / share", "Probability contribution"),
]
for r, row in enumerate(rows, 4):
    for c, value in enumerate(row, 1):
        cell = put(ws, r, c, value, c == 1)
        if c in (2, 3, 4) and row[0] in {"Revenue CAGR (5Y)", "Upside / downside", "Probability"}: cell.number_format = "0.0%"
        elif c in (2, 3, 4) and row[0] in {"Terminal adjusted EPS", "Target price", "Weighted value/share"}: cell.number_format = "$0.00"
put(ws, 15, 1, "Probability-weighted fair value", True, gold)
put(ws, 15, 2, weighted, True, gold).number_format = "$0.00"
put(ws, 16, 1, "Upside from current price", True, gold)
put(ws, 16, 2, weighted / PRICE - 1, True, gold).number_format = "0.0%"
put(ws, 18, 1, "FCF cross-check", True, blue)
put(ws, 18, 2, TTM_FCF, False, blue).number_format = "$#,##0"
put(ws, 18, 5, "TTM FCF ($M); P/FCF 9.72x and EV/FCF 17.19x")
put(ws, 19, 1, "Leverage warning", True, blue)
put(ws, 19, 2, NET_DEBT / TTM_FCF, False, blue).number_format = "0.00x"
put(ws, 19, 5, "Net debt / TTM FCF; reason forward P/E is primary")
finish(ws, [32, 18, 18, 18, 35, 72])

# Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Carnival — Actuals Source Audit", 5, "Financial statement amounts in USD millions")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/ccl"
audit = [
    ("Price", "$22.70", f"{sa}/", "2026-09-09", "Regular close"),
    ("Market cap / EV", "$31.09B / $55.02B", f"{sa}/statistics/", "2026-09-10", "EV-MC implies $23.93B net debt"),
    ("Shares outstanding", "1.37B", f"{sa}/statistics/", "2026-09-10", "+1.09% YoY"),
    ("TTM revenue", "$27.311B", f"{sa}/financials/", "2026-05-31", "+5.15%"),
    ("TTM gross profit", "$15.206B", f"{sa}/financials/", "2026-05-31", "55.68% margin"),
    ("TTM operating income", "$4.439B", f"{sa}/financials/", "2026-05-31", "16.25% margin"),
    ("TTM net income", "$3.069B", f"{sa}/financials/", "2026-05-31", "11.24% margin"),
    ("TTM OCF / capex / FCF", "$6.794B / $3.594B / $3.200B", f"{sa}/financials/cash-flow-statement/", "2026-05-31", "11.72% FCF margin"),
    ("TTM D&A / SBC", "$2.863B / $103M", f"{sa}/financials/cash-flow-statement/", "2026-05-31", "D&A is economically real fleet aging"),
    ("Cash / debt", "$2.243B / $26.170B", f"{sa}/financials/balance-sheet/", "2026-05-31", "Debt down from $35.881B FY2022"),
    ("Current liabilities", "$13.434B", f"{sa}/financials/balance-sheet/", "2026-05-31", "Includes customer deposits / unearned revenue economics"),
    ("Shareholders' equity", "$12.984B", f"{sa}/financials/balance-sheet/", "2026-05-31", "$9.45 book value/share"),
    ("FY2026 revenue / adjusted EPS", "$27.64B / $2.24", f"{sa}/forecast/", "2026-09-09", "25 analysts; EPS non-GAAP adjusted"),
    ("FY2027 revenue / adjusted EPS", "$28.62B / $2.63", f"{sa}/forecast/", "2026-09-09", "Headline public estimate"),
    ("Analyst targets", "$28.70 / $35.30 / $43.00", f"{sa}/forecast/", "2026-09-09", "Low / average / high; 30 analysts"),
    ("Beta", "2.31", f"{sa}/statistics/", "2026-09-10", "Five-year"),
    ("Next earnings", "2026-09-28 before open", f"{sa}/statistics/", "2026-09-10", "Estimated"),
    ("Dividend", "$0.60 / 2.64%", f"{sa}/statistics/", "2026-09-10", "20.65% payout ratio"),
]
for r, row in enumerate(audit, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [38, 28, 100, 18, 82])

# Questions
ws = wb.create_sheet("Questions")
title(ws, "Carnival — Open Diligence Questions", 4, "Items capable of changing conviction or valuation")
header(ws, 3, ["#", "Question", "Why it matters", "Best next evidence"])
questions = [
    (1, "How much of the 2026 earnings bridge depends on ticket price versus occupancy and onboard spend?", "Price-led growth is more durable than filling ships through discounting.", "Net yields, occupancy, close-in pricing and onboard revenue per passenger day."),
    (2, "How much fuel-price exposure is hedged for FY2027?", "Fuel exceeds $1B annually and recent price spikes drove the equity selloff.", "Fuel consumption, hedge book and per-ton sensitivity."),
    (3, "Can net debt fall below 3x EBITDA without sacrificing fleet quality?", "Deleveraging is the main path to lower equity risk and multiple expansion.", "Debt maturity schedule, repayments and adjusted EBITDA guidance."),
    (4, "What portion of capex is maintenance, newbuild commitments and destination investment?", "TTM FCF depends on whether $3.59B capex is a normalized requirement.", "Five-year capex schedule by category."),
    (5, "What refinancing volume is due in 2027-2030 and at what coupons?", "Lower debt does not guarantee lower interest if maturities reprice upward.", "Debt ladder, secured/unsecured mix and callable debt."),
    (6, "Is the 0.71% TTM effective tax rate durable?", "Cruise tax regimes are favorable but policy and geographic mix can change.", "Tax reconciliation and tonnage-tax exposure."),
    (7, "Why did current liabilities rise to $13.43B and what share is customer deposits?", "Deposits fund working capital but create refund and service obligations.", "Unearned-revenue bridge and cancellation terms."),
    (8, "Can gross margin remain above 55% through higher fuel and labor costs?", "Margin durability determines whether modest revenue growth reaches EPS.", "Per-passenger-day cost excluding fuel and fuel-adjusted margin."),
    (9, "What is the optimal dividend-versus-debt-repayment policy?", "The restored dividend competes with balance-sheet repair.", "Capital-allocation priorities and leverage targets."),
    (10, "Why did shares outstanding rise 1.09% YoY despite $381M of TTM repurchases?", "Dilution can offset buyback-funded per-share accretion.", "Dual-listed share reconciliation, SBC and convertible settlement."),
    (11, "How concentrated is profitability in Carnival Cruise Line versus premium brands?", "Brand mix affects pricing, cyclicality and capital needs.", "Brand-level revenue, EBITDA and ROIC."),
    (12, "What returns are expected from Celebration Key and other owned destinations?", "Destination control may lift onboard-like economics but adds capital risk.", "Incremental spend, utilization and project IRR."),
    (13, "Can the fleet meet the 2029 emissions-intensity target without material retrofit capex?", "Regulatory and fuel transitions can raise capital intensity.", "Retrofit schedule, LNG exposure and compliance cost."),
    (14, "How sensitive are bookings to a U.S. consumer slowdown?", "Cruises are discretionary and deposits can reverse.", "Booking curve, cancellation rate and credit-card spending cohorts."),
    (15, "What will September 28 earnings prove?", "The stock sits at a 52-week low ahead of an immediate information event.", "FY2027 booking commentary, fuel bridge, net yields and debt paydown."),
]
for r, row in enumerate(questions, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [7, 86, 76, 76])

# Sources
ws = wb.create_sheet("Sources")
title(ws, "Carnival — Sources", 4, "Public sources accessed September 10, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Identity, price, profile, earnings date and news"),
    (2, "StockAnalysis financial overview", f"{sa}/financials/", "History, segments, cash/debt and margins"),
    (3, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, equity, liabilities and fleet assets"),
    (4, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, debt repayment and dividends"),
    (5, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation, shares, leverage, beta and returns"),
    (6, "StockAnalysis forecast", f"{sa}/forecast/", "Consensus, ratings, targets and FY2026/FY2027 headlines"),
    (7, "Carnival investor relations", "https://www.carnivalcorp.com/investors", "Official results, presentations and filings"),
    (8, "Carnival sustainability", "https://www.carnivalsustainability.com/", "Emissions and fleet-transition context"),
    (9, "U.S. Treasury yield curve", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates", "Risk-free-rate reference"),
]
for r, row in enumerate(sources, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [7, 42, 112, 74])

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, (int, float)) and cell.number_format == "General":
                cell.number_format = "#,##0.00"
wb.save(OUT)

check = load_workbook(OUT, data_only=False)
assert check.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert all(check[name].max_row >= 10 for name in check.sheetnames)
print(f"WACC: {wacc:.2%}")
print("Targets:", ", ".join(f"{name} ${case['target']:.2f}" for name, case in SCENARIOS.items()))
print(f"Weighted FV: ${weighted:.2f} ({weighted / PRICE - 1:+.1%})")
print(f"Wrote {OUT}")
