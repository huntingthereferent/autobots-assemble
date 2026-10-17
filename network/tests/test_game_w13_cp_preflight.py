"""Coordinator W13 preflight unit tests; fixtures are NOT actual browser exports.

Only the dedicated Actions job supplies the two actual prior Chromium artifact
collections and pins the GitHub run and artifact identities.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.cp_motion import checkpoint_frontier
from systems.workspace.game_w13_cp_preflight import (
    ARTIFACTS, BUILD_NEGATIVES, CP, SOURCE_BLOBS, WITNESS_NEGATIVES,
    _git_blob_digest, assess_game_evidence, verify_source_identity,
)

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = json.loads((ROOT / "evidence/game_w13_build_reference.json").read_text())


class W13CoordinatorPreflightTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.build = self.root / "build"
        self.witness = self.root / "witness"
        self.build.mkdir()
        self.witness.mkdir()
        self._make_evidence()

    def write(self, directory, name, data):
        (directory / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf8")

    def _corrupt(self, case):
        data = deepcopy(ORIGINAL)
        if case == "boundary" or case == "crossing":
            data["boundaries"][0]["after"]["state"]["x"] = 44
        elif case == "final" or case == "session-final":
            data["final"]["solved"] = False
        elif case == "first-room":
            data["worlds"][0]["observations"][0]["before"]["turns"] = 99
        elif case == "second-room":
            data["worlds"][1]["observations"][0]["after"]["x"] = -1
        elif case == "global":
            data["actions"][2] = "right"
        elif case == "world-before":
            data["worlds"][0]["observations"][0]["before"]["x"] = 55
        elif case == "world-after":
            data["worlds"][1]["observations"][0]["after"]["turns"] = 77
        elif case == "world-final":
            data["worlds"][0]["final"]["collected"] = False
        else:
            raise AssertionError(f"missing corruption {case}")
        return data

    def _make_evidence(self):
        self.write(self.build, "w13_browser_positive.json", deepcopy(ORIGINAL))
        self.write(self.witness, "witness_real_browser_success.json", deepcopy(ORIGINAL))
        for label in BUILD_NEGATIVES:
            self.write(self.build, f"w13_rejected_{label}.json", self._corrupt(label))
        for label in WITNESS_NEGATIVES:
            self.write(self.witness, f"witness_reject_{label}.json", self._corrupt(label))

    def accept(self):
        return assess_game_evidence(ROOT, self.build, self.witness)

    def test_01_exact_pinned_source_blobs_match_git(self):
        pins = verify_source_identity(ROOT)
        self.assertEqual(set(pins), set(SOURCE_BLOBS))
        self.assertEqual(
            pins["systems/workspace/game_construction.py"]["sha256"],
            "dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1",
        )

    def test_02_separate_complete_browser_shaped_fixtures_pass_preflight(self):
        result = self.accept()
        self.assertEqual(result["verdict"], "SOURCE_BOUND_BROWSER_EVIDENCE_ACCEPTED_FOR_OPERATOR_REVIEW")
        self.assertEqual(result["cp"], CP)
        self.assertTrue(result["independent_w12_replay"]["solved"])
        self.assertEqual(result["independent_w12_replay"]["boundaries_checked"], 1)
        self.assertEqual(len(result["mutated_browser_receipts_rejected"]), 10)

    def test_03_preflight_does_not_admit_execute_or_promote_CP(self):
        result = self.accept()
        self.assertEqual(result["cp_state"], "ADMISSIBLE")
        self.assertFalse(result["cp_witnessed"])
        self.assertFalse(result["job_admitted"])
        self.assertFalse(result["execution_triggered"])
        self.assertFalse(result["checkpoint_promoted"])
        self.assertNotIn(CP, checkpoint_frontier({"jobs": []})["witnessed"])

    def test_04_provenance_runs_pinned_to_original_two_merges(self):
        self.assertEqual(ARTIFACTS["build"]["run"], 38999614131)
        self.assertEqual(ARTIFACTS["witness"]["run"], 39001126918)
        self.assertNotEqual(ARTIFACTS["build"]["head"], ARTIFACTS["witness"]["head"])
        self.assertEqual(ARTIFACTS["build"]["id"], 12088487637)
        self.assertEqual(ARTIFACTS["witness"]["id"], 12088694155)

    def test_05_positive_receipt_missing_blocks(self):
        (self.build / "w13_browser_positive.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.accept()

    def test_06_witness_positive_missing_blocks(self):
        (self.witness / "witness_real_browser_success.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.accept()

    def test_07_replayed_but_different_global_history_blocks(self):
        data = deepcopy(ORIGINAL)
        data["actions"].insert(0, "left")
        data["worlds"][0]["actions"].insert(0, "left")
        # These changed actions are deliberately not accompanied by a
        # reverified native event series, so admission must reject.
        self.write(self.witness, "witness_real_browser_success.json", data)
        with self.assertRaises(ValueError):
            self.accept()

    def test_08_tampered_initial_world_observation_blocks(self):
        data = deepcopy(ORIGINAL)
        data["worlds"][0]["observations"][0]["after"]["turns"] = 77
        self.write(self.build, "w13_browser_positive.json", data)
        with self.assertRaisesRegex(ValueError, "observation"):
            self.accept()

    def test_09_missing_negative_cannot_be_silently_skipped(self):
        (self.witness / "witness_reject_crossing.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.accept()

    def test_10_modified_negative_claim_that_now_passes_blocks(self):
        self.write(self.build, "w13_rejected_boundary.json", deepcopy(ORIGINAL))
        with self.assertRaisesRegex(ValueError, "ACCEPTED a false"):
            self.accept()

    def test_11_build_witness_evidence_directories_must_be_distinct(self):
        with self.assertRaisesRegex(ValueError, "separate archive"):
            assess_game_evidence(ROOT, self.build, self.build)

    def test_12_changed_or_missing_source_pin_fails_closed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in SOURCE_BLOBS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, path)
            self.assertEqual(len(verify_source_identity(root)), len(SOURCE_BLOBS))
            (root / "docs/game_w13_preview.html").write_text("changed browser source")
            with self.assertRaisesRegex(ValueError, "source changed"):
                verify_source_identity(root)

    def test_13_source_pin_refuses_missing_file(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "missing/unsafe"):
                verify_source_identity(Path(tmp))

    def test_14_invalid_duplicate_json_keys_are_not_repaired(self):
        (self.build / "w13_browser_positive.json").write_text('{"actions":1,"actions":2}')
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.accept()

    def test_15_source_tree_bytes_are_not_mutated(self):
        before = {p: (ROOT / p).read_bytes() for p in SOURCE_BLOBS}
        self.accept()
        self.assertEqual(before, {p: (ROOT / p).read_bytes() for p in SOURCE_BLOBS})

    def test_16_alias_world_id_or_last_room_not_collected_rejected(self):
        for kind in ("borrowed", "unfinished"):
            with self.subTest(kind=kind):
                self._make_evidence()
                data = deepcopy(ORIGINAL)
                if kind == "borrowed":
                    data["worlds"][1]["id"] = data["worlds"][0]["id"]
                else:
                    data["final"]["solved"] = False
                self.write(self.witness, "witness_real_browser_success.json", data)
                with self.assertRaises(ValueError):
                    self.accept()


if __name__ == "__main__":
    unittest.main()
