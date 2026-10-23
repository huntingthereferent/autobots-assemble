import sys
import unittest
from pathlib import Path
from work.arc_like_maze.math import World, inverse_candidates
from interfaces.math.closed_loop import run
from interfaces.math.subprocess_world import SubprocessWorld

WORLD_SCRIPT = str(Path(__file__).with_name("independent_world.py"))


def external(phi=(0, 1, 2), mutant=False):
    cmd = (sys.executable, WORLD_SCRIPT, "--phi", ",".join(map(str, phi)))
    if mutant:
        cmd += ("--mutant",)
    return SubprocessWorld(cmd, 3)


class IndependentWorldTests(unittest.TestCase):
    def test_independent_normal_world_matches_finite_construction(self):
        a, b = World(3, (0, 1, 2)), World(3, (0, 2, 1))
        result = run((a, b), external())
        self.assertEqual(result.survivors, (a,))
        self.assertEqual(result.rounds[0].probe, "ABB")

    def test_independent_alternate_world_is_identified(self):
        a, b = World(3, (0, 1, 2)), World(3, (0, 2, 1))
        result = run((a, b), external((0, 2, 1)))
        self.assertEqual(result.survivors, (b,))

    def test_mutant_world_is_detected_outside_candidate_set(self):
        result = run(inverse_candidates(), external(mutant=True))
        self.assertEqual(result.status, "MODEL_SET_EXHAUSTED")
        self.assertEqual(result.survivors, ())
        self.assertTrue(result.rounds)

    def test_external_matches_reference_on_varied_action_paths(self):
        world = World(3, (0, 1, 2))
        runner = external()
        for actions in ("", "A", "B", "ABB", "BBAA", "ABABB", "BABABBA"):
            with self.subTest(actions=actions):
                self.assertEqual(runner(actions), world.apply(actions))


if __name__ == "__main__":
    unittest.main()
