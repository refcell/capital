# Projections: Personalis, Inc. (PSNL)

Model workbook: `[2026-08-25] PSNL Model.xlsx` in `models/`
Quote date: August 25, 2026
Current price: $17.25
Current shares outstanding: ~105.5M (implied from $1.82B MC / $17.25)
Current revenue (TTM): $69.7M
Primary framework: P/S + Cash NAV (P/E and FCF yield are N/A — company is structurally unprofitable)

**Analyst Estimate Anchors:**
| Period | Revenue Consensus | EPS Consensus (GAAP) | Analysts | Source |
|---|---|---|---|---|
| FY2026E | $82.5M | -$1.09 | 7 | Yahoo Finance Analysis |
| FY2027E | $110.2M | -$0.94 | 7 | Yahoo Finance Analysis |

**Extrapolation note:** Public analyst estimates are visible only through FY2027. Revenue and margin assumptions for years 3-10 are extrapolated from the consensus trajectory, historical gross margin trends, and scenario logic documented in the model workbook. P/E ratios are shown as "N/A" because the company remains unprofitable through year 5 in all scenarios. Stock prices work backward from explicit year-10 terminal P/S anchors (Bear: 8x, Base: 15x, Bull: 25x).

---

## Bear Case

*Assumptions: Revenue CAGR 12%, terminal gross margin 14%, dilution factor 1.50x, exit P/S 8x*

| Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | FCF Yield | Stock Price | P/E | CAGR from $17.25 |
|---|---|---|---|---|---|---|---|---|
| 1 | 78 | +12% | -103 | -101 | N/A | $12.40 | N/A | -28% |
| 2 | 87 | +12% | -101 | -99 | N/A | $11.10 | N/A | -36% |
| 3 | 98 | +13% | -99 | -97 | N/A | $9.70 | N/A | -44% |
| 5 | 126 | +12% | -108 | -106 | N/A | $7.80 | N/A | -55% |
| 10 | 126 | 0% | -110 | -108 | N/A | $6.38 | N/A | -63% |

*Year-10 terminal anchor: 8x P/S on $126M revenue = $1.01B MC / 158.3M diluted shares = $6.38*
*Cash/Share floor (current): $212.7M / 105.5M = $2.01 — approaching this by year 10 as cash drains from burn*

---

## Base Case

*Assumptions: Revenue CAGR 20%, terminal gross margin 22%, dilution factor 1.30x, exit P/S 15x*

| Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | FCF Yield | Stock Price | P/E | CAGR from $17.25 |
|---|---|---|---|---|---|---|---|---|
| 1 | 83 | +19% | -82 | -80 | N/A | $16.90 | N/A | -2% |
| 2 | 99 | +20% | -79 | -77 | N/A | $16.80 | N/A | -3% |
| 3 | 119 | +20% | -76 | -74 | N/A | $17.00 | N/A | -1% |
| 5 | 173 | +20% | -69 | -67 | N/A | $18.50 | N/A | +3% |
| 10 | 173 | 0% | -70 | -68 | N/A | $18.96 | N/A | +10% |

*Year-10 terminal anchor: 15x P/S on $173M revenue = $2.60B MC / 137.1M diluted shares = $18.96*
*Extrapolated beyond FY2027 consensus: Revenue plateaus at $173M as growth normalizes; operating losses persist but are manageable with cash runway*

---

## Bull Case

*Assumptions: Revenue CAGR 32%, terminal gross margin 30%, dilution factor 1.15x, exit P/S 25x*

| Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | FCF Yield | Stock Price | P/E | CAGR from $17.25 |
|---|---|---|---|---|---|---|---|---|
| 1 | 83 | +19% | -72 | -70 | N/A | $24.90 | N/A | +44% |
| 2 | 110 | +32% | -55 | -53 | N/A | $34.70 | N/A | +101% |
| 3 | 145 | +32% | -38 | -36 | N/A | $44.50 | N/A | +158% |
| 5 | 290 | +32% | +14 | +12 | +0.7% | $58.00 | 483x | +236% |
| 10 | 290 | 0% | +35 | +30 | +1.8% | $59.80 | 225x | +247% |

*Year-10 terminal anchor: 25x P/S on $290M revenue = $7.26B MC / 121.4M diluted shares = $59.80*
*Extrapolated: Revenue growth of 32% requires Tempus partnership achieving broad commercial adoption and gross margin recovery to FY2024 peak levels. Operating profitability only achieved in year 5 if gross margin reaches 30% and revenue hits $290M — both are stretch assumptions.*
*P/E in year 10 is mechanically distorted — small net income on large MC produces extreme P/E. P/S is the more meaningful metric.*

---

## Scenario Summary

| Metric | Bear (25%) | Base (50%) | Bull (25%) | Weighted FV |
|---|---|---|---|---|
| Revenue CAGR | 12% | 20% | 32% | — |
| Terminal P/S | 8x | 15x | 25x | — |
| Dilution Factor | 1.50x | 1.30x | 1.15x | — |
| Target Price | $6.38 | $18.96 | $59.80 | **$26.03** |
| Upside from $17.25 | -63% | +10% | +247% | **+51%** |

## Key Risk Metrics

| Metric | Value | Note |
|---|---|---|
| Cash per share (current) | $2.01 | Absolute floor if business fails entirely |
| Annual cash burn (TTM OCF) | -$92.3M | ~9 quarters of runway at current cash levels |
| Gross margin (TTM) | 12.7% | Collapsed from 31.7% FY24 — primary variable |
| Dilution history (3yr) | 113% | 45.7M → 97.6M shares — per-share destruction |
| Analyst avg PT | $15.44 | Below current $17.25 — consensus sees limited upside |
| FY2026 EPS consensus | -$1.09 | Worse than FY25 (-$0.91) — losses deepening |
| Next earnings | Nov 3, 2026 | Q3 FY26 — first gross margin trajectory signal |

This projection sheet is generated from the `[2026-08-25] PSNL Model.xlsx` workbook and uses the same P/S + Cash NAV framework. The company's pre-profitability status makes P/E and FCF yield metrics inapplicable through year 3 in all scenarios and through year 5 in the base/bear cases. Revenue growth after year 2 is extrapolated from the FY2027 consensus of $110.2M and does not reflect any specific analyst forecasts beyond that horizon.
