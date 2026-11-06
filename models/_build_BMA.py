#!/usr/bin/env python3
"""Build BMA (Banco Macro S.A.) bank valuation model - 6-sheet workbook.

Bank-specific: P/B + ROE framework. FCF and EV multiples are N/A.
Argentine ADR: 1 NYSE ADR = 10 Class B shares (BYMA: BMA).
Data: StockAnalysis, Yahoo Finance, CNBC, company releases. As of 2026-11-06.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()

title_font = Font(name="Calibri", size=16, bold=True)
subtitle_font = Font(name="Calibri", size=11, italic=True)
header_font = Font(name="Calibri", size=11, bold=True)
normal_font = Font(name="Calibri", size=11)
blue_font = Font(name="Calibri", size=11, color="0000FF")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font_white = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
yellow_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
bear_fill = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")
base_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
bull_fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
wrap = Alignment(wrap_text=True, vertical="center")


def style_header_row(ws, row, cols):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center", wrap_text=True, vertical="center")


def style_data_cell(ws, row, col):
    cell = ws.cell(row=row, column=col)
    cell.font = normal_font
    cell.border = thin_border
    cell.alignment = wrap


def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# DATA — quote date 2026-11-06
# ---------------------------------------------------------------------------
as_of = "2026-11-06"
price = 57.99  # NYSE ADR close Nov 5, 2026 (StockAnalysis / Yahoo)
local_shares_mm = 639.41  # Class B shares (StockAnalysis / BS common stock par)
adr_ratio = 10.0  # 1 ADR = 10 Class B
adr_shares_mm = local_shares_mm / adr_ratio  # 63.941
mc_b = price * adr_shares_mm / 1000.0  # 3.708
equity_b = 4.25  # StockAnalysis statistics, USD book
bvps_adr = equity_b * 1000.0 / adr_shares_mm  # 66.47
pb = price / bvps_adr  # 0.872
beta = 0.41  # StockAnalysis 5Y
rfr = 0.04855  # CNBC US10Y, Nov 5 2026 ~9:30 PM EST
erp = 0.05
crp = 0.065  # Argentina country risk premium overlay
ke = rfr + erp * beta + crp  # 13.405%
kd = 0.10  # USD-equivalent wholesale debt estimate
tax = 0.3854  # TTM effective, StockAnalysis
debt_b = 1.15  # StockAnalysis stats total debt
cash_b = 2.27
net_cash_b = 1.12
e_plus_d = mc_b + debt_b
we = mc_b / e_plus_d
wd = debt_b / e_plus_d
wacc = we * ke + wd * kd * (1.0 - tax)

rev_ttm_b = 2.87
ni_ttm_m = 258.35
eps_ttm = 3.87  # StockAnalysis stated USD EPS
pe_ttm = 14.97
fwd_pe = 6.99
fwd_eps = price / fwd_pe  # 8.30
ps = 1.44
roe = 0.0707
roa = 0.0173
div = 3.67
div_yield = 0.0632
analyst_pt = 105.29
analyst_n = 9
next_earn = "2026-11-25"

# Scenarios — P/B + ROE, 5-year
bear_cagr = 0.03
base_cagr = 0.07
bull_cagr = 0.11
bear_pb = 0.60
base_pb = 0.95
bull_pb = 1.15
bear_tbv = bvps_adr * (1.0 + bear_cagr) ** 5
base_tbv = bvps_adr * (1.0 + base_cagr) ** 5
bull_tbv = bvps_adr * (1.0 + bull_cagr) ** 5
bear_px = bear_tbv * bear_pb
base_px = base_tbv * base_pb
bull_px = bull_tbv * bull_pb
w_bear, w_base, w_bull = 0.25, 0.50, 0.25
fv = w_bear * bear_px + w_base * base_px + w_bull * bull_px
up_bear = bear_px / price - 1.0
up_base = base_px / price - 1.0
up_bull = bull_px / price - 1.0
up_fv = fv / price - 1.0

assert bear_px < price, "Bear target must be below current price"

print("=== BMA BUILD CHECKS ===")
print("Price $%.2f  ADR shares %.3fM  MC $%.3fB" % (price, adr_shares_mm, mc_b))
print("BVPS $%.2f  P/B %.3fx  ROE %.2f%%  Ke %.2f%%" % (bvps_adr, pb, roe * 100, ke * 100))
print("WACC %.2f%%  We %.3f  Wd %.3f" % (wacc * 100, we, wd))
print(
    "Bear $%.2f (%.1f%%)  Base $%.2f (%.1f%%)  Bull $%.2f (%.1f%%)"
    % (bear_px, up_bear * 100, base_px, up_base * 100, bull_px, up_bull * 100)
)
print("FV $%.2f  upside %.1f%%  vs PT $%.2f" % (fv, up_fv * 100, analyst_pt))
print(
    "Bear < price: %s  Base vs PT gap %.1f%%"
    % (bear_px < price, (base_px / analyst_pt - 1) * 100)
)

# ===========================================================================
# Sheet 1: Valuation
# ===========================================================================
ws = wb.active
ws.title = "Valuation"
ws.merge_cells("A1:F1")
ws["A1"].value = "Banco Macro S.A. (NYSE: BMA) — Valuation Summary"
ws["A1"].font = title_font
ws.row_dimensions[1].height = 28

ws.merge_cells("A2:F2")
ws["A2"].value = (
    "As of 2026-11-06 | Bank framework (P/B + ROE / Forward P/E) | "
    "FCF and EV multiples N/A | 1 ADR = 10 Class B"
)
ws["A2"].font = subtitle_font

info = [
    ("Company", "Banco Macro S.A."),
    ("Date", as_of),
    ("Ticker", "NYSE: BMA (ADR); BYMA: BMA (Class B)"),
    ("Sector / Industry", "Financials / Banks — Regional (Argentina)"),
    ("Price (ADR $)", price),
    ("Class B shares (M)", local_shares_mm),
    ("ADR shares implied (M)", round(adr_shares_mm, 3)),
    ("ADR ratio", "10 Class B : 1 ADR"),
    ("Market Cap ($B)", round(mc_b, 3)),
    ("Total Equity ($B)", equity_b),
    ("BVPS — ADR ($)", round(bvps_adr, 2)),
    ("Total Debt ($B)", debt_b),
    ("Total Cash ($B)", cash_b),
    ("Net cash ($B)", net_cash_b),
    ("Enterprise Value", "N/A — deposits are operating liabilities"),
    ("Primary Valuation Lens", "P/B + ROE / Forward P/E (bank + EM overlay)"),
    ("Stance", "Watch"),
]
for i, (k, v) in enumerate(info, 3):
    ws.cell(row=i, column=1, value=k).font = header_font
    cell = ws.cell(row=i, column=2, value=v)
    cell.font = blue_font if isinstance(v, float) else normal_font
    if k in ("Price (ADR $)", "Market Cap ($B)", "BVPS — ADR ($)", "Stance"):
        cell.fill = yellow_fill

start = 22
ws.cell(row=start, column=1, value="Metric")
ws.cell(row=start, column=2, value="Value")
ws.cell(row=start, column=3, value="Comment")
style_header_row(ws, start, 3)

metrics = [
    (
        "P/B (ADR)",
        "%.2fx" % pb,
        "USD book $4.25B / 63.94M ADRs = $66.47 BVPS; 0.87x vs EM-bank 0.7-1.2x",
    ),
    (
        "Justified P/B at TTM ROE",
        "0.44x",
        "(ROE-g)/(Ke-g) with ROE 7.07%, g 2%, Ke 13.4% — current 0.87x prices ~12% ROE",
    ),
    (
        "Trailing P/E",
        "%.2fx" % pe_ttm,
        "StockAnalysis USD EPS $3.87; Yahoo shows 11.86x on $4.89 EPS — FX/share mix",
    ),
    (
        "Forward P/E",
        "%.2fx" % fwd_pe,
        "Implied FY+1 USD EPS $%.2f from StockAnalysis fwd P/E 6.99x" % fwd_eps,
    ),
    ("P/S (TTM)", "%.2fx" % ps, "TTM revenue $2.87B USD (StockAnalysis statistics)"),
    (
        "EV / Sales, EV / EBITDA, P/FCF",
        "N/A",
        "Bank: deposits are operating liabilities; FCF not the earnings lens",
    ),
    (
        "ROE (TTM)",
        "7.07%",
        "Below Ke 13.4%; Q2 2026 reported annualized 13.4%, adj 14.3%",
    ),
    (
        "ROA (TTM)",
        "1.73%",
        "High vs US regionals (~1%); Argentine NIM still elevated in disinflation",
    ),
    (
        "Beta (5Y)",
        beta,
        "StockAnalysis 0.41; Yahoo 0.43 — ADR already discounted vs sovereign vol",
    ),
    (
        "Dividend yield",
        "6.32%",
        "$3.67 trailing ADR dividend; payout 94% of stated EPS — not a safe yield",
    ),
    (
        "CET1 / Basel III",
        "28%",
        "Q2 2026; 11.5% requirement; excess capital ~ARS 4.1T / ~USD 2.7B",
    ),
    (
        "NPL ratio",
        "6.25%",
        "Q2 2026 reported; system 7.7%; consumer NPL 8.4%; coverage 95.4%",
    ),
    ("Next earnings", next_earn, "Q3 FY2026 estimated after close (StockAnalysis)"),
    (
        "Analyst avg PT",
        "$%.2f" % analyst_pt,
        "%d analysts, Buy; Yahoo avg $104.25; UBS cut to $90 on Oct 13" % analyst_n,
    ),
]
for i, (m, v, n) in enumerate(metrics, start + 1):
    ws.cell(row=i, column=1, value=m)
    ws.cell(row=i, column=2, value=v)
    ws.cell(row=i, column=3, value=n)
    for col in range(1, 4):
        style_data_cell(ws, i, col)

set_col_widths(ws, [38, 42, 92])

# ===========================================================================
# Sheet 2: WACC
# ===========================================================================
ws2 = wb.create_sheet("WACC")
ws2.merge_cells("A1:D1")
ws2["A1"].value = "BMA — WACC (CAPM + Argentina country-risk overlay)"
ws2["A1"].font = title_font
ws2.merge_cells("A2:D2")
ws2["A2"].value = "Bank WACC uses wholesale debt, not deposits. Country risk added to cost of equity."
ws2["A2"].font = subtitle_font

ws2.cell(row=3, column=1, value="Component")
ws2.cell(row=3, column=2, value="Value")
ws2.cell(row=3, column=3, value="Comment")
style_header_row(ws2, 3, 3)

wacc_rows = [
    ("Risk-Free Rate (10Y US Treasury)", rfr, "CNBC US10Y 4.855%, Nov 5 2026 ~21:30 EST"),
    ("Equity Risk Premium", erp, "Standard 5% developed-market ERP"),
    ("Beta (5Y)", beta, "StockAnalysis; Yahoo 0.43"),
    ("Country Risk Premium (Argentina)", crp, "Overlay on CAPM; Damodaran-style 6.5% — not in beta"),
    ("Cost of Equity Ke", ke, "Rf + ERP x beta + CRP = 4.855 + 2.05 + 6.50 = 13.41%"),
    ("Cost of Debt Kd", kd, "USD-equivalent estimate; Q2 avg ARS funding cost was ~19%"),
    ("Tax Rate (TTM)", tax, "StockAnalysis 38.54%; FY25 43.12%; FY24 9.31% (anomaly)"),
    ("Market Cap ($B)", round(mc_b, 3), "ADR price x Class B / 10"),
    ("Total Debt ($B)", debt_b, "StockAnalysis statistics; not deposits"),
    ("Equity Weight", round(we, 4), "MC / (MC + Debt)"),
    ("Debt Weight", round(wd, 4), "Debt / (MC + Debt)"),
    ("WACC", round(wacc, 4), "We*Ke + Wd*Kd*(1-t); secondary to P/B for banks"),
]
for i, (k, v, n) in enumerate(wacc_rows, 4):
    ws2.cell(row=i, column=1, value=k)
    cell = ws2.cell(row=i, column=2, value=v)
    cell.font = blue_font
    if k in (
        "Risk-Free Rate (10Y US Treasury)",
        "Equity Risk Premium",
        "Beta (5Y)",
        "Country Risk Premium (Argentina)",
        "Cost of Debt Kd",
    ):
        cell.fill = yellow_fill
    if isinstance(v, float) and k not in ("Market Cap ($B)", "Total Debt ($B)"):
        cell.number_format = "0.00%"
    ws2.cell(row=i, column=3, value=n)
    for col in range(1, 4):
        style_data_cell(ws2, i, col)

set_col_widths(ws2, [42, 18, 88])

# ===========================================================================
# Sheet 3: Scenarios
# ===========================================================================
ws3 = wb.create_sheet("Scenarios")
ws3.merge_cells("A1:E1")
ws3["A1"].value = "BMA — P/B + ROE Scenario Analysis (Bank / EM Framework)"
ws3["A1"].font = title_font
ws3.merge_cells("A2:E2")
ws3["A2"].value = (
    "FCF multiples N/A. Terminal price = ADR BVPS x (1+BVPS CAGR)^5 x exit P/B. "
    "1 ADR = 10 Class B."
)
ws3["A2"].font = subtitle_font

ws3.cell(row=3, column=1, value="Metric")
ws3.cell(row=3, column=2, value="Bear")
ws3.cell(row=3, column=3, value="Base")
ws3.cell(row=3, column=4, value="Bull")
ws3.cell(row=3, column=5, value="Comment")
style_header_row(ws3, 3, 5)

scen = [
    ("Framework", "P/B + ROE", "P/B + ROE", "P/B + ROE", "Bank valuation; Argentina CRP in Ke"),
    ("Revenue CAGR (5Y, USD)", "0%", "4%", "8%", "USD revenue; ARS nominal growth is inflation, not volume"),
    ("BVPS CAGR", "3%", "7%", "11%", "From current ADR BVPS $66.47"),
    ("ROE (terminal)", "5%", "12%", "18%", "TTM 7.07%; mgmt FY26 adj ~12%; 2030 target ~20%"),
    ("Exit P/B", "0.60x", "0.95x", "1.15x", "EM bank band; 0.87x today already prices ~12% ROE"),
    (
        "Terminal BVPS (5Y)",
        "$%.2f" % bear_tbv,
        "$%.2f" % base_tbv,
        "$%.2f" % bull_tbv,
        "BVPS x (1+CAGR)^5",
    ),
    (
        "Implied Price / ADR",
        "$%.2f" % bear_px,
        "$%.2f" % base_px,
        "$%.2f" % bull_px,
        "Terminal BVPS x exit P/B",
    ),
    (
        "Upside from current",
        "%.1f%%" % (up_bear * 100),
        "%.1f%%" % (up_base * 100),
        "%.1f%%" % (up_bull * 100),
        "vs $%.2f Nov 5 close" % price,
    ),
    ("", "", "", "", ""),
    ("Weight", "25%", "50%", "25%", "Probability assignment"),
    (
        "Weighted value / ADR",
        "$%.2f" % (w_bear * bear_px),
        "$%.2f" % (w_base * base_px),
        "$%.2f" % (w_bull * bull_px),
        "",
    ),
    ("Probability-Weighted FV", "", "", "$%.2f" % fv, "Sum of weighted values"),
    ("Current Price", "", "", "$%.2f" % price, "NYSE ADR close 2026-11-05"),
    ("Implied Upside (Weighted)", "", "", "%.1f%%" % (up_fv * 100), "From current price"),
    ("", "", "", "", ""),
    ("Analyst avg PT cross-check", "", "", "$%.2f" % analyst_pt, "StockAnalysis, 9 analysts, Buy"),
    (
        "Base vs analyst PT",
        "",
        "",
        "%.1f%%" % ((base_px / analyst_pt - 1) * 100),
        "Base is below street; street still ~$105 after UBS cut to $90",
    ),
    ("Yahoo PT range", "$83.93", "$104.25", "$130.59", "Yahoo Finance summary Nov 5 2026"),
]
for i, row in enumerate(scen, 4):
    for col, val in enumerate(row, 1):
        cell = ws3.cell(row=i, column=col, value=val)
        style_data_cell(ws3, i, col)
        if row[0] == "":
            continue
        if col == 2:
            cell.fill = bear_fill
        elif col == 3:
            cell.fill = base_fill
        elif col == 4:
            cell.fill = bull_fill

set_col_widths(ws3, [32, 16, 16, 16, 78])

# ===========================================================================
# Sheet 4: Actuals Source Audit
# ===========================================================================
ws4 = wb.create_sheet("Actuals Source Audit")
ws4.merge_cells("A1:E1")
ws4["A1"].value = "BMA — Actuals Source Audit"
ws4["A1"].font = title_font

ws4.cell(row=3, column=1, value="Data Point")
ws4.cell(row=3, column=2, value="Value")
ws4.cell(row=3, column=3, value="Source Page")
ws4.cell(row=3, column=4, value="Date")
ws4.cell(row=3, column=5, value="Notes")
style_header_row(ws4, 3, 5)

audit = [
    ("Stock price (ADR)", "$57.99", "StockAnalysis / Yahoo Summary", "2026-11-05", "NYSE close; 52w $56.10-$106.15; at low"),
    ("Market cap", "$3.708B", "Computed", "2026-11-06", "57.99 x 63.941M ADRs; Yahoo prints $3.708B; SA overview $4.05B is stale/local mix"),
    ("Class B shares", "639.41M", "StockAnalysis statistics / BS", "2026-11-05", "Par value line ARS 639.41; constant FY21-TTM"),
    ("ADR shares", "63.941M", "Class B / 10", "2026-11-06", "Citi DR: 10 ORD : 1 DR; Yahoo SO 62.82M / implied 71.12M — flagged"),
    ("P/B", "0.87x", "Computed from SA equity $4.25B", "2026-11-06", "SA stats printed 0.98x on a higher stale price"),
    ("Trailing P/E", "14.97x", "StockAnalysis statistics", "2026-11-05", "Yahoo 11.86x on EPS $4.89 — do not blend"),
    ("Forward P/E", "6.99x", "StockAnalysis overview", "2026-11-05", "Implied USD EPS $8.30"),
    ("Beta 5Y", "0.41", "StockAnalysis statistics", "2026-11-05", "Yahoo 0.43"),
    ("ROE TTM", "7.07%", "StockAnalysis statistics", "2026-11-05", "Yahoo highlights same 7.07%"),
    ("ROA TTM", "1.73%", "StockAnalysis statistics", "2026-11-05", ""),
    ("TTM revenue USD", "$2.87B", "StockAnalysis statistics", "2026-11-05", "ARS TTM revenue 4,258,556M; implied FX ~ARS 1,484 / USD"),
    ("TTM net income USD", "$258.35M", "StockAnalysis statistics", "2026-11-05", "ARS TTM NI 382,747M"),
    ("TTM EPS USD", "$3.87", "StockAnalysis statistics", "2026-11-05", "Yahoo $4.89; ARS TTM EPS 598.61 x 10 / FX ~ $4.03"),
    ("Dividend / yield", "$3.67 / 6.32%", "StockAnalysis overview", "2026-11-05", "Yahoo fwd $4.19 / 6.99%; payout 94%"),
    ("Ex-div date", "2026-07-06", "StockAnalysis / Yahoo profile", "2026-11-06", "Last cash dividend window"),
    ("Total cash USD", "$2.27B", "StockAnalysis statistics", "2026-11-05", "ARS cash 1,889,697M TTM"),
    ("Total debt USD", "$1.15B", "StockAnalysis statistics", "2026-11-05", "ARS debt 1,706,297M TTM; D/E 0.27"),
    ("Net cash USD", "$1.12B / $1.75 sh", "StockAnalysis statistics", "2026-11-05", "On local-share basis in SA; ADR net cash ~$17.5"),
    ("Equity USD", "$4.25B", "StockAnalysis statistics", "2026-11-05", "ARS equity TTM 6,294,591M"),
    ("TTM assets ARS", "25,756,262M", "SA balance sheet", "2026-06-30", "FY25 23,239,424M"),
    ("TTM net loans ARS", "11,679,857M", "SA balance sheet", "2026-06-30", "Gross 12,400,118M; allowance 720,261M (5.8%)"),
    ("TTM deposits ARS", "14,740,028M", "SA balance sheet", "2026-06-30", "Q2 call: ARS 14.7T, 76% of liabilities, LDR 79%"),
    ("TTM NII ARS", "3,399,243M", "SA income statement", "2026-06-30", "FY25 3,075,046M (+44% YoY)"),
    ("TTM provisions ARS", "756,662M", "SA income statement", "2026-06-30", "FY25 538,422M; FY24 142,214M — credit cost spike"),
    ("TTM pretax ARS", "622,019M", "SA income statement", "2026-06-30", "FY25 511,121M; FY23 2,477,083M inflation-year spike"),
    ("TTM tax rate", "38.54%", "SA income statement", "2026-06-30", "FY25 43.12%; FY24 9.31%; FY21 4.93%"),
    ("TTM OCF ARS", "1,891,123M", "SA cash flow", "2026-06-30", "FY25 OCF -2,055,475M — deposit/loan mix, not earnings"),
    ("FY25 FCF ARS", "-2,227,420M", "SA cash flow", "2026-12-31", "Bank FCF N/A; shown only as audit"),
    ("FY26E revenue ARS", "5.79T-5.99T", "SA forecast / Yahoo analysis", "2026-11-06", "SA 5.79T (9 an.); Yahoo 5.99T (9 an.)"),
    ("FY27E revenue ARS", "6.35T-6.55T", "SA forecast / Yahoo analysis", "2026-11-06", "Yahoo 6.55T, +9.3%"),
    ("FY26E EPS ARS", "1,182 / 12,320", "SA forecast vs Yahoo", "2026-11-06", "SA 1,182.19 (local); Yahoo 12,319.51 looks ADR-scaled x10. Do not mix."),
    ("FY27E EPS ARS (Yahoo)", "17,232", "Yahoo analysis", "2026-11-06", "4 analysts; +40% vs Yahoo FY26"),
    ("Analyst PT", "$105.29 avg", "StockAnalysis overview", "2026-11-06", "Yahoo $104.25; low $83.93 high $130.59"),
    ("Q2 26 NI", "ARS 206.8B", "PR Newswire / Q2 transcript", "2026-08-19/20", "+39% QoQ, +4% YoY; adj NI 221B, adj ROE 14.3%"),
    ("Q2 NPL / coverage", "6.25% / 95.4%", "Q2 2026 release", "2026-08-19", "Stage 3 4.1%; Stage 3 coverage 148.8%; consumer NPL 8.4%"),
    ("Q2 CET1", "28%", "Q2 2026 release", "2026-08-19", "Down from 32% on operational-RWA methodology; still highest among AR banks"),
    ("Q2 liquidity", "74% of deposits", "Q2 2026 release", "2026-08-19", "LDR 79%"),
    ("Loan growth guide", "2-5% real FY26", "Q2 call", "2026-08-20", "Cut from prior; commercial > consumer"),
    ("FY26 adj ROE guide", "~12%", "Q2 call", "2026-08-20", "Raised from ~8%; reported ROE 9-10% after restructuring"),
    ("2030 ROE ambition", "~20% nominal", "Q2 call", "2026-08-20", "Assumes single-digit inflation"),
    ("Buyback", "ARS 160B / ~45 days", "PR Newswire", "2026-10-28", "To defend value after price decline; ~USD 108M at ARS 1,484"),
    ("Banco Saenz deal", "SPA announced", "PR Newswire", "2026-03-20", "With Fintech Digital LLC; terms not fully in public pages"),
    ("10Y Treasury", "4.855%", "CNBC US10Y", "2026-11-05", "Yahoo ^TNX 4.837"),
    ("Earnings date", "2026-11-25", "StockAnalysis overview", "2026-11-06", "Q3 FY26 estimate; Q2 already public Aug 19"),
]
for i, row in enumerate(audit, 4):
    for col, val in enumerate(row, 1):
        ws4.cell(row=i, column=col, value=val)
        style_data_cell(ws4, i, col)

set_col_widths(ws4, [28, 28, 36, 14, 88])

# ===========================================================================
# Sheet 5: Questions
# ===========================================================================
ws5 = wb.create_sheet("Questions")
ws5.merge_cells("A1:C1")
ws5["A1"].value = "BMA — Open Questions"
ws5["A1"].font = title_font
ws5.cell(row=3, column=1, value="#")
ws5.cell(row=3, column=2, value="Question")
ws5.cell(row=3, column=3, value="Category")
style_header_row(ws5, 3, 3)

questions = [
    (
        "Q1",
        "ADR vs local share math: Yahoo SO 62.82M vs implied 71.12M vs Class B 639.41M / 10 = 63.94M. Which float is the economic claim on common equity, and are there treasury, Class A, or convertible overlays?",
        "Share count",
    ),
    (
        "Q2",
        "USD EPS conflict: StockAnalysis $3.87 vs Yahoo $4.89 vs ARS 598.61 x 10 / ~1484 FX ~ $4.03. Which FX and share base should drive trailing P/E?",
        "Data quality",
    ),
    (
        "Q3",
        "IAS 29 inflation accounting: FY23 revenue ARS 8.15T and NI ARS 1.67T then collapsed. How much of TTM ROE 7% is real vs purchasing-power restatement noise?",
        "Earnings quality",
    ),
    (
        "Q4",
        "TTM ROE 7.07% vs Q2 annualized adj 14.3% vs FY26 adj guide 12% vs 2030 20%. Which run-rate is the market 0.87x P/B actually underwriting?",
        "Returns",
    ),
    (
        "Q5",
        "Justified P/B at 7% ROE and 13.4% Ke is ~0.44x (~$29). If ROE does not sustain 12%, is today's price a value trap?",
        "Valuation",
    ),
    (
        "Q6",
        "NPL 6.25% (consumer 8.4%) with coverage 95%. Management guides YE NPL 5.5-6% and cost of risk 6.5-7%. What if consumer NPLs follow the system 12.8%?",
        "Credit",
    ),
    (
        "Q7",
        "Provisions jumped from ARS 142B (FY24) to 538B (FY25) to 757B TTM. Is this the peak of the credit-cost cycle or the new through-cycle cost?",
        "Credit",
    ),
    (
        "Q8",
        "Government securities are ~25% of assets. What is duration, sovereign rating, and P&L sensitivity to a 12-13% 2H26 devaluation (mgmt assumption)?",
        "Sovereign / FX",
    ),
    (
        "Q9",
        "Banco Saenz SPA (Mar 20 2026) with Fintech Digital LLC — purchase price, NPL content, deposit franchise, and close timing?",
        "M&A",
    ),
    (
        "Q10",
        "ARS 160B buyback (~USD 108M, ~3% of MC) announced Oct 28 for 45 days because the price does not reflect fair value. Completed? At what VWAP vs $57.99?",
        "Capital allocation",
    ),
    (
        "Q11",
        "Dividend payout 94% of stated USD EPS while buybacks restart. Is the cash dividend in USD terms sustainable if ARS NI is restated and CET1 is spent on Saenz?",
        "Capital allocation",
    ),
    (
        "Q12",
        "FY24 effective tax 9.31% vs TTM 38.54% vs FY25 43.12%. What is the through-cycle tax rate for residual-income models?",
        "Tax",
    ),
    (
        "Q13",
        "FY25 OCF -ARS 2.06T vs TTM OCF +ARS 1.89T. How much is loan growth vs securities vs inflation restatement?",
        "Cash flow",
    ),
    (
        "Q14",
        "Branch cut 491->402->~370 YE26 and FTE 8,180 (Yahoo 8,490 / SA 7,796). When do restructuring charges end and 2027 savings show in reported ROE?",
        "Efficiency",
    ),
    (
        "Q15",
        "Q3 FY26 on Nov 25: does Stage 3 stay <4.1%, does adj ROE hold ~12-14%, and is real loan growth still 2-5%?",
        "Next earnings",
    ),
    (
        "Q16",
        "Country risk: what election / capital-control / dual-FX path in 2027 would break the 12% ROE underwrite without a CET1 breach?",
        "Country risk",
    ),
]
for i, row in enumerate(questions, 4):
    for col, val in enumerate(row, 1):
        ws5.cell(row=i, column=col, value=val)
        style_data_cell(ws5, i, col)

set_col_widths(ws5, [8, 120, 22])

# ===========================================================================
# Sheet 6: Sources
# ===========================================================================
ws6 = wb.create_sheet("Sources")
ws6.merge_cells("A1:C1")
ws6["A1"].value = "BMA — Sources"
ws6["A1"].font = title_font
ws6.cell(row=3, column=1, value="#")
ws6.cell(row=3, column=2, value="Source")
ws6.cell(row=3, column=3, value="URL")
style_header_row(ws6, 3, 3)

sources = [
    ("S1", "StockAnalysis — BMA overview", "https://stockanalysis.com/stocks/bma/"),
    ("S2", "StockAnalysis — BMA statistics", "https://stockanalysis.com/stocks/bma/statistics/"),
    ("S3", "StockAnalysis — BMA financials", "https://stockanalysis.com/stocks/bma/financials/"),
    ("S4", "StockAnalysis — BMA income statement", "https://stockanalysis.com/stocks/bma/financials/income-statement/"),
    ("S5", "StockAnalysis — BMA balance sheet", "https://stockanalysis.com/stocks/bma/financials/balance-sheet/"),
    ("S6", "StockAnalysis — BMA cash flow", "https://stockanalysis.com/stocks/bma/financials/cash-flow-statement/"),
    ("S7", "StockAnalysis — BMA forecast", "https://stockanalysis.com/stocks/bma/forecast/"),
    ("S8", "StockAnalysis — BMA company profile", "https://stockanalysis.com/stocks/bma/company/"),
    ("S9", "Yahoo Finance — BMA summary", "https://finance.yahoo.com/quote/BMA/"),
    ("S10", "Yahoo Finance — BMA key statistics", "https://finance.yahoo.com/quote/BMA/key-statistics/"),
    ("S11", "Yahoo Finance — BMA analysis", "https://finance.yahoo.com/quote/BMA/analysis/"),
    ("S12", "Yahoo Finance — BMA profile", "https://finance.yahoo.com/quote/BMA/profile/"),
    ("S13", "CNBC — US 10Y Treasury", "https://www.cnbc.com/quotes/US10Y"),
    ("S14", "PR Newswire — Q2 2026 results", "https://www.prnewswire.com/news-releases/banco-macro-announces-results-for-the-second-quarter-of-2026-302855725.html"),
    ("S15", "Q2 2026 earnings call transcript (StockAnalysis)", "https://stockanalysis.com/quote/bcba/BMA/transcripts/681826-q2-2026/"),
    ("S16", "MarketBeat — Q2 2026 call highlights", "https://www.marketbeat.com/instant-alerts/macro-bank-q2-earnings-call-highlights-2026-08-20/"),
    ("S17", "PR Newswire — share buyback Oct 28 2026", "https://www.prnewswire.com/news-releases/banco-macro-sa-announces-share-buyback-program-302922815.html"),
    ("S18", "PR Newswire — Banco Saenz SPA Mar 20 2026", "https://www.prnewswire.com/news-releases/banco-macro-sa-announces-that-it-has-entered-into-a-share-purchase-agreement-to-acquire-banco-saenz-sa-302719992.html"),
    ("S19", "Banco Macro IR — about us", "https://www.macro.com.ar/relaciones-inversores/en/about-us"),
    ("S20", "Citi DR — BMA 10:1 ADR", "https://depositaryreceipts.citi.com/adr/notices/pgm_dispCA.aspx?cusip=05961W105&pageId=15&subpageID=112"),
]
for i, row in enumerate(sources, 4):
    for col, val in enumerate(row, 1):
        ws6.cell(row=i, column=col, value=val)
        style_data_cell(ws6, i, col)

set_col_widths(ws6, [8, 52, 110])

out = "models/[2026-11-06] Banco Macro Model.xlsx"
wb.save(out)
print("Saved", out, "sheets:", wb.sheetnames)
