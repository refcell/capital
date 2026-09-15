#!/usr/bin/env python3
"""Build Cenovus Energy's six-sheet valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).with_name("2026-09-15 Cenovus Energy Model.xlsx")
PRICE = 33.27
SHARES = 1_844.0  # millions
MARKET_CAP = 61_319.0  # USD millions
ENTERPRISE_VALUE = 67_411.0
NET_DEBT = ENTERPRISE_VALUE - MARKET_CAP
TTM_REVENUE = 37_930.0
TTM_EBITDA = 10_100.0
TTM_FCF = 5_380.0
ANALYST_TARGET = 37.01

SCENARIOS = {
    "Bear": {"fcf": 4_200.0, "multiple": 8.0, "net_debt": 8_000.0, "shares": 1_850.0, "weight": 0.25},
    "Base": {"fcf": 6_700.0, "multiple": 10.0, "net_debt": 4_000.0, "shares": 1_750.0, "weight": 0.50},
    "Bull": {"fcf": 8_500.0, "multiple": 11.5, "net_debt": 0.0, "shares": 1_700.0, "weight": 0.25},
}
for case in SCENARIOS.values():
    case["ev"] = case["fcf"] * case["multiple"]
    case["equity"] = case["ev"] - case["net_debt"]
    case["target"] = case["equity"] / case["shares"]
    case["upside"] = case["target"] / PRICE - 1
weighted = sum(case["target"] * case["weight"] for case in SCENARIOS.values())
assert SCENARIOS["Bear"]["target"] < PRICE
assert abs(SCENARIOS["Base"]["target"] / ANALYST_TARGET - 1) < 0.20

rf, erp, beta = 0.0496, 0.05, 0.50
ke = rf + beta * erp
debt, kd, tax = 8_190.0, 0.0465, 0.2031
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
title(ws, "Cenovus Energy Inc. (CVE) — Valuation", 4,
      "Quote: September 14, 2026 close | Model date: September 15, 2026 | USD unless noted")
header(ws, 3, ["Field", "Value", "Comment"])
facts = [
    ("Company", "Cenovus Energy Inc.", "Integrated Canadian oil producer and refiner"),
    ("Ticker", "NYSE: CVE", "U.S.-listed common shares"),
    ("Price", PRICE, "September 14 regular close"),
    ("Shares outstanding (M)", SHARES, "June 30 filing count"),
    ("Market capitalization ($M)", MARKET_CAP, "StockAnalysis, USD"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "StockAnalysis, USD"),
    ("Net debt proxy ($M)", NET_DEBT, "EV less market capitalization"),
    ("Primary lens", "Normalized FCF / EV", "Commodity-cycle earnings require normalized cash flow"),
    ("Stance", "Watch", "Execution is strong, but the price already discounts a favorable cycle"),
]
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
header(ws, 14, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E", 13.05, "GAAP earnings are commodity-price sensitive"),
    ("Forward P/E", 13.17, "Provider ratio; FY2026 forecast table is in CAD"),
    ("P/S", 1.62, "Elevated versus recent history after the share-price rally"),
    ("P/FCF", 11.41, "8.77% trailing FCF yield"),
    ("EV/FCF", 12.54, "Current cash flow includes a favorable commodity/refining period"),
    ("EV/Sales", 1.78, "Integrated upstream/downstream revenue"),
    ("EV/EBITDA", 6.68, "Above FY2022-FY2025 range of 4.5x-5.5x"),
    ("Net debt/FCF", 1.13, "Low enough for FCF valuation to remain usable"),
    ("Interest coverage", 17.99, "Strong debt-service capacity"),
    ("Analyst average target", ANALYST_TARGET, "Low $34.02; median $37.01; high $40"),
]
for row, values in enumerate(metrics, 15):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [34, 28, 100, 14])

ws = wb.create_sheet("WACC")
title(ws, "Cenovus Energy — Weighted Average Cost of Capital", 4,
      "CAPM using market-value weights and September 2026 USD inputs")
header(ws, 3, ["Component", "Value", "Source / formula"])
rows = [
    ("Risk-free rate", rf, "FRED DGS10, September 11, 2026"),
    ("Equity risk premium", erp, "Model assumption"),
    ("Levered beta", beta, "StockAnalysis five-year beta"),
    ("Cost of equity", ke, "Rf + beta × ERP"),
    ("Pre-tax cost of debt", kd, "Normalized estimate; current debt is predominantly fixed-rate"),
    ("Tax rate", tax, "TTM effective tax rate"),
    ("Market cap ($M)", MARKET_CAP, "September 14, 2026"),
    ("Debt ($M)", debt, "StockAnalysis USD translation"),
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
title(ws, "Cenovus Energy — Five-Year Normalized FCF Scenarios", 6,
      "USD millions; normalized FCF primary, EV/EBITDA and forward P/E are cross-checks")
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Units / formula", "Interpretation"])
order = ("Bear", "Base", "Bull")
rows = [
    ("Normalized terminal FCF", *(SCENARIOS[k]["fcf"] for k in order), "$M", "Cycle-normalized owner cash flow"),
    ("Exit EV/FCF", *(SCENARIOS[k]["multiple"] for k in order), "x", "Integrated-energy valuation range"),
    ("Implied enterprise value", *(SCENARIOS[k]["ev"] for k in order), "$M", "FCF × exit multiple"),
    ("Less terminal net debt", *(SCENARIOS[k]["net_debt"] for k in order), "$M", "Debt increases in bear; falls toward target in base/bull"),
    ("Implied equity value", *(SCENARIOS[k]["equity"] for k in order), "$M", "EV less net debt"),
    ("Terminal shares", *(SCENARIOS[k]["shares"] for k in order), "M", "Buybacks depend on excess free funds"),
    ("Target price", *(SCENARIOS[k]["target"] for k in order), "$ / share", "Equity value / shares"),
    ("Upside / downside", *(SCENARIOS[k]["upside"] for k in order), "%", "Versus $33.27"),
    ("Probability", *(SCENARIOS[k]["weight"] for k in order), "%", "25% / 50% / 25%"),
    ("Weighted value/share", *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in order), "$ / share", "Probability contribution"),
]
for row, values in enumerate(rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, col == 1)
        if col in (2, 3, 4) and values[0] in {"Upside / downside", "Probability"}:
            cell.number_format = "0.0%"
        elif col in (2, 3, 4) and values[0] in {"Target price", "Weighted value/share"}:
            cell.number_format = "$0.00"
put(ws, 15, 1, "Probability-weighted fair value", True, gold)
put(ws, 15, 2, weighted, True, gold).number_format = "$0.00"
put(ws, 16, 1, "Upside from current price", True, gold)
put(ws, 16, 2, weighted / PRICE - 1, True, gold).number_format = "0.0%"
put(ws, 18, 1, "Cycle warning", True, blue)
put(ws, 18, 2, "TTM FCF is not a floor", False, blue)
put(ws, 18, 5, "Oil prices, heavy differentials, refinery cracks, turnarounds, and taxes can move FCF sharply")
finish(ws, [34, 18, 18, 18, 35, 80])

ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Cenovus Energy — Actuals Source Audit", 5,
      "Operating statement amounts are CAD unless explicitly labeled USD")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/cve"
audit = [
    ("Price", "$33.27 USD", f"{sa}/", "2026-09-14", "Regular close"),
    ("Market cap / EV", "$61.32B / $67.41B USD", f"{sa}/statistics/", "2026-09-14", "EV-MC implies $6.09B net debt"),
    ("Shares outstanding", "1.84B", f"{sa}/statistics/", "2026-09-14", "+0.20% YoY; filing count 1.844B"),
    ("TTM revenue", "C$53.861B / US$37.93B", f"{sa}/financials/", "2026-06-30", "+3.08%"),
    ("TTM gross profit", "C$16.083B", f"{sa}/financials/", "2026-06-30", "29.86% margin"),
    ("TTM operating income", "C$8.925B", f"{sa}/financials/", "2026-06-30", "16.57% margin"),
    ("TTM net income", "C$6.654B / US$4.69B", f"{sa}/financials/", "2026-06-30", "12.35% margin; GAAP"),
    ("TTM OCF / capex / FCF", "C$12.356B / C$4.884B / C$7.472B", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "13.87% FCF margin"),
    ("Cash / debt", "C$3.170B / C$11.631B", f"{sa}/financials/balance-sheet/", "2026-06-30", "Net debt C$8.461B"),
    ("PP&E / goodwill", "C$47.621B / C$2.912B", f"{sa}/financials/balance-sheet/", "2026-06-30", "Asset-heavy integrated model"),
    ("FY2026 revenue / adjusted EPS", "C$60.85B / C$4.48", f"{sa}/forecast/", "2026-09-08", "Revenue 2 analysts; EPS provider-labelled non-GAAP"),
    ("FY2027 headline revenue / EPS", "C$52.92B / C$3.66", f"{sa}/forecast/", "2026-09-08", "Detailed later rows gated"),
    ("Analyst targets", "$34.02 / $37.01 / $40 USD", f"{sa}/forecast/", "2026-09-08", "Low / average / high; 18 analysts"),
    ("Beta", "0.50", f"{sa}/statistics/", "2026-09-14", "Five-year"),
    ("Earnings date", "2026-10-30 BMO", f"{sa}/statistics/", "2026-09-14", "Estimated"),
    ("Q2 production", "970.4 mboe/d", "https://www.fool.com/earnings/call-transcripts/2026/08/07/cenovus-cve-q2-2026-earnings-call-transcript/", "2026-08-07", "+27% YoY; company record"),
    ("Q2 net debt", "C$5.4B", "https://www.fool.com/earnings/call-transcripts/2026/08/07/cenovus-cve-q2-2026-earnings-call-transcript/", "2026-08-07", "Down C$2.7B QoQ; management definition"),
    ("2026 capex guidance", "C$5.0B-C$5.3B", "https://www.fool.com/earnings/call-transcripts/2026/08/07/cenovus-cve-q2-2026-earnings-call-transcript/", "2026-08-07", "Unchanged"),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [38, 34, 100, 18, 88])

ws = wb.create_sheet("Questions")
title(ws, "Cenovus Energy — Open Diligence Questions", 4,
      "Items capable of changing conviction or valuation")
header(ws, 3, ["#", "Question", "Why it matters", "Best next evidence"])
questions = [
    (1, "How much of Q2's record funds flow came from prices versus sustainable operating gains?", "The model must normalize commodity and crack-spread benefits.", "Price-volume-cost bridge and sensitivity table."),
    (2, "Can oil sands production remain near 1 million boe/d without higher sustaining capital?", "Volume growth only creates value if decline replacement and steam costs stay controlled.", "Three-year sustaining-capital and decline-rate disclosure."),
    (3, "Will Christina Lake North reach 150 mboe/d by 2028 after the MEG acquisition?", "The acquisition thesis depends on low-risk production and synergies.", "Pad-level ramp, steam capacity, and synergy scorecard."),
    (4, "What explains the gap between C$7.68B of gross balance-sheet net debt and C$5.4B management net debt?", "Debt definitions change shareholder-return thresholds.", "Debt, leases, cash, and working-capital reconciliation."),
    (5, "Can U.S. refining sustain 90%+ utilization through turnaround seasons?", "Downstream integration offsets heavy-oil differentials only when assets run reliably.", "Quarterly utilization and unplanned outage days."),
    (6, "How much of downstream margin came from the C$144M inventory holding gain?", "Inventory gains are not recurring operating earnings.", "Adjusted refining margin bridge."),
    (7, "What is normalized U.S. refining market capture after temporary feedstock dislocations?", "Capture was only 67% despite favorable headline cracks.", "Benchmark-to-realized margin reconciliation."),
    (8, "Will West White Rose reach first oil on schedule and budget?", "Offshore projects have high execution and capital risk.", "Commissioning milestones and remaining spend."),
    (9, "What returns does the Spruce Lake solvent-aided project earn at mid-cycle WCS prices?", "The project promises 40%-50% production uplift and 30% lower SOR.", "Sanction economics and realized solvent recovery."),
    (10, "How durable are lower oil-sands nonfuel operating costs?", "C$8.28/bbl supports the margin thesis but can reverse with maintenance and inflation.", "Cost bridge by asset."),
    (11, "Will the long-term C$4B net-debt target be reached before buybacks accelerate?", "A 75% excess-free-funds payout leaves less room for balance-sheet repair.", "Capital-allocation waterfall and debt maturity plan."),
    (12, "Why did total debt rise in 2025 despite strong cash generation?", "The MEG transaction and working capital must be separated from structural leverage.", "Acquisition financing and repayment schedule."),
    (13, "Can buybacks outpace acquisition-related issuance on a full-year basis?", "Shares were +0.20% YoY despite C$3.2B TTM repurchases.", "Average diluted share reconciliation."),
    (14, "What tax rate should investors normalize after C$2.3B-C$2.6B cash-tax guidance?", "Timing and commodity mix can create large FCF swings.", "Current/deferred tax bridge and 2027 payment schedule."),
    (15, "How would an uncompetitive Canadian carbon tax change project economics?", "Policy can raise the cost of long-duration oil-sands barrels.", "Asset-level carbon intensity and breakeven sensitivity."),
    (16, "What does October 30 need to show?", "The next report must confirm production reliability, refinery capture, and deleveraging.", "Q3 production, utilization, net debt, and guidance."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [7, 88, 78, 78])

ws = wb.create_sheet("Sources")
title(ws, "Cenovus Energy — Sources", 4,
      "Public sources accessed September 15, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Identity, price, profile and news"),
    (2, "StockAnalysis financial overview", f"{sa}/financials/", "History, segments and margins"),
    (3, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, debt, assets and equity"),
    (4, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, acquisitions and buybacks"),
    (5, "StockAnalysis ratios", f"{sa}/financials/ratios/", "Historical valuation and returns"),
    (6, "StockAnalysis statistics", f"{sa}/statistics/", "Valuation, shares, leverage, beta and dates"),
    (7, "StockAnalysis forecast", f"{sa}/forecast/", "Consensus, ratings, targets and FY2026/FY2027 headlines"),
    (8, "StockAnalysis company profile", f"{sa}/company/", "Business description, management and filing links"),
    (9, "Cenovus Q2 2026 call transcript", "https://www.fool.com/earnings/call-transcripts/2026/08/07/cenovus-cve-q2-2026-earnings-call-transcript/", "Operations, acquisition integration, guidance and capital allocation"),
    (10, "FRED DGS10", "https://fred.stlouisfed.org/series/DGS10", "Risk-free rate"),
]
for row, values in enumerate(sources, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, col == 1)
finish(ws, [7, 42, 110, 80])

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected
assert all(check[name].max_row >= 13 for name in expected)
print(f"Built {OUT}")
print(f"WACC: {wacc:.2%}")
print("Targets: " + ", ".join(f"{k} ${v['target']:.2f}" for k, v in SCENARIOS.items()))
print(f"Probability-weighted fair value: ${weighted:.2f} ({weighted / PRICE - 1:.1%})")
