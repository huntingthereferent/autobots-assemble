"""W12 receipt-schema boundary only. Original native game tests stay unchanged."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "systems" / "workspace" / "game_construction.py"
spec = importlib.util.spec_from_file_location("game_compatibility_standalone", SOURCE)
game = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = game
spec.loader.exec_module(game)


def expanded(actions):
    trace = game.run_actions(actions)
    return {
        "version": trace["version"],
        "spec": json.loads(game.canonical(trace["spec"])),
        "actions": list(actions),
        "observations": [
            {k: copy.deepcopy(row[k]) for k in ("action", "before", "after", "verdict")}
            for row in trace["steps"]
        ],
        "final": copy.deepcopy(trace["final"]),
    }


def strict_projection(receipt):
    return {
        "version": receipt["version"],
        "actions": receipt["actions"],
        "observations": [
            {k: row[k] for k in ("action", "after", "verdict")}
            for row in receipt["observations"]
        ],
    }


class ExpandedReceiptCompatibilityTests(unittest.TestCase):
    def rejected(self, receipt, pattern=None):
        if pattern is None:
            with self.assertRaises(ValueError):
                game.verify_expanded_browser_receipt(receipt)
        else:
            with self.assertRaisesRegex(ValueError, pattern):
                game.verify_expanded_browser_receipt(receipt)

    def test_success_returns_exact_original_native_result_and_preserves_input(self):
        receipt = expanded(["right", "interact"])
        before = copy.deepcopy(receipt)
        expected = game.verify_browser_receipt(strict_projection(receipt))
        actual = game.verify_expanded_browser_receipt(receipt)
        self.assertEqual(actual, expected)
        self.assertEqual(receipt, before)
        self.assertEqual(actual["native_trace"]["final"], {"x": 1, "y": 1, "collected": True, "turns": 2})
        self.assertTrue(game.verify_trace(actual["native_trace"])["valid"])

    def test_boundary_turn_C1_survives(self):
        receipt = expanded(["left", "right", "interact"])
        proof = game.verify_expanded_browser_receipt(receipt)
        self.assertEqual(proof["steps_verified"], 3)
        self.assertTrue(proof["solved"])
        self.assertEqual(proof["native_trace"]["steps"][0]["verdict"], "blocked-by-boundary")
        self.assertEqual(proof["native_trace"]["steps"][0]["after"]["turns"], 1)

    def test_out_of_reach_keeps_unsolved(self):
        self.assertFalse(game.verify_expanded_browser_receipt(expanded(["interact"]))["solved"])

    def test_empty_receipt_is_valid_not_solved(self):
        proof = game.verify_expanded_browser_receipt(expanded([]))
        self.assertEqual(proof["steps_verified"], 0)
        self.assertFalse(proof["solved"])

    def test_before_must_equal_previous_after(self):
        receipt = expanded(["right", "interact"])
        receipt["observations"][1]["before"]["x"] = 0
        self.rejected(receipt, "before disagrees")

    def test_initial_before_must_match_world(self):
        receipt = expanded(["right"])
        receipt["observations"][0]["before"]["x"] = 1
        self.rejected(receipt, "before disagrees")

    def test_final_must_match_native_replay(self):
        receipt = expanded(["right", "interact"])
        receipt["final"]["collected"] = False
        self.rejected(receipt, "final disagrees")

    def test_missing_before_rejected(self):
        receipt = expanded(["right"])
        del receipt["observations"][0]["before"]
        self.rejected(receipt, "unexpected or missing keys")

    def test_missing_before_state_field_rejected(self):
        receipt = expanded(["right"])
        del receipt["observations"][0]["before"]["turns"]
        self.rejected(receipt, "unexpected or missing keys")

    def test_missing_final_and_spec_rejected(self):
        for field in ("final", "spec"):
            with self.subTest(field=field):
                receipt = expanded(["right"])
                del receipt[field]
                self.rejected(receipt, "unexpected or missing keys")

    def test_spec_mismatch_rejected(self):
        for field, value in (("width", 5), ("start", [1, 1]), ("target", [3, 1]), ("height", 2)):
            with self.subTest(field=field):
                receipt = expanded(["right"])
                receipt["spec"][field] = value
                self.rejected(receipt, "spec disagrees")

    def test_spec_type_mismatch_rejected_not_coerced(self):
        receipt = expanded(["right"])
        receipt["spec"]["width"] = 4.0
        self.rejected(receipt, "spec disagrees")

    def test_final_type_mismatch_rejected_not_coerced(self):
        receipt = expanded(["right"])
        receipt["final"]["collected"] = 0
        self.rejected(receipt, "final disagrees")

    def test_mismatched_after_rejected_by_native(self):
        receipt = expanded(["right"])
        receipt["observations"][0]["after"]["x"] = 0
        self.rejected(receipt, "disagrees with native replay")

    def test_mismatched_verdict_rejected_by_native(self):
        receipt = expanded(["right"])
        receipt["observations"][0]["verdict"] = "collected"
        self.rejected(receipt, "disagrees with native replay")

    def test_actions_and_observations_must_match(self):
        receipt = expanded(["right", "interact"])
        receipt["actions"].pop()
        self.rejected(receipt, "observation count mismatch")

    def test_unknown_and_missing_extension_fields_rejected(self):
        receipt = expanded(["right"])
        receipt["secret"] = True
        self.rejected(receipt, "unexpected or missing keys")
        receipt = expanded(["right"])
        receipt["observations"][0]["secret"] = True
        self.rejected(receipt, "unexpected or missing keys")

    def test_empty_or_malformed_observations_rejected(self):
        receipt = expanded(["right"])
        receipt["observations"] = []
        self.rejected(receipt, "observation count mismatch")
        receipt["observations"] = "bad"
        self.rejected(receipt, "must be a list")

    def test_original_strict_verifier_stays_strict(self):
        with self.assertRaisesRegex(ValueError, "browser receipt has unexpected or missing keys"):
            game.verify_browser_receipt(expanded(["right"]))
        self.assertTrue(game.verify_browser_receipt(strict_projection(expanded(["right"])))['valid'])

    def test_direct_saved_movement2_export(self):
        fixture = ROOT / 'evidence' / 'export_success.json'
        receipt = json.loads(fixture.read_text(encoding='utf-8'))
        self.assertTrue(game.verify_expanded_browser_receipt(receipt)['solved'])
        self.assertEqual(len(receipt['observations']), 2)

    def test_new_cli_accepts_expanded_and_old_cli_rejects(self):
        command = [sys.executable, str(SOURCE)]
        fixture = str(ROOT / 'evidence' / 'export_success.json')
        new = subprocess.run(command + ['verify-browser-expanded', '--receipt', fixture],
                             capture_output=True, text=True)
        self.assertEqual(new.returncode, 0, new.stderr)
        self.assertEqual(json.loads(new.stdout)['steps_verified'], 2)
        old = subprocess.run(command + ['verify-browser', '--receipt', fixture],
                             capture_output=True, text=True)
        self.assertNotEqual(old.returncode, 0)
        self.assertIn('unexpected or missing keys', old.stderr)


if __name__ == '__main__':
    unittest.main()
