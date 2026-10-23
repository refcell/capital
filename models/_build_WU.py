#!/usr/bin/env python3
"""Build the 2026-10-23 Western Union valuation workbook."""

from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


OUT = Path(__file__).with_name("2026-10-23 Western Union Model.xlsx")
PRICE = 6.43  # Oct. 22, 2026 close
SHARES = 311.88  # millions
MARKET_CAP = 2010.0  # $ millions
EV = 3780.0
DEBT = 2697.0
CASH = 919.8
NET_DEBT = DEBT - CASH
EPS_2026_CONSENSUS = 1.27
EPS_2026_GUIDE_MID = 1.30
DIVIDEND = 0.94
OCF_TTM = 609.7
CAPEX_TTM = 44.3
INTANGIBLES_TTM = 141.3  # capitalized software and agent signing bonuses
FCF_PROVIDER = OCF_TTM - CAPEX_TTM
FCF_COMPANY = OCF_TTM - CAPEX_TTM - INTANGIBLES_TTM

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


# Scenario inputs (five-year horizon to FY2031)
REV_2026E = 4060.0
scen = {
    "Bear": {"cagr": -0.025, "margin": 0.134, "eps": 0.85, "pe": 5.0, "fcf": 280.0, "evfcf": 7.0, "netdebt": 2300.0, "shares": 312.0, "divs": 3.00, "w": 0.30},
    "Base": {"cagr": 0.025, "margin": 0.14, "eps": 1.30, "pe": 5.5, "fcf": 420.0, "evfcf": 8.5, "netdebt": 2000.0, "shares": 305.0, "divs": 4.70, "w": 0.50},
    "Bull": {"cagr": 0.045, "margin": 0.15, "eps": 1.75, "pe": 7.0, "fcf": 560.0, "evfcf": 10.0, "netdebt": 1600.0, "shares": 290.0, "divs": 4.70, "w": 0.20},
}
for s in scen.values():
    s["rev"] = REV_2026E * (1 + s["cagr"]) ** 5
    s["target"] = s["eps"] * s["pe"]
    s["fcf_ev"] = s["fcf"] * s["evfcf"]
    s["fcf_px"] = (s["fcf_ev"] - s["netdebt"]) / s["shares"]
weighted_fv = sum(s["target"] * s["w"] for s in scen.values())

wb = Workbook()
ws = wb.active
ws.title = "Valuation"
title(ws, "The Western Union Company (NYSE: WU) — Valuation Summary", 4)
summary = [
    ("Company", "The Western Union Company", "Model date", "2026-10-23"),
    ("Quote", "$6.43 at Oct. 22 close", "Shares outstanding", "311.88M"),
    ("Market capitalization", "$2.01B", "Enterprise value", "$3.78B"),
    ("Net debt", f"${NET_DEBT / 1000:.2f}B (Jun. 30, 2026)", "Pending deal", "Intermex at $16.00/sh cash; DFPI approval suspended"),
    ("Primary lens", "Forward P/E on adjusted EPS; FCF and dividend coverage cross-checks", "Stance", "Watch"),
]
for r, row in enumerate(summary, 3):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, bold=c in (1, 3), fill=YELLOW if c in (1, 3) else None, wrap=True)

headers(ws, 10, ["Metric", "Current / Forward", "Interpretation", "Source date"])
metrics = [
    ("Trailing P/E (GAAP)", "5.17x", "$1.24 TTM GAAP EPS; down 53% YoY", "2026-10-22"),
    ("Forward P/E (provider NTM)", "4.54x", "Implies ~$1.42 NTM EPS, blending FY2026 and FY2027", "2026-10-22"),
    ("FY2026E P/E (consensus)", f"{PRICE / EPS_2026_CONSENSUS:.2f}x", "$6.43 / $1.27 consensus (15 analysts)", "2026-10-22"),
    ("FY2026E P/E (guide midpoint)", f"{PRICE / EPS_2026_GUIDE_MID:.2f}x", "$1.25-$1.35 adjusted EPS guide, cut from $1.75-$1.85 on Jul. 30", "2026-07-30"),
    ("P/S", "0.50x", "$4.04B TTM revenue", "2026-10-22"),
    ("P/FCF (provider)", "3.55x", f"Provider FCF ${FCF_PROVIDER:.0f}M excludes ${INTANGIBLES_TTM:.0f}M capitalized software and signing bonuses", "2026-06-30"),
    ("P/FCF (company-defined)", f"{MARKET_CAP / FCF_COMPANY:.2f}x", f"OCF less capex less intangibles = ${FCF_COMPANY:.0f}M", "2026-06-30"),
    ("EV/FCF (company-defined)", f"{EV / FCF_COMPANY:.2f}x", "Provider basis 6.69x", "2026-06-30"),
    ("EV/Sales", "0.94x", "Mature, declining-revenue franchise", "2026-10-22"),
    ("EV/EBITDA", "4.54x", "$832.5M TTM EBITDA", "2026-10-22"),
    ("Net debt / EBITDA", f"{NET_DEBT / 832.5:.2f}x", "Gross 3.24x; company cites ~3x gross and ~2x net before Intermex", "2026-06-30"),
    ("Interest coverage", "4.37x", "EBIT / interest; cash interest $148M TTM", "2026-06-30"),
    ("Dividend yield", "14.62%", f"$0.94 annualized; {DIVIDEND * SHARES / FCF_COMPANY:.0%} of company-defined TTM FCF", "2026-10-22"),
    ("Short interest", "18.83% of shares", "58.73M shares; 6.3 days to cover", "2026-10-22"),
    ("Probability-weighted FV", f"${weighted_fv:.2f}", f"30% bear / 50% base / 20% bull; {weighted_fv / PRICE - 1:.1%} price upside before dividends", "2026-10-23"),
]
for r, row in enumerate(metrics, 11):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, bold=r == 25, fill=GREEN if r == 25 else None, wrap=True)
ws.column_dimensions["A"].width = 30
ws.column_dimensions["B"].width = 30
ws.column_dimensions["C"].width = 70
ws.column_dimensions["D"].width = 16
ws.freeze_panes = "A11"

ws = wb.create_sheet("WACC")
title(ws, "WU Weighted Average Cost of Capital", 4)
headers(ws, 3, ["Component", "Value", "Calculation / Source", "Comment"])
rf = 0.04966
erp = 0.05
beta = 0.55
ke = rf + beta * erp
cost_debt = 148.0 / DEBT
tax = 0.2158
equity_weight = MARKET_CAP / (MARKET_CAP + DEBT)
debt_weight = 1 - equity_weight
wacc = equity_weight * ke + debt_weight * cost_debt * (1 - tax)
wacc_rows = [
    ("Risk-free rate", rf, "CNBC US10Y", "Oct. 22, 2026 close"),
    ("Equity risk premium", erp, "Model assumption", "Standard US ERP"),
    ("Levered beta", beta, "StockAnalysis statistics", "Five-year beta; understates fundamental risk"),
    ("Cost of equity (CAPM)", ke, "Rf + beta × ERP", "Market-implied earnings yield ~20% says the market demands far more"),
    ("Pre-tax cost of debt", cost_debt, "$148M cash interest / $2,697M debt", "TTM observed cash cost"),
    ("Tax rate", tax, "StockAnalysis effective tax rate", "TTM GAAP"),
    ("Market capitalization", MARKET_CAP, "StockAnalysis", "$ millions"),
    ("Total debt", DEBT, "StockAnalysis", "$ millions, before Intermex delayed-draw funding"),
    ("Equity weight", equity_weight, "MC / (MC + debt)", ""),
    ("Debt weight", debt_weight, "Debt / (MC + debt)", ""),
    ("Computed WACC", wacc, "E/V × Ke + D/V × Kd × (1 − t)", "Provider estimate 5.59%; not used as a hurdle because CAPM beta is unrepresentative"),
]
for r, row in enumerate(wacc_rows, 4):
    for c, value in enumerate(row, 1):
        fmt = None
        if c == 2:
            fmt = "#,##0.0" if r in (10, 11) else ("0.00" if r == 6 else "0.00%")
        put(ws, r, c, value, bold=r == 14, fill=GREEN if r == 14 else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 28
ws.column_dimensions["B"].width = 16
ws.column_dimensions["C"].width = 42
ws.column_dimensions["D"].width = 60

ws = wb.create_sheet("Scenarios")
title(ws, "WU Five-Year Forward P/E Scenario Analysis", 6)
ws.merge_cells("A2:F2")
ws["A2"] = (
    "Primary framework: FY2031 adjusted EPS × exit P/E. Net debt of ~4.2x company-defined FCF puts WU in the "
    "FCF-multiple gray zone, so the FCF/EV rows are a leverage cross-check, not the target."
)
ws["A2"].alignment = Alignment(wrap_text=True)
ws.row_dimensions[2].height = 45
headers(ws, 4, ["Metric", "Bear", "Base", "Bull", "Units / Formula", "Interpretation"])
B, M, U = scen["Bear"], scen["Base"], scen["Bull"]
scenario_rows = [
    ("Revenue CAGR (5Y)", B["cagr"], M["cagr"], U["cagr"], "%", "Bear: deal breaks, retail erosion; base: Intermex closes 2027; bull: plus digital and Consumer Services growth"),
    ("Terminal revenue (FY2031)", B["rev"], M["rev"], U["rev"], "$mm", "From $4.06B FY2026E consensus"),
    ("Adjusted operating margin", B["margin"], M["margin"], U["margin"], "%", "Q2 2026 adjusted 15%; FY2031 levels include lower-margin Intermex revenue and ~$165-175M interest, consistent with terminal EPS at ~14-16% tax"),
    ("Terminal adjusted EPS", B["eps"], M["eps"], U["eps"], "$ / share", "FY2025 adjusted EPS was $1.75; FY2026 guide $1.25-$1.35"),
    ("Exit P/E", B["pe"], M["pe"], U["pe"], "x", "Current FY2026E P/E ~5.1x; 2021-2023 range 7-9x"),
    ("Target price", B["target"], M["target"], U["target"], "$ / share", "EPS × P/E"),
    ("Upside / (downside)", B["target"] / PRICE - 1, M["target"] / PRICE - 1, U["target"] / PRICE - 1, "%", "Versus $6.43 close, before dividends"),
    ("Cumulative dividends (5Y)", B["divs"], M["divs"], U["divs"], "$ / share", "Bear assumes dividend halved after 2027"),
    ("Probability", B["w"], M["w"], U["w"], "%", "Weights sum to 100%"),
    ("Weighted value / share", B["target"] * B["w"], M["target"] * M["w"], U["target"] * U["w"], "$ / share", "Target × probability"),
    ("Probability-weighted FV", None, weighted_fv, None, "$ / share", "Sum of weighted values"),
    ("Upside from current", None, weighted_fv / PRICE - 1, None, "%", "Excludes dividends"),
    ("Cross-check: terminal company FCF", B["fcf"], M["fcf"], U["fcf"], "$mm", "OCF − capex − capitalized signing bonuses/software; TTM $424M"),
    ("Cross-check: exit EV/FCF", B["evfcf"], M["evfcf"], U["evfcf"], "x", "Current 8.9x on company-defined FCF"),
    ("Cross-check: implied EV", B["fcf_ev"], M["fcf_ev"], U["fcf_ev"], "$mm", "FCF × multiple"),
    ("Cross-check: less net debt", B["netdebt"], M["netdebt"], U["netdebt"], "$mm", "Includes ~$500M Intermex funding in bear/base"),
    ("Cross-check: shares", B["shares"], M["shares"], U["shares"], "mm", "Buyback paused Jul. 2026"),
    ("Cross-check: FCF-implied price", B["fcf_px"], M["fcf_px"], U["fcf_px"], "$ / share", "Bear is negative: implied EV falls below net debt if FCF drops to $280M"),
]
for r, row in enumerate(scenario_rows, 5):
    for c, value in enumerate(row, 1):
        fmt = None
        if c in (2, 3, 4) and row[4] == "%":
            fmt = "0.0%"
        elif c in (2, 3, 4) and row[4] == "$ / share":
            fmt = "$#,##0.00"
        elif c in (2, 3, 4) and row[4] in ("$mm", "mm"):
            fmt = "#,##0"
        elif c in (2, 3, 4) and row[4] == "x":
            fmt = "0.0x"
        put(ws, r, c, value, bold=r in (10, 15, 16), fill=GREEN if r in (15, 16) else None, fmt=fmt, wrap=True)
ws.column_dimensions["A"].width = 34
for col in "BCD":
    ws.column_dimensions[col].width = 14
ws.column_dimensions["E"].width = 16
ws.column_dimensions["F"].width = 70
ws.freeze_panes = "A5"

urls = {
    "overview": "https://stockanalysis.com/stocks/wu/",
    "income": "https://stockanalysis.com/stocks/wu/financials/",
    "quarterly": "https://stockanalysis.com/stocks/wu/financials/?p=quarterly",
    "balance": "https://stockanalysis.com/stocks/wu/financials/balance-sheet/",
    "cashflow": "https://stockanalysis.com/stocks/wu/financials/cash-flow-statement/",
    "statistics": "https://stockanalysis.com/stocks/wu/statistics/",
    "forecast": "https://stockanalysis.com/stocks/wu/forecast/",
    "profile": "https://stockanalysis.com/stocks/wu/company/",
    "q2call": "https://stockanalysis.com/stocks/wu/transcripts/654382-q2-2026/",
    "q1call": "https://stockanalysis.com/stocks/wu/transcripts/562063-q1-2026/",
    "q4call": "https://stockanalysis.com/stocks/wu/transcripts/397080-q4-2025/",
    "dfpi": "https://www.sec.gov/Archives/edgar/data/1365135/000119312526350419/d126356dex991.htm",
    "hsr": "https://www.sec.gov/Archives/edgar/data/1365135/000119312526412336/d160759d8k.htm",
    "imxi": "https://stockanalysis.com/stocks/imxi/",
    "treasury": "https://www.cnbc.com/quotes/US10Y",
}
ws = wb.create_sheet("Actuals Source Audit")
title(ws, "WU Actuals Source Audit", 5)
headers(ws, 3, ["Data point", "Value", "Source URL", "As of", "Notes"])
audit = [
    ("Close price", "$6.43 (52-wk $5.87-$10.35)", urls["overview"], "2026-10-22", "After-hours $6.47"),
    ("Market cap / EV", "$2.01B / $3.78B", urls["statistics"], "2026-10-22", "Live provider snapshot"),
    ("Shares outstanding", "311.88M; -5.64% YoY", urls["statistics"], "2026-10-22", "Down from 393.8M at FY2021"),
    ("Beta", "0.55", urls["statistics"], "2026-10-22", "Five-year beta"),
    ("Revenue TTM / FY2025 / FY2021", "$4,037M / $4,051M / $5,071M", urls["income"], "2026-06-30", "Five straight years of decline"),
    ("Segment revenue TTM", "CMT $3,461M; Consumer Services $575.9M", urls["income"], "2026-06-30", "Consumer Services 14% of revenue vs 5% FY2021"),
    ("Gross / operating income TTM", "$1,417M / $653.2M", urls["income"], "2026-06-30", "35.1% gross, 16.2% operating margin"),
    ("Net income / GAAP EPS TTM", "$395.4M / $1.24", urls["income"], "2026-06-30", "FY2024 $934M included tax benefit"),
    ("Q2 2026 revenue / op income / EPS", "$1,013M / $132.1M / $0.24 GAAP; $0.31 adjusted", urls["quarterly"], "2026-06-30", "Adjusted op margin 15%"),
    ("Q1 2026 adjusted EPS", "$0.25 (Q2 was $0.06 better)", urls["q2call"], "2026-03-31", "Down $0.15 YoY"),
    ("FY2025 adjusted EPS", "$1.75", urls["q4call"], "FY2025", "Top of $1.65-$1.75 guide"),
    ("FY2026 guidance", "Adj. revenue +4-6% incl. Intermex; adj. EPS $1.25-$1.35", urls["q2call"], "2026-07-30", "Cut from +6-9% and $1.75-$1.85; assumed Sep. 1 Intermex close"),
    ("Cash / debt / net debt", "$919.8M / $2,697M / $1,777M", urls["balance"], "2026-06-30", "Before Intermex delayed-draw funding"),
    ("Equity / tangible book", "$914.7M / -$1,610M", urls["balance"], "2026-06-30", "Goodwill $2,138M"),
    ("OCF / capex / intangibles", "$609.7M / $44.3M / $141.3M", urls["cashflow"], "TTM 2026-06-30", "Company guides ~$200M 2026 capex incl. signing bonuses"),
    ("Dividends / buybacks TTM", "$302.7M / $142.4M", urls["cashflow"], "TTM 2026-06-30", "Buyback paused Jul. 30, 2026"),
    ("Cash interest / cash taxes TTM", "$148.0M / $74.4M", urls["cashflow"], "TTM 2026-06-30", "Cash taxes fell from $295.7M FY2025"),
    ("Consensus FY2026", "Revenue $4.06B; EPS $1.27 ($1.22-$1.33)", urls["forecast"], "2026-10-22", "15 analysts; FY2027+ gated behind Pro"),
    ("Analyst targets", "$6.66 avg; $5.00-$8.50; Sell consensus", urls["forecast"], "2026-10-22", "18 analysts: 1 buy, 10 hold, 2 sell, 5 strong sell"),
    ("Short interest", "58.73M; 18.83% of shares", urls["statistics"], "2026-10-22", "Up from 46.80M prior month"),
    ("Intermex DFPI status", "Approval extension suspended Aug. 2026", urls["dfpi"], "2026-08-14", "NY DFS approved same day"),
    ("Intermex HSR status", "New HSR filing Oct. 2, 2026; 30-day wait", urls["hsr"], "2026-10-02", "Prior clearance lapsed Oct. 6, 2026"),
    ("IMXI price vs deal price", "$9.51 vs $16.00 cash", urls["imxi"], "2026-10-22", "~41% gross spread signals heavy break risk"),
    ("Dividend", "$0.235 quarterly; $0.94 annual", urls["statistics"], "2026-10-22", "Ex-div Sep. 16, 2026"),
    ("Next earnings", "Nov. 4, 2026", urls["overview"], "2026-10-22", "Q3 2026"),
    ("US 10Y Treasury", "4.966%", urls["treasury"], "2026-10-22", "CNBC quote page"),
]
for r, row in enumerate(audit, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 31
ws.column_dimensions["B"].width = 40
ws.column_dimensions["C"].width = 70
ws.column_dimensions["D"].width = 16
ws.column_dimensions["E"].width = 55
ws.freeze_panes = "A4"

ws = wb.create_sheet("Questions")
title(ws, "WU Open Diligence Questions", 4)
headers(ws, 3, ["#", "Question", "Why it matters", "Evidence needed"])
questions = [
    (1, "What conditions is California's DFPI attaching before it reinstates Intermex approval, and does the merger agreement allow either side to walk or reprice?", "IMXI trades at $9.51 against a $16.00 cash price, so the market assigns a high break or renegotiation probability.", "Outside date, termination fees and DFPI correspondence"),
    (2, "How does FY2026 EPS guidance change now that the Sep. 1 Intermex close assumption has lapsed?", "The $1.25-$1.35 range included Intermex contribution; consensus already sits at $1.27.", "Nov. 4 guidance bridge"),
    (3, "How much lower is contribution profit per transaction on account and wallet payout than cash payout?", "Mix shift, not volume, drove the Q2 margin miss.", "CPPT by payout method and corridor"),
    (4, "What is the run-rate economics of the Middle East digital partnerships?", "They drive most Branded Digital transaction growth at very low revenue per transaction.", "Partner revenue share and contribution margin"),
    (5, "Can Beyond Efficiency deliver $50M run-rate by end-2026 and $200M by end-2027, and how much is reinvested?", "Cost savings are the main lever to rebuild EPS toward $1.75.", "Quarterly savings tracker and opex bridge"),
    (6, "What is the true free cash flow after ~$200M of 2026 capex including agent signing bonuses?", "Provider FCF excludes $141M of capitalized intangibles; dividend coverage depends on the definition.", "Company FCF reconciliation"),
    (7, "Is the $0.94 dividend sustainable if FCF falls toward the $304M FY2026 consensus while Intermex adds ~$500M of debt?", "Dividend costs ~$293M a year; payout could exceed 95% of FCF.", "Board policy, leverage covenant and rating agency commentary"),
    (8, "What leverage ceiling do rating agencies tolerate before investment-grade status is at risk?", "Management targets 2.5-3.0x and paused buybacks to protect it.", "Moody's/S&P reports and covenant definitions"),
    (9, "How quickly will Canada Post, Deutsche Post and Total Wireless volumes ramp, and at what commission rates?", "Competitive takeaways came at the high end of commission ranges.", "Agent-level transaction and commission data"),
    (10, "Is the US retail decline still mid-teens, and what share of retail volume is US-originated?", "New migration is the lifeline of the retail business.", "Retail transactions by send region"),
    (11, "How much float and working capital can USDPT and Treasury Bridge free up, and what returns does it earn?", "Management cited ramping over $1B of float in Q1 2027.", "Treasury Bridge volumes and pre-funding balances"),
    (12, "What reserve, custody and regulatory obligations come with USDPT?", "Stablecoin issuance adds compliance cost and potential liability.", "Reserve attestations and issuer structure"),
    (13, "What drove the Travel Money profit shortfall, and is eurochange integration complete?", "Consumer Services is the main revenue diversifier.", "Segment operating income by business"),
    (14, "How large is exposure to state remittance taxes (Tennessee and others) and the federal remittance excise tax?", "Taxes push customers toward cards and bank products or competitors.", "State-level volume and tax pass-through"),
    (15, "What is the tax position after the FY2024 tax benefit and falling cash taxes?", "Cash taxes fell to $74M TTM from $296M in FY2025, flattering OCF.", "IRS settlement and normalized cash tax rate"),
    (16, "Is there any substance to the August 2026 takeover rumor?", "A take-private at depressed multiples would cap downside but likely at a modest premium.", "13D filings, activist positions"),
]
for r, row in enumerate(questions, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 70
ws.column_dimensions["C"].width = 60
ws.column_dimensions["D"].width = 45

ws = wb.create_sheet("Sources")
title(ws, "WU Sources", 4)
headers(ws, 3, ["#", "Source", "URL", "Use"])
source_rows = [
    (1, "StockAnalysis overview", urls["overview"], "Price, range, news, earnings date"),
    (2, "StockAnalysis statistics", urls["statistics"], "Market value, ratios, shares, short interest, dividend"),
    (3, "StockAnalysis forecast", urls["forecast"], "Consensus revenue/EPS, targets and ratings"),
    (4, "StockAnalysis income statement", urls["income"], "Annual revenue, segments, margins"),
    (5, "StockAnalysis quarterly financials", urls["quarterly"], "Quarterly revenue, margins, EPS, FCF"),
    (6, "StockAnalysis balance sheet", urls["balance"], "Cash, debt, goodwill, equity"),
    (7, "StockAnalysis cash flow", urls["cashflow"], "OCF, capex, intangibles, dividends, buybacks"),
    (8, "StockAnalysis profile", urls["profile"], "Management and filings"),
    (9, "WU Q2 2026 earnings call", urls["q2call"], "Guidance cut, Beyond Efficiency, buyback pause, USDPT"),
    (10, "WU Q1 2026 earnings call", urls["q1call"], "Prior guidance, Intermex synergy commentary"),
    (11, "WU Q4 2025 earnings call", urls["q4call"], "FY2025 adjusted EPS and capital return"),
    (12, "WU 8-K Ex. 99.1 (Aug. 14, 2026)", urls["dfpi"], "NY DFS approval and California DFPI suspension"),
    (13, "WU 8-K (Oct. 2, 2026)", urls["hsr"], "New HSR filing and DFPI status"),
    (14, "StockAnalysis IMXI overview", urls["imxi"], "Intermex price for merger-spread analysis"),
    (15, "CNBC US 10-Year Treasury", urls["treasury"], "WACC risk-free rate"),
]
for r, row in enumerate(source_rows, 4):
    for c, value in enumerate(row, 1):
        put(ws, r, c, value, wrap=True)
ws.column_dimensions["A"].width = 7
ws.column_dimensions["B"].width = 34
ws.column_dimensions["C"].width = 90
ws.column_dimensions["D"].width = 55

for sheet in wb.worksheets:
    sheet.sheet_view.showGridLines = False

wb.save(OUT)
check = load_workbook(OUT, data_only=False)
expected = ["Valuation", "WACC", "Scenarios", "Actuals Source Audit", "Questions", "Sources"]
assert check.sheetnames == expected, check.sheetnames
assert check["Scenarios"]["C15"].value == weighted_fv
assert scen["Bear"]["target"] < PRICE < scen["Base"]["target"] < scen["Bull"]["target"]
print(f"WACC: {wacc:.2%}")
print(f"Company-defined FCF: ${FCF_COMPANY:.1f}M; net debt / FCF {NET_DEBT / FCF_COMPANY:.1f}x")
for k, s in scen.items():
    print(f"{k}: rev ${s['rev']:.0f}M, target ${s['target']:.2f} ({s['target'] / PRICE - 1:.1%}), FCF cross-check ${s['fcf_px']:.2f}")
print(f"Probability-weighted fair value: ${weighted_fv:.2f} ({weighted_fv / PRICE - 1:.1%})")
print(f"Analyst target cross-check: $6.66; model base difference {(scen['Base']['target'] / 6.66 - 1):.1%}")
print(f"Created {OUT}")
