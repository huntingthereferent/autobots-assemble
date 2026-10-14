"""Independent negative/positive witnesses across finite rule changes."""
import unittest
from unittest.mock import patch

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_goal_agent import GoalAgent
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge, ObservationWall
from ab_chatbot_rule_change import RuleChangeAgent
from ab_chatbot_stability_witness import TransportedLaw

IDENT = tuple(DOMAIN)


class RuleChangeTests(unittest.TestCase):
    def make(self, left=(0, 0, 0), right=(0, 1, 2), *,
             left_map=IDENT, right_map=IDENT, edge_budget=54,
             unbound_target=False):
        a = SourceOwnedHTTP(TransportedLaw(left, left_map))
        b = SourceOwnedHTTP(TransportedLaw(right, right_map))
        sa, sb = LoopbackHTTP(a), LoopbackHTTP(b)
        sa.__enter__(); sb.__enter__()
        self.addCleanup(sb.__exit__, None, None, None)
        self.addCleanup(sa.__exit__, None, None, None)
        aa = LanguageBridge(RemoteObserver(sa.url, bound_loopback=sa),
                            owner=a, edge_budget=edge_budget)
        bb = LanguageBridge(RemoteObserver(sb.url, bound_loopback=None if unbound_target else sb),
                            owner=b, edge_budget=edge_budget)
        return RuleChangeAgent(aa, bb), aa, bb, a, b

    @staticmethod
    def finish(agent, per_call=4):
        for _ in range(120):
            r = agent.advance(max_new_edges=per_call)
            if r.status != 'CONTINUING':
                return r
        raise AssertionError('comparison did not terminate')

    def test_changed_law_witnesses_both_survival_and_breakage(self):
        agent, old, new, _, _ = self.make()
        result = self.finish(agent)
        self.assertEqual(result.status, 'RELATION_CHANGED_WITNESSED')
        self.assertEqual(result.old_observed_edges, 10)
        self.assertEqual(result.new_observed_edges, 10)
        self.assertGreaterEqual(len(result.preserved), 1)
        self.assertIn(('', 'AAA'), [(x.left_word, x.right_word) for x in result.preserved])
        w = result.broken
        self.assertIsNotNone(w)
        self.assertEqual((w.left_word, w.right_word), ('BA', 'ABB'))
        self.assertEqual((w.old_equal, w.new_equal), (True, False))
        self.assertEqual(w.old_left.states[-1], w.old_right.states[-1])
        self.assertNotEqual(w.new_left.states[-1], w.new_right.states[-1])
        self.assertEqual(self.finish(agent).new_observed_edges, 10)

    def test_reverse_difference_detects_new_equality(self):
        agent, *_ = self.make(left=(0,1,2), right=(0,0,0))
        result = self.finish(agent)
        self.assertEqual(result.status, 'RELATION_CHANGED_WITNESSED')
        self.assertIsNotNone(result.broken)
        self.assertEqual((result.broken.old_equal, result.broken.new_equal), (False, True))

    def test_same_law_certifies_rooted_generator_correspondence(self):
        agent, *_ = self.make(left=(0,1,2), right=(0,1,2))
        r = self.finish(agent)
        self.assertEqual(r.status, 'ROOTED_PRESERVED_WITNESSED')
        self.assertEqual(r.compared_pairs, 27)
        self.assertEqual((r.old_observed_edges, r.new_observed_edges), (54,54))
        self.assertIsNone(r.broken)

    def test_nonlinear_relabeling_is_not_mistaken_for_rule_change(self):
        shear = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        agent, *_ = self.make(right=(0,0,0), right_map=shear)
        r = self.finish(agent)
        self.assertEqual(r.status, 'ROOTED_PRESERVED_WITNESSED')
        self.assertEqual(r.compared_pairs, 9)
        self.assertEqual(r.new_observed_edges, 18)
        self.assertIsNone(r.broken)

    def test_rooted_preservation_does_not_mean_offroot_equality(self):
        # Off-root coordinate change leaves the k=0 rooted component fixed.
        permutation = list(DOMAIN)
        i, j = DOMAIN.index((0,0,1)), DOMAIN.index((0,1,1))
        permutation[i], permutation[j] = permutation[j], permutation[i]
        agent, old, new, a, b = self.make(right=(0,0,0), right_map=tuple(permutation))
        r = self.finish(agent)
        self.assertEqual(r.status, 'ROOTED_PRESERVED_WITNESSED')
        self.assertEqual(r.compared_pairs, 9)
        self.assertNotEqual(a.select().step((0,0,1), 'B'), b.select().step((0,0,1), 'B'))

    def test_continuation_never_exceeds_per_call_total(self):
        agent, old, new, *_ = self.make()
        for _ in range(100):
            before = len(old.snapshot.edges) + len(new.snapshot.edges)
            r = agent.advance(max_new_edges=1)
            after = len(old.snapshot.edges) + len(new.snapshot.edges)
            self.assertLessEqual(after-before, 1)
            if r.status != 'CONTINUING':
                break
        self.assertEqual(r.status, 'RELATION_CHANGED_WITNESSED')
        self.assertEqual(len(old.snapshot.edges) + len(new.snapshot.edges), 20)

    def test_zero_budget_keeps_state_unmodified(self):
        agent, old, new, *_ = self.make()
        r = agent.advance(max_new_edges=0)
        self.assertEqual(r.status,'CONTINUING')
        self.assertFalse(old.snapshot.edges)
        self.assertFalse(new.snapshot.edges)
        self.assertEqual(r.compared_pairs, 1)

    def test_total_budget_stops_without_raising_it_automatically(self):
        agent, old, new, *_ = self.make(edge_budget=3)
        r = self.finish(agent)
        self.assertEqual(r.status, 'UNKNOWN_BUDGET')
        self.assertLessEqual(r.old_observed_edges, 3)
        self.assertLessEqual(r.new_observed_edges, 3)
        self.assertEqual(old.snapshot.max_edges, 3)
        self.assertEqual(new.snapshot.max_edges, 3)
        # Explicit user-side reauthorization allows a genuine continuation.
        old.snapshot.max_edges = 54
        new.snapshot.max_edges = 54
        self.assertEqual(self.finish(agent).status, 'RELATION_CHANGED_WITNESSED')

    def test_repin_rejects_stale_comparison(self):
        agent, old, new, _, b = self.make()
        agent.advance(max_new_edges=4)
        b.replace(TransportedLaw((1,1,1), IDENT))
        new.ask('Pin current version')
        self.assertEqual(agent.advance(max_new_edges=54).status, 'UNKNOWN_VERSION')

    def test_unbound_origin_downgrades_claim(self):
        agent, *_ = self.make(unbound_target=True)
        r = self.finish(agent)
        self.assertEqual(r.status, 'RELATION_CHANGED_REMOTE_REPORTED')
        self.assertTrue(r.broken)

    def test_invalid_observation_fails_closed(self):
        agent, old, new, *_ = self.make()
        with patch.object(new.snapshot, 'step', side_effect=ObservationWall('simulated bad data')):
            r = agent.advance(max_new_edges=4)
        self.assertEqual(r.status, 'WALL_OBSERVATION')
        self.assertIsNone(r.broken)

    def test_forged_cached_edge_is_not_promoted_to_local_witness(self):
        agent, old, new, *_ = self.make()
        old.snapshot.edges[((0,0,0), 'A')] = (2,2,2)
        r = agent.advance(max_new_edges=4)
        self.assertEqual(r.status, 'WALL_OBSERVATION')
        self.assertIsNone(r.broken)

    def test_rejects_bad_arguments(self):
        agent, *_ = self.make()
        for bad in (-1, 109, True, '4'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                agent.advance(max_new_edges=bad)
        with self.assertRaises(ValueError):
            RuleChangeAgent(agent.old, agent.new, old_root=(3,0,0))

    def test_goal_completion_changes_under_new_law_without_suggested_path(self):
        agent, old, new, *_ = self.make()
        newly_reachable = (1,1,2)
        previous = GoalAgent(old, newly_reachable).advance(max_new_edges=54)
        self.assertEqual(previous.status,'UNREACHABLE_CLOSED_COMPONENT')
        difference = self.finish(agent)
        self.assertEqual(difference.status,'RELATION_CHANGED_WITNESSED')
        current = GoalAgent(new, newly_reachable).advance(max_new_edges=54)
        self.assertEqual(current.status,'COMPLETE_WITNESSED')
        self.assertEqual(current.path.word, 'ABB')
        self.assertEqual(current.path.states[-1], newly_reachable)


if __name__ == '__main__':
    unittest.main()
