import json
import sys
import unittest
from work.arc_like_maze.math import World
from interfaces.math.closed_loop import run
from interfaces.math.subprocess_world import SubprocessWorld


class SubprocessWorldTests(unittest.TestCase):
    def make_world(self, phi=(0, 1, 2), reset=True):
        program = (
            "import sys,json; "
            "from work.arc_like_maze.math import World; "
            "req=json.loads(sys.stdin.readline()); "
            f"state=World(3,{phi!r}).apply(req['actions']); "
            f"print(json.dumps(dict(protocol='unstupid-world-v1',reset_confirmed={reset!r},state=state)))"
        )
        return SubprocessWorld((sys.executable, "-c", program), 3)

    def test_external_process_drives_candidate_selection(self):
        a, b = World(3, (0, 1, 2)), World(3, (0, 2, 1))
        outcome = run((a, b), self.make_world())
        self.assertEqual(outcome.survivors, (a,))
        self.assertEqual(outcome.rounds[0].probe, "ABB")

    def test_reset_confirmation_required(self):
        with self.assertRaises(ValueError):
            self.make_world(reset=False)("ABB")

    def test_bad_state_rejected(self):
        command = (sys.executable, "-c", "import json; print(json.dumps(dict(protocol='unstupid-world-v1',reset_confirmed=True,state=[9,9,9])))")
        with self.assertRaises(ValueError):
            SubprocessWorld(command, 3)("ABB")

    def test_invalid_actions_rejected(self):
        with self.assertRaises(ValueError):
            self.make_world()("ABC")


if __name__ == "__main__":
    unittest.main()
