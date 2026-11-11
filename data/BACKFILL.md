# Backfill report

`scripts/backfill_calls.py` read 129 report versions and wrote 124 calls (when several commits share a report date, the latest wins); 1 hand-curated call(s) were left untouched. Every extracted number has a verbatim evidence quote checked by `python3 -m capital.validate`. Fields the extractor could not quote are null.

## Gaps

- CELH 9c0e68d: no stance stated
- CVE 770f436: no bear/base/bull value table parsed
- DLO e628e69: no stance stated
- ETOR 7fa3f5d: no bear/base/bull value table parsed
- FDS 2f1f48c: no bear/base/bull value table parsed
- FOUR 9343e9b: no stance stated
- HIMS b989626: no stance stated
- HOOD 08623c7: no stance stated
- INTR 2cafc35: no stance stated
- MELI d7d912b: no stance stated
- NOW 450c060: no stance stated
- NU 09300b6: no stance stated; no bear/base/bull value table parsed
- PYPL 9f61507: no stance stated
- QURE 3795ff1: no bear/base/bull value table parsed
- SKT 379105e: no bear/base/bull value table parsed
- SOFI 2f55845: no stance stated
- SPCX 447bd8a: no bear/base/bull value table parsed
- STZ 55eb173: no bear/base/bull value table parsed
- TMDX 83bcdf3: no stance stated
- ZETA b5bcc80: no stance stated; no bear/base/bull value table parsed
