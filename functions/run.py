#!/usr/bin/env python3
"""Run repo-local functions from the command line."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if args.input_json:
        payload.update(json.loads(args.input_json))
    if args.ticker:
        payload["ticker"] = args.ticker
    if args.lookback_months is not None:
        payload["lookback_months"] = args.lookback_months
    if args.as_of:
        payload["as_of"] = args.as_of
    if args.price_source:
        payload["price_source"] = args.price_source
    return payload


def _print_human_result(result: dict[str, Any]) -> None:
    if result.get("function") != "factor_exposure":
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    ticker = result["ticker"]
    timing = result["momentum_timing"]
    metrics = timing["metrics"]
    factor_momentum = result["factor_regression"]["loadings"]["momentum"]["beta"]
    print(f"{ticker} | Momentum score: {timing['score']} / 100 ({_human_level(timing['level'])})")
    print(f"Entry read: {_human_bias(timing['entry_bias'])}")
    print(timing["summary"])
    print(
        "Metrics: "
        f"12-1m return {metrics['return_12m_ex_last_1m_pct']}%, "
        f"vs 200dma {metrics['price_vs_200dma_pct']}%, "
        f"factor momentum beta {factor_momentum}"
    )
    _print_score_formula(timing)
    _print_momentum_chart(timing)
    print(f"As of: {result['analysis_as_of']['latest_price_date']}")
    warnings = _visible_warnings(result.get("warnings") or [])
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


def _human_level(level: str) -> str:
    return level.replace("_", " ")


def _human_bias(entry_bias: str) -> str:
    labels = {
        "avoid_chasing": "avoid chasing; wait for a pullback or size smaller",
        "be_cautious": "be cautious; chart strength can hide valuation risk",
        "neutral": "neutral; momentum is not driving entry timing",
        "constructive_entry_setup": "constructive staged-entry setup if the thesis holds",
        "contrarian_entry_check_falling_knife": (
            "contrarian setup, but check falling-knife risk first"
        ),
    }
    return labels.get(entry_bias, entry_bias.replace("_", " "))


def _visible_warnings(warnings: list[str]) -> list[str]:
    hidden_prefixes = (
        "Factor regression only runs through the latest available French factor month",
    )
    return [
        warning
        for warning in warnings
        if not any(warning.startswith(prefix) for prefix in hidden_prefixes)
    ]


def _print_score_formula(timing: dict[str, Any]) -> None:
    formula = timing.get("score_formula") or {}
    components = formula.get("components") or []
    if not components:
        return
    print()
    print("Score formula:")
    print("  score = sum(weight * component_score)")
    print("  component_score is clamped to [-100,+100]")
    for component in components:
        raw = component.get("raw_value")
        unit = component.get("unit") or ""
        raw_text = f"{raw}%" if unit == "%" else f"{raw} {unit}" if unit else str(raw)
        print(
            f"  {component['effective_weight_pct']:>4.1f}% "
            f"{component['label']:<22} "
            f"{raw_text:>8} -> "
            f"{component['component_score']:>6.1f} "
            f"=> {component['score_contribution']:>6.1f}"
        )


def _print_momentum_chart(timing: dict[str, Any]) -> None:
    history = timing.get("history") or {}
    points = history.get("points") or []
    current = history.get("current") or {}
    chart_points = [
        {"label": row["month"], "return_pct": row["return_pct"]}
        for row in points[-12:]
        if row.get("return_pct") is not None
    ]
    if current.get("return_pct") is not None:
        chart_points.append({"label": "now", "return_pct": current["return_pct"]})
    if not chart_points:
        return

    values = [float(row["return_pct"]) for row in chart_points]
    lower = math.floor(min(min(values), 0.0) / 10.0) * 10.0
    upper = math.ceil(max(max(values), 0.0) / 10.0) * 10.0
    if upper - lower < 40.0:
        midpoint = (upper + lower) / 2.0
        lower = math.floor((midpoint - 20.0) / 10.0) * 10.0
        upper = math.ceil((midpoint + 20.0) / 10.0) * 10.0
    print()
    print("Momentum history: 12m return excluding most recent month")
    for line in _ascii_line_chart(chart_points, lower=lower, upper=upper):
        print(line)


def _ascii_line_chart(
    points: list[dict[str, Any]],
    *,
    lower: float,
    upper: float,
    height: int = 11,
    spacing: int = 5,
) -> list[str]:
    width = (len(points) - 1) * spacing + 1
    grid = [[" " for _ in range(width)] for _ in range(height)]

    def row_for(value: float) -> int:
        if upper == lower:
            return height // 2
        ratio = (upper - value) / (upper - lower)
        return max(0, min(height - 1, int(round(ratio * (height - 1)))))

    zero_row = row_for(0.0)
    if lower <= 0.0 <= upper:
        for col in range(width):
            grid[zero_row][col] = "-"

    coords: list[tuple[int, int, float, str]] = []
    for idx, point in enumerate(points):
        col = idx * spacing
        value = float(point["return_pct"])
        row = row_for(value)
        label = str(point["label"])
        coords.append((row, col, value, label))

    for row, col, _, label in coords:
        grid[row][col] = "X" if label == "now" else "o"

    lines: list[str] = []
    for row, cells in enumerate(grid):
        value = upper - (upper - lower) * row / (height - 1)
        label = f"{value:>5.0f}%"
        axis = "+" if row == zero_row else "|"
        lines.append(f"{label} {axis} {''.join(cells)}")

    lines.append(f"      + {'-' * width}")
    lines.append(f"        {_chart_x_labels(points, width, spacing)}")
    lines.append("        y-axis is raw 12-1m return; score above is normalized composite")
    lines.append("        o historical month-end   X current")
    return lines


def _chart_x_labels(points: list[dict[str, Any]], width: int, spacing: int) -> str:
    chars = [" " for _ in range(width)]
    for idx, point in enumerate(points):
        label = _short_label(str(point["label"]))
        start = max(0, idx * spacing - len(label) // 2)
        if start + len(label) > width:
            start = width - len(label)
        for offset, char in enumerate(label):
            chars[start + offset] = char
    return "".join(chars)


def _short_label(label: str) -> str:
    if label == "now":
        return "now"
    try:
        return datetime.strptime(label, "%Y%m").strftime("%b")
    except ValueError:
        return label[-3:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a repo-local function")
    parser.add_argument("function", help="Function directory name, e.g. factor_exposure")
    parser.add_argument("--input-json", help="JSON object to pass as function input")
    parser.add_argument("--ticker", help="Ticker symbol")
    parser.add_argument("--lookback-months", type=int, help="Regression lookback in months")
    parser.add_argument("--as-of", help="Use data up to YYYY-MM-DD")
    parser.add_argument(
        "--price-source",
        default=None,
        help="Price adapter. Supported by factor_exposure: nasdaq, yahoo, auto",
    )
    parser.add_argument("--full", action="store_true", help="Print full JSON output")
    args = parser.parse_args()

    module = importlib.import_module(f"functions.{args.function}.main")
    result = module.run(_load_payload(args))
    if args.full:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
