"""Point-in-time fundamentals from committed SEC facts. Reads only data/sec/facts/.

    as_of("PFE", "2020-06-01")["revenue"]  -> the value as known on that date

Only facts with filed <= the date are visible. For each period the latest such filing
wins, so a restatement filed later never leaks backward. Duration metrics are
trailing twelve months: the latest annual period, or FY + YTD - prior-year YTD when a
10-Q is newer than the 10-K, or the sum of the last four quarters. Instants (cash,
debt, equity, shares) are the latest balance on or before the date.

Run: python3 -m capital.pit TICKER [DATE]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from functools import lru_cache

from capital import store

FACTS = store.DATA / "sec" / "facts"

# metric -> (kind, candidate (taxonomy, tag) pairs in priority order)
METRICS: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {
    "revenue": ("duration", (
        ("us-gaap", "Revenues"), ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
        ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"),
        ("us-gaap", "SalesRevenueNet"), ("us-gaap", "RevenuesNetOfInterestExpense"),
        ("ifrs-full", "Revenue"), ("ifrs-full", "RevenueFromContractsWithCustomers"),
        ("ifrs-full", "RevenueAndOperatingIncome"), ("ifrs-full", "RevenueFromRenderingOfCargoAndMailTransportServices"),
    )),
    "gross_profit": ("duration", (("us-gaap", "GrossProfit"), ("ifrs-full", "GrossProfit"))),
    "operating_income": ("duration", (("us-gaap", "OperatingIncomeLoss"), ("ifrs-full", "ProfitLossFromOperatingActivities"))),
    "net_income": ("duration", (
        ("us-gaap", "NetIncomeLoss"), ("ifrs-full", "ProfitLossAttributableToOwnersOfParent"), ("ifrs-full", "ProfitLoss"),
    )),
    "eps_diluted": ("duration", (("us-gaap", "EarningsPerShareDiluted"), ("ifrs-full", "DilutedEarningsLossPerShare"))),
    "operating_cash_flow": ("duration", (
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivities"), ("ifrs-full", "CashFlowsFromUsedInOperatingActivities"),
    )),
    "capex": ("duration", (
        ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment"),
        ("ifrs-full", "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"),
    )),
    "stock_comp": ("duration", (("us-gaap", "ShareBasedCompensation"),)),
    "buybacks": ("duration", (("us-gaap", "PaymentsForRepurchaseOfCommonStock"),)),
    "cash": ("instant", (("us-gaap", "CashAndCashEquivalentsAtCarryingValue"), ("ifrs-full", "CashAndCashEquivalents"))),
    "short_term_investments": ("instant", (
        ("us-gaap", "ShortTermInvestments"), ("us-gaap", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"),
        ("us-gaap", "MarketableSecuritiesCurrent"),
    )),
    "cash_and_short_term_investments": ("instant", (("us-gaap", "CashCashEquivalentsAndShortTermInvestments"),)),
    "long_term_debt": ("instant", (
        ("us-gaap", "LongTermDebt"), ("us-gaap", "LongTermDebtNoncurrent"), ("ifrs-full", "Borrowings"),
        ("ifrs-full", "NoncurrentPortionOfNoncurrentBorrowings"),
    )),
    "equity": ("instant", (
        ("us-gaap", "StockholdersEquity"), ("ifrs-full", "EquityAttributableToOwnersOfParent"), ("ifrs-full", "Equity"),
    )),
    "total_assets": ("instant", (("us-gaap", "Assets"), ("ifrs-full", "Assets"))),
    "shares_outstanding": ("instant", (
        ("dei", "EntityCommonStockSharesOutstanding"), ("us-gaap", "CommonStockSharesOutstanding"),
    )),
    "diluted_shares": ("duration_latest", (
        ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding"), ("ifrs-full", "AdjustedWeightedAverageShares"),
    )),
}


@dataclass(frozen=True)
class Fact:
    taxonomy: str
    tag: str
    unit: str
    start: str
    end: str
    val: float
    accn: str
    form: str
    filed: str


@dataclass(frozen=True)
class Value:
    value: float
    unit: str
    start: str | None
    end: str
    method: str
    tag: str
    accns: tuple[str, ...]
    filed: str


@lru_cache(maxsize=256)
def facts(ticker: str) -> tuple[Fact, ...]:
    path = FACTS / f"{ticker}.csv"
    if not path.exists():
        return ()
    with path.open(newline="") as fh:
        return tuple(
            Fact(r["taxonomy"], r["tag"], r["unit"], r["start"], r["end"], float(r["val"]), r["accn"], r["form"], r["filed"])
            for r in csv.DictReader(fh)
        )


def days(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def visible(ticker: str, taxonomy: str, tag: str, on: str) -> dict[tuple[str, str, str], Fact]:
    """(unit, start, end) -> the latest fact filed on or before `on`."""
    out: dict[tuple[str, str, str], Fact] = {}
    for f in facts(ticker):
        if f.taxonomy != taxonomy or f.tag != tag or f.filed > on:
            continue
        key = (f.unit, f.start, f.end)
        prev = out.get(key)
        if prev is None or (f.filed, f.accn) > (prev.filed, prev.accn):
            out[key] = f
    return out


def _value(fs: list[Fact], method: str, tag: str) -> Value:
    total = sum(f.val for f in fs) if method != "ttm_ytd" else fs[0].val + fs[1].val - fs[2].val
    return Value(
        value=round(total, 6), unit=fs[0].unit, start=min(f.start for f in fs) if fs[0].start else None,
        end=max(f.end for f in fs), method=method, tag=tag, accns=tuple(sorted({f.accn for f in fs})),
        filed=max(f.filed for f in fs),
    )


def _near(target: str, candidates: dict[str, Fact], tol: int = 10) -> Fact | None:
    best = None
    for end, f in candidates.items():
        gap = abs(days(target, end))
        if gap <= tol and (best is None or gap < best[0]):
            best = (gap, f)
    return best[1] if best else None


def ttm(seen: dict[tuple[str, str, str], Fact], tag: str) -> Value | None:
    by_unit: dict[str, list[Fact]] = {}
    for (unit, start, _), f in seen.items():
        if start:
            by_unit.setdefault(unit, []).append(f)
    if not by_unit:
        return None
    unit = max(by_unit, key=lambda u: len(by_unit[u]))
    fs = by_unit[unit]
    annual = {f.end: f for f in fs if 350 <= days(f.start, f.end) <= 380}
    quarters = {f.end: f for f in fs if 80 <= days(f.start, f.end) <= 100}
    latest_end = max(f.end for f in fs)
    if latest_end in annual:
        return _value([annual[latest_end]], "annual", tag)
    # YTD route: the longest period ending at latest_end that starts a fiscal year.
    ytd = max((f for f in fs if f.end == latest_end), key=lambda f: days(f.start, f.end))
    length = days(ytd.start, ytd.end)
    if length < 350:
        prior_fy = _near((date.fromisoformat(ytd.start) - timedelta(days=1)).isoformat(), annual)
        prior_end = (date.fromisoformat(ytd.end) - timedelta(days=365)).isoformat()
        prior_ytd = None
        for f in fs:
            if abs(days(prior_end, f.end)) <= 10 and abs(days(f.start, f.end) - length) <= 10:
                prior_ytd = f
        if prior_fy and prior_ytd and length > 100:
            return _value([prior_fy, ytd, prior_ytd], "ttm_ytd", tag)
        if prior_fy and length <= 100:
            # Q1: FY + Q1 - prior-year Q1.
            prior_q = _near(prior_end, quarters)
            if prior_q:
                return _value([prior_fy, ytd, prior_q], "ttm_ytd", tag)
    # Sum of four consecutive quarters ending at the latest quarter.
    if latest_end in quarters:
        chain = [quarters[latest_end]]
        while len(chain) < 4:
            nxt = _near((date.fromisoformat(chain[-1].start) - timedelta(days=1)).isoformat(), quarters, tol=5)
            if not nxt:
                break
            chain.append(nxt)
        if len(chain) == 4:
            return _value(chain, "sum_4q", tag)
    # Fall back to the latest annual period, if any.
    if annual:
        return _value([annual[max(annual)]], "annual_stale", tag)
    return None


def latest_instant(seen: dict[tuple[str, str, str], Fact], tag: str, on: str) -> Value | None:
    fs = [f for (_, start, end), f in seen.items() if not start and end <= on]
    if not fs:
        return None
    f = max(fs, key=lambda f: (f.end, f.filed))
    return Value(f.val, f.unit, None, f.end, "instant", tag, (f.accn,), f.filed)


def latest_duration(seen: dict[tuple[str, str, str], Fact], tag: str) -> Value | None:
    fs = [f for (_, start, _), f in seen.items() if start]
    if not fs:
        return None
    f = max(fs, key=lambda f: (f.end, -days(f.start, f.end)))
    return Value(f.val, f.unit, f.start, f.end, "latest_period", tag, (f.accn,), f.filed)


def as_of(ticker: str, on: str) -> dict[str, Value]:
    out: dict[str, Value] = {}
    for metric, (kind, candidates) in METRICS.items():
        best: Value | None = None
        for taxonomy, tag in candidates:
            seen = visible(ticker, taxonomy, tag, on)
            if not seen:
                continue
            if kind == "duration":
                v = ttm(seen, f"{taxonomy}:{tag}")
            elif kind == "instant":
                v = latest_instant(seen, f"{taxonomy}:{tag}", on)
            else:
                v = latest_duration(seen, f"{taxonomy}:{tag}")
            # Prefer the candidate with the most recent period; ties keep the earlier (preferred) tag.
            if v and (best is None or v.end > best.end):
                best = v
        if best:
            out[metric] = best
    if "operating_cash_flow" in out and "capex" in out and out["operating_cash_flow"].end == out["capex"].end:
        ocf, capex = out["operating_cash_flow"], out["capex"]
        out["free_cash_flow"] = Value(
            ocf.value - capex.value, ocf.unit, ocf.start, ocf.end, ocf.method, "operating_cash_flow - capex",
            tuple(sorted(set(ocf.accns) | set(capex.accns))), max(ocf.filed, capex.filed),
        )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ticker")
    parser.add_argument("date", nargs="?", default=date.today().isoformat())
    args = parser.parse_args(argv)
    values = as_of(args.ticker.upper(), args.date)
    print(json.dumps({k: asdict(v) for k, v in values.items()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
