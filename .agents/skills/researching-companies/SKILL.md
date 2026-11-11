---
name: researching-companies
description: "Runs one research cycle in the refcell/capital repo: picks a new ticker or an earnings update that is due, captures prices and SEC data once into data/, writes the report and the dated call.json, builds the workbook and projection, validates, and commits. Use for the daily company research run, for a post-earnings update on a covered name, or when asked to research or update a ticker in this repo."
---

# Researching companies in refcell/capital

The repo is the store of record. Data is captured once per run into committed, dated files under `data/`, and everything downstream (workbook, projection, library pages, scorecard) reads only those files. Never re-fetch a number that is already committed; never edit a committed `data/<T>/<date>/` directory except to fix an extraction error.

## 1. Choose the work

Run `python3 -m capital.build` and read `library/CALENDAR.md`.

- If "Calls overtaken by an earnings release" lists a name, do an **update** on the oldest one. An update is due whenever the company has reported since its latest call.
- Otherwise start a **new name**: `python3 scripts/pick-company-ticker.py --record`. It skips every ticker in `data/` or `data/coverage.csv`, and `--record` writes `data/universe/<date>.json` (the candidates it drew from and the pick); commit that file with the run.

`python3 -m capital.next` makes this choice for you: a release from the last 30 days first, then older updates alternating with new names. Names marked `dropped` in `data/coverage.csv` get no updates; set `watchlist` with an `entry_price` for a name worth owning only lower, and `dropped` with a reason to stop covering one.

## 2. Capture data (the only network step)

```bash
python3 -m capital.prices TICKER SPY
python3 -m capital.sec TICKER      # needs CAPITAL_SEC_CONTACT; a placeholder is used if unset
git add data && git commit -m "data: capture TICKER prices and SEC facts"
python3 -m capital.new TICKER      # scaffolds data/TICKER/<today>/
```

`capital.new` fills `inputs.json` with the latest committed close and SEC fundamentals as of today (filed on or before today, with accession numbers), pins the sources in `sources/manifest.json`, and drafts `call.json`. For an update it sets `prior_call` and carries over catalysts, kill criteria, and open claims.

Anything else you read on the web (consensus estimates, Street targets, transcripts, releases) must be saved under `data/TICKER/<date>/sources/` and recorded with `python3 -m capital.sources TICKER DATE FILE --url URL --description TEXT`, and the values you use go into `inputs.json` with `source`, `as_of`, and `accession` when one exists. For SEC exhibits, list the filing with `https://www.sec.gov/Archives/edgar/data/<CIK>/<accession without dashes>/index.json` (CIK is in `data/companies.csv`). Prefer SEC filings for financials; treat consensus as an expectations anchor, not as proof of value.

## 3. Write the research

- New name: copy `research/TEMPLATE.md` to `research/TICKER.md`. Fill the Pitch block first. Section 17 (Pre-Mortem And Kill Criteria) is required.
- Update: write `research/updates/TICKER/<date>.md` from `research/UPDATE_TEMPLATE.md`; `research/TICKER.md` stays the initiation. Roll the existing numbers forward. A "no change" review is a valid outcome and still gets a dated call with `research_status: no_change_review`. Example: `research/updates/CNM/2026-11-11.md` with `data/CNM/2026-11-11/`.

Rules that keep calls honest:

- Scenario values come from the business mechanism, not from the Street. Do not force the base case toward the average target. Record the gap in `deviation_from_street` and, when it is 10% or more, give the reason.
- The stance follows the rule in `capital/config.py` (Own at 15% or more a year over 3 years, Avoid below 0%, Watch in between). If the published stance differs, fill `rating_override_reason`.
- Be wary of large stated upside: published targets 70% or more from the price are hit under a quarter of the time. Wide ranges belong in the bear and bull cases with honest weights.

## 4. Fill call.json

Run `python3 -m capital.validate`; the draft fails until these are set, and the failures are the to-do list:

- stance, `primary_lens`, `fair_value`, bear/base/bull values **and** weights, `horizon_years`
- `thesis`, `consensus_view`, `variant_view`, `why_opportunity` (behavioral, analytical, informational, technical)
- `catalysts` with at least one `kind: hard` with a date, `kill_criteria` with check-by dates, `change_my_mind`
- `premortem`: at least 3 failure stories, each with an early signal
- `claims`: at least 3 probability claims a third party could resolve, each with `resolve_by`
- updates: the `update` block, and `resolutions` for every prior claim that is now due
- `next_review` (usually the day after the next estimated release in `library/CALENDAR.md`)
- `artifacts`: report, projection, model, and build-script paths. Leave `commit` null; it refers to the working tree until a later call needs to pin it.

## 5. Model and projection

Build the workbook from the call and inputs (values only, no live formulas): `python3 -m capital.workbook TICKER DATE` writes `models/TICKER/DATE.xlsx`. For a new name, also write `projections/TICKER.md` (see `projections/README.md`); its bear/base/bull prices and fair value must match `call.json`. Updates skip the projection unless the long-run view changed.

## 6. Check and commit

```bash
python3 -m capital.validate && python3 -m capital.build
python3 -m unittest discover -t . -s capital
git add -A && git commit -m "research: TICKER <initial|update> (<lens>)" && git push origin main
```

Commit directly to main. Never put a work email or the owner's employer anywhere in the repo.
