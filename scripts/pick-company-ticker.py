#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "automation" / "state"
SEEN_PATH = STATE_DIR / "seen_tickers.json"
CACHE_PATH = STATE_DIR / "candidate_queue.json"

NASDAQ_SCREENER_URL = "https://api.nasdaq.com/api/screener/stocks?download=true"
SEC_TICKERS_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
YAHOO_SCREENER_URL = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"

MIN_MARKET_CAP = 1_000_000_000
MIN_AVG_DOLLAR_VOLUME = 10_000_000
ALLOWED_YAHOO_EXCHANGES = {"NMS", "NGM", "NCM", "NYQ", "ASE", "BTS", "PCX"}
ALLOWED_SEC_EXCHANGES = {
    "Nasdaq",
    "NYSE",
    "NYSE American",
    "NYSE Arca",
    "CboeBZX",
    "Cboe BYX",
    "Cboe EDGX",
    "Cboe",
}

BUCKETS = {
    "recent_52_week_lows": {"weight": 40, "scr_id": "recent_52_week_lows"},
    "recent_52_week_highs": {"weight": 40, "scr_id": "recent_52_week_highs"},
    "most_actives": {"weight": 10, "scr_id": "most_actives"},
    "random": {"weight": 10, "scr_id": None},
}

RNG = random.SystemRandom()

COMMON_STOCK_SUFFIXES = {
    "INC",
    "INCORPORATED",
    "CORP",
    "CORPORATION",
    "CO",
    "COMPANY",
    "HOLDINGS",
    "HOLDING",
    "GROUP",
    "PLC",
    "PLCS",
    "LTD",
    "LIMITED",
    "NV",
    "N V",
    "S A",
    "SA",
    "SE",
    "AG",
    "LP",
    "LLC",
    "THE",
}

REJECTION_KEYWORDS = (
    "ETF",
    "FUND",
    "TRUST",
    "ETN",
    "ETMF",
    "MUTUAL FUND",
    "INDEX FUND",
    "CLOSED END FUND",
    "EXCHANGE TRADED FUND",
    "PREFERRED",
    "PREFERENCE",
    "PFD",
    "DEPOSITARY SHARES",
    "DEPOSITORY SHARES",
    "WARRANT",
    "WARRANTS",
    "RIGHT",
    "RIGHTS",
    "UNIT",
    "UNITS",
    "ACQUISITION",
    "BLANK CHECK",
    "SHELL COMPANY",
    "ROYALTY TRUST",
    "BENEFICIAL INTEREST",
    "INCOME SHARES",
    "NEXTSHARES",
    "SPDR",
    "ISHARES",
    "PROSHARES",
    "DIREXION",
    "XTRACKERS",
    "INVESCO QQQ",
)

ALLOWED_ADR_PHRASES = (
    "AMERICAN DEPOSITARY SHARE",
    "AMERICAN DEPOSITARY SHARES",
    "ADR",
    "ADS",
)


@dataclass
class Candidate:
    ticker: str
    name: str


@dataclass
class BucketResult:
    bucket: str
    candidates: list[Candidate]
    rejected: list[str]


class SelectionError(RuntimeError):
    pass


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SelectionError(f"invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, data: Any) -> None:
    ensure_state_dir()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp_path.replace(path)


def load_seen_tickers() -> set[str]:
    state = load_json(SEEN_PATH, {"seen_tickers": []})
    if not isinstance(state, dict):
        raise SelectionError(f"unexpected seen-ticker state in {SEEN_PATH}")
    tickers = state.get("seen_tickers", [])
    if not isinstance(tickers, list):
        raise SelectionError(f"unexpected seen-ticker list in {SEEN_PATH}")
    return {str(ticker).upper() for ticker in tickers}


def save_seen_tickers(seen_tickers: Iterable[str]) -> None:
    write_json(SEEN_PATH, {"seen_tickers": sorted({ticker.upper() for ticker in seen_tickers})})


def normalize_text(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()


def company_aliases(name: str) -> set[str]:
    tokens = normalize_text(name).split()
    aliases: set[str] = set()
    if not tokens:
        return aliases

    aliases.add(" ".join(tokens))
    trimmed = list(tokens)
    while trimmed and trimmed[-1] in COMMON_STOCK_SUFFIXES:
        trimmed.pop()
    if trimmed:
        aliases.add(" ".join(trimmed))
    if len(trimmed) > 1 and trimmed[-1] in {"HOLDING", "HOLDINGS", "GROUP"}:
        aliases.add(" ".join(trimmed[:-1]))
    return {alias for alias in aliases if len(alias.replace(" ", "")) >= 4}


def parse_money_string(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        raw = value.get("raw")
        return float(raw) if raw is not None else None
    text = str(value).strip()
    if not text or text in {"n/a", "N/A", "--"}:
        return None
    text = text.replace("$", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def parse_int_like(value: Any) -> int | None:
    parsed = parse_money_string(value)
    if parsed is None:
        return None
    return int(parsed)


def fetch_json(url: str, headers: dict[str, str], timeout: int = 30) -> Any:
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        payload = response.read()
        if response.headers.get("Content-Encoding") == "gzip" or payload[:2] == b"\x1f\x8b":
            payload = gzip.decompress(payload)
    return json.loads(payload)


def fetch_yahoo_screener(scr_id: str) -> list[dict[str, Any]]:
    url = f"{YAHOO_SCREENER_URL}?formatted=true&scrIds={scr_id}&count=100&start=0"
    data = fetch_json(url, headers={"User-Agent": "Mozilla/5.0 capital-picker/1.0"})
    return data["finance"]["result"][0].get("quotes", [])


def fetch_nasdaq_screener() -> list[dict[str, Any]]:
    data = fetch_json(
        NASDAQ_SCREENER_URL,
        headers={
            "User-Agent": "Mozilla/5.0 capital-picker/1.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    return data["data"].get("rows", [])


def fetch_sec_exchange_mapping() -> dict[str, dict[str, str]]:
    data = fetch_json(
        SEC_TICKERS_EXCHANGE_URL,
        headers={
            "User-Agent": "Andreas Bigger capital research automation contact@example.com",
            "Accept": "application/json,text/plain,*/*",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        },
    )
    fields = data.get("fields", [])
    rows = data.get("data", [])
    index = {field: idx for idx, field in enumerate(fields)}
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        ticker = str(row[index["ticker"]]).upper()
        mapping[ticker] = {
            "name": str(row[index["name"]]),
            "exchange": str(row[index["exchange"]]),
        }
    return mapping


def existing_represented_tickers(sec_mapping: dict[str, dict[str, str]]) -> set[str]:
    represented: set[str] = set()

    for directory in (ROOT / "research", ROOT / "projections"):
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            stem = path.stem.upper()
            if stem in {"README", "TEMPLATE"}:
                continue
            represented.add(stem)

    workbook_paths = list((ROOT / "models").glob("*.xlsx"))
    workbook_texts = [(path, normalize_text(path.stem), set(normalize_text(path.stem).split())) for path in workbook_paths]
    for ticker, info in sec_mapping.items():
        aliases = company_aliases(info["name"])
        for _, workbook_text, workbook_tokens in workbook_texts:
            if ticker in workbook_tokens:
                represented.add(ticker)
                break
            if any(alias in workbook_text for alias in aliases):
                represented.add(ticker)
                break
    return represented


def is_allowed_symbol(ticker: str) -> bool:
    if re.fullmatch(r"[A-Z]{1,5}", ticker):
        return not (len(ticker) == 5 and ticker[-1] in {"W", "R", "U", "Z", "Q"})
    return False


def rejection_reason_for_name(name: str) -> str | None:
    normalized = normalize_text(name)
    words = set(normalized.split())
    if any(phrase in normalized for phrase in ALLOWED_ADR_PHRASES):
        adr_allowed = True
    else:
        adr_allowed = False

    for keyword in REJECTION_KEYWORDS:
        keyword_words = keyword.split()
        if len(keyword_words) == 1:
            if keyword not in words:
                continue
        else:
            if keyword not in normalized:
                continue
        if keyword in {"DEPOSITARY SHARES", "DEPOSITORY SHARES"} and adr_allowed:
            continue
        if keyword == "UNIT" and "REVENUE UNIT" in normalized:
            continue
        return "non-common security"
    return None


def passes_yahoo_filters(quote: dict[str, Any], sec_mapping: dict[str, dict[str, str]], represented: set[str], seen: set[str]) -> str | None:
    ticker = str(quote.get("symbol", "")).upper()
    if not ticker:
        return "missing ticker"
    if ticker in represented:
        return "already represented"
    if ticker in seen:
        return "already seen"
    if not is_allowed_symbol(ticker):
        return "unsupported symbol shape"

    name = str(quote.get("longName") or quote.get("shortName") or quote.get("displayName") or "")
    if not name:
        return "missing company name"
    keyword_rejection = rejection_reason_for_name(name)
    if keyword_rejection:
        return keyword_rejection

    if quote.get("quoteType") != "EQUITY":
        return "non-equity quote type"
    if quote.get("exchange") not in ALLOWED_YAHOO_EXCHANGES:
        return "unsupported exchange"

    sec_info = sec_mapping.get(ticker)
    if not sec_info:
        return "missing SEC mapping"
    if sec_info.get("exchange") not in ALLOWED_SEC_EXCHANGES:
        return "unsupported SEC exchange"

    sec_name_rejection = rejection_reason_for_name(sec_info.get("name", ""))
    if sec_name_rejection:
        return sec_name_rejection

    market_cap = parse_money_string(quote.get("marketCap"))
    if market_cap is not None and market_cap < MIN_MARKET_CAP:
        return "market cap below floor"

    average_volume = parse_int_like(quote.get("averageDailyVolume3Month"))
    price = parse_money_string(quote.get("regularMarketPrice"))
    if average_volume is not None and price is not None:
        if average_volume * price < MIN_AVG_DOLLAR_VOLUME:
            return "liquidity below floor"

    return None


def passes_random_filters(row: dict[str, Any], sec_mapping: dict[str, dict[str, str]], represented: set[str], seen: set[str]) -> str | None:
    ticker = str(row.get("symbol", "")).upper()
    if not ticker:
        return "missing ticker"
    if ticker in represented:
        return "already represented"
    if ticker in seen:
        return "already seen"
    if not is_allowed_symbol(ticker):
        return "unsupported symbol shape"

    sec_info = sec_mapping.get(ticker)
    if not sec_info:
        return "missing SEC mapping"
    if sec_info.get("exchange") not in ALLOWED_SEC_EXCHANGES:
        return "unsupported SEC exchange"

    name = str(row.get("name") or sec_info.get("name") or "")
    keyword_rejection = rejection_reason_for_name(name)
    if keyword_rejection:
        return keyword_rejection

    market_cap = parse_money_string(row.get("marketCap"))
    if market_cap is not None and market_cap < MIN_MARKET_CAP:
        return "market cap below floor"

    price = parse_money_string(row.get("lastsale"))
    volume = parse_int_like(row.get("volume"))
    if price is not None and volume is not None and price * volume < MIN_AVG_DOLLAR_VOLUME:
        return "liquidity below floor"

    ipo_year = parse_int_like(row.get("ipoyear"))
    current_year = datetime.now(timezone.utc).year
    if ipo_year is not None and ipo_year >= current_year - 1:
        return "too little operating history"

    return None


def build_bucket_results(sec_mapping: dict[str, dict[str, str]], seen: set[str]) -> dict[str, BucketResult]:
    represented = existing_represented_tickers(sec_mapping)
    results: dict[str, BucketResult] = {}

    lows_rejected: list[str] = []
    lows_candidates: list[Candidate] = []
    for quote in fetch_yahoo_screener("recent_52_week_lows"):
        ticker = str(quote.get("symbol", "")).upper()
        reason = passes_yahoo_filters(quote, sec_mapping, represented, seen)
        if reason:
            lows_rejected.append(f"{ticker}:{reason}")
            continue
        name = str(quote.get("longName") or quote.get("shortName") or quote.get("displayName") or ticker)
        lows_candidates.append(Candidate(ticker=ticker, name=name))
    results["recent_52_week_lows"] = BucketResult(
        bucket="recent_52_week_lows",
        candidates=dedupe_candidates(lows_candidates),
        rejected=lows_rejected,
    )

    highs_rejected: list[str] = []
    highs_candidates: list[Candidate] = []
    for quote in fetch_yahoo_screener("recent_52_week_highs"):
        ticker = str(quote.get("symbol", "")).upper()
        reason = passes_yahoo_filters(quote, sec_mapping, represented, seen)
        if reason:
            highs_rejected.append(f"{ticker}:{reason}")
            continue
        name = str(quote.get("longName") or quote.get("shortName") or quote.get("displayName") or ticker)
        highs_candidates.append(Candidate(ticker=ticker, name=name))
    results["recent_52_week_highs"] = BucketResult(
        bucket="recent_52_week_highs",
        candidates=dedupe_candidates(highs_candidates),
        rejected=highs_rejected,
    )

    actives_rejected: list[str] = []
    actives_candidates: list[Candidate] = []
    for quote in fetch_yahoo_screener("most_actives"):
        ticker = str(quote.get("symbol", "")).upper()
        reason = passes_yahoo_filters(quote, sec_mapping, represented, seen)
        if reason:
            actives_rejected.append(f"{ticker}:{reason}")
            continue
        regular_volume = parse_int_like(quote.get("regularMarketVolume")) or 0
        average_volume = parse_int_like(quote.get("averageDailyVolume3Month")) or 0
        if average_volume and regular_volume / average_volume < 1.2:
            actives_rejected.append(f"{ticker}:not unusual enough")
            continue
        name = str(quote.get("longName") or quote.get("shortName") or quote.get("displayName") or ticker)
        actives_candidates.append(Candidate(ticker=ticker, name=name))
    results["most_actives"] = BucketResult(
        bucket="most_actives",
        candidates=dedupe_candidates(actives_candidates),
        rejected=actives_rejected,
    )

    random_rejected: list[str] = []
    random_candidates: list[Candidate] = []
    for row in fetch_nasdaq_screener():
        ticker = str(row.get("symbol", "")).upper()
        reason = passes_random_filters(row, sec_mapping, represented, seen)
        if reason:
            random_rejected.append(f"{ticker}:{reason}")
            continue
        name = str(row.get("name") or ticker)
        random_candidates.append(Candidate(ticker=ticker, name=name))
    results["random"] = BucketResult(
        bucket="random",
        candidates=dedupe_candidates(random_candidates),
        rejected=random_rejected,
    )

    return results


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    seen_tickers: set[str] = set()
    deduped: list[Candidate] = []
    for candidate in candidates:
        if candidate.ticker in seen_tickers:
            continue
        seen_tickers.add(candidate.ticker)
        deduped.append(candidate)
    return deduped


def save_cache(results: dict[str, BucketResult]) -> None:
    cache_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "buckets": {
            bucket: [candidate.__dict__ for candidate in result.candidates]
            for bucket, result in results.items()
        },
    }
    write_json(CACHE_PATH, cache_payload)


def save_cache_without_touching_git(results: dict[str, BucketResult]) -> None:
    cache_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "buckets": {
            bucket: [candidate.__dict__ for candidate in result.candidates]
            for bucket, result in results.items()
        },
    }
    ensure_state_dir()
    CACHE_PATH.write_text(json.dumps(cache_payload, indent=2, sort_keys=True) + "\n")


def load_cache_results(sec_mapping: dict[str, dict[str, str]], seen: set[str]) -> dict[str, BucketResult]:
    cache = load_json(CACHE_PATH, {})
    if not isinstance(cache, dict) or not isinstance(cache.get("buckets"), dict):
        raise SelectionError(f"invalid cached candidate queue in {CACHE_PATH}")
    represented = existing_represented_tickers(sec_mapping)
    results: dict[str, BucketResult] = {}
    for bucket in BUCKETS:
        raw_candidates = cache["buckets"].get(bucket, [])
        candidates: list[Candidate] = []
        rejected: list[str] = []
        for item in raw_candidates:
            ticker = str(item.get("ticker", "")).upper()
            name = str(item.get("name", ticker))
            if not ticker:
                continue
            if ticker in represented:
                rejected.append(f"{ticker}:already represented")
                continue
            if ticker in seen:
                rejected.append(f"{ticker}:already seen")
                continue
            if not is_allowed_symbol(ticker):
                rejected.append(f"{ticker}:unsupported symbol shape")
                continue
            if rejection_reason_for_name(name):
                rejected.append(f"{ticker}:non-common security")
                continue
            if bucket == "random" and ticker not in sec_mapping:
                rejected.append(f"{ticker}:missing SEC mapping")
                continue
            candidates.append(Candidate(ticker=ticker, name=name))
        results[bucket] = BucketResult(bucket=bucket, candidates=dedupe_candidates(candidates), rejected=rejected)
    return results


def choose_bucket(results: dict[str, BucketResult]) -> BucketResult:
    available = [result for result in results.values() if result.candidates]
    if not available:
        raise SelectionError("no eligible ticker candidates available")
    weights = [BUCKETS[result.bucket]["weight"] for result in available]
    return RNG.choices(available, weights=weights, k=1)[0]


def choose_from_results(results: dict[str, BucketResult]) -> tuple[BucketResult, Candidate]:
    bucket_result = choose_bucket(results)
    candidate = RNG.choice(bucket_result.candidates)
    return bucket_result, candidate


def print_dry_run(bucket_result: BucketResult, candidate: Candidate, source: str) -> None:
    print(f"source={source}")
    print(f"selected_bucket={bucket_result.bucket}")
    print(f"candidate_count={len(bucket_result.candidates)}")
    rejected = ", ".join(bucket_result.rejected[:100])
    if len(bucket_result.rejected) > 100:
        rejected += f", ... ({len(bucket_result.rejected)} total)"
    print(f"rejected_tickers={rejected or '(none)'}")
    print(f"final_ticker={candidate.ticker}")


def mark_seen(ticker: str) -> int:
    normalized = ticker.upper().strip()
    if not normalized:
        raise SelectionError("--mark-seen requires a non-empty ticker")
    if not is_allowed_symbol(normalized):
        raise SelectionError(f"invalid ticker for --mark-seen: {ticker}")
    seen = load_seen_tickers()
    seen.add(normalized)
    save_seen_tickers(seen)
    return 0


def select_ticker(dry_run: bool) -> int:
    ensure_state_dir()
    if not SEEN_PATH.exists():
        save_seen_tickers(load_seen_tickers())

    seen = load_seen_tickers()
    sec_mapping = fetch_sec_exchange_mapping()

    live_error: Exception | None = None
    live_results: dict[str, BucketResult] | None = None
    try:
        live_results = build_bucket_results(sec_mapping, seen)
        if dry_run:
            save_cache(live_results)
        else:
            save_cache_without_touching_git(live_results)
    except (HTTPError, URLError, TimeoutError, KeyError, json.JSONDecodeError, SelectionError) as exc:
        live_error = exc

    if live_results:
        try:
            bucket_result, candidate = choose_from_results(live_results)
            if dry_run:
                print_dry_run(bucket_result, candidate, source="live")
            else:
                print(candidate.ticker)
            return 0
        except SelectionError as exc:
            live_error = live_error or exc

    try:
        cached_results = load_cache_results(sec_mapping, seen)
        bucket_result, candidate = choose_from_results(cached_results)
        if dry_run:
            print_dry_run(bucket_result, candidate, source="cache")
        else:
            print(candidate.ticker)
        return 0
    except Exception as cache_exc:
        live_message = f"live selection failed: {live_error}" if live_error else "live selection failed"
        raise SelectionError(f"{live_message}; cache fallback failed: {cache_exc}") from cache_exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pick one eligible company ticker for daily capital research.")
    parser.add_argument("--dry-run", action="store_true", help="show selection diagnostics instead of printing only the final ticker")
    parser.add_argument("--mark-seen", metavar="TICKER", help="record a ticker as used after a successful full run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run and args.mark_seen:
        raise SelectionError("--dry-run and --mark-seen cannot be used together")
    if args.mark_seen:
        return mark_seen(args.mark_seen)
    return select_ticker(dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SelectionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
