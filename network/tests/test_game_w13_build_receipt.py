"""BUILD-only W13 two-room contract, native replay and adversarial receipt tests.

No claim of independent WORLD W13 WITNESS or authenticated browser origin.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from systems.workspace import game_construction as w12
from systems.workspace import game_w13_engine as builder
from systems.workspace import game_w13_receipt as w13

ROOT = Path(__file__).resolve().parents[2]
ACTIONS = ["right", "interact", "advance", "right", "interact"]
FIXTURE = ROOT / "evidence" / "game_w13_build_reference.json"


class W13BuildReceiptTests(unittest.TestCase):
    def sample(self):
        return w13.build_reference_receipt(ACTIONS)

    def reject(self, data):
        with self.assertRaises(ValueError):
            w13.verify_session_receipt(data)

    def test_01_byte_pinned_original_w12_source_survives(self):
        digest = sha256(Path(w12.__file__).read_bytes()).hexdigest()
        self.assertEqual(digest, w13.W12_SHA256)

    def test_02_exact_W13_candidate_world_example_agrees(self):
        data = json.loads(
            (ROOT / "network/tests/fixtures/world_w13_movement_01.json").read_text()
        )
        self.assertEqual(data["contract"], w13.VERSION)
        self.assertEqual(data["worlds"], list(w13.WORLDS))
        self.assertEqual(data["actions"], ACTIONS)

    def test_03_saved_build_reference_equals_native_generated_receipt(self):
        stored = json.loads(FIXTURE.read_text())
        self.assertEqual(w13.canonical(stored), w13.canonical(self.sample()))
        self.assertTrue(w13.verify_session_receipt(stored)["solved"])

    def test_04_existing_W13_builder_candidate_matches_native_world_traces(self):
        candidate = builder.play(list(w13.WORLDS), ACTIONS)
        checked = w13.verify_session_receipt(self.sample())
        self.assertEqual(candidate["version"], w13.VERSION)
        self.assertEqual(candidate["worlds_completed"], 2)
        self.assertEqual(candidate["last_world"], "second-room")
        for worker, proof in zip(candidate["worlds"], checked["world_proofs"]):
            self.assertEqual(worker["world_id"], proof["world_id"])
            self.assertEqual(worker["trace"]["head_hash"], proof["head_hash"])
            self.assertTrue(w12.verify_trace(worker["trace"])["valid"])

    def test_05_first_room_collection_does_not_complete_session(self):
        receipt = w13.build_reference_receipt(["right", "interact"])
        result = w13.verify_session_receipt(receipt)
        self.assertEqual(result["worlds_completed"], 1)
        self.assertFalse(result["solved"])
        self.assertFalse(result["boundary_verified"])

    def test_06_second_room_uncollected_does_not_complete_session(self):
        receipt = w13.build_reference_receipt(["right", "interact", "advance", "right"])
        result = w13.verify_session_receipt(receipt)
        self.assertEqual(result["worlds_completed"], 1)
        self.assertTrue(result["boundary_verified"])
        self.assertFalse(result["solved"])

    def test_07_boundary_block_consumes_first_world_turn(self):
        receipt = w13.build_reference_receipt(
            ["left", "right", "interact", "advance", "right", "interact"])
        proof = w13.verify_session_receipt(receipt)
        self.assertTrue(proof["solved"])
        self.assertEqual(receipt["worlds"][0]["observations"][0]["verdict"], "blocked-by-boundary")
        self.assertEqual(receipt["worlds"][0]["observations"][0]["after"]["turns"], 1)
        self.assertEqual(receipt["worlds"][0]["final"]["turns"], 3)
        self.assertEqual(receipt["worlds"][1]["final"]["turns"], 2)

    def test_08_diagonal_interact_remains_out_of_reach(self):
        receipt = w13.build_reference_receipt(
            ["right", "interact", "advance", "interact"])
        result = w13.verify_session_receipt(receipt)
        self.assertFalse(result["solved"])
        self.assertEqual(receipt["worlds"][1]["observations"][0]["verdict"], "out-of-reach")
        self.assertEqual(receipt["worlds"][1]["final"]["turns"], 1)

    def test_09_premature_advance_is_rejected_by_native_builder_and_reference(self):
        with self.assertRaisesRegex(ValueError, "advance"):
            w13.build_reference_receipt(["advance", "right", "interact"])
        with self.assertRaisesRegex(ValueError, "advance"):
            builder.play(list(w13.WORLDS), ["advance", "right", "interact"])

    def test_10_second_advance_is_rejected(self):
        with self.assertRaises(ValueError):
            w13.build_reference_receipt(
                ["right", "interact", "advance", "right", "interact", "advance"])
        self.reject({**self.sample(), "actions": ACTIONS + ["advance"]})

    def test_11_forged_first_world_before_after_and_verdict_fail(self):
        for edit in ("before", "after", "verdict"):
            with self.subTest(edit=edit):
                data = self.sample()
                observation = data["worlds"][0]["observations"][0]
                if edit == "verdict":
                    observation[edit] = "collected"
                else:
                    observation[edit]["x"] = 99
                self.reject(data)

    def test_12_forged_second_world_before_after_and_verdict_fail(self):
        for edit in ("before", "after", "verdict"):
            with self.subTest(edit=edit):
                data = self.sample()
                obs = data["worlds"][1]["observations"][0]
                if edit == "verdict":
                    obs[edit] = "blocked-by-boundary"
                else:
                    obs[edit]["turns"] = 33
                self.reject(data)

    def test_13_borrowing_world_one_identity_or_witness_fails(self):
        data = self.sample()
        data["worlds"][1]["id"] = "first-room"
        self.reject(data)
        data = self.sample()
        data["worlds"][1]["observations"] = deepcopy(data["worlds"][0]["observations"])
        self.reject(data)

    def test_14_changed_spec_type_or_extra_world_rejected(self):
        for field, value in (("height", 4), ("width", 3.0), ("start", [0.0, 0])):
            data = self.sample()
            data["worlds"][1]["spec"][field] = value
            with self.subTest(field=field):
                self.reject(data)
        data = self.sample()
        data["worlds"].append(deepcopy(data["worlds"][1]))
        self.reject(data)

    def test_15_forged_advance_boundary_is_rejected(self):
        for kind in ("wrong_after", "wrong_before", "wrong_destination", "omitted"):
            data = self.sample()
            if kind == "wrong_after":
                data["boundaries"][0]["after"]["state"]["turns"] = 1
            elif kind == "wrong_before":
                data["boundaries"][0]["before"]["state"]["collected"] = False
            elif kind == "wrong_destination":
                data["boundaries"][0]["to_world"] = "first-room"
            else:
                data["boundaries"] = []
            with self.subTest(kind=kind):
                self.reject(data)

    def test_16_mismatched_global_order_rejected(self):
        data = self.sample()
        data["actions"] = ["right", "interact", "right", "advance", "interact"]
        self.reject(data)

    def test_17_unexpected_or_missing_schema_rejected(self):
        for kind in ("extra_outer", "missing_world_final", "extra_obs", "version"):
            data = self.sample()
            if kind == "extra_outer":
                data["native_claim"] = "PASS"
            elif kind == "missing_world_final":
                del data["worlds"][0]["final"]
            elif kind == "extra_obs":
                data["worlds"][1]["observations"][0]["head_hash"] = "pretend"
            else:
                data["version"] = "game-w12"
            with self.subTest(kind=kind):
                self.reject(data)

    def test_18_forged_final_solved_count_or_world_rejected(self):
        for kind in ("solved", "worlds_completed", "world_id", "state"):
            data = self.sample()
            if kind == "solved":
                data["final"]["solved"] = False
            elif kind == "worlds_completed":
                data["final"]["worlds_completed"] = 1
            elif kind == "world_id":
                data["final"]["world_id"] = "first-room"
            else:
                data["final"]["state"]["x"] = 2
            with self.subTest(kind=kind):
                self.reject(data)

    def test_19_reject_second_world_actions_without_advance(self):
        data = w13.build_reference_receipt(["right", "interact"])
        data["worlds"][1]["actions"] = ["right"]
        self.reject(data)

    def test_20_old_W12_strict_verifier_cannot_accept_W13_session(self):
        data = self.sample()
        with self.assertRaises(ValueError):
            w12.verify_browser_receipt(data)
        with self.assertRaises(ValueError):
            w12.verify_expanded_browser_receipt(data)

    def test_21_source_hash_change_is_refused_before_receipt_admission(self):
        data = self.sample()
        with TemporaryDirectory() as tmp:
            fake = Path(tmp) / "game_construction.py"
            fake.write_text("not W12 source")
            with patch.object(w12, "__file__", str(fake)):
                self.reject(data)

    def test_22_all_inputs_remain_unchanged_on_success_or_rejection(self):
        data = self.sample()
        old = deepcopy(data)
        self.assertTrue(w13.verify_session_receipt(data)["valid"])
        self.assertEqual(data, old)
        data["final"]["solved"] = False
        old = deepcopy(data)
        self.reject(data)
        self.assertEqual(data, old)


if __name__ == "__main__":
    unittest.main()
