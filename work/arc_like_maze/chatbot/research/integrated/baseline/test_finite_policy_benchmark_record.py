import unittest
from finite_policy_benchmark_record import CASE_LAWS,CASE_GOALS,ROWS,counts,gate,replay_negative_controls

class FinitePolicyRecordTests(unittest.TestCase):
    def test_declared_fully_paired_matrix(self):
        self.assertEqual(len(ROWS),18)
        self.assertEqual(len(CASE_LAWS),len(CASE_GOALS))
        self.assertEqual({(b,c) for b,c,*_ in ROWS},
                         {(budget,case) for budget in (2,3,4) for case in range(6)})

    def test_reported_totals_recomputed_from_rows(self):
        result=counts()
        self.assertEqual(result['goal_ties'],18)
        self.assertEqual(result['edge_fixed_wins'],1)
        self.assertEqual(result['edge_guided_wins'],0)
        self.assertEqual(result['observation_fixed_wins'],2)
        self.assertEqual(result['observation_guided_wins'],0)
        self.assertEqual((result['fixed_reads'],result['guided_reads']),(1422,1426))
        self.assertEqual(result['guided_attempts'],12)
        self.assertEqual(gate(),'KEEP_FIXED_DEFAULT')

    def test_finite_goal_words_independent_replay(self):
        self.assertTrue(replay_negative_controls())

if __name__=='__main__': unittest.main()
