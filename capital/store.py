"""Paths, loading, and canonical writing for the committed data store.

Layout:
    data/<TICKER>/<YYYY-MM-DD>/call.json      the call (stance, scenarios, Street context)
    data/<TICKER>/<YYYY-MM-DD>/inputs.json    point-in-time inputs with sources
    data/<TICKER>/<YYYY-MM-DD>/sources/       saved sources + manifest.json
    data/prices/<SYMBOL>.csv                  daily closes captured once, append-only
"""

from __future__ import annotations

import functools
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRICES = DATA / "prices"
SCHEMAS = Path(__file__).resolve().parent / "schemas"


@dataclass(frozen=True)
class Call:
    dir: Path
    call: dict[str, Any]
    inputs: dict[str, Any] | None
    manifest: dict[str, Any] | None

    @property
    def ticker(self) -> str:
        return self.call["ticker"]

    @property
    def date(self) -> str:
        return self.call["date"]

    @property
    def key(self) -> str:
        return f"{self.ticker}/{self.date}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dumps(obj: Any) -> str:
    """Canonical JSON text for committed files: 2-space indent, UTF-8, trailing newline."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(obj), encoding="utf-8")


def call_dir(ticker: str, date: str) -> Path:
    return DATA / ticker.upper() / date


def call_dirs() -> list[Path]:
    return sorted(p.parent for p in DATA.glob("*/*/call.json"))


def load_call(path: Path) -> Call:
    inputs_path = path / "inputs.json"
    manifest_path = path / "sources" / "manifest.json"
    return Call(
        dir=path,
        call=load_json(path / "call.json"),
        inputs=load_json(inputs_path) if inputs_path.exists() else None,
        manifest=load_json(manifest_path) if manifest_path.exists() else None,
    )


def iter_calls() -> Iterator[Call]:
    for path in call_dirs():
        yield load_call(path)


def latest_calls() -> dict[str, Call]:
    """The most recent call per ticker."""
    latest: dict[str, Call] = {}
    for call in iter_calls():
        prev = latest.get(call.ticker)
        if prev is None or call.date > prev.date:
            latest[call.ticker] = call
    return latest


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@functools.lru_cache(maxsize=1024)
def git_blob(commit: str, path: str) -> bytes | None:
    """File contents at a commit, or None when the commit or path is missing."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def artifact_bytes(artifact: dict[str, Any] | None) -> bytes | None:
    if not artifact:
        return None
    if artifact.get("commit"):
        return git_blob(artifact["commit"], artifact["path"])
    path = ROOT / artifact["path"]
    return path.read_bytes() if path.exists() else None


def weighted_value(scenarios: dict[str, Any]) -> float | None:
    """Probability-weighted value when every scenario has a value and a weight."""
    cases = [scenarios.get(name) for name in ("bear", "base", "bull")]
    if not all(c and c.get("value") is not None and c.get("weight") is not None for c in cases):
        return None
    return sum(c["value"] * c["weight"] for c in cases)  # type: ignore[index]


def fair_value(call: dict[str, Any]) -> float | None:
    fv = call.get("fair_value")
    if fv:
        return fv["value"]
    base = (call.get("scenarios") or {}).get("base") or {}
    return base.get("value")


COVERAGE = DATA / "coverage.csv"
COVERAGE_FIELDS = ["ticker", "status", "since", "entry_price", "reason"]
COVERAGE_STATUSES = ("active", "watchlist", "dropped")


def coverage() -> dict[str, dict[str, str]]:
    """Pipeline state per ticker. active: updated after each release; watchlist: waiting for
    entry_price; dropped: no further updates, with a reason. Hand-edited."""
    import csv

    path = DATA / "coverage.csv"
    if not path.exists():
        return {}
    with path.open(newline="") as fh:
        return {r["ticker"]: r for r in csv.DictReader(fh)}


def add_coverage(ticker: str, since: str) -> None:
    import csv

    rows = coverage()
    if ticker in rows:
        return
    rows[ticker] = {"ticker": ticker, "status": "active", "since": since, "entry_price": "", "reason": ""}
    with (DATA / "coverage.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COVERAGE_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows[k] for k in sorted(rows))
