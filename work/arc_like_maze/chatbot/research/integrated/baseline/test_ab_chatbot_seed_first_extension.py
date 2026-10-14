"""Independent finite-law witnesses and failure controls for seed-first coupling."""
import unittest

from ab_chatbot_seed_first_extension import SeedFirstGoalExtender
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
import test_ab_chatbot_path_union as fixtures

GOALS = ((0,1,0), (0,1,1))

class SeedFirstTests(unittest.TestCase):
    def build(self, right=(1,0,1), *, remote=False, budget=54,
              goals=GOALS, depth=6, finish=True):
        fixture = fixtures.PathUnionTests()
        self.addCleanup(fixture.doCleanups)
        _, old, new, _, owner = fixture.make((0,0,1), right, depth=0,
                                             budget=budget, remote_new=remote)
        bot = SeedFirstGoalExtender(old, new, goals, max_depth=depth)
        if finish:
            for _ in range(200):
                report = bot.advance(max_new_edges=108)
                if report.status not in ('SEARCHING','EXTENDING'):
                    break
            else:
                self.fail('seed-first agent did not reach an explicit terminal status')
        return bot, old, new, owner

    def test_joint_goal_before_extension(self):
        bot, old, new, _ = self.build()
        r = bot.advance(max_new_edges=0)
        self.assertEqual(r.status, 'GOALS_CARRIED_WITNESSED')
        self.assertEqual(len(r.carried_goals), 2)
        self.assertEqual((r.paired_states,r.admitted_edges,r.excluded_edges), (27,41,13))
        self.assertGreaterEqual(len(r.selected_paths), 2)
        self.assertEqual(len(bot.last_union.selected.carried_goals), 2)
        self.assertTrue(all(g in dict(bot.last_extension.state_pairs) for g in GOALS))

    def test_seed_first_recovers_joint_goals_after_completed_first_collision(self):
        from ab_chatbot_backtracked_extension import BacktrackedGoalExtender
        from ab_chatbot_extension_portfolio import CompletedExtensionPortfolio
        fixture = fixtures.PathUnionTests()
        self.addCleanup(fixture.doCleanups)
        _, old, new, *_ = fixture.make((0,0,1), (0,0,0), depth=0, budget=54)
        goals=((0,1,1),(0,2,0))
        individually=[]
        for goal in goals:
            candidate=BacktrackedGoalExtender(old,new,goal,max_depth=6)
            for _ in range(100):
                result=candidate.advance(max_new_edges=108)
                if result.status not in ('SEARCHING','EXTENDING'):
                    break
            self.assertEqual(result.status,'GOAL_CARRIED_WITNESSED')
            individually.append(candidate)
        old_portfolio=CompletedExtensionPortfolio(tuple(individually),goals).run()
        self.assertEqual(old_portfolio.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(len(old_portfolio.selected.carried_goals),1)
        self.assertEqual(len(old_portfolio.conflicts),1)
        joint=SeedFirstGoalExtender(old,new,goals)
        for _ in range(100):
            report=joint.advance(max_new_edges=108)
            if report.status not in ('SEARCHING','EXTENDING'):
                break
        self.assertEqual(report.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((report.paired_states,report.admitted_edges,report.excluded_edges),(9,13,5))
        self.assertEqual(report.selected_paths,('ABAA','ABBABA'))
        self.assertEqual(report.carried_goals,
            (((0,1,1),(0,1,0),'ABBABA'),((0,2,0),(0,2,0),'ABAA')))

    def test_unchanged_finite_law_has_full_closure(self):
        bot,*_=self.build(right=(0,0,1))
        r=bot.advance(max_new_edges=0)
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((r.paired_states,r.admitted_edges,r.excluded_edges),(27,54,0))

    def test_incompatible_pair_never_fakes_joint_goal(self):
        bot, old, new, _=self.build(right=(0,0,0))
        r=bot.advance(max_new_edges=0)
        self.assertEqual(r.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual([g for g,_,_ in r.carried_goals], [GOALS[0]])
        self.assertGreater(r.path_conflicts,0)
        self.assertEqual((r.paired_states,r.admitted_edges,r.excluded_edges),(9,15,3))

    def test_independent_replay_all_admitted_and_rejected(self):
        for right in ((1,0,1),(0,0,0),(0,0,1)):
            with self.subTest(right=right):
                bot,*_=self.build(right=right)
                r=bot.advance(max_new_edges=0)
                forward=dict(bot.last_extension.state_pairs)
                a,b=FiniteSystem((0,0,1)),FiniteSystem(right)
                self.assertEqual(len(forward),len(set(forward.values())))
                for state,action,target,image,new_target in bot.last_extension.admitted_edges:
                    self.assertEqual(forward[state],image)
                    self.assertEqual(forward[target],new_target)
                    self.assertEqual(a.step(state,action),target)
                    self.assertEqual(b.step(image,action),new_target)
                for rejection in bot.last_extension.rejected:
                    witness=rejection.witness
                    self.assertEqual(witness.old_equal,
                                     a.follow(witness.left_word)==a.follow(witness.right_word))
                    self.assertEqual(witness.new_equal,
                                     b.follow(witness.left_word)==b.follow(witness.right_word))
                    self.assertNotEqual(witness.old_equal,witness.new_equal)
                for goal,image,word in r.carried_goals:
                    self.assertEqual(a.follow(word),goal)
                    self.assertEqual(b.follow(word),image)

    def test_no_new_observations_after_completion(self):
        bot,old,new,_=self.build()
        before=(dict(old.snapshot.edges),dict(new.snapshot.edges))
        r=bot.advance(max_new_edges=0)
        self.assertEqual(bot.advance(max_new_edges=0),r)
        self.assertEqual((old.snapshot.edges,new.snapshot.edges),before)

    def test_repin_invalidates_completed_result(self):
        bot,old,new,owner=self.build()
        owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        new.ask('pin current version')
        self.assertEqual(bot.advance(max_new_edges=0).status,'UNKNOWN_VERSION')

    def test_forged_retained_cache_breaks_replay(self):
        bot,old,new,_=self.build()
        s,a,t,_,_=bot.last_extension.admitted_edges[0]
        old.snapshot.edges[(s,a)] = (2,2,2) if t!=(2,2,2) else (0,0,0)
        self.assertEqual(bot.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_remote_is_not_upgraded(self):
        bot,*_=self.build(remote=True)
        self.assertEqual(bot.advance(max_new_edges=0).status,'GOALS_CARRIED_REMOTE_REPORTED')

    def test_budget_resumes_without_fabricated_completion(self):
        bot,old,new,_=self.build(finish=False)
        r=bot.advance(max_new_edges=0)
        self.assertIn(r.status,('SEARCHING','EXTENDING'))
        for _ in range(300):
            r=bot.advance(max_new_edges=2)
            if r.status not in ('SEARCHING','EXTENDING'):
                break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')

    def test_wrong_input_limits(self):
        bot,old,new,_=self.build(finish=False)
        for goals in ((),(GOALS[0],GOALS[0]),((9,9,9),)):
            with self.assertRaises(ValueError):
                SeedFirstGoalExtender(old,new,goals)
        for params in ({'max_depth':9}, {'max_depth':True},
                       {'variants_per_goal':0}, {'max_candidates':17},
                       {'action_order':'AA'}):
            with self.assertRaises(ValueError):
                SeedFirstGoalExtender(old,new,GOALS,**params)
        for limit in (-1,109,True):
            with self.assertRaises(ValueError):
                bot.advance(max_new_edges=limit)

    def test_search_limit_not_global_no_solution(self):
        bot,*_=self.build(depth=0, finish=False)
        r=bot.advance(max_new_edges=0)
        self.assertEqual(r.status,'GOALS_OUTSIDE_SEARCH_BOUND')

if __name__=='__main__': unittest.main()
