"""Offline positive and negative controls for MATH-IDENTITY-001."""
import unittest

from math_odd_sum import evaluate, sum_first_odds


class MathOddSumTests(unittest.TestCase):
    def test_exact_sum_for_small_values(self):
        self.assertEqual([sum_first_odds(n) for n in range(6)], [0, 1, 4, 9, 16, 25])

    def test_reconstruction_and_induction_step(self):
        receipt = evaluate(1000)
        self.assertEqual(receipt["state"], "RECONSTRUCTION_MATCH")
        self.assertEqual(receipt["finite_checks"]["cases_checked"], 1001)
        self.assertTrue(receipt["base_case"]["matches"])
        self.assertTrue(receipt["induction_step"]["matches"])

    def test_negative_control_has_explicit_counterexample(self):
        receipt = evaluate(10)
        negative = receipt["negative_control"]
        self.assertTrue(negative["rejected"])
        self.assertEqual(negative["counterexample"], {
            "n": 1, "observed_sum": 1, "claimed_value": 2
        })

    def test_rejects_negative_n(self):
        with self.assertRaises(ValueError):
            sum_first_odds(-1)

    def test_rejects_negative_bound(self):
        with self.assertRaises(ValueError):
            evaluate(-1)


if __name__ == "__main__":
    unittest.main()
