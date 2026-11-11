"""Point-in-time selection must never see a value before it was filed."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from capital import pit

HEADER = "taxonomy,tag,unit,start,end,val,accn,form,filed,fy,fp\n"
REV = "us-gaap,Revenues,USD"
ROWS = [
    # FY2024 as first filed, then restated a year later.
    f"{REV},2024-01-01,2024-12-31,1000,0000000001-25-000001,10-K,2025-02-20,2024,FY",
    f"{REV},2024-01-01,2024-09-30,700,0000000001-24-000009,10-Q,2024-11-01,2024,Q3",
    f"{REV},2025-01-01,2025-09-30,900,0000000001-25-000009,10-Q,2025-11-01,2025,Q3",
    f"{REV},2024-01-01,2024-12-31,800,0000000001-26-000001,10-K,2026-02-20,2025,FY",
    "us-gaap,CashAndCashEquivalentsAtCarryingValue,USD,,2025-09-30,55,0000000001-25-000009,10-Q,2025-11-01,2025,Q3",
]

EPS, DIL = "us-gaap,EarningsPerShareDiluted,USD/shares", "us-gaap,WeightedAverageNumberOfDilutedSharesOutstanding,shares"
SPLIT_ROWS = [
    # FY2024 10-K before a 4:1 split on 2025-06-16; the H1 2025 10-Q after it restates H1 2024 on the new basis.
    f"{EPS},2024-01-01,2024-12-31,4.00,0000000002-25-000001,10-K,2025-02-20,2024,FY",
    f"{DIL},2024-01-01,2024-12-31,100,0000000002-25-000001,10-K,2025-02-20,2024,FY",
    f"{EPS},2025-01-01,2025-06-30,0.60,0000000002-25-000009,10-Q,2025-08-01,2025,Q2",
    f"{EPS},2024-01-01,2024-06-30,0.50,0000000002-25-000009,10-Q,2025-08-01,2025,Q2",
    f"{DIL},2024-01-01,2024-06-30,400,0000000002-25-000009,10-Q,2025-08-01,2025,Q2",
    f"{DIL},2025-01-01,2025-06-30,400,0000000002-25-000009,10-Q,2025-08-01,2025,Q2",
]
# SPL's 4:1 split is confirmed by the restated H1 2024 count; EXM's 1.05 event (a spin-off) is not.
SPLITS = "symbol,date,numerator,denominator\nSPL,2025-06-16,4,1\nEXM,2025-03-01,105,100\n"


class PitTest(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "EXM.csv").write_text(HEADER + "\n".join(ROWS) + "\n")
        (root / "SPL.csv").write_text(HEADER + "\n".join(SPLIT_ROWS) + "\n")
        (root / "splits.csv").write_text(SPLITS)
        for name, value in (("FACTS", root), ("SPLITS", root / "splits.csv")):
            p = mock.patch.object(pit, name, value)
            p.start()
            self.addCleanup(p.stop)
        for cache in (pit.facts, pit.splits):
            cache.cache_clear()
            self.addCleanup(cache.cache_clear)

    def test_annual_before_the_next_quarter(self) -> None:
        v = pit.as_of("EXM", "2025-06-01")["revenue"]
        self.assertEqual((v.value, v.method, v.end), (1000, "annual", "2024-12-31"))

    def test_ttm_from_ytd_once_the_10q_is_filed(self) -> None:
        # 1000 + 900 - 700, using FY2024 as filed at the time, not the later restatement.
        v = pit.as_of("EXM", "2025-11-02")["revenue"]
        self.assertEqual((v.value, v.method, v.end), (1200, "ttm_ytd", "2025-09-30"))
        self.assertEqual(pit.as_of("EXM", "2025-11-02")["cash"].value, 55)

    def test_restatement_is_invisible_until_filed(self) -> None:
        self.assertEqual(pit.as_of("EXM", "2026-02-19")["revenue"].value, 1200)
        # After the restated 10-K: 800 + 900 - 700.
        self.assertEqual(pit.as_of("EXM", "2026-02-20")["revenue"].value, 1000)

    def test_nothing_known_before_first_filing(self) -> None:
        self.assertNotIn("revenue", pit.as_of("EXM", "2024-10-01"))

    def test_ttm_eps_stays_on_one_share_basis_across_a_split(self) -> None:
        # Pre-split FY2024 $4.00 is $1.00 on the new basis: 1.00 + 0.60 - 0.50 = 1.10, not 4.10.
        v = pit.as_of("SPL", "2025-08-02")
        self.assertAlmostEqual(v["eps_diluted"].value, 1.10)
        # Before the 10-Q, the 10-K's figures are carried to the post-split basis.
        v = pit.as_of("SPL", "2025-07-01")
        self.assertEqual((v["eps_diluted"].value, v["diluted_shares"].value), (1.00, 400))

    def test_spin_off_recorded_as_a_split_is_ignored(self) -> None:
        self.assertEqual(pit.splits("EXM"), ())


if __name__ == "__main__":
    unittest.main()
