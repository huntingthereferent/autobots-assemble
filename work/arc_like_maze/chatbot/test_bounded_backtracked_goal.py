"""Independent word enumeration and replay controls for finite backtracking."""
import unittest
from itertools import product
from finite_goal_priority import Law, ROOT, choose
from bounded_backtracked_goal import discover_and_extend

GOAL = (1, 1, 2)

def independent_paths(old, new, goal, max_depth):
    for count in range(max_depth + 1):
        for seq in product("AB", repeat=count):
            word = "".join(seq)
            x = y = ROOT
            f, r, good = {x: y}, {y: x}, True
            for action in word:
                x, nx = old.step(x, action), new.step(y, action)
                if (x in f and f[x] != nx) or (nx in r and r[nx] != x):
                    good = False
                    break
                y = nx
                f[x], r[y] = y, x
            if good and x == goal:
                yield word, y

class BacktrackedWitnessTests(unittest.TestCase):
    def test_goal_outside_both_priorities_but_carried_by_branching(self):
        old, new = Law((0,0,1)), Law((1,0,1))
        _, candidates, _ = choose(old, new, (GOAL,))
        self.assertTrue(all(not c.reached for c in candidates))
        result = discover_and_extend(old, new, GOAL)
        self.assertEqual((result.status, result.goal_word, result.mapped_goal),
                         ("GOAL_CARRIED_FINITE_WITNESS", "ABBBBB", (1,1,1)))
        self.assertIn((result.goal_word, result.mapped_goal),
                      list(independent_paths(old, new, GOAL, 6)))
        self.assertEqual((len(result.paired_states), len(result.admitted_edges),
                          len(result.rejected_extensions)), (27, 42, 12))

    def test_independent_replay_of_admitted_and_rejected(self):
        old, new = Law((0,0,1)), Law((1,0,1))
        result = discover_and_extend(old, new, GOAL)
        forward = dict(result.paired_states)
        for source, action, target, image, target_image in result.admitted_edges:
            self.assertEqual((forward[source], forward[target]), (image, target_image))
            self.assertEqual((old.step(source, action), new.step(image, action)),
                             (target, target_image))
        for left, right, old_equal, new_equal in result.rejected_prefixes:
            self.assertEqual(old_equal, old.follow(left) == old.follow(right))
            self.assertEqual(new_equal, new.follow(left) == new.follow(right))
            self.assertNotEqual(old_equal, new_equal)

    def test_depth_and_search_limits_remain_scoped(self):
        a,b = Law((0,0,1)), Law((1,0,1))
        self.assertEqual(discover_and_extend(a,b,GOAL,depth=5).status, "GOAL_OUTSIDE_DEPTH")
        result = discover_and_extend(a,b,GOAL,max_prefixes=1)
        self.assertEqual(result.status, "UNKNOWN_SEARCH_LIMIT")
        self.assertTrue(result.truncated)

    def test_identical_rules_close_rooted_domain(self):
        a = Law((0,0,1))
        result = discover_and_extend(a,a,GOAL)
        self.assertEqual((len(result.paired_states), len(result.admitted_edges),
                          len(result.rejected_extensions)), (27,54,0))

    def test_bad_limits_rejected(self):
        a,b = Law((0,0,1)), Law((1,0,1))
        for depth in (-1,9,True,1.5):
            with self.assertRaises(ValueError):
                discover_and_extend(a,b,GOAL,depth=depth)
        for limit in (0,2001,True):
            with self.assertRaises(ValueError):
                discover_and_extend(a,b,GOAL,max_prefixes=limit)
        with self.assertRaises(ValueError):
            discover_and_extend(a,b,(4,0,0))

if __name__ == "__main__":
    unittest.main()
