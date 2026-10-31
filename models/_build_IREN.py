#!/usr/bin/env python3
"""Build the IREN Limited six-sheet valuation workbook."""
from math import isclose
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


OUT = Path(__file__).with_name("2026-10-31 IREN Model.xlsx")
PRICE = 23.95  # October 30, 2026 close
SHARES = 394.06  # ordinary shares outstanding, millions (10-K cover count, Aug 14, 2026)
MARKET_CAP = PRICE * SHARES  # millions
CASH = 5895.6  # unrestricted cash and equivalents, June 30, 2026
RESTRICTED_CASH = 1724.0  # $1,670.3M current + $53.7M non-current; tied to Microsoft GPU financing
TOTAL_DEBT = 7840.0  # convertible notes, drawn GPU financing and finance leases (StockAnalysis)
FINANCE_LEASES = 243.8
DRAWN_FACILITY = 938.0  # Microsoft GPU financing drawn in Q4 FY26
DEFERRED_REVENUE = 1842.6  # customer prepayments, current + non-current
ENTERPRISE_VALUE = MARKET_CAP + TOTAL_DEBT - CASH
EV_INCL_RESTRICTED = ENTERPRISE_VALUE - RESTRICTED_CASH
NET_DEBT = TOTAL_DEBT - CASH
TTM_REVENUE = 707.0
TTM_AI_REVENUE = 128.8
TTM_ADJ_EBITDA = 245.7
TTM_OCF = 2100.4
TTM_CAPEX = 4333.1
TTM_FCF = TTM_OCF - TTM_CAPEX
TTM_SBC = 205.0
BOOK_EQUITY = 4185.6
FY27_REVENUE = 2810.0  # StockAnalysis consensus, 17 analysts
FY28_REVENUE = 7410.0  # StockAnalysis consensus
FY27_EPS = -3.42  # consensus non-GAAP EPS
DEC26_ARR = 4000.0  # contracted ARR targeted operational by Dec 31, 2026
ANALYST_AVG_PT = 75.42
HORIZON = 4.67  # Oct 30, 2026 to June 30, 2031 (FY2031 year end), years

# FY2031 adjusted EBITDA x exit EV/EBITDA, less projected FY2031 net debt, over projected FY2031 shares.
# FCF multiples are not usable: FY26 FCF was -$2.23B and FY27 capex is guided at $25-30B.
SCENARIOS = {
    "Bear": {"revenue": 10500.0, "margin": 0.50, "multiple": 6.0, "net_debt": 22000.0, "shares": 650.0, "discount": 0.20, "weight": 0.30},
    "Base": {"revenue": 16000.0, "margin": 0.60, "multiple": 7.5, "net_debt": 38000.0, "shares": 580.0, "discount": 0.18, "weight": 0.50},
    "Bull": {"revenue": 24000.0, "margin": 0.65, "multiple": 9.0, "net_debt": 50000.0, "shares": 520.0, "discount": 0.16, "weight": 0.20},
}
for case in SCENARIOS.values():
    case["cagr"] = (case["revenue"] / FY27_REVENUE) ** (1 / 4) - 1  # FY2027 consensus to FY2031
    case["ebitda"] = case["revenue"] * case["margin"]
    case["ev"] = case["ebitda"] * case["multiple"]
    case["equity"] = case["ev"] - case["net_debt"]
    case["terminal_price"] = case["equity"] / case["shares"]
    case["target"] = case["terminal_price"] / (1 + case["discount"]) ** HORIZON
    case["dilution"] = case["shares"] / SHARES - 1
weighted_value = sum(case["target"] * case["weight"] for case in SCENARIOS.values())

assert SCENARIOS["Bear"]["target"] < PRICE * 0.9
assert SCENARIOS["Bear"]["target"] > PRICE * 0.2
assert all(case["equity"] > 0 for case in SCENARIOS.values())

rf = 4.98
erp = 5.00
raw_beta = 4.27
beta = 0.67 * raw_beta + 0.33  # Blume-adjusted
cost_equity = rf + beta * erp
pretax_debt_cost = 8.0
tax_rate = 25.0
equity_weight = MARKET_CAP / (MARKET_CAP + TOTAL_DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * cost_equity + debt_weight * pretax_debt_cost * (1 - tax_rate / 100)

wb = Workbook()
navy, blue, gold, gray, white = "17365D", "D9EAF7", "D8B34B", "E7E6E6", "FFFFFF"
thin = Side(style="thin", color="A6A6A6")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, row, col, value, *, bold=False, fill=None, color="000000", size=10, wrap=True):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Aptos", size=size, bold=bold, color=color)
    cell.fill = PatternFill("solid", fgColor=fill) if fill else PatternFill(fill_type=None)
    cell.border = border
    cell.alignment = Alignment(vertical="top", wrap_text=wrap)
    return cell


def title(ws, text, end_col=5, subtitle=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    put(ws, 1, 1, text, bold=True, fill=navy, color=white, size=15)
    ws.row_dimensions[1].height = 28
    if subtitle:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=end_col)
        put(ws, 2, 1, subtitle, bold=True, fill=blue)


def header(ws, row, values):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=True, fill=navy, color=white)


def widths(ws, values):
    for col, width in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.freeze_panes = "A3"


# 1. Valuation
ws = wb.active
ws.title = "Valuation"
title(ws, "IREN Limited (IREN) — Valuation", 4, "Quote date: October 30, 2026 close | Model date: October 31, 2026 | Fiscal year ends June 30")
facts = [
    ("Company", "IREN Limited (formerly Iris Energy)", "Vertically integrated AI cloud: owned land, grid connections, data centers, GPUs and Mirantis software; Bitcoin mining being decommissioned by Dec 2026"),
    ("Ticker", "NASDAQ: IREN", "Sydney-incorporated, U.S.-listed; reports in USD; StockAnalysis classifies as Financials / Capital Markets (legacy mining SIC 6199)"),
    ("Price", PRICE, "StockAnalysis close October 30, 2026 (-8.76% on the day); 52-week range $23.06-$76.87"),
    ("Ordinary shares outstanding (M)", SHARES, "StockAnalysis / 10-K cover; +41.6% YoY from ATM sales, convert inducements and Mirantis stock consideration"),
    ("Market capitalization ($M)", MARKET_CAP, "Price × shares; StockAnalysis shows $9.44B"),
    ("Total debt ($M)", TOTAL_DEBT, "Convertible notes (2029-2033), $938M drawn Microsoft GPU financing, $244M finance leases"),
    ("Unrestricted cash ($M)", CASH, "June 30, 2026; excludes $1,724M restricted cash pledged to Microsoft GPU financing"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "Market cap + debt - unrestricted cash; matches StockAnalysis $11.38B"),
    ("EV incl. restricted cash ($M)", EV_INCL_RESTRICTED, "If restricted cash is netted against the GPU financing it secures"),
    ("Customer prepayments ($M)", DEFERRED_REVENUE, "Deferred revenue; an operating liability funded by customers, not counted as debt"),
    ("Primary valuation lens", "FY2031 EV/EBITDA, net of projected debt", "GAAP EPS and FCF are negative in a deliberate build cycle; EV/ARR and EV/forward revenue are cross-checks"),
    ("Stance", "Watch / Speculative positive bias", "Contracted ARR supports upside, but $3-8B of FY27 capex is unfunded and every case assumes heavy dilution"),
]
header(ws, 3, ["Field", "Value", "Comment"])
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            cell.number_format = "$0.00" if values[0] == "Price" else "#,##0.0"

metric_start = 4 + len(facts) + 1
header(ws, metric_start, ["Valuation metric", "Value", "Interpretation"])
metrics = [
    ("Trailing P/E (GAAP)", "n/m", "FY26 net loss $702.6M (-$2.22/share) after $638.8M mining impairments"),
    ("Forward P/E (FY27 non-GAAP)", "n/m", "FY27 consensus EPS -$3.42 (range -$6.89 to -$1.18); D&A on new GPUs precedes full revenue"),
    ("P/S (TTM)", MARKET_CAP / TTM_REVENUE, "TTM revenue $707.0M is 82% Bitcoin mining, a business being shut down"),
    ("P/S (FY27 consensus)", MARKET_CAP / FY27_REVENUE, "$2.81B consensus, 17 analysts"),
    ("EV/Sales (TTM)", ENTERPRISE_VALUE / TTM_REVENUE, "Backward-looking; not meaningful during the transition"),
    ("EV/Sales (FY27 consensus)", ENTERPRISE_VALUE / FY27_REVENUE, "Forward revenue cross-check"),
    ("EV/Sales (FY28 consensus)", ENTERPRISE_VALUE / FY28_REVENUE, "$7.41B FY28 consensus; first full year of Dec-2026 capacity"),
    ("EV / Dec-2026 contracted ARR", ENTERPRISE_VALUE / DEC26_ARR, "$4B ARR targeted operational by Dec 31, 2026; ~85% under contract per July 20 update"),
    ("EV/Adj. EBITDA (FY26)", ENTERPRISE_VALUE / TTM_ADJ_EBITDA, "FY26 adjusted EBITDA $245.7M (35% margin), mostly mining"),
    ("P/B", MARKET_CAP / BOOK_EQUITY, "Book equity $4.19B; tangible book $3.83B"),
    ("P/OCF (TTM)", MARKET_CAP / TTM_OCF, "Flattered: $1,841.7M of FY26 OCF was customer prepayments"),
    ("FCF yield (TTM)", TTM_FCF / MARKET_CAP, "OCF $2,100.4M less capex $4,333.1M = -$2,232.7M"),
    ("Unrestricted cash per share", CASH / SHARES, "$5.90B / 394.06M; committed to FY27 capex, not a liquidation floor"),
    ("Net debt per share", -NET_DEBT / SHARES, "Debt $7.84B less unrestricted cash"),
]
for row, values in enumerate(metrics, metric_start + 1):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            if "yield" in values[0]:
                cell.number_format = "0.0%"
            elif "per share" in values[0]:
                cell.number_format = "$0.00"
            else:
                cell.number_format = "0.0x"
widths(ws, [36, 30, 100, 14])

# 2. WACC
ws = wb.create_sheet("WACC")
title(ws, "IREN — WACC", 4, "CAPM and debt-weighted cost of capital")
header(ws, 3, ["Component", "Value", "Source / formula"])
wacc_rows = [
    ("Risk-free rate", rf / 100, "FRED DGS10 10-year Treasury, October 29, 2026 (4.98%)"),
    ("Equity risk premium", erp / 100, "Model assumption"),
    ("Raw levered beta (5Y)", raw_beta, "StockAnalysis; dominated by Bitcoin-miner history"),
    ("Blume-adjusted beta", beta, "0.67 × raw + 0.33; used for cost of equity"),
    ("Cost of equity", cost_equity / 100, "Risk-free rate + adjusted beta × ERP"),
    ("Pre-tax cost of debt", pretax_debt_cost / 100, "Blend: 0.25%-3.5% convert coupons (option value excluded), 6.0% IG GPU financing, 9.0% Blue Owl/PIMCO facility"),
    ("Tax rate", tax_rate / 100, "Blend of Australia 30% and U.S. 21%; cash taxes near zero today"),
    ("Market cap ($M)", MARKET_CAP, "Price × shares"),
    ("Total debt ($M)", TOTAL_DEBT, "StockAnalysis standardized total debt, June 30, 2026"),
    ("Equity weight", equity_weight, "Market cap / (market cap + debt)"),
    ("Debt weight", debt_weight, "Debt / (market cap + debt)"),
    ("After-tax debt cost", pretax_debt_cost / 100 * (1 - tax_rate / 100), "Kd × (1 − tax rate)"),
    ("WACC", wacc / 100, "E/V × Ke + D/V × Kd × (1 − t); StockAnalysis shows 15.42%"),
    ("Scenario discount rates", "20% / 18% / 16%", "Bear / base / bull equity discount rates applied to FY2031 per-share values; near Ke because the scenario output is levered equity"),
]
for row, values in enumerate(wacc_rows, 4):
    for col, value in enumerate(values, 1):
        is_wacc = values[0] == "WACC"
        cell = put(ws, row, col, value, bold=(col == 1 or is_wacc), fill=(gold if is_wacc else None))
        if col == 2 and values[0] in {"Market cap ($M)", "Total debt ($M)"}:
            cell.number_format = "#,##0.0"
        elif col == 2 and "beta" in values[0]:
            cell.number_format = "0.00"
        elif col == 2 and isinstance(value, float):
            cell.number_format = "0.00%"
widths(ws, [30, 22, 100, 14])

# 3. Scenarios
ws = wb.create_sheet("Scenarios")
title(ws, "IREN — FY2031 EV/EBITDA Scenarios", 5, "FY2027 consensus revenue ($2.81B) compounded to FY2031; terminal equity value discounted 4.67 years; USD millions")
header(ws, 3, ["Metric", "Bear", "Base", "Bull", "Notes"])
keys = ("Bear", "Base", "Bull")
scenario_rows = [
    ("Revenue CAGR (FY27-FY31)", *(SCENARIOS[k]["cagr"] for k in keys), "From $2.81B FY27 consensus; FY28 consensus is $7.41B"),
    ("FY2031 revenue ($M)", *(SCENARIOS[k]["revenue"] for k in keys), "Bear ~0.75GW monetized at lower pricing; base ~1.2GW; bull ~1.6GW+ from the >5GW pipeline"),
    ("Adjusted EBITDA margin", *(SCENARIOS[k]["margin"] for k in keys), "AI cloud cost of revenue ~13% of segment revenue in Q4 FY26; SG&A scales down as a % of revenue"),
    ("FY2031 adjusted EBITDA ($M)", *(SCENARIOS[k]["ebitda"] for k in keys), "Revenue × margin"),
    ("Exit EV/EBITDA", *(SCENARIOS[k]["multiple"] for k in keys), "GPUs depreciate in ~5 years, so EBITDA overstates owner cash; mature infra leasing trades ~6-10x"),
    ("Implied EV ($M)", *(SCENARIOS[k]["ev"] for k in keys), "EBITDA × multiple"),
    ("Less FY2031 net debt ($M)", *(-SCENARIOS[k]["net_debt"] for k in keys), "Today $1.94B; FY27 capex $25-30B plus later builds funded by GPU financing, converts and asset debt"),
    ("Equity value ($M)", *(SCENARIOS[k]["equity"] for k in keys), "Implied EV − net debt"),
    ("FY2031 shares (M)", *(SCENARIOS[k]["shares"] for k in keys), "394.06M today; $3.5B ATM capacity remains; in-the-money 2029/2030 converts; SBC"),
    ("Dilution vs. today", *(SCENARIOS[k]["dilution"] for k in keys), "Bear assumes equity is raised at depressed prices"),
    ("FY2031 value per share", *(SCENARIOS[k]["terminal_price"] for k in keys), "Undiscounted"),
    ("Discount rate", *(SCENARIOS[k]["discount"] for k in keys), "Levered equity rate; CAPM Ke with adjusted beta is ~21%"),
    ("Present target price", *(SCENARIOS[k]["target"] for k in keys), "FY2031 value discounted 4.67 years"),
    ("Upside / (downside)", *((SCENARIOS[k]["target"] / PRICE - 1) for k in keys), "Versus $23.95 close"),
    ("Probability", *(SCENARIOS[k]["weight"] for k in keys), "30% / 50% / 20%; bear weight reflects funding and execution risk"),
    ("Weighted value/share", *(SCENARIOS[k]["target"] * SCENARIOS[k]["weight"] for k in keys), "Contribution to fair value"),
]
pct_rows = {"Revenue CAGR (FY27-FY31)", "Adjusted EBITDA margin", "Discount rate", "Upside / (downside)", "Probability", "Dilution vs. today"}
usd_rows = {"FY2031 value per share", "Present target price", "Weighted value/share"}
for row, values in enumerate(scenario_rows, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col in (2, 3, 4) and values[0] in pct_rows:
            cell.number_format = "0.0%"
        elif col in (2, 3, 4) and values[0] in usd_rows:
            cell.number_format = "$0.00"
        elif col in (2, 3, 4) and values[0] == "Exit EV/EBITDA":
            cell.number_format = "0.0x"
        elif col in (2, 3, 4):
            cell.number_format = "#,##0.0"
fv_row = 4 + len(scenario_rows) + 1
put(ws, fv_row, 1, "Probability-weighted fair value", bold=True, fill=gold)
put(ws, fv_row, 2, weighted_value, bold=True, fill=gold).number_format = "$0.00"
put(ws, fv_row + 1, 1, "Upside from current price", bold=True, fill=gold)
put(ws, fv_row + 1, 2, weighted_value / PRICE - 1, bold=True, fill=gold).number_format = "0.0%"
put(ws, fv_row + 2, 1, "EV/ARR and analyst cross-check", bold=True, fill=gray)
put(ws, fv_row + 2, 2, f"At ${PRICE:.2f} IREN trades at {ENTERPRISE_VALUE / DEC26_ARR:.1f}x EV to the $4B Dec-2026 ARR target and {ENTERPRISE_VALUE / FY28_REVENUE:.1f}x FY28 consensus revenue, but net debt will rise by tens of billions before that ARR is fully billed. Analyst targets: $37 low / $75.42 average / $76.50 median / $139 high (20 analysts). The base case sits ~64% below the average target because sell-side targets have not caught up with the October funding-cost repricing (B. Riley cut $91 to $64 on Oct 30) and because this model charges for dilution explicitly.", fill=gray)
ws.merge_cells(start_row=fv_row + 2, start_column=2, end_row=fv_row + 2, end_column=5)
put(ws, fv_row + 3, 1, "Framework note", bold=True, fill=gray)
put(ws, fv_row + 3, 2, "FCF multiples are not used: FY26 FCF was -$2.23B, FY27 capex is guided at $25-30B, and FY26 OCF of $2.10B included $1.84B of customer prepayments. GAAP EPS is distorted by mining impairments ($638.8M), held-for-sale losses, $558.5M of unrealized derivative gains and $111.8M of convert inducement expense. The equity is a levered residual of a large asset base, so small changes in the exit multiple move the per-share value sharply: each 1.0x of FY2031 base EV/EBITDA is worth about $16.55 per share undiscounted.", fill=gray)
ws.merge_cells(start_row=fv_row + 3, start_column=2, end_row=fv_row + 3, end_column=5)
ws.row_dimensions[fv_row + 2].height = 75
ws.row_dimensions[fv_row + 3].height = 75
widths(ws, [32, 18, 18, 18, 96])

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "IREN — Actuals Source Audit", 5, "Financial statement figures in USD millions unless noted; fiscal year ends June 30")
header(ws, 3, ["Data point", "Value", "Source URL", "Source date", "Notes"])
sa = "https://stockanalysis.com/stocks/iren"
pr = "https://www.sec.gov/Archives/edgar/data/1878848/000187884826000051/irenreportsfy26results.htm"
jul = "https://www.sec.gov/Archives/edgar/data/1878848/000114036126028871/ef20078253_ex99-1.htm"
conv = "https://www.sec.gov/Archives/edgar/data/1878848/000114036126021285/ef20073507_ex99-1.htm"
prev = "https://equibles.com/research/iren-limited-iren-q1-fy27-earnings-preview-and-forecast"
audit = [
    ("Stock price", "$23.95", f"{sa}/", "2026-10-30", "Close, -8.76%; after-hours $24.16; 52-week range $23.06-$76.87"),
    ("Market cap", "$9.44B", f"{sa}/statistics/", "2026-10-30", "394.06M shares; -44.4% YoY market cap"),
    ("Enterprise value", "$11.38B", f"{sa}/statistics/", "2026-10-30", "Excludes restricted cash"),
    ("Shares outstanding", "394.06M", f"{sa}/statistics/", "2026-08-14", "+41.6% YoY; +8.89% QoQ; balance sheet count 380.19M at Jun-30 before Mirantis shares"),
    ("Revenue FY26", "$707.0M", pr, "2026-06-30", "AI Cloud $128.8M (FY25 $16.4M); Bitcoin mining $578.2M (FY25 $484.6M)"),
    ("Revenue Q4 FY26", "$137.2M", pr, "2026-06-30", "AI Cloud $70.5M; mining $66.7M; Q3 FY26 $144.8M"),
    ("Revenue history", "FY22 $59.0M / FY23 $75.5M / FY24 $187.2M / FY25 $501.0M", f"{sa}/financials/", "2026-06-30", "Pre-FY26 almost entirely Bitcoin mining"),
    ("Cost of revenue FY26 (ex-D&A)", "$219.7M", pr, "2026-06-30", "AI Cloud $16.9M (13.1% of segment revenue); mining $202.8M"),
    ("SG&A FY26", "$449.1M", pr, "2026-06-30", "FY25 $136.5M; includes $205.0M SBC"),
    ("D&A FY26", "$417.7M", pr, "2026-06-30", "FY25 $181.1M"),
    ("Impairments FY26", "$638.8M", pr, "2026-06-30", "Q4 $450.4M; decommissioned mining hardware"),
    ("Operating loss FY26", "-$1,046.7M", pr, "2026-06-30", "StockAnalysis standardizes to -$378.8M by moving impairments and disposals below EBIT"),
    ("Unrealized gain on financial instruments FY26", "$558.5M", pr, "2026-06-30", "Capped call / derivative marks; non-cash"),
    ("Debt conversion inducement expense FY26", "$111.8M", pr, "2026-06-30", "Induced conversion of part of the 2029 and 2030 notes; $1,623.5M cash paid"),
    ("Net income FY26", "-$702.6M", pr, "2026-06-30", "EPS -$2.22; FY25 +$86.9M"),
    ("Adjusted EBITDA FY26", "$245.7M (35%)", pr, "2026-06-30", "Q4 $19.2M (14%); FY25 $269.7M (54%)"),
    ("Cash and equivalents", "$5,895.6M", pr, "2026-06-30", "Plus restricted cash $1,670.3M current and $53.7M non-current"),
    ("Total debt", "$7,840M", f"{sa}/financials/balance-sheet/", "2026-06-30", "Debt $169.4M current + $7,423.6M non-current + finance leases $243.8M"),
    ("Convertible notes issued FY26", "$6,299.6M proceeds", pr, "2026-06-30", "Includes $3.0B 1.00% 2033 notes (conv. $73.07) and $1B 2032 + $1B 2033 notes"),
    ("2033 notes (May 2026)", "$3.0B, 1.00%, conv. $73.07", conv, "2026-05-14", "Capped call to $110.30; no investor put"),
    ("Deferred revenue", "$1,842.6M", pr, "2026-06-30", "$46.5M current + $1,796.1M non-current; customer prepayments"),
    ("Remaining performance obligations", "$5.1B", prev, "2026-06-30", "Per 10-K as summarized by Equibles"),
    ("PP&E, net", "$6,753.2M", pr, "2026-06-30", "Construction in progress $3.66B"),
    ("Stockholders' equity", "$4,185.6M", pr, "2026-06-30", "Goodwill $36.6M; intangibles $317.4M (Mirantis/Nostrum)"),
    ("Operating cash flow FY26", "$2,100.4M", pr, "2026-06-30", "Includes $1,841.7M increase in deferred revenue"),
    ("Capex FY26", "$4,333.1M", pr, "2026-06-30", "PP&E $2,998.0M + computer hardware $1,335.1M"),
    ("FCF FY26", "-$2,232.7M", f"{sa}/financials/cash-flow-statement/", "2026-06-30", "OCF less capex"),
    ("Equity issued FY26", "$4,742.8M", pr, "2026-06-30", "ATM and placements; $2.5B sold under $6.0B ATM by Aug 14"),
    ("SBC FY26", "$205.0M", pr, "2026-06-30", "29% of revenue; FY25 $42.6M"),
    ("ARR", "$1B operating (Aug 26); $4B contracted for 2026 capacity", pr, "2026-08-27", "ARR = GPU-hour pricing × 8,760; not GAAP revenue"),
    ("Contract pricing", ">$20M revenue per MW (IT), ~2-year payback", pr, "2026-08-27", "Active discussions ~$25M/MW; prepayments 45-55% of GPU capex"),
    ("Capacity targets", "0.3GW IT 2026; 0.8GW IT cumulative 2027", pr, "2026-08-27", ">5GW pipeline: Sweetwater, Kiowa, Bundey, Badajoz"),
    ("FY27 capex guide", "$25-30B", "https://finance.yahoo.com/quote/F8P.F/earnings/F8P.F-Q4-2026-earnings_call-662889.html", "2026-08-27", "~$14B secured (cash, committed financing, prepayments)"),
    ("GPU financing", "$3.6B IG at 6.0%; $2.4B Blue Owl/PIMCO at 9.0%", pr, "2026-08-27", "Microsoft financing + prepayments fund 96% of associated GPU capex"),
    ("Customers", "Microsoft, NVIDIA, Perplexity, Figure AI, Together AI, Fluidstack, Fireworks, Fal, Hume, Cohere, frontier lab", jul, "2026-07-20", "Weighted average contract term ~4 years"),
    ("FY27 consensus", "Revenue $2.81B; EPS -$3.42; op. income -$715.9M; FCF -$21.42B", f"{sa}/forecast/", "2026-10-30", "17 analysts; revenue range $2.52B-$3.28B"),
    ("FY28 consensus revenue", "$7.41B", f"{sa}/forecast/", "2026-10-30", "+164%; detail beyond revenue gated"),
    ("Q1 FY27 consensus", "Revenue ~$221-228M; EPS ~-$0.67 to -$0.72", prev, "2026-10-26", "Equibles cites $221.3M (13 analysts); ChartMill $227.9M; TipRanks EPS -$0.72"),
    ("Analyst price target", "$75.42 avg / $76.50 median / $37-$139", f"{sa}/forecast/", "2026-10-30", "20 analysts: 13 Strong Buy, 3 Buy, 4 Hold"),
    ("Beta", "4.27", f"{sa}/statistics/", "2026-10-30", "Five-year"),
    ("Short interest", "94.62M (24.01% of shares)", f"{sa}/statistics/", "2026-10-15", "Previous month 81.65M; 2.17 days to cover"),
    ("U.S. 10Y Treasury", "4.98%", "https://fred.stlouisfed.org/series/DGS10", "2026-10-29", "Risk-free rate"),
    ("Next earnings", "Nov 5, 2026 (after close)", f"{sa}/statistics/", "2026-10-30", "Q1 FY27, quarter ended Sep 30, 2026"),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [34, 40, 90, 14, 72])

# 5. Questions
ws = wb.create_sheet("Questions")
title(ws, "IREN — Open Questions", 4, "Items that can change valuation or conviction")
header(ws, 3, ["#", "Question", "Why it matters", "Best evidence / next check"])
questions = [
    (1, "How will IREN fund the $3-8B gap between $25-30B of FY27 capex and ~$14B secured plus ~$8B of expected GPU financing?", "The remaining $3.5B ATM would be ~146M shares at $23.95 (+37%); the funding mix decides per-share value more than revenue does.", "Q1 FY27 release (Nov 5): ATM sales after Aug 14, new data center financing, capex guide update."),
    (2, "How much of the 2029 (conv. ~$13.64) and 2030 (conv. ~$16.81) convertible notes remain after the FY26 induced conversions?", "Both are deep in the money; residual principal converts into tens of millions of shares unless settled in cash.", "10-K debt footnote; Q1 FY27 10-Q."),
    (3, "Will Horizons 2-4 for Microsoft be delivered and accepted in the December quarter as targeted?", "Microsoft is ~half of the $4B December ARR; delays push revenue into 2027 while interest and D&A accrue.", "Delivery/acceptance 8-Ks; Q2 FY27 revenue (Feb 2027)."),
    (4, "What is the true counterparty mix and credit quality behind the $4B ARR?", "Non-investment-grade AI labs (Perplexity, Figure, Fal, Hume) carry higher default risk; the Blue Owl/PIMCO facility costs 9.0% for that reason.", "Customer concentration disclosure; prepayment terms; any customer defaults in the sector."),
    (5, "Who is the undisclosed frontier AI lab and what are its term, pricing and prepayment?", "A frontier-lab anchor could fill 2027 capacity at >$20M/MW; it also adds concentration.", "Customer announcement; 8-K."),
    (6, "What depreciation life does IREN use for GB300-class GPUs, and does it match contract terms (~4 years weighted average)?", "If GPUs outlive contracts only at much lower re-lease rates, EBITDA overstates owner earnings and terminal multiples should be lower.", "10-K PP&E policy; renewal pricing on first contracts to roll."),
    (7, "Is the $20-25M revenue per MW pricing durable as Blackwell supply grows and Rubin arrives?", "Pricing per MW is the main revenue driver; a reset toward $12-15M/MW would cut base-case revenue materially.", "New contract disclosures; peer pricing (CoreWeave, Nebius)."),
    (8, "How exposed are Childress and Sweetwater to ERCOT large-load interconnection changes and the Texas governor's audit?", "Texas sites are central to the 2027 capacity plan; batching or curtailment rules could delay energization.", "ERCOT large-load rulings; management commentary."),
    (9, "What is the cost and timing of decommissioning mining, and are further impairments coming?", "FY26 carried $638.8M of impairments and $110.6M held-for-sale losses; remaining miners (23.2 EH/s installed on Jun-30) will be retired by Dec 2026.", "Q1/Q2 FY27 impairment lines; assets held for sale."),
    (10, "How much revenue and margin do Mirantis and Nostrum add, and what did they cost?", "Mirantis (~12.6M shares + ~$40M cash) is pitched as a managed-services margin lever; Nostrum expands into Spain.", "Segment disclosure; purchase price allocation."),
    (11, "Why did cash SG&A rise so fast ($85.4M in Q4 FY26, guided +$40-50M in Q1 FY27), and when does it plateau?", "Headcount nearly tripled in FY26; SG&A is the swing factor between 50% and 65% EBITDA margins.", "Quarterly SG&A and headcount."),
    (12, "Do covenants on the GPU financings restrict cash movement or require cash sweeps from specific contracts?", "$1.72B of cash is already restricted; project-level ring-fencing limits corporate flexibility.", "Financing agreements filed as 8-K exhibits."),
    (13, "Is the 24% short interest mostly convertible-arbitrage hedging or fundamental shorts?", "$8B+ of converts support a structural short base; a fundamental short would signal skepticism on funding.", "Short interest trend vs. convert issuance."),
    (14, "What is the expected effective tax rate once AI cloud is profitable, given Australian domicile and U.S./Canadian operations?", "Long-run net income and P/E anchors depend on the tax blend.", "10-K tax footnote."),
    (15, "Does Microsoft's lower-than-expected capex (late October 2026) change demand for third-party GPU capacity in 2027-2028?", "Hyperscaler capex is the demand signal for neocloud contracting; 2027 capacity is not yet contracted.", "2027 contract signings; hyperscaler capex guides."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 80, 72, 60])

# 6. Sources
ws = wb.create_sheet("Sources")
title(ws, "IREN — Sources", 4, "Public sources accessed October 31, 2026")
header(ws, 3, ["#", "Source", "URL", "Use"])
sources = [
    (1, "StockAnalysis overview", f"{sa}/", "Price, range, headline market data, news"),
    (2, "StockAnalysis financials", f"{sa}/financials/", "Income statement, segment revenue (annual and quarterly)"),
    (3, "StockAnalysis balance sheet", f"{sa}/financials/balance-sheet/", "Cash, restricted cash, debt, deferred revenue, equity, share count"),
    (4, "StockAnalysis cash flow", f"{sa}/financials/cash-flow-statement/", "OCF, capex, FCF, SBC, equity and debt issuance"),
    (5, "StockAnalysis statistics", f"{sa}/statistics/", "EV, beta, shares, short interest, valuation ratios"),
    (6, "StockAnalysis forecast", f"{sa}/forecast/", "Consensus revenue/EPS/FCF and price targets"),
    (7, "StockAnalysis profile", f"{sa}/company/", "Company identity, executives, filings"),
    (8, "IREN FY26 results (SEC 8-K Ex. 99.1, Aug 27, 2026)", pr, "Financial statements, ARR, pricing, financing, capacity"),
    (9, "IREN July 20, 2026 contract update (SEC 8-K Ex. 99.1)", jul, "$2.8B TCV, customer list, ARR target"),
    (10, "IREN $3.0B 2033 convertible notes close (SEC 8-K Ex. 99.1)", conv, "Convert terms"),
    (11, "IREN Q4 FY26 earnings call (Quartr via Yahoo Finance)", "https://finance.yahoo.com/quote/F8P.F/earnings/F8P.F-Q4-2026-earnings_call-662889.html", "FY27 capex guide, funding commentary"),
    (12, "Equibles Q1 FY27 earnings preview (Oct 26, 2026)", prev, "Consensus, ARR math, ATM usage, short interest"),
    (13, "IREN $2B convertible notes pricing (2032/2033)", "https://irisenergy.gcs-web.com/news-releases/news-release-details/iren-prices-2-billion-convertible-notes-offering", "2032/2033 notes; legacy 2029/2030 conversion prices"),
    (14, "TipRanks IREN earnings calendar", "https://www.tipranks.com/stocks/iren/earnings", "Nov 5 confirmed date; Q1 EPS consensus"),
    (15, "FRED DGS10", "https://fred.stlouisfed.org/series/DGS10", "Risk-free rate"),
]
for row, values in enumerate(sources, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [7, 50, 110, 60])

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert isclose(check["Scenarios"].cell(row=fv_row, column=2).value, weighted_value, rel_tol=1e-12)
print(f"Market cap: ${MARKET_CAP:,.1f}M | EV: ${ENTERPRISE_VALUE:,.1f}M | EV incl. restricted cash: ${EV_INCL_RESTRICTED:,.1f}M")
print(f"Adjusted beta: {beta:.2f} | Cost of equity: {cost_equity:.2f}% | WACC: {wacc:.2f}%")
for name, case in SCENARIOS.items():
    print(f"{name}: CAGR {case['cagr']:.1%}, EBITDA ${case['ebitda']:,.0f}M, EV ${case['ev']:,.0f}M, equity ${case['equity']:,.0f}M, FY31 ${case['terminal_price']:.2f}, target ${case['target']:.2f} ({case['target'] / PRICE - 1:+.1%})")
print(f"Probability-weighted fair value: ${weighted_value:.2f} ({weighted_value / PRICE - 1:+.1%})")
print(f"Wrote and verified {OUT}")
