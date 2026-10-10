"""Continuity Engine entry/re-entry, using native Cyclic Action math."""
import json
import unittest
from itertools import product
from research.continuity_engine import ContinuityEngine
from work.arc_like_maze.cyclic_action_engine import CyclicActionEngine
from work.arc_like_maze.window_two import WindowProcess

Z = (0,) * 9
Q0 = tuple(int(y == 2) for x, y in product(range(3), repeat=2))
Q1 = tuple(int(x == 2 and y == 2) for x, y in product(range(3), repeat=2))
DOUBLE = tuple(2 * n % 3 for n in Q1)
W9 = WindowProcess(1, (Q0, Z), (Z,))
W27 = WindowProcess(1, (Q0, Q1), (Z,))
W27S = WindowProcess(1, (Q0, DOUBLE), (Z,))
CARRIER = CyclicActionEngine.fiber(5)


class ContinuityHandoffTests(unittest.TestCase):
    def setUp(self):
        self.engine = ContinuityEngine()

    def test_start_and_continue_negative_witness(self):
        a = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        self.assertEqual(a.status, "UNKNOWN_BUDGET")
        b = self.engine.resume(a.serialize(), 9, expected_question_id=a.question_id)
        self.assertEqual((b.status, b.powers_examined),
                         ("DISTINGUISHED_B_ACTIONS", 9))
        self.assertEqual(len(b.snapshots), 2)
        self.assertEqual(self.engine.verify(b.serialize()).status, b.status)
        self.assertEqual(b.research_question, a.research_question)
        self.assertEqual(b.scope, "B_ONLY_ON_DECLARED_INVARIANT_CARRIER")

    def test_positive_map_never_claims_AB(self):
        a = self.engine.start_cyclic(W27, W27S, CARRIER, 26)
        self.assertEqual(a.status, "UNKNOWN_BUDGET")
        b = self.engine.resume(a.serialize(), 27)
        self.assertEqual(b.status, "B_ONLY_CONJUGACY_WITNESSED")
        self.assertEqual(len(b.witness), 81)
        self.assertEqual(json.loads(b.snapshots[-1]["payload"])["simultaneous_A_B"],
                         "UNKNOWN_NOT_WATCHED")

    def test_witness_replay_rejects_changed_observation(self):
        a = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        raw = json.loads(a.serialize())
        data = json.loads(raw["snapshots"][0]["payload"])
        data["observations"][0]["source_anchor_image"][1] = 2
        from research.continuity_engine import _hash, _wire
        raw["snapshots"][0]["payload"] = _wire(data)
        raw["snapshots"][0]["sha256"] = _hash(_wire(data))
        with self.assertRaises(ValueError):
            self.engine.verify(_wire(raw))

    def test_original_history_replacement_is_rejected(self):
        a = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        b = self.engine.resume(a.serialize(), 9)
        raw = json.loads(b.serialize())
        raw["snapshots"].reverse()
        with self.assertRaises(ValueError):
            self.engine.verify(json.dumps(raw))

    def test_tampered_area_scope_and_anchor_fail(self):
        a = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        for key, replacement in (("area", "physics"),
                                 ("scope", "SIMULTANEOUS_AB"),
                                 ("question_id", "wrong")):
            raw = json.loads(a.serialize())
            raw[key] = replacement
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.engine.verify(json.dumps(raw))
        with self.assertRaises(ValueError):
            self.engine.verify(a.serialize(), expected_question_id="wrong")

    def test_budget_cannot_move_backward(self):
        a = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        with self.assertRaises(ValueError):
            self.engine.resume(a.serialize(), 7)

    def test_terminal_distinction_persists(self):
        b = self.engine.start_cyclic(W9, W27, CARRIER, 9)
        c = self.engine.resume(b.serialize(), 27)
        self.assertEqual(c.status, "DISTINGUISHED_B_ACTIONS")
        self.assertEqual(c.powers_examined, 9)
        self.assertEqual(self.engine.resume(c.serialize(), 27).serialize(), c.serialize())

    def test_only_admitted_area_exposed(self):
        self.assertEqual(self.engine.supported_areas(), ("cyclic_action/B",))

    def test_dimension_is_not_fixed_in_outer_engine(self):
        c = CyclicActionEngine.fiber(6)
        a = self.engine.start_cyclic(W9, W9, c, 3)
        self.assertEqual(len(a.research_question["carrier"]), 243)
        self.assertEqual(a.status, "UNKNOWN_BUDGET")


if __name__ == "__main__":
    unittest.main()
