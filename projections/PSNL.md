# PSNL Projection

Date: 2026-11-25
Company: Personalis, Inc.
Ticker: Nasdaq: PSNL
Model: `models/PSNL/2026-11-25.xlsx`, rendered by `python3 -m capital.workbook PSNL 2026-11-25` from `data/PSNL/2026-11-25/call.json` and `inputs.json`; the tables below are printed by `python3 models/_build_PSNL_2026-11-25.py`
Report: `research/updates/PSNL/2026-11-25.md` (update); initiation `research/PSNL.md`
Price: $14.53 at the November 24, 2026 close; TEM $54.83 on the same day

This is investment research support, not personalized financial advice.

Personalis agreed on July 20, 2026 to be acquired by Tempus AI. The stockholder vote is November 30 and closing is expected on December 1, 2 or 3, 2026. After closing PSNL stops trading, so this sheet does not carry the usual 1-, 2-, 3-, 5- and 10-year tables or a terminal P/E anchor; there is no PSNL share to project. The August 25 sheet's standalone tables (base $18.96, bull $59.80) were written after the merger was signed and are withdrawn.

## What A PSNL Share Becomes

Per eligible share at closing: $6.27 of cash (Cash Consideration Fraction 0.385815 × $16.25, from Tempus's November 24 cash election) plus 0.6142 × $16.25 / VWAP Tempus Class A shares. The VWAP is TEM's 15 trading days ending the day before the last trading day before closing, estimated from daily bars as typical price weighted by volume, with missing days filled at the scenario's TEM price. Below a $48.42 VWAP the ratio is fixed at 0.3356; below $46.00 Personalis may walk away. Neither is close.

| Closing date | VWAP estimate | Exchange Ratio | TEM shares per PSNL share | Package at TEM $54.83 |
|---|---:|---:|---:|---:|
| December 1 | $66.19 | 0.2455 | 0.151 | $14.54 |
| December 2 | $64.81 | 0.2507 | 0.154 | $14.71 |
| December 3 | $62.44 | 0.2603 | 0.160 | $15.03 |
| December 4 | $60.85 | 0.2671 | 0.164 | $15.26 |

## Scenarios At Closing (December 2)

| Case | Weight | TEM at closing | Exchange Ratio | Cash | Stock | Value per PSNL share | vs $14.53 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bear | 27% | $43.86 (−20%) | 0.2568 | $6.27 | $6.92 | $13.19 | −9.2% |
| Base | 50% | $54.83 | 0.2507 | $6.27 | $8.44 | $14.71 | +1.3% |
| Bull | 23% | $65.80 (+20%) | 0.2449 | $6.27 | $9.90 | $16.17 | +11.3% |
| Fair value | | | | | | $14.64 | +0.7% |

The weights reproduce a 98% chance of closing with TEM equally likely 20% up or down, plus a 2% deal break valued at $12.00 (below the $14.68 unaffected price, inside Centerview's standalone ranges): 0.98 × $14.70 + 0.02 × $12.00 = $14.64.

## Package Value By TEM Price

| TEM at closing | $35 | $40 | $45 | $50 | $54.83 | $60 | $65 | $70 | $75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Value per PSNL share | $11.90 | $12.63 | $13.35 | $14.05 | $14.71 | $15.41 | $16.06 | $16.71 | $17.34 |
| Stock share of value | 47% | 50% | 53% | 55% | 57% | 59% | 61% | 62% | 64% |

Each $1 move in TEM moves the package by about $0.14–0.15. The Reorg Threshold, which would reduce the cash portion if stock fell below 40% of value, binds only below a TEM price of about $27.

## After Closing

A holder's long-run outcome is $6.27 of cash plus about 0.154 TEM shares per PSNL share, so the three-, five- and ten-year path is Tempus's, which this repo has not researched. The only long-run forecast for Personalis itself is management's standalone case in the merger proxy (DEFM14A, October 21, 2026): revenue of $90M in 2026, $143M in 2027, $457M in 2029 and $1.15B in 2031, with adjusted EBITDA turning positive in 2029. It is shown for reference only. It assumes Personalis stays independent, it is not a Street estimate, and Centerview's DCF on it gave $11.05 to $16.75 a share.
