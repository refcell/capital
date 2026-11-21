# STLA Projection

Date: 2026-11-20
Company: Stellantis N.V.
Ticker: NYSE: STLA
Model: `models/STLA/2026-11-20.xlsx`, rendered by `python3 -m capital.workbook STLA 2026-11-20` from `data/STLA/2026-11-20/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_STLA.py`
Report: `research/STLA.md`
Price: $3.54 at the November 19, 2026 close (EUR 3.23 at EUR/USD 1.0972; 2,902.1M diluted shares in Q3 2026; market cap $10.27B or EUR 9.36B; EV EUR 13.89B including EUR 4.93B of hybrid perpetual notes and EUR 5.00B of employee benefit liabilities, less EUR 5.40B of industrial net cash)

This is investment research support, not personalized financial advice.

Years are calendar years. Revenue, AOI and net income are in millions of euros; EPS is in euros; stock prices are in dollars at the November 19, 2026 EUR/USD rate, held constant. Stock prices work backward from an explicit year-10 terminal P/E anchor for each case, held constant from year 1. Each anchor is set so that the year-3 (2029) price equals the call's December 31, 2029 value, which is 2029 adjusted EPS times the exit P/E plus dividends paid in 2028-2029. Prices in other years are that multiple applied to each year's EPS, not forecasts of where the stock trades. A P/E on a loss gives no price, so loss years show "n.m.".

## Analyst Estimate Anchor

| Source | As Of | Year | Revenue Consensus | EPS Consensus | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-11-20 | 2026 | EUR 161,090M (159,100-163,400) | EUR 0.50 (0.36-0.61) | $6.39 mean ($3.92-$10) | 8 targets; 23 on estimates | Non-GAAP adjusted EPS |
| StockAnalysis (S&P Global) | 2026-11-20 | 2027 | EUR 164,460M | EUR 0.90 | — | — | Detail and 2028 behind the Pro paywall |
| Visible Alpha via Milano Finanza | 2026-11-18 | 2027 | — | — | — | — | AOI margin 2.3% |
| Oddo BHF | 2026-11-17 | 2027 | — | — | EUR 3.00 | 1 | AOI margin 1.6%; IFCF -EUR 2.2B |
| Company guidance | 2026-10-28 | 2026 | Mid-single-digit growth | — | — | — | Low-single-digit AOI margin; IFCF improved; positive IFCF in 2027 |
| Company targets (FaSTLAne 2030) | 2026-05-21 | 2028 / 2030 | EUR 175B / 190B | — | — | — | AOI margin 5% / 7%; IFCF EUR 3B / 6B |
| This projection (base) | 2026-11-20 | 2027 | EUR 164,500M | EUR 0.52 | — | — | AOI 2.3% (Visible Alpha consensus); EPS after a EUR 0.5B restructuring allowance |

Every row after 2027 is extrapolated from the company's 2028 and 2030 targets and this report's assumptions; there is no visible public consensus past 2027.

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| 9M 2026 AOI | EUR 1,989M (1.7%) | 9M 2025 EUR 630M (0.6%) |
| Q3 2026 AOI | EUR 256M (0.7%) | Summer shutdown quarter; beat the EUR 191M Reuters poll |
| Q4 2026 AOI needed for a 2.0% year | about EUR 1,230M | Q1 was EUR 960M, Q2 EUR 773M |
| 9M 2026 IFCF | -EUR 4,930M | 9M 2025 -EUR 7,309M; Q4 2025 recovered about EUR 2.8B |
| Industrial net cash | EUR 5,400M | Includes EUR 4,927M of hybrid notes |
| Industrial available liquidity | EUR 42,652M | 26% of TTM revenue; target 25-30% |

## Method

Revenue and AOI margin for 2027-2029 are set per case (base: EUR 164.5B / 169.5B / 175B and 2.3% / 3.6% / 4.2%). Net income is AOI less net financial expense (base EUR 0.85-0.9B) and a recurring allowance for restructuring and other unusual items (base EUR 0.5B), taxed at 27%, less EUR 0.26B of after-tax coupons on the hybrid perpetual notes; the bear adds a further EUR 3B hybrid at 8% in 2027. Diluted shares grow 10M a year from 2,902M; there are no buybacks. Dividends are 27% (base) or 30% (bull) of the prior year's net income, paid from 2028; none in the bear. FCF is the company's industrial free cash flow, set per case for 2027-2029 (base EUR 0 / 1.5B / 2.5B) and 60-70% of net income after 2029; FCF yield is that year's FCF over that year's price times shares, in euros. Rows after 2029 extrapolate: revenue growth fades linearly to the 2036 rate and the AOI margin moves to its terminal level by 2032.

## Bear Projection

Terminal P/E anchor: 4.00x on 2036 EPS. Cost inflation absorbs the Value Creation Program: the AOI margin is 1.2% in 2027, 1.8% in 2028 and 2.3% in 2029 on flat revenue, IFCF is -EUR 2.2B, -EUR 1.0B and zero, the rating falls to junk and financing costs rise to EUR 1.0-1.2B. After 2029 revenue grows 1.5% a year and the margin drifts to 2.8%. The December 2029 value ($1.25) is EUR 0.29 of EPS at 4x with no dividends; on cash terms (6.5x 2029 IFCF plus industrial net cash, less hybrids and benefit liabilities) the equity is worth less than nothing (-$2.33).

| Years Out | Year | Revenue (EUR M) | Revenue Growth YoY | AOI (EUR M) | Net Income (EUR M) | EPS (EUR) | FCF Yield | Stock Price (USD) | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 158,000 | -1.9% | 1,896 | -352 | -0.12 | n.m. | n.m. | n.m. | n.m. |
| 2 | 2028 | 160,000 | +1.3% | 2,880 | 293 | 0.10 | -85.2% | $0.44 | 4.00x | -64.7% |
| 3 | 2029 | 162,000 | +1.2% | 3,726 | 838 | 0.29 | 0.0% | $1.25 | 4.00x | -29.2% |
| 5 | 2031 | 166,251 | +1.3% | 4,378 | 1,314 | 0.45 | 15.0% | $1.95 | 4.00x | -11.2% |
| 10 | 2036 | 178,470 | +1.5% | 4,997 | 1,766 | 0.59 | 15.0% | $2.58 | 4.00x | -3.1% |

## Base Projection

Terminal P/E anchor: 4.31x on 2036 EPS. A partial recovery that misses the FaSTLAne 2030 path: revenue reaches EUR 175B in 2029 (the plan's 2028 figure, a year late), the AOI margin goes 2.3% (the consensus), 3.6% and 4.2% as about EUR 5B of further savings are offset by about EUR 3B of cost inflation, and IFCF goes 0, EUR 1.5B and EUR 2.5B. After 2029 growth fades to 2.5% and the margin reaches 5.0% by 2032, the plan's 2028 level. The December 2029 value ($6.59) is EUR 1.39 of EPS at 4x plus EUR 0.43 of dividends.

| Years Out | Year | Revenue (EUR M) | Revenue Growth YoY | AOI (EUR M) | Net Income (EUR M) | EPS (EUR) | FCF Yield | Stock Price (USD) | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 164,500 | +2.1% | 3,784 | 1,521 | 0.52 | 0.0% | $2.47 | 4.31x | -30.2% |
| 2 | 2028 | 169,500 | +3.0% | 6,102 | 3,177 | 1.09 | 11.0% | $5.14 | 4.31x | +20.5% |
| 3 | 2029 | 175,000 | +3.2% | 7,350 | 4,089 | 1.39 | 14.2% | $6.59 | 4.31x | +23.0% |
| 5 | 2031 | 185,965 | +3.0% | 8,802 | 5,149 | 1.74 | 16.2% | $8.25 | 4.31x | +18.4% |
| 10 | 2036 | 212,594 | +2.5% | 10,630 | 6,483 | 2.16 | 16.2% | $10.21 | 4.31x | +11.2% |

## Bull Projection

Terminal P/E anchor: 5.83x on 2036 EPS. The plan arrives about a year late: the AOI margin goes 3.0%, 4.6% and 5.8% on revenue of EUR 167B, 175B and 183B, North America returns above 8%, and IFCF goes EUR 1.0B, 3.0B and 4.5B. After 2029 growth fades to 3% and the margin reaches the plan's 7% by 2032. The December 2029 value ($14.51) is EUR 2.27 of EPS at 5.5x, below GM's and Ford's ten-year median P/E (6.4x and 6.7x), plus EUR 0.74 of dividends.

| Years Out | Year | Revenue (EUR M) | Revenue Growth YoY | AOI (EUR M) | Net Income (EUR M) | EPS (EUR) | FCF Yield | Stock Price (USD) | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027 | 167,000 | +3.7% | 5,010 | 2,526 | 0.87 | 6.8% | $5.55 | 5.83x | +56.7% |
| 2 | 2028 | 175,000 | +4.8% | 8,050 | 4,746 | 1.62 | 10.8% | $10.39 | 5.83x | +71.3% |
| 3 | 2029 | 183,000 | +4.6% | 10,614 | 6,654 | 2.27 | 11.6% | $14.51 | 5.83x | +60.0% |
| 5 | 2031 | 198,827 | +4.1% | 13,123 | 8,485 | 2.87 | 12.0% | $18.38 | 5.83x | +39.0% |
| 10 | 2036 | 235,557 | +3.0% | 16,489 | 10,942 | 3.64 | 12.0% | $23.31 | 5.83x | +20.7% |

## Summary

| Case | Weight | December 2029 value | 10-year price | Terminal P/E anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 35% | $1.25 | $2.58 | 4.00x | -29.2% | -3.1% |
| Base | 45% | $6.59 | $10.21 | 4.31x | +23.0% | +11.2% |
| Bull | 20% | $14.51 | $23.31 | 5.83x | +60.0% | +20.7% |
| Weighted fair value | | $6.30 | | | +21.2% | |

The weighted fair value matches `data/STLA/2026-11-20/call.json`. The bear and base anchors (4.00x and 4.31x) sit below GM's and Ford's ten-year 10th-percentile P/E (4.9x and 4.8x); the bull's 5.5x exit is below their 25th percentile (5.6x) and its 5.83x anchor sits between their 25th percentile and median (6.4x and 6.7x). Stellantis itself traded at 2.5-3.6x peak earnings in 2022-2023 and 6.8x depressed 2024 earnings. The 15%-a-year entry price on these values is about $4.14 on the 3-year rating rule. The FCF cross-check (6.5x 2029 IFCF plus end-2029 industrial net cash, less the hybrid notes and EUR 5.0B of employee benefit liabilities, plus dividends) gives about $6.44 in the base, $12.99 in the bull and -$2.33 in the bear.
