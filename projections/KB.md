# KB Projection

Date: 2026-11-12
Company: KB Financial Group Inc.
Ticker: NYSE: KB (ADS; one ADS = one common share, Korea Exchange 105560)
Model: `models/KB/2026-11-12.xlsx`, rendered by `python3 -m capital.workbook KB 2026-11-12` from `data/KB/2026-11-12/call.json` and `inputs.json`
Report: `research/KB.md`
Price: $114.75 at the November 11, 2026 close (KRW 153,984 at USD/KRW 1,341.91; 347.15M shares, market cap $39.8B)

This is investment research support, not personalized financial advice.

Bank framework: stock prices work backward from an explicit year-10 terminal **P/B** anchor for each case, held constant from year 1. P/E is shown as the implied cross-check. FCF yield is not meaningful for a bank and is replaced by shareholder yield (dividends plus buybacks over market value).

## Analyst Estimate Anchor

| Source | As Of | Fiscal Year | EPS Consensus (KRW) | Revenue Consensus (KRW) | Target | Analysts | Notes |
|---|---|---|---:|---:|---:|---:|---|
| Yahoo Finance quoteSummary | 2026-11-12 | FY2026 | 18,660.7 | 19.13T | $168.02 | 1 | Single analyst; revenue definition not stated |
| Yahoo Finance quoteSummary | 2026-11-12 | FY2027 | 20,375.6 | 19.70T | — | 1 | |
| StockAnalysis forecast | 2026-11-12 | — | — | — | — | — | Page returned 404 |
| This projection (base) | 2026-11-12 | FY2027 | 18,127 | 19.98T | — | — | Net operating revenue as defined below |

Every row beyond FY2027 is extrapolated; there is no visible public estimate past FY2027.

## Run-Rate Sanity Check

| Metric | Value | Read |
|---|---:|---|
| TTM profit to parent | KRW 6.35T | Q4 2025 711B + Q1-Q3 2026 after the November 12 amendment |
| 9M 2026 profit to parent | KRW 5.64T | +10.2% year on year |
| FY2026 estimate | KRW 6.44T | Assumes KRW 800B in a seasonally weak Q4 |
| Common BVPS (Sep-26 est.) | KRW 163,843 | June 30 equity less hybrids, rolled forward |
| P/B | 0.94x | 10-year year-end range 0.37x-0.81x |
| ROE on common (FY2026 est.) | ~11.0% | FY2025 about 10.5% |
| CET1 (Dec-25) | 13.82% | Policy returns capital above 13% / 13.5% |
| 2026 buybacks | KRW 1.90T | All for cancellation |
| Trailing dividend | KRW 5,070 | 3.3% yield |

## Method

The model starts from estimated end-2026 common equity of KRW 57.2T on 347.15M shares (BVPS KRW 164,795). Each year, profit to common is ROE times beginning common equity; a fixed share goes to dividends and a fixed share to buybacks at a stated price-to-book, and bought shares are cancelled. Bear: ROE 8.5%, 25% dividends, 20% buybacks at 0.80/0.70/0.60x book, then 0.55x. Base: ROE 11.0%, 27% and 28% at 0.93/0.94/0.95x book. Bull: ROE 12.5%, 28% and 32% at 1.00/1.10/1.15x, then 1.20x. The same drivers run unchanged from FY2030 to FY2036.

Net income in the tables is profit to parent shareholders, which is profit to common plus about KRW 200B of hybrid distributions. Pre-tax profit grosses net income up at the 27.5% statutory rate. Net operating revenue (operating profit before provisions plus G&A; FY2025 KRW 17.95T, FY2026 estimate about KRW 19.8T) is backed out from net income at a margin of 27% (bear), 32.5% (base) and 34.5% (bull); FY2025's margin was 32.5%. Revenue is an output here, not a driver.

Stock price is that year's end BVPS times the case's P/B anchor, converted at a constant KRW 1,341.91 per dollar. "Value incl. dividends" adds dividends received from 2027 through that year, undiscounted; the 3-year value equals the call's bear, base and bull values. CAGR is computed on that value.

## Bear Projection

Terminal P/B anchor: 0.55x (about 7.0x earnings), slightly below the end-2024 level of 0.59x. Credit costs rise above KRW 3T a year, fee income fades, regulators keep fining the group, and buybacks are cut to hold CET1 near 13%.

| Years Out | Fiscal Year | Net Operating Revenue (KRW tn) | Revenue Growth YoY | Pre-Tax Profit (KRW tn) | Net Income (KRW tn) | EPS (KRW) | BVPS (KRW) | Shareholder Yield | Stock Price (USD/ADS) | Value incl. Dividends (USD) | P/E | P/B | CAGR From Current (value) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 18.75 | -5.3% | 6.98 | 5.06 | 14,008 | 176,245 | 6.6% | $72.24 | $74.85 | 6.9x | 0.55x | -34.8% |
| 2 | FY2028 | 19.59 | +4.5% | 7.30 | 5.29 | 14,981 | 189,076 | 6.6% | $77.50 | $82.90 | 6.9x | 0.55x | -15.0% |
| 3 | FY2029 | 20.47 | +4.5% | 7.62 | 5.53 | 16,071 | 203,686 | 6.6% | $83.48 | $91.88 | 7.0x | 0.55x | -7.1% |
| 5 | FY2031 | 22.36 | +4.5% | 8.33 | 6.04 | 18,701 | 237,639 | 6.6% | $97.40 | $112.50 | 7.0x | 0.55x | -0.4% |
| 10 | FY2036 | 27.91 | +4.5% | 10.39 | 7.54 | 27,495 | 349,390 | 6.6% | $143.20 | $180.39 | 7.0x | 0.55x | +4.6% |

## Base Projection

Terminal P/B anchor: 0.95x (about 9.4x earnings), roughly today's multiple, above every 2016-2025 year-end level (maximum 0.81x), and the justified P/B for an 11% ROE against an 11% cost of equity. Fee income settles, net interest income grows 2-4% a year, one regulatory charge lands each year, and the payout holds near 55%.

| Years Out | Fiscal Year | Net Operating Revenue (KRW tn) | Revenue Growth YoY | Pre-Tax Profit (KRW tn) | Net Income (KRW tn) | EPS (KRW) | BVPS (KRW) | Shareholder Yield | Stock Price (USD/ADS) | Value incl. Dividends (USD) | P/E | P/B | CAGR From Current (value) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 19.98 | +0.9% | 8.96 | 6.49 | 18,127 | 178,877 | 6.1% | $126.64 | $130.28 | 9.4x | 0.95x | +13.5% |
| 2 | FY2028 | 20.94 | +4.8% | 9.39 | 6.80 | 19,676 | 194,091 | 6.1% | $137.41 | $145.01 | 9.4x | 0.95x | +12.4% |
| 3 | FY2029 | 21.94 | +4.8% | 9.84 | 7.13 | 21,350 | 210,523 | 6.1% | $149.04 | $160.94 | 9.4x | 0.95x | +11.9% |
| 5 | FY2031 | 24.11 | +4.8% | 10.81 | 7.83 | 25,118 | 247,681 | 6.1% | $175.34 | $196.96 | 9.4x | 0.95x | +11.4% |
| 10 | FY2036 | 30.53 | +4.8% | 13.68 | 9.92 | 37,711 | 371,854 | 6.1% | $263.25 | $317.33 | 9.4x | 0.95x | +10.7% |

## Bull Projection

Terminal P/B anchor: 1.20x (about 10.4x earnings), above any year-end level in the past decade. Fee income holds near 2026 levels, credit costs stay near 0.45% of loans, and the payout rises to 60%.

| Years Out | Fiscal Year | Net Operating Revenue (KRW tn) | Revenue Growth YoY | Pre-Tax Profit (KRW tn) | Net Income (KRW tn) | EPS (KRW) | BVPS (KRW) | Shareholder Yield | Stock Price (USD/ADS) | Value incl. Dividends (USD) | P/E | P/B | CAGR From Current (value) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | FY2027 | 21.31 | +7.6% | 10.14 | 7.35 | 20,599 | 180,245 | 6.0% | $161.18 | $165.48 | 10.5x | 1.20x | +44.2% |
| 2 | FY2028 | 22.34 | +4.9% | 10.63 | 7.71 | 22,531 | 196,399 | 6.0% | $175.63 | $184.63 | 10.5x | 1.20x | +26.8% |
| 3 | FY2029 | 23.43 | +4.9% | 11.15 | 8.08 | 24,550 | 213,650 | 6.0% | $191.06 | $205.18 | 10.4x | 1.20x | +21.4% |
| 5 | FY2031 | 25.77 | +4.9% | 12.27 | 8.89 | 29,009 | 252,074 | 6.0% | $225.42 | $251.16 | 10.4x | 1.20x | +17.0% |
| 10 | FY2036 | 32.74 | +4.9% | 15.58 | 11.29 | 43,862 | 381,145 | 6.0% | $340.84 | $405.64 | 10.4x | 1.20x | +13.5% |

## Probability-Weighted View

| Case | 3-Year Value | Weight | Contribution |
|---|---:|---:|---:|
| Bear | $91.88 | 25% | $22.97 |
| Base | $160.94 | 50% | $80.47 |
| Bull | $205.18 | 25% | $51.30 |
| Fair value | $154.74 | 100% | +10.5% a year from $114.75 |

## Notes

- All rows after FY2027 are extrapolated beyond visible public estimates; the only visible consensus is one analyst on Yahoo Finance.
- Year-1 prices apply the terminal multiple immediately, so the bear year-1 row (-34.8%) overstates a one-year loss; read the 3-, 5- and 10-year rows for valuation.
- Currency is held at KRW 1,341.91 per dollar throughout. The won traded between 1,322 and 1,554 over the past year; a 10% move in the won moves every USD figure by about 10%.
- Base FY2027 EPS of KRW 18,127 is 11% below the single visible estimate (KRW 20,376) because the base assumes part of 2026's brokerage fee surge does not recur.
