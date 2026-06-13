#!/usr/bin/env python3
"""Discover ticker symbols represented by repo markdown files."""

from __future__ import annotations

from pathlib import Path


EXCLUDED_STEMS = {"README", "TEMPLATE"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def discover_tickers(root: Path | None = None) -> list[str]:
    base = root or repo_root()
    tickers: set[str] = set()
    for directory in ("research", "projections"):
        path = base / directory
        if not path.exists():
            continue
        for item in path.glob("*.md"):
            stem = item.stem.strip().upper()
            if stem and stem not in EXCLUDED_STEMS:
                tickers.add(stem)
    return sorted(tickers)


def main() -> int:
    for ticker in discover_tickers():
        print(ticker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

