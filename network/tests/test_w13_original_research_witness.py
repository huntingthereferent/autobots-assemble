"""Original (not synthetic) W13 receipt pin and failed-identity controls."""
from __future__ import annotations

from pathlib import Path
import json
import unittest
from unittest.mock import patch
from systems.workspace.github_w13_continuation import (
    RUN_ID, ARTIFACT_ID, ORIGINAL_DIGEST, ORIGINAL_HEAD, JOB_ID)
from systems.workspace.w13_original_research_witness import RESEARCH_PATH,verify_original

ROOT=Path(__file__).resolve().parents[2]


class OriginalW13SourceTests(unittest.TestCase):
    def test_original_committed_record_has_exact_native_receipt(self):
        record=json.loads((ROOT/RESEARCH_PATH).read_text())
        self.assertEqual(record["result_state"],"MOVE_WITH_WALL")
        self.assertEqual(record["schema_version"],1)
        source=record["original_source"];decl=record["native_workstation_receipt"]
        self.assertEqual((source["run_id"],source["artifact_id"],
                          source["head_sha"],source["artifact_digest"]),
                         (RUN_ID,ARTIFACT_ID,ORIGINAL_HEAD,ORIGINAL_DIGEST))
        self.assertEqual(decl["job_id"],JOB_ID)
        self.assertEqual(decl["result_event_id"],"evt_208f2fbdb380437eb59790a9a704c0b9")
        self.assertEqual(decl["native_verifier_id"],"cp-checker:GAME-W13-WORLDS")
        self.assertEqual(decl["source_fingerprint"],"798ed2399413ecbb30a1eb94c547a5517ee03dfd002600d868376f88f03f458a")
        self.assertTrue(record["walls"])

    def test_owner_only_replay_repair_pins_original_record_and_loads_dependencies_first(self):
        workflow=(ROOT/".github/workflows/w13-native-research-source.yml").read_text()
        self.assertIn("github.actor == github.repository_owner",workflow)
        self.assertIn("branches: [main]",workflow)
        self.assertIn("0baeeae60718b0651f3afc503d98a39dd0a95b0a",workflow)
        self.assertIn("f8fbf981c75ccf53a8a72006053f8b02a31343dc",workflow)
        self.assertIn("git('diff','--name-status',parents[1],sha,'--',path)",workflow)
        self.assertIn("cryptography>=45,<47",workflow)
        self.assertLess(workflow.index("Install original native verifier dependency"),
                        workflow.index("Authenticate original owner-run"))
        self.assertIn("'.github/workflows/w13-native-research-source.yml'",workflow)

    def test_missing_original_artifact_cannot_verify(self):
        with self.assertRaises(ValueError):
            verify_original(artifact_dir=ROOT/"missing-artifact",
                source_binding=ROOT/"missing-binding",
                repo_root=ROOT,research_commit="a"*40)

    def test_unpinned_commit_cannot_verify(self):
        with self.assertRaisesRegex(ValueError,"exact committed research SHA"):
            verify_original(artifact_dir=ROOT,source_binding=ROOT,
                repo_root=ROOT,research_commit="main")

    def test_source_authentication_is_not_skipped(self):
        binding={"repository":"huntingthereferent/autobots-assemble",
                 "run_id":RUN_ID,"artifact_id":ARTIFACT_ID,"attempt":1,
                 "head_sha":ORIGINAL_HEAD,"digest":ORIGINAL_DIGEST}
        with patch("systems.workspace.w13_original_research_witness._object",
                   return_value=binding),patch(
                   "systems.workspace.w13_original_research_witness.validate_archive_metadata",
                   side_effect=ValueError("owner source refused")):
            with self.assertRaisesRegex(ValueError,"owner source refused"):
                verify_original(artifact_dir=ROOT,source_binding=ROOT,
                    repo_root=ROOT,research_commit="f"*40)


if __name__=="__main__":
    unittest.main()
