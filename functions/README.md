# Functions

This directory contains small, repo-local Python functions for repeatable
research tasks.

Each function lives in its own subdirectory and follows the same contract:

```python
def run(input: dict) -> dict:
    ...
```

The return value must be JSON-serializable and should include source metadata
for any live data used.

## CLI

Run a function from the repo root:

```bash
python3 functions/run.py factor_exposure --ticker CRM
python3 functions/run.py factor_exposure --ticker CRM --full
python3 functions/run.py factor_exposure --ticker ELF --lookback-months 36
python3 functions/run.py factor_exposure --input-json '{"ticker":"NKE","lookback_months":60}'
just functions all
just functions all --full
```

## Current Functions

### `factor_exposure`

Builds a momentum entry-timing read and a Fama/French factor exposure estimate
for a ticker.

The momentum timing read is meant for position-entry discipline:

- high momentum: avoid chasing, use a smaller starter, or wait for a pullback
- neutral momentum: no timing edge from momentum alone
- low momentum: potentially better entry setup if the fundamental thesis is
  intact

The factor regression uses monthly ticker returns against the Fama/French 5
factors plus momentum. The reported factor weights are normalized absolute beta
shares, not portfolio weights.

The default single-ticker output includes a compact terminal chart of the
ticker's historical 12-month momentum excluding the most recent month. Use
`--full` for the complete JSON payload.

Default price source: Nasdaq historical quotes. Yahoo Finance can be requested
with `--price-source yahoo` if Nasdaq does not support the symbol.

`just functions all` runs this for every ticker discovered from `research/*.md`
and `projections/*.md`, excluding `README.md` and `TEMPLATE.md`. Tickers with
insufficient live price history are reported as skipped rather than causing the
whole batch to fail.
