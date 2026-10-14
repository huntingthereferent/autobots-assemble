"""Bounded same-target/changed-target witness tests in the F3 mathematical model."""
import unittest
from dataclasses import replace
from itertools import product

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import DOMAIN, discover
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_pinned_identity import (
    KEYS, OwnedVersions, PinnedView, table_digest, mutable_scan_counterexample,
    unbound_external_identity,
)


class PinnedIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = FiniteSystem((0, 0, 0))
        cls.h = tuple((i, j, (k+i*j)%3) for i,j,k in DOMAIN)

    def setUp(self):
        self.owner = OwnedVersions(TransportedLaw(self.src.phi, self.h))
        self.old = self.owner.pin()
        self.discovered = discover(self.src, self.old.step, full=True)
        self.assertEqual(self.discovered.status, 'FULL_CONJUGACY')
        self.bound = self.owner.bind(self.src, self.discovered, self.old)

    def test_same_pinned_version_reuses_witness_without_rereading(self):
        r = self.owner.reenter(self.src, self.discovered, self.bound)
        self.assertEqual((r.status, r.inspected_edges), ('SAME_PINNED_VERSION', 0))
        self.assertTrue(self.owner.current(self.old))

    def test_a_new_law_does_not_borrow_old_correspondence(self):
        self.owner.replace(TransportedLaw((0, 2, 1), self.h))
        result = self.owner.reenter(self.src, self.discovered, self.bound)
        self.assertEqual(result.status, 'CHANGED')
        self.assertIsNotNone(result.mismatch)
        self.assertFalse(self.owner.current(self.old))
        self.assertEqual(self.owner.reenter(self.src, self.discovered, self.bound, current=self.old).status,
                         'SAME_PINNED_VERSION')  # historical, NOT current live

    def test_same_table_across_new_epoch_does_not_certify_uninterrupted_history(self):
        self.owner.replace(TransportedLaw((0, 1, 2), self.h))
        self.owner.replace(TransportedLaw((0, 0, 0), self.h))
        r = self.owner.reenter(self.src, self.discovered, self.bound)
        self.assertEqual((r.status, r.inspected_edges), ('SAME_ENDPOINT_LAW_NEW_VERSION', 54))
        self.assertNotEqual(self.owner.pin().version, self.old.version)
        self.assertEqual(self.owner.pin().digest, self.old.digest)
        self.assertIn('intervening', r.scope)

    def test_even_an_identical_replace_changes_revision(self):
        self.owner.replace(TransportedLaw(self.src.phi, self.h))
        self.assertEqual(self.owner.reenter(self.src, self.discovered, self.bound).status,
                         'SAME_ENDPOINT_LAW_NEW_VERSION')

    def test_pinned_historical_view_is_immutable_and_replayable(self):
        old_values = self.old.values
        self.owner.replace(TransportedLaw((0, 1, 0), self.h))
        self.assertEqual(self.old.values, old_values)
        self.assertTrue(all(self.old.step(s,a) == v for (s,a),v in zip(KEYS,old_values)))
        with self.assertRaises(AttributeError):
            self.old.version = 32

    def test_54_step_unfrozen_scan_misses_a_temporal_change(self):
        result, calls, actually_changed = mutable_scan_counterexample(self.src, self.discovered, self.old)
        self.assertEqual((result.status, calls, actually_changed),
                         ('OBSERVED_FULL_TABLE_MATCH',54,True))

    def test_copied_or_other_owner_view_is_not_a_source_owned_proof(self):
        copy = PinnedView(self.old.version,self.old.values,self.old.digest)
        with self.assertRaises(ValueError):
            self.owner.bind(self.src,self.discovered,copy)
        other = OwnedVersions(TransportedLaw(self.src.phi,self.h))
        self.assertEqual(other.reenter(self.src,self.discovered,self.bound).status,'UNKNOWN_UNBOUND')
        self.assertEqual(self.owner.reenter(self.src,self.discovered,replace(self.bound,view=copy)).status,
                         'UNKNOWN_UNBOUND')

    def test_tampered_witness_and_wrong_source_cannot_reenter(self):
        self.assertEqual(self.owner.reenter(FiniteSystem((1,0,0)),self.discovered,self.bound).status,
                         'WALL_INVALID')
        self.assertEqual(self.owner.reenter(self.src,self.discovered,replace(self.bound, proof_digest='fake')).status,
                         'WALL_INVALID')
        partial = discover(self.src,self.old.step,full=False)
        self.assertEqual(self.owner.reenter(self.src,partial,self.bound).status,'WALL_INVALID')

    def test_different_old_view_cannot_admit_prior_discovery(self):
        changed = self.owner.replace(TransportedLaw((0,2,2),self.h))
        with self.assertRaises(ValueError):
            self.owner.bind(self.src,self.discovered,changed)

    def test_hash_revision_target_string_alone_is_insufficient(self):
        r = unbound_external_identity('owner-X',0,self.old.digest)
        self.assertEqual(r.status,'UNKNOWN_UNBOUND')
        self.assertEqual(r.inspected_edges,0)

    def test_all_27_constructed_source_laws_have_pinned_tables(self):
        self.assertEqual(len(KEYS),54)
        signatures=set()
        for phi in product(range(3),repeat=3):
            target = TransportedLaw(phi,self.h)
            v=self.owner.replace(target)
            self.assertEqual(table_digest(v.values),v.digest)
            self.assertEqual(v.values,tuple(target.step(s,a) for s,a in KEYS))
            signatures.add(v.digest)
        self.assertEqual(len(signatures),27)

    def test_invalid_external_callback_cannot_be_pinned(self):
        with self.assertRaises(ValueError):
            OwnedVersions(lambda s,a: self.old.step(s,a))
        with self.assertRaises(ValueError):
            self.owner.replace(lambda s,a: self.old.step(s,a))

    def test_corrupted_source_record_is_rejected(self):
        altered=replace(self.discovered,status='ROOTED_REACHABLE')
        with self.assertRaises(ValueError):
            self.owner.bind(self.src,altered,self.old)
        self.assertEqual(self.owner.reenter(self.src,altered,self.bound).status,'WALL_INVALID')

    def test_wrong_h_construction_does_not_silently_match(self):
        # Same phi, a different invertible relabeling; full table may differ.
        wrong=TransportedLaw(self.src.phi,tuple(DOMAIN))
        self.owner.replace(wrong)
        r=self.owner.reenter(self.src,self.discovered,self.bound)
        self.assertEqual(r.status,'CHANGED')


if __name__ == '__main__':
    unittest.main()
