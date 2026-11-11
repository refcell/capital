"""Marks must use the adjusted series so corporate actions do not look like returns."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from capital import score, store

CALL = {
    "ticker": "EXM",
    "date": "2026-01-05",
    "price": {"value": 100.0, "currency": "USD", "date": "2026-01-02"},
    "scenarios": {"bear": {"value": 80.0}, "base": {"value": 120.0}, "bull": {"value": 160.0}},
    "fair_value": {"value": 133.1, "method": "stated"},
}


class ScoreTest(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        prices = root / "data" / "prices"
        prices.mkdir(parents=True)
        # A 2-for-1 split on 01-06: the raw close halves, the adjusted close does not.
        (prices / "EXM.csv").write_text(
            "date,close,adj_close\n2026-01-02,100,50\n2026-01-05,104,52\n2026-01-06,55,55\n2026-01-07,63,63\n"
        )
        (prices / "SPY.csv").write_text(
            "date,close,adj_close\n2026-01-02,500,500\n2026-01-05,505,505\n2026-01-06,510,510\n2026-01-07,525,525\n"
        )
        for p in (mock.patch.object(store, "PRICES", prices), mock.patch.dict(score._series, clear=True)):
            p.start()
            self.addCleanup(p.stop)

    def test_mark_survives_a_split(self) -> None:
        m = score.mark(CALL)
        # 100 x 63/50 = 126, not 63 (raw close) and not a -37% loss.
        self.assertEqual(m.start, "2026-01-02")
        self.assertEqual(m.as_of, "2026-01-07")
        self.assertAlmostEqual(m.mark, 126.0)
        self.assertAlmostEqual(m.ret, 0.26)
        self.assertAlmostEqual(m.bench_ret, 0.05)
        self.assertAlmostEqual(m.excess, 0.21)
        self.assertEqual(m.band, "base to bull")

    def test_mark_as_of_uses_last_session_on_or_before(self) -> None:
        m = score.mark(CALL, as_of="2026-01-05")
        self.assertAlmostEqual(m.mark, 104.0)
        self.assertEqual(m.band, "bear to base")

    def test_rule_rating_boundaries(self) -> None:
        # 133.1 / 100 over 3 years is exactly 10% a year: Watch.
        self.assertAlmostEqual(score.expected_annual(CALL), 0.10)
        self.assertEqual(score.rule_rating(CALL), "watch")
        own = dict(CALL, fair_value={"value": 152.1, "method": "stated"})  # 1.15^3 = 1.520875
        self.assertEqual(score.rule_rating(own), "own")
        avoid = dict(CALL, fair_value={"value": 99.0, "method": "stated"})
        self.assertEqual(score.rule_rating(avoid), "avoid")


if __name__ == "__main__":
    unittest.main()
