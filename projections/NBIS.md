# NBIS Projection

Date: 2026-11-21
Company: Nebius Group N.V.
Ticker: NASDAQ: NBIS
Model: `models/NBIS/2026-11-21.xlsx`, rendered by `python3 -m capital.workbook NBIS 2026-11-21` from `data/NBIS/2026-11-21/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_NBIS_2026-11-21.py --projection`
Report: `research/updates/NBIS/2026-11-21.md` (initiation `research/NBIS.md`)
Price: $81.31 at the November 20, 2026 close (292.9M shares outstanding plus 21.1M NVIDIA pre-funded warrant shares; market cap $25.5B; enterprise value about $34.6B on unrestricted cash, before $9.41B of deferred revenue)

This is investment research support, not personalized financial advice.

Earnings are negative or near zero through 2029 in the bear and base (the bull turns positive in 2027), so years 1 to 3 cannot be priced on a P/E. The year-3 (FY2029) price is the call's end-2029 value: 2030 adjusted EBITDA at an exit EV/EBITDA, less end-2029 net debt, plus the equity stakes at book, over end-2029 shares (75% of deferred revenue deducted; capex at $40-42M per MW added, with the 2030 capacity fully paid by end-2029). Years 1 and 2 sit on a constant-return path from $81.31 to that value. The year-10 price is FY2036 EPS times an explicit terminal P/E anchor, and year 5 sits on a constant-return path from year 3 to year 10. Every row after FY2029 is extrapolated: revenue growth fades from the 2030 rate to the terminal rate by 2036, the 2030 adjusted EBITDA margin is held, D&A drifts toward a terminal share of revenue, capex is 1.1 times D&A, interest is charged on net debt at the case rate, tax is 21% on positive pre-tax income, and shares grow 1% a year from stock compensation.

## Analyst Estimate Anchor

| Source | As Of | Fiscal Year | Revenue | EPS | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| StockAnalysis (S&P Global) | 2026-11-16 | FY2026 | $3.16B | -$1.12 | $231.60 mean ($84-$380) | 22 | EPS non-GAAP; consensus Buy |
| StockAnalysis (S&P Global) | 2026-11-16 | FY2027 | $12.36B | -$3.04 | — | — | FY2028 behind the Pro paywall |
| LSEG via CNBC | 2026-11-12 | FY2026 / FY2027 | $3.37B / $11.98B | — | — | — | Before the guidance update |
| Company outlook | 2026-11-12 | FY2026 / FY2027 | low end of $3.0-3.4B / $12-13B | — | — | — | 2027 capex $40-45B; pre-tax breakeven in Q4 2027 |
| This projection (base) | 2026-11-21 | FY2027 | $12.33B | -$3.51 (GAAP) | — | — | GAAP includes D&A on a five-year GPU life and interest |

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| Q3 2026 revenue | $980.8M | +571% YoY; $325.1M of it one-off strategic-partnership revenue |
| Q3 revenue excluding partnerships | $655.7M | Q4 guide implies about $1.04B |
| Q3 adjusted EBITDA | $465.8M (47.5%) | AI cloud $518.2M (53.2%), including the partnership revenue |
| Q3 capex / 9M capex | $7.30B / $15.43B | FY2026 about $27B |
| Debt principal / unrestricted cash (Sept 30) | $16.48B / $7.43B | Plus $1.22B restricted; excludes the $3.5B Citi facility signed October 22 |
| Deferred revenue / RPO | $9.41B / $38.7B | 40% of RPO due within 24 months |

## Bear Projection

Terminal P/E anchor: none (equity worth nothing). GPU pricing resets toward $10-11M per MW and the build stops near 1.6 GW. Enterprise value at 5.0x 2030 EBITDA ($35.3B) is below end-2029 net debt ($42.0B), so the equity is worth nothing at the end of 2029 and stays underwater on these assumptions through 2036.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 9,000 | +200.0% | -2,108 | -3,536 | $-6.29 | n/m | n/m | n/m | n/m |
| 2 | FY2028 | 14,625 | +62.5% | -2,503 | -4,917 | $-8.74 | n/m | n/m | n/m | n/m |
| 3 | FY2029 | 16,675 | +14.0% | -3,238 | -5,830 | $-10.36 | n/m | $0.00 | n/m | -100% |
| 5 | FY2031 | 16,989 | +1.1% | -3,418 | -6,763 | $-11.78 | n/m | n/m | n/m | n/m |
| 10 | FY2036 | 18,987 | +3.0% | 1,139 | -5,484 | $-9.09 | n/m | n/m | n/m | n/m |

## Base Projection

Terminal P/E anchor: 16x FY2036 EPS of $19.78, terminal price $316.45. About 2.6 GW billing by end-2029 at a blended $15.5M per MW, 50% adjusted EBITDA margin by 2030, 6.0x exit EBITDA, capex at $40M per MW. GAAP net income stays near zero until depreciation on the 2027-2030 build levels off after 2031.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 12,325 | +310.8% | -125 | -1,497 | $-3.51 | -76.1% | $85.29 | n/m | +4.9% |
| 2 | FY2028 | 24,750 | +100.8% | 2,004 | -591 | $-1.39 | -55.6% | $89.46 | n/m | +4.9% |
| 3 | FY2029 | 34,875 | +40.9% | 3,283 | 80 | $0.19 | -25.2% | $93.84 | n/m | +4.9% |
| 5 | FY2031 | 48,107 | +16.4% | 3,390 | -1,075 | $-2.47 | -5.4% | $132.80 | n/m | +10.3% |
| 10 | FY2036 | 77,920 | +6.0% | 15,584 | 9,042 | $19.78 | 6.3% | $316.45 | 16.0x | +14.6% |

## Bull Projection

Terminal P/E anchor: 18x FY2036 EPS of $82.16, terminal price $1,478.91. About 1 GW a year delivered at near-today's pricing, 56% margin by 2030, 7.5x exit, every convertible series converts. The 2031-2036 rows extrapolate a business larger than any public cloud other than the hyperscalers; treat them as an illustration of the upside's shape, not a forecast.

| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 15,355 | +411.8% | 1,641 | 181 | $0.42 | -54.0% | $140.17 | n/m | +72.4% |
| 2 | FY2028 | 32,930 | +114.5% | 6,052 | 2,591 | $5.95 | -25.0% | $241.65 | 40.6x | +72.4% |
| 3 | FY2029 | 50,040 | +52.0% | 10,708 | 5,745 | $13.19 | -6.8% | $416.59 | 31.6x | +72.4% |
| 5 | FY2031 | 80,659 | +25.2% | 16,373 | 10,236 | $23.04 | 3.8% | $598.30 | 26.0x | +49.1% |
| 10 | FY2036 | 160,796 | +8.0% | 45,023 | 38,370 | $82.16 | 6.4% | $1,478.91 | 18.0x | +33.7% |

## Summary

| Case | Weight | End-2029 value | 10-year price | Terminal P/E anchor | 3-year CAGR | 10-year CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 35% | $0.00 | n/m | none | -100% | n/m |
| Base | 50% | $93.84 | $316.45 | 16x | +4.9% | +14.6% |
| Bull | 15% | $416.59 | $1,478.91 | 18x | +72.4% | +33.7% |
| Weighted fair value | | $109.41 | | | +10.4% | |

The weighted fair value matches `data/NBIS/2026-11-21/call.json`. The base path's year-5 P/E is not meaningful because 2031 earnings are close to zero after depreciation and interest; the terminal 16x assumes a mature, still-growing infrastructure business. The October projection (FY2031 values, `models/2026-10-27 Nebius Group Model.xlsx`) is superseded.

## Source Notes

- Q3 2026 6-K exhibits (accessions 0001104659-26-126008 and 0001104659-26-126238), FY2025 20-F, StockAnalysis forecast and press sources, all saved under `data/NBIS/2026-11-21/sources/`.
- Prices: `data/prices/NBIS.csv`. Extrapolation: all FY2030-FY2036 rows are scenario estimates, not consensus.
