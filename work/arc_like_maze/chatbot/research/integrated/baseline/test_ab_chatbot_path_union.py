"""Independent finite-law, provenance, boundary and obstruction tests for path unions."""
import unittest
from dataclasses import replace

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
import test_ab_chatbot_restricted_rule_transport as fixture


class PathUnionTests(unittest.TestCase):
    def make(self, old_phi=(0, 0, 1), new_phi=(0, 0, 0), *,
             depth=7, remote_new=False, budget=54, finish=True):
        host = fixture.RestrictedRuleTransportTests()
        self.addCleanup(host.doCleanups)
        _, old, new, old_owner, new_owner = host.make(
            old_phi=old_phi, new_phi=new_phi, budget=budget,
            remote_new=remote_new)
        discovered = BranchDiscoverer(old, new, (0, 1, 1), max_depth=depth)
        if finish:
            for _ in range(250):
                report = discovered.advance(max_new_edges=5)
                if report.status != 'CONTINUING':
                    break
            else:
                self.fail('discovery did not finish within 250 increments')
        return discovered, old, new, old_owner, new_owner

    @staticmethod
    def oracle(old_law, new_law, words, goals):
        """Independent powerset oracle using explicit finite laws, not cached paths."""
        best = (-1, -1, -1, -10**9)
        outcomes = set()
        valid_count = 0
        for bits in range(1, 1 << len(words)):
            chosen = [w for j, w in enumerate(words) if bits & (1 << j)]
            fwd, reverse, edges = {}, {}, set()
            valid = True
            for word in chosen:
                old, new = (0,0,0), (0,0,0)
                for a in ' ' + word:  # includes root without depending on implementation
                    if a != ' ':
                        nx = old_law.step(old, a)
                        ny = new_law.step(new, a)
                        edges.add((old, a, nx, new, ny))
                        old, new = nx, ny
                    if (old in fwd and fwd[old] != new) or (new in reverse and reverse[new] != old):
                        valid = False
                        break
                    fwd[old], reverse[new] = new, old
                if not valid:
                    break
            if not valid:
                continue
            valid_count += 1
            carried = {g: fwd[g] for g in goals
                       if g in fwd and any(old_law.follow(w) == g for w in chosen)}
            score = (len(carried), len(edges), len(fwd), -len(chosen))
            if score > best:
                best = score
                outcomes = {(tuple(sorted(carried.items())), tuple(sorted(chosen)))}
            elif score == best:
                outcomes.add((tuple(sorted(carried.items())), tuple(sorted(chosen))))
        return best, outcomes, valid_count

    def test_merges_distinct_goals_to_reusable_partial_graph(self):
        agent, old, new, *_ = self.make()
        result = PathUnionAgent(agent, ((0,1,1), (2,2,0))).run()
        self.assertEqual(result.status, 'UNION_WITNESSED')
        self.assertEqual({g for g, _, _ in result.selected.carried_goals}, {(0,1,1),(2,2,0)})
        self.assertGreater(len(result.selected.admitted_edges), 5)
        self.assertGreaterEqual(len(result.selected.words), 2)
        mapping = dict(result.selected.state_pairs)
        for s, a, t, mapped_s, mapped_t in result.selected.admitted_edges:
            self.assertEqual((mapping[s], mapping[t]), (mapped_s, mapped_t))
            self.assertEqual(old.snapshot.edges[(s,a)], t)
            self.assertEqual(new.snapshot.edges[(mapped_s,a)], mapped_t)
        self.assertLess(len(result.selected.admitted_edges), 54)  # no full-state claim

    def test_rejected_union_contains_exact_replayable_collision(self):
        agent, *_ = self.make()
        r = PathUnionAgent(agent, ((1,1,1),(1,1,0))).run()
        self.assertEqual(r.status, 'PARTIAL_UNION_WITNESSED')
        collision = next((c for c in r.conflicts
                          if set((c.left_candidate,c.right_candidate)) == {'ABB','BA'}), None)
        self.assertIsNotNone(collision)
        w = collision.witness
        self.assertNotEqual(w.old_equal, w.new_equal)
        self.assertEqual(w.old_equal,
            FiniteSystem((0,0,1)).follow(w.left_word) == FiniteSystem((0,0,1)).follow(w.right_word))
        self.assertEqual(w.new_equal,
            FiniteSystem((0,0,0)).follow(w.left_word) == FiniteSystem((0,0,0)).follow(w.right_word))

    def test_partial_result_not_mislabeled_full_completion(self):
        agent, *_ = self.make()
        r = PathUnionAgent(agent, ((0,1,1),(0,1,0))).run()
        self.assertEqual(r.status, 'PARTIAL_UNION_WITNESSED')
        self.assertEqual(len(r.selected.carried_goals), 1)
        self.assertEqual(len(r.possible_goal_images), 2)
        self.assertIn('carried 1/2', r.detail)

    def test_independent_powerset_reference_three_law_pairs(self):
        for old_phi, new_phi in [((0,0,1),(0,0,0)), ((0,0,0),(0,0,1)),
                                 ((0,1,0),(2,1,0))]:
            with self.subTest(old=old_phi, new=new_phi):
                agent, *_ = self.make(old_phi,new_phi)
                goals = ((0,1,1), (2,2,0), (0,1,0))
                r = PathUnionAgent(agent,goals,variants_per_goal=4,max_candidates=12).run()
                reference, alternatives, num_valid = self.oracle(
                    FiniteSystem(old_phi), FiniteSystem(new_phi), r.candidate_words, goals)
                selected = r.selected
                measured = (len(selected.carried_goals), len(selected.admitted_edges),
                            len(selected.state_pairs), -len(selected.words))
                self.assertEqual(measured, reference)
                self.assertIn((tuple(sorted((g, t) for g,t,_ in selected.carried_goals)),
                               tuple(sorted(selected.words))), alternatives)
                self.assertEqual(r.compatible_subsets, num_valid)

    def test_alternative_goal_images_survive_strategy_selection(self):
        agent, *_ = self.make(old_phi=(0,0,0), new_phi=(0,0,1))
        r = PathUnionAgent(agent, ((1,1,0),), variants_per_goal=6).run()
        self.assertEqual(r.status, 'UNION_WITNESSED')
        self.assertEqual(r.possible_goal_images,
                         (((1,1,0), ((1,1,0),(1,1,1))),))
        self.assertIn(r.selected.carried_goals[0][1], ((1,1,0),(1,1,1)))

    def test_observation_cache_unchanged_during_merge(self):
        agent, old, new, *_ = self.make()
        before = (dict(old.snapshot.edges), dict(new.snapshot.edges))
        r = PathUnionAgent(agent, ((0,1,1),(2,2,0))).run()
        self.assertEqual(r.status, 'UNION_WITNESSED')
        self.assertEqual(before,(old.snapshot.edges,new.snapshot.edges))

    def test_source_must_finish_discovery_first(self):
        agent, *_ = self.make(finish=False)
        self.assertEqual(PathUnionAgent(agent, ((0,1,1),)).run().status,
                         'DISCOVERY_INCOMPLETE')

    def test_empty_depth_partial_root_goal(self):
        agent, *_ = self.make(depth=0)
        r = PathUnionAgent(agent, ((0,0,0),(0,1,1))).run()
        self.assertEqual(r.status, 'PARTIAL_UNION_WITNESSED')
        self.assertEqual(r.selected.carried_goals, (((0,0,0),(0,0,0),''),))
        self.assertEqual(r.selected.admitted_edges, ())

    def test_no_requested_goal_in_discovery(self):
        agent, *_ = self.make(depth=0)
        r = PathUnionAgent(agent, ((0,1,1),)).run()
        self.assertEqual(r.status,'GOALS_OUTSIDE_CANDIDATES')
        self.assertIsNone(r.selected)

    def test_candidate_limit_is_reported_and_does_not_claim_exhaustive(self):
        agent, *_ = self.make()
        r = PathUnionAgent(agent, ((0,1,1),(2,2,0),(0,1,0)),
                           variants_per_goal=5, max_candidates=2).run()
        self.assertTrue(r.candidate_pool_truncated)
        self.assertGreater(r.paths_available,r.paths_considered)
        self.assertEqual(r.paths_considered,2)
        self.assertIn('chosen candidate paths only',r.detail)

    def test_remote_reporting_does_not_claim_local_verification(self):
        agent, *_ = self.make(remote_new=True)
        r = PathUnionAgent(agent,((0,1,1),(2,2,0))).run()
        self.assertEqual(r.status,'UNION_REMOTE_REPORTED')

    def test_repin_blocks_reuse(self):
        agent, old, new, _, owner = self.make()
        owner.replace(TransportedLaw((1,1,1),tuple(DOMAIN)))
        new.ask('pin current version')
        r = PathUnionAgent(agent, ((0,1,1),(2,2,0))).run()
        self.assertEqual(r.status,'UNKNOWN_VERSION')

    def test_forged_cache_blocks_reuse(self):
        agent, old, *_ = self.make()
        old.snapshot.edges[((0,0,0),'A')] = (2,2,2)
        r = PathUnionAgent(agent, ((0,1,1),(2,2,0))).run()
        self.assertEqual(r.status,'WALL_OBSERVATION')

    def test_limit_validation(self):
        agent, *_ = self.make(depth=0)
        for bad in (0,17,True,1.5):
            with self.assertRaises(ValueError):
                PathUnionAgent(agent, ((0,0,0),), max_candidates=bad)
        for bad in (0,11,True,1.5):
            with self.assertRaises(ValueError):
                PathUnionAgent(agent, ((0,0,0),), variants_per_goal=bad)
        for goals in ((), ((0,0,0),(0,0,0)), ((3,0,0),)):
            with self.assertRaises(ValueError):
                PathUnionAgent(agent,goals)

    def test_identical_systems_allow_simple_joint_union(self):
        agent, *_ = self.make(old_phi=(0,0,0),new_phi=(0,0,0))
        r = PathUnionAgent(agent,((0,1,0),(2,2,0))).run()
        self.assertEqual(r.status,'UNION_WITNESSED')
        self.assertTrue(all(o==n for o,n in r.selected.state_pairs))
        self.assertEqual(len(r.selected.carried_goals),2)


if __name__ == '__main__':
    unittest.main()
