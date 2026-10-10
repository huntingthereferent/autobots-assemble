"""Focused regression at the repo-style namespaced module entry."""
import json
import unittest
from research.continuity_fifth_couplings import ContinuityFifthCouplingClassifier as C
from research.continuity_fifth_couplings.continuity_classifier import UNKNOWN, NEGATIVE, POSITIVE
from research.continuity_fifth_couplings.core import R, S, A, B, orbit_RS, fingerprint, find_conjugacy

Q1=(0,0,0,0,0,1,0,1,1)
Q2=(0,0,0,0,1,1,0,1,0)

class NamespacedClassificationTests(unittest.TestCase):
    def test_positive_transport_constructs_full_intertwiner(self):
        other=R(Q1)
        witness=C.start(Q1, other, max_features=1)
        self.assertEqual(witness.status,POSITIVE)
        f=witness.record['positive_full_AB_witness']['mapping']
        self.assertEqual(len(set(f)),243)
        b1,b2=B(Q1),B(other)
        self.assertTrue(all(f[A[i]]==A[f[i]] and f[b1[i]]==b2[f[i]] for i in range(243)))
        self.assertEqual(C.replay(witness.serialize()).serialize(),witness.serialize())

    def test_exact_negative_after_inconclusive_prefix(self):
        early=C.start(Q1,Q2,max_features=1)
        self.assertEqual(early.status,UNKNOWN)
        late=C.resume(early.serialize(),max_features=4,expected_question_id=early.question_id)
        self.assertEqual(late.status,NEGATIVE)
        self.assertEqual(late.question_id,early.question_id)
        self.assertEqual(late.record['observations'][:1],early.record['observations'])
        self.assertNotEqual(fingerprint(Q1),fingerprint(Q2))
        actual,trials=find_conjugacy(Q1,Q2)
        self.assertIsNone(actual)
        self.assertEqual(trials,243)

    def test_scope_and_evidence_mutation_refused(self):
        early=C.start(Q1,Q2,max_features=2)
        item=json.loads(early.serialize())
        item['observations'][0]['source_histogram']=[[0,243]]
        with self.assertRaises(ValueError):C.replay(json.dumps(item))
        item=json.loads(early.serialize())
        item['question']['relation']='B_ONLY'
        with self.assertRaises(ValueError):C.replay(json.dumps(item))

    def test_positive_class_preserves_features(self):
        for x in orbit_RS(Q1):
            self.assertEqual(fingerprint(x),fingerprint(Q1))

    def test_original_b_only_engine_is_not_modified(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[2]
        if not (root/'work/arc_like_maze/cyclic_action_engine.py').exists():
            self.skipTest('Exact repository cyclic module not included in standalone installation candidate')
        from work.arc_like_maze.cyclic_action_engine import CyclicActionEngine
        self.assertEqual(len(CyclicActionEngine.fiber(5)),81)

if __name__=='__main__':unittest.main()
