#!/usr/bin/env python3
"""Build the Sprouts Farmers Market six-sheet valuation workbook."""
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


OUT = Path(__file__).with_name("[2026-11-05] Sprouts Farmers Market Model.xlsx")

# Quote: StockAnalysis / Nasdaq close November 4, 2026. Model date November 5, 2026.
# Q3 FY2026 (period ended September 27, 2026) already public (released October 28).
# USD millions unless noted.
PRICE = 54.40
SHARES = 92.23  # millions, StockAnalysis shares outstanding
MARKET_CAP = PRICE * SHARES  # 5,017.3
CASH = 228.66
TOTAL_DEBT = 2236.0  # standardized; almost entirely operating leases
ENTERPRISE_VALUE = MARKET_CAP + TOTAL_DEBT - CASH
NET_DEBT = TOTAL_DEBT - CASH
BOOK_EQUITY = 1529.0
LT_DEBT_FINANCIAL = 118.56  # long-term borrowings excluding leases
LT_LEASES = 1921.0
CURRENT_LEASES = 196.06

TTM_REVENUE = 9108.0
TTM_GP = 3536.0
TTM_EBIT = 665.34
TTM_EBITDA = 844.73
TTM_NI = 496.17
TTM_EPS = 5.21
TTM_OCF = 693.65
TTM_CAPEX = 356.40
TTM_FCF = 337.26
TTM_SBC = 28.52
TTM_DA_CF = 339.29
TTM_INTEREST = 3.46
TTM_TAX = 168.40
TTM_BUYBACKS = 433.39
GROSS_MARGIN = 38.82
OP_MARGIN = 7.31
FCF_MARGIN = 3.70
ETR = 25.34
BVPS = 16.50

FY21_REV, FY22_REV, FY23_REV, FY24_REV, FY25_REV = 6100.0, 6404.0, 6837.0, 7719.0, 8806.0
FY21_NI, FY22_NI, FY23_NI, FY24_NI, FY25_NI = 244.16, 261.16, 258.86, 380.60, 523.67
FY21_EPS, FY22_EPS, FY23_EPS, FY24_EPS, FY25_EPS = 2.10, 2.39, 2.50, 3.75, 5.31
FY21_FCF, FY22_FCF, FY23_FCF, FY24_FCF, FY25_FCF = 262.42, 247.32, 239.76, 414.84, 467.73
FY21_EBIT, FY22_EBIT, FY23_EBIT, FY24_EBIT, FY25_EBIT = 338.84, 366.43, 386.68, 532.70, 686.16

# Street (StockAnalysis / S&P Global, last checked November 2, 2026). EPS is
# non-GAAP adjusted. FY2027/FY2028 later years are Pro-gated on the public page;
# overview still printed FY2027 revenue $9.78B and EPS $4.60.
FY26_REV_CONS = 9330.0
FY26_EPS = 5.06  # 13 analysts, non-GAAP
FY26_NI = 474.48
FY26_EBIT_CONS = 622.59
FY26_FCF_CONS = 377.52
FY26_EPS_GUIDE = 4.80  # company FY26 EPS print from post-Q3 outlook
FY26_SALES_GROWTH_52W = 0.043
FY26_COMPS_GUIDE = -0.017
FY26_EBIT_GUIDE_52W = 605.0
FY26_WEEK53_SALES = 190.0
FY26_WEEK53_EBIT = 20.0
FY26_WEEK53_EPS = 0.16
FY27_REV_CONS = 9780.0
FY27_EPS = 4.60
ANALYST_AVG_PT = 61.00
ANALYST_MED_PT = 58.00
ANALYST_LOW_PT = 45.00
ANALYST_HIGH_PT = 114.00
N_ANALYSTS = 16
N_FY26_ANALYSTS = 13

# Primary lens: FY2031 EPS x exit P/E. Lease-adjusted net debt is 6.0x TTM FCF
# (gray zone). FCF multiples would crush equity value because $2.01B of "debt"
# is mostly store leases, not cash interest-bearing borrowings. Financial net
# cash is about $110M. Do not use FCF multiples as the scenario engine.
SCENARIOS = {
    "Bear": {
        "rev_cagr": 0.025,
        "eps": 3.90,
        "pe": 9.0,
        "fcf_margin": 0.025,
        "weight": 0.30,
    },
    "Base": {
        "rev_cagr": 0.050,
        "eps": 5.10,
        "pe": 12.0,
        "fcf_margin": 0.040,
        "weight": 0.50,
    },
    "Bull": {
        "rev_cagr": 0.070,
        "eps": 5.60,
        "pe": 13.0,
        "fcf_margin": 0.050,
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
assert 20 < SCENARIOS["Base"]["target"] < 120
assert 30 < SCENARIOS["Bull"]["target"] < 150
assert abs(SCENARIOS["Base"]["target"] - ANALYST_AVG_PT) / ANALYST_AVG_PT < 0.20
assert weighted_value > 0
assert NET_DEBT / TTM_FCF > 3  # gray-zone flag; FCF not primary

rf = 4.845  # CNBC US10Y, November 4, 2026 10:01 PM EST
erp = 5.00
beta = 0.79  # StockAnalysis 5Y
cost_equity = rf + beta * erp
# Cash interest is $3.0M on $2.24B of standardized debt because nearly all of
# the balance is operating leases. Use a 5.5% lease-equivalent pretax cost.
pretax_debt_cost = 5.50
tax_rate = ETR
equity_weight = MARKET_CAP / (MARKET_CAP + TOTAL_DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * cost_equity + debt_weight * pretax_debt_cost * (1 - tax_rate / 100)

print(f"MC ${MARKET_CAP:.1f}M  EV ${ENTERPRISE_VALUE:.1f}M  Net debt ${NET_DEBT:.1f}M")
print(f"Ke {cost_equity:.2f}%  E-weight {equity_weight*100:.1f}%  WACC {wacc:.2f}%")
print(
    f"Bear ${SCENARIOS['Bear']['target']:.2f}  "
    f"Base ${SCENARIOS['Base']['target']:.2f}  "
    f"Bull ${SCENARIOS['Bull']['target']:.2f}"
)
print(f"Weighted FV ${weighted_value:.2f}  upside {total_upside*100:.1f}%")
print(f"Analyst avg PT ${ANALYST_AVG_PT:.2f}  net_debt/FCF {NET_DEBT/TTM_FCF:.1f}x")
print(f"Bear vs price {SCENARIOS['Bear']['target']/PRICE-1:.1%}  Base vs PT {(SCENARIOS['Base']['target']/ANALYST_AVG_PT-1):.1%}")

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
    "Sprouts Farmers Market, Inc. (SFM) — Valuation",
    4,
    "Quote date: November 4, 2026 close $54.40 | Model date: November 5, 2026 | Q3 FY2026 already reported October 28, 2026",
)
facts = [
    ("Company", "Sprouts Farmers Market, Inc.", "Healthy grocery retailer; HQ Phoenix, AZ; 504 stores in 25 states at Sep 27, 2026; 36,000 employees; CEO listed Jack Sinclair, Nick Konat stepping into CEO role on the Q3 call"),
    ("Ticker", "NASDAQ: SFM", "Consumer Staples / Grocery Stores; IPO Aug 1, 2013; CIK 0001575515; fiscal year ends late December (FY2026 is a 53-week year)"),
    ("Price", PRICE, "StockAnalysis / Nasdaq close November 4, 2026 $54.40; after-hours $55.04; 52-week range $47.35-$94.89; -35.1% in 52 weeks"),
    ("Shares outstanding (M)", SHARES, "StockAnalysis 92.23M; -4.30% YoY; float 91.49M; TTM diluted average ~95M"),
    ("Market capitalization ($M)", MARKET_CAP, "Price x shares $5,017M; StockAnalysis printed $5.02B at this quote"),
    ("Total debt ($M)", TOTAL_DEBT, "StockAnalysis standardized $2.24B at Sep 27, 2026. Financial LT debt $119M; current leases $196M; LT leases $1,921M"),
    ("Cash ($M)", CASH, "Cash and equivalents $228.66M at Sep 27, 2026; Q3 call also cited $22M letters of credit"),
    ("Enterprise value ($M)", ENTERPRISE_VALUE, "Market cap + standardized debt - cash. Yahoo printed $6.85B; StockAnalysis $7.02B. Difference is quote timing plus lease gross-up."),
    ("Net debt ($M)", NET_DEBT, "EV - MC. $21.76/share. 6.0x TTM FCF, 2.4x TTM EBITDA. Financial net cash is ~$110M if leases are excluded."),
    ("Book value / share", BVPS, "Equity $1.53B / 92.67M shares on the balance sheet; P/B 3.30x"),
    ("Dividend", "None", "No dividend. Capital return is 100% buybacks ($433M TTM, 62% of OCF)."),
    ("Primary valuation lens", "FY2031 EPS x exit P/E", "Forward P/E is primary because lease-adjusted net debt is 6.0x TTM FCF (gray zone). FCF multiples are a cross-check only. Trailing P/E is a peak-margin print."),
    ("Stance", "Watch", "Fallen-angel grocer: 43% off the 52-week high after a Q3 miss, negative comps, and a January pricing reset. Probability-weighted FV is near the quote. Next catalyst is Q4 / FY2026 results (expected late February 2027), not the already-printed Q3."),
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
    ("Trailing P/E", "10.44x", "TTM diluted EPS $5.21. Compressed from ~22x when the stock was near $95 in late 2025. Peak-margin denominator."),
    ("Forward P/E (FY2026e)", "10.75x", "Street non-GAAP EPS $5.06 (13 analysts). Company post-Q3 guide is $4.80, which is 11.33x."),
    ("Forward P/E (FY2027e)", "11.83x", "Street EPS $4.60, down 9.2% vs FY2026e. This is the number the market is underwriting at $54.40."),
    ("P/S (TTM)", "0.55x", "TTM revenue $9.11B. Grocery-store range. Forward P/S 0.51x on $9.33B FY2026e."),
    ("P/FCF (TTM)", "14.88x", "TTM FCF $337M after a capex spike. FY2025 P/FCF on $468M would have been ~10.7x."),
    ("EV/FCF (TTM)", "20.83x", "Lease-grossed EV $7.02B / $337M. Distorted by store leases. Not the primary multiple."),
    ("EV/Sales", "0.77x", "EV $7.02B / TTM $9.11B."),
    ("EV/EBITDA", "8.32x", "EV $7.02B / TTM EBITDA $845M. Reasonable for a grocer if EBITDA holds. Q4 guide implies near-term compression."),
    ("EV/EBIT", "10.56x", "EV / TTM EBIT $665M. Company FY2026 52-week EBIT guide is $605M."),
    ("P/B", "3.30x", "MC $5.02B / equity $1.53B. ROE 33.5% supports a premium to book until margins reset."),
    ("FCF yield (TTM)", "6.72%", "$337M / $5.02B. Depressed by $356M capex (42-store year). OCF yield is 13.8%."),
    ("52-week range", "$47.35 - $94.89", "Close is 13% above the low and 43% below the high. Post-Q3 print tagged $48.05 intraday."),
]
for row, values in enumerate(metrics, 19):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [28, 18, 110])
ws.row_dimensions[4].height = 48
ws.row_dimensions[16].height = 48

# 2. WACC
ws = wb.create_sheet("WACC")
title(
    ws,
    "WACC — CAPM",
    4,
    "Selected WACC uses lease-equivalent pretax debt cost. Cash interest on financial borrowings is de minimis.",
)
header(ws, 3, ["Component", "Value", "Source / Notes"])
wacc_rows = [
    ("Risk-free rate (10Y US)", f"{rf:.3f}%", "CNBC US10Y quote 4.845% at 10:01 PM EST November 4, 2026; day low 4.845%, prior close 4.892%"),
    ("Beta (5Y monthly)", f"{beta:.2f}", "StockAnalysis statistics. Defensive grocer; below 1.0. Yahoo matches 0.79."),
    ("Equity risk premium", f"{erp:.2f}%", "Standard 5% assumption"),
    ("Cost of equity", f"{cost_equity:.2f}%", f"{rf:.3f}% + {beta:.2f} x {erp:.2f}%"),
    ("Market cap ($M)", f"{MARKET_CAP:,.1f}", "Price x 92.23M shares"),
    ("Total debt ($M)", f"{TOTAL_DEBT:,.1f}", "Standardized. Financial LT debt $119M; remainder is current and long-term operating leases"),
    ("Cash ($M)", f"{CASH:,.2f}", "September 27, 2026"),
    ("Net debt ($M)", f"{NET_DEBT:,.1f}", "Lease-adjusted. Financial net cash ~$110M if leases are excluded."),
    ("Total capitalization ($M)", f"{MARKET_CAP + TOTAL_DEBT:,.1f}", "MC + standardized debt"),
    ("Equity weight", f"{equity_weight*100:.1f}%", "MC / (MC + Debt)"),
    ("Debt weight", f"{debt_weight*100:.1f}%", "Debt / (MC + Debt)"),
    ("Pre-tax cost of debt", f"{pretax_debt_cost:.2f}%", "Lease-equivalent. TTM cash interest paid $3.0M on $2.24B standardized debt is 0.13% and is not an economic cost of capital."),
    ("Tax rate (TTM effective)", f"{tax_rate:.2f}%", "TTM tax $168.40M / pretax $664.56M. Company FY2026 guide ~25%."),
    ("WACC", f"{wacc:.2f}%", "Equity-weighted CAPM plus after-tax lease-equivalent debt cost. StockAnalysis prints 5.98%; this model is more conservative on lease cost."),
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
    "Primary engine is FY2031 EPS x exit P/E. FCF multiples are shown as a cross-check only. Lease-adjusted net debt of $2.01B is 6.0x TTM FCF, so FCF x multiple minus net debt would produce economically meaningless equity values.",
)
header(ws, 3, ["Item", "Bear", "Base", "Bull", "Notes"])
s = SCENARIOS
rows = [
    ("Revenue CAGR (5Y)", f"{s['Bear']['rev_cagr']:.1%}", f"{s['Base']['rev_cagr']:.1%}", f"{s['Bull']['rev_cagr']:.1%}", "Bridges from TTM $9.11B. Street FY2026 $9.33B / FY2027 $9.78B already imply ~4-6% near-term growth from new stores against negative comps."),
    ("TTM revenue ($M)", f"{TTM_REVENUE:,.0f}", f"{TTM_REVENUE:,.0f}", f"{TTM_REVENUE:,.0f}", "Period ended September 27, 2026"),
    ("Terminal revenue FY2031 ($M)", f"{s['Bear']['term_rev']:,.0f}", f"{s['Base']['term_rev']:,.0f}", f"{s['Bull']['term_rev']:,.0f}", "TTM x (1+CAGR)^5"),
    ("FY2026e EPS (street, non-GAAP)", f"{FY26_EPS:.2f}", f"{FY26_EPS:.2f}", f"{FY26_EPS:.2f}", "13 analysts. Company post-Q3 guide is $4.80. 53rd week adds $0.16."),
    ("FY2027e EPS (street)", f"{FY27_EPS:.2f}", f"{FY27_EPS:.2f}", f"{FY27_EPS:.2f}", "Street already cuts 9% as the January pricing reset and affordability investments hit the P&L."),
    ("Terminal EPS FY2031 ($)", f"{s['Bear']['eps']:.2f}", f"{s['Base']['eps']:.2f}", f"{s['Bull']['eps']:.2f}", "Bear: margin stuck near the 5% EBIT floor. Base: earnings recover to ~FY2025. Bull: comps turn positive and EBIT margin rebuilds toward 6.5-7%."),
    ("Exit P/E", f"{s['Bear']['pe']:.1f}x", f"{s['Base']['pe']:.1f}x", f"{s['Bull']['pe']:.1f}x", "Grocery range. KR-type floor ~9x; quality specialty grocer 12-14x. Not the 20x+ the stock held in 2025."),
    ("Target price", f"${s['Bear']['target']:.2f}", f"${s['Base']['target']:.2f}", f"${s['Bull']['target']:.2f}", "Terminal EPS x exit P/E. Share count held at 92.23M; buybacks are upside not in the price."),
    ("Upside vs $54.40", f"{s['Bear']['upside']:.1%}", f"{s['Base']['upside']:.1%}", f"{s['Bull']['upside']:.1%}", "Bear must be below the quote. Base is calibrated to the $61 average Street PT."),
    ("Probability weight", f"{s['Bear']['weight']:.0%}", f"{s['Base']['weight']:.0%}", f"{s['Bull']['weight']:.0%}", "30/50/20. Traffic has not inflected and a new CEO is resetting price. Bull is not the base."),
    ("Weighted value / share", "", "", f"${weighted_value:.2f}", "0.30 x 35.10 + 0.50 x 61.20 + 0.20 x 72.80"),
    ("Current price", "", "", f"${PRICE:.2f}", "November 4, 2026 close"),
    ("Probability-weighted upside", "", "", f"{total_upside:.1%}", "Near flat. Watch, not Own."),
    ("", "", "", "", ""),
    ("FCF cross-check (not primary)", "", "", "", "Shown so the gray-zone math is explicit, not used for the target."),
    ("Terminal FCF margin", f"{s['Bear']['fcf_margin']:.1%}", f"{s['Base']['fcf_margin']:.1%}", f"{s['Bull']['fcf_margin']:.1%}", "TTM FCF margin 3.70% after the 42-store capex year. FY2025 was 5.31%."),
    ("Terminal FCF ($M)", f"{s['Bear']['term_fcf']:,.0f}", f"{s['Base']['term_fcf']:,.0f}", f"{s['Bull']['term_fcf']:,.0f}", "Term rev x FCF margin"),
    ("Implied EV at 10x FCF ($M)", f"{s['Bear']['term_fcf']*10:,.0f}", f"{s['Base']['term_fcf']*10:,.0f}", f"{s['Bull']['term_fcf']*10:,.0f}", "10x is a mid grocer FCF multiple"),
    ("Equity after $2,007M net debt ($M)", f"{s['Bear']['term_fcf']*10 - NET_DEBT:,.0f}", f"{s['Base']['term_fcf']*10 - NET_DEBT:,.0f}", f"{s['Bull']['term_fcf']*10 - NET_DEBT:,.0f}", "This is why FCF is not the engine: lease gross-up eats most of the EV at compressed multiples."),
]
for row, values in enumerate(rows, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [36, 16, 16, 16, 110])
ws.row_dimensions[2].height = 48

# 4. Actuals Source Audit
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "Actuals Source Audit — Sprouts Farmers Market (SFM)", 5, "Every figure below was read from a public page on November 4-5, 2026. SEC API is blocked in this environment.")
header(ws, 3, ["Item", "Value", "As of", "Source", "Notes"])
audit = [
    ("Stock price", "$54.40", "2026-11-04 close", "https://stockanalysis.com/stocks/sfm/", "After-hours $55.04. Yahoo close $54.40 same session."),
    ("Market cap", "$5.02B", "2026-11-04", "https://stockanalysis.com/stocks/sfm/", "Price x 92.23M = $5,017M."),
    ("Enterprise value", "$7.02B", "2026-11-04", "https://stockanalysis.com/stocks/sfm/statistics/", "Yahoo Key Stats printed $6.85B at a $4.84B MC snapshot."),
    ("Shares outstanding", "92.23M", "2026-11-04", "https://stockanalysis.com/stocks/sfm/statistics/", "Filing-date shares 92.23M; BS total common 92.67M; TTM diluted avg ~95M. Use 92.23M for per-share."),
    ("Shares change YoY", "-4.30%", "2026-11-04", "https://stockanalysis.com/stocks/sfm/statistics/", "Buybacks. QoQ -0.79%."),
    ("Float / short", "91.49M / 13.37% of shares", "short as of 2026-10-15", "https://stockanalysis.com/stocks/sfm/statistics/", "Short 12.33M shares; 13.48% of float; days to cover 5.59. Yahoo short % of float 17.28% — flag discrepancy."),
    ("Beta", "0.79", "5Y monthly", "https://stockanalysis.com/stocks/sfm/statistics/", "Yahoo matches."),
    ("Trailing P/E", "10.44x", "2026-11-04", "https://stockanalysis.com/stocks/sfm/", "Yahoo trailing P/E 10.03x on $5.23 diluted EPS."),
    ("Forward P/E", "12.23x", "2026-11-04", "https://stockanalysis.com/stocks/sfm/", "Yahoo Key Stats forward P/E 13.09x. Difference is which EPS year is in the denominator."),
    ("TTM revenue", "$9,108M", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/", "+5.25% vs prior TTM. Perishables $5,179M / non-perishables $3,929M."),
    ("FY2025 revenue", "$8,806M", "FY ended 2025-12-28", "https://stockanalysis.com/stocks/sfm/financials/", "+14.08% vs FY2024 $7,719M."),
    ("FY2024 revenue", "$7,719M", "FY ended 2024-12-29", "https://stockanalysis.com/stocks/sfm/financials/", "+12.90%."),
    ("FY2023 revenue", "$6,837M", "FY ended 2023-12-31", "https://stockanalysis.com/stocks/sfm/financials/", "+6.76%."),
    ("FY2022 revenue", "$6,404M", "FY ended 2023-01-01", "https://stockanalysis.com/stocks/sfm/financials/", "+4.99%."),
    ("FY2021 revenue", "$6,100M", "FY ended 2022-01-02", "https://stockanalysis.com/stocks/sfm/financials/", "-5.70% post-COVID."),
    ("TTM gross profit", "$3,536M / 38.82%", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/income-statement/", "FY2025 GM 39.03% was the peak. Q3 2026 GM 38.2%."),
    ("TTM operating income", "$665.34M / 7.31%", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/income-statement/", "Down from FY2025 $686.16M / 7.79%."),
    ("TTM net income", "$496.17M / 5.45%", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/income-statement/", "Down 3.37% vs prior TTM. FY2025 NI $523.67M."),
    ("TTM diluted EPS", "$5.21", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/income-statement/", "Basic $5.24. FY2025 diluted $5.31. Yahoo Key Stats $5.23."),
    ("TTM EBITDA", "$844.73M / 9.27%", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/income-statement/", "D&A for EBITDA $179.39M. CF statement D&A is $339.29M including lease depreciation."),
    ("TTM interest expense", "$3.46M", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/income-statement/", "Interest coverage 192x. Lease cost sits in occupancy, not interest."),
    ("TTM tax / ETR", "$168.40M / 25.34%", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/statistics/", "FY2025 ETR 23.97%. Company FY2026 guide ~25%."),
    ("TTM OCF", "$693.65M", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/cash-flow-statement/", "-1.24% vs prior. FY2025 OCF $716M."),
    ("TTM capex", "$356.40M", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/cash-flow-statement/", "Up from FY2025 $248.27M. 42-store year. Investing CF equals capex — no acquisition gap."),
    ("TTM FCF", "$337.26M / 3.70%", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/cash-flow-statement/", "-26.29% vs prior. Capex-cycle trough, not an OCF collapse. FCF/share $3.54."),
    ("TTM buybacks", "$433.39M", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/cash-flow-statement/", "62% of OCF. FY2025 buybacks $474.02M. No dividend."),
    ("TTM SBC", "$28.52M", "TTM to 2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/cash-flow-statement/", "0.31% of revenue. Not a distortion."),
    ("Cash", "$228.66M", "2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/balance-sheet/", "Down 29% YoY. Working capital -$23.28M."),
    ("Total debt (standardized)", "$2,236M", "2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/balance-sheet/", "LT debt $118.56M + LT leases $1,921M + current leases $196.06M."),
    ("Net debt", "$2,007M / -$21.76/sh", "2026-09-27", "https://stockanalysis.com/stocks/sfm/statistics/", "6.0x TTM FCF. Yahoo total debt $2.24B matches."),
    ("Equity / BVPS", "$1,529M / $16.50", "2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/balance-sheet/", "Goodwill $381.75M unchanged since FY2024. Tangible book $10.14."),
    ("Inventory", "$440.43M", "2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/balance-sheet/", "Turnover 13.26x. Current ratio 0.97, quick 0.34 — grocer-normal."),
    ("Goodwill / intangibles", "$381.75M / $208.22M", "2026-09-27", "https://stockanalysis.com/stocks/sfm/financials/balance-sheet/", "Stable. No recent acquisition spike."),
    ("FY2026e revenue", "$9.33B", "forecast page 2026-11-02", "https://stockanalysis.com/stocks/sfm/forecast/", "13 analysts. High $9.4B / low $9.0B. +5.96% vs FY2025, includes 53rd week."),
    ("FY2026e EPS", "$5.06 non-GAAP", "forecast page 2026-11-02", "https://stockanalysis.com/stocks/sfm/forecast/", "High $5.56 / low $4.80. Company guide $4.80. Street still above the company number."),
    ("FY2026e EBIT / NI / FCF", "$623M / $474M / $378M", "forecast page 2026-11-02", "https://stockanalysis.com/stocks/sfm/forecast/", "Company 52-week EBIT guide $605M + $20M 53rd week = $625M, in line."),
    ("FY2027e revenue / EPS", "$9.78B / $4.60", "overview + forecast 2026-11-02", "https://stockanalysis.com/stocks/sfm/forecast/", "FY2027-28 tables are Pro-gated. Overview still printed next-year revenue $9.78B and EPS $4.60 (-9.15%)."),
    ("Company FY2026 guide (52-week)", "sales +4.3%, comps -1.7%, EBIT $605M, 42 net new stores, capex ~$310M, tax 25%", "Q3 FY2026 call 2026-10-28", "https://stockanalysis.com/stocks/sfm/transcripts/718715-q3-2026/", "53rd week +$190M sales, +$20M EBIT, +$0.16 EPS. Q4 EPS guide $0.47-$0.51. Q4 comps (2%)-(4%). EBIT margin to remain above 5%."),
    ("Q3 FY2026 actuals", "sales $2.3B +5%, comps -0.9%, EPS $1.21 vs $1.23, EBIT $153M, NI $113M, GM 38.2%", "released 2026-10-28", "https://stockanalysis.com/stocks/sfm/transcripts/718715-q3-2026/", "Cyclospora -60 bps of comps. Transactions -3.3%, basket +2.5%. Street miss on sales ($2.33B) and EPS."),
    ("Store count", "504 stores / 25 states", "2026-09-27", "Q3 call", "15 openings, 1 closure in Q3. YTD 27 net new. Pipeline >105 executed leases, >160 approved. 42 net new still expected in 2026."),
    ("E-commerce / private brand", "e-comm +12% and >16% of sales; Sprouts Brand ~26% of sales", "Q3 FY2026", "Q3 call", "Shipt added as fourth e-comm platform in October 2026."),
    ("Analyst PT / rating", "avg $61 / median $58 / low $45 / high $114; Buy, 16 analysts", "2026-11-02", "https://stockanalysis.com/stocks/sfm/forecast/", "Post-Q3 cuts: Jefferies $95→$63, GS $94→$58, WF $100→$60, JPM $90→$58, Barclays $100→$65, BMO $80→$45, RBC $111→$49 and downgrade to Sector Perform. Oct mix 5 Strong Buy / 2 Buy / 7 Hold / 1 Sell / 1 Strong Sell."),
    ("10Y Treasury", "4.845%", "2026-11-04 22:01 ET", "https://www.cnbc.com/quotes/US10Y", "Used for WACC."),
    ("Next earnings", "Q4 / FY2026, expected late February 2027", "2026-11-04", "StockEvents / company calendar", "Q3 is already public. Do not treat October 28 as a future catalyst. StockEvents listed Feb 25, 2027."),
    ("Employees / HQ", "36,000 / Phoenix, AZ", "2026-11-04", "https://stockanalysis.com/stocks/sfm/company/", "CEO listed Jack Sinclair; President/COO Nicholas Konat; CFO Curtis Valentine. Founded 2002 (roots 1943)."),
]
for row, values in enumerate(audit, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
widths(ws, [34, 42, 22, 70, 95])

# 5. Questions
ws = wb.create_sheet("Questions")
title(ws, "Open Questions — Sprouts Farmers Market (SFM)", 3, "Numbered. Each item is a live underwriting issue, not a template leftover.")
header(ws, 3, ["#", "Question", "Why it matters"])
questions = [
    ("1", "Will comparable-store traffic inflect after the January 2027 national pricing reset, or does the 3.3% Q3 transaction decline mark a structural share loss to value grocers?", "This is the entire equity. New stores are working; the core fleet is not. Management said traffic, units, and frequency were not recovering even against easier compares. If Q1 FY2027 comps stay negative after the reset, the 5% EBIT-margin floor becomes the base, not the bear."),
    ("2", "How deep is the gross-margin investment, and is 90 bps of FY2026 GM deleverage the run-rate or the start of a multi-year price war?", "Company said Q4 / FY2026 GM deleverage is ~90 bps from affordability plus shrink and fuel. Nick described three buckets (Sprouts Brand entry points, conventional-produce trust builders, and broader accessibility). Breadth is the risk: a produce-price reset is recoverable; matching Kroger/Walmart on a wide basket is not."),
    ("3", "What is the CEO succession, and does Jack Sinclair remain in the chair?", "StockAnalysis still lists Jack Sinclair as CEO. On the Q3 call Nick Konat said 'as I step into the CEO role.' An October 14, 2026 8-K is on the recent-filings list. Governance and strategy ownership are not the same person the profile page implies."),
    ("4", "Is the 5% EBIT-margin 'floor' a commitment or a hope?", "Curtis said EBIT margins should remain above 5% while they invest. Q4 is seasonally the weakest quarter and the guide implies something quite a bit lower than 5% in that quarter. If FY2027 opens below 5%, the Street's $4.60 EPS is still too high."),
    ("5", "How much of the Q3 miss was cyclospora versus a weaker consumer?", "Management put cyclospora at ~60 bps of the 90 bp comp decline, peaking in August/early September and fading into Q4. That is a one-time produce event. The other 30 bps plus the 3.3% transaction drop is the consumer. Mixing the two inflates the 'transitory' argument."),
    ("6", "Can 42 net new stores and $310M of capex continue if core comps stay negative?", "New-store vintages are outperforming and year 2-4 vintages are still comping positive. That is the bull case for unit growth. It is also a cash use. TTM capex $356M already cut FCF 26%. If they keep building into a core-store traffic problem, FCF stays compressed and buybacks slow."),
    ("7", "What is inside the $2.24B of standardized total debt versus $119M of financial long-term debt?", "Almost all of it is operating leases (current $196M + LT $1,921M). Yahoo and StockAnalysis agree on the $2.24B total. EV/FCF of 21x is a lease-accounting number, not a solvency number. Cash interest is $3M. Still, lease-adjusted leverage 2.4x EBITDA and a 0.97 current ratio leave limited working-capital slack."),
    ("8", "Why is Yahoo short-interest 17.28% of float while StockAnalysis prints 13.48%?", "Same 12.33M share short position, different float definitions. Either way shorts are elevated after the Q3 print. A squeeze is not a thesis; it is a trading overlay if Q4 comps surprise."),
    ("9", "Will buybacks of ~$430-470M per year continue at $50-55, or will the board cut them to fund price investment and stores?", "TTM buybacks were 62% of OCF and 128% of FCF. That is sustainable only if capex normalizes or OCF holds. Shares are already -4.3% YoY, which is why EPS is still +1.2% TTM on -3.4% net income. Cutting the buyback removes the per-share shock absorber."),
    ("10", "Is FY2027 Street EPS of $4.60 a trough or a waystation?", "Street already has FY2026 $5.06 → FY2027 $4.60. Company has not guided 2027. If the January reset works, 2027 is the trough and 12x is cheap. If it does not, 2028 is lower still and 12x is a value trap."),
    ("11", "What is customer concentration and the middle-income mix of the 504-store fleet?", "Management said customers are migrating to value channels and that many stores sit in more middle-income areas. Sprouts' historic identity is the health enthusiast, not the fill-in grocery trip. If the core customer is trading down out of the banner, private-brand cage-free eggs will not bring them back."),
    ("12", "How durable is 26% Sprouts Brand mix as they cut price on those SKUs?", "Private brand is the margin pool. Using it as the affordability weapon lowers the mix accretive effect that funded 39% gross margins in FY2025. Need SKU-level mix and margin on Sprouts Brand vs national brand after January."),
    ("13", "What does e-commerce at 16% of sales and +12% growth do to contribution margin once Shipt is the fourth platform?", "E-comm is the bright spot and a densification tool. It is also a lower-margin, higher-labor channel. Four platforms (plus own channel) create fee leakage. Need contribution margin, not just GMV."),
    ("14", "When is Q4 / FY2026 earnings, and will 2027 guide be issued then?", "StockEvents listed February 25, 2027. Curtis said they will have a much more specific 2027 answer in February. That print is the first look at whether January pricing is a campaign or a structural reset."),
    ("15", "Does preferred stock, convertible debt, or off-balance-sheet remaining-lease residual sit outside the $2.24B?", "No preferred equity on the balance sheet. Letters of credit $22M. No Key-Stats vs balance-sheet debt discrepancy of the JOBY type — both sources print $2.24B. Still confirm the lease discount rate and remaining term in the 10-Q."),
]
for row, values in enumerate(questions, 4):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=(col == 1))
        if col == 2:
            ws.row_dimensions[row].height = 48
widths(ws, [6, 88, 110])

# 6. Sources
ws = wb.create_sheet("Sources")
title(ws, "Sources — Sprouts Farmers Market (SFM)", 3, "Numbered. Accessed November 4-5, 2026. SEC API blocked; no EDGAR full-text pull.")
header(ws, 3, ["#", "Source", "URL"])
sources = [
    ("1", "StockAnalysis overview — price, MC, PE, PT, earnings date", "https://stockanalysis.com/stocks/sfm/"),
    ("2", "StockAnalysis statistics — EV, shares, debt, cash, FCF, beta, short, margins", "https://stockanalysis.com/stocks/sfm/statistics/"),
    ("3", "StockAnalysis financials overview — revenue, GP, EBIT, NI, EPS, FCF, segments, margins", "https://stockanalysis.com/stocks/sfm/financials/"),
    ("4", "StockAnalysis income statement", "https://stockanalysis.com/stocks/sfm/financials/income-statement/"),
    ("5", "StockAnalysis balance sheet", "https://stockanalysis.com/stocks/sfm/financials/balance-sheet/"),
    ("6", "StockAnalysis cash flow statement", "https://stockanalysis.com/stocks/sfm/financials/cash-flow-statement/"),
    ("7", "StockAnalysis forecast — PT, ratings mix, FY2026/FY2027 estimates", "https://stockanalysis.com/stocks/sfm/forecast/"),
    ("8", "StockAnalysis company profile", "https://stockanalysis.com/stocks/sfm/company/"),
    ("9", "StockAnalysis Q3 FY2026 earnings-call transcript", "https://stockanalysis.com/stocks/sfm/transcripts/718715-q3-2026/"),
    ("10", "Yahoo Finance quote / profile (identity check)", "https://finance.yahoo.com/quote/SFM/profile/"),
    ("11", "Yahoo Finance Key Statistics (cross-check MC, EV, PE, debt, short)", "https://finance.yahoo.com/quote/SFM/key-statistics/"),
    ("12", "CNBC US10Y Treasury yield", "https://www.cnbc.com/quotes/US10Y"),
    ("13", "Business Wire Q3 FY2026 earnings release (page was bot-walled; figures taken from transcript and StockAnalysis news items)", "https://www.businesswire.com/news/home/20261028815125/en/Sprouts-Farmers-Market-Inc.-Reports-Third-Quarter-2026-Results/"),
    ("14", "Distill Markets 10-Q FY2026 period ended Sep 27, 2026 (assets, equity, cash, Q3 P&L cross-check)", "https://www.distillmarkets.com/company/SFM"),
    ("15", "This workbook and companion research/projection files", "models/[2026-11-05] Sprouts Farmers Market Model.xlsx; research/SFM.md; projections/SFM.md"),
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
assert wb2["Scenarios"]["B11"].value.startswith("$")
print("Workbook reopen OK:", wb2.sheetnames)
