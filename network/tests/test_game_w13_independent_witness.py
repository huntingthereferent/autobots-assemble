"""W13 WITNESS controls: independent W12 replay; no BUILD W13 import."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from network.witness_w13_independent import (
    W12_SOURCE_SHA256, WORLD_CONTRACT, independent_w13_replay, strict_json,
)
from systems.workspace import game_construction as original_w12

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evidence" / "game_w13_build_reference.json"


class IndependentW13WitnessTests(unittest.TestCase):
    def sample(self):
        return strict_json(RECEIPT.read_text(encoding="utf8"))

    def fail(self, case):
        with self.assertRaises(ValueError):
            independent_w13_replay(case)

    def test_01_source_is_original_byte_preserved_W12(self):
        from hashlib import sha256
        self.assertEqual(sha256(Path(original_w12.__file__).read_bytes()).hexdigest(), W12_SOURCE_SHA256)

    def test_02_W13_worlds_match_declared_WORLD_contract(self):
        self.assertEqual(WORLD_CONTRACT[0][0], "first-room")
        self.assertEqual(WORLD_CONTRACT[1][0], "second-room")
        world = self.sample()
        self.assertEqual([(v["id"], v["spec"]) for v in world["worlds"]], list(WORLD_CONTRACT))

    def test_03_positive_build_sample_independently_replays(self):
        result = independent_w13_replay(self.sample())
        self.assertTrue(result["valid"])
        self.assertTrue(result["solved"])
        self.assertEqual(result["worlds_completed"], 2)
        self.assertEqual(result["boundaries_checked"], 1)
        self.assertFalse(result["browser_origin_authenticated"])
        self.assertFalse(result["w13_checkpoint_promoted"])

    def test_04_preserved_first_room_native_trace_has_original_hash(self):
        result = independent_w13_replay(self.sample())
        original = original_w12.run_actions(["right", "interact"])
        self.assertEqual(result["per_world"][0]["native_head_hash"], original["head_hash"])

    def test_05_preserved_second_world_native_trace_has_original_hash(self):
        result = independent_w13_replay(self.sample())
        spec = original_w12.GameSpec(3, 3, (0, 0), (1, 1))
        original = original_w12.run_actions(["right", "interact"], spec)
        self.assertEqual(result["per_world"][1]["native_head_hash"], original["head_hash"])

    def test_06_blocked_first_move_w12_turn_verdict_replays(self):
        obj = self.sample()
        original = original_w12.run_actions(["left", "right", "interact"])
        obs = [{k: step[k] for k in ("action", "before", "after", "verdict")}
               for step in original["steps"]]
        obj["actions"].insert(0, "left")
        obj["worlds"][0]["actions"].insert(0, "left")
        obj["worlds"][0]["observations"] = obs
        obj["worlds"][0]["final"] = original["final"]
        obj["boundaries"][0]["before"]["state"] = original["final"]
        self.assertTrue(independent_w13_replay(obj)["solved"])
        self.assertEqual(obs[0]["verdict"], "blocked-by-boundary")
        self.assertEqual(obs[0]["after"]["turns"], 1)

    def test_07_first_world_only_is_not_full_session(self):
        data = self.sample()
        data["actions"] = ["right", "interact"]
        data["boundaries"] = []
        data["worlds"][1]["actions"] = []
        data["worlds"][1]["observations"] = []
        data["worlds"][1]["final"] = {"x": 0, "y": 0, "turns": 0, "collected": False}
        data["final"] = {"world_id": "first-room", "state": data["worlds"][0]["final"],
                         "worlds_completed": 1, "solved": False}
        self.assertFalse(independent_w13_replay(data)["solved"])

    def test_08_advance_before_collection_forbidden(self):
        case = self.sample()
        case["actions"] = ["advance"] + case["actions"]
        self.fail(case)

    def test_09_repeated_advance_forbidden(self):
        case = self.sample()
        case["actions"].append("advance")
        self.fail(case)

    def test_10_diagonal_interact_cannot_be_claimed_as_collection(self):
        data = self.sample()
        data["actions"] = ["right", "interact", "advance", "interact"]
        trace = original_w12.run_actions(["interact"], original_w12.GameSpec(3, 3, (0, 0), (1, 1)))
        data["worlds"][1]["actions"] = ["interact"]
        data["worlds"][1]["observations"] = [
            {k: step[k] for k in ("action", "before", "after", "verdict")}
            for step in trace["steps"]
        ]
        data["worlds"][1]["final"] = trace["final"]
        data["final"] = {"world_id": "second-room", "state": trace["final"],
                         "worlds_completed": 1, "solved": False}
        result = independent_w13_replay(data)
        self.assertEqual(data["worlds"][1]["observations"][0]["verdict"], "out-of-reach")
        self.assertFalse(result["solved"])
        self.assertEqual(result["worlds_completed"], 1)

    def test_11_falsified_first_room_observations(self):
        for part in ("before", "after", "verdict"):
            with self.subTest(part=part):
                data = self.sample()
                obs = data["worlds"][0]["observations"][0]
                if part == "verdict":
                    obs["verdict"] = "collected"
                else:
                    obs[part]["turns"] = 99
                self.fail(data)

    def test_12_falsified_second_room_observations(self):
        for part in ("before", "after", "verdict"):
            with self.subTest(part=part):
                data = self.sample()
                obs = data["worlds"][1]["observations"][0]
                if part == "verdict":
                    obs["verdict"] = "blocked-by-boundary"
                else:
                    obs[part]["x"] = -5
                self.fail(data)

    def test_13_changed_first_world_spec_or_version(self):
        for mode in ("target", "width", "float", "version"):
            with self.subTest(mode=mode):
                data = self.sample()
                if mode == "target":
                    data["worlds"][0]["spec"]["target"] = [3, 1]
                elif mode == "width":
                    data["worlds"][0]["spec"]["width"] = 5
                elif mode == "float":
                    data["worlds"][0]["spec"]["width"] = 4.0
                else:
                    data["worlds"][0]["version"] = "game-invented"
                self.fail(data)

    def test_14_duplicate_world_or_borrowed_first_world_proof(self):
        for mode in ("id", "spec", "observations"):
            with self.subTest(mode=mode):
                data = self.sample()
                data["worlds"][1][mode] = deepcopy(data["worlds"][0][mode])
                self.fail(data)

    def test_15_tampered_boundary_from_and_to(self):
        for mode in ("from_world", "to_world", "before", "after"):
            with self.subTest(mode=mode):
                data = self.sample()
                item = data["boundaries"][0]
                if mode in ("from_world", "to_world"):
                    item[mode] = "invented"
                else:
                    item[mode]["state"]["x"] = 99
                self.fail(data)

    def test_16_missing_or_extra_boundary_rejected(self):
        data = self.sample()
        data["boundaries"] = []
        self.fail(data)
        data = self.sample()
        data["boundaries"].append(deepcopy(data["boundaries"][0]))
        self.fail(data)

    def test_17_false_session_completion_or_world_count(self):
        for mode in ("solved", "worlds_completed", "world_id", "state"):
            with self.subTest(mode=mode):
                data = self.sample()
                if mode == "solved":
                    data["final"]["solved"] = False
                elif mode == "worlds_completed":
                    data["final"]["worlds_completed"] = 1
                elif mode == "world_id":
                    data["final"]["world_id"] = "first-room"
                else:
                    data["final"]["state"]["turns"] = 3
                self.fail(data)

    def test_18_bad_global_action_order_rejected(self):
        data = self.sample()
        data["actions"] = ["right", "interact", "right", "advance", "interact"]
        self.fail(data)

    def test_19_local_actions_or_observations_cannot_be_lent(self):
        data = self.sample()
        data["worlds"][1]["actions"] = ["interact", "right"]
        self.fail(data)
        data = self.sample()
        data["worlds"][1]["observations"] = deepcopy(data["worlds"][0]["observations"])
        self.fail(data)

    def test_20_unknown_and_non_string_actions_rejected(self):
        for action in ("teleport", None, 1, 3.0, {"action": "right"}):
            with self.subTest(action=action):
                data = self.sample()
                data["actions"][0] = action
                self.fail(data)

    def test_21_shape_missing_and_extra_fields_rejected(self):
        for kind in ("session_missing", "session_extra", "world_extra", "local_missing", "more_worlds"):
            with self.subTest(kind=kind):
                data = self.sample()
                if kind == "session_missing":
                    del data["actions"]
                elif kind == "session_extra":
                    data["native_authorized"] = True
                elif kind == "world_extra":
                    data["worlds"][0]["claim"] = True
                elif kind == "local_missing":
                    del data["worlds"][1]["observations"][0]["before"]["turns"]
                else:
                    data["worlds"].append(deepcopy(data["worlds"][1]))
                self.fail(data)

    def test_22_w12_only_verifiers_still_reject_W13_envelope(self):
        data = self.sample()
        with self.assertRaises(ValueError):
            original_w12.verify_browser_receipt(data)
        with self.assertRaises(ValueError):
            original_w12.verify_expanded_browser_receipt(data)

    def test_23_source_fingerprint_change_rejected(self):
        data = self.sample()
        with TemporaryDirectory() as tmp:
            changed = Path(tmp) / "game_construction.py"
            changed.write_text("not original W12")
            with patch.object(original_w12, "__file__", str(changed)):
                self.fail(data)

    def test_24_input_never_repaired_mutated_or_reused(self):
        data = self.sample()
        old = deepcopy(data)
        independent_w13_replay(data)
        self.assertEqual(data, old)
        data["worlds"][1]["final"]["x"] = 999
        old = deepcopy(data)
        self.fail(data)
        self.assertEqual(data, old)

    def test_25_strict_parser_rejects_duplicate_json_keys_and_nan(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict_json(raw)

    def test_26_manifested_candidate_example_still_W12_scoped(self):
        data = self.sample()
        self.assertEqual(data["version"], "game-w13-multiworld-v1")
        proof = independent_w13_replay(data)
        self.assertEqual(proof["source_sha256"], W12_SOURCE_SHA256)
        self.assertFalse(proof["w13_checkpoint_promoted"])


if __name__ == "__main__":
    unittest.main()
