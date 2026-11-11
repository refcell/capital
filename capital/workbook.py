"""Render a call's workbook from committed data. Run: python3 -m capital.workbook TICKER DATE

Writes models/<TICKER>/<DATE>.xlsx. The workbook is a view of data/<TICKER>/<DATE>/:
every cell is a value (no live formulas), every input carries its source and as-of
date, and a Checks sheet repeats the data-store checks with a master result shown on
every sheet. Sheet order follows the FAST/ICAEW layout: Notes, Inputs, Scenarios,
Fundamentals, Checks, Sources.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from capital import config, pit, prices, score, store

MODELS = store.ROOT / "models"
NAVY, INPUT_FILL, HEAD_FILL, OK_FILL, BAD_FILL = "17365D", "FFF2CC", "D9EAF7", "C6EFCE", "FFC7CE"
THIN = Side(style="thin", color="A6A6A6")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def path_for(ticker: str, day: str) -> Path:
    return MODELS / ticker / f"{day}.xlsx"


def checks(c: store.Call) -> list[tuple[str, bool, str]]:
    """(check, passed, detail). Mirrors capital.validate for the numbers in this workbook."""
    call, out = c.call, []
    scen = call.get("scenarios") or {}
    vals = [(scen.get(k) or {}).get("value") for k in ("bear", "base", "bull")]
    if None not in vals:
        out.append(("Scenarios ordered bear <= base <= bull", vals[0] <= vals[1] <= vals[2], " / ".join(f"{v:,.2f}" for v in vals)))
    weights = [(scen.get(k) or {}).get("weight") for k in ("bear", "base", "bull")]
    if None not in weights:
        out.append(("Weights sum to 100%", abs(sum(weights) - 1) <= 0.011, f"{sum(weights):.0%}"))
    weighted, fv = store.weighted_value(scen), call.get("fair_value")
    if weighted is not None and fv:
        out.append(("Fair value matches weighted scenarios", abs(weighted - fv["value"]) <= max(0.015 * fv["value"], 0.02), f"{fv['value']:,.2f} vs {weighted:,.2f}"))
    day = call["price"].get("date")
    rows = [r for r in prices.closes(c.ticker) if day and r[0] == day]
    if rows:
        diff = call["price"]["value"] / rows[0][1] - 1
        out.append(("Price matches the committed close", abs(diff) <= config.PRICE_CHECK_TOLERANCE, f"{call['price']['value']:,.2f} vs {rows[0][1]:,.2f} ({diff:+.1%})"))
    values = (c.inputs or {}).get("values") or {}
    if "market_cap_m" in values and "shares_outstanding_m" in values:
        mc = call["price"]["value"] * values["shares_outstanding_m"]["value"]
        got = values["market_cap_m"]["value"]
        out.append(("Market cap = price x shares", abs(mc / got - 1) <= 0.05, f"{got:,.0f} vs {mc:,.0f}"))
    dev, street = call.get("deviation_from_street"), call.get("street") or {}
    if dev and street.get("target_mean") and store.fair_value(call):
        expect = (store.fair_value(call) / street["target_mean"] - 1) * 100
        out.append(("Deviation from Street matches", abs(expect - dev["pct"]) <= 0.6, f"{dev['pct']:+.1f}% vs {expect:+.1f}%"))
    return out


class Sheet:
    def __init__(self, wb: Workbook, title: str, master: bool, first: bool = False) -> None:
        self.ws = wb.active if first else wb.create_sheet()
        self.ws.title = title
        self.row = 1
        self.put(1, title, bold=True, size=14, color=NAVY)
        self.put(2, "MASTER CHECK: " + ("OK" if master else "FAIL"), bold=True, fill=OK_FILL if master else BAD_FILL)
        self.row = 3

    def put(self, col: int, value: Any, *, bold: bool = False, size: int = 10, color: str = "000000", fill: str | None = None, fmt: str | None = None) -> None:
        cell = self.ws.cell(row=self.row, column=col, value=value)
        cell.font = Font(name="Aptos", size=size, bold=bold, color=color)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        if fill:
            cell.fill = PatternFill("solid", fgColor=fill)
        if fmt:
            cell.number_format = fmt
        if self.row > 2:
            cell.border = BORDER

    def header(self, *names: str) -> None:
        self.row += 1
        for i, n in enumerate(names, 1):
            self.put(i, n, bold=True, fill=HEAD_FILL)
        self.row += 1

    def line(self, *values: Any, fill: str | None = None, fmts: dict[int, str] | None = None) -> None:
        for i, v in enumerate(values, 1):
            self.put(i, v, fill=fill if i > 1 else None, fmt=(fmts or {}).get(i))
        self.row += 1

    def widths(self, *ws: int) -> None:
        for i, w in enumerate(ws):
            self.ws.column_dimensions[chr(65 + i)].width = w


def render(c: store.Call) -> Workbook:
    call = c.call
    results = checks(c)
    master = all(ok for _, ok, _ in results)
    wb = Workbook()
    wb.properties.creator = "capital.workbook"
    wb.properties.created = wb.properties.modified = datetime.fromisoformat(call["date"])

    s = Sheet(wb, "Notes", master, first=True)
    s.widths(28, 90)
    rule = score.rule_rating(call)
    er = score.expected_annual(call)
    for k, v in (
        ("Company", f"{call['company']} ({call.get('exchange') or ''}: {call['ticker']})"),
        ("Call date", call["date"]),
        ("Stance (published)", call["stance_text"]),
        ("Rule rating", f"{rule or '—'} ({er:+.1%} a year over {config.RATING_HORIZON_YEARS} years)" if er is not None else "—"),
        ("Rating rule", "; ".join(f"{k}: {v}" for k, v in config.RATING_DEFINITIONS.items())),
        ("Valuation lens", call.get("lens_text") or call.get("primary_lens") or "—"),
        ("Thesis", call.get("thesis") or "—"),
        ("Consensus view", call.get("consensus_view") or "—"),
        ("Variant view", call.get("variant_view") or "—"),
        ("Data", f"data/{call['ticker']}/{call['date']}/ — this workbook is rendered from it; edit the data, not the workbook."),
        ("Qualifications", "Values only, no live formulas. Inputs are as captured on the call date; SEC fundamentals are as filed on or before it. "
         "Scenario values are per share in the call's currency. " + " ".join(n for n in call.get("notes", []) if "generated by" not in n)),
    ):
        s.line(k, v)

    s = Sheet(wb, "Inputs", master)
    s.widths(28, 16, 12, 60, 24)
    s.header("Input", "Value", "As of", "Source", "Accession")
    for key, v in sorted(((c.inputs or {}).get("values") or {}).items()):
        s.line(key, v["value"], v.get("as_of") or "", v["source"], v.get("accession") or "", fill=INPUT_FILL, fmts={2: "#,##0.00"})
    street = call.get("street") or {}
    s.line("price (call)", call["price"]["value"], call["price"].get("date") or "", "call.json", "", fill=INPUT_FILL, fmts={2: "#,##0.00"})
    for k in ("target_mean", "target_median", "target_low", "target_high", "analysts"):
        if street.get(k) is not None:
            s.line(f"street {k}", street[k], street.get("as_of") or "", street.get("source") or "call.json", "", fill=INPUT_FILL, fmts={2: "#,##0.00"})

    s = Sheet(wb, "Scenarios", master)
    s.widths(16, 14, 10, 14, 14, 60)
    s.header("Scenario", "Value / share", "Weight", "vs price", "Annualized", "Basis")
    px = call["price"]["value"]
    years = config.RATING_HORIZON_YEARS
    for case in ("bear", "base", "bull"):
        sc = (call.get("scenarios") or {}).get(case) or {}
        v = sc.get("value")
        s.line(
            case.capitalize(), v, sc.get("weight"), (v / px - 1) if v is not None else None,
            ((v / px) ** (1 / years) - 1) if v else None, sc.get("basis") or "",
            fmts={2: "#,##0.00", 3: "0%", 4: "+0.0%;-0.0%", 5: "+0.0%;-0.0%"},
        )
    fv = store.fair_value(call)
    s.line("Fair value", fv, None, (fv / px - 1) if fv else None, er, (call.get("fair_value") or {}).get("method", ""),
           fmts={2: "#,##0.00", 4: "+0.0%;-0.0%", 5: "+0.0%;-0.0%"})
    dev = call.get("deviation_from_street")
    if dev:
        s.line("vs Street mean", street.get("target_mean"), None, dev["pct"] / 100, None, dev.get("reason") or "",
               fmts={2: "#,##0.00", 4: "+0.0%;-0.0%"})

    s = Sheet(wb, "Fundamentals", master)
    s.widths(24, 18, 10, 12, 14, 24)
    s.header("Metric", "Value", "Unit", "Period end", "Basis", "Accession")
    for metric, v in pit.as_of(call["ticker"], call["date"]).items():
        s.line(metric, v.value, v.unit, v.end, v.method, v.accns[-1], fmts={2: "#,##0.00"})

    s = Sheet(wb, "Checks", master)
    s.widths(42, 10, 50)
    s.header("Check", "Result", "Detail")
    for name, ok, detail in results:
        s.line(name, "OK" if ok else "FAIL", detail, fill=OK_FILL if ok else BAD_FILL)

    s = Sheet(wb, "Sources", master)
    s.widths(14, 50, 60, 66)
    s.header("Id", "Path", "URL", "SHA-256")
    for e in (c.manifest or {}).get("entries", []):
        s.line(e["id"], e["path"] + (f"@{e['commit']}" if e.get("commit") else ""), e.get("url") or "", e["sha256"])
    for name, a in (call.get("artifacts") or {}).items():
        if a:
            s.line(name, a["path"] + (f"@{a['commit']}" if a.get("commit") else ""), "", "")
    return wb


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ticker")
    parser.add_argument("date")
    args = parser.parse_args(argv)
    d = store.call_dir(args.ticker, args.date)
    if not (d / "call.json").exists():
        print(f"no call at {d.relative_to(store.ROOT)}", file=sys.stderr)
        return 1
    c = store.load_call(d)
    out = path_for(c.ticker, c.date)
    out.parent.mkdir(parents=True, exist_ok=True)
    render(c).save(out)
    failed = [n for n, ok, _ in checks(c) if not ok]
    print(f"wrote {out.relative_to(store.ROOT)}" + (f" with failing checks: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
