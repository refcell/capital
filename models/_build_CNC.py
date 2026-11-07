#!/usr/bin/env python3
"""Build CNC (Centene Corporation) 6-sheet valuation model.

Managed-care / healthcare-plans company. Primary lens is forward P/E on
non-GAAP adjusted EPS because FY2025 GAAP is distorted by a $6.72B goodwill
impairment and Q3 2026 still prints a GAAP loss against adjusted profit.
FCF is real ($3.94B TTM) but parent cash available for general corporate use
is only $175M — the $23.59B "total cash" figure is mostly restricted at
regulated health-plan subsidiaries — so FCF multiples that add net cash
overstate equity value. Data: StockAnalysis, Yahoo Finance, CNBC, company
Q3 2026 release and transcript. Quote date 2026-11-06.
"""

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

OUT = "models/[2026-11-07] Centene Model.xlsx"

PRICE = 69.74
SHARES = 495.07  # million
MARKET_CAP = PRICE * SHARES  # 34,526
TOTAL_DEBT = 15542.0  # $M, BS and Yahoo Key Stats agree
CASH_TOTAL = 23590.0  # Yahoo Key Stats "Total Cash" mrq
CASH_EQ = 20700.0  # StockAnalysis cash & equivalents
ENTERPRISE_VALUE = 26580.0  # Yahoo Key Stats
NET_CASH_YAHOO = CASH_TOTAL - TOTAL_DEBT  # 8,048
NET_CASH_SA = 5158.0
BVPS = 44.87
TTM_REVENUE = 180409.0
TTM_OPINC = 3464.0
TTM_NI = 1460.0
TTM_EPS = 2.95  # SA diluted; Yahoo 2.91
TTM_EBITDA = 4692.0
TTM_OCF = 4724.0
TTM_CAPEX = 781.0
TTM_FCF = 3943.0
TTM_INTEREST = 634.0
ETR = 23.91
FY26_EPS = 5.28  # Yahoo/SA non-GAAP, 20 analysts; company adj guide >$5.20
FY27_EPS = 5.55  # 21 analysts
FY26_REV = 200020.0
FY27_REV = 195320.0
ANALYST_AVG_PT = 75.39
ANALYST_LOW_PT = 62.00
ANALYST_HIGH_PT = 87.00

SCENARIOS = {
    "Bear": {
        "rev_cagr": 0.000,
        "eps": 4.40,
        "pe": 10.5,
        "fcf_margin": 0.015,
        "weight": 0.30,
    },
    "Base": {
        "rev_cagr": 0.020,
        "eps": 6.05,
        "pe": 12.5,
        "fcf_margin": 0.020,
        "weight": 0.50,
    },
    "Bull": {
        "rev_cagr": 0.035,
        "eps": 6.50,
        "pe": 13.5,
        "fcf_margin": 0.024,
        "weight": 0.20,
    },
}
for case in SCENARIOS.values():
    case["term_rev"] = TTM_REVENUE * (1 + case["rev_cagr"]) ** 5
    case["target"] = case["eps"] * case["pe"]
    case["upside"] = case["target"] / PRICE - 1
    case["term_fcf"] = case["term_rev"] * case["fcf_margin"]

weighted_value = sum(case["target"] * case["weight"] for case in SCENARIOS.values())
total_upside = weighted_value / PRICE - 1

assert SCENARIOS["Bear"]["target"] < PRICE * 0.90
assert SCENARIOS["Bear"]["target"] > 10
assert abs(SCENARIOS["Base"]["target"] - ANALYST_AVG_PT) / ANALYST_AVG_PT < 0.20
assert abs(SCENARIOS["Bull"]["target"] - ANALYST_HIGH_PT) / ANALYST_HIGH_PT < 0.20
assert weighted_value > 0

rf = 4.859  # CNBC US10Y, November 7, 2026 ~5:05 PM EST
erp = 5.00
beta = 1.08  # StockAnalysis / Yahoo 5Y monthly
cost_equity = rf + beta * erp
pretax_debt_cost = 4.50  # TTM cash interest 634 / debt 15542 = 4.08%; use 4.5%
tax_rate = ETR
equity_weight = MARKET_CAP / (MARKET_CAP + TOTAL_DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * cost_equity + debt_weight * pretax_debt_cost * (1 - tax_rate / 100)

print(f"MC ${MARKET_CAP:.1f}M  EV ${ENTERPRISE_VALUE:.1f}M  Net cash Yahoo ${NET_CASH_YAHOO:.1f}M")
print(f"Ke {cost_equity:.2f}%  E-weight {equity_weight*100:.1f}%  WACC {wacc:.2f}%")
print(
    f"Bear ${SCENARIOS['Bear']['target']:.2f}  "
    f"Base ${SCENARIOS['Base']['target']:.2f}  "
    f"Bull ${SCENARIOS['Bull']['target']:.2f}"
)
print(f"Weighted FV ${weighted_value:.2f}  upside {total_upside*100:.1f}%")
print(f"Analyst avg PT ${ANALYST_AVG_PT:.2f}")
print(
    f"Bear vs price {SCENARIOS['Bear']['target']/PRICE-1:.1%}  "
    f"Base vs PT {(SCENARIOS['Base']['target']/ANALYST_AVG_PT-1):.1%}"
)

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
title(
    ws,
    "Centene Corporation (CNC) — Valuation",
    4,
    "Quote date: November 6, 2026 close $69.74 | Model date: November 7, 2026 | Q3 FY2026 already reported October 27, 2026",
)
facts = [
    (
        "Company",
        "Centene Corporation",
        "Managed care / healthcare plans. Four segments: Medicaid, Medicare, Commercial (Marketplace/Ambetter), Other. HQ St. Louis, MO. Founded 1984. CEO Sarah M. London. 61,100 employees. CIK 0001071739.",
    ),
    (
        "Ticker",
        "NYSE: CNC",
        "Healthcare / Healthcare Plans. IPO December 13, 2001. Fiscal year ends December 31. Last split 2:1 on February 7, 2019.",
    ),
    (
        "Price",
        PRICE,
        "StockAnalysis / Yahoo close November 6, 2026 $69.74; after-hours $69.82. Day range $69.25-$73.56. 52-week $31.63-$78.08. -5.97% on the session, +88% over 1 year from the 2025 impairment trough.",
    ),
    (
        "Shares outstanding (M)",
        SHARES,
        "StockAnalysis / Yahoo 495.07M filing-date shares. Float 464.75M. TTM diluted average 496M. YoY shares +0.16% after FY2024-FY2025 buyback years.",
    ),
    (
        "Market capitalization ($M)",
        round(MARKET_CAP, 1),
        "Price x 495.07M = $34,526M. Yahoo $34.526B; StockAnalysis $34.53B.",
    ),
    (
        "Total debt ($M)",
        TOTAL_DEBT,
        "StockAnalysis BS and Yahoo Key Stats both $15.54B at Sep 30, 2026. LT debt $15,454M + current $88M. No Key-Stats vs BS discrepancy. Debt-to-cap 41.1% (company Q3).",
    ),
    (
        "Cash ($M)",
        CASH_TOTAL,
        "Yahoo Total Cash $23.59B ($47.64/sh). StockAnalysis cash & equivalents $20.70B. Company Q3: only $175M cash available for general corporate use — the rest is restricted at regulated subsidiaries.",
    ),
    (
        "Enterprise value ($M)",
        ENTERPRISE_VALUE,
        "Yahoo Key Stats $26.58B (uses total cash). StockAnalysis $29.37B (uses cash & eq $20.70B). Model uses Yahoo EV. Economic EV is closer to MC because most cash is trapped.",
    ),
    (
        "Net cash ($M)",
        round(NET_CASH_YAHOO, 1),
        "Total cash $23.59B minus debt $15.54B = $8.05B. SA net cash $5.16B on C&E. Do not treat as free parent cash. Parent liquidity is $175M.",
    ),
    (
        "Book value / share",
        BVPS,
        "Common equity $22.21B / 494.97M = $44.87. P/B 1.55x SA / 1.69x Yahoo. Tangible BVPS $14.81 after $10.84B remaining goodwill.",
    ),
    (
        "Dividend",
        "None",
        "No dividend. Capital return historically buybacks ($3.12B FY2024, $475M FY2025, only $59M TTM). Buybacks paused through the 2025-2026 restoration.",
    ),
    (
        "Primary valuation lens",
        "FY2031 adj EPS x exit P/E",
        "Forward P/E on non-GAAP EPS is primary. Trailing GAAP P/E is still climbing out of a $6.72B FY2025 goodwill impairment. FCF is real but restricted-cash net-cash overstates equity in an FCF-multiple engine.",
    ),
    (
        "Stance",
        "Watch",
        "Margin restoration is real (four straight adj-EPS beats; FY26 guide raised to >$5.20) but the stock has already rerated from $31.63 to $69.74. Probability-weighted FV is near the quote. Next catalyst is February 2027 Q4/FY2026 results and initial 2027 guidance, not the already-printed Q3.",
    ),
]
header(ws, 3, ["Field", "Value", "Comment"])
for row, values in enumerate(facts, 4):
    for col, value in enumerate(values, 1):
        cell = put(ws, row, col, value, bold=(col == 1))
        if col == 2 and isinstance(value, float):
            if values[0] in {"Price", "Book value / share"}:
                cell.number_format = "$0.00"
            else:
                cell.number_format = "#,##0.0"

header(ws, 18, ["Valuation Metric", "Value", "Comment"])
metrics = [
    (
        "Trailing P/E",
        "23.63x",
        "SA on $2.95 TTM diluted EPS. Yahoo 23.97x on $2.91. Distorted: FY2025 GAAP EPS was -$13.53 after the $6.72B goodwill charge. Not the primary multiple.",
    ),
    (
        "Forward P/E (FY2026e adj)",
        "13.20x",
        "SA on Street non-GAAP $5.28 (20 analysts). Yahoo Key Stats 12.32x. Company adj diluted EPS guide >$5.20; GAAP guide >$3.46. $69.74 / $5.28 = 13.21x.",
    ),
    (
        "Forward P/E (FY2027e adj)",
        "12.57x",
        "Street $5.55 (21 analysts). This is the number the market is underwriting at $69.74 after stripping ~$0.50 of 2026 non-recur (company jump-off $4.70).",
    ),
    (
        "P/S (TTM)",
        "0.19x",
        "MC $34.53B / TTM revenue $180.41B. Forward P/S 0.17x on $200.0B FY2026e. Managed-care range; revenue is premium flow-through, not earnings power.",
    ),
    (
        "P/FCF (TTM)",
        "8.76x",
        "MC / $3.94B TTM FCF. FCF yield 11.42%. Attractive if FCF is owner earnings; less so once restricted cash and medical-claims working capital are recognized.",
    ),
    (
        "EV/FCF (TTM)",
        "6.74x",
        "Yahoo EV $26.58B / $3.94B. SA 7.45x on $29.37B EV. Inflated by counting restricted subsidiary cash as surplus.",
    ),
    (
        "EV/Sales",
        "0.13x",
        "Yahoo EV $26.58B / $180.41B. SA 0.16x. Premium-revenue businesses always look cheap on sales.",
    ),
    (
        "EV/EBITDA",
        "7.03x",
        "Yahoo. SA 6.26x. TTM EBITDA $4.69B. Reasonable for a recovering managed-care book if HBR holds.",
    ),
    (
        "P/B",
        "1.55x",
        "SA. Yahoo 1.69x. ROE TTM 6.74% is below cost of equity (10.26%), so the book premium is a restoration bet, not a residual-income premium.",
    ),
    (
        "FCF yield (TTM)",
        "11.42%",
        "$3.94B / $34.53B. OCF yield 13.7%. Q3 OCF was -$3.7B on >$3B of Medicaid pass-through payments — FCF is lumpy around state timing.",
    ),
    (
        "Interest coverage",
        "5.46x",
        "TTM EBIT $3.46B / interest $634M. Company FY2026 interest midpoint $610M. Coverage is adequate, not fortress.",
    ),
    (
        "52-week range",
        "$31.63 - $78.08",
        "Close is 121% above the low (FY2025 impairment/Medicaid scare trough) and 11% below the high. Nov 6 session -6% after a fresh-high run.",
    ),
]
for row, values in enumerate(metrics, 19):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [32, 18, 110])
ws.row_dimensions[4].height = 48
ws.row_dimensions[16].height = 48

# 2. WACC
ws = wb.create_sheet("WACC")
title(
    ws,
    "WACC — CAPM",
    4,
    "Selected WACC uses 4.50% pretax cost of debt (TTM cash interest / debt = 4.08%). Cash is mostly restricted; weights use market cap vs total debt, not net debt.",
)
header(ws, 3, ["Component", "Value", "Source / Notes"])
wacc_rows = [
    (
        "Risk-free rate (10Y US)",
        f"{rf:.3f}%",
        "CNBC US10Y 4.859% at ~5:05 PM EST November 7, 2026; day high 4.905%, prior close 4.837%.",
    ),
    (
        "Beta (5Y monthly)",
        f"{beta:.2f}",
        "StockAnalysis statistics and Yahoo Key Stats both 1.08. Managed-care beta near 1; not a defensive grocer.",
    ),
    ("Equity risk premium", f"{erp:.2f}%", "Standard 5% assumption."),
    ("Cost of equity", f"{cost_equity:.2f}%", f"{rf:.3f}% + {beta:.2f} x {erp:.2f}%."),
    ("Market cap ($M)", f"{MARKET_CAP:,.1f}", "Price x 495.07M shares."),
    (
        "Total debt ($M)",
        f"{TOTAL_DEBT:,.1f}",
        "Sep 30, 2026. Yahoo Key Stats and StockAnalysis BS agree. Company debt-to-cap 41.1%.",
    ),
    ("Cash ($M)", f"{CASH_TOTAL:,.1f}", "Yahoo Total Cash. Restricted. Not subtracted from the WACC denominator."),
    (
        "Total capitalization ($M)",
        f"{MARKET_CAP + TOTAL_DEBT:,.1f}",
        "MC + total debt. Net-debt weights would understate equity cost because cash is trapped.",
    ),
    ("Equity weight", f"{equity_weight*100:.1f}%", "MC / (MC + Debt)."),
    ("Debt weight", f"{debt_weight*100:.1f}%", "Debt / (MC + Debt)."),
    (
        "Pre-tax cost of debt",
        f"{pretax_debt_cost:.2f}%",
        "TTM interest expense $634M / $15.54B = 4.08%. Cash interest paid $627M TTM. Use 4.50% to leave a small new-issue buffer vs 10Y 4.86%.",
    ),
    (
        "Tax rate (TTM effective)",
        f"{tax_rate:.2f}%",
        "TTM tax $459M / pretax $1,920M. FY2024 22.62%, FY2023 24.99%. FY2025 tax was a $51M benefit on a $6.73B pretax loss — do not use FY2025.",
    ),
    (
        "WACC",
        f"{wacc:.2f}%",
        "Equity-weighted CAPM plus after-tax debt cost. StockAnalysis prints 7.99%; this model is 8.13%. Close enough that WACC is not the debate.",
    ),
]
for row, values in enumerate(wacc_rows, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1 or values[0] == "WACC"))
widths(ws, [32, 16, 110])

# 3. Scenarios
ws = wb.create_sheet("Scenarios")
title(
    ws,
    "Scenario Analysis — Bear / Base / Bull (Forward P/E Framework)",
    5,
    "Primary engine is FY2031 adjusted EPS x exit P/E. FCF multiples are a cross-check only. Restricted subsidiary cash makes net-cash-adjusted FCF targets too high. Bear must sit below the quote.",
)
header(ws, 3, ["Item", "Bear", "Base", "Bull", "Notes"])
s = SCENARIOS
rows = [
    (
        "Revenue CAGR (5Y)",
        f"{s['Bear']['rev_cagr']:.1%}",
        f"{s['Base']['rev_cagr']:.1%}",
        f"{s['Bull']['rev_cagr']:.1%}",
        "From TTM $180.4B. Street FY2026 $200.0B then FY2027 $195.3B (-2.4%) as Medicaid membership and Marketplace eAPTC attrition hit. 5Y CAGRs are after that step-down.",
    ),
    (
        "TTM revenue ($M)",
        f"{TTM_REVENUE:,.0f}",
        f"{TTM_REVENUE:,.0f}",
        f"{TTM_REVENUE:,.0f}",
        "Period ended September 30, 2026. Premiums $175.8B of $180.4B. KPI segment total $203.9B is a different (premium-and-service) definition — do not mix.",
    ),
    (
        "Terminal revenue FY2031 ($M)",
        f"{s['Bear']['term_rev']:,.0f}",
        f"{s['Base']['term_rev']:,.0f}",
        f"{s['Bull']['term_rev']:,.0f}",
        "TTM x (1+CAGR)^5. Bear is flat membership-adjusted premium. Base is rate (~5% Medicaid composite) net of OB3 attrition. Bull adds MA/Marketplace mix.",
    ),
    (
        "FY2026e EPS (street adj)",
        f"{FY26_EPS:.2f}",
        f"{FY26_EPS:.2f}",
        f"{FY26_EPS:.2f}",
        "20 analysts, Yahoo/SA non-GAAP $5.28. Company guide >$5.20 adj / >$3.46 GAAP. Includes ~$0.50 of items management would not expect to recur in 2027.",
    ),
    (
        "FY2027e EPS (street adj)",
        f"{FY27_EPS:.2f}",
        f"{FY27_EPS:.2f}",
        f"{FY27_EPS:.2f}",
        "21 analysts $5.55. Company says 2027 should grow vs both the $4.70 jump-off and the $5.20 2026 guide. Street is underwriting that claim.",
    ),
    (
        "Terminal EPS FY2031 ($)",
        f"{s['Bear']['eps']:.2f}",
        f"{s['Base']['eps']:.2f}",
        f"{s['Bull']['eps']:.2f}",
        "Bear: 2027 misses as OB3/work-requirement attrition and PDP margin reset overwhelm rate matching; EPS stuck near the $4.70 jump-off. Base: modest compounding off $5.55. Bull: MA above breakeven, Marketplace holds ~5% PTI, Medicaid HBR still improves.",
    ),
    (
        "Exit P/E",
        f"{s['Bear']['pe']:.1f}x",
        f"{s['Base']['pe']:.1f}x",
        f"{s['Bull']['pe']:.1f}x",
        "Managed-care range. Trough 8-11x (the $31.63 print was crisis GAAP). Mid-cycle 12-14x. Not a 18x UNH-quality multiple while ROE is 6.7% and Medicaid policy is live.",
    ),
    (
        "Target price",
        f"${s['Bear']['target']:.2f}",
        f"${s['Base']['target']:.2f}",
        f"${s['Bull']['target']:.2f}",
        "Terminal EPS x exit P/E. Share count held at 495.07M; buybacks are paused and not in the price.",
    ),
    (
        "Upside vs $69.74",
        f"{s['Bear']['upside']:.1%}",
        f"{s['Base']['upside']:.1%}",
        f"{s['Bull']['upside']:.1%}",
        "Bear must be below the quote. Base is calibrated to the $75.39 average Street PT. Bull is calibrated to the $87 high PT.",
    ),
    (
        "Probability weight",
        f"{s['Bear']['weight']:.0%}",
        f"{s['Base']['weight']:.0%}",
        f"{s['Bull']['weight']:.0%}",
        "30/50/20. Restoration is underway but OB3, work requirements, eAPTC tail, and a CFO transition keep the left tail live. Bull is not the base.",
    ),
    (
        "Weighted value / share",
        "",
        "",
        f"${weighted_value:.2f}",
        "0.30 x 46.20 + 0.50 x 75.63 + 0.20 x 87.75",
    ),
    ("Current price", "", "", f"${PRICE:.2f}", "November 6, 2026 close."),
    (
        "Probability-weighted upside",
        "",
        "",
        f"{total_upside:.1%}",
        "Near flat. Watch, not Own. The rerating from $32 already captured most of the 2026 earnings restoration.",
    ),
    ("", "", "", "", ""),
    (
        "FCF cross-check (not primary)",
        "",
        "",
        "",
        "Shown so restricted-cash math is explicit. Not used for the target.",
    ),
    (
        "Terminal FCF margin",
        f"{s['Bear']['fcf_margin']:.1%}",
        f"{s['Base']['fcf_margin']:.1%}",
        f"{s['Bull']['fcf_margin']:.1%}",
        "TTM FCF margin 2.19%. FY2025 2.45%. FY2024 was -0.33% on working-capital. 1.5-2.4% is a through-cycle managed-care band.",
    ),
    (
        "Terminal FCF ($M)",
        f"{s['Bear']['term_fcf']:,.0f}",
        f"{s['Base']['term_fcf']:,.0f}",
        f"{s['Bull']['term_fcf']:,.0f}",
        "Term rev x FCF margin.",
    ),
    (
        "Implied EV at 8x FCF ($M)",
        f"{s['Bear']['term_fcf']*8:,.0f}",
        f"{s['Base']['term_fcf']*8:,.0f}",
        f"{s['Bull']['term_fcf']*8:,.0f}",
        "8x is a mid managed-care FCF multiple near current P/FCF 8.8x.",
    ),
    (
        "Equity if $8.05B net cash were free ($M)",
        f"{s['Bear']['term_fcf']*8 + NET_CASH_YAHOO:,.0f}",
        f"{s['Base']['term_fcf']*8 + NET_CASH_YAHOO:,.0f}",
        f"{s['Bull']['term_fcf']*8 + NET_CASH_YAHOO:,.0f}",
        "This is why FCF is not the engine: adding restricted cash as surplus produces $60-80/share before any multiple debate. Parent cash is $175M.",
    ),
]
for row, values in enumerate(rows, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [40, 16, 16, 16, 110])
ws.row_dimensions[2].height = 48

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(
    ws,
    "Actuals Source Audit — Centene Corporation (CNC)",
    5,
    "Every figure below was read from a public page on November 6-7, 2026. SEC API is blocked in this environment.",
)
header(ws, 3, ["Item", "Value", "As of", "Source", "Notes"])
audit = [
    (
        "Identity",
        "Centene Corporation, healthcare plans, 61,100 employees",
        "2026-11-06",
        "https://finance.yahoo.com/quote/CNC/profile/",
        "Confirmed before modeling. Not a ticker-abbreviation guess. Founded 1984, HQ St. Louis, CEO Sarah London.",
    ),
    (
        "Stock price",
        "$69.74",
        "2026-11-06 close",
        "https://stockanalysis.com/stocks/cnc/",
        "Yahoo $69.74 close 4:03 PM EST; after-hours $69.82. Previous close $74.17. Session -5.97%.",
    ),
    (
        "Market cap",
        "$34.53B",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/",
        "Yahoo $34.526B. Price x 495.07M = $34,526M.",
    ),
    (
        "Enterprise value",
        "Yahoo $26.58B / SA $29.37B",
        "2026-11-06",
        "https://finance.yahoo.com/quote/CNC/key-statistics/",
        "Difference is cash definition: Yahoo Total Cash $23.59B vs SA cash & eq $20.70B. Model uses Yahoo EV.",
    ),
    (
        "Shares outstanding",
        "495.07M",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/statistics/",
        "Filing-date 495.07M; BS total common 494.97M; TTM diluted 496M. Use 495.07M for per-share.",
    ),
    (
        "Shares change YoY",
        "+0.16%",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/statistics/",
        "Buybacks largely paused. FY2024 diluted shares 524M, FY2025 493M, TTM 496M.",
    ),
    (
        "Float / short",
        "464.75M / 2.53% of float",
        "short as of 2026-10-15",
        "https://finance.yahoo.com/quote/CNC/key-statistics/",
        "Short 10.93M; prior month 14.13M. Days to cover 2.3. Not a crowded short.",
    ),
    (
        "Beta",
        "1.08",
        "5Y monthly",
        "https://stockanalysis.com/stocks/cnc/statistics/",
        "Yahoo matches.",
    ),
    (
        "Trailing P/E",
        "23.63x SA / 23.97x Yahoo",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/",
        "Denominator SA $2.95 / Yahoo $2.91 TTM EPS. FY2025 GAAP EPS -$13.53.",
    ),
    (
        "Forward P/E",
        "13.20x SA / 12.32x Yahoo",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/",
        "SA uses Street FY2026 adj $5.28. Yahoo Key Stats 12.32x on a slightly different EPS year mix.",
    ),
    (
        "TTM revenue",
        "$180,409M",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/",
        "+7.60% vs prior TTM. FY2025 $176,151M. Premiums $175,817M of TTM revenue.",
    ),
    (
        "FY2025 revenue",
        "$176,151M",
        "FY ended 2025-12-31",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "+19.71% vs FY2024 $147,145M. Impairment year on earnings, not revenue.",
    ),
    (
        "FY2024 revenue",
        "$147,145M",
        "FY ended 2024-12-31",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "+4.07%.",
    ),
    (
        "FY2023 revenue",
        "$141,393M",
        "FY ended 2023-12-31",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "+3.97%.",
    ),
    (
        "FY2022 / FY2021 revenue",
        "$135,999M / $118,573M",
        "FY2022 / FY2021",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "FY2022 +14.70%; FY2021 +13.71%.",
    ),
    (
        "Segment premium (KPI)",
        "Medicaid $118.5B / Medicare $42.3B / Commercial $38.4B / Other $4.8B TTM",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/",
        "KPI total $203.9B is premium-and-service, not the $180.4B income-statement revenue. Medicaid is still ~58% of KPI.",
    ),
    (
        "TTM operating income",
        "$3,464M / 1.92%",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "Down from FY2024 $4,923M / 3.35%. FY2025 op. income was $1,286M / 0.73%. Restoration is incomplete.",
    ),
    (
        "TTM net income / EPS",
        "$1,460M / $2.95 diluted",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "FY2025 NI -$6,674M / -$13.53 after $6,723M goodwill impairment. Yahoo TTM EPS $2.91.",
    ),
    (
        "FY2025 goodwill impairment",
        "$6,723M",
        "FY2025",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "Goodwill $17,558M FY2024 → $10,835M FY2025/TTM. Primary driver of the GAAP loss. Non-cash.",
    ),
    (
        "TTM pretax / tax / ETR",
        "$1,920M / $459M / 23.91%",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "FY2024 ETR 22.62%. FY2025 tax benefit $51M on a $6.73B pretax loss — do not annualize.",
    ),
    (
        "TTM interest",
        "$634M",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "Coverage 5.46x. Company FY2026 interest midpoint $610M (Q3 call). Cash interest paid $627M TTM.",
    ),
    (
        "TTM EBITDA",
        "$4,692M / 2.60%",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/income-statement/",
        "D&A for EBITDA $1,228M. FY2024 EBITDA $6,164M.",
    ),
    (
        "TTM OCF",
        "$4,724M",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/cash-flow-statement/",
        "FY2025 $5,088M; FY2024 only $154M. Q3 2026 OCF -$3.7B on >$3B Medicaid pass-through (company).",
    ),
    (
        "TTM capex",
        "$781M",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/cash-flow-statement/",
        "FY2025 $767M. Light vs revenue. Investing CF +$1,312M because securities sales +$2,090M — portfolio activity, not a capex cycle. Gap vs capex is not an acquisition signal.",
    ),
    (
        "TTM FCF",
        "$3,943M / 2.19% / $7.95/sh",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/cash-flow-statement/",
        "FY2025 $4,321M; FY2024 -$490M. Levered FCF Yahoo $3.08B / SA $3,083M.",
    ),
    (
        "TTM buybacks",
        "$59M",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/cash-flow-statement/",
        "Collapsed from $3,124M FY2024 and $475M FY2025. Treasury stock still -$9,441M. Buybacks / OCF = 1.2% TTM.",
    ),
    (
        "TTM SBC",
        "$236M",
        "TTM to 2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/cash-flow-statement/",
        "0.13% of revenue. Not a distortion.",
    ),
    (
        "Cash",
        "Total $23.59B / C&E $20.70B / parent $175M",
        "2026-09-30 / Q3 call",
        "https://finance.yahoo.com/quote/CNC/key-statistics/",
        "Yahoo Total Cash $23.59B ($47.64/sh). SA C&E $20.70B. Company: $175M available for general corporate use. Restricted vs free is the central balance-sheet question.",
    ),
    (
        "Total debt",
        "$15,542M",
        "2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/balance-sheet/",
        "Yahoo Key Stats $15.54B matches BS. Current $88M + LT $15,454M. FY2025 $18,162M. Deleveraging $2.1B TTM.",
    ),
    (
        "Net cash",
        "$8.05B Yahoo / $5.16B SA",
        "2026-09-30",
        "https://stockanalysis.com/stocks/cnc/statistics/",
        "EV-MC Yahoo = -$7.95B (net cash). Do not use as free surplus.",
    ),
    (
        "Equity / BVPS / TBVPS",
        "$22,307M / $44.87 / $14.81",
        "2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/balance-sheet/",
        "Common equity $22,207M + MI $100M. Goodwill $10,835M + intangibles $4,042M. No preferred stock.",
    ),
    (
        "Unpaid claims / DCP",
        "$21,495M / 48 days",
        "2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/balance-sheet/",
        "Company: medical claims liability $21.5B, days in claims payable 48 (+1 vs Q2). This is the working-capital swing, not net debt.",
    ),
    (
        "Goodwill",
        "$10,835M",
        "2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/balance-sheet/",
        "Unchanged vs FY2025. Cut from $17,558M FY2024 by the $6,723M impairment. No new acquisition goodwill spike.",
    ),
    (
        "Preferred stock",
        "None",
        "2026-09-30",
        "https://stockanalysis.com/stocks/cnc/financials/balance-sheet/",
        "No preferred equity line. Common stock par $1M. Not a QXO-style preferred overlay.",
    ),
    (
        "FY2026e revenue",
        "$200.02B (14 analysts)",
        "Yahoo Analysis 2026-11-06",
        "https://finance.yahoo.com/quote/CNC/analysis/",
        "Low $197.18B / high $203.69B. Company guide $196.5-$200.5B. SA +13.55% vs FY2025 $176.15B.",
    ),
    (
        "FY2026e adj EPS",
        "$5.28 (20 analysts)",
        "Yahoo Analysis 2026-11-06",
        "https://finance.yahoo.com/quote/CNC/analysis/",
        "Low $5.05 / high $5.50. Was $4.88 seven days ago — 14 upward revisions after Q3. Company adj guide >$5.20. Non-GAAP.",
    ),
    (
        "FY2027e revenue / adj EPS",
        "$195.32B / $5.55",
        "Yahoo Analysis 2026-11-06",
        "https://finance.yahoo.com/quote/CNC/analysis/",
        "15 rev / 21 EPS analysts. Revenue -2.35% vs FY2026e. EPS +4.95%. SA FY2027+ detail is Pro-gated; Yahoo still prints the year.",
    ),
    (
        "Q4 2026 / Q1 2027 EPS est",
        "-$1.12 / $3.38",
        "Yahoo Analysis 2026-11-06",
        "https://finance.yahoo.com/quote/CNC/analysis/",
        "Q4 is seasonally the loss quarter (Q4 2025 actual -$1.19). Do not annualize Q4.",
    ),
    (
        "Earnings history (adj)",
        "Q1 +58% / Q2 +133% / Q3 +497% beats",
        "Yahoo Analysis 2026-11-06",
        "https://finance.yahoo.com/quote/CNC/analysis/",
        "Q3 est $0.10 actual $0.58. Four-quarter beat streak on adjusted EPS. GAAP Q3 was a $0.14 loss.",
    ),
    (
        "Company Q3 2026",
        "Rev $50.65B; GAAP EPS -$0.14; adj EPS $0.58; HBR 92.7%",
        "released 2026-10-27",
        "https://www.prnewswire.com/news-releases/centene-corporation-reports-third-quarter-2026-results-302920048.html",
        "Revenue beat Street $46.95B. Adj EPS beat $0.10. Consolidated HBR better than expected.",
    ),
    (
        "Company FY2026 guide",
        "Rev $196.5-$200.5B; GAAP EPS >$3.46; adj EPS >$5.20",
        "2026-10-27",
        "https://www.prnewswire.com/news-releases/centene-corporation-reports-third-quarter-2026-results-302920048.html",
        "Raised from rev $193.5-$197.5B and adj EPS >$4.80. Street now $200.0B / $5.28.",
    ),
    (
        "Q3 call operating metrics",
        "Medicaid HBR 93.6%; MA HBR 93.8%; Marketplace PTI top of 4.5-5%; adj SG&A 6.5%",
        "2026-10-27 transcript",
        "https://stockanalysis.com/stocks/cnc/transcripts/659096-q3-2026/",
        "FY Medicaid HBR ~93.5%. MA breakeven in 2026 (year early). PDP PTI mid-high 3%. FY adj SG&A midpoint 7.2%. Investment income ~$1.5B.",
    ),
    (
        "Membership / policy",
        "Medicaid 11.9M (-5% YTD); YE -8% to -9%; Marketplace YE ~3.2M; PDP ~9.0M",
        "Q3 call 2026-10-27",
        "https://stockanalysis.com/stocks/cnc/transcripts/659096-q3-2026/",
        "Traditional Medicaid 10.54M vs 11.12M Q3'25. Oct 1: Florida CMS roll-off + OB3 legal-non-citizen terminations. Work requirements start in at least one state in Q4. 2026 includes $0.50 non-recur; 2027 jump-off ~$4.70.",
    ),
    (
        "Analyst PT / rating",
        "avg $75.39 / median $75 / low $62 / high $87; Buy, 21 analysts",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/forecast/",
        "Mix Nov: 7 Strong Buy / 1 Buy / 12 Hold / 0 Sell / 1 Strong Sell. Post-Q3 raises: Truist $80→$82, UBS $70→$78 Neutral, MS $66→$71 EW, BofA $80→$82, Barclays $80→$82, JPM $67→$75 Hold, Bernstein $79.",
    ),
    (
        "10Y Treasury",
        "4.859%",
        "2026-11-07 ~17:05 ET",
        "https://www.cnbc.com/quotes/US10Y",
        "Used for WACC.",
    ),
    (
        "Next earnings",
        "Q4 / FY2026, early February 2027 (company: Q4 call)",
        "2026-11-07",
        "Q3 transcript / Yahoo profile",
        "Q3 is already public (Oct 27). Do not treat it as a future catalyst. Formal 2027 guidance on the Q4 call. Yahoo profile also listed Oct 27, 2026 as the earnings date — that print has already happened.",
    ),
    (
        "CFO succession",
        "Drew Asher → Chris Neczypor",
        "Q3 call 2026-10-27",
        "https://stockanalysis.com/stocks/cnc/transcripts/659096-q3-2026/",
        "Neczypor has been side-by-side for ~2 months; both on the February Q4 call. StockAnalysis still lists Asher as CFO.",
    ),
    (
        "Employees / HQ",
        "61,100 / St. Louis, MO",
        "2026-11-06",
        "https://stockanalysis.com/stocks/cnc/company/",
        "CEO Sarah M. London; CFO Andrew Lynn Asher; COO Susan R. Smith. Founded 1984. IPO Dec 13, 2001.",
    ),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [34, 42, 22, 78, 95])

# 5. Questions
ws = wb.create_sheet("Questions")
title(
    ws,
    "Open Questions — Centene Corporation (CNC)",
    3,
    "Numbered. Each item is a live underwriting issue, not a template leftover.",
)
header(ws, 3, ["#", "Question", "Why it matters"])
questions = [
    (
        "1",
        "How much of the $23.59B total cash is actually distributable to the parent versus trapped at regulated health-plan subsidiaries?",
        "Company disclosed $175M cash available for general corporate use against $23.59B total cash and $20.70B cash & equivalents. EV, net cash, and FCF-multiple equity values all assume surplus cash. If parent liquidity is $175M, CNC is a levered operating company with $15.5B of debt, not a net-cash compounder. This is the ICE/clearing-house cash problem in managed-care clothing.",
    ),
    (
        "2",
        "Will 2027 adjusted EPS grow through the $5.20 2026 guide, or only through the $4.70 jump-off after stripping $0.50 of 2026 non-recur?",
        "Management said 2027 should grow versus both. Street is at $5.55. The $0.50 is $180M Marketplace plus $160M Medicare/PDP. If PDP margins reset toward 2-3% and Marketplace eAPTC attrition continues, $5.55 is the bull case inside the base. February 2027 guidance settles this.",
    ),
    (
        "3",
        "How deep is OB3 / work-requirement / legal-non-citizen Medicaid attrition in 2027 versus the 8-9% already guided for year-end 2026?",
        "Medicaid is still ~58% of KPI premium. Q3 membership 11.9M, -5% YTD, with Florida CMS already rolled off October 1. Acuity rises as healthier members leave, which is why HBR can worsen even if rates are up ~5%. If 2027 attrition is another high-single-digit, rate-matching may not cover it.",
    ),
    (
        "4",
        "Is the $6.72B FY2025 goodwill impairment the end of WellCare/Medicare write-downs, or is remaining $10.84B goodwill still at risk if MA membership is shrunk into 2027?",
        "Management is constructing a smaller MA footprint to expand margin. Shrinking a book that was just impaired can trigger another charge. Remaining goodwill is 49% of common equity. A second impairment would not change cash but would reset the GAAP earnings and book-value narrative the 2026 rerating is built on.",
    ),
    (
        "5",
        "What is inside the GAAP vs adjusted EPS gap (Q3 GAAP -$0.14 vs adj $0.58; FY26 GAAP >$3.46 vs adj >$5.20)?",
        "Workforce/enterprise optimization is $480M excluded from adjusted, mostly taken in Q3 with a Q4 tail into early 2027. Merger/restructuring TTM $397M. Asset-sale losses TTM $516M. If 'adjusted' becomes the permanent earnings definition, owner earnings are closer to GAAP. Need a bridge that does not keep adding back cash costs.",
    ),
    (
        "6",
        "Can Marketplace hold a 5% pre-tax margin in 2027 after eAPTC expiration and program-integrity attrition?",
        "Management called 5% PTI an 'incredible turnaround' from summer 2025 and expects slight 2027 market contraction with membership TBD pending open enrollment. Ambetter pricing is set for margin over growth. A bronze-mix or acuity surprise in Q1 2027 is the fastest way the $5.55 Street number breaks.",
    ),
    (
        "7",
        "Is Medicare Advantage breakeven in 2026 durable once Stars (released this month, impacting 2028) and a smaller 2027 footprint are in the book?",
        "Breakeven a year early is the quality signal. Stars affect 2028, not 2027, so 2027 MA profit is a bid-and-benefit construction problem, not a Stars problem. If the 2027 bid undershoots trend, breakeven reverses. Need 2027 MA membership, bid margin, and whether PDP outperformance (majority of Q3 Medicare beat) is being mistaken for MA health.",
    ),
    (
        "8",
        "What happens to PDP margins in 2027 after mid-to-high 3% 2026 PTI that management already flags as non-recurring in part?",
        "$160M of the $0.50 2026 non-recur is Medicare/PDP. Direct subsidy is up, which helps premium yield, but management said 2027 PDP margins reset lower, at least initially. Street $5.55 assumes the reset is modest. A return to 2% PTI on a ~9M member PDP book is material.",
    ),
    (
        "9",
        "When do buybacks restart, at what price versus $44.87 book, and with what parent cash?",
        "TTM buybacks $59M vs $3.12B in FY2024. Treasury stock -$9.44B. Restarting buybacks at $70 against $175M parent cash means either upstreaming restricted cash (regulator-constrained) or issuing holdco debt. Buybacks funded by regulated-sub dividends are a capital-adequacy question, not a capital-return question.",
    ),
    (
        "10",
        "Is the CFO transition (Asher to Neczypor) a continuity handoff or a reset of 2027 guidance philosophy?",
        "Neczypor has been alongside Asher for two months and will be on the February call. Guidance tone, add-back policy, and 2027 margin targets could shift. Restoration stories are fragile around a CFO change because the market is underwriting the guide, not trailing GAAP.",
    ),
    (
        "11",
        "What is state concentration in Medicaid, and which states start work requirements in Q4 2026 / 2027?",
        "New York EP program changes already mixed. California removing Unsatisfactory Immigration Status from managed care is a named 2027 headwind. One unnamed state starts work requirements in Q4. A Florida-sized contract loss has already hit. Need the top-10 state PMPM and reprocurement calendar.",
    ),
    (
        "12",
        "Are behavioral health, home health, and high-cost drugs actually stabilizing, or is Q3 'in line' just the 50 bp rate cushion being spent?",
        "Management said YoY BH trend has stabilized and home health is beginning to. They also said Q3 chewed up some of the 50 bp back-half cushion. If Q4 acuity from the 8-9% membership drop spends the rest, 2027 HBR improvement is a hope, not a run-rate.",
    ),
    (
        "13",
        "Why did unpaid claims rise to $21.5B and DCP to 48 days, and is reserve adequacy conservative after 2025's medical-cost shock?",
        "One extra day of claims payable on this book is hundreds of millions. Prior-period development is the quiet earnings quality tell in managed care. Need favorable vs adverse development in the 10-Q, not just DCP.",
    ),
    (
        "14",
        "What drove TTM asset-sale losses of $516M and merger/restructuring of $397M, and is the portfolio still being pruned?",
        "FY2025 also had $511M asset-sale loss and $75M writedown. Divestiture accounting can hide both value realization and value destruction. Remaining 'Other' KPI revenue is $4.8B TTM, down from $11.5B in FY2022 — the portfolio has already been shrunk.",
    ),
    (
        "15",
        "Does Key Stats vs income-statement share count, or EV vs MC, hide convertibles, minority interest, or leases?",
        "Shares 495.07M outstanding = implied. MI only $100M. No preferred. Debt agrees across Yahoo and the BS. Leases are not the SFM problem here. The live discrepancy is cash: $23.59B vs $20.70B vs $175M parent. That is the capital-structure question.",
    ),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
        if col == 2:
            ws.row_dimensions[row].height = 52
widths(ws, [6, 92, 110])

# 6. Sources
ws = wb.create_sheet("Sources")
title(
    ws,
    "Sources — Centene Corporation (CNC)",
    3,
    "Numbered. Accessed November 6-7, 2026. SEC API blocked; no EDGAR full-text pull.",
)
header(ws, 3, ["#", "Source", "URL"])
sources = [
    ("1", "StockAnalysis overview — price, MC, PE, PT, earnings date", "https://stockanalysis.com/stocks/cnc/"),
    ("2", "StockAnalysis statistics — EV, shares, debt, cash, FCF, beta, short, margins", "https://stockanalysis.com/stocks/cnc/statistics/"),
    ("3", "StockAnalysis financials overview — revenue, op. income, NI, EPS, FCF, segments, cash/debt", "https://stockanalysis.com/stocks/cnc/financials/"),
    ("4", "StockAnalysis income statement", "https://stockanalysis.com/stocks/cnc/financials/income-statement/"),
    ("5", "StockAnalysis balance sheet", "https://stockanalysis.com/stocks/cnc/financials/balance-sheet/"),
    ("6", "StockAnalysis cash flow statement", "https://stockanalysis.com/stocks/cnc/financials/cash-flow-statement/"),
    ("7", "StockAnalysis forecast — PT, ratings mix, FY2026/FY2027 estimates", "https://stockanalysis.com/stocks/cnc/forecast/"),
    ("8", "StockAnalysis company profile", "https://stockanalysis.com/stocks/cnc/company/"),
    ("9", "StockAnalysis Q3 FY2026 earnings-call transcript", "https://stockanalysis.com/stocks/cnc/transcripts/659096-q3-2026/"),
    ("10", "Yahoo Finance quote", "https://finance.yahoo.com/quote/CNC/"),
    ("11", "Yahoo Finance profile (identity, executives, events)", "https://finance.yahoo.com/quote/CNC/profile/"),
    ("12", "Yahoo Finance Key Statistics", "https://finance.yahoo.com/quote/CNC/key-statistics/"),
    ("13", "Yahoo Finance Analysis — EPS/revenue estimates, revisions, history", "https://finance.yahoo.com/quote/CNC/analysis/"),
    ("14", "CNBC US10Y Treasury yield", "https://www.cnbc.com/quotes/US10Y"),
    ("15", "Centene Q3 2026 earnings release (PR Newswire)", "https://www.prnewswire.com/news-releases/centene-corporation-reports-third-quarter-2026-results-302920048.html"),
    ("16", "This workbook and companion research/projection files", "models/[2026-11-07] Centene Model.xlsx; research/CNC.md; projections/CNC.md"),
]
for row, values in enumerate(sources, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [6, 88, 110])

wb.save(OUT)
print(f"Wrote {OUT}")

wb2 = load_workbook(OUT)
assert wb2.sheetnames == ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert wb2["Valuation"]["B6"].value == PRICE
assert str(wb2["Scenarios"]["B11"].value).startswith("$")
print("Workbook reopen OK:", wb2.sheetnames)
