"""Counterexamples for incremental rooted A/B transport and re-entry."""
import json
from collections import Counter
from dataclasses import replace
from itertools import product
from random import Random
import unittest

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import DOMAIN, Discovery, ZERO, discover
from ab_chatbot_witness_transport import ReachedWitness, Shear, SourceWitness
from ab_chatbot_structural_witness import CovariantSource
from ab_chatbot_admission_probe import OffOrbitAlteration
from ab_chatbot_incremental_correspondence import (
    PartialWitness, Incremental, from_discovery, _hash, _wire,
)


class IncrementalCorrespondenceTests(unittest.TestCase):
    def setUp(self):
        self.source = FiniteSystem((0, 0, 0))
        self.target = ReachedWitness(SourceWitness.establish(
            CovariantSource.for_law(self.source.phi))).transport(Shear(1))

    def initial(self, observe=None, target_id='fixed-1'):
        if observe is None:
            observe = self.target.step
        proof = discover(self.source, observe, full=False)
        self.assertEqual(proof.status, 'ROOTED_REACHABLE')
        self.assertEqual(len(proof.rooted_pairs), 9)
        return from_discovery(self.source, proof, target_id=target_id)

    def test_incremental_autonomous_9_to_18_to_27_without_requery(self):
        calls = Counter()
        def observed(s, a):
            calls[s, a] += 1
            return self.target.step(s, a)
        first = self.initial(observed)
        self.assertEqual(len(calls), 18)
        tracker = Incremental(self.source, observed, first, target_id='fixed-1')
        one = tracker.extend_next(max_new_queries=18)
        self.assertEqual((one.status, one.witness.mapped, one.new_queries), ('EXTENDED', 18, 18))
        two = tracker.extend_next(max_new_queries=18)
        self.assertEqual((two.status, two.witness.mapped, two.new_queries), ('FULL_CONJUGACY', 27, 18))
        self.assertEqual((len(calls), set(calls.values())), (54, {1}))
        self.assertEqual(len(two.witness.observations), 54)
        two.witness.verify(self.source, target_id='fixed-1')
        for s, t in two.witness.pairs:
            for a in 'AB':
                self.assertEqual(dict(two.witness.pairs)[self.source.step(s, a)], self.target.step(t, a))
        self.assertEqual(tracker.extend_next().status, 'UNCHANGED')
        self.assertEqual(len(calls), 54)

    def test_three_nonlinear_source_transports_without_given_h(self):
        for c in range(3):
            target = ReachedWitness(SourceWitness.establish(
                CovariantSource.for_law(self.source.phi))).transport(Shear(c))
            initial = from_discovery(self.source, discover(self.source, target.step, full=False),
                                     target_id=f'shear-{c}')
            tracker = Incremental(self.source, target.step, initial, target_id=f'shear-{c}')
            self.assertEqual(tracker.extend_next().status, 'EXTENDED')
            self.assertEqual(tracker.extend_next().status, 'FULL_CONJUGACY')
            self.assertEqual(len(tracker.current.observations), 54)

    def test_arbitrary_permutation_of_states_and_root_preservation(self):
        base = self.source
        for seed in (1, 2, 3):
            others = list(DOMAIN[1:])
            Random(seed).shuffle(others)
            H = dict(zip(DOMAIN, [ZERO, *others]))
            inverse = {v: k for k, v in H.items()}
            def target(t, a):
                return H[base.step(inverse[t], a)]
            initial = from_discovery(base, discover(base, target, full=False), target_id=str(seed))
            tracker = Incremental(base, target, initial, target_id=str(seed))
            self.assertEqual(tracker.extend_next().status, 'EXTENDED')
            self.assertEqual(tracker.extend_next().status, 'FULL_CONJUGACY')
            self.assertEqual(tracker.current.mapped, 27)

    def test_query_budget_retains_old_witness_and_new_observations_for_retry(self):
        counts = Counter()
        def observe(s, a):
            counts[s, a] += 1
            return self.target.step(s, a)
        initial = self.initial(observe)
        tracker = Incremental(self.source, observe, initial, target_id='fixed-1')
        part = tracker.extend_at((0, 0, 1), (0, 0, 1), max_new_queries=7)
        self.assertEqual((part.status, part.witness.mapped, part.new_queries),
                         ('UNKNOWN_QUERY_BUDGET', 9, 7))
        self.assertEqual(len(part.witness.observations), 25)
        recovered = tracker.extend_at((0, 0, 1), (0, 0, 1), max_new_queries=11)
        self.assertEqual((recovered.status, recovered.witness.mapped, recovered.new_queries),
                         ('EXTENDED', 18, 11))
        self.assertEqual(len(recovered.witness.observations), 36)
        self.assertEqual(set(counts.values()), {1})
        self.assertEqual(tracker.extend_next().status, 'FULL_CONJUGACY')

    def test_reenter_snapshot_after_part_and_continue(self):
        original = self.initial()
        tracker = Incremental(self.source, self.target.step, original, target_id='fixed-1')
        tracker.extend_next()
        restored = PartialWitness.reenter(tracker.current.snapshot(), self.source, target_id='fixed-1')
        other = Incremental(self.source, self.target.step, restored, target_id='fixed-1')
        self.assertEqual(other.extend_next().status, 'FULL_CONJUGACY')
        self.assertEqual(len(other.current.observations), 54)

    def test_unchanged_anchor_and_incompatible_anchor_do_not_advance(self):
        initial = self.initial()
        tracker = Incremental(self.source, self.target.step, initial, target_id='fixed-1')
        self.assertEqual(tracker.extend_at(ZERO, ZERO).status, 'UNCHANGED')
        bad = tracker.extend_at((0, 0, 1), ZERO)
        self.assertEqual((bad.status, bad.witness.mapped, bad.new_queries),
                         ('ANCHOR_OBSTRUCTED', 9, 0))
        self.assertEqual(tracker.extend_at((0, 0, 1), (0, 0, 1)).status, 'EXTENDED')

    def test_off_orbit_mutation_not_promoted_to_full_proof(self):
        strange = OffOrbitAlteration()
        initial = self.initial(strange.step, target_id='modified')
        tracker = Incremental(self.source, strange.step, initial, target_id='modified')
        result = tracker.extend_next()
        self.assertEqual(result.status, 'ANCHOR_OBSTRUCTED')
        self.assertEqual(result.witness.mapped, 9)
        self.assertGreaterEqual(result.new_queries, 1)

    def test_exhausted_anchor_search_is_unknown(self):
        tracker = Incremental(self.source, self.target.step, self.initial(), target_id='fixed-1')
        limited = tracker.extend_next(max_anchor_attempts=0)
        self.assertEqual((limited.status, limited.attempted_anchors, limited.witness.mapped),
                         ('UNKNOWN_SEARCH_BUDGET', 0, 9))
        self.assertEqual(tracker.extend_next().status, 'EXTENDED')

    def test_reentry_rejects_content_change_and_different_source_or_target(self):
        initial = self.initial()
        with self.assertRaises(ValueError):
            PartialWitness.reenter(initial.snapshot(), self.source, target_id='another')
        with self.assertRaises(ValueError):
            PartialWitness.reenter(initial.snapshot(), FiniteSystem((1, 0, 0)), target_id='fixed-1')
        data = json.loads(initial.snapshot())
        data['pairs'][0][1] = [2, 2, 2]
        with self.assertRaises(ValueError):
            PartialWitness.reenter(json.dumps(data), self.source, target_id='fixed-1')
        with self.assertRaises(ValueError):
            PartialWitness.reenter('{}', self.source, target_id='fixed-1')

    def test_valid_digest_not_sufficient_to_fake_commuting_square(self):
        initial = self.initial()
        pairs = list(initial.pairs)
        pairs[1] = (pairs[1][0], (2, 2, 2))
        forged_pairs = tuple(pairs)
        forged_digest = _hash(_wire(initial.source_phi, initial.target_id,
                                    initial.anchors, forged_pairs, initial.observations))
        forged = replace(initial, pairs=forged_pairs, digest=forged_digest)
        with self.assertRaises(ValueError):
            forged.verify(self.source, target_id='fixed-1')

    def test_oracle_drift_is_detected_if_explicitly_audited(self):
        mutable = {'changed': False}
        def oracle(s, a):
            if mutable['changed'] and (s, a) == (ZERO, 'B'):
                return ZERO
            return self.target.step(s, a)
        proof = self.initial(oracle)
        tracker = Incremental(self.source, oracle, proof, target_id='fixed-1')
        self.assertEqual((tracker.audit_previous().status, tracker.audit_previous().calls),
                         ('PRESERVED', 18))
        mutable['changed'] = True
        result = tracker.audit_previous()
        self.assertEqual(result.status, 'CHANGED')
        self.assertEqual(result.mismatch[0:2], (ZERO, 'B'))
        self.assertEqual(tracker.current.mapped, 9)
        # This change is not magically detected by the no-requery continuation.
        # Reuse depends on stable-source provenance, not just a copied identifier.

    def test_zero_query_budget_does_not_promote_part(self):
        tracker = Incremental(self.source, self.target.step, self.initial(), target_id='fixed-1')
        result = tracker.extend_next(max_new_queries=0)
        self.assertEqual((result.status, result.witness.mapped, result.new_queries),
                         ('UNKNOWN_QUERY_BUDGET', 9, 0))

    def test_existing_full_rooted_is_already_complete(self):
        source = FiniteSystem((1, 0, 2))
        target = ReachedWitness(SourceWitness.establish(CovariantSource.for_law(source.phi))).transport(Shear(2))
        initial = from_discovery(source, discover(source, target.step, full=False), target_id='fully-reachable')
        self.assertEqual(initial.mapped, 27)
        tracker = Incremental(source, target.step, initial, target_id='fully-reachable')
        self.assertEqual(tracker.extend_next().status, 'UNCHANGED')

    def test_reentry_from_incomplete_initial_discovery_fails(self):
        result = discover(self.source, self.target.step, full=True, max_queries=18)
        self.assertEqual(result.status, 'UNKNOWN_QUERY_BUDGET')
        with self.assertRaises(ValueError):
            from_discovery(self.source, result, target_id='fixed-1')


if __name__ == '__main__':
    unittest.main(verbosity=2)
