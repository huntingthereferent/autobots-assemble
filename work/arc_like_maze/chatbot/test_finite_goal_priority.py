"""Independent finite reference for goal-priority experiment."""
import unittest
from finite_goal_priority import ROOT, Law, extend, choose

def oracle(old, new, order):
    forward, reverse = {ROOT: ROOT}, {ROOT: ROOT}
    queue = [(ROOT, a) for a in order]
    admitted = set()
    rejected = 0
    for source, action in queue:
        image = forward[source]
        target = old.step(source, action)
        new_target = new.step(image, action)
        if (target in forward and forward[target] != new_target or
                new_target in reverse and reverse[new_target] != target):
            rejected += 1
            continue
        admitted.add((source, action, target, image, new_target))
        if target not in forward:
            forward[target], reverse[new_target] = new_target, target
            queue.extend((target, a) for a in order)
    return set(forward.items()), admitted, rejected

class FinitePriorityTests(unittest.TestCase):
    def test_goal_priority(self):
        best, candidates, images = choose(
            Law((0, 0, 1)), Law((1, 0, 1)), ((0, 0, 2),))
        self.assertEqual(best.order, "BA")
        self.assertEqual([len(r.pairing) for r in candidates], [20, 25])
        self.assertEqual([len(r.admitted) for r in candidates], [28, 37])
        self.assertEqual(candidates[0].reached, ())
        self.assertEqual(candidates[1].reached,
                         (((0, 0, 2), (0, 0, 1), "BBBBBB"),))
        self.assertEqual(images, (((0, 0, 2), ((0, 0, 1),)),))

    def test_independent_law_oracle(self):
        pairs = [((0,0,1),(1,0,1)), ((0,0,1),(0,0,0)),
                 ((0,0,1),(0,0,1)), ((0,1,0),(2,1,0))]
        for a, b in pairs:
            for order in ("AB", "BA"):
                with self.subTest(a=a, b=b, order=order):
                    old, new = Law(a), Law(b)
                    r = extend(old, new, order, (ROOT,))
                    pairing, admitted, rejected = oracle(old, new, order)
                    self.assertEqual(set(r.pairing), pairing)
                    self.assertEqual(set(r.admitted), admitted)
                    self.assertEqual(len(r.excluded), rejected)
                    for _, _, _, left, right, old_eq, new_eq in r.excluded:
                        self.assertEqual(old.follow(left) == old.follow(right), old_eq)
                        self.assertEqual(new.follow(left) == new.follow(right), new_eq)
                        self.assertNotEqual(old_eq, new_eq)

    def test_identical_law_closure(self):
        r = extend(Law((0, 0, 1)), Law((0, 0, 1)), "AB", (ROOT,))
        self.assertEqual((len(r.pairing), len(r.admitted), len(r.excluded)),
                         (27, 54, 0))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            extend(Law((0,0,0)), Law((0,0,1)), "AA", (ROOT,))
        with self.assertRaises(ValueError):
            choose(Law((0,0,0)), Law((0,0,1)), ())
        with self.assertRaises(ValueError):
            choose(Law((0,0,0)), Law((0,0,1)), (ROOT, ROOT))

if __name__ == "__main__":
    unittest.main()
