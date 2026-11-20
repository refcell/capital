# CRS Projection

Date: 2026-11-18
Company: Carpenter Technology Corporation
Ticker: NYSE: CRS
Model: `models/CRS/2026-11-18.xlsx`, rendered by `python3 -m capital.workbook CRS 2026-11-18` from `data/CRS/2026-11-18/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_CRS.py`
Report: `research/CRS.md`
Price: $269.68 at the November 17, 2026 close (49.54M shares outstanding, 50.0M diluted in Q1 FY2027; market cap $13.36B; EV $14.01B including $109.4M of pension and postretirement liabilities)

This is investment research support, not personalized financial advice.

Fiscal years end June 30 (FY2027 is July 2026 to June 2027). Stock prices work backward from an explicit year-10 terminal P/E anchor for each case, held constant from year 1. Each anchor is set so that the year-3 (FY2029) price equals the call's June 2029 value, which comes from FY2029 operating income times an exit EV/EBIT plus June 2029 net cash and dividends paid. Prices in other years are that multiple applied to each year's GAAP EPS, not forecasts of where the stock trades.

## Analyst Estimate Anchor

| Source | As Of | Fiscal Year | Revenue Consensus | EPS Consensus | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-10-26 | FY2027 | $3,436.6M | $13.44 | $438 mean ($315-$520) | 8 | EPS non-GAAP adjusted; 7 analysts on estimates; targets checked 2026-11-18 |
| StockAnalysis (S&P Global) | 2026-10-26 | FY2028 | $3,786.0M | $15.98 | — | — | FY2029 is behind the Pro paywall |
| Company guidance | 2026-10-22 | FY2027 | — | — | — | — | Operating income $850-880M, FCF $400-430M, capex $355-375M |
| Company target | 2026-10-22 | FY2029 | — | — | — | — | Operating income $1.2-1.3B; "not the peak" |
| This projection (base) | 2026-11-18 | FY2027 | $3,420M | $13.25 (GAAP) | — | — | Operating income $860M |

Every row beyond FY2028 is extrapolated; there is no visible public estimate past FY2028, and FY2029 rows rest on the company target, trimmed in the base.

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| Q1 FY2027 operating income | $196.4M | +28% year over year, -5% sequentially (planned maintenance) |
| Q2 FY2027 guide | $192-197M | Second half must average about $228-246M a quarter to reach the FY2027 guide |
| TTM revenue / operating margin | $3,188.7M / 23.4% | FY2019 prior peak margin 10.1% |
| SAO adjusted operating margin | 37.7% | Record 37.8% in Q4 FY2026 |
| TTM FCF | $340.8M | Capex $277.8M during the brownfield build |
| Net debt incl. benefit liabilities | $649.9M | 0.6x net debt/EBITDA; notes due 2034 |

## Method

Revenue, operating income and capex for FY2027-FY2029 are set per case (base: $3.42B / $3.76B / $4.10B revenue and $860M / $1,000M / $1,130M operating income). Net income taxes operating income less net interest (5.625% on $700M of notes, less $16M of capitalized interest in FY2027, less 3.5% on positive cash) at 21%. FCF is net income plus D&A ($150M in FY2027, 4.3% of revenue after) and stock compensation (0.9% of revenue), less capex, 20% of each year's revenue increase for working capital and $19M of pension cash. FCF after dividends ($0.20 a quarter) accrues as cash instead of buying back stock at an assumed price; diluted shares grow 0.4% a year from 50.0M. FY2027 FCF excludes the Q1 actual (-$24.8M), already in September 30 cash. FCF yield is that year's FCF over that year's price times shares. Rows after FY2029 extrapolate: revenue growth fades linearly to the FY2036 rate, operating margin moves to its terminal level by FY2032, and capex is 5% of revenue.

## Bear Projection

Terminal P/E anchor: 16.8x on FY2036 GAAP EPS. Revenue falls back to $3.2B by FY2029 as the aerospace supply chain destocks and pricing flattens, then grows 2% a year by FY2036. Operating income peaks at $800M in FY2027 (below the guide) and slides to $720M in FY2029, a 22.5% margin, and to 22% by FY2032. The June 2029 value ($187.98) is 12x FY2029 operating income plus $761M of net cash and $2.20 of dividends.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 3,300 | +5.6% | 800 | 618 | $12.31 | 3.7% | $206.64 | 16.8x | -23.4% |
| 2 | FY2028 | 3,250 | -1.5% | 760 | 584 | $11.59 | 5.5% | $194.61 | 16.8x | -15.1% |
| 3 | FY2029 | 3,200 | -1.5% | 720 | 567 | $11.20 | 5.9% | $187.98 | 16.8x | -11.3% |
| 5 | FY2031 | 3,150 | -0.5% | 698 | 578 | $11.34 | 5.9% | $190.38 | 16.8x | -6.7% |
| 10 | FY2036 | 3,309 | +2.0% | 728 | 678 | $13.04 | 5.7% | $218.84 | 16.8x | -2.1% |

## Base Projection

Terminal P/E anchor: 22.9x on FY2036 GAAP EPS. Revenue grows about 9.5% a year to $4.10B in FY2029 as the Athens brownfield adds volume from FY2028, then fades to 5% by FY2036. Operating income reaches $1.13B in FY2029 (27.6% margin, 6% below the low end of the company target) and the margin moves to 28% by FY2032. The June 2029 value ($404.56) is 17x FY2029 operating income plus $1,150M of net cash and $2.20 of dividends.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 3,420 | +9.5% | 860 | 665 | $13.25 | 2.6% | $303.43 | 22.9x | +12.5% |
| 2 | FY2028 | 3,760 | +9.9% | 1,000 | 774 | $15.36 | 3.7% | $351.71 | 22.9x | +14.2% |
| 3 | FY2029 | 4,100 | +9.0% | 1,130 | 894 | $17.67 | 4.0% | $404.56 | 22.9x | +14.5% |
| 5 | FY2031 | 4,798 | +7.9% | 1,336 | 1,103 | $21.62 | 4.1% | $495.06 | 22.9x | +12.9% |
| 10 | FY2036 | 6,467 | +5.0% | 1,811 | 1,644 | $31.59 | 4.2% | $723.28 | 22.9x | +10.4% |

## Bull Projection

Terminal P/E anchor: 29.1x on FY2036 GAAP EPS. Revenue grows about 12% a year to $4.40B in FY2029 on higher LTA pricing and a fast brownfield ramp, then fades to 7% by FY2036. Operating income reaches $1.32B in FY2029 (30% margin, above the target). The June 2029 value ($602.05) is 22x FY2029 operating income, Carpenter's own median EV/EBIT, plus $1,314M of net cash and $2.20 of dividends.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 3,480 | +11.4% | 880 | 681 | $13.57 | 2.0% | $395.42 | 29.1x | +46.6% |
| 2 | FY2028 | 3,900 | +12.1% | 1,080 | 837 | $16.61 | 2.9% | $484.16 | 29.1x | +34.0% |
| 3 | FY2029 | 4,400 | +12.8% | 1,320 | 1,045 | $20.66 | 3.1% | $602.05 | 29.1x | +30.7% |
| 5 | FY2031 | 5,477 | +11.2% | 1,643 | 1,354 | $26.55 | 3.1% | $773.85 | 29.1x | +23.5% |
| 10 | FY2036 | 8,296 | +7.0% | 2,489 | 2,235 | $42.96 | 3.3% | $1,251.86 | 29.1x | +16.6% |

## Summary

| Case | Weight | June 2029 value | 10-year price | Terminal P/E anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 30% | $187.98 | $218.84 | 16.8x | -11.3% | -2.1% |
| Base | 45% | $404.56 | $723.28 | 22.9x | +14.5% | +10.4% |
| Bull | 25% | $602.05 | $1,251.86 | 29.1x | +30.7% | +16.6% |
| Weighted fair value | | $388.95 | | | +13.0% | |

The weighted fair value matches `data/CRS/2026-11-18/call.json`. The P/E anchors sit below Carpenter's own median trailing P/E (38.4x over 89 months, a history full of depressed earnings); the bear's is between its 25th percentile (15.0x) and the current 23.7x. The 15%-a-year entry price on these values is about $256 on the 3-year rating rule; over the actual 2.62 years to June 2029 the weighted value already implies 15.0% a year at $269.68.
