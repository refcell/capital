"""Record a saved source file in a call's manifest.

    python3 -m capital.sources CNM 2026-11-11 data/CNM/2026-11-11/sources/8k.htm \
        --url https://www.sec.gov/... --description "Q3 pre-announcement (8-K EX-99.1)"

The file must already sit under data/<T>/<date>/sources/. Its SHA-256 and fetch time are
recorded; CI then fails if the file ever changes.

    python3 -m capital.sources --repin

Repoints repo entries whose pinned commit is no longer in history (after a rebase) to the
earliest commit where the file has the recorded SHA-256. Run it after rebasing a run onto main.
"""

from __future__ import annotations

import argparse
import re
import subprocess
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


def repin() -> list[str]:
    """Fix repo entries pinned to commits that a rebase removed. Returns the changes made."""
    changes = []
    for manifest_path in sorted(store.ROOT.glob("data/*/*/sources/manifest.json")):
        manifest = store.load_json(manifest_path)
        changed = False
        for entry in manifest["entries"]:
            if entry["kind"] != "repo" or store.git_blob(entry["commit"], entry["path"]) is not None:
                continue
            log = subprocess.run(
                ["git", "log", "--reverse", "--format=%H", "--", entry["path"]],
                cwd=store.ROOT, capture_output=True, text=True, check=True,
            ).stdout.split()
            for commit in log:
                data = store.git_blob(commit, entry["path"])
                if data is not None and store.sha256_bytes(data) == entry["sha256"]:
                    changes.append(f"{manifest_path.relative_to(store.ROOT)}: {entry['id']} {entry['commit']} -> {commit[:12]}")
                    entry["commit"] = commit[:12]
                    changed = True
                    break
        if changed:
            store.write_json(manifest_path, manifest)
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ticker", nargs="?")
    parser.add_argument("date", nargs="?")
    parser.add_argument("file", type=Path, nargs="?")
    parser.add_argument("--url")
    parser.add_argument("--description")
    parser.add_argument("--repin", action="store_true", help="repoint repo entries after a rebase")
    args = parser.parse_args(argv)
    if args.repin:
        for line in repin():
            print(line)
        return 0
    if not (args.ticker and args.date and args.file):
        parser.error("ticker, date and file are required unless --repin is given")
    entry = add(args.ticker.upper(), args.date, args.file, args.url, args.description)
    print(f"recorded {entry['id']} ({entry['sha256'][:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
