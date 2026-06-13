from __future__ import annotations

import unittest

from functions.common.stats import ols
from functions.factor_exposure import main


class FactorExposureTests(unittest.TestCase):
    def test_ols_recovers_simple_coefficients(self) -> None:
        x = []
        y = []
        for i in range(1, 20):
            x.append([1.0, float(i)])
            y.append(2.0 + 3.0 * i)

        result = ols(y, x, ["alpha", "factor"])

        self.assertAlmostEqual(result["coefficients"]["alpha"]["beta"], 2.0)
        self.assertAlmostEqual(result["coefficients"]["factor"]["beta"], 3.0)
        self.assertAlmostEqual(result["r_squared"], 1.0)

    def test_parse_five_factor_csv(self) -> None:
        text = """Header text
,Mkt-RF,SMB,HML,RMW,CMA,RF
202501,1.00,2.00,3.00,4.00,5.00,0.25
202502,-1.50,0.10,0.20,0.30,0.40,0.26

Annual Factors: January-December
"""
        parsed = main._parse_five_factor_csv(text)

        self.assertEqual(parsed["202501"]["market"], 1.0)
        self.assertEqual(parsed["202502"]["risk_free"], 0.26)

    def test_parse_momentum_csv(self) -> None:
        text = """Header text
,Mom
202501,7.25
202502,-2.50

Annual Factors: January-December
"""
        parsed = main._parse_momentum_csv(text)

        self.assertEqual(parsed["202501"], 7.25)
        self.assertEqual(parsed["202502"], -2.5)

    def test_momentum_classification(self) -> None:
        high = main._classify_momentum(
            score=45.0,
            percentile=90.0,
            ret_12_1=0.35,
            price_vs_200=0.10,
        )
        low = main._classify_momentum(
            score=-45.0,
            percentile=10.0,
            ret_12_1=-0.05,
            price_vs_200=-0.08,
        )

        self.assertEqual(high[1], "be_cautious")
        self.assertEqual(low[1], "constructive_entry_setup")


if __name__ == "__main__":
    unittest.main()

