# Data store

This directory is the store of record. Each research run captures its data once and commits it here. Nothing downstream re-fetches: workbooks, projections, scorecards, and CI read only these files.

```
data/<TICKER>/<YYYY-MM-DD>/call.json             the call: stance, bear/base/bull values and weights, Street context, catalysts, next review
data/<TICKER>/<YYYY-MM-DD>/inputs.json           point-in-time inputs; every value has a source and as-of date
data/<TICKER>/<YYYY-MM-DD>/sources/manifest.json every source used, with a SHA-256
data/<TICKER>/<YYYY-MM-DD>/sources/*             saved copies of fetched pages and filings
data/prices/<SYMBOL>.csv                         daily closes, append-only (date,close,adj_close)
data/companies.csv                               ticker, CIK, SEC name, exchange, filer category, sector
data/sec/facts/<TICKER>.csv                      point-in-time SEC XBRL facts, append-only
data/sec/restatements.csv                        values that changed in a later filing
data/calendar/earnings.csv                       8-K Item 2.02 releases and periodic filings, with session
data/calls.csv                                   generated: one row per call
```

Capture (the only commands that touch the network):

```bash
python3 -m capital.prices          # append new daily closes
CAPITAL_SEC_CONTACT=you@example.org python3 -m capital.sec   # append new SEC facts and filings
```

Point-in-time fundamentals: `python3 -m capital.pit CNC 2026-11-07` shows only what had been filed by that date. The SEC `frame` field is never stored because it points at the latest restated value.

Schemas live in `capital/schemas/`. Check everything offline with:

```bash
python3 -m capital.validate   # schemas, hashes, cross-file consistency, evidence quotes
python3 -m capital.fmt        # rewrite JSON in canonical form
python3 -m capital.build      # regenerate data/calls.csv and library/
```

Rules:

- A dated directory is never rewritten except to fix an extraction error. A new view is a new date.
- Missing data is `null`, never zero.
- `origin: backfill` calls were extracted from reports published before this store existed. Each extracted number has a verbatim `evidence` quote that CI checks against the report version the call cites.
- `origin: run` calls must also carry `inputs.json`, sources, a thesis, catalysts, `next_review`, `change_my_mind`, and a reason whenever fair value is 10% or more away from the Street mean.
