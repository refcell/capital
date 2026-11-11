# PRIM Projection

Date: 2026-11-10
Company: Primoris Services Corporation
Ticker: NYSE: PRIM
Model: `models/PRIM/2026-11-10.xlsx`, rendered by `python3 -m capital.workbook PRIM 2026-11-10` from `data/PRIM/2026-11-10/call.json` and `inputs.json`
Report: `research/PRIM.md`
Price: $71.24 at the November 9, 2026 close (52.53M shares, market cap $3.74B, net debt $0.58B)

This is investment research support, not personalized financial advice.

## Analyst Estimate Anchor

| Source | As Of | Fiscal Year | Low Revenue | Consensus Revenue | High Revenue | EPS Low | EPS Consensus | EPS High | Analysts | Notes |
|---|---|---|---|---|---|---|---|---|---:|---|
| StockAnalysis forecast (S&P Global) | 2026-11-10 | FY2026 | $6.8B | $7.07B | $7.5B | $2.11 | $2.23 | $2.40 | 16 | Adjusted (non-GAAP) EPS. Company guide is $2.10-2.25 adjusted, $1.20-1.35 GAAP. |
| StockAnalysis forecast (S&P Global) | 2026-11-10 | FY2027 | n/a | $8.03B | n/a | n/a | $5.32 | n/a | n/a | Headline only; detail is gated. |
| Company Q3 2026 release | 2026-11-03 | FY2026 | n/a | n/a | n/a | $2.10 | n/a | $2.25 | n/a | Adjusted EBITDA $290-310M; Energy gross margin target 6-8%, Utilities 10-12%. |
| This projection | 2026-11-10 | FY2027+ | Extrapolated | Extrapolated | Extrapolated | Extrapolated | Extrapolated | Extrapolated | n/a | Beyond visible public estimates; built from the scenario drivers in the call. |

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| TTM revenue | $7,058M | Down 6.8% from FY2025's $7,575M; Q3 revenue -10.4% |
| TTM gross margin | 8.5% | FY2025 10.7%; Q3 2026 10.5% |
| TTM operating margin | 2.4% | FY2025 5.4%; Q3 2026 4.9% |
| TTM net income / diluted EPS | $96.3M / $1.77 | FY2025 $274.9M / $5.02 |
| TTM FCF | $37.7M | OCF $151.8M less capex $114.1M; FY2025 FCF $340.5M |
| Net debt | $580.8M | Debt $784.3M, cash $203.5M at 9/30/2026; net cash $65.6M at 12/31/2025 |
| Backlog | $14.07B | Record; MSA $8.50B |
| Street target | $100.47 mean, $64-$127 | 16 analysts |

## Method

Each case starts from an estimated $7.00B of FY2026 revenue (nine-month $5,200.5M plus about $1.80B in Q4; the S&P consensus is $7.07B). FY2027-FY2029 follow the explicit drivers in `call.json`: revenue growth, GAAP operating margin, interest (re-based on the Q3 2026 run-rate of about $57M a year), tax rate and diluted shares. Adjusted EPS adds back intangible amortization (declining from about $52M in FY2027) and $21M of stock compensation, taxed at the case's effective rate, which is how the company's reconciliation treats adjustments. FY2030-FY2036 are extrapolated: bear revenue +1% a year at a flat 3.6% margin, $60M interest and flat shares; base +5% a year at 5.0% margin, $40M interest and 1% annual share reduction; bull +7% a year at 6.0% margin, $35M interest and 1.5% annual share reduction.

Stock prices work backward from an explicit year-10 terminal P/E anchor on adjusted EPS for each case, held constant across the horizon: bear 10x, base 13x, bull 17x (13.3x, 15.3x and 19.3x on FY2029 GAAP EPS). Price in each row is that year's adjusted EPS times the anchor, undiscounted, which is the same convention as the call's FY2029 value; the 3-year row therefore equals the call's bear, base and bull values. FCF yield is FCF divided by the implied market value, with FCF set at 70% (bear), 85% (base) and 90% (bull) of adjusted net income over a cycle; single years will swing with working capital.

## Bear Projection

Terminal P/E anchor: 10.0x adjusted EPS. Renewables volume keeps shrinking, gas and data-center work only partly replaces it, and Energy margins stay at the bottom of the 6-8% gross margin range. The multiple returns to the 2018-2023 range.

| Years Out | Fiscal Year | Revenue ($mm) | Revenue Growth YoY | Operating Income ($mm) | Net Income ($mm) | Adj EPS | FCF Yield | Stock Price | P/E (adj) | Price CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 7,070 | +1.0% | 226 | 116 | $3.08 | 7.0% | $30.83 | 10.0x | -56.7% |
| 2 | FY2028 | 7,141 | +1.0% | 250 | 131 | $3.32 | 7.0% | $33.21 | 10.0x | -31.7% |
| 3 | FY2029 | 7,212 | +1.0% | 260 | 138 | $3.43 | 7.0% | $34.26 | 10.0x | -21.7% |
| 5 | FY2031 | 7,357 | +1.0% | 265 | 141 | $3.38 | 7.0% | $33.77 | 10.0x | -13.9% |
| 10 | FY2036 | 7,732 | +1.0% | 278 | 151 | $3.32 | 7.0% | $33.19 | 10.0x | -7.4% |

## Base Projection

Terminal P/E anchor: 13.0x adjusted EPS, one point above the top of the 2018-2023 GAAP range once converted. The six legacy projects finish in Q4 2026, Utilities grows mid-single digits at 11-13% gross margin, and Energy margins recover to about 9% gross by 2028 as crews move to gas and electrical work. Profitability returns to the 2025 level, before amortization, by FY2029.

| Years Out | Fiscal Year | Revenue ($mm) | Revenue Growth YoY | Operating Income ($mm) | Net Income ($mm) | Adj EPS | FCF Yield | Stock Price | P/E (adj) | Price CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 7,525 | +7.5% | 324 | 193 | $4.59 | 6.5% | $59.67 | 13.0x | -16.2% |
| 2 | FY2028 | 8,052 | +7.0% | 370 | 229 | $5.28 | 6.5% | $68.68 | 13.0x | -1.8% |
| 3 | FY2029 | 8,575 | +6.5% | 412 | 261 | $5.92 | 6.5% | $76.96 | 13.0x | +2.6% |
| 5 | FY2031 | 9,454 | +5.0% | 473 | 307 | $6.82 | 6.5% | $88.69 | 13.0x | +4.5% |
| 10 | FY2036 | 12,066 | +5.0% | 603 | 400 | $8.82 | 6.5% | $114.70 | 13.0x | +4.9% |

## Bull Projection

Terminal P/E anchor: 17.0x adjusted EPS. FY2027 revenue meets the Street's $8.03B, data-center electrical and gas generation convert backlog quickly, and GAAP operating margin passes 2025's 5.4% by FY2029.

| Years Out | Fiscal Year | Revenue ($mm) | Revenue Growth YoY | Operating Income ($mm) | Net Income ($mm) | Adj EPS | FCF Yield | Stock Price | P/E (adj) | Price CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 7,945 | +13.5% | 381 | 237 | $5.46 | 5.3% | $92.74 | 17.0x | +30.2% |
| 2 | FY2028 | 8,740 | +10.0% | 463 | 299 | $6.67 | 5.3% | $113.45 | 17.0x | +26.2% |
| 3 | FY2029 | 9,613 | +10.0% | 538 | 356 | $7.84 | 5.3% | $133.20 | 17.0x | +23.2% |
| 5 | FY2031 | 11,006 | +7.0% | 660 | 447 | $9.76 | 5.3% | $166.00 | 17.0x | +18.4% |
| 10 | FY2036 | 15,437 | +7.0% | 926 | 637 | $14.36 | 5.3% | $244.05 | 17.0x | +13.1% |

## Probability-Weighted View

| Case | 3-Year Value | Weight | Contribution |
|---|---:|---:|---:|
| Bear | $34.26 | 30% | $10.28 |
| Base | $76.96 | 50% | $38.48 |
| Bull | $133.20 | 20% | $26.64 |
| Fair value | $75.40 | 100% | +1.9% a year from $71.24 |

## Notes

- Revenue for FY2027 onward is extrapolated beyond visible public estimates except the FY2027 headline consensus of $8.03B, which the bull case approaches ($7.95B).
- Year-1 and year-2 prices sit below the current price in the base case because the price column values each year on its own EPS, while the market prices the next year's recovery; read the 3-, 5- and 10-year rows for the valuation.
- Net income is GAAP; EPS and P/E are company-adjusted. The FY2027 base adjusted EPS of $4.59 is 14% below the Street's $5.32; the base reaches the Street's FY2027 number only in FY2028 ($5.28).
