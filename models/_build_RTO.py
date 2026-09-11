#!/usr/bin/env python3
"""Build Rentokil Initial's six-sheet valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).with_name("2026-09-11 Rentokil Initial Model.xlsx")
PRICE, SHARES = 22.42, 2526.0
MARKET_CAP, ENTERPRISE_VALUE = 11270.0, 15010.0
NET_DEBT = ENTERPRISE_VALUE - MARKET_CAP
TTM_REVENUE, TTM_FCF, TTM_EBITDA = 7133.0, 769.0, 1250.0
FY26_REVENUE, FY26_EPS, FY27_REVENUE, FY27_EPS = 7210.0, 1.487, 7490.0, 1.645

SCENARIOS = {
    "Bear": {"cagr": .010, "terminal_eps": 1.60, "pe": 11.0, "weight": .25},
    "Base": {"cagr": .042, "terminal_eps": 2.15, "pe": 14.0, "weight": .50},
    "Bull": {"cagr": .060, "terminal_eps": 2.55, "pe": 15.5, "weight": .25},
}
for case in SCENARIOS.values():
    case["terminal_revenue"] = FY27_REVENUE * (1 + case["cagr"]) ** 5
    case["target"] = case["terminal_eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1
weighted = sum(c["target"] * c["weight"] for c in SCENARIOS.values())
assert SCENARIOS["Bear"]["target"] < PRICE
assert abs(SCENARIOS["Base"]["target"] / 32.03 - 1) < .20

rf, erp, beta = .043, .05, .41
ke = rf + beta * erp
debt, kd, tax = 6140.0, 251.0 / 6140.0, .2632
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
    for c, value in enumerate(values, 1): put(ws, r, c, value, True, navy, white)

def finish(ws, widths):
    for c, width in enumerate(widths, 1): ws.column_dimensions[get_column_letter(c)].width = width
    ws.freeze_panes = "A4"
    ws.sheet_view.showGridLines = False
    ws.auto_filter.ref = ws.dimensions

ws = wb.active
ws.title = "Valuation"
title(ws, "Rentokil Initial plc (RTO) — Valuation", 4, "Quote: September 10, 2026 close | Model date: September 11, 2026 | USD")
header(ws, 3, ["Field", "Value", "Comment"])
facts = [
    ("Company", "Rentokil Initial plc", "Route-based pest control and hygiene services"),
    ("Ticker", "NYSE: RTO", "ADR quotation; financial data standardized to USD"),
    ("Price", PRICE, "September 10 close"), ("Shares outstanding (M)", SHARES, "Current filing count"),
    ("Market capitalization ($M)", MARKET_CAP, "StockAnalysis"), ("Enterprise value ($M)", ENTERPRISE_VALUE, "StockAnalysis"),
    ("Net debt proxy ($M)", NET_DEBT, "EV less market capitalization"),
    ("Primary lens", "Forward P/E", "Debt/FCF is 8.0x; P/E avoids EV-to-equity amplification"),
    ("Stance", "Watch / self-help setup", "Attractive valuation offset by North America execution and leverage"),
]
for r, row in enumerate(facts, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
header(ws, 14, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E", 23.59, "Provider GAAP ADR basis"), ("Forward P/E", 15.08, "Implied adjusted EPS about $1.49"),
    ("P/S", 1.58, "Equity value / TTM revenue"), ("P/FCF", 14.66, "6.82% FCF yield"),
    ("EV/FCF", 19.52, "Debt-adjusted cross-check"), ("EV/Sales", 2.10, "Route density and recurring service value"),
    ("EV/EBITDA", 11.99, "Enterprise cross-check"), ("Debt/EBITDA", 4.35, "Elevated after Terminix"),
    ("Interest coverage", 3.64, "Adequate, not generous"), ("Analyst average target", 32.03, "Low $26.70, high $35.00"),
]
for r, row in enumerate(metrics, 15):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [34, 28, 100, 14])

ws = wb.create_sheet("WACC")
title(ws, "Rentokil Initial — Weighted Average Cost of Capital", 4, "CAPM using market-value weights")
header(ws, 3, ["Component", "Value", "Source / formula"])
rows = [("Risk-free rate", rf, "Normalized U.S. 10-year reference"), ("Equity risk premium", erp, "Model assumption"),
        ("Levered beta", beta, "StockAnalysis five-year beta"), ("Cost of equity", ke, "Rf + beta × ERP"),
        ("Pre-tax cost of debt", kd, "$251M cash interest / $6.14B debt"), ("Tax rate", tax, "TTM effective rate"),
        ("Market cap ($M)", MARKET_CAP, "USD millions"), ("Debt ($M)", debt, "June 2026"),
        ("Equity weight", ew, "E/(D+E)"), ("Debt weight", dw, "D/(D+E)"), ("WACC", wacc, "E/V×Ke + D/V×Kd×(1−T)")]
for r, row in enumerate(rows, 4):
    for c, value in enumerate(row, 1):
        cell = put(ws, r, c, value, c == 1 or row[0] == "WACC", gold if row[0] == "WACC" else None)
        if c == 2 and row[0] not in {"Levered beta", "Market cap ($M)", "Debt ($M)"}: cell.number_format = "0.00%"
finish(ws, [34, 24, 100, 14])

ws = wb.create_sheet("Scenarios")
title(ws, "Rentokil Initial — Five-Year Forward P/E Scenarios", 6, "Forward P/E primary; EV/EBITDA and FCF are cross-checks")
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Units / formula", "Interpretation"])
order = ("Bear", "Base", "Bull")
rows = [
    ("FY2026 revenue consensus", FY26_REVENUE, FY26_REVENUE, FY26_REVENUE, "$M", "Visible public estimate"),
    ("FY2027 revenue anchor", FY27_REVENUE, FY27_REVENUE, FY27_REVENUE, "$M", "Visible headline estimate"),
    ("Revenue CAGR (5Y)", *(SCENARIOS[k]["cagr"] for k in order), "%", "After FY2027"),
    ("Terminal revenue", *(SCENARIOS[k]["terminal_revenue"] for k in order), "$M", "FY2027 compounded five years"),
    ("Terminal adjusted EPS", *(SCENARIOS[k]["terminal_eps"] for k in order), "$ / ADR", "Execution and interest assumptions"),
    ("Exit forward P/E", *(SCENARIOS[k]["pe"] for k in order), "x", "Business-services range"),
    ("Target price", *(SCENARIOS[k]["target"] for k in order), "$ / ADR", "EPS × P/E"),
    ("Upside / downside", *(SCENARIOS[k]["upside"] for k in order), "%", "Versus $22.42"),
    ("Probability", *(SCENARIOS[k]["weight"] for k in order), "%", "25% / 50% / 25%"),
    ("Weighted value/share", *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in order), "$ / ADR", "Probability contribution"),
]
for r, row in enumerate(rows, 4):
    for c, value in enumerate(row, 1):
        cell = put(ws, r, c, value, c == 1)
        if c in (2, 3, 4) and row[0] in {"Revenue CAGR (5Y)", "Upside / downside", "Probability"}: cell.number_format = "0.0%"
        elif c in (2, 3, 4) and row[0] in {"Terminal adjusted EPS", "Target price", "Weighted value/share"}: cell.number_format = "$0.00"
put(ws, 15, 1, "Probability-weighted fair value", True, gold); put(ws, 15, 2, weighted, True, gold).number_format = "$0.00"
put(ws, 16, 1, "Upside from current price", True, gold); put(ws, 16, 2, weighted / PRICE - 1, True, gold).number_format = "0.0%"
put(ws, 18, 1, "Leverage warning", True, blue); put(ws, 18, 2, NET_DEBT / TTM_FCF, False, blue).number_format = "0.00x"
put(ws, 18, 5, "Net debt / TTM FCF; reason forward P/E is primary")
finish(ws, [34, 18, 18, 18, 35, 76])

ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Rentokil Initial — Actuals Source Audit", 5, "Financial statement amounts in USD millions")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/rto"
audit = [
    ("Price", "$22.42", f"{sa}/", "2026-09-10", "Regular close"), ("Market cap / EV", "$11.27B / $15.01B", f"{sa}/statistics/", "2026-09-10", "EV-MC implies $3.74B net debt"),
    ("Shares outstanding", "2.53B", f"{sa}/statistics/", "2026-09-10", "+0.34% YoY"), ("TTM revenue", "$7.133B", f"{sa}/financials/", "2026-06-30", "+3.26%"),
    ("TTM gross profit", "$999M", f"{sa}/financials/", "2026-06-30", "Provider standardized gross margin is not comparable with pre-2023 presentation"),
    ("TTM operating income", "$920M", f"{sa}/financials/", "2026-06-30", "12.90% margin"), ("TTM net income", "$478M", f"{sa}/financials/", "2026-06-30", "6.70% margin"),
    ("TTM OCF / capex / FCF", "$930M / $161M / $769M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "10.78% FCF margin"),
    ("Cash / debt", "$2.471B / $6.140B", f"{sa}/financials/balance-sheet/", "2026-06-30", "Net debt $3.669B"),
    ("Goodwill / intangibles", "$6.584B / $2.302B at FY2025", f"{sa}/financials/balance-sheet/", "2025-12-31", "Terminix acquisition makes impairment testing important"),
    ("FY2026 revenue / adjusted EPS", "$7.21B / $0.28 local-share basis", f"{sa}/forecast/", "2026-08-04", "18 analysts; EPS provider-labelled non-GAAP"),
    ("ADR implied forward EPS", "$1.49", f"{sa}/statistics/", "2026-09-10", "$22.42 / 15.08x; reconciles ADR ratio issue"),
    ("Analyst targets", "$26.70 / $32.03 / $35.00", f"{sa}/forecast/", "2026-07-31", "Low / average / high; four ADR analysts"),
    ("Beta", "0.41", f"{sa}/statistics/", "2026-09-10", "Five-year"), ("Last earnings", "2026-07-30", f"{sa}/statistics/", "2026-09-10", "H1 2026 already released"),
]
for r, row in enumerate(audit, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [38, 32, 100, 18, 88])

ws = wb.create_sheet("Questions")
title(ws, "Rentokil Initial — Open Diligence Questions", 4, "Items capable of changing conviction or valuation")
header(ws, 3, ["#", "Question", "Why it matters", "Best next evidence"])
questions = [
    (1, "Can North America commercial pest return to growth while residential retention improves?", "Terminix execution is the central earnings variable.", "Organic growth by channel, retention and technician productivity."),
    (2, "How much of H1 improvement came from pricing rather than volume?", "Price-only growth has a ceiling if service quality remains uneven.", "Price/volume bridge and customer additions."),
    (3, "What portion of Terminix integration savings is realized versus still forecast?", "Unrealized savings underpin margin and EPS expectations.", "Run-rate savings, one-time cost and headcount bridge."),
    (4, "Why did FY2025 gross-profit presentation differ sharply from pre-2023 periods?", "Provider classification changes impair historical margin comparison.", "Reported cost-of-services reconciliation."),
    (5, "Could $8.9B of goodwill and intangibles be impaired?", "The acquisition premium exceeds common equity and tangible book is negative.", "Cash-generating-unit headroom and discount-rate sensitivity."),
    (6, "Can debt/EBITDA fall below 3.5x without sacrificing route investment?", "Current 4.35x debt/EBITDA limits flexibility.", "Covenants, maturities and deleveraging target."),
    (7, "Why is current debt split unusually high at June 2026?", "Near-term refinancing can offset operating progress.", "Debt maturity schedule and committed liquidity."),
    (8, "How sustainable is the $394M TTM divestiture inflow?", "Divestiture cash is not recurring FCF.", "Portfolio simplification pipeline and proceeds use."),
    (9, "What is normalized maintenance capex for route density and digital systems?", "FCF depends on whether $161M TTM capex is a trough.", "Capex by maintenance, growth and integration."),
    (10, "Will shares outstanding remain flat?", "Small dilution can offset modest per-share growth.", "SBC, ADR ratio and buyback policy."),
    (11, "How concentrated are customers and national accounts?", "Large commercial contract repricing can move growth and margins.", "Top-customer concentration and renewal schedule."),
    (12, "Can hygiene margins recover without acquisition-led growth?", "Hygiene diversifies pest control but may have weaker post-pandemic demand.", "Segment organic growth and margin disclosure."),
    (13, "What is the next earnings date and exact FY2026 guidance?", "July 30 results are already public; the next event is the forward catalyst.", "Company IR calendar and H1 guidance bridge."),
    (14, "How does FX translation affect ADR earnings and target prices?", "The business reports in sterling while this model is in USD.", "Constant-currency guidance and ADR ratio reconciliation."),
    (15, "Can customer-service investment improve retention without depressing near-term margin?", "The new operating plan requires spending before benefits.", "Service levels, complaints, callbacks and labor cost."),
]
for r, row in enumerate(questions, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [7, 88, 78, 78])

ws = wb.create_sheet("Sources")
title(ws, "Rentokil Initial — Sources", 4, "Public sources accessed September 11, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [(1, "StockAnalysis overview", f"{sa}/", "Identity, price, profile and news"),
           (2, "StockAnalysis financial overview", f"{sa}/financials/", "History, segments and margins"),
           (3, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, goodwill and equity"),
           (4, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, acquisitions and divestitures"),
           (5, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation, shares, leverage, beta and returns"),
           (6, "StockAnalysis forecast", f"{sa}/forecast/", "Consensus, ratings, targets and FY2026/FY2027 headlines"),
           (7, "Rentokil investor relations", "https://www.rentokil-initial.com/investors/", "Official H1 results and strategy"),
           (8, "U.S. Treasury yield curve", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates", "Risk-free-rate reference")]
for r, row in enumerate(sources, 4):
    for c, value in enumerate(row, 1): put(ws, r, c, value, c == 1)
finish(ws, [7, 44, 112, 80])

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, (int, float)) and cell.number_format == "General": cell.number_format = "#,##0.00"
wb.save(OUT)
check = load_workbook(OUT, data_only=False)
assert check.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert all(check[name].max_row >= 10 for name in check.sheetnames)
print(f"WACC: {wacc:.2%}")
print("Targets:", ", ".join(f"{name} ${case['target']:.2f}" for name, case in SCENARIOS.items()))
print(f"Weighted FV: ${weighted:.2f} ({weighted / PRICE - 1:+.1%})")
print(f"Wrote {OUT}")
