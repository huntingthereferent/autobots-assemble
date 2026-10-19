"""Independent replay and adversarial tests for source-defined WORLD48 challenges."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from work.arc_like_maze.window_combined import family, rooted_conflict
from work.arc3.window48_challenges import (
    CHALLENGE_SCHEMA, SCOPE, check_rooted_paths, rooted_roster,
    verify_certificate,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/window48_challenges.json"
GAME = ROOT / "docs/window48_challenges.html"


def trial(ids, word):
    laws = family()
    states = [(0,0,0),(0,0,0)]
    events = []
    for action in word:
        before = [s[0]*9+s[1]*3+s[2] for s in states]
        states = [laws[ids[i]].step(states[i],action) for i in range(2)]
        after = [s[0]*9+s[1]*3+s[2] for s in states]
        events.append({"action":action,"before":before,"after":after})
    return {"actions":word,"events":events,"final":[s[0]*9+s[1]*3+s[2] for s in states]}


def example_certificate(challenge_id):
    ch = rooted_roster()[challenge_id]
    ids = ch["law_ids"]
    words = ch["example_words"]
    return {
        "schema":CHALLENGE_SCHEMA,"scope":SCOPE,"challenge_id":challenge_id,
        "law_ids":ids,"trials":[trial(ids, word) for word in words],
        "verdict":{"left_collides":True,"right_splits":True,"passed":True}
    }


class OriginalWindow48ChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster = rooted_roster()
        cls.saved = json.loads(MANIFEST.read_text(encoding="utf8"))

    def test_source_generated_16_challenges_are_exactly_published(self):
        self.assertEqual(self.saved["challenges"],self.roster)
        self.assertEqual(self.saved["source"],"work/arc_like_maze/window_combined.py")
        self.assertEqual(self.saved["scope"],SCOPE)
        self.assertEqual(len(self.roster),16)
        self.assertEqual(len({tuple(c["law_ids"]) for c in self.roster}),16)
        self.assertEqual(len({tuple((family()[i].support,family()[i].pulse,family()[i].balanced))
                              for ch in self.roster for i in ch["law_ids"]}),16)

    def test_each_example_is_original_bfs_source_witness(self):
        worlds=family()
        for item in self.roster:
            ids=item["law_ids"]
            expected=rooted_conflict(worlds[ids[0]],worlds[ids[1]])
            self.assertIsNotNone(expected)
            self.assertEqual(item["example_words"],[expected[0],expected[1]])
            self.assertEqual(item["example_source_endpoint"],list(expected[2]))
            self.assertEqual(item["example_target_endpoints"],[list(expected[3]),list(expected[4])])
            witnessed=check_rooted_paths(ids,*item["example_words"])
            self.assertTrue(witnessed["left_collides"])
            self.assertTrue(witnessed["right_splits"])
            self.assertTrue(witnessed["passed"])

    def test_every_source_certificate_replays(self):
        for n in range(16):
            report=verify_certificate(example_certificate(n))
            self.assertTrue(report["verified"])
            self.assertTrue(report["passed"])
            self.assertEqual(report["challenge_id"],n)

    def test_any_other_valid_rooted_witness_can_pass(self):
        ch=self.roster[2]
        w1,w2=ch["example_words"]
        self.assertTrue(check_rooted_paths(ch["law_ids"],w1,w2)["passed"])
        # Source witnesses can be submitted in either order; no fixed-string gate.
        c=example_certificate(2)
        c["trials"].reverse()
        self.assertTrue(verify_certificate(c)["passed"])

    def test_nonwinning_honest_paths_are_not_called_wins(self):
        ids=self.roster[2]["law_ids"]
        words=("A","B")
        observed=check_rooted_paths(ids,*words)
        c={"schema":CHALLENGE_SCHEMA,"scope":SCOPE,"challenge_id":2,"law_ids":ids,
           "trials":[trial(ids,w) for w in words],
           "verdict":{k:observed[k] for k in ("left_collides","right_splits","passed")}}
        self.assertTrue(verify_certificate(c)["verified"])
        self.assertFalse(verify_certificate(c)["passed"])

    def test_forged_certificates_rejected_by_actual_source(self):
        original=example_certificate(2)
        edits=[
            lambda c:c["trials"][0]["events"][0]["after"].__setitem__(0,24),
            lambda c:c["trials"][1]["events"][0]["before"].__setitem__(1,11),
            lambda c:c["trials"][0]["events"][0].__setitem__("action","A"),
            lambda c:c["trials"][0]["final"].__setitem__(0,25),
            lambda c:c["trials"][1].__setitem__("actions","AB"*70),
            lambda c:c["trials"].pop(),
            lambda c:c["law_ids"].__setitem__(0,47),
            lambda c:c.__setitem__("challenge_id",44),
            lambda c:c.__setitem__("scope","native-arc"),
            lambda c:c["verdict"].__setitem__("passed",False),
        ]
        for mutate in edits:
            with self.subTest(mutate=mutate):
                bad=deepcopy(original)
                mutate(bad)
                with self.assertRaises(ValueError):
                    verify_certificate(bad)

    def test_game_html_keeps_exact_source_boundary(self):
        html=GAME.read_text(encoding="utf8")
        for term in ("window48_world_data.json","window48_challenges.json",
                     "Lock path","Check the two paths","Retry challenge",
                     "Export verified certificate","marked origin","finite-mathematical-source-only"):
            self.assertIn(term,html)
        self.assertNotIn("GameState.WIN",html)
        self.assertNotIn("native arcade result",html.lower())


if __name__=="__main__":
    unittest.main()
