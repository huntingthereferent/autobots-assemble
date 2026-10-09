"""Witness-level closure for 270 marked process objects, not native ARC execution."""
import unittest
from collections import Counter
from itertools import product

from work.arc_like_maze.marked_quotient import (
    seeds, objects, canonical, object_key, gauge_eight, apply_gauge,
    gauge_orbits, alignment_classes, marked_alignment, missing_bridges,
    certify_marked_quotient,
)
from work.arc_like_maze.marked_operator_system import (
    BoundaryGauge, MarkedObject, MarkedArrow, same_arrow,
    invert_arrow, compose_arrows, transform_arrow, shift_arrow, interchange,
)
from work.arc_like_maze.root_transport import Process, verify_marked_pair


class MarkedQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = seeds()
        cls.universe = objects()
        cls.orbits = gauge_orbits()
        cls.classes = alignment_classes()
        cls.bridges = missing_bridges()

    def test_162_periodic_inputs_expand_to_270_marked_objects(self):
        self.assertEqual((len(self.seed), len(self.universe)), (162, 270))
        self.assertEqual(len(set(map(object_key, self.universe))), 270)
        self.assertEqual(len(set(map(object_key, self.seed))), 162)
        # Explicit new one-rule stems are NOT discarded at the root.
        stemmed = [obj for obj in self.universe
                   if obj.process.rule(0) != obj.process.rule(2)]
        self.assertEqual(len(stemmed), 108)

    def test_eight_gauges_partition_into_36_closed_orbits(self):
        self.assertEqual(len(self.orbits), 36)
        self.assertEqual(Counter(map(len, self.orbits)), {2: 1, 4: 3, 8: 32})
        all_keys = set(map(object_key, self.universe))
        for orbit in self.orbits:
            orbit_keys = set(map(object_key, orbit))
            for obj in orbit:
                for gauge in gauge_eight():
                    self.assertIn(object_key(apply_gauge(obj, gauge)), orbit_keys)
        self.assertEqual(set(object_key(o) for orbit in self.orbits for o in orbit),
                         all_keys)

    def test_exact_gauge_action_preserves_stream_and_mark(self):
        # Exhaust all 270 marked objects and all 64 ordered gauge compositions.
        gauges = gauge_eight()
        for obj in self.universe:
            for left in gauges:
                for right in gauges:
                    direct = apply_gauge(obj, left.compose(right))
                    sequential = apply_gauge(apply_gauge(obj, right), left)
                    self.assertEqual(object_key(direct), object_key(sequential))
            identity = BoundaryGauge(1, (1, 1))
            self.assertEqual(object_key(apply_gauge(obj, identity)), object_key(obj))

    def test_full_coinductive_quotient_has_34_classes(self):
        self.assertEqual(len(self.classes), 34)
        self.assertEqual(Counter(map(len, self.classes)),
                         {2: 1, 4: 3, 8: 28, 16: 2})
        self.assertEqual(set(object_key(o) for cls in self.classes for o in cls),
                         set(map(object_key, self.universe)))
        for cls in self.classes:
            for obj in cls:
                self.assertIsNotNone(marked_alignment(cls[0], obj))

    def test_representatives_of_distinct_classes_have_no_admitted_alignment(self):
        # Same assertion as coinductive classification, checked independently.
        for i, source in enumerate(self.classes):
            for target in self.classes[i + 1:]:
                self.assertIsNone(marked_alignment(source[0], target[0]))

    def test_two_bridges_are_genuinely_missing_from_period_two_gauges(self):
        self.assertEqual(len(self.bridges), 2)
        for bridge in self.bridges:
            arrow = bridge.arrow()  # constructor re-verifies coinductive witness
            self.assertEqual(arrow.witness.status, "ALIGNED")
            self.assertTrue(arrow.witness.head)
            self.assertNotEqual(arrow.source, arrow.target)
            for gauge in gauge_eight():
                self.assertNotEqual(object_key(apply_gauge(bridge.source, gauge)),
                                    object_key(bridge.target))

    def test_explicit_nonperiodic_alignment_is_not_period_two(self):
        a, b, c = (0, 1, 2), (0, 1, 1), (0, 2, 2)
        src = MarkedObject(Process((a,), (b, a)), 1)
        dst = MarkedObject(Process((a,), (c, a)), 1)
        w = marked_alignment(src, dst)
        self.assertIsNotNone(w)
        self.assertEqual(w.incoming, 1)
        self.assertEqual(w.scale(0), 1)
        self.assertEqual(w.scale(1), 2)
        self.assertEqual(w.scale(2), 2)
        self.assertNotEqual(w.scale(0), w.scale(2))
        self.assertTrue(all(object_key(apply_gauge(src, g)) != object_key(dst)
                            for g in gauge_eight()))

    def test_missing_witnesses_align_all_states_at_checked_depths(self):
        for bridge in self.bridges:
            a = bridge.arrow()
            for depth in range(3, 8):
                self.assertTrue(verify_marked_pair(
                    a.source.world(), a.target.world(), a.witness, depth))

    def test_bridge_arrows_remain_composable_and_reversible(self):
        for bridge in self.bridges:
            arrow = bridge.arrow()
            identity = compose_arrows(arrow, invert_arrow(arrow))
            self.assertEqual(identity.source, identity.target)
            self.assertEqual(identity.witness.incoming, 1)
            self.assertTrue(all(identity.witness.scale(i) == 1 for i in range(25)))

    def test_bridge_interchange_keeps_exact_witness_and_boundary(self):
        g = BoundaryGauge(2, (1, 2))
        h = BoundaryGauge(1, (2, 1))
        for bridge in self.bridges:
            arrow = bridge.arrow()
            for turns in (0, 1, 2, 3, 5):
                self.assertTrue(interchange(arrow, g, h, turns))

    def test_certificate_reports_both_quotients_without_conflation(self):
        cert = certify_marked_quotient()
        self.assertEqual(cert.status,
                         "CLOSED_GAUGE_ACTION_INCOMPLETE_FOR_COINDUCTIVE_ARROWS")
        self.assertEqual((cert.seed_objects, cert.closed_objects,
                          cert.period_two_gauges, cert.gauge_orbits,
                          cert.coinductive_classes, cert.nonperiodic_bridges),
                         (162, 270, 8, 36, 34, 2))
        self.assertEqual(cert.gauge_orbit_sizes, ((2, 1), (4, 3), (8, 32)))
        self.assertEqual(cert.alignment_class_sizes,
                         ((2, 1), (4, 3), (8, 28), (16, 2)))

    def test_out_of_scope_canonical_shapes_are_rejected(self):
        r = (0, 1, 2)
        with self.assertRaises(ValueError):
            canonical(MarkedObject(Process((r, r), (r,)), 1))
        with self.assertRaises(ValueError):
            apply_gauge(self.seed[0], BoundaryGauge(1, (1,)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
