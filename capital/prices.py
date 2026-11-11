"""Capture daily closes into data/prices/<SYMBOL>.csv. Run: python3 -m capital.prices

This is the only module that fetches prices. It appends rows newer than the last
committed date and never rewrites a committed row, so a score computed today can be
recomputed from the same files later. Scoring reads only the committed CSVs.

Symbols captured: every ticker with a call, plus the benchmark ETFs in BENCHMARKS.
Source: Yahoo Finance chart API (close and split/dividend-adjusted close).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from capital import store
from functions.common.http import fetch_bytes

BENCHMARKS = ("SPY",)
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={p1}&period2={p2}&interval=1d&events=div%2Csplit"
SOURCES = store.PRICES / "sources.json"


def path_for(symbol: str) -> Path:
    return store.PRICES / f"{symbol}.csv"


def read(symbol: str) -> list[dict[str, str]]:
    path = path_for(symbol)
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def closes(symbol: str) -> list[tuple[str, float, float]]:
    """(date, close, adj_close) rows from the committed file, oldest first."""
    return [(r["date"], float(r["close"]), float(r["adj_close"])) for r in read(symbol)]


def fetch_yahoo(symbol: str, start: date, end: date) -> list[tuple[str, float, float]]:
    p1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
    p2 = int(datetime(end.year, end.month, end.day, tzinfo=timezone.utc).timestamp()) + 86400
    url = YAHOO_URL.format(symbol=quote(symbol.replace(".", "-"), safe="-^"), p1=p1, p2=p2)
    payload = json.loads(fetch_bytes(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}).body)
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result or not result.get("timestamp"):
        raise ValueError(f"no chart data for {symbol}")
    offset = result.get("meta", {}).get("gmtoffset", 0)
    quote_rows = result["indicators"]["quote"][0]["close"]
    adj = (result["indicators"].get("adjclose") or [{}])[0].get("adjclose") or quote_rows
    rows = []
    for ts, c, a in zip(result["timestamp"], quote_rows, adj):
        if c is None or a is None or c <= 0 or a <= 0:
            continue
        day = datetime.fromtimestamp(ts + offset, tz=timezone.utc).date().isoformat()
        rows.append((day, round(c, 4), round(a, 4)))
    # Keep the last row per day (Yahoo can repeat the live bar).
    return sorted({d: (d, c, a) for d, c, a in rows}.values())


def capture(symbol: str, start: date, today: date) -> int:
    """Append completed sessions after the last committed row. Returns rows added."""
    existing = read(symbol)
    last = existing[-1]["date"] if existing else None
    begin = (date.fromisoformat(last) + timedelta(days=1)) if last else start
    if begin >= today:
        return 0
    # Only completed sessions: stop the day before today so a live bar never lands.
    rows = [r for r in fetch_yahoo(symbol, begin, today) if r[0] < today.isoformat() and (last is None or r[0] > last)]
    if not rows:
        return 0
    path = path_for(symbol)
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with path.open("a", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if new_file:
            w.writerow(["date", "close", "adj_close"])
        for d, c, a in rows:
            w.writerow([d, f"{c:g}", f"{a:g}"])
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("symbols", nargs="*", help="default: every covered ticker plus benchmarks")
    args = parser.parse_args(argv)

    first_call: dict[str, str] = {}
    for c in store.iter_calls():
        first_call[c.ticker] = min(first_call.get(c.ticker, c.date), c.date)
    earliest = min(first_call.values()) if first_call else date.today().isoformat()
    wanted = {s: first_call.get(s, earliest) for s in (args.symbols or [*first_call, *BENCHMARKS])}

    sources = store.load_json(SOURCES) if SOURCES.exists() else {}
    today = date.today()
    failed = []
    for symbol, first in sorted(wanted.items()):
        start = date.fromisoformat(first) - timedelta(days=10)
        try:
            added = capture(symbol, start, today)
        except Exception as exc:  # noqa: BLE001 - report and continue with the rest
            failed.append(f"{symbol}: {exc}")
            continue
        if added:
            sources[symbol] = {
                "source": "Yahoo Finance chart API v8 (close, adjclose)",
                "url": YAHOO_URL.split("?")[0].format(symbol=symbol),
                "last_capture": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            }
        print(f"{symbol}: +{added}")
        time.sleep(0.3)
    store.write_json(SOURCES, dict(sorted(sources.items())))
    for line in failed:
        print("failed " + line, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
