"""Equal-trial policy comparison with actual edge and goal replay."""
import unittest
from dataclasses import replace
from ab_chatbot_policy_benchmark import (
    run_once, compare, adoption_gate, summarize, DEFAULT_CASES)

class PolicyBenchmarkTests(unittest.TestCase):
    def test_equal_budget_control_replays_owner_edges(self):
        old,new,goals=DEFAULT_CASES[0]
        for guided in (False,True):
            r=run_once(old,new,goals,budget=2,guided=guided)
            self.assertTrue(r.replay_verified)
            self.assertEqual(r.trials,2)
            self.assertEqual(r.completed,2)
            self.assertEqual(r.observed_old,54)
            self.assertEqual(r.observed_new,54)
            self.assertTrue(r.candidate_pool_truncated)

    def test_nonimproving_guidance_remains_opt_in(self):
        old,new,goals=DEFAULT_CASES[0]
        pairs=compare(((old,new,goals),),budgets=(3,4))
        self.assertEqual(len(pairs),2)
        self.assertEqual([(f.admitted,g.admitted) for f,g in pairs],[(41,41),(42,41)])
        report=adoption_gate(pairs)
        self.assertEqual(report['decision'],'KEEP_FIXED_DEFAULT')
        self.assertEqual(report['summary']['edge_admissions'],
                         {'fixed':1,'guided':0,'tie':1})

    def test_cost_difference_reported_when_goals_tie(self):
        pair=compare((DEFAULT_CASES[3],),budgets=(3,))[0]
        fixed,guided=pair
        self.assertEqual((fixed.completed,guided.completed),(2,2))
        self.assertEqual((fixed.admitted,guided.admitted),(13,13))
        self.assertEqual((fixed.observed_old,guided.observed_old),(26,28))
        self.assertEqual(summarize((pair,))['observation_cost']['fixed'],1)

    def test_budget_validation(self):
        with self.assertRaises(ValueError):
            run_once(*DEFAULT_CASES[0],budget=True,guided=True)
        with self.assertRaises(ValueError):
            adoption_gate(())

if __name__=='__main__':unittest.main()
