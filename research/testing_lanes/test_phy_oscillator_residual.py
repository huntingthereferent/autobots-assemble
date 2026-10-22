"""Offline controls for PHY-OSCILLATOR-RESIDUAL-001."""
import unittest

from phy_oscillator_residual import (
    TIME_STEPS, analytic_x, build_receipt, euler_trace, rmse_against_analytic,
)


class PhyOscillatorTests(unittest.TestCase):
    def test_initial_condition_matches_reference(self):
        self.assertAlmostEqual(analytic_x(0.0), 1.0, places=12)
        self.assertEqual(euler_trace(0.02)[0], (0.0, 1.0))

    def test_refinement_reduces_residual(self):
        errors = [rmse_against_analytic(euler_trace(dt)) for dt in TIME_STEPS]
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])

    def test_rejects_invalid_time_step(self):
        with self.assertRaises(ValueError):
            euler_trace(0)
        with self.assertRaises(ValueError):
            euler_trace(0.03)

    def test_receipt_keeps_simulation_boundary_explicit(self):
        receipt = build_receipt()
        self.assertEqual(receipt["status"], "STEP_REFINEMENT_CONVERGES")
        self.assertIn("no independently measured physical signal", " ".join(receipt["limits"]))
        self.assertTrue(receipt["controls"]["all_sample_counts_match_horizon"])


if __name__ == "__main__":
    unittest.main()
