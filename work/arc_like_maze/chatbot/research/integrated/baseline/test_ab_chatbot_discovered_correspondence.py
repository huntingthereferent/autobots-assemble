"""Discovery of rooted and full A/B correspondences from transition oracles."""
from __future__ import annotations

from dataclasses import replace
from itertools import product
from collections import Counter
from random import Random
import unittest

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_admission_probe import OffOrbitAlteration
from ab_chatbot_structural_witness import CovariantSource
from ab_chatbot_witness_transport import Shear, SourceWitness, ReachedWitness
from ab_chatbot_discovered_correspondence import (
    DOMAIN, ZERO, Discovery, discover, verify_recorded_full,
)


class CorrespondenceDiscoveryTests(unittest.TestCase):
    def target(self, phi=(0, 0, 0), shear=1):
        return ReachedWitness(SourceWitness.establish(
            CovariantSource.for_law(phi))).transport(Shear(shear))

    def test_all_27_source_laws_three_nonlin_transports_without_given_h(self):
        for phi in product(range(3), repeat=3):
            src = FiniteSystem(phi)
            for c in range(3):
                # Only a step oracle crosses the boundary. The discovery
                # code never receives Shear(c) or any explicit H.
                result = discover(src, self.target(phi, c).step)
                with self.subTest(phi=phi, c=c):
                    self.assertEqual(result.status, "FULL_CONJUGACY", result.detail)
                    self.assertEqual(len(result.full_pairs), 27)
                    self.assertEqual(result.calls, 54)
                    self.assertTrue(verify_recorded_full(src, result))
                    self.assertEqual(dict(result.full_pairs)[ZERO], ZERO)

    def test_arbitrary_full_state_relabeling_fixed_origin(self):
        for phi in ((0, 0, 0), (0, 1, 2), (1, 0, 2)):
            law = FiniteSystem(phi)
            points = list(DOMAIN)
            shuffled = points[1:]
            Random(sum(phi) + 21).shuffle(shuffled)
            actual_h = dict(zip(points, [ZERO, *shuffled]))
            inverse = {v: k for k, v in actual_h.items()}
            def target(t, a):
                return actual_h[law.step(inverse[t], a)]
            found = discover(law, target)
            self.assertEqual(found.status, "FULL_CONJUGACY")
            self.assertTrue(verify_recorded_full(law, found))
            # Distinct H can produce the same conjugacy; there is no uniqueness claim.
            self.assertEqual(len(set(dict(found.full_pairs).values())), 27)

    def test_rooted_observations_not_promoted_to_full_state(self):
        src = FiniteSystem((0, 0, 0))
        result = discover(src, self.target().step, full=False)
        self.assertEqual(result.status, "ROOTED_REACHABLE")
        self.assertEqual(result.rooted_count, 9)
        self.assertEqual(result.calls, 18)
        self.assertEqual(result.full_pairs, ())
        self.assertFalse(verify_recorded_full(src, result))

    def test_full_state_obstruction_outside_origin_orbit(self):
        src = FiniteSystem((0, 0, 0))
        altered = OffOrbitAlteration()
        partial = discover(src, altered.step, full=False)
        self.assertEqual(partial.status, "ROOTED_REACHABLE")
        self.assertEqual(partial.rooted_count, 9)
        full = discover(src, altered.step)
        self.assertEqual(full.status, "FULL_OBSTRUCTED")
        self.assertIn("orbit sizes", full.detail)
        self.assertFalse(verify_recorded_full(src, full))

    def test_contradictory_rooted_observation(self):
        src = FiniteSystem((0, 1, 2))
        def bad(s, a):
            if s == ZERO and a == "A":
                return ZERO
            return src.step(s, a)
        res = discover(src, bad)
        self.assertEqual(res.status, "ROOTED_OBSTRUCTED")
        self.assertEqual(res.full_pairs, ())

    def test_missing_observations_do_not_certify(self):
        src = FiniteSystem((0, 0, 0))
        target = self.target().step
        for limit in (0, 1, 17, 18, 53):
            with self.subTest(limit=limit):
                res = discover(src, target, max_queries=limit)
                self.assertEqual(res.status, "UNKNOWN_QUERY_BUDGET")
                self.assertEqual(res.calls, limit)
                self.assertEqual(res.full_pairs, ())
                self.assertFalse(verify_recorded_full(src, res))

    def test_search_budget_keeps_unknown_instead_of_negative(self):
        src = FiniteSystem((0, 0, 0))
        res = discover(src, self.target().step, max_extension_attempts=0)
        self.assertEqual(res.status, "UNKNOWN_SEARCH_BUDGET")
        self.assertEqual(res.rooted_count, 9)
        self.assertEqual(res.calls, 54)
        self.assertEqual(res.attempts, 0)

    def test_observer_queries_cached_once_per_transition(self):
        src = FiniteSystem((0, 1, 2))
        calls = Counter()
        target = self.target((0, 1, 2)).step
        def audit(s, a):
            calls[s, a] += 1
            return target(s, a)
        result = discover(src, audit)
        self.assertEqual(result.status, "FULL_CONJUGACY")
        self.assertEqual(sum(calls.values()), 54)
        self.assertEqual(set(calls.values()), {1})
        self.assertEqual(len(result.observed), 54)

    def test_saved_observations_verify_only_self_consistency(self):
        src = FiniteSystem((2, 0, 1))
        result = discover(src, self.target((2, 0, 1)).step)
        self.assertTrue(verify_recorded_full(src, result))
        pairs = list(result.full_pairs)
        pairs[0], pairs[1] = (pairs[0][0], pairs[1][1]), (pairs[1][0], pairs[0][1])
        self.assertFalse(verify_recorded_full(src, replace(result, full_pairs=tuple(pairs))))
        records = list(result.observed)
        records[0] = replace(records[0], output=(0, 0, 0) if records[0].output != ZERO else (1, 1, 1))
        self.assertFalse(verify_recorded_full(src, replace(result, observed=tuple(records))))
        self.assertFalse(verify_recorded_full(src, result, target_root=(1, 0, 0)))

    def test_invalid_oracle_values_and_budget_validation(self):
        src = FiniteSystem((0, 0, 0))
        result = discover(src, lambda s, a: (9, 9, 9))
        self.assertEqual(result.status, "WALL_INVALID_OBSERVATION")
        with self.assertRaises(ValueError):
            discover(src, src.step, max_queries=-1)
        with self.assertRaises(ValueError):
            discover(src, src.step, max_extension_attempts=-1)
        with self.assertRaises(ValueError):
            discover(src, src.step, source_root=(3, 0, 0))
        with self.assertRaises(TypeError):
            discover(object(), src.step)

    def test_nonbijective_off_orbit_law_obstructs_full(self):
        src = FiniteSystem((0, 0, 0))
        def target(s, a):
            return s if s == (0, 0, 1) and a == "B" else src.step(s, a)
        res = discover(src, target)
        self.assertEqual(res.status, "FULL_OBSTRUCTED")
        self.assertIn("not bijective", res.detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
