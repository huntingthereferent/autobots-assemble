"""Evidence scopes for incremental finite mathematical A/B model continuity."""
from dataclasses import replace
from itertools import combinations, product
import unittest

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import DOMAIN, discover
from ab_chatbot_stability_witness import (
    TransportedLaw, compare_anchor_stability, recheck_full_record,
    recheck_bijective_target,
)


class StabilityWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = FiniteSystem((0, 0, 0))
        cls.original_h = tuple((i, j, (k + i*j) % 3) for i, j, k in DOMAIN)
        cls.original = TransportedLaw(cls.source.phi, cls.original_h)
        cls.baseline = discover(cls.source, cls.original.step, full=True)
        assert cls.baseline.status == 'FULL_CONJUGACY'
        cls.found_h = tuple(dict(cls.baseline.full_pairs)[s] for s in DOMAIN)

    def make(self, phi=(0, 0, 0), subfamily=False):
        return TransportedLaw(phi, self.found_h, require_phi0_zero=subfamily)

    def test_full_baseline_and_nonlinear_transport(self):
        self.assertEqual(len(self.baseline.full_pairs), 27)
        self.assertEqual(len(self.baseline.observed), 54)
        self.assertEqual(len(set(self.found_h)), 27)
        stable = self.make()
        result = compare_anchor_stability(self.source, self.baseline, stable.step, owned_family=stable)
        self.assertEqual(result.status, 'VERIFIED_WITHIN_OWNED_FAMILY')
        self.assertEqual(result.calls, 3)

    def test_without_structure_anchor_matching_is_not_certification(self):
        observed = compare_anchor_stability(self.source, self.baseline, self.make().step)
        self.assertEqual(observed.status, 'CONDITIONAL_MATCH')
        self.assertEqual(observed.calls, 3)

    def test_all_27_owned_laws_are_separated_from_reference_by_three_anchors(self):
        statuses = {}
        for phi in product(range(3), repeat=3):
            with self.subTest(phi=phi):
                owned = self.make(phi)
                result = compare_anchor_stability(self.source, self.baseline, owned.step, owned_family=owned)
                self.assertLessEqual(result.calls, 3)
                self.assertEqual(result.status, 'VERIFIED_WITHIN_OWNED_FAMILY' if phi == self.source.phi else 'CHANGED')
                statuses[phi] = result.status
        self.assertEqual(len(statuses), 27)

    def test_missing_one_of_three_anchors_underdetermines_unrestricted_phi(self):
        for missing in range(3):
            alt = [0, 0, 0]
            alt[missing] = 1
            alt_law = self.make(tuple(alt))
            old_law = self.make()
            for j in range(3):
                if j == missing:
                    continue
                s = self.found_h[DOMAIN.index((0, j, 0))]
                self.assertEqual(alt_law.step(s, 'B'), old_law.step(s, 'B'))
            self.assertNotEqual(alt_law.step(self.found_h[DOMAIN.index((0, missing, 0))], 'B'),
                                old_law.step(self.found_h[DOMAIN.index((0, missing, 0))], 'B'))

    def test_budget_two_is_unknown_if_last_anchor_can_change(self):
        alt = self.make((0, 0, 1))
        result = compare_anchor_stability(self.source, self.baseline, alt.step, owned_family=alt, max_queries=2)
        self.assertEqual(result.status, 'UNKNOWN_BUDGET')
        self.assertEqual(result.calls, 2)
        self.assertEqual(compare_anchor_stability(self.source, self.baseline, alt.step, owned_family=alt).status, 'CHANGED')

    def test_certified_nine_member_subfamily_needs_only_two_anchors(self):
        src = self.source
        stable = self.make(subfamily=True)
        self.assertEqual(compare_anchor_stability(src, self.baseline, stable.step, owned_family=stable).calls, 2)
        for a, b in product(range(3), repeat=2):
            law = self.make((0, a, b), subfamily=True)
            result = compare_anchor_stability(src, self.baseline, law.step, owned_family=law)
            self.assertLessEqual(result.calls, 2)
            self.assertEqual(result.status, 'VERIFIED_WITHIN_OWNED_FAMILY' if (a,b) == (0,0) else 'CHANGED')
        with self.assertRaises(ValueError):
            self.make((1, 0, 0), subfamily=True)

    def test_out_of_family_change_agrees_on_anchors_but_full_scan_catches(self):
        original = self.make()
        target = self.found_h[DOMAIN.index((1, 0, 1))]
        def mutant(s, a):
            v = original.step(s, a)
            return ((v[0] + 1) % 3, v[1], v[2]) if (s, a) == (target, 'B') else v
        shortcut = compare_anchor_stability(self.source, self.baseline, mutant)
        self.assertEqual(shortcut.status, 'CONDITIONAL_MATCH')
        self.assertEqual(shortcut.calls, 3)
        replay = recheck_full_record(self.source, self.baseline, mutant)
        self.assertEqual(replay.status, 'CHANGED')
        self.assertGreater(replay.calls, shortcut.calls)

    def test_last_unchecked_arbitrary_edge_can_change(self):
        original = self.make()
        target = DOMAIN[-1]
        def mutant(s, a):
            v = original.step(s,a)
            return ((v[0]+1) % 3, v[1], v[2]) if (s,a)==(target,'B') else v
        short = recheck_full_record(self.source, self.baseline, mutant, max_queries=53)
        self.assertEqual((short.status, short.calls), ('UNKNOWN_BUDGET', 53))
        full = recheck_full_record(self.source, self.baseline, mutant, max_queries=54)
        self.assertEqual((full.status, full.calls), ('CHANGED', 54))

    def test_unrestricted_complete_reread_matches_54_edges(self):
        stable = self.make()
        result = recheck_full_record(self.source, self.baseline, stable.step)
        self.assertEqual((result.status, result.calls), ('OBSERVED_FULL_TABLE_MATCH', 54))

    def test_permutation_premise_reduces_reads_to_52_conditionally(self):
        stable = self.make()
        unknown = recheck_bijective_target(self.source, self.baseline, stable.step)
        self.assertEqual((unknown.status, unknown.calls), ('UNKNOWN_STRUCTURE', 0))
        conditional = recheck_bijective_target(self.source, self.baseline, stable.step,
                                                independently_guaranteed_bijective=True)
        self.assertEqual((conditional.status, conditional.calls), ('CONDITIONAL_ON_BIJECTIVITY', 52))
        self.assertEqual(recheck_bijective_target(self.source, self.baseline, stable.step,
                         independently_guaranteed_bijective=True, max_queries=51).status, 'UNKNOWN_BUDGET')

    def test_permutation_swap_escapes_fifty_one_checks_but_not_fifty_two(self):
        original = self.make()
        p, q = DOMAIN[-2:]
        def swapped(s, a):
            if a == 'B' and s == p:
                return original.step(q,a)
            if a == 'B' and s == q:
                return original.step(p,a)
            return original.step(s,a)
        self.assertEqual(len({swapped(s, 'B') for s in DOMAIN}), 27)
        fewer = recheck_bijective_target(self.source, self.baseline, swapped,
                                          independently_guaranteed_bijective=True,max_queries=51)
        self.assertEqual((fewer.status,fewer.calls), ('UNKNOWN_BUDGET',51))
        more = recheck_bijective_target(self.source, self.baseline, swapped,
                                         independently_guaranteed_bijective=True,max_queries=52)
        self.assertEqual((more.status,more.calls), ('CHANGED',52))

    def test_wrong_correspondence_cannot_borrow_owned_contract(self):
        old_h = self.original_h
        if self.found_h == old_h:
            alternative = tuple(reversed(self.found_h))
        else:
            alternative = old_h
        another = TransportedLaw((0,0,0), alternative)
        with self.assertRaises(ValueError):
            compare_anchor_stability(self.source, self.baseline, another.step,
                                      owned_family=another)
        with self.assertRaises(ValueError):
            compare_anchor_stability(self.source, self.baseline, self.make().step,
                                      owned_family=self.make())

    def test_reject_fabricated_old_full_claim(self):
        partial = discover(self.source, self.original.step, full=False)
        with self.assertRaises(ValueError):
            compare_anchor_stability(self.source, partial, self.make().step)
        with self.assertRaises(ValueError):
            recheck_full_record(self.source, replace(self.baseline, full_pairs=()), self.make().step)

    def test_invalid_observation_and_query_budget(self):
        def invalid(s, a):
            return (5, 1, 0)
        self.assertEqual(compare_anchor_stability(self.source, self.baseline, invalid).status, 'WALL_INVALID')
        self.assertEqual(recheck_full_record(self.source, self.baseline, invalid).status, 'WALL_INVALID')
        self.assertEqual(compare_anchor_stability(self.source, self.baseline, invalid, max_queries=0).status,
                         'UNKNOWN_BUDGET')
        for fn in (compare_anchor_stability, recheck_full_record, recheck_bijective_target):
            with self.assertRaises(ValueError):
                fn(self.source, self.baseline, self.make().step, max_queries=-1)


if __name__ == '__main__':
    unittest.main()
