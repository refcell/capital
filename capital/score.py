"""Score calls against committed prices. Reads only data/; never fetches.

A call is marked in its own price terms: mark = call price x adj_close(t) / adj_close(t0),
where t0 is the last committed session on or before the call's price date. Using the
adjusted series keeps splits, spin-offs, and dividends from moving the mark, so the mark
compares directly with the call's bear, base, and bull values.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass
from datetime import date
from typing import Any

from capital import config, prices, store


def expected_annual(call: dict[str, Any]) -> float | None:
    """Annualized return implied by fair value over the rating horizon."""
    fv = store.fair_value(call)
    px = call["price"]["value"]
    if fv is None or px <= 0:
        return None
    if fv <= 0:
        return -1.0
    return (fv / px) ** (1 / config.RATING_HORIZON_YEARS) - 1


def rule_rating(call: dict[str, Any]) -> str | None:
    er = expected_annual(call)
    if er is None:
        return None
    if er >= config.RATING_OWN_MIN_ANNUAL:
        return "own"
    if er < config.RATING_AVOID_MAX_ANNUAL:
        return "avoid"
    return "watch"


_series: dict[str, tuple[list[str], list[tuple[str, float, float]]]] = {}


def series(symbol: str) -> tuple[list[str], list[tuple[str, float, float]]]:
    if symbol not in _series:
        rows = prices.closes(symbol)
        _series[symbol] = ([r[0] for r in rows], rows)
    return _series[symbol]


def _at_or_before(symbol: str, day: str) -> tuple[str, float, float] | None:
    dates, rows = series(symbol)
    i = bisect.bisect_right(dates, day) - 1
    return rows[i] if i >= 0 else None


def last_date(symbol: str = config.RATING_BENCHMARK) -> str | None:
    dates, _ = series(symbol)
    return dates[-1] if dates else None


@dataclass(frozen=True)
class Mark:
    as_of: str
    start: str
    mark: float
    ret: float
    bench_ret: float | None
    band: str | None

    @property
    def excess(self) -> float | None:
        return None if self.bench_ret is None else self.ret - self.bench_ret


BANDS = ("below bear", "bear to base", "base to bull", "above bull")


def band(value: float, scenarios: dict[str, Any]) -> str | None:
    vals = [(scenarios.get(c) or {}).get("value") for c in ("bear", "base", "bull")]
    if any(v is None for v in vals):
        return None
    bear, base, bull = vals
    if value < bear:
        return BANDS[0]
    if value < base:
        return BANDS[1]
    if value <= bull:
        return BANDS[2]
    return BANDS[3]


def mark(call: dict[str, Any], as_of: str | None = None) -> Mark | None:
    start_day = call["price"].get("date") or call["date"]
    t0 = _at_or_before(call["ticker"], start_day)
    end_day = as_of or last_date(call["ticker"])
    t1 = _at_or_before(call["ticker"], end_day) if end_day else None
    if not t0 or not t1 or t1[0] <= t0[0]:
        return None
    ratio = t1[2] / t0[2]
    value = call["price"]["value"] * ratio
    b0 = _at_or_before(config.RATING_BENCHMARK, t0[0])
    b1 = _at_or_before(config.RATING_BENCHMARK, t1[0])
    bench = (b1[2] / b0[2] - 1) if b0 and b1 and b0[0] == t0[0] else None
    return Mark(as_of=t1[0], start=t0[0], mark=value, ret=ratio - 1, bench_ret=bench, band=band(value, call.get("scenarios") or {}))


def years_between(a: str, b: str) -> float:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days / 365.25
