"""Tests for exact shift-loop certificates over complete construction streams."""
import unittest
from itertools import product

from work.arc_like_maze.process_alignment import (
    IDENTITY, NEGATIVE, NONLINEAR, ZERO, PeriodicProcess, verify_lasso,
)
from work.arc_like_maze.process_family import (
    audit_two_phase_templates, certify_shift_orbit,
)


class ProcessFamilyTests(unittest.TestCase):
    def test_all_period_two_templates_are_exhaustively_partitioned(self):
        result = audit_two_phase_templates()
        self.assertEqual(result.status, "EXACT_PERIOD_TWO_DIAGONAL_CLASSIFICATION")
        self.assertEqual((result.templates, result.process_classes), (81, 34))
        self.assertEqual(result.class_size_distribution, ((1, 1), (2, 26), (4, 7)))

    def test_only_four_nondegenerate_one_turn_shift_loops(self):
        result = audit_two_phase_templates()
        self.assertEqual((result.one_turn_closed, result.changing_one_turn_closed), (13, 4))

    def test_two_different_rules_form_genuine_coinductive_two_turn_loop(self):
        process = PeriodicProcess.repeat(IDENTITY, NEGATIVE)
        witness = certify_shift_orbit(process)
        self.assertEqual(witness.status, "CLOSED_COINDUCTIVE_SHIFT_ORBIT")
        self.assertEqual((witness.distinct_turns, witness.verified_edges), (2, 2))
        self.assertEqual(len(witness.witnesses), 2)
        for turn, cert in enumerate(witness.witnesses):
            self.assertTrue(verify_lasso(process.shift(turn),
                                         process.shift(turn + 1), cert))
            self.assertEqual(cert.status, "COINDUCTIVE_DIAGONAL_ALIGNMENT")
            for depth in range(3, 7):
                before, after = process.shift(turn), process.shift(turn+1)
                for state in product(range(3),repeat=depth):
                    mapped=cert.map_state(state)
                    for action in "AB":
                        self.assertEqual(cert.map_state(before.step(state,action)),
                                         after.step(mapped,action))

    def test_not_every_two_turn_process_closes(self):
        process=PeriodicProcess.repeat(IDENTITY,NONLINEAR)
        outcome=certify_shift_orbit(process)
        self.assertEqual(outcome.status,"OPEN_SHIFT_ORBIT")
        self.assertEqual((outcome.failure_turn,outcome.failure_coordinate_depth),(0,3))

    def test_vacuously_constant_rule_is_not_called_changing(self):
        process=PeriodicProcess.repeat(ZERO,ZERO)
        result=certify_shift_orbit(process)
        self.assertEqual((result.status,result.distinct_turns,result.verified_edges),
                         ("CLOSED_COINDUCTIVE_SHIFT_ORBIT",1,1))

    def test_redundant_period_reduces_to_actual_orbit(self):
        process=PeriodicProcess.repeat(IDENTITY,NEGATIVE,IDENTITY,NEGATIVE)
        result=certify_shift_orbit(process)
        self.assertEqual(result.status,"CLOSED_COINDUCTIVE_SHIFT_ORBIT")
        self.assertEqual(result.distinct_turns,2)

    def test_finite_stem_is_not_silently_declared_cyclic(self):
        process=PeriodicProcess((IDENTITY,),(IDENTITY,NEGATIVE))
        status=certify_shift_orbit(process)
        self.assertEqual(status.status,"UNKNOWN_NONCYCLIC_STEM")

if __name__=="__main__":
    unittest.main(verbosity=2)
