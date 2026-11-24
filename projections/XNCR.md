# XNCR Projection

Date: 2026-11-23
Company: Xencor, Inc.
Ticker: NASDAQ: XNCR
Model: `models/XNCR/2026-11-23.xlsx`, rendered by `python3 -m capital.workbook XNCR 2026-11-23` from `data/XNCR/2026-11-23/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_XNCR_2026-11-23.py --projection`
Report: `research/updates/XNCR/2026-11-23.md` (initiation `research/XNCR.md`)
Price: $33.26 at the November 20, 2026 close (75.04M shares outstanding; market cap $2.50B; $555.7M of cash and marketable debt securities at September 30; no borrowed debt)

This is investment research support, not personalized financial advice.

Earnings are negative through 2029 in every case, so years 1 to 3 cannot be priced on a P/E. The year-3 (FY2029) price is the call's end-2029 sum of parts: net cash after 2027-2029 burn and equity raised, plus XmAb819 at peak sales x probability of approval x NPV-to-peak multiple, plus XmAb942, other pipeline and the royalty portfolio, less overhead and the OMERS liability left at end-2029, over end-2029 shares. Years 1 and 2 sit on a constant-return path from $33.26 to that value. The year-10 price is FY2036 EPS times an explicit terminal P/E (base 15x, bull 13x); the bear has no FY2036 earnings and is anchored on a $5.00 per-share value (residual cash and royalties). Year 5 sits on a constant-return path from year 3 to year 10. Every row is this call's extrapolation: the base FY2027 revenue of $90M sits below the $115.79M S&P Global consensus (see the base case), and no public estimate goes past FY2027. Net income is operating income plus net interest, taxed at 21% once positive. The FCF yield column is net income over market value, a close proxy here because stock comp and D&A ($35-45M a year) roughly offset capex and working capital.

## Analyst Estimate Anchor

| Source | As Of | Fiscal Year | Revenue | EPS | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-11-19 | FY2026 | $198.65M | -$2.30 | $43.83 mean ($26-$70) | 14 | Includes $105M of Alexion settlement revenue; EPS non-GAAP |
| StockAnalysis (S&P Global) | 2026-11-19 | FY2027 | $115.79M | -$3.79 | — | — | FY2028 behind the Pro paywall |
| Truist | 2026-11-04 | Q3 2026 | $63.0M consensus | -$0.33 | $40 (Buy) | — | Actual $116.5M and $0.50 |
| Company guidance | 2026-11-04 | YE2026 | — | — | — | — | $480-500M cash and debt securities; runway into 2029 |
| This projection (base) | 2026-11-23 | FY2027 | $90M | -$3.36 (GAAP) | — | — | Opex $400M |

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| Q3 2026 revenue | $116.5M | $77.4M Alexion settlement, $25.0M Astellas milestone; about $10M of recurring royalties |
| Q3 2026 R&D + G&A | $93.7M | G&A helped by a legal-expense recovery |
| 9M 2026 operating cash flow | -$120.6M | Includes $52.5M of Alexion cash in August |
| Cash and debt securities (Sept 30) | $555.7M | Plus $27.0M of Zenas stock; OMERS royalty liability $95.1M; Xencor funds shortfalls against OMERS's $35M annual amount |
| Implied Q4 2026 cash use | about $66M | From $555.7M to the $490M guide midpoint |
| Net cash per share | $6.26 | $555.7M less $65.2M of leases, over the 78.35M diluted shares the model starts from ($6.54 on 75.04M outstanding) |
| Pipeline and royalty premium | about $27.00 a share | Price less net cash per share |

## Bear Projection

Terminal anchor: $5.00 a share (no FY2036 earnings). The fuller 400 µg/kg cohort shows the confirmed response rate settling below about 25%, or a tolerability problem appears; the FDA declines an accelerated path, and XENITH-UC misses. Xencor cuts programs (2027-2029 burn $560M, including $22M of OMERS shortfall funding), raises $100M at $30 before the update and $50M at $10 after it, and lives on residual royalties and milestones. End-2029 value $1.70, after deducting about $44M of OMERS liability left at end-2029.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 70 | -64.8% | -310 | -300 | $-3.57 | -28.9% | $12.34 | n/m | -62.9% |
| 2 | FY2028 | 60 | -14.3% | -200 | -195 | $-2.17 | -47.4% | $4.58 | n/m | -62.9% |
| 3 | FY2029 | 60 | +0.0% | -140 | -140 | $-1.53 | -90.0% | $1.70 | n/m | -62.9% |
| 5 | FY2031 | 80 | +15.5% CAGR | -90 | -90 | $-0.96 | -41.7% | $2.31 | n/m | -41.3% |
| 10 | FY2036 | 110 | +6.6% CAGR | -50 | -50 | $-0.51 | -10.2% | $5.00 | n/m | -17.3% |

## Base Projection

Terminal P/E anchor: 15x FY2036 EPS of $6.51, terminal price $97.62. The confirmed response rate settles between about 25% and 45% in the full cohort, the Phase 3 against tivozanib starts around YE2027 and is enrolled by end-2029, and an accelerated approval in refractory ccRCC comes after 2029. FY2027 revenue is $90M of royalties and milestones, below the $115.79M consensus because it assumes about $50M of milestones against roughly $75M implied in consensus. XmAb819 reaches about $1.6B of sales by FY2036 on the way to a $2.0B peak, plus royalties; total revenue $2.0B. Xencor raises $600M at $32. End-2029 value $34.61.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 90 | -54.7% | -310 | -300 | $-3.36 | -10.0% | $33.70 | n/m | +1.3% |
| 2 | FY2028 | 110 | +22.2% | -330 | -325 | $-3.24 | -9.5% | $34.15 | n/m | +1.3% |
| 3 | FY2029 | 140 | +27.3% | -330 | -330 | $-3.24 | -9.4% | $34.61 | n/m | +1.3% |
| 5 | FY2031 | 450 | +79.3% CAGR | -150 | -150 | $-1.44 | -3.1% | $46.54 | n/m | +7.0% |
| 10 | FY2036 | 2,000 | +34.8% CAGR | 900 | 711 | $6.51 | 6.7% | $97.62 | 15.0x | +11.4% |

## Bull Projection

Terminal P/E anchor: 13x FY2036 EPS of $13.36, terminal price $173.62. The confirmed response rate holds at or above 45% in 25 or more patients, the FDA agrees an accelerated path, approval in refractory ccRCC comes around end-2029, and XmAb819 moves into earlier lines; XENITH-UC wins. Xencor raises $400M at $45 in 2027 and $400M at $55 in 2028. End-2029 value $84.25. The lower terminal multiple reflects a larger, maturing product base by 2036.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 115 | -42.1% | -315 | -305 | $-3.47 | -7.6% | $45.34 | n/m | +36.3% |
| 2 | FY2028 | 150 | +30.4% | -370 | -365 | $-3.74 | -6.0% | $61.80 | n/m | +36.3% |
| 3 | FY2029 | 250 | +66.7% | -350 | -350 | $-3.52 | -4.2% | $84.25 | n/m | +36.3% |
| 5 | FY2031 | 1,000 | +100.0% CAGR | 200 | 158 | $1.56 | 1.5% | $103.58 | 66.4x | +25.5% |
| 10 | FY2036 | 3,200 | +26.2% CAGR | 1,800 | 1,422 | $13.36 | 7.7% | $173.62 | 13.0x | +18.0% |

## Summary

| Case | Weight | End-2029 value | 10-year price | Terminal anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 30% | $1.70 | $5.00 | $5.00 a share | -62.9% | -17.3% |
| Base | 50% | $34.61 | $97.62 | 15x | +1.3% | +11.4% |
| Bull | 20% | $84.25 | $173.62 | 13x | +36.3% | +18.0% |
| Weighted fair value | | $34.66 | | | +1.4% | |

The weighted fair value matches `data/XNCR/2026-11-23/call.json`. FY2026 revenue growth in year 1 is measured from the $198.65M FY2026 consensus, which includes $105M of one-off settlement revenue. The October projection (today-values, `models/2026-10-29 Xencor Model.xlsx`) is superseded.

## Source Notes

- Q3 2026 10-Q and earnings release (accessions 0001326732-26-000063 and 0001326732-26-000062), the November 9 ACR release, StockAnalysis forecast page, Truist and J.P. Morgan notes, all saved under `data/XNCR/2026-11-23/sources/`.
- Prices: `data/prices/XNCR.csv`. Extrapolation: every row, including FY2027 in all three cases, is a scenario estimate, not consensus.
