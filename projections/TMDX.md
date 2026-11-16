# TMDX Projection

Date: 2026-11-15
Company: TransMedics Group, Inc.
Ticker: NASDAQ: TMDX
Model: `models/TMDX/2026-11-15.xlsx`, rendered by `python3 -m capital.workbook TMDX 2026-11-15` from `data/TMDX/2026-11-15/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_TMDX.py`
Report: `research/updates/TMDX/2026-11-15.md` (initiation `research/TMDX.md`)
Price: $91.38 at the November 13, 2026 close (34.73M shares outstanding, 35.94M diluted excluding the convertible; market cap $3.17B)

This is investment research support, not personalized financial advice.

Stock prices work backward from an explicit year-10 terminal P/E anchor for each case, held constant from year 1. Each anchor is set so that the year-3 (FY2029) price equals the call's end-2029 value, which comes from 2029 operating income times an exit EV/EBIT plus end-2029 net cash. Year-1 and year-2 prices are therefore that multiple applied to earnings still depressed by trial spending, not forecasts of where the stock trades.

## Analyst Estimate Anchor

| Source | As Of | Fiscal Year | Revenue Consensus | EPS Consensus | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-11-09 | FY2026 | $767.1M | $1.67 | $104.55 mean ($70-$125) | 13 | EPS non-GAAP adjusted; 12 analysts on estimates |
| StockAnalysis (S&P Global) | 2026-11-09 | FY2027 | $901.4M | $2.49 | — | — | FY2028 is behind the Pro paywall |
| Company guidance | 2026-11-05 | FY2026 | $764M-$774M | — | — | — | Includes about $14M of PAD Aviation |
| This projection (base) | 2026-11-15 | FY2027 | $885M | $2.21 (GAAP) | — | — | 11% below the Street's adjusted EPS; GAAP includes stock compensation |

Every row beyond FY2027 is extrapolated; there is no visible public estimate past FY2027.

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| Q3 2026 revenue | $203.0M | +41.1%; +34.6% organic |
| 9M 2026 revenue | $566.9M | +27.5% |
| Q3 2026 GAAP operating margin | 13.9% | 9M 11.5%; R&D $29.2M a quarter, nearly double a year earlier |
| Q3 product / service gross margin | 79.2% / 32.2% | Q1 77.5% / 26.5% |
| Q2 + Q3 2026 FCF | $37.8M | Q1 -$12.1M after the Somerville parcel purchase |
| TTM GAAP EPS | $3.67 | Includes the Q4 2025 tax-allowance release; 9M 2026 $1.08 |
| Cash / obligations due by mid-2028 | $493.0M / $889.6M | Convertible $460.0M, CIBC $55.0M, headquarters option $374.6M |
| Headquarters buildout | $200M-$240M | Through 2030; $13.8M spent, $57.5M committed |

## Method

Revenue starts from FY2026 of $765M / $770M / $775M. GAAP operating income is revenue times the case's margin path. Net income taxes operating income plus net interest (3.5% on net cash, which starts at September 30 cash less the $889.6M of obligations, assumed refinanced at no change in net debt) at 24%. FCF is revenue times the case's FCF margin; net cash changes by FCF, after-tax interest and the remaining headquarters buildout ($206M at the midpoint: $10M in Q4 2026, $60M, $60M, $50M and $26M in 2027-30). Diluted shares start at 35.94M and grow 2.4% / 1.8% / 1.35% a year from stock awards; the convertible's principal is a cash obligation and only shares above the $141.88 capped-call cap are added (bull, from 2028). FCF yield is that year's FCF over that year's price times shares. Rows after FY2029 extrapolate: growth fades linearly to the FY2036 rate and margins move to their terminal level by FY2033.

## Bear Projection

Terminal P/E anchor: 17.1x on FY2036 GAAP EPS. Revenue grows 8% a year to 2029, then fades to 4% by 2036; liver matures or loses share, lung keeps shrinking and the trials add little before 2030. GAAP operating margin stays near 11-12% as trial, kidney and Europe spending keep rising. The end-2029 value ($33.74) is 15x 2029 operating income less end-2029 net debt of $433M.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 826 | +8.0% | 87 | 56 | $1.51 | 4.4% | $25.77 | 17.1x | -71.8% |
| 2 | FY2028 | 892 | +8.0% | 98 | 63 | $1.68 | 4.9% | $28.74 | 17.1x | -43.9% |
| 3 | FY2029 | 964 | +8.0% | 116 | 76 | $1.98 | 5.2% | $33.74 | 17.1x | -28.3% |
| 5 | FY2031 | 1,106 | +6.9% | 133 | 90 | $2.23 | 5.0% | $38.12 | 17.1x | -16.0% |
| 10 | FY2036 | 1,421 | +4.0% | 171 | 130 | $2.85 | 4.5% | $48.63 | 17.1x | -6.1% |

## Base Projection

Terminal P/E anchor: 29.2x on FY2036 GAAP EPS. Revenue grows 15% a year to 2029, then fades to 7% by 2036. Operating margin rises from about 12% in 2026 to 13.5% in 2027 and 19% in 2029 as R&D levels off after the ENHANCE and DENOVO trials, and to 22% by 2033. The end-2029 value ($124.28) is 22x 2029 operating income less $183M of net debt.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 885 | +15.0% | 120 | 81 | $2.21 | 3.8% | $64.51 | 29.2x | -29.4% |
| 2 | FY2028 | 1,018 | +15.0% | 168 | 118 | $3.17 | 3.8% | $92.69 | 29.2x | +0.7% |
| 3 | FY2029 | 1,171 | +15.0% | 223 | 161 | $4.25 | 3.7% | $124.28 | 29.2x | +10.8% |
| 5 | FY2031 | 1,503 | +12.7% | 308 | 234 | $5.95 | 3.5% | $174.15 | 29.2x | +13.8% |
| 10 | FY2036 | 2,342 | +7.0% | 515 | 434 | $10.11 | 3.1% | $295.81 | 29.2x | +12.5% |

## Bull Projection

Terminal P/E anchor: 34.9x on FY2036 GAAP EPS. Revenue grows 23% a year to 2029, then fades to 10% by 2036, with heart and lung indications from the trials, Europe NOP and kidney. Operating margin reaches 15% in 2027, 24% in 2029 and 27% by 2033. The end-2029 value ($228.60) is 26x 2029 operating income less $22M of net debt, on shares that include about 1.9M convertible shares above the $141.88 cap.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 953 | +23.0% | 143 | 99 | $2.71 | 3.3% | $94.59 | 34.9x | +3.5% |
| 2 | FY2028 | 1,172 | +23.0% | 229 | 165 | $4.25 | 3.1% | $148.55 | 34.9x | +27.5% |
| 3 | FY2029 | 1,442 | +23.0% | 346 | 257 | $6.55 | 2.9% | $228.60 | 34.9x | +35.8% |
| 5 | FY2031 | 2,084 | +19.3% | 531 | 411 | $10.21 | 2.8% | $356.54 | 34.9x | +31.3% |
| 10 | FY2036 | 3,957 | +10.0% | 1,068 | 902 | $21.00 | 2.6% | $733.35 | 34.9x | +23.2% |

## Summary

| Case | Weight | End-2029 value | 10-year price | Terminal P/E anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 30% | $33.74 | $48.63 | 17.1x | -28.3% | -6.1% |
| Base | 50% | $124.28 | $295.81 | 29.2x | +10.8% | +12.5% |
| Bull | 20% | $228.60 | $733.35 | 34.9x | +35.8% | +23.2% |
| Weighted fair value | | $117.98 | | | +8.9% | |

The weighted fair value matches `data/TMDX/2026-11-15/call.json`. The P/E anchors sit below TransMedics' own median trailing P/E (63.5x over 25 months); the bear's is just above its 10th percentile (16.8x).
