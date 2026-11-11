"""Record a saved source file in a call's manifest.

    python3 -m capital.sources CNM 2026-11-11 data/CNM/2026-11-11/sources/8k.htm \
        --url https://www.sec.gov/... --description "Q3 pre-announcement (8-K EX-99.1)"

The file must already sit under data/<T>/<date>/sources/. Its SHA-256 and fetch time are
recorded; CI then fails if the file ever changes.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from capital import store


def add(ticker: str, day: str, file: Path, url: str | None, description: str | None) -> dict:
    src = store.call_dir(ticker, day) / "sources"
    file = file.resolve()
    rel = file.relative_to(src.resolve()).as_posix()
    manifest_path = src / "manifest.json"
    manifest = store.load_json(manifest_path) if manifest_path.exists() else {"schema_version": 1, "entries": []}
    entries = [e for e in manifest["entries"] if not (e["kind"] == "file" and e["path"] == rel)]
    ident = re.sub(r"[^a-z0-9]+", "-", Path(rel).stem.lower()).strip("-")
    mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat()
    entry = {
        "id": ident, "kind": "file", "path": rel, "url": url, "fetched_at": mtime,
        "sha256": store.sha256_bytes(file.read_bytes()), "description": description,
    }
    entries.append(entry)
    manifest["entries"] = entries
    store.write_json(manifest_path, manifest)
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ticker")
    parser.add_argument("date")
    parser.add_argument("file", type=Path)
    parser.add_argument("--url")
    parser.add_argument("--description")
    args = parser.parse_args(argv)
    entry = add(args.ticker.upper(), args.date, args.file, args.url, args.description)
    print(f"recorded {entry['id']} ({entry['sha256'][:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
