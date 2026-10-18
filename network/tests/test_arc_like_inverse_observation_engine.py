"""Independent tests of native F3 source-law inverse observations."""
import unittest
from itertools import product
from work.arc_like_maze.math import inverse_candidates
from work.arc_like_maze.inverse_observation_engine import (
    Investigation,Observation,minimal_observations_certificate,
)

class InverseObservationEngineTests(unittest.TestCase):
    def test_two_observations_recover_all_nine_phi(self):
        proof=minimal_observations_certificate()
        self.assertEqual(proof["minimum_rooted_observations"],2)
        self.assertEqual(proof["distinct_world_signatures"],9)
        for law in inverse_candidates():
            state=Investigation()
            for word in ("BB","BBB"):
                state=state.admit(Observation(word,law.apply(word)))
            self.assertEqual(tuple(w.phi for w in state.candidates),(law.phi,))
            self.assertEqual(state.receipt()["status"],"IDENTIFIED_WITHIN_F3_FAMILY")

    def test_one_word_cannot_distinguish_nine(self):
        laws=inverse_candidates()
        for length in range(1,7):
            for actions in product("AB",repeat=length):
                self.assertLessEqual(len({w.apply("".join(actions)) for w in laws}),3)

    def test_source_chooses_first_word_and_reidentifies_every_world(self):
        first=Investigation().next_probe()
        self.assertEqual(first.word,"BB")
        self.assertEqual(first.worst_case_survivors,3)
        self.assertEqual(first.eliminated_pairs,27)
        for law in inverse_candidates():
            state=Investigation()
            words=[]
            for _ in range(3):
                probe=state.next_probe()
                if probe is None:
                    break
                words.append(probe.word)
                state=state.admit(Observation(probe.word,law.apply(probe.word)))
            self.assertEqual(len(words),2)
            self.assertEqual(tuple(w.phi for w in state.candidates),(law.phi,))

    def test_candidates_of_each_predicted_outcome_are_exact(self):
        state=Investigation()
        probe=state.next_probe()
        for endpoint,candidates in probe.possible_outcomes:
            self.assertEqual(tuple(w.phi for w in state.candidates
                                   if w.apply(probe.word)==endpoint),candidates)

    def test_conflicts_duplicates_and_incomplete_claims(self):
        state=Investigation().admit(Observation("BB",(0,2,1)))
        self.assertIs(state.admit(Observation("BB",(0,2,1))),state)
        with self.assertRaisesRegex(ValueError,"conflicting repeat"):
            state.admit(Observation("BB",(0,2,2)))
        with self.assertRaisesRegex(ValueError,"duplicated"):
            Investigation((Observation("BB",(0,2,1)),)*2)
        impossible=Investigation().admit(Observation("BB",(2,2,0)))
        self.assertEqual(impossible.receipt()["status"],"CONTRADICTION")
        self.assertIsNone(impossible.next_probe())

    def test_invalid_words_states_and_search_budget(self):
        for word in ("","C","AB-C","A"*13):
            with self.assertRaises(ValueError):
                Observation(word,(0,0,0))
        for endpoint in ((0,0,3),(0,True,0),(0,0),[0,0,0]):
            with self.assertRaises(ValueError):
                Observation("A",endpoint)
        with self.assertRaises(ValueError):
            Investigation().next_probe(9)

    def test_budget_wall_does_not_eliminate_unknown_candidates(self):
        s=Investigation()
        self.assertIsNone(s.next_probe(1))
        self.assertEqual(s.receipt(1)["status"],"OBSERVATION_WALL")
        self.assertEqual(len(s.receipt(1)["remaining_phi"]),9)

    def test_source_rooted_noncommutation_is_preserved(self):
        for w in inverse_candidates():
            self.assertNotEqual(w.apply("AB"),w.apply("BA"))
            self.assertEqual(w.apply("AAA"),w.origin)

if __name__=="__main__":
    unittest.main()
