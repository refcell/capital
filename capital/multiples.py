"""Valuation multiples from committed data: each name's own history and its SEC industry peers.

    python3 -m capital.multiples capture [TICKERS...]   # network: 10 years of monthly closes and splits
    python3 -m capital.multiples NRG                    # offline: current, own-history bands, peers

`capture` is the only network step. It writes as-traded monthly closes to
data/prices/monthly/<T>.csv (completed months only, append-only) and split events to
data/splits.csv. To add peers that are not covered, capture them here and run
`python3 -m capital.sec TICKER` for their facts; they then join their SIC group.

Everything else reads only committed files. `python3 -m capital.build` writes
data/multiples/<T>.csv (one row per month) and library/MULTIPLES.md from them.

Multiples are point in time. Each month uses its last trading close as traded and the SEC
facts filed on or before the month's last day (capital.pit, which puts shares and per-share
values on the split basis of its date), adjusted for any split between the last filing and
the month end. EV is market value plus long-term
debt less cash, equivalents and short-term investments; leases, preferred stock and
minority interests are not included. Non-USD filers are skipped.
"""

from __future__ import annotations

import argparse
import bisect
import calendar
import csv
import json
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote

from capital import pit, prices, store

MONTHLY = store.PRICES / "monthly"
SPLITS = store.DATA / "splits.csv"
OUT = store.DATA / "multiples"
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=10y&interval=1mo&events=split"
METRICS = (("pe", "P/E"), ("ev_sales", "EV/Sales"), ("ev_ebit", "EV/EBIT"), ("p_fcf", "P/FCF"))
FIELDS = ["month", "as_of", "price", "market_cap_m", "ev_m", "pe", "ev_sales", "ev_ebit", "p_fcf", "facts_filed"]
STALE_DAYS = 460  # skip a month when the latest annual or TTM period ended more than ~15 months earlier
CAP = 1000.0  # multiples above this are treated as not meaningful


# ---------------------------------------------------------------- capture (network)

def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _utc_day(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()


def capture(symbol: str, today: date) -> int:
    from functions.common.http import fetch_bytes

    url = YAHOO_URL.format(symbol=quote(symbol.replace(".", "-"), safe="-^"))
    payload = json.loads(fetch_bytes(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}).body)
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result or not result.get("timestamp"):
        raise ValueError(f"no chart data for {symbol}")
    events = []
    for ev in (result.get("events") or {}).get("splits", {}).values():
        events.append((_utc_day(ev["date"]), float(ev["numerator"]), float(ev["denominator"])))
    have_splits = {(r["symbol"], r["date"]) for r in _read_csv(SPLITS)}
    new_splits = [e for e in events if (symbol, e[0]) not in have_splits]
    if new_splits:
        exists = SPLITS.exists()
        with SPLITS.open("a", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            if not exists:
                w.writerow(["symbol", "date", "numerator", "denominator"])
            for d, n, den in sorted(new_splits):
                w.writerow([symbol, d, f"{n:g}", f"{den:g}"])
    ratios = sorted((d, n / den) for d, n, den in events)

    this_month = today.strftime("%Y-%m")
    bars: dict[str, float] = {}
    for ts, c in zip(result["timestamp"], result["indicators"]["quote"][0]["close"]):
        if c is None or c <= 0:
            continue
        month = _utc_day(ts)[:7]  # bars are stamped at the month's first local midnight, after 00:00 UTC
        if month < this_month:
            bars[month] = c  # Yahoo can repeat a bar; the last one wins
    path = MONTHLY / f"{symbol}.csv"
    existing = _read_csv(path)
    last = existing[-1]["month"] if existing else ""
    rows = []
    for month in sorted(bars):
        if month <= last:
            continue
        end = month_end(month)
        factor = 1.0
        for d, r in ratios:
            if d > end:
                factor *= r
        rows.append((month, round(bars[month] * factor, 4), round(bars[month], 4)))
    if not rows:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if not existing:
            w.writerow(["month", "close", "split_adjusted_close"])
        for month, close, adj in rows:
            w.writerow([month, f"{close:g}", f"{adj:g}"])
    return len(rows)


# ---------------------------------------------------------------- compute (offline)

def month_end(month: str) -> str:
    y, m = int(month[:4]), int(month[5:7])
    return f"{month}-{calendar.monthrange(y, m)[1]:02d}"


def _ratio(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den <= 0 or num <= 0:
        return None
    v = num / den
    return round(v, 2) if v <= CAP else None


@dataclass
class Point:
    month: str
    as_of: str
    price: float
    market_cap_m: float | None
    ev_m: float | None
    pe: float | None
    ev_sales: float | None
    ev_ebit: float | None
    p_fcf: float | None
    facts_filed: str

    def row(self) -> dict[str, str]:
        def f(v: float | None, nd: int = 2) -> str:
            return "" if v is None else f"{v:.{nd}f}"
        return {
            "month": self.month, "as_of": self.as_of, "price": f"{self.price:g}",
            "market_cap_m": f(self.market_cap_m, 0), "ev_m": f(self.ev_m, 0),
            "pe": f(self.pe), "ev_sales": f(self.ev_sales), "ev_ebit": f(self.ev_ebit), "p_fcf": f(self.p_fcf),
            "facts_filed": self.facts_filed,
        }


def _filing_dates(ticker: str) -> list[str]:
    return sorted({f.filed for f in pit.facts(ticker)})


_asof_cache: dict[tuple[str, str], dict[str, pit.Value]] = {}


def _fundamentals(ticker: str, on: str, filings: list[str]) -> dict[str, pit.Value]:
    """pit.as_of keyed by the last filing date visible on `on` (facts change only on filings)."""
    i = bisect.bisect_right(filings, on)
    if i == 0:
        return {}
    key = (ticker, filings[i - 1])
    if key not in _asof_cache:
        _asof_cache[key] = pit.as_of(ticker, filings[i - 1])
    return _asof_cache[key]


def _liquidity(f: dict[str, pit.Value]) -> float:
    """Cash, equivalents and short-term investments at the latest balance-sheet date."""
    cash, sti, both = f.get("cash"), f.get("short_term_investments"), f.get("cash_and_short_term_investments")
    if both and (not cash or both.end >= cash.end):
        return both.value
    if not cash:
        return 0.0
    return cash.value + (sti.value if sti and sti.end == cash.end else 0.0)


def point(ticker: str, month: str, on: str, price: float, filings: list[str]) -> Point | None:
    f = _fundamentals(ticker, on, filings)
    # pit values are on the share basis of the last filing date; carry them to `on`.
    i = bisect.bisect_right(filings, on)
    split = pit.split_factor(ticker, filings[i - 1], on) if i else 1.0
    rev = f.get("revenue")
    if not rev or rev.unit != "USD" or pit.days(rev.end, on) > STALE_DAYS:
        return None
    sh = f.get("shares_outstanding")
    if not sh or sh.value <= 0 or pit.days(sh.end, on) > STALE_DAYS:
        sh = f.get("diluted_shares")  # multi-class filers often lack a current cover-page count
    shares = sh.value * split if sh else None
    mcap = price * shares / 1e6 if shares else None
    debt = f["long_term_debt"].value / 1e6 if "long_term_debt" in f else 0.0
    cash = _liquidity(f) / 1e6
    ev = mcap + debt - cash if mcap is not None else None
    # EPS as trailing net income over diluted shares, which works when the filer reports no EPS tag.
    ni, dil = f.get("net_income"), f.get("diluted_shares")
    eps_v = ni.value / (dil.value * split) if ni and dil and dil.value > 0 else None
    oi = f.get("operating_income")
    fcf = f.get("free_cash_flow")
    return Point(
        month=month, as_of=on, price=price,
        market_cap_m=mcap, ev_m=ev,
        pe=_ratio(price, eps_v),
        ev_sales=_ratio(ev, rev.value / 1e6),
        ev_ebit=_ratio(ev, oi.value / 1e6 if oi else None),
        p_fcf=_ratio(mcap, fcf.value / 1e6 if fcf else None),
        facts_filed=max(v.filed for v in f.values()),
    )


def history(ticker: str) -> list[Point]:
    rows = _read_csv(MONTHLY / f"{ticker}.csv")
    if not rows or not (pit.FACTS / f"{ticker}.csv").exists():
        return []
    filings = _filing_dates(ticker)
    out = []
    for r in rows:
        p = point(ticker, r["month"], month_end(r["month"]), float(r["close"]), filings)
        if p:
            out.append(p)
    return out


def current(ticker: str) -> Point | None:
    daily = prices.closes(ticker)
    if not daily or not (pit.FACTS / f"{ticker}.csv").exists():
        return None
    d, close, _ = daily[-1]
    return point(ticker, d[:7], d, close, _filing_dates(ticker))


def tickers() -> list[str]:
    return sorted(p.stem for p in MONTHLY.glob("*.csv")) if MONTHLY.exists() else []


def bands(points: list[Point], metric: str, years: int = 10) -> dict[str, float] | None:
    if not points:
        return None
    last = points[-1].month
    cutoff = f"{int(last[:4]) - years}{last[4:]}"
    vals = sorted(getattr(p, metric) for p in points if p.month > cutoff and getattr(p, metric) is not None)
    if len(vals) < 12:
        return None
    q = statistics.quantiles(vals, n=20, method="inclusive")
    return {"n": len(vals), "p10": q[1], "p25": q[4], "p50": statistics.median(vals), "p75": q[14], "p90": q[17]}


def sic_groups() -> dict[str, dict[str, str]]:
    from capital.sec import COMPANIES, read_csv

    return {r["ticker"]: r for r in read_csv(COMPANIES)}


def peers(ticker: str, companies: dict[str, dict[str, str]], available: set[str]) -> tuple[list[str], str]:
    """Tickers sharing the SIC code at the narrowest level with at least three peers."""
    sic = (companies.get(ticker) or {}).get("sic") or ""
    if not sic:
        return [], ""
    for digits in (4, 3, 2):
        group = sorted(
            t for t, r in companies.items()
            if t != ticker and t in available and (r.get("sic") or "")[:digits] == sic[:digits]
        )
        if len(group) >= 3 or digits == 2:
            return group, f"SIC {sic[:digits]}{'x' * (4 - digits)}"
    return [], ""


def fmt(v: float | None) -> str:
    return "—" if v is None else f"{v:.1f}x"


def summary(ticker: str, cache: dict[str, tuple[Point | None, list[Point]]], companies: dict[str, dict[str, str]]) -> dict:
    cur, hist = cache[ticker]
    group, level = peers(ticker, companies, {t for t, (c, _) in cache.items() if c})
    out = {"ticker": ticker, "current": cur, "bands": {}, "peers": group, "level": level, "peer_median": {}}
    for m, _ in METRICS:
        out["bands"][m] = bands(hist, m)
        vals = [getattr(cache[p][0], m) for p in group if cache[p][0] and getattr(cache[p][0], m) is not None]
        out["peer_median"][m] = (statistics.median(vals), len(vals)) if vals else None
    return out


def load_all() -> dict[str, tuple[Point | None, list[Point]]]:
    return {t: (current(t), history(t)) for t in tickers()}


def history_csv(points: list[Point]) -> str:
    import io

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for p in points:
        w.writerow(p.row())
    return buf.getvalue()


def page(covered: list[str], header: str) -> tuple[str, dict[Path, str]]:
    """library/MULTIPLES.md and data/multiples/<T>.csv for every ticker with monthly prices."""
    cache = load_all()
    companies = sic_groups()
    files = {OUT / f"{t}.csv": history_csv(h) for t, (_, h) in cache.items() if h}
    out = [header, "# Valuation Multiples\n"]
    out.append(
        "Each name's multiples today, its own range over up to ten years of month-end prices, and the median "
        "of its SEC industry (SIC) peers among captured names. Use it to test exit multiples: an exit multiple "
        "above the name's own 75th percentile or its peer median needs a stated reason.\n"
    )
    out.append(
        "Point in time: each month uses the as-traded close and SEC facts filed by the month's last day, "
        "split-adjusted where a split falls between the filing and the month end. P/E is price over trailing GAAP "
        "net income per diluted share, so companies whose guidance is on an adjusted basis read higher here. EV is market value "
        "plus long-term debt less cash and short-term investments; leases and preferred stock are excluded. "
        "Multiples above 1,000x or on negative earnings are blank. Monthly history: `data/multiples/<T>.csv`; "
        "detail for one name: `python3 -m capital.multiples TICKER`. For banks and insurers EV multiples are not "
        "meaningful (deposits and policy liabilities are operating funding); use P/E and book value.\n"
    )
    out.append("| Ticker | Industry (SIC) | P/E now | P/E own p25–p75 | EV/Sales now | EV/Sales own p25–p75 | EV/EBIT now | EV/EBIT own p25–p75 | Peers (median EV/Sales, P/E) |")
    out.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for t in covered:
        if t not in cache:
            out.append(f"| [{t}]({t}.md) | {(companies.get(t) or {}).get('sic_description') or '—'} | no monthly prices captured | | | | | | |")
            continue
        s = summary(t, cache, companies)
        cur = s["current"]

        def band(m: str) -> str:
            b = s["bands"][m]
            return f"{b['p25']:.1f}–{b['p75']:.1f}x" if b else "—"

        pm = s["peer_median"]
        peer_txt = "—"
        if s["peers"]:
            ev = f"{pm['ev_sales'][0]:.1f}x" if pm["ev_sales"] else "—"
            pe = f"{pm['pe'][0]:.1f}x" if pm["pe"] else "—"
            peer_txt = f"{s['level']}, {len(s['peers'])} names: {ev}, {pe}"
        out.append(
            f"| [{t}]({t}.md) | {(companies.get(t) or {}).get('sic_description') or '—'} | "
            f"{fmt(cur.pe if cur else None)} | {band('pe')} | {fmt(cur.ev_sales if cur else None)} | {band('ev_sales')} | "
            f"{fmt(cur.ev_ebit if cur else None)} | {band('ev_ebit')} | {peer_txt} |"
        )
    out.append("")
    return "\n".join(out), files


def report(ticker: str) -> str:
    cache = load_all()
    if ticker not in cache:
        return f"{ticker}: no monthly prices; run python3 -m capital.multiples capture {ticker}"
    companies = sic_groups()
    s = summary(ticker, cache, companies)
    cur = s["current"]
    co = companies.get(ticker) or {}
    lines = [f"{ticker} — {co.get('sic_description') or 'SIC unknown'} (SIC {co.get('sic') or '?'})"]
    if cur:
        lines.append(f"current ({cur.as_of}, ${cur.price:g}, facts filed by {cur.facts_filed}): "
                     + ", ".join(f"{label} {fmt(getattr(cur, m))}" for m, label in METRICS))
    for m, label in METRICS:
        b = s["bands"][m]
        if b:
            lines.append(f"own {label}: p10 {b['p10']:.1f}x, p25 {b['p25']:.1f}x, median {b['p50']:.1f}x, p75 {b['p75']:.1f}x, p90 {b['p90']:.1f}x ({b['n']} months)")
        else:
            lines.append(f"own {label}: fewer than 12 meaningful months")
    if s["peers"]:
        lines.append(f"peers ({s['level']}): " + ", ".join(s["peers"]))
        for m, label in METRICS:
            pm = s["peer_median"][m]
            lines.append(f"peer median {label}: " + (f"{pm[0]:.1f}x ({pm[1]} names)" if pm else "—"))
        for p in s["peers"]:
            pc = cache[p][0]
            if pc:
                lines.append(f"  {p}: " + ", ".join(f"{label} {fmt(getattr(pc, m))}" for m, label in METRICS))
    else:
        lines.append("peers: none captured in the same SIC group")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("args", nargs="+", help="capture [TICKERS...] | TICKER")
    a = parser.parse_args(argv).args
    if a[0] == "capture":
        wanted = [t.upper() for t in a[1:]] or sorted(store.latest_calls())
        today = date.today()
        failed = []
        for t in wanted:
            try:
                print(f"{t}: +{capture(t, today)} months")
            except Exception as exc:  # noqa: BLE001 - report and continue
                failed.append(f"{t}: {exc}")
            time.sleep(0.3)
        for line in failed:
            print("failed " + line, file=sys.stderr)
        return 0
    print(report(a[0].upper()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
