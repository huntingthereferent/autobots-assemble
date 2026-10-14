"""Watches actual rejected edges become admitted by independently replayed alternatives."""
import unittest
from ab_chatbot_conflict_guided import ConflictGuidedPortfolio
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
import test_ab_chatbot_path_union as fixture_module

class GuidedTests(unittest.TestCase):
    def fixture(self,right=(1,0,1),*,remote=False,goals=((0,1,0),(0,1,1)),
                trial_budget=3, finish=True, **extra):
        f=fixture_module.PathUnionTests()
        self.addCleanup(f.doCleanups)
        _,old,new,_,owner=f.make((0,0,1),right,depth=0,remote_new=remote,budget=54)
        bot=ConflictGuidedPortfolio(old,new,goals,trial_budget=trial_budget,
              candidate_pool_limit=12,max_depth=6,variants_per_goal=4,
              candidate_limit=7,**extra)
        if finish:
            for _ in range(70):
                report=bot.advance(max_new_edges=108)
                if report.status not in ('SEARCHING','EVALUATING'):break
            else:self.fail('did not terminate under test budget')
        else:report=None
        return bot,report,old,new,owner

    def test_conflict_has_independently_replayed_alternative(self):
        bot,r,_,_,_=self.fixture(trial_budget=3)
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertGreaterEqual(len(r.attempts),1)
        repaired=[a for a in r.attempts if a.outcome=='ALTERNATIVE_REPLAY_ADMITS_EDGE']
        self.assertTrue(repaired)
        old,new=FiniteSystem((0,0,1)),FiniteSystem((1,0,1))
        for a in repaired:
            self.assertEqual(old.step(a.old_source,a.action),a.old_target)
            self.assertEqual(new.step(a.prior_new_source,a.action),a.prior_new_target)
            self.assertEqual(new.step(a.alternative_new_source,a.action),a.alternative_new_target)
            if a.cause=='SOURCE_COLLISION':
                self.assertIsNotNone(a.prior_assigned_target_image)
                self.assertNotEqual(a.prior_assigned_target_image, a.prior_new_target)
                self.assertEqual(a.alternative_assigned_target_image, a.alternative_new_target)
            self.assertNotEqual(old.follow(a.left_word)==old.follow(a.right_word),
                                new.follow(a.left_word)==new.follow(a.right_word))
        self.assertEqual(r.chosen_trials,3)
        self.assertTrue(r.remaining_candidates_not_tested)

    def test_no_conflict_falls_back_without_repair(self):
        bot,r,*_=self.fixture(right=(0,0,1),trial_budget=2)
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertFalse(r.attempts)
        self.assertEqual((r.portfolio.selected.paired_states,
                          r.portfolio.selected.admitted_edges),(27,54))

    def test_ongoing_finite_failure_stays_partial(self):
        bot,r,*_=self.fixture(right=(0,0,0),goals=((0,1,0),(0,1,1)),trial_budget=3)
        self.assertEqual(r.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(len(r.portfolio.selected.carried),1)

    def test_remote_status_does_not_get_promoted(self):
        bot,r,*_=self.fixture(remote=True,trial_budget=2)
        self.assertEqual(r.status,'GOALS_CARRIED_REMOTE_REPORTED')

    def test_version_change_revokes_success_and_attempts(self):
        bot,r,old,new,owner=self.fixture(trial_budget=3)
        self.assertTrue(r.attempts)
        owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        new.ask('pin current version')
        newer=bot.advance(max_new_edges=0)
        self.assertEqual(newer.status,'UNKNOWN_VERSION')
        self.assertFalse(newer.attempts)
        self.assertIsNone(newer.portfolio.selected)

    def test_cache_forgery_revokes_reported_repair(self):
        bot,r,old,new,owner=self.fixture(trial_budget=3)
        e=bot._extenders[1]
        s,a,t,_,_=next(iter(e.edges.values()))
        old.snapshot.edges[(s,a)]=(2,2,2) if t!=(2,2,2) else (0,0,0)
        changed=bot.advance(max_new_edges=0)
        self.assertEqual(changed.status,'WALL_OBSERVATION')
        self.assertFalse(changed.attempts)

    def test_resume_and_bound(self):
        bot,_,*_=self.fixture(trial_budget=2,finish=False)
        report=bot.advance(max_new_edges=0)
        self.assertIn(report.status,('SEARCHING','EVALUATING'))
        for _ in range(400):
            report=bot.advance(max_new_edges=2)
            if report.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(report.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(report.chosen_trials,2)

    def test_heuristic_not_guaranteed_to_beat_fixed_order(self):
        bot,r,*_=self.fixture(trial_budget=4)
        baseline_fixture=fixture_module.PathUnionTests()
        self.addCleanup(baseline_fixture.doCleanups)
        _,old,new,*_=baseline_fixture.make((0,0,1),(1,0,1),depth=0,budget=54)
        fixed=PostExtensionPortfolio(old,new,((0,1,0),(0,1,1)),
            max_depth=6,variants_per_goal=4,candidate_limit=7,max_trials=4)
        for _ in range(70):
            base=fixed.advance(max_new_edges=108)
            if base.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(base.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(r.status,base.status)
        self.assertEqual(len(r.portfolio.selected.carried),2)
        self.assertEqual((base.selected.admitted_edges,r.portfolio.selected.admitted_edges),(42,41))

    def test_observations_are_not_guessed(self):
        bot,r,old,new,_=self.fixture(trial_budget=3)
        self.assertEqual((r.portfolio.observed_old,r.portfolio.observed_new),(54,54))
        for a in r.attempts:
            if a.outcome=='ALTERNATIVE_REPLAY_ADMITS_EDGE':
                self.assertEqual(a.alternative_assigned_target_image,a.alternative_new_target)
                self.assertNotEqual(a.prior_assigned_target_image,a.prior_new_target)

    def test_safety_limits(self):
        bot,report,old,new,owner=self.fixture(trial_budget=2)
        for kwargs in ({'trial_budget':0},{'trial_budget':True},
                       {'candidate_pool_limit':0},{'trial_budget':5,'candidate_pool_limit':2}):
            with self.assertRaises(ValueError):
                ConflictGuidedPortfolio(old,new,((0,1,0),),**kwargs)
        for k in (-1,109,True):
            with self.assertRaises(ValueError):bot.advance(max_new_edges=k)

if __name__=='__main__':unittest.main()
