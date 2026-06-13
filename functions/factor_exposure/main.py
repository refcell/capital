from __future__ import annotations

import csv
import io
import json
import math
import zipfile
from datetime import date, datetime, timezone
from functools import lru_cache
from typing import Any
from urllib.parse import quote

from functions.common.http import fetch_bytes
from functions.common.stats import clamp, mean, ols, percentile_rank


FIVE_FACTOR_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_5_Factors_2x3_CSV.zip"
)
MOMENTUM_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Momentum_Factor_CSV.zip"
)
YAHOO_CHART_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/"
    "{symbol}?range=10y&interval=1d&events=history&includeAdjustedClose=true"
)
NASDAQ_HISTORICAL_URL = (
    "https://api.nasdaq.com/api/quote/{symbol}/historical"
    "?assetclass=stocks&fromdate={from_date}&todate={to_date}&limit=9999"
)

FACTOR_NAMES = [
    "market",
    "size",
    "value",
    "profitability",
    "investment",
    "momentum",
]


def run(input: dict[str, Any]) -> dict[str, Any]:
    ticker = str(input.get("ticker", "")).strip().upper()
    if not ticker:
        raise ValueError("factor_exposure requires input['ticker']")

    lookback_months = int(input.get("lookback_months") or 36)
    if lookback_months < 18:
        raise ValueError("lookback_months must be at least 18")

    price_source = str(input.get("price_source") or "nasdaq").lower()
    if price_source not in {"nasdaq", "yahoo", "auto"}:
        raise ValueError("supported price sources: nasdaq, yahoo, auto")

    as_of = _parse_optional_date(input.get("as_of"))
    prices, price_meta = _fetch_prices(ticker, source=price_source, as_of=as_of)
    if len(prices) < 260:
        raise ValueError(f"not enough price history for {ticker}: {len(prices)} daily points")

    factors, factor_meta = _fetch_factors()
    monthly_returns, monthly_closes = _monthly_returns(prices)
    regression = _factor_regression(monthly_returns, factors, lookback_months)
    timing = _momentum_timing(prices, monthly_closes)
    weighting = _factor_weighting(regression["loadings"])

    warnings: list[str] = []
    if regression["observations"] < lookback_months:
        warnings.append(
            "Regression used fewer observations than requested because factor "
            "or price history was unavailable for part of the window."
        )
    if regression["observations"] < 24:
        warnings.append(
            "Factor regression has fewer than 24 monthly observations; treat "
            "the loadings as directional only."
        )
    if timing["metrics"]["momentum_percentile_sample_months"] < 24:
        warnings.append(
            "Momentum percentile has fewer than 24 historical samples and was "
            "excluded from the timing score."
        )
    if factor_meta["latest_factor_month"] < monthly_returns[-1]["month"]:
        warnings.append(
            "Factor regression only runs through the latest available French "
            "factor month; momentum timing uses the latest available price."
        )

    return {
        "schema_version": 1,
        "function": "factor_exposure",
        "ticker": ticker,
        "analysis_as_of": {
            "latest_price_date": prices[-1]["date"].isoformat(),
            "latest_price": _round(prices[-1]["close"], 4),
            "latest_factor_month": factor_meta["latest_factor_month"],
        },
        "momentum_timing": timing,
        "factor_regression": regression,
        "factor_weighting": weighting,
        "source_audit": [
            {
                "name": "Kenneth French Data Library - Fama/French 5 Factors 2x3",
                "url": FIVE_FACTOR_URL,
                "latest_month": factor_meta["latest_five_factor_month"],
                "last_modified": factor_meta["five_factor_last_modified"],
            },
            {
                "name": "Kenneth French Data Library - Momentum Factor",
                "url": MOMENTUM_URL,
                "latest_month": factor_meta["latest_momentum_month"],
                "last_modified": factor_meta["momentum_last_modified"],
            },
            {
                "name": price_meta["name"],
                "url": price_meta["url"],
                "symbol": price_meta["symbol"],
                "price_field": price_meta["price_field"],
                "latest_date": prices[-1]["date"].isoformat(),
            },
        ],
        "warnings": warnings,
    }


def _parse_optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _fetch_zip_text(url: str) -> tuple[str, dict[str, str]]:
    result = fetch_bytes(url)
    with zipfile.ZipFile(io.BytesIO(result.body)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not names:
            raise ValueError(f"zip file from {url} did not contain a CSV")
        text = archive.read(names[0]).decode("latin-1")
    return text, result.headers


@lru_cache(maxsize=1)
def _fetch_factors() -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    five_text, five_headers = _fetch_zip_text(FIVE_FACTOR_URL)
    momentum_text, momentum_headers = _fetch_zip_text(MOMENTUM_URL)

    five = _parse_five_factor_csv(five_text)
    momentum = _parse_momentum_csv(momentum_text)

    factors: dict[str, dict[str, float]] = {}
    for month, row in five.items():
        if month in momentum:
            merged = dict(row)
            merged["momentum"] = momentum[month]
            factors[month] = merged

    if not factors:
        raise ValueError("no overlapping French factor and momentum data")

    return factors, {
        "latest_factor_month": max(factors),
        "latest_five_factor_month": max(five),
        "latest_momentum_month": max(momentum),
        "five_factor_last_modified": five_headers.get("last-modified"),
        "momentum_last_modified": momentum_headers.get("last-modified"),
    }


def _parse_five_factor_csv(text: str) -> dict[str, dict[str, float]]:
    rows = csv.reader(io.StringIO(text))
    data: dict[str, dict[str, float]] = {}
    in_monthly_section = False
    for row in rows:
        if not row:
            continue
        first = row[0].strip()
        if not in_monthly_section:
            labels = [cell.strip().lower() for cell in row]
            if "mkt-rf" in labels and "smb" in labels and "hml" in labels:
                in_monthly_section = True
            continue
        if not first.isdigit() or len(first) != 6:
            if data:
                break
            continue
        if len(row) < 7:
            continue
        data[first] = {
            "market": float(row[1]),
            "size": float(row[2]),
            "value": float(row[3]),
            "profitability": float(row[4]),
            "investment": float(row[5]),
            "risk_free": float(row[6]),
        }
    if not data:
        raise ValueError("could not parse monthly Fama/French 5-factor data")
    return data


def _parse_momentum_csv(text: str) -> dict[str, float]:
    rows = csv.reader(io.StringIO(text))
    data: dict[str, float] = {}
    in_monthly_section = False
    for row in rows:
        if not row:
            continue
        first = row[0].strip()
        if not in_monthly_section:
            labels = [cell.strip().lower() for cell in row]
            if any(label in {"mom", "mom   "} or label.startswith("mom") for label in labels):
                in_monthly_section = True
            continue
        if not first.isdigit() or len(first) != 6:
            if data:
                break
            continue
        if len(row) < 2:
            continue
        data[first] = float(row[1])
    if not data:
        raise ValueError("could not parse monthly momentum factor data")
    return data


def _fetch_prices(
    ticker: str,
    *,
    source: str,
    as_of: date | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if source == "nasdaq":
        return _fetch_nasdaq_prices(ticker, as_of=as_of)
    if source == "yahoo":
        return _fetch_yahoo_prices(ticker, as_of=as_of)
    try:
        return _fetch_nasdaq_prices(ticker, as_of=as_of)
    except Exception:
        return _fetch_yahoo_prices(ticker, as_of=as_of)


def _fetch_nasdaq_prices(
    ticker: str,
    *,
    as_of: date | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    symbol = ticker.strip().upper()
    request_to_date = date.today()
    from_date = _years_ago(as_of or request_to_date, 10)
    url = NASDAQ_HISTORICAL_URL.format(
        symbol=quote(symbol, safe=".-^"),
        from_date=from_date.isoformat(),
        to_date=request_to_date.isoformat(),
    )
    result = fetch_bytes(
        url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/",
        },
    )
    payload = json.loads(result.body.decode("utf-8"))
    rows = (
        payload.get("data", {})
        .get("tradesTable", {})
        .get("rows")
        or []
    )

    prices: list[dict[str, Any]] = []
    for row in rows:
        observed = datetime.strptime(row["date"], "%m/%d/%Y").date()
        if as_of and observed > as_of:
            continue
        close = _parse_money(row["close"])
        if close is None:
            continue
        prices.append({"date": observed, "close": close})

    prices.sort(key=lambda row: row["date"])
    if not prices:
        raise ValueError(f"Nasdaq returned no usable price data for {symbol}")

    return prices, {
        "name": "Nasdaq historical quotes",
        "url": url,
        "symbol": symbol,
        "price_field": "close",
    }


def _fetch_yahoo_prices(
    ticker: str,
    *,
    as_of: date | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    symbol = _to_yahoo_symbol(ticker)
    url = YAHOO_CHART_URL.format(symbol=quote(symbol, safe=".-^"))
    result = fetch_bytes(url, headers={"Accept": "application/json"})
    payload = json.loads(result.body.decode("utf-8"))
    chart = payload.get("chart", {})
    errors = chart.get("error")
    if errors:
        raise ValueError(f"Yahoo Finance error for {symbol}: {errors}")
    results = chart.get("result") or []
    if not results:
        raise ValueError(f"Yahoo Finance returned no price data for {symbol}")

    item = results[0]
    timestamps = item.get("timestamp") or []
    indicators = item.get("indicators") or {}
    quote_rows = indicators.get("quote") or [{}]
    close = quote_rows[0].get("close") or []
    adj_rows = indicators.get("adjclose") or [{}]
    adjclose = adj_rows[0].get("adjclose") or []
    use_adjclose = len(adjclose) == len(timestamps)

    prices: list[dict[str, Any]] = []
    for idx, ts in enumerate(timestamps):
        raw_price = adjclose[idx] if use_adjclose else close[idx]
        if raw_price is None:
            continue
        observed = datetime.fromtimestamp(int(ts), tz=timezone.utc).date()
        if as_of and observed > as_of:
            continue
        prices.append({"date": observed, "close": float(raw_price)})

    prices.sort(key=lambda row: row["date"])
    if not prices:
        raise ValueError(f"Yahoo Finance returned no usable price data for {symbol}")

    return prices, {
        "name": "Yahoo Finance chart endpoint",
        "url": url,
        "symbol": symbol,
        "price_field": "adjclose" if use_adjclose else "close",
    }


def _to_yahoo_symbol(ticker: str) -> str:
    symbol = ticker.strip().upper()
    if "." in symbol:
        left, right = symbol.rsplit(".", 1)
        if len(right) == 1:
            return f"{left}-{right}"
    return symbol


def _years_ago(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, day=28)


def _parse_money(value: str) -> float | None:
    cleaned = str(value).strip().replace("$", "").replace(",", "")
    if cleaned in {"", "N/A", "nan"}:
        return None
    return float(cleaned)


def _monthly_returns(
    prices: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    month_end: dict[str, dict[str, Any]] = {}
    for row in prices:
        key = f"{row['date'].year:04d}{row['date'].month:02d}"
        month_end[key] = row

    months = sorted(month_end)
    closes = [
        {"month": month, "date": month_end[month]["date"], "close": month_end[month]["close"]}
        for month in months
    ]
    returns: list[dict[str, Any]] = []
    for idx in range(1, len(closes)):
        previous = closes[idx - 1]["close"]
        current = closes[idx]["close"]
        returns.append(
            {
                "month": closes[idx]["month"],
                "date": closes[idx]["date"],
                "return_pct": 100.0 * (current / previous - 1.0),
            }
        )
    return returns, closes


def _factor_regression(
    monthly_returns: list[dict[str, Any]],
    factors: dict[str, dict[str, float]],
    lookback_months: int,
) -> dict[str, Any]:
    aligned: list[dict[str, Any]] = []
    for row in monthly_returns:
        month = row["month"]
        if month not in factors:
            continue
        factor_row = factors[month]
        aligned.append(
            {
                "month": month,
                "stock_excess_return": row["return_pct"] - factor_row["risk_free"],
                "factors": factor_row,
            }
        )

    aligned = aligned[-lookback_months:]
    minimum = min(10, lookback_months)
    if len(aligned) < minimum:
        raise ValueError(
            f"not enough overlapping monthly observations: {len(aligned)} < {minimum}"
        )

    y = [row["stock_excess_return"] for row in aligned]
    x = [
        [
            1.0,
            row["factors"]["market"],
            row["factors"]["size"],
            row["factors"]["value"],
            row["factors"]["profitability"],
            row["factors"]["investment"],
            row["factors"]["momentum"],
        ]
        for row in aligned
    ]
    result = ols(y, x, ["alpha", *FACTOR_NAMES])
    coefficients = result["coefficients"]

    loadings = {
        factor: {
            "beta": _round(coefficients[factor]["beta"], 4),
            "t_stat": _round(coefficients[factor]["t_stat"], 2),
            "std_error": _round(coefficients[factor]["std_error"], 4),
        }
        for factor in FACTOR_NAMES
    }

    return {
        "model": "ticker excess monthly return ~ Fama/French 5 factors + momentum",
        "window": {
            "start_month": aligned[0]["month"],
            "end_month": aligned[-1]["month"],
            "requested_months": lookback_months,
        },
        "observations": result["observations"],
        "r_squared": _round(result["r_squared"], 4),
        "alpha_monthly_pct": _round(coefficients["alpha"]["beta"], 4),
        "alpha_t_stat": _round(coefficients["alpha"]["t_stat"], 2),
        "loadings": loadings,
    }


def _factor_weighting(loadings: dict[str, dict[str, float]]) -> dict[str, Any]:
    abs_sum = sum(abs(row["beta"]) for row in loadings.values())
    if abs_sum <= 0:
        weights = {factor: 0.0 for factor in loadings}
    else:
        weights = {
            factor: _round(100.0 * abs(row["beta"]) / abs_sum, 1)
            for factor, row in loadings.items()
        }
    signed = {
        factor: {
            "direction": "positive" if row["beta"] >= 0 else "negative",
            "beta": row["beta"],
            "absolute_beta_share_pct": weights[factor],
        }
        for factor, row in loadings.items()
    }
    return {
        "method": "absolute beta share across non-alpha factors; not a portfolio weight",
        "weights_pct": weights,
        "signed_exposures": signed,
    }


def _momentum_timing(
    prices: list[dict[str, Any]],
    monthly_closes: list[dict[str, Any]],
) -> dict[str, Any]:
    current = prices[-1]["close"]
    ret_1m = _trading_day_return(prices, end_offset=0, lookback=21)
    ret_3m = _trading_day_return(prices, end_offset=0, lookback=63)
    ret_6m = _trading_day_return(prices, end_offset=0, lookback=126)
    ret_12m = _trading_day_return(prices, end_offset=0, lookback=252)
    ret_12_1 = _trading_day_return(prices, end_offset=21, lookback=231)
    sma_50 = _sma(prices, 50)
    sma_200 = _sma(prices, 200)
    price_vs_50 = current / sma_50 - 1.0 if sma_50 else None
    price_vs_200 = current / sma_200 - 1.0 if sma_200 else None
    rsi_14 = _rsi(prices, 14)
    historical_12_1_series = _historical_monthly_12_1_series(monthly_closes)
    historical_12_1 = [row["return_pct"] / 100.0 for row in historical_12_1_series]
    historical_count = len(historical_12_1_series)
    percentile = (
        percentile_rank(historical_12_1, ret_12_1)
        if ret_12_1 is not None and historical_count >= 24
        else None
    )

    score_details = _momentum_score_details(
        percentile=percentile,
        ret_12_1=ret_12_1,
        ret_6m=ret_6m,
        ret_3m=ret_3m,
        price_vs_200=price_vs_200,
        rsi_14=rsi_14,
    )
    score = float(score_details["score"])
    level, entry_bias, note = _classify_momentum(score, percentile, ret_12_1, price_vs_200)

    return {
        "level": level,
        "entry_bias": entry_bias,
        "score": _round(score, 1),
        "score_scale": "-100 very low momentum, 0 neutral, +100 very high momentum",
        "score_formula": score_details,
        "summary": note,
        "metrics": {
            "return_1m_pct": _pct(ret_1m),
            "return_3m_pct": _pct(ret_3m),
            "return_6m_pct": _pct(ret_6m),
            "return_12m_pct": _pct(ret_12m),
            "return_12m_ex_last_1m_pct": _pct(ret_12_1),
            "momentum_percentile_vs_own_history": _round(percentile, 1),
            "momentum_percentile_sample_months": historical_count,
            "price_vs_50dma_pct": _pct(price_vs_50),
            "price_vs_200dma_pct": _pct(price_vs_200),
            "rsi_14": _round(rsi_14, 1),
        },
        "history": {
            "metric": "12-month return excluding most recent month",
            "unit": "percent",
            "points": historical_12_1_series,
            "current": {
                "label": "now",
                "return_pct": _pct(ret_12_1),
            },
        },
    }


def _trading_day_return(
    prices: list[dict[str, Any]],
    *,
    end_offset: int,
    lookback: int,
) -> float | None:
    end_idx = len(prices) - 1 - end_offset
    start_idx = end_idx - lookback
    if start_idx < 0 or end_idx <= start_idx:
        return None
    start = prices[start_idx]["close"]
    end = prices[end_idx]["close"]
    if start <= 0:
        return None
    return end / start - 1.0


def _sma(prices: list[dict[str, Any]], window: int) -> float | None:
    if len(prices) < window:
        return None
    return mean(row["close"] for row in prices[-window:])


def _rsi(prices: list[dict[str, Any]], window: int) -> float | None:
    if len(prices) <= window:
        return None
    changes = [
        prices[idx]["close"] - prices[idx - 1]["close"]
        for idx in range(len(prices) - window, len(prices))
    ]
    gains = [max(0.0, change) for change in changes]
    losses = [max(0.0, -change) for change in changes]
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def _historical_monthly_12_1_series(
    monthly_closes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for idx in range(12, len(monthly_closes)):
        start = monthly_closes[idx - 12]["close"]
        end = monthly_closes[idx - 1]["close"]
        if start > 0:
            values.append(
                {
                    "month": monthly_closes[idx]["month"],
                    "return_pct": _pct(end / start - 1.0),
                }
            )
    return values


def _momentum_score(
    *,
    percentile: float | None,
    ret_12_1: float | None,
    ret_6m: float | None,
    ret_3m: float | None,
    price_vs_200: float | None,
    rsi_14: float | None,
) -> float:
    return float(
        _momentum_score_details(
            percentile=percentile,
            ret_12_1=ret_12_1,
            ret_6m=ret_6m,
            ret_3m=ret_3m,
            price_vs_200=price_vs_200,
            rsi_14=rsi_14,
        )["score"]
    )


def _momentum_score_details(
    *,
    percentile: float | None,
    ret_12_1: float | None,
    ret_6m: float | None,
    ret_3m: float | None,
    price_vs_200: float | None,
    rsi_14: float | None,
) -> dict[str, Any]:
    components: list[dict[str, Any]] = []
    if percentile is not None:
        components.append(
            _score_component(
                "own_history_rank",
                "own-history percentile",
                0.35,
                percentile,
                "clamp((percentile - 50) / 50)",
                clamp((percentile - 50.0) / 50.0, -1.0, 1.0),
                "pctile",
            )
        )
    if ret_12_1 is not None:
        components.append(
            _score_component(
                "return_12m_ex_last_1m",
                "12-1m return",
                0.25,
                100.0 * ret_12_1,
                "clamp(return / 50%)",
                clamp(ret_12_1 / 0.50, -1.0, 1.0),
                "%",
            )
        )
    if ret_6m is not None:
        components.append(
            _score_component(
                "return_6m",
                "6m return",
                0.15,
                100.0 * ret_6m,
                "clamp(return / 35%)",
                clamp(ret_6m / 0.35, -1.0, 1.0),
                "%",
            )
        )
    if ret_3m is not None:
        components.append(
            _score_component(
                "return_3m",
                "3m return",
                0.10,
                100.0 * ret_3m,
                "clamp(return / 20%)",
                clamp(ret_3m / 0.20, -1.0, 1.0),
                "%",
            )
        )
    if price_vs_200 is not None:
        components.append(
            _score_component(
                "price_vs_200dma",
                "price vs 200dma",
                0.10,
                100.0 * price_vs_200,
                "clamp(distance / 25%)",
                clamp(price_vs_200 / 0.25, -1.0, 1.0),
                "%",
            )
        )
    if rsi_14 is not None:
        components.append(
            _score_component(
                "rsi_14",
                "RSI 14",
                0.05,
                rsi_14,
                "clamp((RSI - 50) / 30)",
                clamp((rsi_14 - 50.0) / 30.0, -1.0, 1.0),
                "",
            )
        )
    if not components:
        return {
            "formula": "score = 100 * weighted_average(clamped component values)",
            "note": "No momentum components were available.",
            "score": 0.0,
            "components": [],
        }
    total_weight = sum(float(item["base_weight"]) for item in components)
    for item in components:
        effective_weight = float(item["base_weight"]) / total_weight
        normalized_value = float(item["normalized_value"])
        item["effective_weight_pct"] = _round(100.0 * effective_weight, 1)
        item["component_score"] = _round(100.0 * normalized_value, 1)
        item["score_contribution"] = _round(100.0 * effective_weight * normalized_value, 1)
        item.pop("base_weight")
        item.pop("normalized_value")
    score = sum(float(item["score_contribution"]) for item in components)
    return {
        "formula": "score = sum(effective_weight * component_score); each component_score is clamped to [-100,+100]",
        "note": "If a component is unavailable, remaining weights are renormalized.",
        "score": _round(score, 1),
        "components": components,
    }


def _score_component(
    key: str,
    label: str,
    weight: float,
    raw_value: float,
    transform: str,
    normalized_value: float,
    unit: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "base_weight": weight,
        "raw_value": _round(raw_value, 1),
        "unit": unit,
        "transform": transform,
        "normalized_value": normalized_value,
    }


def _classify_momentum(
    score: float,
    percentile: float | None,
    ret_12_1: float | None,
    price_vs_200: float | None,
) -> tuple[str, str, str]:
    high_history = percentile is not None and percentile >= 85.0
    low_history = percentile is not None and percentile <= 15.0
    extended = price_vs_200 is not None and price_vs_200 >= 0.25
    depressed = price_vs_200 is not None and price_vs_200 <= -0.20
    strong_trailing = ret_12_1 is not None and ret_12_1 >= 0.50
    weak_trailing = ret_12_1 is not None and ret_12_1 <= -0.25

    if score >= 60.0 or (high_history and (extended or strong_trailing)):
        return (
            "very_high",
            "avoid_chasing",
            "Momentum is very high. For a new position, require a larger margin "
            "of safety, wait for a pullback, or use a smaller starter size.",
        )
    if score >= 30.0 or high_history:
        return (
            "high",
            "be_cautious",
            "Momentum is high. The main risk is paying up because the chart is "
            "working; staggered entry or a pullback trigger is preferable.",
        )
    if score <= -60.0 or (low_history and (depressed or weak_trailing)):
        return (
            "very_low",
            "contrarian_entry_check_falling_knife",
            "Momentum is very low. Entry may be more attractive, but check for "
            "business deterioration, estimate cuts, or balance-sheet stress.",
        )
    if score <= -30.0 or low_history:
        return (
            "low",
            "constructive_entry_setup",
            "Momentum is low. This can be a better staged-entry setup if the "
            "fundamental thesis and valuation still hold.",
        )
    return (
        "neutral",
        "neutral",
        "Momentum is not extreme enough to drive entry timing by itself.",
    )


def _round(value: float | None, digits: int) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return round(float(value), digits)


def _pct(value: float | None) -> float | None:
    return _round(None if value is None else 100.0 * value, 1)


if __name__ == "__main__":
    print(json.dumps(run({"ticker": "CRM"}), indent=2, sort_keys=True))
