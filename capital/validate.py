"""Offline checks for the data store. Run: python3 -m capital.validate

Nothing here touches the network. A failing check prints one line per problem and
exits 1. The checks:

- every call.json, inputs.json, and sources/manifest.json matches its schema;
- the directory name matches the call's ticker and date, and files are canonical JSON;
- scenario values are ordered bear <= base <= bull and weights sum to 1;
- fair value and deviation from the Street agree with the numbers they come from;
- inputs.json agrees with call.json on the price;
- every manifest entry still hashes to its recorded SHA-256;
- every evidence quote appears verbatim in the report version the call cites;
- calls written by a research run (origin=run) carry the fields a reviewer needs;
- price files are well formed.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from capital import store

SCHEMA_FILES = {
    "call": "call.schema.json",
    "inputs": "inputs.schema.json",
    "manifest": "manifest.schema.json",
}

RUN_REQUIRED_REPORT_HEADINGS = (
    "Thesis In One Page",
    "Valuation",
    "Catalysts",
    "Risks",
    "What Would Change My Mind",
    "Pre-Mortem",
    "Sources",
)

_validators: dict[str, Draft202012Validator] = {}


def validator(kind: str) -> Draft202012Validator:
    if kind not in _validators:
        schema = store.load_json(store.SCHEMAS / SCHEMA_FILES[kind])
        Draft202012Validator.check_schema(schema)
        _validators[kind] = Draft202012Validator(schema)
    return _validators[kind]


def normalize(text: str) -> str:
    """Whitespace-collapsed text with markdown emphasis, backticks, and table pipes removed."""
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[*`|]", "", text)
    text = re.sub(r"\\([$_\[\]()#+\-.!])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def check_schema(kind: str, obj: Any, where: str, errors: list[str]) -> None:
    for err in sorted(validator(kind).iter_errors(obj), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{where}: schema: {loc}: {err.message}")


def check_canonical(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if text != store.dumps(store.load_json(path)):
        errors.append(f"{path.relative_to(store.ROOT)}: not canonical JSON (run python3 -m capital.fmt)")


def check_call(c: store.Call, errors: list[str]) -> None:
    rel = c.dir.relative_to(store.ROOT)
    call = c.call
    check_schema("call", call, f"{rel}/call.json", errors)
    check_canonical(c.dir / "call.json", errors)
    if c.inputs is not None:
        check_schema("inputs", c.inputs, f"{rel}/inputs.json", errors)
        check_canonical(c.dir / "inputs.json", errors)
    if c.manifest is not None:
        check_schema("manifest", c.manifest, f"{rel}/sources/manifest.json", errors)
        check_canonical(c.dir / "sources" / "manifest.json", errors)

    ticker, date = c.dir.parent.name, c.dir.name
    if call.get("ticker") != ticker or call.get("date") != date:
        errors.append(f"{rel}: directory says {ticker}/{date} but call.json says {call.get('ticker')}/{call.get('date')}")
    if c.inputs is not None and (c.inputs.get("ticker") != ticker or c.inputs.get("date") != date):
        errors.append(f"{rel}/inputs.json: ticker/date do not match the directory")

    scen = call.get("scenarios") or {}
    values = [(n, (scen.get(n) or {}).get("value")) for n in ("bear", "base", "bull")]
    present = [(n, v) for n, v in values if v is not None]
    for (n1, v1), (n2, v2) in zip(present, present[1:]):
        if v1 > v2:
            errors.append(f"{rel}: scenario {n1} ${v1} is above {n2} ${v2}")
    for n in ("bear", "base", "bull"):
        s = scen.get(n) or {}
        lo, hi, v = s.get("low"), s.get("high"), s.get("value")
        if lo is not None and hi is not None and not (lo <= (v if v is not None else lo) <= hi):
            errors.append(f"{rel}: scenario {n} value {v} is outside its range {lo}-{hi}")
    weights = [(scen.get(n) or {}).get("weight") for n in ("bear", "base", "bull") if scen.get(n)]
    if weights and all(w is not None for w in weights) and abs(sum(weights) - 1) > 0.011:
        errors.append(f"{rel}: scenario weights sum to {sum(weights):.3f}, not 1")

    fv = call.get("fair_value")
    weighted = store.weighted_value(scen)
    if fv and fv["method"] == "weighted":
        if weighted is None:
            errors.append(f"{rel}: fair_value method is weighted but scenarios lack values or weights")
        elif abs(weighted - fv["value"]) > max(0.015 * fv["value"], 0.02):
            errors.append(f"{rel}: fair_value {fv['value']} does not match weighted scenarios {weighted:.2f}")
    if fv and fv["method"] == "base" and (scen.get("base") or {}).get("value") != fv["value"]:
        errors.append(f"{rel}: fair_value method is base but value differs from the base scenario")

    dev = call.get("deviation_from_street")
    street = call.get("street") or {}
    if dev:
        fair = store.fair_value(call)
        mean = street.get("target_mean")
        if fair is None or not mean:
            errors.append(f"{rel}: deviation_from_street needs a fair value and street.target_mean")
        else:
            expect = (fair / mean - 1) * 100
            if abs(expect - dev["pct"]) > 0.6:
                errors.append(f"{rel}: deviation_from_street.pct {dev['pct']} but fair value vs Street mean is {expect:.1f}")

    if c.inputs is not None:
        price = (c.inputs.get("values") or {}).get("price")
        if price and abs(price["value"] - call["price"]["value"]) > 0.005:
            errors.append(f"{rel}: inputs price {price['value']} differs from call price {call['price']['value']}")

    check_manifest(c, errors)
    check_evidence(c, errors)
    check_artifacts(c, errors)
    if call.get("origin") == "run":
        check_run_call(c, errors)


def check_manifest(c: store.Call, errors: list[str]) -> None:
    if not c.manifest:
        return
    rel = c.dir.relative_to(store.ROOT)
    ids: set[str] = set()
    for entry in c.manifest.get("entries", []):
        if entry["id"] in ids:
            errors.append(f"{rel}/sources/manifest.json: duplicate id {entry['id']}")
        ids.add(entry["id"])
        if entry["kind"] == "file":
            path = c.dir / "sources" / entry["path"]
            data = path.read_bytes() if path.exists() else None
        else:
            if not entry.get("commit"):
                errors.append(f"{rel}/sources/manifest.json: repo entry {entry['id']} needs a commit")
                continue
            data = store.git_blob(entry["commit"], entry["path"])
        if data is None:
            errors.append(f"{rel}/sources/manifest.json: {entry['id']} ({entry['path']}) is missing")
        elif store.sha256_bytes(data) != entry["sha256"]:
            errors.append(f"{rel}/sources/manifest.json: {entry['id']} ({entry['path']}) hash changed")
    if c.manifest:
        saved = {e["path"] for e in c.manifest.get("entries", []) if e["kind"] == "file"}
        for path in (c.dir / "sources").rglob("*"):
            name = path.relative_to(c.dir / "sources").as_posix()
            if path.is_file() and name != "manifest.json" and name not in saved:
                errors.append(f"{rel}/sources/{name}: not listed in manifest.json")


def _artifact_texts(call: dict[str, Any]) -> list[str]:
    texts = []
    for artifact in (call.get("artifacts") or {}).values():
        data = store.artifact_bytes(artifact)
        if data is not None and not artifact["path"].endswith(".xlsx"):
            texts.append(normalize(data.decode("utf-8", errors="replace")))
    return texts


def check_evidence(c: store.Call, errors: list[str]) -> None:
    rel = c.dir.relative_to(store.ROOT)
    quotes = list((c.call.get("evidence") or {}).items())
    for name, value in ((c.inputs or {}).get("values") or {}).items():
        if value.get("quote"):
            quotes.append((f"inputs.{name}", value["quote"]))
    if not quotes:
        return
    texts = _artifact_texts(c.call)
    for field, quote in quotes:
        q = normalize(quote)
        if not any(q in t for t in texts):
            errors.append(f"{rel}: evidence for {field} not found verbatim in the cited artifacts: {quote[:90]!r}")


def check_artifacts(c: store.Call, errors: list[str]) -> None:
    rel = c.dir.relative_to(store.ROOT)
    for name, artifact in (c.call.get("artifacts") or {}).items():
        if artifact and store.artifact_bytes(artifact) is None:
            where = f"{artifact['path']}@{artifact['commit']}" if artifact.get("commit") else artifact["path"]
            errors.append(f"{rel}: artifacts.{name} {where} does not exist")


MIN_CLAIMS = 3
MIN_PREMORTEM = 3


def check_run_call(c: store.Call, errors: list[str]) -> None:
    """Calls written by a research run carry the decision journal a reviewer and the scorecard need."""
    from capital import score

    rel = c.dir.relative_to(store.ROOT)
    call = c.call
    if c.inputs is None:
        errors.append(f"{rel}: runs must commit inputs.json")
    if not c.manifest or not c.manifest.get("entries"):
        errors.append(f"{rel}: runs must commit sources/manifest.json with at least one source")
    for field in ("stance", "next_review", "thesis", "consensus_view", "variant_view", "fair_value", "primary_lens", "horizon_years"):
        if not call.get(field):
            errors.append(f"{rel}: runs must set {field}")
    for field in ("catalysts", "change_my_mind", "kill_criteria", "why_opportunity"):
        if not call.get(field):
            errors.append(f"{rel}: runs must list {field}")
    for case in ("bear", "base", "bull"):
        s = (call.get("scenarios") or {}).get(case) or {}
        if s.get("value") is None or s.get("weight") is None:
            errors.append(f"{rel}: runs must give the {case} scenario a value and a weight")
    if len(call.get("premortem") or []) < MIN_PREMORTEM:
        errors.append(f"{rel}: runs must give at least {MIN_PREMORTEM} pre-mortem reasons, each with a signal")
    claims = call.get("claims") or []
    if len(claims) < MIN_CLAIMS:
        errors.append(f"{rel}: runs must make at least {MIN_CLAIMS} resolvable probability claims")
    ids = [k["id"] for k in claims]
    if len(ids) != len(set(ids)):
        errors.append(f"{rel}: claim ids must be unique")
    for k in claims:
        if k["resolve_by"] <= call["date"]:
            errors.append(f"{rel}: claim {k['id']} resolves on or before the call date")
    if not any((k.get("kind") == "hard" and k.get("date")) for k in call.get("catalysts") or []):
        errors.append(f"{rel}: runs must list at least one hard catalyst with a date")
    dev = call.get("deviation_from_street")
    if dev and abs(dev["pct"]) >= 10 and not dev.get("reason"):
        errors.append(f"{rel}: deviation from the Street is {dev['pct']:.1f}%; give a reason")
    rule = score.rule_rating(call)
    if rule and call.get("stance") in ("own", "watch", "avoid") and call["stance"] != rule and not call.get("rating_override_reason"):
        errors.append(f"{rel}: stance {call['stance']} differs from the rule rating {rule}; set rating_override_reason")
    for r in call.get("resolutions") or []:
        key, cid = r["claim"].split("#")
        target = store.DATA / key / "call.json"
        if not target.exists() or key >= f"{call['ticker']}/{call['date']}":
            errors.append(f"{rel}: resolution {r['claim']} must point at an earlier call")
        elif cid not in {k["id"] for k in store.load_json(target).get("claims") or []}:
            errors.append(f"{rel}: resolution {r['claim']}: no such claim")
    if call.get("prior_call"):
        prior = store.DATA / call["prior_call"] / "call.json"
        if not prior.exists():
            errors.append(f"{rel}: prior_call {call['prior_call']} does not exist")
        elif call["prior_call"] >= f"{call['ticker']}/{call['date']}" or not call["prior_call"].startswith(call["ticker"] + "/"):
            errors.append(f"{rel}: prior_call must be an earlier call on the same ticker")
    if call.get("research_status") in ("post_earnings", "no_change_review") and not (call.get("update") or {}).get("event"):
        errors.append(f"{rel}: updates must fill the update block (event, expected, actual, pillars, action)")
    report = store.artifact_bytes((call.get("artifacts") or {}).get("report"))
    if report is not None and call.get("research_status") not in ("post_earnings", "no_change_review"):
        text = report.decode("utf-8", errors="replace")
        headings = {normalize(re.sub(r"^#+\s*(\d+\.\s*)?", "", h)).lower() for h in re.findall(r"^#{1,3} .+$", text, re.M)}
        for required in RUN_REQUIRED_REPORT_HEADINGS:
            if not any(h.startswith(required.lower()) for h in headings):
                errors.append(f"{rel}: report {call['artifacts']['report']['path']} lacks a '{required}' section")


def check_call_prices(errors: list[str]) -> None:
    """A call's stated price must match the committed close on its price date."""
    from capital import config, prices

    exceptions_path = store.PRICES / "exceptions.json"
    exceptions = store.load_json(exceptions_path) if exceptions_path.exists() else {}
    for c in store.iter_calls():
        day = c.call["price"].get("date")
        rows = prices.closes(c.ticker) if day else []
        if not rows or c.key in exceptions:
            continue
        on_or_before = [r for r in rows if r[0] <= day]
        if not on_or_before or on_or_before[-1][0] != day:
            continue
        close = on_or_before[-1][1]
        diff = c.call["price"]["value"] / close - 1
        if abs(diff) > config.PRICE_CHECK_TOLERANCE:
            errors.append(
                f"{c.dir.relative_to(store.ROOT)}: price {c.call['price']['value']} is {diff:+.1%} from the committed "
                f"{day} close {close}; fix the call or add a reason to data/prices/exceptions.json"
            )
    for key in exceptions:
        if not (store.DATA / key / "call.json").exists():
            errors.append(f"data/prices/exceptions.json: {key} is not a call")


def check_prices(errors: list[str]) -> None:
    if not store.PRICES.exists():
        return
    for path in sorted(store.PRICES.glob("*.csv")):
        rel = path.relative_to(store.ROOT)
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames != ["date", "close", "adj_close"]:
                errors.append(f"{rel}: header must be date,close,adj_close")
                continue
            prev = ""
            for i, row in enumerate(reader, start=2):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["date"] or "") or row["date"] <= prev:
                    errors.append(f"{rel}:{i}: dates must be ISO and strictly increasing")
                    break
                prev = row["date"]
                try:
                    if float(row["close"]) <= 0 or float(row["adj_close"]) <= 0:
                        raise ValueError
                except ValueError:
                    errors.append(f"{rel}:{i}: close and adj_close must be positive numbers")
                    break


def check_sec(errors: list[str]) -> None:
    """SEC files have the expected columns and every fact's accession and filed date are well formed."""
    from capital.sec import EARNINGS_FIELDS, FACT_FIELDS

    FACTS = store.DATA / "sec" / "facts"
    EARNINGS = store.DATA / "calendar" / "earnings.csv"
    for path in sorted(FACTS.glob("*.csv")) if FACTS.exists() else []:
        rel = path.relative_to(store.ROOT)
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames != FACT_FIELDS:
                errors.append(f"{rel}: header must be {','.join(FACT_FIELDS)}")
                continue
            for i, row in enumerate(reader, start=2):
                if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", row["accn"]) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["filed"]):
                    errors.append(f"{rel}:{i}: malformed accn or filed date")
                    break
    if EARNINGS.exists():
        with EARNINGS.open(newline="") as fh:
            if csv.DictReader(fh).fieldnames != EARNINGS_FIELDS:
                errors.append(f"{EARNINGS.relative_to(store.ROOT)}: header must be {','.join(EARNINGS_FIELDS)}")


def check_workbooks(errors: list[str]) -> None:
    """Workbooks rendered by capital.workbook are values only and their master check passes."""
    from openpyxl import load_workbook

    for path in sorted((store.ROOT / "models").glob("*/????-??-??.xlsx")):
        rel = path.relative_to(store.ROOT)
        if not (store.DATA / path.parent.name / path.stem / "call.json").exists():
            errors.append(f"{rel}: no matching call in data/")
            continue
        wb = load_workbook(path)
        for ws in wb:
            if ws.sheet_state != "visible":
                errors.append(f"{rel}: sheet {ws.title} is hidden")
            if ws["B1"].value != "MASTER CHECK: OK":
                errors.append(f"{rel}: sheet {ws.title} master check is {ws['B1'].value!r}")
            for row in ws.iter_rows():
                for cell in row:
                    if isinstance(cell.value, str) and cell.value.startswith("="):
                        errors.append(f"{rel}: {ws.title}!{cell.coordinate} holds a formula; workbooks are values only")
                        break


def check_coverage(errors: list[str]) -> None:
    path = store.DATA / "coverage.csv"
    if not path.exists():
        return
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != store.COVERAGE_FIELDS:
            errors.append(f"data/coverage.csv: header must be {','.join(store.COVERAGE_FIELDS)}")
            return
        rows = list(reader)
    seen = set()
    for i, r in enumerate(rows, start=2):
        t = r["ticker"]
        if t in seen:
            errors.append(f"data/coverage.csv:{i}: duplicate {t}")
        seen.add(t)
        if r["status"] not in store.COVERAGE_STATUSES:
            errors.append(f"data/coverage.csv:{i}: status must be one of {', '.join(store.COVERAGE_STATUSES)}")
        if r["status"] == "dropped" and not r["reason"]:
            errors.append(f"data/coverage.csv:{i}: dropped names need a reason")
        if r["status"] == "watchlist":
            try:
                if float(r["entry_price"]) <= 0:
                    raise ValueError
            except ValueError:
                errors.append(f"data/coverage.csv:{i}: watchlist names need a positive entry_price")
    for t in sorted({c.ticker for c in store.iter_calls()} - seen):
        errors.append(f"data/coverage.csv: {t} has calls but no coverage row")


def run() -> list[str]:
    errors: list[str] = []
    for path in sorted(store.DATA.glob("*/*/")):
        if path.parent.name == "prices" or path.parent == store.DATA:
            continue
        if path.is_dir() and not (path / "call.json").exists() and path.parent.parent == store.DATA:
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.name):
                errors.append(f"{path.relative_to(store.ROOT)}: dated directory without call.json")
    for c in store.iter_calls():
        check_call(c, errors)
    check_prices(errors)
    check_call_prices(errors)
    check_sec(errors)
    check_workbooks(errors)
    check_coverage(errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    errors = run()
    for line in errors:
        print(line)
    n = len(store.call_dirs())
    if errors:
        print(f"\n{len(errors)} problem(s) across {n} call(s)", file=sys.stderr)
        return 1
    print(f"ok: {n} call(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
