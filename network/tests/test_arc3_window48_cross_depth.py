"""Negative controls for independent WORLD48 cross-depth observation records."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from work.arc3.window48_cross_depth import (
    SCHEMA, SOURCE, build_observation, verify_observation,
)

ROOT = Path(__file__).resolve().parents[2]


class OriginalWorld48CrossDepthObservationTests(unittest.TestCase):
    def test_all_48_original_source_charts_replay_observations(self):
        roster=json.loads((ROOT/"docs/window48_challenges.json").read_text(encoding="utf8"))
        self.assertEqual(len(roster["challenges"]),48)
        for ch in roster["challenges"]:
            with self.subTest(challenge=ch["id"]):
                a,b=ch["example_words"]
                data=build_observation(ch["id"],[a,b],[len(a),len(b)])
                self.assertEqual(data["schema"],SCHEMA)
                self.assertEqual(data["source"],SOURCE)
                self.assertEqual(data["law_ids"],ch["law_ids"])
                self.assertEqual(data["pair_count"],(len(a)+1)*(len(b)+1))
                self.assertEqual(data["candidate_count"],1)
                self.assertEqual(data["first_candidate"]["depths"],[len(a),len(b)])
                report=verify_observation(data)
                self.assertTrue(report["verified"])
                self.assertTrue(report["candidate"])
                self.assertFalse(report["win_certificate"])

    def test_observations_are_not_winning_certificates(self):
        from work.arc3.window48_challenges import verify_certificate
        data=build_observation(2,["BAB","BBBA"],[2,1])
        self.assertFalse(verify_observation(data)["candidate"])
        with self.assertRaises(ValueError):
            verify_certificate(data)

    def test_empty_and_distinct_depths_replay_without_padding(self):
        full=build_observation(1,["","BBB"],[0,3])
        self.assertEqual(full["pair_count"],4)
        self.assertEqual(full["selected_states"][0],[0,0])
        self.assertTrue(verify_observation(full)["candidate"])
        at_root=build_observation(1,["","BBB"],[0,0])
        self.assertEqual(at_root["selected_states"],[[0,0],[0,0]])
        self.assertFalse(verify_observation(at_root)["candidate"])
        self.assertEqual(at_root["candidate_count"],full["candidate_count"])
        self.assertEqual(at_root["first_candidate"],full["first_candidate"])

    def test_honest_nonwinning_paths_can_be_documented(self):
        receipt=build_observation(2,["AA","AA"],[1,2])
        self.assertEqual(receipt["candidate_count"],0)
        self.assertIsNone(receipt["first_candidate"])
        self.assertFalse(verify_observation(receipt)["candidate"])
        self.assertTrue(verify_observation(receipt)["verified"])

    def test_forged_claims_are_rejected_by_original_source(self):
        original=build_observation(2,["BAB","BBBA"],[2,3])
        edits=[
            lambda x: x["selected_states"][0].__setitem__(0,26),
            lambda x: x["selected_depths"].__setitem__(0,99),
            lambda x: x["selected_depths"].__setitem__(1,True),
            lambda x: x["words"].__setitem__(0,"AA"),
            lambda x: x["words"].__setitem__(1,"AB"*70),
            lambda x: x["law_ids"].__setitem__(0,47),
            lambda x: x.__setitem__("challenge_id",47),
            lambda x: x.__setitem__("scope","native-arc"),
            lambda x: x.__setitem__("source","unrelated"),
            lambda x: x.__setitem__("candidate_count",999),
            lambda x: x.__setitem__("pair_count",1),
            lambda x: x.__setitem__("first_candidate",None),
            lambda x: x.__setitem__("schema","original-window48-rooted-collision-certificate/v1"),
            lambda x: x.__setitem__("win",True),
        ]
        for mutate in edits:
            with self.subTest(mutate=mutate):
                forged=deepcopy(original)
                mutate(forged)
                with self.assertRaises(ValueError):
                    verify_observation(forged)

    def test_invalid_action_words_and_depths_fail_closed(self):
        bad_cases=[
            (True,["A","B"],[1,1]),
            (48,["A","B"],[1,1]),
            (0,["A"],[1,0]),
            (0,["A","B"],[1]),
            (0,["A","X"],[1,1]),
            (0,["A","AB"*65],[1,1]),
            (0,["A","B"],[2,1]),
            (0,["A","B"],[-1,1]),
            (0,["A","B"],[True,1]),
            (0,["A","B"],[0.5,1]),
        ]
        for cid,words,depths in bad_cases:
            with self.subTest(args=(cid,words,depths)),self.assertRaises(ValueError):
                build_observation(cid,words,depths)

    def test_schema_has_no_native_result_or_publication_status(self):
        record=build_observation(2,["BAB","BBBA"],[3,4])
        self.assertEqual(
            set(record),
            {"schema","scope","source","challenge_id","law_ids","words",
             "selected_depths","selected_states","pair_count","candidate_count",
             "first_candidate"},
        )
        self.assertNotIn("passed",record)
        self.assertNotIn("published",record)
        self.assertNotIn("win",record)


if __name__ == "__main__":
    unittest.main()
