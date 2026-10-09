"""End-to-end algebra of transported root witnesses and coordinate gauges."""
import unittest
from itertools import product

from work.arc_like_maze.root_transport import (
    Process, Witness, find, verify, ZERO, IDENTITY, NEGATIVE, MarkedWorld,
    verify_marked_pair,
)
from work.arc_like_maze.marked_operator_system import (
    BoundaryGauge, MarkedObject, MarkedArrow, identical_streams, witness_tail,
    shift_arrow, transform_arrow, same_arrow, interchange, compose_arrows,
    invert_arrow, audit_period_two,
)


class MarkedOperatorSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Process.repeat(ZERO, (0, 0, 1))
        q = Process.repeat(ZERO, (0, 1, 0))
        cls.arrow = MarkedArrow(MarkedObject(p, 1), MarkedObject(q, 1), find(p, q))

    def test_eight_gauges_form_a_group(self):
        gauges = tuple(BoundaryGauge(b, (s, t))
                       for b, s, t in product((1, 2), repeat=3))
        signatures = {(g.incoming, g.period) for g in gauges}
        self.assertEqual(len(signatures), 8)
        for g in gauges:
            self.assertEqual(g.compose(g.inverse()), BoundaryGauge(1, (1, 1)))
            for h in gauges:
                self.assertIn((g.compose(h).incoming, g.compose(h).period), signatures)
                self.assertEqual(g.compose(h), h.compose(g))

    def test_exhaustive_group_action_and_interchange(self):
        cert = audit_period_two()
        self.assertEqual(cert.status, "CLOSED_MARKED_GAUGE_SHIFT_SYSTEM")
        self.assertEqual((cert.gauges, cert.raw_templates), (8, 81))
        self.assertEqual((cert.exact_compositions, cert.interchange_squares),
                         (5184, 256))
        self.assertTrue(cert.boundary_mismatch)

    def test_shift_preserves_the_original_witness_not_a_new_choice(self):
        p = Process.repeat(ZERO, ZERO)
        w = Witness('ALIGNED', 2, (1, 2, 2), (2, 1, 1))
        a = MarkedArrow(MarkedObject(p, 1), MarkedObject(p, 2), w)
        for k in range(0, 17):
            shifted = shift_arrow(a, k)
            self.assertEqual(shifted.witness.incoming,
                             w.incoming if k == 0 else w.scale(k - 1))
            for i in range(23):
                self.assertEqual(shifted.witness.scale(i), w.scale(k + i))
        # Multiple possible zero-rule alignments must NOT be conflated.
        other = Witness('ALIGNED', 2, (), (1,))
        self.assertTrue(verify(p, p, other))
        self.assertNotEqual(w.scale(1), other.scale(1))

    def test_interchange_square_for_different_source_target_gauges(self):
        a = self.arrow
        options = ((1, (1, 2)), (2, (2, 1)), (2, (2, 2)), (1, (1,)))
        for inc_a, scales_a in options:
            for inc_b, scales_b in options:
                u, v = BoundaryGauge(inc_a, scales_a), BoundaryGauge(inc_b, scales_b)
                for k in (0, 1, 2, 3, 4, 11):
                    self.assertTrue(interchange(a, u, v, k))

    def test_interchange_for_stemmed_processes(self):
        p = Process((IDENTITY, ZERO, NEGATIVE), (ZERO, IDENTITY))
        u = BoundaryGauge(2, (1, 2, 2))
        q = u.apply(p)
        a = MarkedArrow(MarkedObject(p, 1), MarkedObject(q, 2),
                        Witness('ALIGNED', 2, (), (1, 2, 2)))
        for k in (0, 1, 2, 3, 4, 5, 8):
            self.assertTrue(interchange(
                a, BoundaryGauge(2, (2, 1)), BoundaryGauge(1, (1, 2, 2)), k))

    def test_marked_interchange_on_full_finite_state_spaces(self):
        u, v = BoundaryGauge(2, (2, 1)), BoundaryGauge(1, (1, 2))
        for k in (1, 2, 3):
            transformed = transform_arrow(shift_arrow(self.arrow, k),
                                          u.shifted(k), v.shifted(k))
            for depth in range(3, 8):
                self.assertTrue(verify_marked_pair(transformed.source.world(),
                                                   transformed.target.world(),
                                                   transformed.witness, depth))

    def test_arrows_compose_and_invert_with_exact_marks(self):
        p = Process.repeat(ZERO, (0, 0, 1))
        u, v = BoundaryGauge(2, (2, 1)), BoundaryGauge(1, (1, 2))
        q = u.apply(p)
        r = v.apply(q)
        first = MarkedArrow(MarkedObject(p, 1), MarkedObject(q, u.incoming),
                            Witness('ALIGNED', u.incoming, (), u.period))
        second = MarkedArrow(first.target,
                             MarkedObject(r, u.incoming * v.incoming % 3),
                             Witness('ALIGNED', v.incoming, (), v.period))
        composed = compose_arrows(first, second)
        self.assertTrue(verify(p, r, composed.witness))
        reverse = invert_arrow(composed)
        identity = compose_arrows(composed, reverse)
        self.assertEqual(identity.witness.incoming, 1)
        self.assertTrue(all(identity.witness.scale(i) == 1 for i in range(40)))
        for k in range(1, 5):
            shifted_first = shift_arrow(first, k)
            shifted_second = shift_arrow(second, k,
                                          new_source_gain=shifted_first.target.gain)
            self.assertTrue(same_arrow(
                compose_arrows(shifted_first, shifted_second),
                shift_arrow(composed, k),
            ))

    def test_gauge_change_of_composed_arrow_is_functorial(self):
        p = Process.repeat(IDENTITY, NEGATIVE)
        a = BoundaryGauge(2, (1, 2))
        b = BoundaryGauge(2, (2, 1))
        q = a.apply(p)
        r = b.apply(q)
        first = MarkedArrow(MarkedObject(p, 1), MarkedObject(q, 2),
                            Witness('ALIGNED', 2, (), a.period))
        second = MarkedArrow(first.target, MarkedObject(r, 1),
                             Witness('ALIGNED', 2, (), b.period))
        orig = compose_arrows(first, second)
        u, v, z = (BoundaryGauge(1, (2, 1)),
                    BoundaryGauge(2, (1, 2)),
                    BoundaryGauge(2, (2, 2)))
        direct = transform_arrow(orig, u, z)
        edges = compose_arrows(transform_arrow(first, u, v),
                               transform_arrow(second, v, z))
        self.assertTrue(same_arrow(direct, edges))

    def test_boundary_cannot_be_silently_reset(self):
        shifted = shift_arrow(self.arrow, 1)
        self.assertEqual(shifted.witness.incoming, 2)
        with self.assertRaises(ValueError):
            MarkedArrow(shifted.source,
                        MarkedObject(shifted.target.process, 1), shifted.witness)

    def test_addition_still_breaks_free_boundary_equivalence(self):
        def add(p):
            def plus(rule):
                return tuple((a + b) % 3 for a, b in zip(rule, IDENTITY))
            return Process(tuple(plus(r) for r in p.stem),
                           tuple(plus(r) for r in p.period))
        p, q = Process.repeat(IDENTITY), Process.repeat(NEGATIVE)
        self.assertEqual(find(p, q).status, 'ALIGNED')
        for b in (1, 2):
            self.assertEqual(find(add(p), add(q), b).status, 'OPEN')

    def test_invalid_marks_cannot_be_admitted(self):
        with self.assertRaises(ValueError):
            BoundaryGauge(3, (1, 2))
        with self.assertRaises(ValueError):
            BoundaryGauge(1, (1, 0))
        with self.assertRaises(ValueError):
            shift_arrow(self.arrow, -1)
        with self.assertRaises(ValueError):
            shift_arrow(self.arrow, 1, new_source_gain=0)
        with self.assertRaises(ValueError):
            MarkedArrow(self.arrow.source, self.arrow.target,
                        Witness('ALIGNED', 1, (), (1,)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
