"""Capture SEC EDGAR data once into committed files. Run: python3 -m capital.sec [TICKER ...]

Writes:
    data/companies.csv              ticker, CIK, SEC name, exchange, filer category, fiscal year end, SIC code
    data/sec/facts/<T>.csv          point-in-time XBRL facts for the concepts in CONCEPTS
    data/sec/restatements.csv       a period's value changed in a later filing (append-only)
    data/calendar/earnings.csv      earnings releases (8-K Item 2.02) and 10-Q/10-K/20-F/40-F filings
    data/sec/sources.json           when each file was last captured, with the response hash

Fact files are append-only and point-in-time: a row is (taxonomy, tag, unit, start, end, val,
accn, form, filed, fy, fp). Only the first filing of each distinct value for a period is
kept; a later filing with a different value (a restatement) adds a row. `fy`/`fp` describe
the filing, not the fact. The SEC `frame` field is deliberately not stored: it points at the
latest restated value and leaks the future into any backtest. See capital/pit.py.

SEC asks for <= 10 requests/second and a User-Agent with a contact email; this client sends
<= 5/second and reads the contact from CAPITAL_SEC_CONTACT (capital/config.py).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from capital import config, store

SEC = store.DATA / "sec"
FACTS = SEC / "facts"
CALENDAR = store.DATA / "calendar"
COMPANIES = store.DATA / "companies.csv"
RESTATEMENTS = SEC / "restatements.csv"
EARNINGS = CALENDAR / "earnings.csv"
SOURCES = SEC / "sources.json"

TICKERS_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"

# Concepts captured per filer. capital/pit.py maps them to metrics.
CONCEPTS: dict[str, tuple[str, ...]] = {
    "us-gaap": (
        "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
        "RevenuesNetOfInterestExpense", "GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic", "EarningsPerShareDiluted", "EarningsPerShareBasic",
        "NetCashProvidedByUsedInOperatingActivities", "PaymentsToAcquirePropertyPlantAndEquipment",
        "DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "ShareBasedCompensation",
        "InterestExpense", "IncomeTaxExpenseBenefit", "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "LongTermDebt", "LongTermDebtNoncurrent",
        "LongTermDebtCurrent", "DebtCurrent", "StockholdersEquity", "Assets", "Liabilities",
        "WeightedAverageNumberOfDilutedSharesOutstanding", "CommonStockSharesOutstanding",
        "PaymentsForRepurchaseOfCommonStock", "PaymentsOfDividends", "PaymentsOfDividendsCommonStock",
        "CashCashEquivalentsAndShortTermInvestments", "ShortTermInvestments",
        "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "MarketableSecuritiesCurrent",
    ),
    "ifrs-full": (
        "Revenue", "RevenueFromContractsWithCustomers", "RevenueAndOperatingIncome",
        "RevenueFromRenderingOfCargoAndMailTransportServices", "GrossProfit", "ProfitLossFromOperatingActivities",
        "ProfitLoss", "ProfitLossAttributableToOwnersOfParent", "DilutedEarningsLossPerShare",
        "BasicEarningsLossPerShare", "CashFlowsFromUsedInOperatingActivities",
        "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities", "CashAndCashEquivalents",
        "Borrowings", "NoncurrentPortionOfNoncurrentBorrowings", "CurrentBorrowings", "Equity",
        "EquityAttributableToOwnersOfParent", "Assets", "Liabilities",
        "WeightedAverageNumberOfOrdinarySharesOutstanding", "AdjustedWeightedAverageShares",
    ),
    "dei": ("EntityCommonStockSharesOutstanding",),
}

FACT_FIELDS = ["taxonomy", "tag", "unit", "start", "end", "val", "accn", "form", "filed", "fy", "fp"]
EARNINGS_FIELDS = ["ticker", "cik", "form", "items", "filing_date", "acceptance_utc", "session", "report_date", "accn"]
PERIODIC_FORMS = {"10-Q", "10-K", "20-F", "40-F", "10-K/A", "10-Q/A", "20-F/A", "40-F/A"}


class Client:
    def __init__(self) -> None:
        self.user_agent = config.sec_user_agent()
        self._last = 0.0

    def get(self, url: str) -> bytes:
        for attempt in range(5):
            wait = 0.2 - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = Request(url, headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip", "Accept": "application/json"})
            try:
                with urlopen(req, timeout=60) as resp:
                    body = resp.read()
                    if resp.headers.get("Content-Encoding") == "gzip" or body[:2] == b"\x1f\x8b":
                        body = gzip.decompress(body)
                    return body
            except HTTPError as exc:
                if exc.code == 404:
                    raise
                if exc.code in (403, 429, 500, 502, 503) and attempt < 4:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
            except URLError:
                if attempt < 4:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        raise RuntimeError(f"gave up on {url}")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def append_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> int:
    rows = list(rows)
    if not rows:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)
    return len(rows)


def fmt_val(v: Any) -> str:
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def fact_rows(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Facts for CONCEPTS, oldest filing first, first filing of each distinct value only."""
    rows = []
    for taxonomy, tags in CONCEPTS.items():
        facts = payload.get("facts", {}).get(taxonomy, {})
        for tag in tags:
            for unit, items in (facts.get(tag) or {}).get("units", {}).items():
                for f in items:
                    rows.append({
                        "taxonomy": taxonomy, "tag": tag, "unit": unit, "start": f.get("start", ""), "end": f["end"],
                        "val": fmt_val(f["val"]), "accn": f["accn"], "form": f.get("form", ""), "filed": f["filed"],
                        "fy": str(f.get("fy") or ""), "fp": f.get("fp") or "",
                    })
    rows.sort(key=lambda r: (r["filed"], r["accn"], r["taxonomy"], r["tag"], r["unit"], r["end"], r["start"]))
    seen: dict[tuple, str] = {}
    out = []
    for r in rows:
        key = (r["taxonomy"], r["tag"], r["unit"], r["start"], r["end"])
        if seen.get(key) == r["val"]:
            continue
        seen[key] = r["val"]
        out.append(r)
    return out


def capture_facts(ticker: str, cik: int, client: Client, sources: dict[str, Any]) -> tuple[int, int]:
    """Append new fact rows; log restatements. Returns (rows added, restatements)."""
    try:
        body = client.get(FACTS_URL.format(cik=cik))
    except HTTPError as exc:
        if exc.code == 404:
            return 0, 0
        raise
    payload = json.loads(body)
    path = FACTS / f"{ticker}.csv"
    existing = read_csv(path)
    have = {(r["taxonomy"], r["tag"], r["unit"], r["start"], r["end"], r["val"]) for r in existing}
    latest: dict[tuple, dict[str, str]] = {}
    for r in existing:
        latest[(r["taxonomy"], r["tag"], r["unit"], r["start"], r["end"])] = r
    new_rows, restated = [], []
    for r in fact_rows(payload):
        key = (r["taxonomy"], r["tag"], r["unit"], r["start"], r["end"])
        if key + (r["val"],) in have:
            continue
        prior = latest.get(key)
        if prior and r["filed"] < prior["filed"]:
            continue  # older than what we already hold for this period; history is append-only
        if prior and prior["val"] != r["val"]:
            restated.append({
                "ticker": ticker, "taxonomy": r["taxonomy"], "tag": r["tag"], "unit": r["unit"], "start": r["start"],
                "end": r["end"], "old_val": prior["val"], "old_accn": prior["accn"], "old_filed": prior["filed"],
                "new_val": r["val"], "new_accn": r["accn"], "new_filed": r["filed"], "detected": now()[:10],
            })
        latest[key] = r
        have.add(key + (r["val"],))
        new_rows.append(r)
    added = append_csv(path, FACT_FIELDS, new_rows)
    # Only log restatements against rows that were committed before this capture.
    if existing:
        append_csv(RESTATEMENTS, list(restated[0].keys()) if restated else [], restated)
    sources[f"facts/{ticker}"] = {"url": FACTS_URL.format(cik=cik), "fetched_at": now(), "sha256": store.sha256_bytes(body)}
    return added, len(restated) if existing else 0


def session(acceptance_utc: str) -> str:
    """pre / during / post US regular session, from the EDGAR acceptance time (UTC)."""
    if not acceptance_utc:
        return ""
    t = datetime.fromisoformat(acceptance_utc.replace("Z", "+00:00"))
    # US Eastern is UTC-4 in daylight time (mid-March to early November) and UTC-5 otherwise; this is
    # approximate at the switch weeks but only labels the session.
    offset = 4 if 3 <= t.month <= 10 else 5
    minutes = (t.hour - offset) * 60 + t.minute
    minutes %= 24 * 60
    if minutes < 9 * 60 + 30:
        return "pre"
    if minutes < 16 * 60:
        return "during"
    return "post"


def capture_calendar(ticker: str, cik: int, client: Client, sources: dict[str, Any], meta: dict[str, Any]) -> int:
    body = client.get(SUBMISSIONS_URL.format(cik=cik))
    d = json.loads(body)
    meta["category"] = d.get("category") or ""
    meta["fiscal_year_end"] = d.get("fiscalYearEnd") or ""
    meta["sic"] = d.get("sic") or ""
    meta["sic_description"] = d.get("sicDescription") or ""
    r = d["filings"]["recent"]
    have = {row["accn"] for row in read_csv(EARNINGS) if row["ticker"] == ticker}
    rows = []
    for i in range(len(r["form"])):
        form, items = r["form"][i], r["items"][i] or ""
        is_release = form in ("8-K", "6-K") and "2.02" in items.split(",")
        if not (is_release or form in PERIODIC_FORMS):
            continue
        accn = r["accessionNumber"][i]
        if accn in have:
            continue
        rows.append({
            "ticker": ticker, "cik": cik, "form": form, "items": items, "filing_date": r["filingDate"][i],
            "acceptance_utc": r["acceptanceDateTime"][i], "session": session(r["acceptanceDateTime"][i]),
            "report_date": r["reportDate"][i], "accn": accn,
        })
    rows.sort(key=lambda x: (x["filing_date"], x["accn"]))
    sources[f"submissions/{ticker}"] = {"url": SUBMISSIONS_URL.format(cik=cik), "fetched_at": now(), "sha256": store.sha256_bytes(body)}
    return append_csv(EARNINGS, EARNINGS_FIELDS, rows)


def ticker_map(client: Client) -> dict[str, dict[str, Any]]:
    d = json.loads(client.get(TICKERS_URL))
    idx = {f: i for i, f in enumerate(d["fields"])}
    return {row[idx["ticker"]].upper(): {"cik": int(row[idx["cik"]]), "name": row[idx["name"]], "exchange": row[idx["exchange"]]} for row in d["data"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tickers", nargs="*", help="default: every covered ticker")
    args = parser.parse_args(argv)
    client = Client()
    sources = store.load_json(SOURCES) if SOURCES.exists() else {}
    latest = store.latest_calls()
    first: dict[str, str] = {}
    for c in store.iter_calls():
        first[c.ticker] = min(first.get(c.ticker, c.date), c.date)
    wanted = [t.upper() for t in args.tickers] or sorted(latest)
    tmap = ticker_map(client)
    companies = {r["ticker"]: r for r in read_csv(COMPANIES)}
    missing = []
    for t in wanted:
        info = tmap.get(t) or tmap.get(t.replace(".", "-"))
        if not info:
            missing.append(t)
            continue
        meta: dict[str, Any] = {}
        n_cal = capture_calendar(t, info["cik"], client, sources, meta)
        added, restated = capture_facts(t, info["cik"], client, sources)
        call = latest.get(t)
        companies[t] = {
            "ticker": t, "cik": info["cik"], "sec_name": info["name"], "exchange": info["exchange"],
            "filer_category": meta.get("category", ""), "fiscal_year_end": meta.get("fiscal_year_end", ""),
            "sector": (call.call.get("sector") or "") if call else "", "first_call": first.get(t, ""),
            "sic": meta.get("sic", ""), "sic_description": meta.get("sic_description", ""),
        }
        print(f"{t}: facts +{added}, restatements {restated}, calendar +{n_cal}")
    fields = ["ticker", "cik", "sec_name", "exchange", "filer_category", "fiscal_year_end", "sector", "first_call", "sic", "sic_description"]
    with COMPANIES.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(companies[k] for k in sorted(companies))
    store.write_json(SOURCES, dict(sorted(sources.items())))
    if missing:
        print("not in the SEC ticker map: " + ", ".join(missing), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
