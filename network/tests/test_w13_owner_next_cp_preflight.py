"""Negative controls for original, non-executing owner W13 next-CP preflight."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch
from systems.workspace.w13_owner_next_cp_preflight import (
    examine_original,EXPECTED_PARENT_BLOB,EXPECTED_WITNESS_BLOB,
    EXPECTED_BRIDGE_BLOB,
    OWNER_REQUEST,SCHEMA
)
from systems.workspace.github_w13_continuation import (
    ARTIFACT_ID,ORIGINAL_DIGEST,ORIGINAL_HEAD,RUN_ID)

ROOT=Path(__file__).resolve().parents[2]


class OriginalOwnerPreflightTests(unittest.TestCase):
    def test_source_record_and_registered_witness_are_independently_pinned(self):
        from systems.workspace.github_w13_continuation import _git_blob
        record=ROOT/"research/dives/W13-NATIVE-RECEIPT-001/dive.json"
        worker=ROOT/"systems/workspace/game_native_verifier_worker_source/native_verifier.py"
        bridge=ROOT/"systems/workspace/game_native_verifier_bridge.py"
        self.assertEqual(_git_blob(record),EXPECTED_PARENT_BLOB)
        self.assertEqual(_git_blob(worker),EXPECTED_WITNESS_BLOB)
        self.assertEqual(_git_blob(bridge),EXPECTED_BRIDGE_BLOB)
        self.assertEqual(SCHEMA,"owner-w13-game-native-verifier-source-preflight/v1")

    def test_missing_or_false_source_binding_rejected_without_runtime(self):
        with self.assertRaises(ValueError):
            examine_original(artifact_dir=ROOT/"no-archive",
                source_binding=ROOT/"no-binding",repo_root=ROOT,research_commit="a"*40)
        with self.assertRaisesRegex(ValueError,"exact committed research revision"):
            examine_original(artifact_dir=ROOT,source_binding=ROOT,
                repo_root=ROOT,research_commit="main")

    def test_other_run_with_fake_original_name_rejected_before_unpack(self):
        fake={"repository":"huntingthereferent/autobots-assemble",
              "workflow":"workstation-w13-owner-merged-one-shot",
              "run_id":RUN_ID+1,"artifact_id":ARTIFACT_ID,"attempt":1,
              "head_sha":ORIGINAL_HEAD,"digest":ORIGINAL_DIGEST}
        with patch("systems.workspace.w13_owner_next_cp_preflight._object",
                   return_value=fake), patch(
                   "systems.workspace.w13_owner_next_cp_preflight.unpack_native_runtime"
                   ) as unpack:
            with self.assertRaisesRegex(ValueError,"provenance mismatched"):
                examine_original(artifact_dir=ROOT,source_binding=ROOT,
                    repo_root=ROOT,research_commit="a"*40)
            unpack.assert_not_called()

    def test_does_not_offer_any_execution_or_autonomous_staffing_operation(self):
        from systems.workspace import w13_owner_next_cp_preflight as mod
        import inspect
        source=inspect.getsource(mod.examine_original)
        self.assertNotIn(".execute(",source)
        self.assertNotIn(".admit(",source)
        self.assertNotIn(".copy_source(",source)
        self.assertNotIn("open_help(",source)
        self.assertIn("child_job_executed",source)
        self.assertIn("owner_child_authorized",source)


if __name__=="__main__":
    unittest.main()
