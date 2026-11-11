"""Month-end multiples must stay on one share basis across a stock split."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from capital import multiples, pit

HEADER = "taxonomy,tag,unit,start,end,val,accn,form,filed,fy,fp\n"
K, Q = "0000000001-25-000001", "0000000001-25-000009"
ROWS = [
    # FY2024 10-K, filed before a 10:1 split on 2025-06-16.
    f"us-gaap,Revenues,USD,2024-01-01,2024-12-31,1000,{K},10-K,2025-02-20,2024,FY",
    f"us-gaap,NetIncomeLoss,USD,2024-01-01,2024-12-31,100,{K},10-K,2025-02-20,2024,FY",
    f"us-gaap,EarningsPerShareDiluted,USD/shares,2024-01-01,2024-12-31,1.00,{K},10-K,2025-02-20,2024,FY",
    f"us-gaap,WeightedAverageNumberOfDilutedSharesOutstanding,shares,2024-01-01,2024-12-31,100,{K},10-K,2025-02-20,2024,FY",
    # H1 2025 10-Q, filed after the split: per-share facts are on the new basis.
    f"us-gaap,Revenues,USD,2025-01-01,2025-06-30,600,{Q},10-Q,2025-08-01,2025,Q2",
    f"us-gaap,Revenues,USD,2024-01-01,2024-06-30,500,{Q},10-Q,2025-08-01,2025,Q2",
    f"us-gaap,NetIncomeLoss,USD,2025-01-01,2025-06-30,60,{Q},10-Q,2025-08-01,2025,Q2",
    f"us-gaap,NetIncomeLoss,USD,2024-01-01,2024-06-30,50,{Q},10-Q,2025-08-01,2025,Q2",
    f"us-gaap,EarningsPerShareDiluted,USD/shares,2025-01-01,2025-06-30,0.06,{Q},10-Q,2025-08-01,2025,Q2",
    f"us-gaap,EarningsPerShareDiluted,USD/shares,2024-01-01,2024-06-30,0.05,{Q},10-Q,2025-08-01,2025,Q2",
    f"us-gaap,WeightedAverageNumberOfDilutedSharesOutstanding,shares,2025-01-01,2025-06-30,1000,{Q},10-Q,2025-08-01,2025,Q2",
]
SPLIT = [("2025-06-16", 10.0)]


class MultiplesTest(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "EXM.csv").write_text(HEADER + "\n".join(ROWS) + "\n")
        p = mock.patch.object(pit, "FACTS", root)
        p.start()
        self.addCleanup(p.stop)
        pit.facts.cache_clear()
        self.addCleanup(pit.facts.cache_clear)
        multiples._asof_cache.clear()
        self.addCleanup(multiples._asof_cache.clear)
        self.filings = multiples._filing_dates("EXM")

    def pe(self, month: str, price: float) -> float | None:
        p = multiples.point("EXM", month, multiples.month_end(month), price, SPLIT, self.filings)
        return p.pe if p else None

    def test_pe_is_unchanged_by_the_split_itself(self) -> None:
        # $50 before the split and $5 after it are the same company value: 50x on $1.00.
        self.assertEqual(self.pe("2025-05", 50.0), 50.0)
        self.assertEqual(self.pe("2025-06", 5.0), 50.0)

    def test_pe_after_the_first_post_split_filing(self) -> None:
        # TTM net income 100 + 60 - 50 = 110 on 1,000 post-split shares: $0.11, so $5 is 45.45x.
        # Summing per-share facts instead (1.00 + 0.06 - 0.05) would give about 5x.
        self.assertEqual(self.pe("2025-08", 5.0), 45.45)


if __name__ == "__main__":
    unittest.main()
