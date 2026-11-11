"""The validator must reject calls whose numbers disagree with each other or with the report."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from capital import store, validate

REPORT = """# Example Corp (NYSE: EXM) Investment Research

EXM closed at $50.00 on November 6, 2026.

| | Bear | Base | Bull |
|---|---:|---:|---:|
| Target | $30.00 | $60.00 | $90.00 |
| Weight | 25% | 50% | 25% |

Probability-weighted fair value $60.00. Street average target $55.00.
"""

CALL = {
    "schema_version": 1,
    "ticker": "EXM",
    "exchange": "NYSE",
    "company": "Example Corp",
    "date": "2026-11-07",
    "origin": "backfill",
    "stance": "watch",
    "stance_text": "Watch",
    "price": {"value": 50.0, "currency": "USD", "date": "2026-11-06"},
    "scenarios": {
        "bear": {"value": 30.0, "weight": 0.25},
        "base": {"value": 60.0, "weight": 0.5},
        "bull": {"value": 90.0, "weight": 0.25},
    },
    "fair_value": {"value": 60.0, "method": "weighted"},
    "street": {"target_mean": 55.0},
    "deviation_from_street": {"pct": 9.1},
    "artifacts": {"report": {"path": "research/EXM.md", "commit": None}},
    "evidence": {"fair_value.value": "Probability-weighted fair value $60.00"},
}


class ValidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "research").mkdir()
        (self.root / "research" / "EXM.md").write_text(REPORT)
        patches = [
            mock.patch.object(store, "ROOT", self.root),
            mock.patch.object(store, "DATA", self.root / "data"),
            mock.patch.object(store, "PRICES", self.root / "data" / "prices"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, self.root)

    def errors_for(self, call: dict) -> list[str]:
        store.write_json(store.call_dir(call["ticker"], call["date"]) / "call.json", call)
        return validate.run()

    def test_consistent_call_passes(self) -> None:
        self.assertEqual(self.errors_for(CALL), [])

    def test_inconsistent_numbers_fail(self) -> None:
        bad = copy.deepcopy(CALL)
        # Weighted value of these scenarios is 56.25, not the stated 60.
        bad["scenarios"]["bull"]["value"] = 75.0
        # Fair value 60 against a Street mean of 55 is +9.1%, not +20%.
        bad["deviation_from_street"]["pct"] = 20.0
        errors = "\n".join(self.errors_for(bad))
        self.assertIn("does not match weighted scenarios 56.25", errors)
        self.assertIn("deviation_from_street.pct 20.0", errors)

    def test_misordered_scenarios_and_missing_quote_fail(self) -> None:
        bad = copy.deepcopy(CALL)
        bad["scenarios"]["bear"]["value"] = 65.0
        bad["evidence"]["fair_value.value"] = "Probability-weighted fair value $61.00"
        errors = "\n".join(self.errors_for(bad))
        self.assertIn("scenario bear $65.0 is above base $60.0", errors)
        self.assertIn("evidence for fair_value.value not found", errors)

    def test_run_calls_need_review_fields(self) -> None:
        run = copy.deepcopy(CALL)
        run["origin"] = "run"
        errors = "\n".join(self.errors_for(run))
        for field in ("inputs.json", "next_review", "thesis", "catalysts", "change_my_mind", "'Valuation' section"):
            self.assertIn(field, errors)


if __name__ == "__main__":
    unittest.main()
