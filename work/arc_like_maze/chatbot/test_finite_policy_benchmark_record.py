"""Checks against retained benchmark summary, not a new integrated rerun."""
import unittest
from finite_policy_benchmark_record import (
    CASE_LAWS,CASE_GOALS,ROWS,counts,gate,replay_negative_controls)

class BenchmarkRecordChecks(unittest.TestCase):
    def test_matrix_complete(self):
        self.assertEqual(len(ROWS),18)
        self.assertEqual(len(CASE_LAWS),len(CASE_GOALS))
        self.assertEqual({(b,c) for b,c,*_ in ROWS},
                         {(budget,case) for budget in (2,3,4) for case in range(6)})

    def test_recorded_totals(self):
        r=counts()
        self.assertEqual(r['goal_ties'],18)
        self.assertEqual((r['edge_fixed_wins'],r['edge_guided_wins']),(1,0))
        self.assertEqual((r['observation_fixed_wins'],r['observation_guided_wins']),(2,0))
        self.assertEqual((r['fixed_reads'],r['guided_reads']),(1422,1426))
        self.assertEqual(r['guided_attempts'],12)
        self.assertEqual(gate(),'KEEP_FIXED_DEFAULT')

    def test_example_goal_paths(self):
        self.assertTrue(replay_negative_controls())

if __name__=='__main__': unittest.main()
