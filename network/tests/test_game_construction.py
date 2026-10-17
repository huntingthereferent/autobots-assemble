"""Tests for bounded game adapter. Run from repository root, or bundle root."""
import copy
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "systems" / "workspace" / "game_construction.py"
spec = importlib.util.spec_from_file_location("game_construction_standalone", SOURCE)
game = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = game
spec.loader.exec_module(game)


class GameConstructionTests(unittest.TestCase):
    def test_demo_witness(self):
        trace = game.run_actions(["right", "interact"])
        self.assertTrue(trace["solved"])
        self.assertEqual(trace["steps"][1]["verdict"], "collected")
        self.assertEqual(game.verify_trace(trace)["steps_verified"], 2)

    def test_replay_is_deterministic(self):
        a = game.run_actions(["up", "left", "right", "interact"])
        self.assertEqual(a, game.run_actions(["up", "left", "right", "interact"]))
        self.assertTrue(game.verify_trace(a)["valid"])

    def test_out_of_reach_is_not_a_win(self):
        trace = game.run_actions(["interact"])
        self.assertFalse(trace["solved"])
        self.assertEqual(trace["steps"][0]["verdict"], "out-of-reach")

    def test_boundary_is_recorded(self):
        trace = game.run_actions(["left"])
        self.assertEqual(trace["steps"][0]["verdict"], "blocked-by-boundary")
        self.assertEqual(trace["final"]["turns"], 1)

    def test_tampered_after_state_fails(self):
        trace = game.run_actions(["right", "interact"])
        trace["steps"][0]["after"]["x"] = 3
        with self.assertRaisesRegex(ValueError, "replay mismatch"):
            game.verify_trace(trace)

    def test_tampered_chain_fails(self):
        trace = game.run_actions(["right", "interact"])
        trace["steps"][1]["previous_hash"] = "fake"
        with self.assertRaisesRegex(ValueError, "ancestry"):
            game.verify_trace(trace)

    def test_tampered_verdict_fails(self):
        trace = game.run_actions(["right"])
        trace["steps"][0]["verdict"] = "collected"
        with self.assertRaisesRegex(ValueError, "replay mismatch"):
            game.verify_trace(trace)

    def test_invalid_action_fails(self):
        with self.assertRaises(ValueError):
            game.run_actions(["teleport"])

    def test_browser_receipt_reproduces(self):
        t = game.run_actions(["right", "interact"])
        receipt = {"version": game.VERSION, "actions": [r["action"] for r in t["steps"]],
                   "observations": [{k: row[k] for k in ("action", "after", "verdict")} for row in t["steps"]]}
        self.assertTrue(game.verify_browser_receipt(receipt)["solved"])
        receipt["observations"][0]["after"]["x"] = 0
        with self.assertRaisesRegex(ValueError, "disagrees"):
            game.verify_browser_receipt(receipt)

    def test_spec_scope_guards(self):
        with self.assertRaises(ValueError):
            game.GameSpec(width=0).validate()
        with self.assertRaises(ValueError):
            game.GameSpec(start=(2, 1)).validate()
        with self.assertRaises(ValueError):
            game.GameSpec(width=True).validate()

    def test_empty_trace_is_valid_but_not_solved(self):
        t = game.run_actions([])
        self.assertTrue(game.verify_trace(t)["valid"])
        self.assertFalse(t["solved"])


if __name__ == "__main__":
    unittest.main()
