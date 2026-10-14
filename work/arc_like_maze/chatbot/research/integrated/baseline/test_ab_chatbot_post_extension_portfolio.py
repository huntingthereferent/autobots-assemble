"""Bounded downstream comparison; independent finite replay and invalidation controls."""
import unittest

from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
from test_ab_chatbot_path_union import PathUnionTests

GOALS = ((0,1,1),(0,2,0))

class PostExtensionPortfolioTests(unittest.TestCase):
    def build(self, right=(0,0,0), *, goals=GOALS, remote=False, depth=6,
              limit=6, finish=True):
        fixture=PathUnionTests()
        self.addCleanup(fixture.doCleanups)
        _,old,new,_,owner=fixture.make((0,0,1),right,depth=0,
                                       remote_new=remote,budget=54)
        bot=PostExtensionPortfolio(old,new,goals,max_depth=depth,
                                   candidate_limit=5,max_trials=limit)
        if finish:
            for _ in range(80):
                report=bot.advance(max_new_edges=108)
                if report.status not in ('SEARCHING','EVALUATING'):
                    break
            else:self.fail('no bounded terminal report')
        return bot,old,new,owner

    def test_competing_extensions_preserve_joint_goals(self):
        bot,*_=self.build()
        result=bot.advance(max_new_edges=0)
        self.assertEqual(result.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((result.evaluated,result.candidates),(6,6))
        self.assertEqual(result.selected.words,('ABAA','ABBABA'))
        self.assertEqual((result.selected.paired_states,result.selected.admitted_edges,
                          result.selected.excluded_edges),(9,13,5))
        self.assertEqual(len(result.selected.carried),2)
        self.assertTrue(any(len(t.carried)==1 for t in result.trials))
        self.assertTrue(result.candidate_cap_reached)

    def test_downstream_selection_beats_seed_only_edge_coverage(self):
        from ab_chatbot_seed_first_extension import SeedFirstGoalExtender
        goals=((0,1,0),(0,1,1))
        fixture=PathUnionTests()
        self.addCleanup(fixture.doCleanups)
        _,old,new,*_=fixture.make((0,0,1),(1,0,1),depth=0,budget=54)
        earlier=SeedFirstGoalExtender(old,new,goals,max_depth=6,
                                       variants_per_goal=3,max_candidates=5)
        for _ in range(50):
            previous=earlier.advance(max_new_edges=108)
            if previous.status not in ('SEARCHING','EXTENDING'):break
        self.assertEqual(previous.status,'GOALS_CARRIED_WITNESSED')
        later=PostExtensionPortfolio(old,new,goals,max_depth=6,
                                      variants_per_goal=3,candidate_limit=5,max_trials=6)
        for _ in range(50):
            outcome=later.advance(max_new_edges=108)
            if outcome.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(outcome.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((previous.admitted_edges,outcome.selected.admitted_edges),(40,42))
        self.assertEqual(len(outcome.selected.carried),2)
        self.assertNotEqual(previous.selected_paths,outcome.selected.words)
        a,b=FiniteSystem((0,0,1)),FiniteSystem((1,0,1))
        for goal,image,word in outcome.selected.carried:
            self.assertEqual((a.follow(word),b.follow(word)),(goal,image))

    def test_all_reported_paths_replay_in_independent_laws(self):
        for phi in ((0,0,0),(1,0,1),(0,0,1)):
            with self.subTest(phi=phi):
                bot,*_=self.build(right=phi,limit=4)
                r=bot.advance(max_new_edges=0)
                self.assertIn(r.status,('GOALS_CARRIED_WITNESSED','PARTIAL_GOALS_WITNESSED'))
                a,b=FiniteSystem((0,0,1)),FiniteSystem(phi)
                for trial in r.trials:
                    self.assertGreater(trial.admitted_edges,0)
                    for goal,image,word in trial.carried:
                        self.assertEqual((a.follow(word),b.follow(word)),(goal,image))
                self.assertEqual(len(r.selected.carried),max(len(x.carried) for x in r.trials))

    def test_identical_law_is_closed(self):
        bot,*_=self.build(right=(0,0,1),limit=3)
        r=bot.advance(max_new_edges=0)
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((r.selected.paired_states,r.selected.admitted_edges,
                          r.selected.excluded_edges),(27,54,0))

    def test_remote_does_not_upgrade_provenance(self):
        bot,*_=self.build(remote=True,limit=2)
        self.assertEqual(bot.advance(max_new_edges=0).status,'GOALS_CARRIED_REMOTE_REPORTED')

    def test_repin_refuses_prior_success(self):
        bot,old,new,owner=self.build()
        owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        new.ask('pin current version')
        r=bot.advance(max_new_edges=0)
        self.assertEqual(r.status,'UNKNOWN_VERSION')
        self.assertIsNone(r.selected)
        self.assertFalse(r.trials)

    def test_cache_tamper_refuses_prior_success(self):
        bot,old,new,_=self.build()
        s,a,t,_,_=bot._extenders[0].edges[next(iter(bot._extenders[0].edges))]
        old.snapshot.edges[(s,a)]=(2,2,2) if t!=(2,2,2) else (0,0,0)
        r=bot.advance(max_new_edges=0)
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertIsNone(r.selected)
        self.assertFalse(r.trials)

    def test_resumable_with_small_budgets(self):
        bot,*_=self.build(finish=False,limit=2)
        r=bot.advance(max_new_edges=0)
        self.assertIn(r.status,('SEARCHING','EVALUATING'))
        for _ in range(400):
            r=bot.advance(max_new_edges=2)
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(len(r.trials),2)

    def test_path_limit_only_is_not_global_impossibility(self):
        bot,*_=self.build(depth=0,finish=False)
        r=bot.advance(max_new_edges=108)
        self.assertEqual(r.status,'GOALS_OUTSIDE_SEARCH_BOUND')

    def test_limits(self):
        bot,old,new,_=self.build(finish=False)
        for goals in ((),(GOALS[0],GOALS[0]),((3,0,0),)):
            with self.assertRaises(ValueError):PostExtensionPortfolio(old,new,goals)
        for k in ('max_depth','variants_per_goal','candidate_limit','max_trials'):
            with self.subTest(key=k):
                with self.assertRaises(ValueError):PostExtensionPortfolio(old,new,GOALS,**{k:True})
        for n in (-1,109,True):
            with self.assertRaises(ValueError):bot.advance(max_new_edges=n)

if __name__=='__main__':unittest.main()
