"""Tests for goal-dependent selection of explicitly bounded partial maps."""
import unittest

from ab_chatbot_goal_selected_restrictions import GoalSelectedRestrictions
from ab_chatbot_restricted_rule_transport import RestrictedRuleTransport
from ab_chatbot_stability_witness import TransportedLaw
import test_ab_chatbot_restricted_rule_transport as previous_tests


class GoalSelectionTests(unittest.TestCase):
    def make(self, goal=(1, 1, 1), *, old_phi=(0, 0, 1), new_phi=(0, 0, 0),
             budget=54, remote_new=False):
        host = previous_tests.RestrictedRuleTransportTests()
        self.addCleanup(host.doCleanups)
        _, old, new, old_owner, new_owner = host.make(
            old_phi=old_phi, new_phi=new_phi, budget=budget, remote_new=remote_new)
        return GoalSelectedRestrictions(old, new, goal), old, new, old_owner, new_owner

    def run_to_end(self, agent, per_call=3):
        for i in range(500):
            r = agent.advance(max_new_edges=per_call)
            if r.status != 'CONTINUING':
                return r
        self.fail('no terminal result')

    def test_selects_dfs_when_bfs_cannot_carry_goal(self):
        agent, old, new, *_ = self.make()
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_SELECTED_WITNESSED')
        self.assertEqual(r.selected_strategy, 'DFS_BA')
        self.assertEqual(r.original_path.word, 'ABB')
        self.assertEqual(r.changed_path.word, 'ABB')
        self.assertEqual(r.original_path.states[-1], (1, 1, 1))
        self.assertEqual(r.target_image, (1, 1, 0))
        self.assertEqual({c.strategy: c.goal_status for c in r.candidates}, {
            'BFS_AB': 'GOAL_OUTSIDE_RESTRICTION', 'DFS_BA': 'GOAL_CARRIED_WITNESSED'})
        self.assertEqual(r.old_observed_edges, len(old.snapshot.edges))
        self.assertEqual(r.new_observed_edges, len(new.snapshot.edges))

    def test_selects_bfs_for_opposite_goal(self):
        agent, *_ = self.make(goal=(1, 1, 0))
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_SELECTED_WITNESSED')
        self.assertEqual(r.selected_strategy, 'BFS_AB')
        self.assertEqual(r.original_path.word, 'BA')
        self.assertEqual(r.target_image, (1, 1, 0))

    def test_selects_shortest_route_when_both_usable(self):
        agent, *_ = self.make(goal=(0, 0, 0))
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_SELECTED_WITNESSED')
        self.assertEqual(r.selected_strategy, 'BFS_AB')
        self.assertEqual(r.original_path.word, '')
        self.assertEqual(sum(c.goal_status == 'GOAL_CARRIED_WITNESSED'
                             for c in r.candidates), 2)

    def test_different_valid_destination_images_are_not_hidden(self):
        agent, *_ = self.make(goal=(1, 1, 0), old_phi=(0, 0, 0), new_phi=(0, 0, 1))
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_SELECTED_WITNESSED')
        self.assertEqual(r.selected_strategy, 'BFS_AB')
        self.assertEqual(r.original_path.word, 'BA')
        images = {c.target_image for c in r.candidates}
        self.assertEqual(images, {(1, 1, 0), (1, 1, 1)})
        self.assertIn('does not establish a unique correspondence', r.detail)

    def test_candidate_discovery_is_distinct(self):
        agent, *_ = self.make()
        self.run_to_end(agent)
        first = set(agent.strategies[0][1].forward)
        second = set(agent.strategies[1][1].forward)
        self.assertIn((1, 1, 1), second - first)
        self.assertIn((1, 1, 0), first - second)
        for _, candidate in agent.strategies:
            candidate._audit()

    def test_no_goal_in_tested_pair_is_not_global_impossibility(self):
        agent, *_ = self.make(goal=(0, 0, 1))
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_OUTSIDE_TESTED_RESTRICTIONS')
        self.assertIsNone(r.selected_strategy)

    def test_one_edge_shared_budget_never_overreads(self):
        agent, old, new, *_ = self.make()
        for _ in range(220):
            before = len(old.snapshot.edges) + len(new.snapshot.edges)
            r = agent.advance(max_new_edges=1)
            after = len(old.snapshot.edges) + len(new.snapshot.edges)
            self.assertLessEqual(after-before, 1)
            if r.status != 'CONTINUING': break
        self.assertEqual(r.status, 'GOAL_SELECTED_WITNESSED')

    def test_zero_budget_does_not_read(self):
        agent, old, new, *_ = self.make()
        r = agent.advance(max_new_edges=0)
        self.assertEqual(r.status, 'CONTINUING')
        self.assertEqual(len(old.snapshot.edges)+len(new.snapshot.edges), 0)

    def test_exhausted_owner_budget_is_unknown_not_failure(self):
        agent, old, new, *_ = self.make(budget=2)
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'UNKNOWN_BUDGET')
        old.snapshot.max_edges = new.snapshot.max_edges = 54
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_SELECTED_WITNESSED')

    def test_changed_pinned_version_invalidates_both(self):
        agent, old, new, _, new_owner = self.make()
        self.run_to_end(agent)
        from ab_chatbot_discovered_correspondence import DOMAIN
        new_owner.replace(TransportedLaw((0, 1, 1), tuple(DOMAIN)))
        new.ask('pin current version')
        self.assertEqual(agent.advance().status, 'UNKNOWN_VERSION')

    def test_cache_forgery_fails_reaudit_even_when_choice_previously_complete(self):
        agent, old, new, *_ = self.make()
        self.run_to_end(agent)
        old.snapshot.edges[((0, 0, 0), 'A')] = (2, 2, 2)
        self.assertEqual(agent.advance(max_new_edges=0).status, 'WALL_OBSERVATION')

    def test_remote_reports_are_not_upgraded_to_locally_verified(self):
        agent, *_ = self.make(remote_new=True)
        r = self.run_to_end(agent)
        self.assertEqual(r.status, 'GOAL_SELECTED_REMOTE_REPORTED')
        self.assertTrue(all(c.restriction_status.endswith('REMOTE_REPORTED') for c in r.candidates))

    def test_not_all_correspondences_claimed_enumerated(self):
        agent, *_ = self.make()
        r = self.run_to_end(agent)
        self.assertIn('two explicitly tested', r.detail)
        self.assertEqual(len(r.candidates), 2)

    def test_all_targets_match_independent_finite_graph_reference(self):
        # This oracle uses the FiniteSystem rules directly. The chooser is only
        # given pinned observers and the goal, not the oracle or its mapping.
        from collections import deque
        from ab_chatbot_discovered_correspondence import FiniteSystem

        def independent(old_law, new_law, mode, order):
            root = (0, 0, 0)
            forward = {root: (root, '')}
            reverse = {root: root}
            queue = deque([root])
            while queue:
                old_state = queue.popleft() if mode == 'BFS' else queue.pop()
                new_state, word = forward[old_state]
                for act in order:
                    dst_old = old_law.step(old_state, act)
                    dst_new = new_law.step(new_state, act)
                    if (dst_old in forward and forward[dst_old][0] != dst_new) or (
                        dst_new in reverse and reverse[dst_new] != dst_old):
                        continue
                    if dst_old not in forward:
                        forward[dst_old] = (dst_new, word + act)
                        reverse[dst_new] = dst_old
                        queue.append(dst_old)
            return forward

        cases = [((0, 0, 1), (0, 0, 0)),
                 ((0, 1, 0), (2, 1, 0)),
                 ((0, 1, 2), (2, 1, 0))]
        for old_phi, new_phi in cases:
            with self.subTest(old=old_phi, new=new_phi):
                agent, old, new, *_ = self.make(
                    goal=(0, 0, 0), old_phi=old_phi, new_phi=new_phi)
                self.run_to_end(agent)
                old_law, new_law = FiniteSystem(old_phi), FiniteSystem(new_phi)
                references = {
                    'BFS_AB': independent(old_law, new_law, 'BFS', 'AB'),
                    'DFS_BA': independent(old_law, new_law, 'DFS', 'BA'),
                }
                for name, branch in agent.strategies:
                    self.assertEqual(branch.forward, references[name])
                for i in range(3):
                    for j in range(3):
                        for k in range(3):
                            target = (i, j, k)
                            chooser = GoalSelectedRestrictions(old, new, target)
                            out = chooser.advance(max_new_edges=0)
                            self.assertNotEqual(out.status, 'CONTINUING')
                            choices = [(len(table[target][1]), table[target][1], name,
                                        table[target][0])
                                       for name, table in references.items() if target in table]
                            if not choices:
                                self.assertEqual(out.status, 'GOAL_OUTSIDE_TESTED_RESTRICTIONS')
                                continue
                            _, word, name, image = min(choices)
                            self.assertEqual(out.selected_strategy, name)
                            self.assertEqual(out.original_path.word, word)
                            self.assertEqual(out.target_image, image)
                            self.assertEqual(out.original_path.states[-1], target)
                            self.assertEqual(out.changed_path.states[-1], image)

    def test_bad_inputs_rejected(self):
        agent, *_ = self.make()
        for n in (-1, 109, True, 1.2):
            with self.assertRaises(ValueError): agent.advance(max_new_edges=n)
        with self.assertRaises(ValueError):
            RestrictedRuleTransport(agent.old, agent.new, frontier_mode='bogus')
        with self.assertRaises(ValueError):
            RestrictedRuleTransport(agent.old, agent.new, action_order='AA')


if __name__ == '__main__':
    unittest.main()
