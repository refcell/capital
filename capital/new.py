"""Start a dated call from committed data. Run: python3 -m capital.new TICKER [--date YYYY-MM-DD]

Creates data/<T>/<date>/ with:
    inputs.json            price from data/prices and SEC fundamentals as of the date (filed <= date),
                           each value carrying its source and accession number
    sources/manifest.json  the committed price and SEC files this call read, pinned to HEAD
    call.json              a draft: known fields filled, judgment fields null

When the ticker already has a call, the draft is an update: prior_call is set and the
prior call's catalysts, kill criteria, and open claims are carried over for review.

Run `python3 -m capital.prices TICKER` and `python3 -m capital.sec TICKER` first and
commit their output, so the manifest can pin them. The draft fails
`python3 -m capital.validate` until the research run fills it in; the failures are the
to-do list.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date

from capital import pit, prices, score, store

# pit metric -> (inputs.json key, scale divisor)
PIT_TO_INPUTS = {
    "revenue": ("ttm_revenue_m", 1e6),
    "gross_profit": ("ttm_gross_profit_m", 1e6),
    "operating_income": ("ttm_operating_income_m", 1e6),
    "net_income": ("ttm_net_income_m", 1e6),
    "eps_diluted": ("ttm_eps", 1),
    "operating_cash_flow": ("ttm_ocf_m", 1e6),
    "capex": ("ttm_capex_m", 1e6),
    "free_cash_flow": ("ttm_fcf_m", 1e6),
    "cash": ("cash_m", 1e6),
    "long_term_debt": ("total_debt_m", 1e6),
    "shares_outstanding": ("shares_outstanding_m", 1e6),
    "diluted_shares": ("diluted_shares_m", 1e6),
}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=store.ROOT, capture_output=True, text=True, check=True).stdout.strip()


def committed(path: str) -> bool:
    return bool(git("ls-files", path)) and not git("status", "--porcelain", "--", path)


def build_inputs(ticker: str, day: str) -> tuple[dict, list[str]]:
    notes: list[str] = []
    values: dict = {}
    rows = [r for r in prices.closes(ticker) if r[0] <= day]
    if rows:
        d, close, _ = rows[-1]
        values["price"] = {"value": close, "as_of": d, "source": f"data/prices/{ticker}.csv (Yahoo Finance close)"}
    else:
        notes.append("No committed price on or before the call date; run python3 -m capital.prices first.")
    currency = "USD"
    for metric, v in pit.as_of(ticker, day).items():
        if metric not in PIT_TO_INPUTS:
            continue
        key, div = PIT_TO_INPUTS[metric]
        unit_currency = v.unit.split("/")[0]
        entry = {
            "value": round(v.value / div, 4),
            "as_of": v.end,
            "source": f"SEC XBRL {v.tag} ({v.method.replace('_', ' ')}), filed {v.filed}",
            "accession": v.accns[-1],
        }
        if unit_currency not in ("shares", "USD"):
            entry["currency"] = unit_currency
        values[key] = entry
    shares_key = "shares_outstanding_m" if "shares_outstanding_m" in values else "diluted_shares_m"
    if shares_key in values and "price" in values:
        mc = values["price"]["value"] * values[shares_key]["value"]
        values["market_cap_m"] = {
            "value": round(mc, 2), "as_of": values["price"]["as_of"],
            "source": f"price x {shares_key}",
        }
    return {
        "schema_version": 1, "ticker": ticker, "date": day, "currency": currency, "origin": "run",
        "values": values, "notes": notes,
    }, notes


def build_manifest(ticker: str) -> dict:
    head = git("rev-parse", "HEAD")
    entries = []
    for ident, path, desc in (
        ("prices", f"data/prices/{ticker}.csv", "Daily closes captured by capital.prices"),
        ("sec-facts", f"data/sec/facts/{ticker}.csv", "Point-in-time SEC XBRL facts captured by capital.sec"),
        ("calendar", "data/calendar/earnings.csv", "SEC 8-K Item 2.02 releases and periodic filings"),
    ):
        if not committed(path):
            continue
        blob = store.git_blob(head, path)
        entries.append({
            "id": ident, "kind": "repo", "path": path, "commit": head[:12], "sha256": store.sha256_bytes(blob),
            "description": desc,
        })
    return {"schema_version": 1, "entries": entries}


def pin_prior_artifacts(prior: store.Call) -> None:
    """Point the prior call's working-tree artifacts at the commit that last changed them.

    Run calls leave artifact commits null while the files are current. An update is about
    to overwrite research/<T>.md, so the prior call must cite the version it was written
    from. This is the one edit allowed on a committed call: it records which version, and
    changes no value.
    """
    changed = False
    for a in (prior.call.get("artifacts") or {}).values():
        if a and not a.get("commit"):
            a["commit"] = git("log", "-1", "--format=%h", "--", a["path"]) or None
            changed = changed or bool(a["commit"])
    if changed:
        store.write_json(prior.dir / "call.json", prior.call)


def draft_call(ticker: str, day: str, inputs: dict) -> dict:
    prior = store.latest_calls().get(ticker)
    if prior and prior.date < day:
        pin_prior_artifacts(prior)
    p = prior.call if prior and prior.date < day else None
    price = inputs["values"].get("price")
    open_claims = []
    if p:
        resolved = {r["claim"] for c in store.iter_calls() for r in c.call.get("resolutions") or []}
        open_claims = [f"{prior.key}#{k['id']}" for k in p.get("claims") or [] if f"{prior.key}#{k['id']}" not in resolved]
    notes = []
    if open_claims:
        notes.append("Open claims from the prior call to resolve in `resolutions` when due: " + ", ".join(open_claims))
    return {
        "schema_version": 1,
        "ticker": ticker,
        "exchange": p.get("exchange") if p else None,
        "company": p["company"] if p else ticker,
        "sector": p.get("sector") if p else None,
        "date": day,
        "origin": "run",
        "prior_call": prior.key if p else None,
        "research_status": "post_earnings" if p else "initial",
        "research_status_text": None,
        "stance": None,
        "bias": None,
        "stance_text": "",
        "rating_override_reason": None,
        "primary_lens": None,
        "lens_text": None,
        "price": {"value": price["value"] if price else 0.01, "currency": "USD", "date": price["as_of"] if price else None},
        "scenarios": {
            "bear": {"value": None, "weight": None, "basis": None},
            "base": {"value": None, "weight": None, "basis": None},
            "bull": {"value": None, "weight": None, "basis": None},
        },
        "fair_value": None,
        "horizon_years": 3,
        "horizon_text": None,
        "street": {"target_mean": None, "target_median": None, "target_low": None, "target_high": None, "analysts": None, "rating_text": None, "as_of": None, "source": None},
        "deviation_from_street": None,
        "thesis": None,
        "consensus_view": None,
        "variant_view": None,
        "why_opportunity": [],
        "edge": None,
        "catalysts": [dict(k, kind=k.get("kind")) for k in (p.get("catalysts") or [])] if p else [],
        "premortem": [],
        "kill_criteria": [dict(k, status=k.get("status") or "open") for k in (p.get("kill_criteria") or [])] if p else [],
        "claims": [],
        "resolutions": [],
        "change_my_mind": list(p.get("change_my_mind") or []) if p else [],
        "base_rate": None,
        "update": {"event": "", "event_date": None, "expected": None, "actual": None, "thesis_pillars": [], "action": "no_change"} if p else None,
        "next_review": None,
        "next_review_trigger": None,
        "artifacts": {"report": {"path": f"research/{ticker}.md", "commit": None}},
        "evidence": {},
        "notes": notes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ticker")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    ticker = args.ticker.upper()
    d = store.call_dir(ticker, args.date)
    if (d / "call.json").exists():
        print(f"{d.relative_to(store.ROOT)} already exists", file=sys.stderr)
        return 1
    inputs, notes = build_inputs(ticker, args.date)
    store.write_json(d / "inputs.json", inputs)
    store.write_json(d / "sources" / "manifest.json", build_manifest(ticker))
    store.write_json(d / "call.json", draft_call(ticker, args.date, inputs))
    print(f"created {d.relative_to(store.ROOT)}/ (call.json is a draft)")
    for n in notes:
        print("note: " + n)
    rule = score.config.RATING_DEFINITIONS
    print("rating rule: " + "; ".join(f"{k}: {v}" for k, v in rule.items()))
    print("next: write the report, fill call.json, then python3 -m capital.validate until it passes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
