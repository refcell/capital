"""Print the next research task. Run: python3 -m capital.next

An update is due when a covered company has filed an earnings release (8-K Item 2.02)
after its latest call. Releases from the last FRESH_DAYS days go first, newest first,
so an update lands while the event is current. Older (backlog) updates alternate with
new names by calendar day, so coverage keeps growing while the backlog clears. A new
name comes from scripts/pick-company-ticker.py. Output is one JSON line:
    {"task": "update", "ticker": "ACM", "prior_call": "ACM/2026-08-18", "release": "2026-11-17"}
    {"task": "new"}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta

from capital import store
from capital.build import releases


FRESH_DAYS = 30


def next_task(today: date) -> dict:
    rel = releases()
    due = []
    for t, c in store.latest_calls().items():
        newer = [r for r in rel.get(t, []) if r["filing_date"] > c.date]
        if newer:
            due.append((newer[-1]["filing_date"], newer[0]["filing_date"], t, c.key))
    fresh_cutoff = (today - timedelta(days=FRESH_DAYS)).isoformat()
    fresh = sorted((d for d in due if d[0] >= fresh_cutoff), reverse=True)
    if fresh:
        latest, _, ticker, key = fresh[0]
        return {"task": "update", "ticker": ticker, "prior_call": key, "release": latest, "reason": "fresh release"}
    if due and today.toordinal() % 2 == 0:
        latest, _, ticker, key = min(due, key=lambda d: d[1])
        return {"task": "update", "ticker": ticker, "prior_call": key, "release": latest, "reason": "backlog"}
    return {"task": "new", "backlog": len(due)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    print(json.dumps(next_task(date.fromisoformat(args.date))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
