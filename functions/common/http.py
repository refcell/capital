"""Small HTTP helpers with explicit source metadata."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept": "*/*",
}


@dataclass(frozen=True)
class FetchResult:
    url: str
    body: bytes
    status: int
    headers: dict[str, str]


def fetch_bytes(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: int = 30,
) -> FetchResult:
    request_headers = dict(DEFAULT_HEADERS)
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            status = int(response.getcode() or 0)
            body = response.read()
            response_headers = {k.lower(): v for k, v in response.headers.items()}
    except (HTTPError, URLError) as exc:
        return _fetch_with_curl(url, request_headers, timeout, exc)
    if status >= 400:
        raise RuntimeError(f"HTTP {status} fetching {url}")
    return FetchResult(url=url, body=body, status=status, headers=response_headers)


def _fetch_with_curl(
    url: str,
    headers: Mapping[str, str],
    timeout: int,
    original_error: Exception,
) -> FetchResult:
    cmd = [
        "curl",
        "-sS",
        "-L",
        "--max-time",
        str(timeout),
        "-A",
        headers.get("User-Agent", DEFAULT_HEADERS["User-Agent"]),
    ]
    for key, value in headers.items():
        if key.lower() == "user-agent":
            continue
        cmd.extend(["-H", f"{key}: {value}"])
    cmd.append(url)

    result = subprocess.run(cmd, check=False, capture_output=True)
    if result.returncode != 0 or not result.stdout:
        raise RuntimeError(
            f"failed fetching {url}; urllib error={original_error!r}; "
            f"curl rc={result.returncode}; stderr={result.stderr.decode('utf-8', 'ignore')}"
        ) from original_error
    return FetchResult(url=url, body=result.stdout, status=0, headers={})
