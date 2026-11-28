# PK Projection

Date: 2026-11-26
Company: Park Hotels & Resorts Inc.
Ticker: NYSE: PK
Model: `models/PK/2026-11-26.xlsx`, rendered by `python3 -m capital.workbook PK 2026-11-26` from `data/PK/2026-11-26/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_PK_2026-11-26.py`
Report: `research/updates/PK/2026-11-26.md` (update); initiation `research/PK.md`
Price: $15.89 at the November 25, 2026 close (202.08M shares outstanding on October 30; market cap about $3.21B; company Net Debt $3,725M at September 30, 2026, so EV about $6.94B, 10.8x the 2026 Adjusted EBITDA guide midpoint)

This is investment research support, not personalized financial advice.

Years are calendar years. Adjusted EBITDA, net interest and Adjusted FFO are in millions of dollars on Park's own definitions; Adjusted FFO is before capital expenditure. Park is a lodging REIT, so GAAP net income is depressed by depreciation (about $266M in 2026) and is not the earnings measure here; the P/E columns of the house format are replaced by P/FFO on Adjusted FFO per diluted share. Stock prices work backward from an explicit year-10 terminal P/FFO anchor for each case, held constant from year 1. Each anchor is set so that the year-3 (2029) price equals the call's December 31, 2029 value, which is 2029 Adjusted FFO per share times the exit P/FFO plus the twelve dividends paid January 2027 through October 2029. The anchors are therefore above the exit multiples (5.5x / 7.5x / 9.0x) by the dividends: the 7.00x / 8.79x / 10.09x anchors are not multiples we expect the stock to trade at. Prices in other years are that anchor applied to each year's Adjusted FFO per share, not forecasts of where the stock trades.

## Analyst Estimate Anchor

| Source | As Of | Year | Revenue Consensus | Per-Share Consensus | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-11-20 | 2026 | $2.53B (-0.5%) | FFO $2.03; EPS $0.35 | $17.21 mean ($14-$21, median $17) | 18 | Consensus Hold; FCF estimate $125.4M |
| StockAnalysis (S&P Global) | 2026-11-20 | 2027 | $2.58B (+1.7%) | EPS $0.60 | — | — | FFO and 2028 estimates behind the Pro paywall |
| Company guidance | 2026-11-04 | 2026 | — | Adjusted FFO $2.00-$2.05; GAAP EPS $0.31-$0.36 | — | — | Adjusted EBITDA $635-$645M; capex $270-$280M; 201M diluted shares |
| Company commentary (Q3 call) | 2026-11-05 | 2027-2028 | — | — | — | — | About $30M a year of higher interest; 2027 capex $175-185M; Royal Palm $14M (2027) to $28M stabilized (2028); Hawaii recapture $60M+ |
| This projection (base) | 2026-11-26 | 2027 | — | Adjusted FFO $2.10 | — | — | Adjusted EBITDA $674M; net interest $232M |

Every row after 2026 is extrapolated from this report's assumptions; the only visible public per-share estimate past 2026 is the FY2027 GAAP EPS above.

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| 9M 2026 Adjusted FFO per share | $1.54 (Q3 $0.39) | Guide implies Q4 $0.46-$0.51 against $0.51 in Q4 2025 |
| 9M 2026 Adjusted EBITDA | $476M | Guide implies Q4 $159-$169M against $152M in Q4 2025 |
| Q3 2026 Comparable RevPAR / Total RevPAR | +8.4% / +5.6% | October preliminary RevPAR +11% |
| 9M 2026 OCF less capex | $315M - $204M = $111M | Dividends paid $150M; no buybacks |
| Net Debt / 2026 Adjusted EBITDA | $3,725M / $640M = 5.8x | $1.7B floating; no significant maturity before October 2028 |
| FY2026 starting point in the model | Adjusted EBITDA $640M; Adjusted FFO $2.025 | Guide midpoints; $640M - $215M net interest - $18M = $407M |

## Method

Adjusted FFO = Adjusted EBITDA - net interest - $18M of taxes, noncontrolling interests and joint-venture items, over diluted shares that start at the 201M in the 2026 guide and grow 0.5% a year from stock awards; the $18M is calibrated so the 2026 guide midpoints tie. Adjusted EBITDA grows organically from $640M (base +2% a year; bear -4% / -2% / +2%; bull +4% / +4% / +3.5%) and adds the Royal Palm ramp (base $11M / $21M / $25M over 2026) and the Hawaii recapture (base $10M / $20M / $30M). Net interest rises from $215M in 2026 to $232M in the 2027 base with the rest of the $30M refinancing headwind, and the 2028 and 2029 notes refinance at case-specific rates (near 7.75% / 6.5% / 6.0%; 2029: bear $264M, base $243M, bull $225M). Dividends are $0.25 a quarter; the bear carries a 50% chance of a cut to $0.18 from the October 2027 payment. FCF is Adjusted FFO less $175-185M of capex; FCF yield is that year's FCF over that year's price times shares. Remaining Non-Core sales are treated as neutral. Rows after 2029 extrapolate: organic growth moves linearly to a 2036 rate (bear +1%, base +2%, bull +2.5%) and net interest holds at its 2029 level.

## Bear Projection

Terminal P/FFO anchor: 7.00x, held from year 1.

| Years Out | Year | Adj. EBITDA ($M) | EBITDA Growth YoY | Net Interest ($M) | Adj. FFO ($M) | Adj. FFO/Share | FCF Yield | Stock Price | P/FFO | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 622 | -2.8% | 236 | 368 | 1.82 | 7.5% | $12.77 | 7.00x | -19.6% |
| 2 | 2028 | 626 | +0.6% | 240 | 368 | 1.81 | 7.5% | $12.69 | 7.00x | -10.6% |
| 3 | 2029 | 647 | +3.4% | 264 | 365 | 1.79 | 7.4% | $12.53 | 7.00x | -7.6% |
| 5 | 2031 | 669 | +1.6% | 264 | 387 | 1.88 | 7.8% | $13.16 | 7.00x | -3.7% |
| 10 | 2036 | 711 | +1.0% | 264 | 429 | 2.03 | 8.5% | $14.22 | 7.00x | -1.1% |

## Base Projection

Terminal P/FFO anchor: 8.79x, held from year 1.

| Years Out | Year | Adj. EBITDA ($M) | EBITDA Growth YoY | Net Interest ($M) | Adj. FFO ($M) | Adj. FFO/Share | FCF Yield | Stock Price | P/FFO | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 674 | +5.3% | 232 | 424 | 2.10 | 6.5% | $18.45 | 8.79x | +16.1% |
| 2 | 2028 | 707 | +4.9% | 230 | 459 | 2.26 | 6.9% | $19.87 | 8.79x | +11.8% |
| 3 | 2029 | 734 | +3.9% | 243 | 473 | 2.32 | 7.0% | $20.39 | 8.79x | +8.7% |
| 5 | 2031 | 762 | +1.9% | 243 | 501 | 2.43 | 7.3% | $21.36 | 8.79x | +6.1% |
| 10 | 2036 | 835 | +1.9% | 243 | 574 | 2.72 | 7.8% | $23.89 | 8.79x | +4.2% |

## Bull Projection

Terminal P/FFO anchor: 10.09x, held from year 1.

| Years Out | Year | Adj. EBITDA ($M) | EBITDA Growth YoY | Net Interest ($M) | Adj. FFO ($M) | Adj. FFO/Share | FCF Yield | Stock Price | P/FFO | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 697 | +8.8% | 222 | 457 | 2.26 | 5.9% | $22.81 | 10.09x | +43.6% |
| 2 | 2028 | 761 | +9.3% | 218 | 525 | 2.59 | 6.4% | $26.11 | 10.09x | +28.2% |
| 3 | 2029 | 804 | +5.7% | 225 | 561 | 2.75 | 6.6% | $27.77 | 10.09x | +20.5% |
| 5 | 2031 | 852 | +2.9% | 225 | 609 | 2.96 | 6.9% | $29.84 | 10.09x | +13.4% |
| 10 | 2036 | 965 | +2.3% | 225 | 722 | 3.42 | 7.4% | $34.48 | 10.09x | +8.1% |

## Summary

| Case | Weight | December 2029 value | 10-year price | Terminal P/FFO anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 30% | $12.53 | $14.22 | 7.00x | -7.6% | -1.1% |
| Base | 50% | $20.39 | $23.89 | 8.79x | +8.7% | +4.2% |
| Bull | 20% | $27.77 | $34.48 | 10.09x | +20.5% | +8.1% |
| Weighted fair value | | $19.51 | | | +7.1% | |

The weighted fair value matches `data/PK/2026-11-26/call.json`. The 10-year prices hold each anchor, which includes three years of dividends, so they overstate where the shares would trade and the 10-year CAGRs are not comparable with the 3-year ones. On price alone (exit P/FFO times 2029 Adjusted FFO per share) the cases are $9.84 / $17.39 / $24.77 and the weighted value is $16.60, 4% below the Street's $17.21 mean 12-month target. The exit multiples compare with PK's own year-end readings of 6.8x (end-2024) and 5.3x (end-2025) and 7.85x today on the 2026 guide, after a 2026 in which the lodging group rerated (PK +59%, HST and SHO +43%, PEB +90% from end-2025 to October); HST is about 11x net income plus D&A, which is not Adjusted FFO. The 15%-a-year entry price on these values is about $12.83. The cross-check at 9.0x / 10.5x / 12.0x 2029 Adjusted EBITDA less end-2029 net debt, plus dividends, gives $13.11 / $23.51 / $33.89; the P/FFO values imply 8.8x / 9.6x / 10.4x.
