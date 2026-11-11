"""Base rates for revenue growth from SEC XBRL frames.

    python3 -m capital.base_rates capture   # fetch missing calendar years (network)

Capture writes data/base_rates/revenue/CY<YEAR>.csv: one annual revenue per filer, the
largest value across the revenue concepts in TAGS (filers use different tags, and a
smaller one is usually a component). Reading is offline: `distribution()` gives the
5-year revenue CAGR distribution by starting-revenue bucket, and `percentile()` places a
forecast CAGR inside it.

Caveats, also printed on library/BASE_RATES.md:
- frames returns the latest filed value for each period, so these are restated figures.
  That is fine for a cross-sectional distribution and wrong for a backtest; use
  capital.pit for anything point-in-time.
- Only filers present in both years count, so firms that failed or were acquired drop
  out (survivorship bias pushes the distribution up).
- XBRL begins in 2009, so the sample covers 2009-2025, not the decades in published
  base-rate studies. Starting revenue is nominal, not inflation-adjusted.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import sys
from datetime import date, datetime, timezone
from functools import lru_cache

from capital import store

DIR = store.DATA / "base_rates"
REVENUE = DIR / "revenue"
SOURCES = DIR / "sources.json"
FIRST_YEAR = 2009
TAGS = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "RevenuesNetOfInterestExpense",
)
FRAMES_URL = "https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/USD/CY{year}.json"
YEARS = 5
MIN_START = 50e6
BUCKETS = (
    (50e6, "$50M–$325M"), (325e6, "$325M–$700M"), (700e6, "$700M–$1.5B"), (1.5e9, "$1.5B–$3B"),
    (3e9, "$3B–$6B"), (6e9, "$6B–$12B"), (12e9, "$12B–$25B"), (25e9, "$25B–$50B"), (50e9, "Over $50B"),
)
PCTS = (5, 10, 25, 50, 75, 90, 95)


def bucket(start_revenue: float) -> str | None:
    if start_revenue < MIN_START:
        return None
    label = BUCKETS[0][1]
    for floor, name in BUCKETS:
        if start_revenue >= floor:
            label = name
    return label


def capture() -> int:
    from capital.sec import Client

    client = Client()
    sources = store.load_json(SOURCES) if SOURCES.exists() else {}
    last_full_year = date.today().year - 1
    added = 0
    for year in range(FIRST_YEAR, last_full_year + 1):
        path = REVENUE / f"CY{year}.csv"
        if path.exists():
            continue
        best: dict[int, dict] = {}
        for tag in TAGS:
            url = FRAMES_URL.format(tag=tag, year=year)
            try:
                body = client.get(url)
            except Exception as exc:  # noqa: BLE001 - a tag can be absent for a year
                if "404" in str(exc):
                    continue
                raise
            sources[f"CY{year}/{tag}"] = {
                "url": url, "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "sha256": store.sha256_bytes(body),
            }
            for row in json.loads(body)["data"]:
                cur = best.get(row["cik"])
                if cur is None or row["val"] > cur["val"]:
                    best[row["cik"]] = {"cik": row["cik"], "entity": row["entityName"], "val": row["val"], "tag": tag, "accn": row["accn"]}
        REVENUE.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["cik", "entity", "val", "tag", "accn"], lineterminator="\n")
            w.writeheader()
            w.writerows(best[k] for k in sorted(best))
        print(f"CY{year}: {len(best)} filers")
        added += 1
    store.write_json(SOURCES, dict(sorted(sources.items())))
    return added


@lru_cache(maxsize=None)
def year(y: int) -> dict[int, float]:
    path = REVENUE / f"CY{y}.csv"
    if not path.exists():
        return {}
    with path.open(newline="") as fh:
        return {int(r["cik"]): float(r["val"]) for r in csv.DictReader(fh)}


def years() -> list[int]:
    return sorted(int(p.stem[2:]) for p in REVENUE.glob("CY*.csv"))


@lru_cache(maxsize=1)
def samples() -> dict[str, list[float]]:
    """Bucket -> sorted 5-year CAGRs across every start year with an end year on file."""
    out: dict[str, list[float]] = {name: [] for _, name in BUCKETS}
    ys = set(years())
    for y in sorted(ys):
        if y + YEARS not in ys:
            continue
        a, b = year(y), year(y + YEARS)
        for cik, start in a.items():
            end = b.get(cik)
            name = bucket(start)
            if name and end and end > 0:
                out[name].append((end / start) ** (1 / YEARS) - 1)
    for v in out.values():
        v.sort()
    return out


def quantile(xs: list[float], q: float) -> float:
    i = (len(xs) - 1) * q
    lo = int(i)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def distribution() -> list[dict]:
    rows = []
    for _, name in BUCKETS:
        xs = samples()[name]
        if not xs:
            continue
        row = {"bucket": name, "n": len(xs)}
        for p in PCTS:
            row[f"p{p}"] = round(quantile(xs, p / 100), 4)
        row["share_below_0"] = round(bisect.bisect_left(xs, 0.0) / len(xs), 4)
        row["share_above_10"] = round(1 - bisect.bisect_right(xs, 0.10) / len(xs), 4)
        row["share_above_20"] = round(1 - bisect.bisect_right(xs, 0.20) / len(xs), 4)
        rows.append(row)
    return rows


def percentile(start_revenue: float, cagr: float) -> tuple[str, float] | None:
    """(bucket, share of the bucket's history at or below this CAGR, 0-100)."""
    name = bucket(start_revenue)
    xs = samples().get(name or "", [])
    if not xs:
        return None
    return name, 100 * bisect.bisect_right(xs, cagr) / len(xs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["capture", "show"])
    args = parser.parse_args(argv)
    if args.command == "capture":
        print(f"captured {capture()} year(s)")
    else:
        for row in distribution():
            print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
