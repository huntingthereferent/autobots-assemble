"""Regressions for source-native mathematical continuation."""
import copy
import unittest
from work.arc_like_maze.native_world_continuation import run, verify
from work.arc_like_maze.window_combined import family


class NativeWorldContinuationTests(unittest.TestCase):
    def test_source_transitions_and_replay(self):
        r = run(law_ids=(0, 1), actions="AAB", repeat=25)
        self.assertTrue(verify(r))
        self.assertEqual(len(r["events"]), 75)
        self.assertEqual(r["events"][0]["after"][0], list(family()[0].step((0, 0, 0), "A")))

    def test_reproducible(self):
        self.assertEqual(run(actions="ABBA", repeat=50), run(actions="ABBA", repeat=50))

    def test_refuse_invalid_feed(self):
        for kw in ({"actions": "AC"}, {"repeat": 0}, {"budget": 2, "repeat": 3},
                   {"law_ids": (0, 0)}, {"law_ids": (48, 1)}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                run(**kw)

    def test_tampering_rejected(self):
        r = run(actions="ABB", repeat=5)
        changed = copy.deepcopy(r)
        changed["events"][0]["after"][0] = [2, 2, 2]
        with self.assertRaises(ValueError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
