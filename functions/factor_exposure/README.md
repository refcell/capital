# factor_exposure

`factor_exposure` estimates whether a ticker is currently extended or washed
out from a momentum-entry perspective, then computes factor loadings against:

- market excess return
- size
- value
- profitability
- investment
- momentum

The factor data comes from the Kenneth French Data Library. Price history comes
from Nasdaq historical quotes by default. Yahoo Finance can be requested with
`--price-source yahoo` for symbols Nasdaq does not cover.

## Usage

```bash
python3 functions/run.py factor_exposure --ticker CRM
python3 functions/run.py factor_exposure --ticker CRM --full
python3 functions/run.py factor_exposure --ticker ELF --lookback-months 60
python3 functions/run.py factor_exposure --input-json '{"ticker":"NKE","as_of":"2026-06-01"}'
just functions all
just functions all --full
```

## How To Read The Momentum Timing Output

The `entry_bias` field is the practical read:

- `avoid_chasing`: momentum is very high; wait for a pullback or size smaller
- `be_cautious`: momentum is high; avoid making valuation mistakes because the
  chart looks strong
- `neutral`: no clear timing signal from momentum alone
- `constructive_entry_setup`: momentum is low enough to be more attractive for
  a staged entry if the thesis is intact
- `contrarian_entry_check_falling_knife`: momentum is very low; entry may be
  attractive, but the business/news risk needs extra checking

The `factor_weighting` output is a normalized view of regression betas. It is
not a fund-style portfolio weight.

The default single-ticker terminal output also prints a short ASCII chart of
historical 12-month momentum excluding the most recent month. The final `now`
row shows the current daily signal used in the timing read.
