"""Admitted process operators must preserve equivalence under composition."""
import unittest
from itertools import product

from work.arc_like_maze.process_alignment import (
    IDENTITY, NEGATIVE, ZERO, PeriodicProcess, find_process_alignment,
)
from work.arc_like_maze.process_operators import (
    AddRule, GaugeSchedule, audit_process_operators,
    find_operator_breaks, same_rule_stream,
)


class ProcessOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = audit_process_operators()

    def test_four_gauges_compose_as_closed_group(self):
        gauges = tuple(GaugeSchedule((a, b)) for a, b in product((1, 2), repeat=2))
        keys = {g.period for g in gauges}
        self.assertEqual(len(keys), 4)
        for a in gauges:
            self.assertEqual(a.compose(a.inverse()).period, (1, 1))
            for b in gauges:
                self.assertIn(a.compose(b).period, keys)
                self.assertEqual(a.compose(b), b.compose(a))

    def test_finite_exhaustive_period_two_operator_audit(self):
        cert = self.audit
        self.assertEqual(cert.status, "CLOSED_GAUGE_GROUP_NOT_ALL_PROCESS_OPERATORS")
        self.assertEqual((cert.period_two_gauges, cert.examined_rule_templates), (4, 81))
        self.assertEqual((cert.all_depth_gauge_witnesses, cert.composition_checks),
                         (4 * 81, 4 * 4 * 81))
        self.assertFalse(cert.shift_descends)
        self.assertFalse(cert.additive_descends)
        self.assertEqual((cert.shift_break_depth, cert.additive_break_depth), (3, 3))

    def test_exact_whole_process_gauge_alignment_exhaustive_finite_states(self):
        processes = (
            PeriodicProcess.repeat(IDENTITY, NEGATIVE),
            PeriodicProcess.repeat(ZERO, (0, 0, 1)),
            PeriodicProcess((IDENTITY, NEGATIVE), (ZERO, IDENTITY)),
        )
        for gauge in (GaugeSchedule((1, 2)), GaugeSchedule((2, 1)),
                      GaugeSchedule((2, 2))):
            for process in processes:
                target = gauge.apply(process)
                for depth in range(3, 8):
                    for state in product(range(3), repeat=depth):
                        mapped = state[:2] + tuple(gauge.scale(i)*state[i+2] % 3
                                                  for i in range(depth-2))
                        for action in "AB":
                            lhs = process.step(state, action)
                            mapped_lhs = lhs[:2] + tuple(gauge.scale(i)*lhs[i+2] % 3
                                                        for i in range(depth-2))
                            self.assertEqual(target.step(mapped, action), mapped_lhs)

    def test_compositions_act_on_stemmed_and_periodic_streams(self):
        processes = (
            PeriodicProcess((IDENTITY, ZERO, NEGATIVE), (IDENTITY,)),
            PeriodicProcess((ZERO,), (NEGATIVE, IDENTITY, ZERO)),
            PeriodicProcess.repeat(IDENTITY, NEGATIVE),
        )
        for process in processes:
            for a, b, c in product((1, 2), repeat=3):
                left, right = GaugeSchedule((a, b, c)), GaugeSchedule((c, a))
                self.assertTrue(same_rule_stream(
                    left.apply(right.apply(process)),
                    left.compose(right).apply(process),
                ))
                self.assertTrue(same_rule_stream(
                    left.apply(left.inverse().apply(process)), process,
                ))

    def test_one_shift_breaks_preexisting_equivalence(self):
        shift, addition = find_operator_breaks()
        self.assertEqual(shift.operation, "shift")
        self.assertEqual((shift.before, shift.after),
                         ("COINDUCTIVE_DIAGONAL_ALIGNMENT", "OPEN_DIAGONAL_ALIGNMENT"))
        p, q = shift.left, shift.right
        self.assertEqual(p.shift(2), p)
        self.assertEqual(q.shift(2), q)
        self.assertEqual(find_process_alignment(p, q).status,
                         "COINDUCTIVE_DIAGONAL_ALIGNMENT")
        self.assertEqual(find_process_alignment(p.shift(1), q.shift(1)).status,
                         "OPEN_DIAGONAL_ALIGNMENT")

    def test_reversible_rule_addition_does_not_descend_to_quotient(self):
        _, addition = find_operator_breaks()
        self.assertEqual((addition.before, addition.after),
                         ("COINDUCTIVE_DIAGONAL_ALIGNMENT", "OPEN_DIAGONAL_ALIGNMENT"))
        op = AddRule(IDENTITY)
        for source in (addition.left, addition.right):
            once = op.apply(source)
            twice = op.apply(once)
            third = op.apply(twice)
            self.assertTrue(same_rule_stream(source, third))
            self.assertFalse(same_rule_stream(source, once))
        self.assertEqual(op.compose(op).compose(op), AddRule(ZERO))

    def test_gauge_preserves_equivalence_even_if_shift_does_not(self):
        shift, _ = find_operator_breaks()
        for scale in ((1, 2), (2, 1), (2, 2)):
            gauge = GaugeSchedule(scale)
            p, q = gauge.apply(shift.left), gauge.apply(shift.right)
            self.assertEqual(find_process_alignment(p, q).status,
                             "COINDUCTIVE_DIAGONAL_ALIGNMENT")

    def test_projections_hold_for_nonidentical_gauged_processes(self):
        p = PeriodicProcess.repeat(IDENTITY, NEGATIVE)
        q = GaugeSchedule((1, 2)).apply(p)
        for state in product(range(3), repeat=6):
            for action in "AB":
                self.assertEqual(q.step(state, action)[:-1],
                                 q.step(state[:-1], action))

    def test_invalid_operators_are_not_admitted(self):
        for bad in ((), (0,), (1, 3), (True, 2)):
            with self.assertRaises(ValueError):
                GaugeSchedule(bad)
        with self.assertRaises(ValueError):
            GaugeSchedule((1, 2)).scale(-1)
        with self.assertRaises(ValueError):
            AddRule((1, 0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
