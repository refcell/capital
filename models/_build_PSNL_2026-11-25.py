#!/usr/bin/env python3
"""PSNL 2026-11-25 scenario values (Tempus merger consideration).

Reads nothing from the network. Deal terms are from Note 13 of the Q3 2026 10-Q
(accession 0001193125-26-447201) and the DEFM14A (0001193125-26-427872); the
cash election is from the 8-K filed 2026-11-25 (0001193125-26-478697); the
expected closing dates (December 1, 2 or 3, 2026) are from the Rule 425
employee FAQ (0001193125-26-475641). TEM daily bars are the committed Yahoo
chart file in data/PSNL/2026-11-25/sources/. Prints the bear/base/bull values
that go into call.json and the tables in the update note and projections/PSNL.md.
The workbook is rendered by `python3 -m capital.workbook PSNL 2026-11-25`. The
August initiation's script is models/_build_PSNL.py and is left as it was.

Per eligible PSNL share at closing:
  cash  = Cash Consideration Fraction x $16.25
  stock = (1 - fraction) x Exchange Ratio x TEM price at closing
  Exchange Ratio = $16.25 / Parent Stock Price if that is above the $48.42
  Floor Price, else 0.3356. Parent Stock Price is TEM's VWAP over the 15
  trading days ending the day before the last trading day before closing.

The VWAP is estimated from daily bars as sum(typical price x volume) /
sum(volume), typical price = (high + low + close) / 3. Days after
2026-11-25 are filled at each scenario's TEM price.

Scenarios are values at closing, conditional on the deal closing, with TEM 20%
below, at, or 20% above its 2026-11-24 close. The 27/50/23 weights reproduce
the expectation of a 98% close with TEM down or up 20% equally likely
(25/50/25) plus a 2% deal break valued at $12.00.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "data/PSNL/2026-11-25/sources/yahoo-chart-TEM-1mo-2026-11-25.json"

DEAL_CASH = 16.25
CASH_SHARE_NUMBER = 36_923_077
ELIGIBLE_SHARES = 95_701_564  # 108,740,631 outstanding less Tempus-held Cancelled Shares (8-K 2026-11-25)
FRACTION = CASH_SHARE_NUMBER / ELIGIBLE_SHARES
FLOOR, FIXED_RATIO, LOWER_FLOOR = 48.42, 0.3356, 46.00
PSNL_PRICE, TEM_REF = 14.53, 54.83  # 2026-11-24 closes, data/prices/
BREAK_VALUE, BREAK_ODDS = 12.00, 0.02

# Trading days after the committed bars (Thanksgiving 2026-11-26 is closed).
FUTURE = [date(2026, 11, 27), date(2026, 11, 30), date(2026, 12, 1), date(2026, 12, 2), date(2026, 12, 3)]


def bars() -> list[tuple[date, float, int]]:
    r = json.loads(CHART.read_text())["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    out = []
    for i, ts in enumerate(r["timestamp"]):
        day = datetime.fromtimestamp(ts, timezone.utc).date()
        typical = (q["high"][i] + q["low"][i] + q["close"][i]) / 3
        out.append((day, typical, q["volume"][i]))
    return out


def vwap(closing: date, fill: float) -> tuple[float, int]:
    known = bars()
    days = [(d, p, v) for d, p, v in known] + [(d, fill, None) for d in FUTURE]
    before = [x for x in days if x[0] < closing]
    window = before[-16:-1]  # 15 days ending the day before the last pre-closing trading day
    avg_vol = sum(v for _, _, v in known[-15:]) / 15
    num = sum(p * (v if v is not None else avg_vol) for _, p, v in window)
    den = sum(v if v is not None else avg_vol for _, _, v in window)
    return num / den, sum(1 for x in window if x[2] is None)


def package(tem_close: float, closing: date = date(2026, 12, 2)) -> dict[str, float]:
    pv, unknown = vwap(closing, tem_close)
    ratio = DEAL_CASH / pv if pv > FLOOR else FIXED_RATIO
    cash = FRACTION * DEAL_CASH
    stock = (1 - FRACTION) * ratio * tem_close
    return {"vwap": pv, "unknown_days": unknown, "ratio": ratio, "tem_per_psnl": (1 - FRACTION) * ratio,
            "cash": cash, "stock": stock, "value": cash + stock, "stock_share": stock / (cash + stock)}


def main() -> None:
    print(f"cash fraction {FRACTION:.6f}; cash per PSNL share ${FRACTION * DEAL_CASH:.4f}")
    print("\nVWAP and package by closing date (TEM held at the 2026-11-24 close for unknown days)")
    for d in (date(2026, 12, 1), date(2026, 12, 2), date(2026, 12, 3), date(2026, 12, 4)):
        p = package(TEM_REF, d)
        print(f"  close {d}: VWAP ${p['vwap']:.2f} ({p['unknown_days']} days assumed), ratio {p['ratio']:.4f}, "
              f"TEM per PSNL {p['tem_per_psnl']:.4f}, value ${p['value']:.2f}")

    cases = {"bear": TEM_REF * 0.8, "base": TEM_REF, "bull": TEM_REF * 1.2}
    vals = {k: package(t) for k, t in cases.items()}
    print("\nScenarios (close 2026-12-02)")
    for k, p in vals.items():
        print(f"  {k}: TEM ${cases[k]:.2f}, VWAP ${p['vwap']:.2f}, ratio {p['ratio']:.4f}, cash ${p['cash']:.2f} + "
              f"stock ${p['stock']:.2f} = ${p['value']:.2f} ({p['value'] / PSNL_PRICE - 1:+.1%}); stock share {p['stock_share']:.0%}")

    cond = 0.25 * vals["bear"]["value"] + 0.5 * vals["base"]["value"] + 0.25 * vals["bull"]["value"]
    expect = (1 - BREAK_ODDS) * cond + BREAK_ODDS * BREAK_VALUE
    w = {"bear": 0.27, "base": 0.50, "bull": 0.23}
    fv = sum(w[k] * vals[k]["value"] for k in w)
    print(f"\nexpected value: 98% x ${cond:.3f} + 2% x ${BREAK_VALUE:.2f} = ${expect:.3f}")
    print(f"weighted 27/50/23: ${fv:.2f} ({fv / PSNL_PRICE - 1:+.2%} to the close)")

    print("\nPackage value by TEM price at closing")
    for t in (35, 40, 45, 50, 54.83, 60, 65, 70, 75):
        p = package(t)
        print(f"  TEM ${t:>6.2f}: ${p['value']:.2f}  stock share {p['stock_share']:.0%}")

    # Reorg Threshold: stock must be at least 40% of value at the closing price.
    base = vals["base"]
    r = 0.4 * base["cash"] / ((1 - 0.4) * base["tem_per_psnl"])
    print(f"\nReorg Threshold binds only below TEM ${r:.2f}; walk-away right needs VWAP below ${LOWER_FLOOR:.2f}")
    print(f"TEM fall needed for the walk-away right: VWAP is ${base['vwap']:.2f}")


if __name__ == "__main__":
    main()
