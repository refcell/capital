#!/usr/bin/env python3
"""Build the 2026-10-28 FirstCash Holdings valuation workbook."""

from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


OUT = Path(__file__).with_name("2026-10-28 FirstCash Holdings Model.xlsx")
PRICE = 185.35  # Oct. 27, 2026 close
PRE_PRINT_PRICE = 216.75  # Oct. 21, 2026 close, day before Q3 release
SHARES = 42.89  # millions, StockAnalysis shares outstanding
MARKET_CAP = 7950.0  # $ millions
CASH = 203.2  # Sep. 30, 2026
FUNDED_DEBT = 169.0 + 2278.1  # revolver + senior notes (net of issuance costs)
LEASES = 111.2 + 249.4  # operating lease liabilities
DEBT = FUNDED_DEBT + LEASES  # provider total debt $2,808M
NET_DEBT = DEBT - CASH
PROVIDER_EV = 10550.0
RAMSDENS = 308.0  # pending cash acquisition, $ millions equity value
REV_TTM = 4286.0
REV_FY25 = 3661.0
REV_FY26_CONS = 4360.0
EPS_FY25_ADJ = 8.76
EPS_TTM_GAAP = 9.24
EPS_TTM_ADJ = 7.87 + (8.76 - 6.12)  # 9M 2026 adj + Q4 2025 adj
EPS_FY26_CONS = 10.99  # adjusted, S&P Global, 4 analysts
FWD_PE = 15.18
EPS_NTM = PRICE / FWD_PE
ADJ_NI_TTM = 462.5
ADJ_EBITDA_TTM = 834.9
OCF_TTM = 679.0
ADJ_FCF_TTM = 392.9  # after net pawn-loan and finance-receivable fundings
BVPS = 52.46
ANALYST_PT = 247.5
TAX = 0.265
HORIZON = 5

NAVY = "17365D"
BLUE = "D9EAF7"
GREEN = "E2F0D9"
YELLOW = "FFF2CC"
WHITE = "FFFFFF"
thin = Side(style="thin", color="B7B7B7")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, row, col, value, *, bold=False, fill=None, fmt=None, wrap=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.border = border
    cell.font = Font(bold=bold, color=WHITE if fill == NAVY else "000000")
    cell.alignment = Alignment(vertical="top", wrap_text=wrap)
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    if fmt:
        cell.number_format = fmt
    return cell


def title(ws, text, end_col):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    cell = ws.cell(1, 1, text)
    cell.font = Font(size=15, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 24


def headers(ws, row, values):
    for col, value in enumerate(values, 1):
        put(ws, row, col, value, bold=True, fill=BLUE, wrap=True)


# WACC
rf = 0.04993
erp = 0.05
beta = 0.55
ke = rf + beta * erp
ke_floor = 0.095  # judgmental cost of equity for a regulated subprime lender
cost_debt = 0.060  # 6.125% 2034 notes are the marginal cost; TTM interest $143M on ~$2.4B funded debt
equity_weight = MARKET_CAP / (MARKET_CAP + DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * ke + debt_weight * cost_debt * (1 - TAX)

# Scenario inputs: FY2031 adjusted EPS x exit P/E. EV/EBITDA is the cross-check.
scen = {
    "Bear": {"cagr": 0.03, "margin": 0.110, "shares": 41.5, "pe": 11.0, "ebitda_m": 0.180, "ev_mult": 8.5, "net_debt": 3000.0, "w": 0.25},
    "Base": {"cagr": 0.08, "margin": 0.120, "shares": 41.0, "pe": 14.0, "ebitda_m": 0.200, "ev_mult": 10.5, "net_debt": 2800.0, "w": 0.50},
    "Bull": {"cagr": 0.11, "margin": 0.130, "shares": 40.5, "pe": 17.0, "ebitda_m": 0.210, "ev_mult": 12.5, "net_debt": 2600.0, "w": 0.25},
}
for s in scen.values():
    s["rev"] = REV_FY26_CONS * (1 + s["cagr"]) ** HORIZON
    s["ni"] = s["rev"] * s["margin"]
    s["eps"] = s["ni"] / s["shares"]
    s["eps_cagr"] = (s["eps"] / EPS_FY26_CONS) ** (1 / HORIZON) - 1
    s["target"] = s["eps"] * s["pe"]
    s["pv"] = s["target"] / (1 + ke) ** HORIZON
    s["ebitda"] = s["rev"] * s["ebitda_m"]
    s["ev"] = s["ebitda"] * s["ev_mult"]
    s["ev_target"] = (s["ev"] - s["net_debt"]) / s["shares"]
weighted_fv = sum(s["target"] * s["w"] for s in scen.values())
weighted_pv = weighted_fv / (1 + ke) ** HORIZON
weighted_pv_floor = weighted_fv / (1 + ke_floor) ** HORIZON

wb = Workbook()
ws = wb.active
ws.title = "Valuation"
title(ws, "FirstCash Holdings, Inc. (NASDAQ: FCFS) — Valuation Summary", 4)
summary = [
    ("Company", "FirstCash Holdings, Inc.", "Model date", "2026-10-28"),
    ("Quote", "$185.35 at Oct. 27, 2026 close ($216.75 before Q3 print)", "Shares outstanding", "42.89M (43.34M at Sep. 30 balance sheet)"),
    ("Market capitalization", "$7.95B", "Enterprise value", f"${PROVIDER_EV / 1000:.2f}B (MC + $2.81B debt incl. $0.36B leases − $0.20B cash)"),
    ("Net debt (Sep. 30, 2026)", f"${NET_DEBT / 1000:.2f}B incl. leases; ${(FUNDED_DEBT - CASH) / 1000:.2f}B funded", "Pending", f"Ramsdens (U.K.) cash acquisition ~${RAMSDENS:.0f}M, targeted to close by YE2026"),
    ("Primary lens", "FY2031 adjusted EPS × exit P/E; EV/EBITDA cross-check (net debt 6.6x adj. FCF puts FCF multiples in the gray zone)", "Stance", "Watch / Positive bias"),
]
for r, row in enumerate(summary, 3):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, bold=c in (1, 3), fill=YELLOW if c in (1, 3) else None, wrap=True)

headers(ws, 10, ["Metric", "Current / Forward", "Interpretation", "Source date"])
metrics = [
    ("Trailing P/E (GAAP)", f"{PRICE / EPS_TTM_GAAP:.1f}x", f"TTM GAAP EPS ${EPS_TTM_GAAP:.2f}; includes ~$1.06/sh acquired-intangible amortization", "2026-09-30"),
    ("Trailing P/E (adjusted)", f"{PRICE / EPS_TTM_ADJ:.1f}x", f"TTM adjusted EPS ${EPS_TTM_ADJ:.2f} (9M 2026 $7.87 + Q4 2025 $2.64)", "2026-09-30"),
    ("Forward P/E (FY2026E)", f"{PRICE / EPS_FY26_CONS:.1f}x", f"${EPS_FY26_CONS:.2f} adjusted consensus (4 analysts, $10.86-$11.14); implies Q4 ${EPS_FY26_CONS - 7.87:.2f} vs $2.64", "2026-10-28"),
    ("Forward P/E (NTM, provider)", f"{FWD_PE:.2f}x", f"Implied NTM EPS ${EPS_NTM:.2f}; five-year average ~16x; 18x before the Q3 print", "2026-10-28"),
    ("P/S (TTM)", f"{MARKET_CAP / REV_TTM:.2f}x", f"TTM revenue ${REV_TTM:,.0f}M (+22.9%); $531M is low-margin scrap gold", "2026-09-30"),
    ("P/FCF (adjusted FCF)", f"{MARKET_CAP / ADJ_FCF_TTM:.1f}x", f"Company adj. FCF ${ADJ_FCF_TTM:.0f}M after funding pawn-loan growth; provider FCF $606M excludes loan fundings", "2026-09-30"),
    ("EV / adjusted FCF", f"{PROVIDER_EV / ADJ_FCF_TTM:.1f}x", "Net debt / adj. FCF 6.6x", "2026-09-30"),
    ("EV / Sales", f"{PROVIDER_EV / REV_TTM:.2f}x", "Revenue mix shifting from AFF leasing to pawn and scrap", "2026-09-30"),
    ("EV / adjusted EBITDA", f"{PROVIDER_EV / ADJ_EBITDA_TTM:.1f}x", f"TTM adj. EBITDA ${ADJ_EBITDA_TTM:.0f}M; EZCORP trades ~9.0x", "2026-09-30"),
    ("P/B", f"{PRICE / BVPS:.2f}x", "Tangible book near zero after goodwill ($2.04B); adjusted ROE 20%", "2026-09-30"),
    ("Dividend yield", f"{1.84 / PRICE:.2%}", "$0.46 quarterly after 10% raise; ~17% of adjusted EPS", "2026-10-22"),
    ("Net debt / adj. EBITDA", "2.7x (2.6x pro forma)", "Revolver covenant allows up to 3.5x after Aug. 2026 amendment", "2026-09-30"),
    ("Analyst target (12M)", f"${ANALYST_PT:.2f} avg ($235-$255)", f"{ANALYST_PT / PRICE - 1:.0%} upside; 4 analysts, Strong Buy; two cuts on Oct. 23", "2026-10-28"),
    ("Probability-weighted FV (FY2031)", f"${weighted_fv:.2f}", f"25% bear / 50% base / 25% bull; {weighted_fv / PRICE - 1:.0%} undiscounted before ~1% dividend", "2026-10-28"),
    ("PV of weighted FV at cost of equity", f"${weighted_pv:.2f}", f"Discounted 5 years at CAPM {ke:.2%}; ${weighted_pv_floor:.2f} at a {ke_floor:.1%} judgmental Ke", "2026-10-28"),
]
for r, row in enumerate(metrics, 11):
    for c, value in enumerate(row, 1):
        hl = r in (24, 25)
        put(ws, r, c, value, bold=hl, fill=GREEN if hl else None, wrap=True)
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 30
ws.column_dimensions["C"].width = 78
ws.column_dimensions["D"].width = 14
ws.freeze_panes = "A11"

ws = wb.create_sheet("WACC")
title(ws, "FCFS Weighted Average Cost of Capital", 4)
headers(ws, 3, ["Component", "Value", "Calculation / Source", "Comment"])
wacc_rows = [
    ("Risk-free rate", rf, "Yahoo Finance ^TNX (10-year Treasury)", "Oct. 27-28, 2026"),
    ("Equity risk premium", erp, "Model assumption", "Standard US ERP"),
    ("Levered beta", beta, "StockAnalysis statistics", "Five-year beta; low because pawn demand is countercyclical"),
    ("Cost of equity (CAPM)", ke, "Rf + beta × ERP", f"Likely understated for a subprime lender with CFPB/Mexico regulatory exposure; {ke_floor:.1%} used as a sensitivity"),
    ("Pre-tax cost of debt", cost_debt, "6.125% 2034 notes (May 2026) are marginal cost; TTM cash interest ~5.9% of funded debt", "Assumption"),
    ("Tax rate", TAX, "2026 guidance 26%-27%", "TTM effective 26.6%"),
    ("Market capitalization", MARKET_CAP, "StockAnalysis", "$ millions"),
    ("Total debt", DEBT, "Balance sheet, Sep. 30, 2026", "$ millions; $2,447M funded + $361M leases"),
    ("Equity weight", equity_weight, "MC / (MC + debt)", ""),
    ("Debt weight", debt_weight, "Debt / (MC + debt)", ""),
    ("Computed WACC", wacc, "E/V × Ke + D/V × Kd × (1 − t)", "Provider estimate 6.35%"),
]
for r, row in enumerate(wacc_rows, 4):
    for c, value in enumerate(row, 1):
        fmt = None
        if c == 2:
            fmt = "#,##0.0" if r in (10, 11) else ("0.00" if r == 6 else "0.00%")
        put(ws, r, c, value, bold=r == 14, fill=GREEN if r == 14 else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 28
ws.column_dimensions["B"].width = 16
ws.column_dimensions["C"].width = 60
ws.column_dimensions["D"].width = 58

ws = wb.create_sheet("Scenarios")
title(ws, "FCFS Five-Year Forward P/E Scenario Analysis (FY2031)", 6)
ws.merge_cells("A2:F2")
ws["A2"] = (
    "Primary framework: FY2031 revenue × adjusted net margin ÷ diluted shares = adjusted EPS, × exit P/E. "
    "FCF multiples are not the primary lens: net debt is 6.6x adjusted FCF, and FCF is struck after funding pawn-loan growth, "
    "so it understates owner earnings in a growth year. EV/EBITDA less projected net debt is shown as a cross-check."
)
ws["A2"].alignment = Alignment(wrap_text=True)
ws.row_dimensions[2].height = 48
headers(ws, 4, ["Metric", "Bear", "Base", "Bull", "Units / Formula", "Interpretation"])
B, M, U = scen["Bear"], scen["Base"], scen["Bull"]
scenario_rows = [
    ("Revenue CAGR (FY2026E-FY2031)", B["cagr"], M["cagr"], U["cagr"], "%", "From $4.36B FY2026 consensus; bear: gold reverses and scrap/loan sizes shrink, AFF keeps contracting"),
    ("FY2031 revenue", B["rev"], M["rev"], U["rev"], "$mm", "Base: ~4% store growth + mid-single-digit same-store; bull adds Ramsdens and further M&A"),
    ("Adjusted net margin", B["margin"], M["margin"], U["margin"], "%", "TTM 10.8% ($462M adj. NI); mix shifts from AFF toward pawn"),
    ("FY2031 adjusted net income", B["ni"], M["ni"], U["ni"], "$mm", "Revenue × margin"),
    ("FY2031 diluted shares", B["shares"], M["shares"], U["shares"], "mm", "42.89M today; buybacks ~1%-2% a year net of grants"),
    ("FY2031 adjusted EPS", B["eps"], M["eps"], U["eps"], "$ / share", "Net income / shares"),
    ("Adjusted EPS CAGR (FY2026E-FY2031)", B["eps_cagr"], M["eps_cagr"], U["eps_cagr"], "%", "Provider 3-year EPS growth forecast 19.95%"),
    ("Exit P/E", B["pe"], M["pe"], U["pe"], "x", "Five-year average ~16x forward; EZCORP ~14x; bear prices a regulatory/gold-reversal discount"),
    ("Target price (FY2031)", B["target"], M["target"], U["target"], "$ / share", "EPS × exit P/E"),
    ("Upside / (downside)", B["target"] / PRICE - 1, M["target"] / PRICE - 1, U["target"] / PRICE - 1, "%", "Versus $185.35 close; undiscounted, before dividends"),
    ("Probability", B["w"], M["w"], U["w"], "%", "Weights sum to 100%"),
    ("Weighted value / share", B["target"] * B["w"], M["target"] * M["w"], U["target"] * U["w"], "$ / share", "Target × probability"),
    ("Probability-weighted FV (FY2031)", None, weighted_fv, None, "$ / share", "Sum of weighted values"),
    ("Upside from current", None, weighted_fv / PRICE - 1, None, "%", "Undiscounted five-year"),
    ("PV of weighted FV at Ke", None, weighted_pv, None, "$ / share", f"Discounted {HORIZON} years at CAPM {ke:.2%}"),
    ("PV upside from current", None, weighted_pv / PRICE - 1, None, "%", f"At {ke_floor:.1%} Ke the PV is ${weighted_pv_floor:.2f}"),
    ("Cross-check: adj. EBITDA margin", B["ebitda_m"], M["ebitda_m"], U["ebitda_m"], "%", "TTM 19.5% ($835M)"),
    ("Cross-check: FY2031 adj. EBITDA", B["ebitda"], M["ebitda"], U["ebitda"], "$mm", "Revenue × margin"),
    ("Cross-check: exit EV/EBITDA", B["ev_mult"], M["ev_mult"], U["ev_mult"], "x", "Today 12.6x; EZCORP ~9.0x"),
    ("Cross-check: FY2031 net debt incl. leases", B["net_debt"], M["net_debt"], U["net_debt"], "$mm", "$2.6B today plus Ramsdens; held near 2.5x-3.0x EBITDA"),
    ("Cross-check: EV/EBITDA value / share", B["ev_target"], M["ev_target"], U["ev_target"], "$ / share", "(EV − net debt) / shares; leverage amplifies the bear case"),
]
for r, row in enumerate(scenario_rows, 5):
    for c, value in enumerate(row, 1):
        fmt = None
        if c in (2, 3, 4) and row[4] == "%":
            fmt = "0.0%"
        elif c in (2, 3, 4) and row[4] == "$ / share":
            fmt = "$#,##0.00"
        elif c in (2, 3, 4) and row[4] in ("$mm", "mm"):
            fmt = "#,##0.0"
        elif c in (2, 3, 4) and row[4] == "x":
            fmt = "0.0x"
        hl = r in (17, 18, 19, 20)
        put(ws, r, c, value, bold=r == 13 or hl, fill=GREEN if hl else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 40
for col in "BCD":
    ws.column_dimensions[col].width = 14
ws.column_dimensions["E"].width = 16
ws.column_dimensions["F"].width = 82
ws.freeze_panes = "A5"

urls = {
    "overview": "https://stockanalysis.com/stocks/fcfs/",
    "income": "https://stockanalysis.com/stocks/fcfs/financials/",
    "quarterly": "https://stockanalysis.com/stocks/fcfs/financials/?p=quarterly",
    "balance": "https://stockanalysis.com/stocks/fcfs/financials/balance-sheet/",
    "cashflow": "https://stockanalysis.com/stocks/fcfs/financials/cash-flow-statement/",
    "statistics": "https://stockanalysis.com/stocks/fcfs/statistics/",
    "forecast": "https://stockanalysis.com/stocks/fcfs/forecast/",
    "history": "https://stockanalysis.com/stocks/fcfs/history/",
    "q3pr": "https://investors.firstcash.com/news-releases/news-release-details/firstcash-reports-record-third-quarter-operating-results-0",
    "q3_8k": "https://www.sec.gov/Archives/edgar/data/840489/000084048926000097/fcfs10222026exhibit991.htm",
    "q2pr": "https://www.sec.gov/Archives/edgar/data/840489/000084048926000082/fcfs07232026exhibit991.htm",
    "notes": "https://ir.firstcash.com/news-releases/news-release-details/firstcash-announces-upsize-and-pricing-750-million-senior-notes",
    "ramsdens": "https://ir.firstcash.com/news-releases/news-release-details/firstcash-acquire-ramsdens-leading-pawn-retail-and-financial",
    "succession": "https://investors.firstcash.com/news-releases/news-release-details/firstcash-announces-planned-leadership-succession",
    "drop": "https://finance.yahoo.com/markets/stocks/articles/firstcash-sinks-13-ezcorp-down-173426222.html",
    "stockstory": "https://stockstory.org/us/stocks/nasdaq/fcfs/news/why-up-down/firstcash-fcfs-stock-trades-down-here-is-why",
    "lawfirm": "https://www.businesswire.com/news/home/20261023272361/en/Did-You-Lose-Money-on-FirstCash-Holdings-Inc.-Stock-The-Law-Offices-of-Howard-G.-Smith-Announces-Securities-Fraud-Investigation-After-14.75-Share-Price-Decline",
    "gold": "https://www.cnbc.com/2026/09/30/gold-on-track-for-monthly-decline-as-investors-await-us-inflation-data.html",
    "ezpw": "https://stockanalysis.com/stocks/ezpw/statistics/",
    "treasury": "https://finance.yahoo.com/quote/%5ETNX/",
}
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "FCFS Actuals Source Audit", 5)
headers(ws, 3, ["Data point", "Value", "Source URL", "As of", "Notes"])
audit = [
    ("Close price", "$185.35 (52-wk $146.77-$238.93)", urls["history"], "2026-10-27", "Oct. 21 $216.75; Oct. 22 $184.78 (−14.75%); Oct. 23 $172.75 (−6.51%); Oct. 26 $175.27"),
    ("Market cap / EV", "$7.95B / $10.55B", urls["statistics"], "2026-10-27", "EV = MC + $2.81B debt − $0.20B cash"),
    ("Shares outstanding", "42.89M; −1.64% YoY", urls["statistics"], "2026-10-27", "Balance sheet 43.34M at Sep. 30; Q3 diluted 43.335M"),
    ("Beta", "0.55", urls["statistics"], "2026-10-27", "Five-year"),
    ("Revenue TTM / FY2025 / FY2024", "$4,286M / $3,661M / $3,389M", urls["income"], "2026-09-30", "TTM +22.9%"),
    ("Revenue mix TTM", "Retail $1,918M; pawn fees $1,042M; scrap $531M; leasing $479M; finance fees $302M", urls["income"], "2026-09-30", "Scrap was $132M in FY2024"),
    ("Q3 2026 revenue / GAAP EPS / adj. EPS", "$1,101.2M / $2.33 / $2.68", urls["q3pr"], "2026-09-30", "Consensus adj. EPS $2.63, revenue $1.07B"),
    ("Q3 scrap revenue / cost", "$172.5M / $140.2M", urls["q3pr"], "2026-09-30", "Scrap gross margin 18.8%; Q3 2025 revenue $86.7M"),
    ("Segment pre-tax income Q3 2026", "U.S. $133.3M; LatAm $64.6M; U.K. $29.2M; AFF $33.2M", urls["q3pr"], "2026-09-30", "Q3 2025: $112.0M / $47.0M / $17.9M / $46.0M"),
    ("Segment pre-tax income 9M 2026", "U.S. $403.9M; LatAm $173.6M; U.K. $102.0M; AFF $87.8M", urls["q3pr"], "2026-09-30", "Total $767.5M"),
    ("AFF metrics", "GTV −15% YoY; net revenue −20%; net charge-offs 5.6%", urls["q3pr"], "2026-09-30", "Conn's and American Freight bankruptcies; Q4 GTV guided down mid-teens"),
    ("Pawn receivables", "$907.7M (+15%); U.S. $487.2M, LatAm $205.5M, U.K. $214.9M", urls["q3pr"], "2026-09-30", "U.S. same-store +12%; LatAm +15% constant currency; U.K. same-store +14% local"),
    ("Pawn collateral jewelry share", "U.S. 63%; LatAm 52%; U.K. 99%; total 67%", urls["q3pr"], "2026-09-30", "Prior year 72% / 42% / 98% / 72%"),
    ("Store count", "3,352 (U.S. 1,215; LatAm 1,839; U.K. 298)", urls["q3pr"], "2026-09-30", "70 added in TTM; 480 owned properties"),
    ("Net income TTM / FY2025", "$406.5M / $330.4M", urls["income"], "2026-09-30", "Adjusted TTM $462.5M"),
    ("Adjusted EBITDA TTM", "$834.9M", urls["q3pr"], "2026-09-30", "EBITDA $823.1M; D&A $127.6M; interest $143.2M"),
    ("Operating income TTM", "$702.9M (16.4% margin)", urls["income"], "2026-09-30", "Provider statistics show $691.9M"),
    ("OCF / adj. FCF TTM", "$679.0M / $392.9M", urls["q3pr"], "2026-09-30", "Adj. FCF after $180M net pawn-loan and finance-receivable fundings and $73M capex"),
    ("Investing CF FY2025 vs capex", "−$828.1M vs −$54.9M", urls["cashflow"], "2025-12-31", "Gap: $475M acquisitions (H&T), $62M real estate, ~$236M net loan fundings"),
    ("Cash / debt", "$203.2M / $2,808M", urls["balance"], "2026-09-30", "Revolver $169M; notes $2,278M; leases $361M"),
    ("Senior notes issued 2026", "$750M 6.125% due 2034", urls["notes"], "2026-04-28", "Proceeds repaid revolver ($559M at Dec. 2025)"),
    ("Credit facility", "$1.055B unsecured, maturity Aug. 2031", urls["q3pr"], "2026-08", "Net debt leverage covenant up to 3.5x"),
    ("Net debt / adj. EBITDA", "2.7x (2.6x pro forma)", urls["q3pr"], "2026-09-30", "2.9x at Sep. 2025 after H&T"),
    ("Equity / BVPS / TBVPS", "$2,273M / $52.46 / $1.22", urls["balance"], "2026-09-30", "Goodwill $2,035M; intangibles $185M"),
    ("Buybacks / dividends", "$250M YTD at $206.66; $0.46 quarterly", urls["q3pr"], "2026-09-30", "$50M left on July 2026 authorization"),
    ("Ramsdens acquisition", "675p per share + 9p dividend; ~£232M ($308M)", urls["q2pr"], "2026-07-16", "Raised from 600p; shareholder and FCA approvals received; antitrust pending"),
    ("Leadership succession", "Brent Stuart CEO from Jan. 1, 2027; Wessel Executive Chairman", urls["succession"], "2026-07-22", ""),
    ("Consensus FY2026", "Rev $4.36B; adj. EPS $10.99 ($10.86-$11.14)", urls["forecast"], "2026-10-28", "4 analysts; FY2027+ gated; 3Y EPS growth forecast 19.95%"),
    ("Analyst targets", "$247.50 avg; $235-$255", urls["forecast"], "2026-10-28", "TD Cowen $242→$235, Canaccord $265→$250 on Oct. 23"),
    ("Short interest", "2.42M; 5.65% of shares; 6.4 days", urls["statistics"], "2026-10-27", ""),
    ("Gold", "~$4,062/oz; fell 6.6% in Sep.; ~2% on Oct. 22", urls["gold"], "2026-10-28", "Spot from Yahoo GC=F banner"),
    ("Peer: EZCORP", "MC $1.82B; EV/EBITDA 8.97x; fwd P/E 14.2x", urls["ezpw"], "2026-10-27", ""),
    ("Next earnings", "Late Jan./early Feb. 2027 (Q4 2026)", urls["overview"], "2026-10-28", "Date not yet announced"),
    ("US 10Y Treasury", "4.993%", urls["treasury"], "2026-10-27", "Yahoo ^TNX"),
]
for r, row in enumerate(audit, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 48
ws.column_dimensions["C"].width = 70
ws.column_dimensions["D"].width = 14
ws.column_dimensions["E"].width = 58
ws.freeze_panes = "A4"

ws = wb.create_sheet("Questions")
title(ws, "FCFS Open Diligence Questions", 4)
headers(ws, 3, ["#", "Question", "Why it matters", "Evidence needed"])
questions = [
    (1, "How much of the 15% pawn-receivable growth is higher gold prices (bigger loans per item) versus more loans?", "Average U.S. loan rose 10% to $319 and U.K. 18% to $905; a gold reversal would shrink loan sizes and fees.", "Loan count vs average loan by segment; gold sensitivity disclosure"),
    (2, "What is the scrap gold gross profit sensitivity to a $500/oz move?", "Scrap revenue quadrupled from $132M (FY2024) to $531M TTM; Q3 scrap gross margin 18.8%.", "Ounces sold, realized price, hedging policy"),
    (3, "Why did U.S. jewelry collateral fall from 72% to 63% while LatAm rose from 42% to 52%?", "Mix change could reflect classification, acquisitions, or general-merchandise lending growth.", "10-Q collateral detail, call commentary"),
    (4, "Is AFF's earnings decline (pre-tax $46.0M → $33.2M in Q3) bottoming, and what is the plan if furniture demand stays weak?", "AFF is ~10% of segment income; the law-firm investigations cite it; divestiture is possible.", "Q4 GTV, merchant additions, strategic review"),
    (5, "Do the shareholder-firm 'investigations' after the Oct. 22 drop have any substance?", "These are routine solicitations, but an actual complaint would add legal cost and noise.", "Court filings (PACER), 10-K legal proceedings"),
    (6, "What is the status of the CFPB Military Lending Act matter after the 2025 settlement ($11M)?", "Regulatory overhang on AFF and U.S. pawn lending to servicemembers.", "Settlement terms, compliance obligations"),
    (7, "What is the Ramsdens purchase multiple and its EBITDA, and why was the offer raised from 600p to 675p?", "~$308M equity value; raising the bid may imply competition or overpayment.", "Ramsdens FY2026 results, scheme document"),
    (8, "How exposed is LatAm (52% of collateral is jewelry, 1,839 stores) to Mexican regulation and peso swings?", "Peso strength added 8% to Q3 LatAm revenue in dollars; Q4 guide assumes flat FX.", "Constant-currency trends, Mexico regulatory updates"),
    (9, "What are the maturities and coupons of the senior notes stack beyond the 2034 issue?", "Refinancing older lower-coupon notes at ~6% raises interest expense (+5% guided for Q4).", "10-Q debt footnote"),
    (10, "How much of operating cash flow growth is reinvested in pawn-loan growth each year?", "Adj. FCF ($393M) is ~58% of OCF ($679M); loan growth absorbs cash in good years and releases it in bad ones.", "Net loan fundings by year"),
    (11, "What happens to forfeiture rates and retail margins if gold falls sharply?", "Inventory carried at cost could be sold at lower margins; U.S. retail margin already slipped to 42% from 43%.", "Inventory aging, margin by category"),
    (12, "Will Brent Stuart change capital allocation (M&A pace, buybacks, AFF) when he becomes CEO on Jan. 1, 2027?", "Wessel built the M&A machine; succession is a governance and strategy transition.", "Q4 call, 2027 outlook"),
    (13, "Why is the U.K. aged inventory 11.6% vs 7.9% a year ago?", "H&T integration onto FirstPawn may be clearing old stock; elevated aging can presage write-downs.", "U.K. inventory detail"),
    (14, "What is the realistic 2027 earnings base once AFF stops shrinking and gold normalizes?", "FY2027 consensus is gated; provider shows 3-year EPS growth of ~20%, which embeds high gold.", "FY2027 guidance in February 2027"),
    (15, "How much store-level growth remains in the U.S. through M&A versus de novo in LatAm?", "70 stores added TTM on 3,352 base (~2%); long-run growth relies on acquisitions.", "Pipeline commentary (35-40 acquired stores mentioned)"),
]
for r, row in enumerate(questions, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 72
ws.column_dimensions["C"].width = 62
ws.column_dimensions["D"].width = 45

ws = wb.create_sheet("Sources")
title(ws, "FCFS Sources", 4)
headers(ws, 3, ["#", "Source", "URL", "Use"])
source_rows = [
    (1, "StockAnalysis overview", urls["overview"], "Price, news, earnings date"),
    (2, "StockAnalysis statistics", urls["statistics"], "Market value, ratios, shares, beta, short interest"),
    (3, "StockAnalysis forecast", urls["forecast"], "Consensus revenue/EPS, targets and ratings"),
    (4, "StockAnalysis income statement", urls["income"], "Annual revenue mix, margins"),
    (5, "StockAnalysis quarterly financials", urls["quarterly"], "Quarterly revenue, EPS, cash flow"),
    (6, "StockAnalysis balance sheet", urls["balance"], "Cash, debt, goodwill, equity"),
    (7, "StockAnalysis cash flow", urls["cashflow"], "OCF, capex, acquisitions, buybacks"),
    (8, "StockAnalysis price history", urls["history"], "Daily closes around the Q3 print"),
    (9, "FirstCash Q3 2026 earnings release", urls["q3pr"], "Segments, pawn metrics, guidance, non-GAAP reconciliations"),
    (10, "FirstCash Q3 2026 8-K Exhibit 99.1", urls["q3_8k"], "Same release on EDGAR"),
    (11, "FirstCash Q2 2026 8-K Exhibit 99.1", urls["q2pr"], "Ramsdens revised terms, notes offering"),
    (12, "FirstCash $750M 2034 notes pricing", urls["notes"], "Coupon and maturity"),
    (13, "FirstCash Ramsdens announcement", urls["ramsdens"], "Original terms"),
    (14, "FirstCash leadership succession", urls["succession"], "CEO transition"),
    (15, "Yahoo/TIKR: FirstCash sinks 13%", urls["drop"], "Gold-driven selloff narrative"),
    (16, "StockStory: why FCFS traded down", urls["stockstory"], "AFF-driven selloff narrative"),
    (17, "Business Wire: shareholder firm notice", urls["lawfirm"], "Drop magnitude and cited disclosure"),
    (18, "CNBC: gold monthly decline", urls["gold"], "Gold price context"),
    (19, "StockAnalysis EZCORP statistics", urls["ezpw"], "Peer multiples"),
    (20, "Yahoo Finance 10-Year Treasury", urls["treasury"], "WACC risk-free rate"),
]
for r, row in enumerate(source_rows, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 44
ws.column_dimensions["C"].width = 95
ws.column_dimensions["D"].width = 45

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert abs(check["Scenarios"]["C17"].value - weighted_fv) < 1e-6
assert scen["Bear"]["target"] < PRICE < scen["Base"]["target"] < scen["Bull"]["target"]
print(f"WACC: {wacc:.2%} (Ke {ke:.2%}, Kd {cost_debt:.2%})")
print(f"EV ${PROVIDER_EV:,.0f}M; net debt ${NET_DEBT:,.0f}M; EV/adj. EBITDA {PROVIDER_EV / ADJ_EBITDA_TTM:.2f}x; TTM adj. EPS ${EPS_TTM_ADJ:.2f}; NTM EPS ${EPS_NTM:.2f}")
for k, s in scen.items():
    print(f"{k}: rev ${s['rev']:,.0f}M, EPS ${s['eps']:.2f} (CAGR {s['eps_cagr']:.1%}), target ${s['target']:.2f} ({s['target'] / PRICE - 1:.1%}), PV ${s['pv']:.2f}, EV/EBITDA x-check ${s['ev_target']:.2f}")
print(f"Probability-weighted FV: ${weighted_fv:.2f} ({weighted_fv / PRICE - 1:.1%}); PV ${weighted_pv:.2f} ({weighted_pv / PRICE - 1:.1%}); PV at {ke_floor:.1%} ${weighted_pv_floor:.2f}")
print(f"Analyst target cross-check: ${ANALYST_PT}")
print(f"Created {OUT}")
