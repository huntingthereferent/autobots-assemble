"""Independent controls for partial transport through a changed finite law."""
import unittest
from dataclasses import replace

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_goal_agent import GoalAgent
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge, PathWitness
from ab_chatbot_restricted_rule_transport import RestrictedRuleTransport
from ab_chatbot_rule_change import _cached_path
from ab_chatbot_stability_witness import TransportedLaw

IDENT = tuple(DOMAIN)


class RestrictedRuleTransportTests(unittest.TestCase):
    def make(self, *, old_phi=(0, 0, 0), new_phi=(0, 1, 2),
             old_map=IDENT, new_map=IDENT, budget=54, remote_new=False,
             old_root=(0, 0, 0), new_root=(0, 0, 0)):
        a = SourceOwnedHTTP(TransportedLaw(old_phi, old_map))
        b = SourceOwnedHTTP(TransportedLaw(new_phi, new_map))
        sa, sb = LoopbackHTTP(a), LoopbackHTTP(b)
        sa.__enter__()
        sb.__enter__()
        self.addCleanup(sb.__exit__, None, None, None)
        self.addCleanup(sa.__exit__, None, None, None)
        aa = LanguageBridge(RemoteObserver(sa.url, bound_loopback=sa),
                            owner=a, edge_budget=budget)
        bb = LanguageBridge(RemoteObserver(sb.url, bound_loopback=None if remote_new else sb),
                            owner=b if not remote_new else None, edge_budget=budget)
        agent = RestrictedRuleTransport(aa, bb, old_root=old_root, new_root=new_root)
        return agent, aa, bb, a, b

    @staticmethod
    def finish(agent, *, per_call=3):
        for _ in range(150):
            r = agent.advance(max_new_edges=per_call)
            if r.status != 'CONTINUING':
                return r
        raise AssertionError('no result after 150 bounded observations')

    @staticmethod
    def reach_goal(bridge, target):
        task = GoalAgent(bridge, target)
        for _ in range(150):
            r = task.advance(max_new_edges=3)
            if r.status != 'CONTINUING':
                return r
        raise AssertionError('goal not resolved')

    def test_bounded_changed_law_admits_reuses_and_excludes(self):
        ag, old, new, *_ = self.make()
        r = self.finish(ag)
        self.assertEqual(r.status, 'RESTRICTED_SUBGRAPH_WITNESSED')
        self.assertEqual((len(r.state_pairs), len(r.admitted), len(r.excluded)), (9, 12, 6))
        self.assertEqual((r.old_observed_edges, r.new_observed_edges), (18, 18))
        self.assertTrue(all(x.obstruction.old_equal != x.obstruction.new_equal for x in r.excluded))
        # It is a partial graph isomorphism, not two-generator closure.
        mapping = dict(r.state_pairs)
        for s, a, u, v in r.admitted:
            self.assertEqual(mapping[u], v)
            self.assertEqual(old.snapshot.edges[(s, a)], u)
            self.assertEqual(new.snapshot.edges[(mapping[s], a)], v)
        self.assertTrue(all((x.from_old, x.action) not in ag.admitted for x in r.excluded))
        before = (len(old.snapshot.edges), len(new.snapshot.edges))
        carried = ag.carry_target((0, 2, 0))
        self.assertEqual(carried.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual(carried.original_path.word, 'BB')
        self.assertEqual(carried.changed_path.word, 'BB')
        self.assertEqual(carried.target_image, (0, 2, 1))
        self.assertEqual(ag.admitted[((0, 2, 0), 'B')], ((0, 0, 0), (0, 0, 0)))
        self.assertEqual(before, (len(old.snapshot.edges), len(new.snapshot.edges)))
        self.assertEqual(self.finish(ag).status, r.status)

    def test_actual_completed_goal_transports_without_new_reads(self):
        ag, old, new, *_ = self.make()
        self.finish(ag)
        completed = self.reach_goal(old, (0, 2, 0))
        self.assertEqual(completed.status, 'COMPLETE_WITNESSED')
        before = (len(old.snapshot.edges), len(new.snapshot.edges))
        result = ag.carry_prior_goal(completed)
        self.assertEqual(result.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual(result.changed_path.word, 'BB')
        self.assertEqual(before, (len(old.snapshot.edges), len(new.snapshot.edges)))

    def test_replans_prior_valid_path_crossing_an_excluded_arc(self):
        ag, old, new, *_ = self.make()
        self.finish(ag)
        completed = self.reach_goal(old, (1, 1, 0))
        self.assertEqual(completed.path.word, 'BA')
        # ABB is a second *legitimate original-law path* to the same goal,
        # but its changed-law path would land at a different endpoint.
        old_abb = _cached_path(old, (0, 0, 0), 'ABB')
        new_abb = _cached_path(new, (0, 0, 0), 'ABB')
        self.assertEqual(old_abb.states[-1], (1, 1, 0))
        self.assertEqual(new_abb.states[-1], (1, 1, 2))
        alternative = replace(completed, path=old_abb)
        carried = ag.carry_prior_goal(alternative)
        self.assertEqual(carried.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual(carried.original_path.word, 'BA')
        self.assertEqual(carried.changed_path.states[-1], (1, 1, 0))
        self.assertNotEqual(carried.changed_path.states[-1], new_abb.states[-1])

    def test_goals_outside_partial_graph_not_declared_globally_unreachable(self):
        ag, *_ = self.make()
        self.finish(ag)
        r = ag.carry_target((0, 0, 1))
        self.assertEqual(r.status, 'GOAL_OUTSIDE_RESTRICTION')
        self.assertIsNone(r.changed_path)

    def test_zero_and_incremental_budget_never_overread(self):
        ag, old, new, *_ = self.make()
        r = ag.advance(max_new_edges=0)
        self.assertEqual(r.status, 'CONTINUING')
        self.assertEqual((len(old.snapshot.edges), len(new.snapshot.edges)), (0, 0))
        self.assertEqual(ag.carry_target((0, 0, 0)).status, 'UNKNOWN_NOT_CERTIFIED')
        for _ in range(120):
            before = len(old.snapshot.edges) + len(new.snapshot.edges)
            r = ag.advance(max_new_edges=1)
            after = len(old.snapshot.edges) + len(new.snapshot.edges)
            self.assertLessEqual(after - before, 1)
            if r.status != 'CONTINUING':
                break
        self.assertEqual(r.status, 'RESTRICTED_SUBGRAPH_WITNESSED')
        self.assertEqual(len(old.snapshot.edges) + len(new.snapshot.edges), 36)

    def test_underlying_budget_stops_and_can_be_explicitly_extended(self):
        ag, old, new, *_ = self.make(budget=4)
        r = self.finish(ag)
        self.assertEqual(r.status, 'UNKNOWN_BUDGET')
        self.assertEqual((old.snapshot.max_edges, new.snapshot.max_edges), (4, 4))
        self.assertEqual(ag.carry_target((0, 2, 0)).status, 'UNKNOWN_NOT_CERTIFIED')
        old.snapshot.max_edges = 54
        new.snapshot.max_edges = 54
        self.assertEqual(self.finish(ag).status, 'RESTRICTED_SUBGRAPH_WITNESSED')

    def test_forged_admitted_cache_invalidates_completion(self):
        ag, old, *_ = self.make()
        self.finish(ag)
        old.snapshot.edges[((0, 0, 0), 'A')] = (2, 2, 2)
        self.assertEqual(ag.carry_target((0, 2, 0)).status, 'WALL_OBSERVATION')
        self.assertEqual(ag.advance(max_new_edges=0).status, 'WALL_OBSERVATION')

    def test_forged_excluded_cache_invalidates_rejection_witness(self):
        ag, old, *_ = self.make()
        r = self.finish(ag)
        self.assertGreater(len(r.excluded), 0)
        excluded = r.excluded[0]
        old.snapshot.edges[(excluded.from_old, excluded.action)] = (2, 2, 2)
        self.assertEqual(ag.carry_target((0, 2, 0)).status, 'WALL_OBSERVATION')
        self.assertEqual(ag.advance(max_new_edges=0).status, 'WALL_OBSERVATION')

    def test_version_repin_invalidates_reuse(self):
        ag, old, new, _, owner_new = self.make()
        self.finish(ag)
        owner_new.replace(TransportedLaw((1, 1, 1), IDENT))
        new.ask('pin current version')
        self.assertEqual(ag.carry_target((0, 2, 0)).status, 'UNKNOWN_VERSION')
        self.assertEqual(ag.advance().status, 'UNKNOWN_VERSION')

    def test_remote_observation_never_marked_locally_verified(self):
        ag, *_ = self.make(remote_new=True)
        r = self.finish(ag)
        self.assertEqual(r.status, 'RESTRICTED_SUBGRAPH_REMOTE_REPORTED')
        self.assertEqual(ag.carry_target((0, 2, 0)).status, 'GOAL_CARRIED_REMOTE_REPORTED')

    def test_identical_law_observes_closed_rooted_graph(self):
        ag, *_ = self.make(new_phi=(0, 0, 0))
        r = self.finish(ag)
        self.assertEqual(r.status, 'ROOTED_PRESERVED_WITNESSED')
        self.assertEqual((len(r.state_pairs), len(r.admitted), len(r.excluded)), (9, 18, 0))

    def test_relabeling_never_triggers_spurious_exclusion(self):
        shear = tuple((i, j, (k + i * j) % 3) for i, j, k in DOMAIN)
        ag, *_ = self.make(new_phi=(0, 0, 0), new_map=shear)
        r = self.finish(ag)
        self.assertEqual(r.status, 'ROOTED_PRESERVED_WITNESSED')
        self.assertEqual((len(r.state_pairs), len(r.admitted), len(r.excluded)), (9, 18, 0))

    def test_reversed_rule_change_retains_replayable_rejections(self):
        ag, *_ = self.make(old_phi=(0, 1, 2), new_phi=(0, 0, 0))
        r = self.finish(ag)
        self.assertEqual(r.status, 'RESTRICTED_SUBGRAPH_WITNESSED')
        self.assertTrue(any(not e.obstruction.old_equal and e.obstruction.new_equal for e in r.excluded))

    def test_forged_prior_goal_never_transported(self):
        ag, old, *_ = self.make()
        self.finish(ag)
        goal = self.reach_goal(old, (0, 2, 0))
        forged = replace(goal, path=PathWitness('AA', ((0,0,0),(1,0,0),(0,2,0))))
        self.assertEqual(ag.carry_prior_goal(forged).status, 'WALL_SOURCE_GOAL')
        self.assertEqual(ag.carry_prior_goal(replace(goal, pinned_version=('bad',0,'bad'))).status,
                         'WALL_SOURCE_GOAL')

    def test_independent_law_family_stress_partial_certificate(self):
        variants = [(0,0,0), (0,1,0), (0,1,2), (2,1,0)]
        for left, right in zip(variants, variants[1:]):
            with self.subTest(left=left, right=right):
                ag, *_ = self.make(old_phi=left, new_phi=right)
                r = self.finish(ag, per_call=2)
                self.assertIn(r.status, ('RESTRICTED_SUBGRAPH_WITNESSED',
                                         'ROOTED_PRESERVED_WITNESSED'))
                mapping = dict(r.state_pairs)
                self.assertEqual(len(mapping), len(set(mapping.values())))
                for src, act, old_to, new_to in r.admitted:
                    self.assertEqual(mapping[old_to], new_to)
                self.assertEqual(ag.carry_target((0,0,0)).status,
                                 'GOAL_CARRIED_WITNESSED')


if __name__ == '__main__':
    unittest.main()
