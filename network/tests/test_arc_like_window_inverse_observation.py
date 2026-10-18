"""Tests for separate 48-law invariant inverse contract (not rooted endpoints)."""
from collections import Counter
from itertools import combinations
import unittest
from work.arc_like_maze.window_combined import family,classify_pair,fixed_word_formula
from work.arc_like_maze.window_inverse_observation import (
    WORDS,Observation,Investigation,measured,certify_partition
)

class WindowInverseTests(unittest.TestCase):
    def test_exact_full_and_rooted_partition_and_source_formula(self):
        proof=certify_partition()
        self.assertEqual((proof["laws"],proof["full_state_classes"],proof["rooted_classes"]),
                         (48,14,16))
        self.assertEqual(proof["full_class_sizes"],[3]*12+[6]*2)
        self.assertEqual(proof["unpointed_nonroot_unordered_pairs"],18)
        for w in family():
            for word in WORDS:
                self.assertEqual(measured(w,word),
                    fixed_word_formula(word,3,w.support,w.pulse,w.balanced))

    def test_adaptive_source_probe_identifies_full_class_in_all_48_cases(self):
        partitions=Counter()
        laws=family()
        for target in laws:
            state=Investigation()
            seen=set()
            for _ in range(5):
                proposal=state.next_probe()
                if proposal is None:break
                self.assertNotIn(proposal["word"],seen)
                seen.add(proposal["word"])
                observed=measured(target,proposal["word"])
                state=state.admit(Observation(proposal["word"],observed))
            self.assertIsNone(state.next_probe())
            expected=set(w for w in laws if all(measured(w,word)==measured(target,word)
                                                 for word in WORDS))
            self.assertEqual(set(state.candidates),expected)
            self.assertIn(target,state.candidates)
            partitions[frozenset(expected)]+=1
            status=state.receipt()["status"]
            if len(expected)==6:
                self.assertEqual(status,"FULL_CLASS_KNOWN_ROOTED_DISTINCTION_OPEN")
                self.assertIsNotNone(state.root_obstruction())
            else:
                self.assertEqual(status,"ROOTED_CLASS_IDENTIFIED_WITHIN_FAMILY")
                self.assertIsNone(state.root_obstruction())
        self.assertEqual(len(partitions),14)
        self.assertEqual(sorted(partitions.values()),[3]*12+[6]*2)

    def test_pairwise_rooted_obstruction_replays_exact_action_words(self):
        from work.arc_like_maze.window_combined import CombinedWorld
        for law in family():
            if law.support not in (0,3) or law.pulse!=1 or law.balanced!=0:
                continue
            s=Investigation(tuple(Observation(word,measured(law,word)) for word in WORDS))
            record=s.root_obstruction()
            self.assertIsNotNone(record)
            a,b=(CombinedWorld(*record[key]) for key in ("source","target"))
            w1,w2=record["same_source_words"]
            self.assertEqual(a.apply((0,0,0),w1),a.apply((0,0,0),w2))
            self.assertNotEqual(b.apply((0,0,0),w1),b.apply((0,0,0),w2))
            self.assertFalse(classify_pair(a,b).root_preserving)

    def test_invalid_and_conflicting_evidence_wall(self):
        with self.assertRaises(ValueError):Observation("BA",4)
        for v in (-1,28,True,2.1):
            with self.assertRaises(ValueError):Observation("B",v)
        s=Investigation().admit(Observation("B",9))
        self.assertIs(s.admit(Observation("B",9)),s)
        with self.assertRaisesRegex(ValueError,"conflicting"):
            s.admit(Observation("B",6))
        with self.assertRaisesRegex(ValueError,"duplicate"):
            Investigation((Observation("B",9),Observation("B",9)))
        impossible=Investigation().admit(Observation("B",1))
        self.assertEqual(impossible.receipt()["status"],"CONTRADICTION")
        self.assertEqual(impossible.candidates,())
        self.assertIsNone(impossible.next_probe())

if __name__=="__main__":unittest.main()
