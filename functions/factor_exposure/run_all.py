#!/usr/bin/env python3
"""Run factor_exposure across every repo ticker."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from functions.common.tickers import discover_tickers
from functions.factor_exposure.main import run


def _format_cell(value: Any, width: int) -> str:
    text = "" if value is None else str(value)
    if len(text) > width:
        text = text[: width - 1] + "..."
    return text.ljust(width)


def _print_summary(results: list[dict[str, Any]], failures: list[dict[str, str]]) -> None:
    columns = [
        ("ticker", 6),
        ("level", 10),
        ("entry_bias", 38),
        ("score", 7),
        ("12-1m%", 8),
        ("vs200%", 8),
        ("factor_mom_beta", 15),
        ("price_date", 10),
    ]
    print(" ".join(_format_cell(name, width) for name, width in columns))
    print(" ".join("-" * width for _, width in columns))
    for result in results:
        timing = result["momentum_timing"]
        metrics = timing["metrics"]
        factor_momentum = result["factor_regression"]["loadings"]["momentum"]["beta"]
        row = {
            "ticker": result["ticker"],
            "level": timing["level"],
            "entry_bias": timing["entry_bias"],
            "score": timing["score"],
            "12-1m%": metrics["return_12m_ex_last_1m_pct"],
            "vs200%": metrics["price_vs_200dma_pct"],
            "factor_mom_beta": factor_momentum,
            "price_date": result["analysis_as_of"]["latest_price_date"],
        }
        print(" ".join(_format_cell(row[name], width) for name, width in columns))

    if failures:
        print()
        print("Skipped:")
        for failure in failures:
            print(f"- {failure['ticker']}: {failure['error']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run factor_exposure for every repo ticker")
    parser.add_argument("--lookback-months", type=int, default=36)
    parser.add_argument("--price-source", default="nasdaq")
    parser.add_argument("--output", help="Optional path for full JSON results")
    parser.add_argument("--full", action="store_true", help="Print full JSON output")
    parser.add_argument("--progress", action="store_true", help="Print per-ticker progress")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any ticker cannot be analyzed",
    )
    args = parser.parse_args()

    tickers = discover_tickers(ROOT)
    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for idx, ticker in enumerate(tickers, start=1):
        if args.progress:
            print(f"[{idx}/{len(tickers)}] {ticker}", file=sys.stderr, flush=True)
        try:
            result = run(
                {
                    "ticker": ticker,
                    "lookback_months": args.lookback_months,
                    "price_source": args.price_source,
                }
            )
            results.append(result)
        except Exception as exc:
            failures.append({"ticker": ticker, "error": str(exc)})

    if args.full:
        print(json.dumps({"results": results, "failures": failures}, indent=2, sort_keys=True))
    else:
        _print_summary(results, failures)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps({"results": results, "failures": failures}, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return 1 if failures and args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
