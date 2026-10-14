"""Independent full-state tests of transported A/B mathematical witnesses."""
import copy
import unittest
from itertools import product

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_admission_probe import OffOrbitAlteration
from ab_chatbot_structural_witness import CovariantSource, add
from ab_chatbot_witness_transport import (
    E0, E2, E01, F3, Shear, SourceWitness, ReachedWitness, check_external,
)


class TransportTests(unittest.TestCase):
    def test_shear_bijection_and_three_turn_return(self):
        points = tuple(product(F3, repeat=3))
        for c in F3:
            h = Shear(c)
            self.assertEqual(len({h.forward(x) for x in points}), 27)
            self.assertTrue(all(h.inverse(h.forward(x)) == x and
                                h.forward(h.inverse(x)) == x for x in points))
        self.assertEqual(Shear(1).then(Shear(1)).then(Shear(1)), Shear(0))

    def test_conjugacy_both_generators_all_27_phis_three_shears(self):
        for phi in product(F3, repeat=3):
            src = FiniteSystem(phi)
            reached = ReachedWitness(SourceWitness.establish(CovariantSource.for_law(phi)))
            for c in F3:
                now = reached.transport(Shear(c))
                h = Shear(c)
                for x in product(F3, repeat=3):
                    for action in "AB":
                        self.assertEqual(now.step(h.forward(x), action),
                                         h.forward(src.step(x, action)))

    def test_native_relation_transport_all_states(self):
        basis = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        for phi in product(F3, repeat=3):
            start = ReachedWitness(SourceWitness.establish(CovariantSource.for_law(phi)))
            for c in (1, 2):
                now = start.transport(Shear(c))
                for x in product(F3, repeat=3):
                    for t in basis:
                        self.assertEqual(now.step(now.shift(x, t), "A"),
                                         now.shift(now.step(x, "A"), t))
                    self.assertEqual(now.step(now.shift(x, E0), "B"),
                                     now.shift(now.step(x, "B"), E01))
                    self.assertEqual(now.step(now.shift(x, E2), "B"),
                                     now.shift(now.step(x, "B"), E2))

    def test_raw_translation_loses_covariance_after_nonlinear_relabel(self):
        reached = ReachedWitness(SourceWitness.establish(
            CovariantSource.for_law((0, 1, 2)))).transport(Shear(1))
        x = (0, 0, 0)
        self.assertNotEqual(reached.step(add(x, E0), "B"),
                            add(reached.step(x, "B"), E01))
        self.assertEqual(reached.step(reached.shift(x, E0), "B"),
                         reached.shift(reached.step(x, "B"), E01))

    def test_three_anchors_survive_nontrivial_compositions(self):
        src = CovariantSource.for_law((2, 0, 1))
        root = SourceWitness.establish(src)
        reached = ReachedWitness(root)
        for c in (1, 2, 2, 1, 1):
            reached = reached.transport(Shear(c))
            self.assertIs(reached.root, root)
            self.assertEqual(len(reached.root.anchor_record), 3)
            self.assertEqual(len(reached.anchors()), 3)
            for y, expected in reached.anchors():
                self.assertEqual(reached.step(y, "B"), expected)

    def test_native_packet_reentry_and_tamper_rejection(self):
        start = ReachedWitness(SourceWitness.establish(CovariantSource.for_law((0, 1, 2))))
        reached = start.transport(Shear(1)).transport(Shear(1))
        reentered = ReachedWitness.reenter(reached.packet())
        self.assertEqual(reentered.packet(), reached.packet())
        altered = copy.deepcopy(reached.packet())
        altered["anchor_record"][2]["result"][2] = 0
        with self.assertRaisesRegex(ValueError, "observation history"):
            ReachedWitness.reenter(altered)
        altered = copy.deepcopy(reached.packet())
        altered["current_shear"] = 1
        with self.assertRaisesRegex(ValueError, "correspondence"):
            ReachedWitness.reenter(altered)
        altered = copy.deepcopy(reached.packet())
        altered["scope"] = "external-verified"
        with self.assertRaisesRegex(ValueError, "scope"):
            ReachedWitness.reenter(altered)

    def test_invalid_shear_and_unwitnessed_callable_are_rejected(self):
        for c in (-1, 3, True, 1.5):
            with self.assertRaises(ValueError):
                Shear(c)
        root = SourceWitness.establish(CovariantSource.for_law((0, 0, 0)))
        with self.assertRaises(TypeError):
            ReachedWitness(root).transport(lambda x: x)

    def test_external_unknown_cannot_borrow_copied_anchors(self):
        root = SourceWitness.establish(CovariantSource.for_law((0, 0, 0)))
        reached = ReachedWitness(root)
        altered = OffOrbitAlteration()
        self.assertEqual(check_external(reached, altered.step, max_calls=0).status,
                         "UNKNOWN_BUDGET")
        failure = check_external(reached, altered.step)
        self.assertEqual(failure.status, "COUNTEREXAMPLE")
        self.assertEqual(failure.witness[:2], ((0, 0, 1), "B"))

    def test_external_full_verification_requires_full_budget(self):
        root = SourceWitness.establish(CovariantSource.for_law((1, 2, 0)))
        reached = ReachedWitness(root).transport(Shear(1))
        for budget in (0, 3, 53):
            self.assertEqual(check_external(reached, reached.step, max_calls=budget).status,
                             "UNKNOWN_BUDGET")
        self.assertEqual(check_external(reached, reached.step).status,
                         "VERIFIED_AGAINST_NATIVE_TABLE")
        self.assertEqual(check_external(reached, reached.step).calls, 54)

    def test_fabricated_root_proof_does_not_replay(self):
        original = SourceWitness.establish(CovariantSource.for_law((0, 0, 0)))
        fabricated = SourceWitness(original.source, (2, 2, 2), original.anchor_record)
        with self.assertRaisesRegex(ValueError, "source proof"):
            ReachedWitness(fabricated).transport(Shear(1))


if __name__ == "__main__":
    unittest.main()
