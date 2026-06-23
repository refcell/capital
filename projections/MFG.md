# MFG — Mizuho Financial Group, Inc. Projection Sheet

**Ticker:** NYSE: MFG
**Company:** Mizuho Financial Group, Inc.
**Quote Date:** 2026-06-22
**Close Price:** $10.15
**Model Workbook:** `models/2026-06-22 Mizuho Financial Group Model.xlsx`
**Primary Framework:** P/B × BVPS (bank-specific — FCF not applicable)
**Currency Note:** All fundamentals in JPY; prices in USD

---

## Current Anchors

| Metric | Value | Source |
|---|---|---|
| Closing Price | $10.15 | Yahoo Finance |
| Market Cap | $119.60B | Yahoo Finance |
| P/B (current) | 1.78x | Yahoo Finance statistics |
| BVPS | $5.79 | Yahoo Finance MRQ |
| ROE (TTM) | 11.44% | Yahoo Finance statistics |
| Revenue FY2026 | ¥4,317B | Yahoo Finance /financials |
| Net Income FY2026 | ¥1,249B | Yahoo Finance /financials |
| EPS (diluted, JPY) | ¥100.58 | Yahoo Finance /financials |
| Forward P/E | 15.53x | Yahoo Finance statistics |
| Shares Outstanding | 12.18B | Yahoo Finance statistics |

---

## Bear Case

**Assumptions:** ROE normalizes to 8% as BOJ rate policy stabilizes/cuts. NII compresses. P/B mean-reverts to 1.30x (historical Japanese bank average). BVPS compounds at 5-6% annually (ROE × retention of ~80% = ~6.4%).

| Horizon | BVPS | Price (×1.30) | P/E Implied | Rev. Growth Implied |
|---|---:|---:|---:|---:|
| 1-yr | $6.13 | $8.00 | ~14.5x | ~5% |
| 2-yr | $6.50 | $8.45 | ~13.8x | ~4% |
| 3-yr | $6.90 | $8.97 | ~13.4x | ~3% |
| 5-yr | $7.75 | $10.08 | ~12.8x | ~2% |
| 10-yr | $10.00 | $13.00 | ~12.0x | ~1% |

Stock-price CAGR from $10.15: 1-yr: -21%, 5-yr: 2.1%, 10-yr: 5.3%

**Year-10 terminal anchor:** P/E of 12.0x based on fully normalized ROE of 8% and global bank average. BVPS of $10.00 implies 5.8% CAGR over 10 years (ROE of 8% × 75% retention ratio).

**Note:** Years 4-10 are extrapolated beyond visible analyst estimates. Yahoo Finance revenue estimates cover FY2027-FY2028 only.

---

## Base Case

**Assumptions:** ROE sustains near 10-11% as rate normalization stabilizes. BVPS compounds at 7.5-8.5% (ROE of 10.5% × 78% retention = 8.2%). P/B trades at 1.60-1.70x, consistent with current market levels.

| Horizon | BVPS | Price (×1.65) | P/E Implied | Rev. Growth Implied |
|---|---:|---:|---:|---:|
| 1-yr | $6.26 | $10.33 | ~15.2x | ~10% |
| 2-yr | $6.78 | $11.19 | ~15.6x | ~8% |
| 3-yr | $7.34 | $12.11 | ~16.0x | ~7% |
| 5-yr | $8.57 | $14.14 | ~15.5x | ~5% |
| 10-yr | $12.50 | $20.63 | ~15.0x | ~3% |

Stock-price CAGR from $10.15: 1-yr: +1.8%, 5-yr: +8.0%, 10-yr: +11.11%

**Year-10 terminal anchor:** P/E of 15.0x based on sustained ROE of 10-11% and cost of equity of 6.45%, consistent with Residual Income fair P/B of ~1.70x. BVPS of $12.50 implies 8.3% CAGR over 10 years (ROE of 10.5% × 80% retention ratio).

**Note:** Years 4-10 are extrapolated beyond visible analyst estimates. Base case BVPS growth rate of 8.2% is consistent with current ROE × retention.

---

## Bull Case

**Assumptions:** ROE expands to 12.5%+ as rate normalization continues and securities franchise monetizes. P/B re-rates to 2.00x as market recognizes Mizuho as a diversified financial platform rather than a utility bank. BVPS compounds at 9-10% (ROE of 12.5% × 78% retention = 9.8%).

| Horizon | BVPS | Price (×2.00) | P/E Implied | Rev. Growth Implied |
|---|---:|---:|---:|---:|
| 1-yr | $6.54 | $13.08 | ~17.5x | ~15% |
| 2-yr | $7.26 | $14.52 | ~17.0x | ~12% |
| 3-yr | $8.04 | $16.08 | ~16.5x | ~10% |
| 5-yr | $9.95 | $19.90 | ~16.0x | ~7% |
| 10-yr | $15.00 | $30.00 | ~15.5x | ~4% |

Stock-price CAGR from $10.15: 1-yr: +28.9%, 5-yr: +12.46%, 10-yr: +13.82%

**Year-10 terminal anchor:** P/E of 15.5x based on sustained ROE of 12.5%+ at a P/B of 2.0x. BVPS of $15.00 implies 11.9% CAGR over 10 years (ROE of 12.5% × 82% retention ratio).

**Note:** Years 4-10 are extrapolated beyond visible analyst estimates. Bull case requires both rate tailwind persistence AND multiple expansion — two assumptions that must simultaneously hold.

---

## Probability-Weighted Summary

| Scenario | Weight | 5-Yr Target | Implied CAGR (5Y) |
|---|---:|---:|---:|
| Bear | 25% | $10.08 | 0.2% |
| Base | 50% | $14.14 | 7.1% |
| Bull | 25% | $19.90 | 12.4% |
| **Weighted** | **100%** | **$14.48** | **7.0%** |

Weighted fair value: $14.48 (43% upside from $10.15, implied 7% annual CAGR).

---

## Methodology Notes

1. **Framework:** Book Value Per Share × Price/Book multiple. FCF-based terminal values are not applicable — deposits offset loan origination for banks.
2. **BVPS compounding:** Calculated as BVPS_current × (1 + ROE × retention_ratio)^(n). Payout ratio ~28%, implying retention ~72%.
3. **Terminal P/E anchors:** Year-10 prices work backward from explicit P/E assumptions rather than forward multiples, per projections/README.md guidance.
4. **Extrapolation:** Analyst revenue estimates (Yahoo Finance) cover FY2027-FY2028 only. The 4- and 10-year horizon BVPS projections are extrapolated from current ROE × retention ratios.
5. **No EPS estimates:** Yahoo Finance shows empty EPS analyst estimates for all periods. Projections use ROE/BVPS framework exclusively.
6. **FCF yield:** N/A — bank cash flow is inherently negative due to deposit-loan accounting mechanics.

---

This projection sheet supplements the full research report at `research/MFG.md` and the workbook model at `models/2026-06-22 Mizuho Financial Group Model.xlsx`.
