"""Rewrite every JSON file under data/ in canonical form. Run: python3 -m capital.fmt

Files saved under a call's sources/ directory are verbatim captures pinned by hash in
manifest.json, so they are never rewritten; only manifest.json itself is.
"""

from __future__ import annotations

from capital import store


def main() -> None:
    changed = 0
    for path in sorted(store.DATA.rglob("*.json")):
        if path.parent.name == "sources" and path.name != "manifest.json":
            continue
        text = path.read_text(encoding="utf-8")
        canonical = store.dumps(store.load_json(path))
        if text != canonical:
            path.write_text(canonical, encoding="utf-8")
            changed += 1
    print(f"formatted {changed} file(s)")


if __name__ == "__main__":
    main()
