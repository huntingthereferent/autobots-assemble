"""Finite owner-law checks for downstream seed-union ranking."""
import unittest
from finite_goal_priority import Law
from finite_seed_first import select_and_extend
from finite_post_extension_portfolio import compare

class PostExtensionFiniteTests(unittest.TestCase):
    def test_ranking_changes_after_extension(self):
        a,b=Law((0,0,1)),Law((1,0,1))
        goals=((0,1,0),(0,1,1))
        previous=select_and_extend(a,b,goals,variants=3,limit=5)
        post=compare(a,b,goals)
        self.assertEqual(previous['status'],'GOALS_CARRIED')
        self.assertEqual(post['status'],'GOALS_CARRIED')
        self.assertEqual((len(previous['edges']),post['best'][3]),(40,42))
        self.assertNotEqual(previous['paths'],post['best'][0])
        self.assertEqual(len(post['best'][1]),2)
        self.assertTrue(post['candidate_cap_reached'])

    def test_continuity_over_three_rule_pairs(self):
        old=Law((0,0,1))
        for phi,goals in [((0,0,0),((0,1,1),(0,2,0))),
                          ((1,0,1),((0,1,0),(0,1,1))),
                          ((0,0,1),((0,1,0),(0,1,1)))]:
            b=Law(phi)
            r=compare(old,b,goals,trial_limit=6)
            self.assertEqual(r['status'],'GOALS_CARRIED')
            for words,carried,states,edges,excluded in r['trials']:
                self.assertGreater(states,0)
                self.assertEqual(edges+excluded,2*states)
                for goal,image,word in carried:
                    self.assertEqual((old.follow(word),b.follow(word)),(goal,image))

    def test_partial_not_promoted(self):
        r=compare(Law((0,0,1)),Law((0,0,0)),((0,1,0),(0,1,1)))
        self.assertEqual(r['status'],'PARTIAL_GOALS')
        self.assertEqual(len(r['best'][1]),1)

    def test_bounded_and_invalid_inputs(self):
        a=Law((0,0,1))
        r=compare(a,a,((0,1,1),),depth=0)
        self.assertEqual(r['status'],'GOALS_OUTSIDE_SEARCH_BOUND')
        for goals in ((),((0,1,1),(0,1,1)),((3,0,0),)):
            with self.assertRaises(ValueError):compare(a,a,goals)
        for k in ('depth','variants','pool_limit','trial_limit'):
            with self.assertRaises(ValueError):compare(a,a,((0,1,1),),**{k:True})

if __name__=='__main__':unittest.main()
