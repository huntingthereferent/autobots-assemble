"""Adversarial checks for the recorded ANY pre-movement comparison."""
import unittest
from runtime.pre_move_lens import Comparison, check_before_move


class LensTests(unittest.TestCase):
    def base(self):
        return dict(
            proposed_move="Test independent finite branches",
            ab_comparison=Comparison(
                "bounded recurrence", "foundation/program_kernel/recurrence.py",
                "output is next input; no shared parent branch operation", "analogous"),
            production_comparison=Comparison(
                "digital twin branch semantics", "unverified: comparison needed",
                "no production equivalence established", "unverified"),
            simplification="Reuse recurrence; shared-origin relation remains unknown",
            claim="experiment",
        )

    def test_bounded_experiment_can_proceed_with_explicit_unknown(self):
        self.assertTrue(check_before_move(**self.base()).admitted)

    def test_missing_math_comparison_blocks(self):
        args = self.base()
        args["ab_comparison"] = None
        self.assertIn("missing A/B comparison", check_before_move(**args).reasons)

    def test_missing_production_comparison_blocks(self):
        args = self.base()
        args["production_comparison"] = None
        self.assertIn("missing production comparison", check_before_move(**args).reasons)

    def test_claiming_equivalence_from_unknown_blocks(self):
        args = self.base()
        args["claim"] = "equivalent"
        self.assertFalse(check_before_move(**args).admitted)

    def test_production_ready_claim_blocks(self):
        args = self.base()
        args["claim"] = "production_ready"
        self.assertFalse(check_before_move(**args).admitted)

    def test_empty_source_blocks(self):
        args = self.base()
        args["ab_comparison"] = Comparison("recurrence", "", "observed", "equivalent")
        self.assertFalse(check_before_move(**args).admitted)

    def test_empty_simplification_blocks(self):
        args = self.base()
        args["simplification"] = ""
        self.assertFalse(check_before_move(**args).admitted)


if __name__ == "__main__":
    unittest.main()
