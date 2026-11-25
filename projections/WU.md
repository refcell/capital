# WU Projection

Date: 2026-11-24
Company: The Western Union Company
Ticker: NYSE: WU
Model: `models/WU/2026-11-24.xlsx`, rendered by `python3 -m capital.workbook WU 2026-11-24` from `data/WU/2026-11-24/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_WU_2026-11-24.py`
Report: `research/updates/WU/2026-11-24.md` (update); initiation `research/WU.md`
Price: $6.24 at the November 23, 2026 close (313.5M diluted shares in Q3 2026; market cap about $1.95B; borrowings $2,900.2M at par less $1,098.0M of cash at September 30, 2026, so net debt about $1.80B and EV about $3.75B)

This is investment research support, not personalized financial advice.

Years are calendar years. Revenue and operating and net income are in millions of dollars and on Western Union's adjusted basis, which excludes Beyond program costs, severance, acquisition costs and the non-cash tax charge from the international reorganization. Stock prices work backward from an explicit year-10 terminal P/E anchor for each case, held constant from year 1. Each anchor is set so that the year-3 (2029) price equals the call's December 31, 2029 value, which is 2029 adjusted EPS times the exit P/E, plus dividends paid from the Q4 2026 payment through Q4 2029, less any Intermex litigation payment per share. The anchors are therefore above the exit P/Es (3.5x / 5.0x / 6.0x) by the dividends: the 4.35x / 6.99x / 7.60x anchors are not multiples we expect the stock to trade at. Prices in other years are that anchor applied to each year's EPS, not forecasts of where the stock trades.

## Analyst Estimate Anchor

| Source | As Of | Year | Revenue Consensus | Adjusted EPS Consensus | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-11-13 | 2026 | $4.00B (-1.2%) | $1.32 ($1.28-$1.36) | $6.73 mean ($6.00-$8.50, median $6.50) | 18 | Consensus Sell; FCF estimate $166.5M |
| StockAnalysis (S&P Global) | 2026-11-13 | 2027 | $4.11B (+2.8%) | $1.46 (+10.5%) | — | — | Updated three days after the Intermex termination; may still include Intermex. 2028 behind the Pro paywall |
| Company guidance | 2026-11-04 | 2026 | -2% to -1% excluding Intermex | $1.28-$1.38 | — | — | Adjusted tax rate 10-12%; capex about $190M |
| Company target (Beyond efficiency) | 2026-07-30 | 2026 / 2027 | — | — | — | — | $50M / $200M run-rate savings by year-end |
| This projection (base) | 2026-11-24 | 2027 | $3.91B | $1.34 | — | — | Includes the full-year exit from the Saudi account-payout partner; no Intermex |

Every row after 2026 is extrapolated from this report's assumptions; the only visible public estimates past 2026 are the FY2027 revenue and EPS above.

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| 9M 2026 adjusted EPS | $0.97 ($0.25 / $0.31 / $0.42) | Guide implies Q4 $0.31-$0.41 against $0.45 in Q4 2025 |
| Q3 2026 adjusted operating margin | 18% | 13% and 15% in Q1 and Q2; 20% in Q3 2025; helped by expense timing |
| 9M 2026 revenue / adjusted operating income | $3,005.2M / $454.1M | 15.1% margin; FY2025 $4,050.7M / $790.5M (19.5%) |
| 9M 2026 OCF less capex | $321.2M - $130.3M = $190.9M | Dividends paid $226.5M; buybacks paused |
| Gross / net leverage | 3.3x / 2.0x | Target 2.5-3.0x gross |
| FY2026 starting point in the model | Revenue $3,990M; adjusted EPS $1.33 | Guide midpoint |

## Method

Adjusted EPS = (revenue x adjusted operating margin - net interest + $3M of other income) x (1 - tax) / diluted shares. Revenue growth and the margin are set per case for 2027-2029 (base -2% / 0% / +1% and 16% / 16.5% / 16.5%); net interest is $145-155M in the base as the 2029 maturities refinance; tax is 12% (13% in the bear); diluted shares start at 313.5M and grow 1% a year from stock awards (1.5% in the bear; the bull buys back $100M a year in 2028-2029). Dividends are $0.235 a quarter in the bull, are halved from Q2 2027 in the bear, and in the base are held with an 85% chance and halved from Q2 2027 with a 15% chance (the value uses the weighted $2.86). Intermex litigation costs $0 / $50M / $300M, paid in 2027. FCF is adjusted net income plus $60M, less cash restructuring and $170-180M of capex (2026 OCF about $456M in the model against about $357M implied by the Street's $166.5M FCF); FCF yield is that year's FCF over that year's price times shares. Rows after 2029 extrapolate: revenue growth moves linearly to the 2036 rate (bear -1%, base +1%, bull +2%) and the margin holds at its 2029 level.

## Bear Projection

Terminal P/E anchor: 4.35x. North America retail keeps shrinking and digital pricing tightens: revenue falls 3.5%, 2% and 1% in 2027-2029, the Beyond savings are spent on commissions and pricing so the adjusted margin settles at 14%, and net interest rises to $170M. The board halves the dividend from Q2 2027 and Western Union pays $300M to Intermex, a forced close or damages of similar size. The December 2029 value ($4.11) is $0.94 of 2029 EPS at 3.5x plus $1.76 of dividends less $0.96 of litigation.

| Years Out | Year | Revenue ($M) | Revenue Growth YoY | Adj. Operating Income ($M) | Adj. Net Income ($M) | Adj. EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 3,850 | -3.5% | 558 | 358 | 1.12 | 13.7% | $4.89 | 4.35x | -21.6% |
| 2 | 2028 | 3,773 | -2.0% | 528 | 323 | 1.00 | 14.1% | $4.35 | 4.35x | -16.5% |
| 3 | 2029 | 3,736 | -1.0% | 523 | 310 | 0.94 | 13.7% | $4.11 | 4.35x | -13.0% |
| 5 | 2031 | 3,661 | -1.0% | 513 | 301 | 0.89 | 13.4% | $3.87 | 4.35x | -9.1% |
| 10 | 2036 | 3,482 | -1.0% | 487 | 279 | 0.77 | 12.7% | $3.33 | 4.35x | -6.1% |

## Base Projection

Terminal P/E anchor: 6.99x. Retail stabilizes slowly and digital growth offsets it from 2028: revenue is flat over three years after the 2027 Saudi exit, the $200M Beyond run-rate mostly offsets mix so the adjusted margin settles at 16.5% (below Q3's 18% and 2025's 19.5%), and the dividend holds with an 85% chance, covered about 1.05x by free cash flow in 2028-2029. The December 2029 value ($9.51) is $1.36 of 2029 EPS at 5.0x plus $2.86 of weighted dividends less $0.16 of litigation cost.

| Years Out | Year | Revenue ($M) | Revenue Growth YoY | Adj. Operating Income ($M) | Adj. Net Income ($M) | Adj. EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 3,910 | -2.0% | 626 | 426 | 1.34 | 9.4% | $9.39 | 6.99x | +50.5% |
| 2 | 2028 | 3,910 | +0.0% | 645 | 438 | 1.37 | 10.4% | $9.58 | 6.99x | +23.9% |
| 3 | 2029 | 3,949 | +1.0% | 652 | 440 | 1.36 | 10.4% | $9.51 | 6.99x | +15.1% |
| 5 | 2031 | 4,029 | +1.0% | 665 | 451 | 1.37 | 10.5% | $9.57 | 6.99x | +8.9% |
| 10 | 2036 | 4,234 | +1.0% | 699 | 481 | 1.39 | 10.7% | $9.70 | 6.99x | +4.5% |

## Bull Projection

Terminal P/E anchor: 7.60x. Migration flows recover and the new partnerships add volume: revenue grows 0%, 2% and 3%, the savings drop through to an 18.5% adjusted margin (still below 2025), buybacks of $100M a year resume in 2028 once gross leverage is inside 3.0x, and Intermex's suit fails. The December 2029 value ($14.50) is $1.91 of 2029 EPS at 6.0x plus $3.05 of dividends.

| Years Out | Year | Revenue ($M) | Revenue Growth YoY | Adj. Operating Income ($M) | Adj. Net Income ($M) | Adj. EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 3,990 | +0.0% | 678 | 476 | 1.52 | 9.0% | $11.55 | 7.60x | +85.1% |
| 2 | 2028 | 4,070 | +2.0% | 733 | 524 | 1.73 | 9.9% | $13.12 | 7.60x | +45.0% |
| 3 | 2029 | 4,192 | +3.0% | 776 | 562 | 1.91 | 10.1% | $14.50 | 7.60x | +32.5% |
| 5 | 2031 | 4,429 | +2.7% | 819 | 600 | 2.04 | 10.3% | $15.49 | 7.60x | +20.0% |
| 10 | 2036 | 4,958 | +2.0% | 917 | 687 | 2.33 | 10.7% | $17.72 | 7.60x | +11.0% |

## Summary

| Case | Weight | December 2029 value | 10-year price | Terminal P/E anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 35% | $4.11 | $3.33 | 4.35x | -13.0% | -6.1% |
| Base | 45% | $9.51 | $9.70 | 6.99x | +15.1% | +4.5% |
| Bull | 20% | $14.50 | $17.72 | 7.60x | +32.5% | +11.0% |
| Weighted fair value | | $8.62 | | | +11.4% | |

The weighted fair value matches `data/WU/2026-11-24/call.json`. The 10-year prices hold each anchor, which includes three years of dividends, so they overstate where the shares would trade and the 10-year CAGRs are not comparable with the 3-year ones. On price alone (exit P/E times 2029 EPS) the cases are $3.31 / $6.81 / $11.45 and the weighted value is $6.51, close to the Street's $6.73 mean 12-month target. The exit multiples on adjusted EPS (3.5x / 5.0x / 6.0x) are about 4.0-4.2x / 5.8-6.0x / 6.9-7.2x on GAAP EPS at a recurring adjusted-to-GAAP gap of 15-20%, against WU's own ten-year GAAP P/E 10th percentile of 3.9x, 25th of 5.6x and median of 7.1x. The 15%-a-year entry price on these values is about $5.67. The cross-check at 5.0x 2029 EBITDA less end-2029 net debt, plus dividends and less litigation, gives $5.59 / $10.05 / $13.66.
