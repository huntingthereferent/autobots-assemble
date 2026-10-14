"""Independent reference and witness controls for branching path restrictions."""
import unittest
from collections import deque

from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_goal_selected_restrictions import GoalSelectedRestrictions
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw
import test_ab_chatbot_restricted_rule_transport as fixture


class BranchDiscovererTests(unittest.TestCase):
    def make(self, *, goal=(0, 1, 1), old_phi=(0, 0, 1), new_phi=(0, 0, 0),
             budget=54, depth=7, remote_new=False):
        host = fixture.RestrictedRuleTransportTests()
        self.addCleanup(host.doCleanups)
        _, old, new, old_owner, new_owner = host.make(
            old_phi=old_phi, new_phi=new_phi, budget=budget, remote_new=remote_new)
        return (BranchDiscoverer(old, new, goal, max_depth=depth),
                old, new, old_owner, new_owner)

    def finish(self, agent, per_call=5):
        for i in range(200):
            report = agent.advance(max_new_edges=per_call)
            if report.status != 'CONTINUING':
                return report
        self.fail('branch agent failed to produce terminal status')

    @staticmethod
    def oracle(old_law, new_law, depth):
        """Independent enumeration by applying both explicit finite laws."""
        root = (0, 0, 0)
        q = deque([('', (root,), (root,))])
        accepted, rejected = [], []
        while q:
            word, os, ns = q.popleft()
            accepted.append((word, os, ns))
            if len(word) == depth:
                continue
            mapping, reverse = dict(zip(os, ns)), dict(zip(ns, os))
            for a in 'AB':
                x, y = old_law.step(os[-1], a), new_law.step(ns[-1], a)
                if ((x in mapping and mapping[x] != y) or
                    (y in reverse and reverse[y] != x)):
                    rejected.append(word+a)
                else:
                    q.append((word+a, os+(x,), ns+(y,)))
        return accepted, rejected

    def test_branch_discovers_goal_outside_both_preset_restrictions(self):
        agent, old, new, *_ = self.make()
        prior = GoalSelectedRestrictions(old, new, (0, 1, 1))
        for _ in range(200):
            previous = prior.advance(max_new_edges=5)
            if previous.status != 'CONTINUING': break
        self.assertEqual(previous.status, 'GOAL_OUTSIDE_TESTED_RESTRICTIONS')
        result = self.finish(agent)
        self.assertEqual(result.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual(result.selected.word, 'ABBAA')
        self.assertEqual(result.selected.source_target, (0, 1, 1))
        self.assertEqual(result.selected.target_image, (0, 1, 0))
        self.assertGreater(len(result.rejected), 0)
        self.assertGreater(len(result.alternatives), 1)
        self.assertIn('No maximality', result.detail)

    def test_observation_budget_exactly_preserved_on_each_increment(self):
        agent, old, new, *_ = self.make()
        r = agent.advance(max_new_edges=0)
        self.assertEqual(r.status, 'CONTINUING')
        self.assertEqual(r.old_observed_edges+r.new_observed_edges, 0)
        for _ in range(160):
            before = len(old.snapshot.edges) + len(new.snapshot.edges)
            r = agent.advance(max_new_edges=1)
            after = len(old.snapshot.edges) + len(new.snapshot.edges)
            self.assertLessEqual(after-before, 1)
            if r.status != 'CONTINUING': break
        self.assertEqual(r.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual(r.selected.word, 'ABBAA')
        self.assertEqual(r.old_observed_edges, len(old.snapshot.edges))
        self.assertEqual(r.new_observed_edges, len(new.snapshot.edges))

    def test_shallow_limit_is_not_unreachability(self):
        agent, *_ = self.make(depth=3)
        r = self.finish(agent)
        self.assertEqual(r.status, 'GOAL_OUTSIDE_SEARCH_BOUND')
        self.assertIsNone(r.selected)
        self.assertIn('not a whole-system', r.detail)

    def test_rejection_witnesses_are_real_separating_equalities(self):
        agent, *_ = self.make()
        r = self.finish(agent)
        a, b = FiniteSystem((0, 0, 1)), FiniteSystem((0, 0, 0))
        for denial in r.rejected:
            p = denial.obstruction
            self.assertNotEqual(p.old_equal, p.new_equal)
            self.assertEqual(p.old_equal,
                             a.follow(p.left_word) == a.follow(p.right_word))
            self.assertEqual(p.new_equal,
                             b.follow(p.left_word) == b.follow(p.right_word))
            self.assertEqual(p.right_word, denial.attempted_word)
            self.assertIn(denial.cause, ('SOURCE_COLLISION', 'TARGET_COLLISION'))
        self.assertEqual(r.explored_prefixes, r.admitted_extensions+len(r.rejected))

    def test_all_prefixes_and_rejections_match_independent_oracle(self):
        cases = [((0, 0, 1), (0, 0, 0)),
                 ((0, 1, 0), (2, 1, 0)),
                 ((0, 0, 0), (0, 0, 1))]
        for old_phi, new_phi in cases:
            with self.subTest(old=old_phi, new=new_phi):
                agent, *_ = self.make(old_phi=old_phi, new_phi=new_phi)
                result = self.finish(agent)
                accepted, rejected = self.oracle(FiniteSystem(old_phi), FiniteSystem(new_phi), 7)
                self.assertEqual([(p.word, p.old_states, p.new_states)
                                  for p in agent.prefixes], accepted)
                self.assertEqual([x.attempted_word for x in result.rejected], rejected)
                # The same search history yields an independently checkable
                # answer for every destination, not just the declared goal.
                for goal in DOMAIN:
                    oracle_goals = sorted((word, ns[-1]) for word, os, ns
                                          in accepted if os[-1] == goal)
                    found = sorted((p.word, p.new_states[-1]) for p in agent.prefixes
                                   if p.old_states[-1] == goal)
                    self.assertEqual(found, oracle_goals)

    def test_nonunique_destination_images_retained(self):
        agent, *_ = self.make(goal=(1, 1, 0), old_phi=(0, 0, 0), new_phi=(0, 0, 1))
        r = self.finish(agent)
        self.assertEqual(r.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual({c.target_image for c in r.alternatives},
                         {(1, 1, 0), (1, 1, 1)})
        self.assertIn('not a unique correspondence', r.detail)

    def test_owner_budget_can_be_increased_explicitly(self):
        agent, old, new, *_ = self.make(budget=2)
        self.assertEqual(self.finish(agent).status, 'UNKNOWN_BUDGET')
        self.assertLessEqual(len(old.snapshot.edges), 2)
        self.assertLessEqual(len(new.snapshot.edges), 2)
        old.snapshot.max_edges = new.snapshot.max_edges = 54
        self.assertEqual(self.finish(agent).status, 'GOAL_CARRIED_WITNESSED')

    def test_owner_cache_tampering_rejected_after_completion(self):
        agent, old, new, *_ = self.make()
        self.assertEqual(self.finish(agent).status, 'GOAL_CARRIED_WITNESSED')
        old.snapshot.edges[((0, 0, 0), 'A')] = (2, 2, 2)
        self.assertEqual(agent.advance(max_new_edges=0).status, 'WALL_OBSERVATION')

    def test_owner_cache_tampering_rejected_while_continuing(self):
        agent, old, new, *_ = self.make()
        self.assertEqual(agent.advance(max_new_edges=2).status, 'CONTINUING')
        old.snapshot.edges[((0, 0, 0), 'A')] = (2, 2, 2)
        self.assertEqual(agent.advance(max_new_edges=0).status, 'WALL_OBSERVATION')

    def test_changed_version_rejects_prior_evidence(self):
        agent, old, new, _, owner = self.make()
        self.finish(agent)
        owner.replace(TransportedLaw((0, 1, 1), tuple(DOMAIN)))
        new.ask('pin current version')
        self.assertEqual(agent.advance(max_new_edges=0).status, 'UNKNOWN_VERSION')

    def test_remote_is_not_upgraded_to_local_owner_provenance(self):
        agent, *_ = self.make(remote_new=True)
        result = self.finish(agent)
        self.assertEqual(result.status, 'GOAL_CARRIED_REMOTE_REPORTED')
        self.assertEqual(result.selected.word, 'ABBAA')

    def test_empty_word_goal_and_hard_depth_limit(self):
        agent, *_ = self.make(goal=(0, 0, 0), depth=0)
        result = agent.advance(max_new_edges=0)
        self.assertEqual(result.status, 'GOAL_CARRIED_WITNESSED')
        self.assertEqual(result.selected.word, '')
        self.assertEqual(result.old_observed_edges, 0)
        self.assertEqual(result.new_observed_edges, 0)

    def test_invalid_arguments(self):
        agent, old, new, *_ = self.make()
        for number in (-1, 109, True, 1.5):
            with self.assertRaises(ValueError):
                agent.advance(max_new_edges=number)
        for depth in (-1, 9, True, 1.5):
            with self.assertRaises(ValueError):
                BranchDiscoverer(old, new, (0,0,0), max_depth=depth)
        with self.assertRaises(ValueError):
            BranchDiscoverer(old, new, (4,0,0))


if __name__ == '__main__':
    unittest.main()
