"""Finite regression for frozen native SP80 boundary projection semantics.

This verifies that later native runs cannot silently change the
predeclared residual rule or treat predicted-but-absent effects as success.
Native arc-agi evidence is collected in separate actual-game CI.
"""
from __future__ import annotations
import unittest

from work.arc3.native_sp80_boundary_prediction import (
    boundary_positions,projected_with_frozen_boundary,score,FROZEN_MAPS
)


class SP80BoundaryWitnessTests(unittest.TestCase):
    def test_frozen_source_observed_bottom_row_schedule(self):
        self.assertEqual(boundary_positions(1),((0,63),))
        self.assertEqual(boundary_positions(2),((1,63),(2,63)))
        self.assertEqual(boundary_positions(3),((3,63),))
        self.assertEqual(boundary_positions(4),((4,63),(5,63)))
        self.assertEqual(boundary_positions(5),((6,63),))
        self.assertEqual(boundary_positions(6),((7,63),(8,63)))

    def test_native_palette_is_unmodified_and_completion_preserves_labels(self):
        for model in FROZEN_MAPS:
            predicted,clipped,conflicts=projected_with_frozen_boundary(
                {(10,5):(9,12)},model,1)
            self.assertEqual(predicted[(0,63)],(14,0))
            self.assertIn((9,12),set(predicted.values()))
            self.assertEqual(conflicts,[])

    def test_extraneous_predicted_pixel_not_exact(self):
        expected={(0,63):(14,0),(61,20):(14,0)}
        native={(0,63):(14,0)}
        outcome=score(expected,native)
        self.assertFalse(outcome["complete_exact_native_pixel_color_changes"])
        self.assertEqual(len(outcome["missing_native_changes"]),0)
        self.assertEqual(len(outcome["false_positive_native_changes"]),1)
        self.assertEqual(outcome["exact_native_color_pair_matches"],1)

    def test_wrong_color_not_accepted_as_exact(self):
        predicted={(0,63):(14,0)}
        native={(0,63):(14,3)}
        outcome=score(predicted,native)
        self.assertTrue(outcome["exact_frame_change_mask_match"])
        self.assertFalse(outcome["complete_exact_native_pixel_color_changes"])
        self.assertEqual(len(outcome["same_position_but_different_native_colors"]),1)


if __name__=="__main__":
    unittest.main()
