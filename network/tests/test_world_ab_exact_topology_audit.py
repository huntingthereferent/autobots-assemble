"""Independent test cases for exact finite WORLD incidence predicates.

This is a source-topology audit, not a contact/physics solver. Python's exact
Fractions are a separate oracle for the *recorded binary float coordinates*.
"""
import unittest

from systems.workspace.world_ab_connected_routing import assemble
from systems.workspace.world_ab_exact_topology_audit import (
    orientation, segment_kind, audit_classification,
)


class ExactTopologyAuditTests(unittest.TestCase):
    def test_real_world_source_crossing_stays_a_crossing(self):
        source = assemble()
        a, b = [s["endpoints"] for s in source["surfaces"]]
        report = audit_classification(a, b)
        self.assertEqual(report["exact_recorded_coordinate_kind"], "interior-crossing")
        self.assertTrue(report["agrees_with_approximation"])
        self.assertFalse(report["execution_started"])
        self.assertFalse(report["world_source_changed"])
        self.assertFalse(report["contact_resolution_claimed"])
        self.assertEqual(segment_kind(a, b), segment_kind(b, a))
        self.assertEqual(segment_kind(list(reversed(a)), b), "interior-crossing")
        self.assertEqual(segment_kind(a, list(reversed(b))), "interior-crossing")

    def test_exact_orientation_exposes_float_cancellation(self):
        # Chosen floating-point inputs cause both rounded products to match,
        # although their exact binary products have a nonzero determinant.
        a = (0., 0.)
        b = (11.344055354362153, 3.0664009210711876)
        c = (21.074905418779654, 5.696737839240536)
        naive = b[0] * c[1] - b[1] * c[0]
        self.assertEqual(naive, 0.0)
        self.assertEqual(orientation(a, b, c), -1)
        self.assertEqual(orientation(a, c, b), 1)
        self.assertEqual(orientation(a, b, b), 0)
        report = audit_classification((a, b), (a, c))
        self.assertEqual(report["exact_recorded_coordinate_kind"], "shared-endpoint")
        self.assertEqual(report["existing_approximate_kind"], "parallel-or-unresolved")
        self.assertFalse(report["agrees_with_approximation"])

    def test_distinguish_touches_overlap_and_disjoint(self):
        a = ((0, 0), (2, 0))
        cases = (
            (((2, 0), (3, 1)), "shared-endpoint"),
            (((1, 0), (1, 1)), "endpoint-interior"),
            (((2, 0), (4, 0)), "collinear-touch"),
            (((1, 0), (4, 0)), "collinear-overlap"),
            (((3, 0), (4, 0)), "disjoint"),
            (((1, -1), (1, 1)), "interior-crossing"),
            (((0, 1), (2, 1)), "disjoint"),
        )
        for other, kind in cases:
            with self.subTest(other=other):
                self.assertEqual(segment_kind(a, other), kind)
                self.assertEqual(segment_kind(other, a), kind)
                self.assertEqual(segment_kind(a, tuple(reversed(other))), kind)

    def test_prohibit_unsupported_and_unbounded_inputs(self):
        valid = ((0, 0), (1, 1))
        bad = (
            ((0, 0), (0, 0)),
            ((0, 0), (float("nan"), 1)),
            ((0, 0), (float("inf"), 1)),
            ((0, 0), (10001, 0)),
            ((0, 0), (True, 1)),
            ((0, 0), ("1", 1)),
            ((0, 0),),
        )
        for candidate in bad:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                segment_kind(candidate, valid)

    def test_no_contact_asserted_for_nearby_but_not_touching_segments(self):
        a = ((0., 0.), (2., 0.))
        b = ((2. + 2**-40, 0.), (3., 1.))
        self.assertEqual(segment_kind(a, b), "disjoint")


if __name__ == "__main__":
    unittest.main()
