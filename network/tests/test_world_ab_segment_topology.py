"""Independent topology checks against ORIGINAL Trial 05 source surfaces.

No changes to Trial 06/07/08 collision or multi-contact mechanics. The
Box2D ghost-chain idea is only considered when source segments join end-to-end.
"""
from copy import deepcopy
import unittest

from systems.workspace.world_ab_connected_routing import assemble
from systems.workspace.world_ab_segment_topology import classify_pair


class SegmentTopologyTests(unittest.TestCase):
    def test_actual_source_meeting_is_interior_crossing_not_ghost_chain(self):
        original = assemble()
        before = deepcopy(original)
        surfaces = original["surfaces"]
        report = classify_pair(surfaces[0]["endpoints"], surfaces[1]["endpoints"])
        self.assertEqual(report["topology"], "interior-crossing")
        self.assertFalse(report["chain_ghost_rule_applicable"])
        # Independently compare source-derived local parameters, where source
        # u/v use centered [-.5,+.5] and this predicate uses endpoint [0,1].
        expected = original["junction_local_coordinates"]
        self.assertAlmostEqual(report["intersection_fractions"][0], expected[0] + .5, places=6)
        self.assertAlmostEqual(report["intersection_fractions"][1], expected[1] + .5, places=6)
        self.assertEqual(original, before)
        reversed_one = classify_pair(list(reversed(surfaces[0]["endpoints"])),
                                     surfaces[1]["endpoints"])
        self.assertEqual(reversed_one["topology"], report["topology"])
        self.assertFalse(reversed_one["chain_ghost_rule_applicable"])

    def test_only_a_shared_endpoint_is_candidate_for_chain_analysis(self):
        result = classify_pair(((0, 0), (1, 0)), ((1, 0), (1, 1)))
        self.assertEqual(result["topology"], "shared-endpoint")
        self.assertTrue(result["chain_ghost_rule_applicable"])
        self.assertIn("further", result["conclusion"])

    def test_endpoint_to_interior_does_not_satisfy_chain_boundary(self):
        result = classify_pair(((0, 0), (2, 0)), ((1, 0), (1, 1)))
        self.assertEqual(result["topology"], "endpoint-interior")
        self.assertFalse(result["chain_ghost_rule_applicable"])

    def test_disjoint_parallel_unresolved_are_not_mislabelled(self):
        a = ((0, 0), (2, 0))
        for b, expected in (
            (((3, -1), (3, 1)), "disjoint"),
            (((0, 1), (2, 1)), "parallel-or-unresolved"),
            (((1, 0), (3, 0)), "parallel-or-unresolved"),
        ):
            with self.subTest(b=b):
                got = classify_pair(a, b)
                self.assertEqual(got["topology"], expected)
                self.assertFalse(got["chain_ghost_rule_applicable"])

    def test_nonfinite_degenerate_and_missing_source_are_rejected(self):
        for a, b in (
            (((0, 0), (0, 0)), ((0, 0), (1, 1))),
            (((float("nan"), 0), (1, 0)), ((0, 0), (1, 1))),
            (((0, 0), (1, 0)), ((0, float("inf")), (1, 1))),
            (((0, 0),), ((0, 0), (1, 1))),
        ):
            with self.subTest(a=a,b=b), self.assertRaises(ValueError):
                classify_pair(a, b)


if __name__ == "__main__":
    unittest.main()
