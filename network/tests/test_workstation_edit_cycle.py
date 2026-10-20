"""Real workstation edit feedback: OS proposal, native test, and source fork."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import unittest

from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.workstation_edit_cycle import (
    CANONICAL_SOURCE, SOURCE_NAME, WORKER, edit_pass, run_once,
)


class NativeEditCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bench = ProcessWorkstation(self.root / "workstation")

    def seed(self):
        src = self.root / "trusted-source"
        src.mkdir()
        (src / SOURCE_NAME).write_bytes(CANONICAL_SOURCE.read_bytes())
        return self.bench.copy_source(src, worker_id=WORKER, version_id="base")

    def test_actual_source_defect_edit_worker_and_verified_successor(self):
        source_sha = CANONICAL_SOURCE.read_bytes()
        receipt = run_once(data_dir=self.root, run_id="first", execute=True)
        self.assertEqual(receipt["schema"], "workstation-native-edit-cycle/v1")
        self.assertEqual(receipt["outcome"], "ACCEPTED_EDITION")
        self.assertEqual(receipt["initial_observation"]["returncode"], 4)
        self.assertIn("BLANK_PRODUCT_ACCEPTED", receipt["initial_observation"]["stderr"])
        self.assertEqual(receipt["independent_recheck"]["returncode"], 0)
        self.assertTrue(receipt["successor_created"])
        self.assertGreater(receipt["proposal_worker_pid"], 0)
        self.assertFalse(receipt["ai_model"])
        base = self.root / "workstation" / WORKER / "factory-first-base" / SOURCE_NAME
        candidate = self.root / "workstation" / WORKER / "factory-first-candidate" / SOURCE_NAME
        accepted = self.root / "workstation" / WORKER / "factory-first-accepted" / SOURCE_NAME
        self.assertEqual(base.read_bytes(), source_sha)
        self.assertEqual(CANONICAL_SOURCE.read_bytes(), source_sha)
        self.assertNotEqual(candidate.read_bytes(), source_sha)
        self.assertEqual(accepted.read_bytes(), candidate.read_bytes())
        self.assertEqual(self.bench.inspect(worker_id=WORKER,
                         version_id="factory-first-candidate")["modified"], [SOURCE_NAME])
        accepted_info = self.bench.inspect(worker_id=WORKER,
                                           version_id="factory-first-accepted")
        self.assertEqual(accepted_info["parent_version"], "factory-first-candidate")
        self.assertEqual(accepted_info["modified"], [])
        self.assertFalse(accepted_info["verified"])  # No source-authority upgrade.

    def test_no_action_without_explicit_execution(self):
        with self.assertRaises(PermissionError):
            run_once(data_dir=self.root, run_id="denied")
        with self.assertRaises(PermissionError):
            run_once(data_dir=self.root, run_id="denied", execute=False)
        self.assertFalse((self.root / "workstation").exists())

    def test_same_id_cannot_duplicate_work(self):
        run_once(data_dir=self.root, run_id="one", execute=True)
        with self.assertRaises(FileExistsError):
            run_once(data_dir=self.root, run_id="one", execute=True)

    def test_changed_parent_refused_before_worker(self):
        self.seed()
        parent = self.root / "workstation" / WORKER / "base" / SOURCE_NAME
        parent.write_text(parent.read_text() + "\n# unreviewed\n")
        with self.assertRaises(ValueError):
            edit_pass(desk=self.bench, worker_id=WORKER, parent_version="base",
                      candidate_version="candidate", accepted_version="next", execute=True)
        self.assertFalse(self.bench._edition(WORKER, "candidate").exists())

    def test_native_verifier_failure_leaves_candidate_unaccepted(self):
        self.seed()
        actual = __import__(
            "systems.workspace.workstation_edit_cycle", fromlist=["_run_verifier"]
        )._run_verifier
        calls = 0

        def verifier(source):
            nonlocal calls
            calls += 1
            return actual(source) if calls == 1 else {
                "returncode": 9, "stdout": "", "stderr": "REGRESSION"
            }

        with mock.patch("systems.workspace.workstation_edit_cycle._run_verifier",
                        side_effect=verifier):
            receipt = edit_pass(desk=self.bench, worker_id=WORKER,
                                parent_version="base", candidate_version="candidate",
                                accepted_version="next", execute=True)
        self.assertEqual(receipt["outcome"], "REJECTED_CANDIDATE")
        self.assertEqual(calls, 2)
        self.assertTrue(self.bench._edition(WORKER, "candidate").exists())
        self.assertFalse(self.bench._edition(WORKER, "next").exists())

    def test_no_observed_failure_means_no_candidate(self):
        self.seed()
        with mock.patch("systems.workspace.workstation_edit_cycle._run_verifier",
                        return_value={"returncode":0, "stdout":"ok", "stderr":""}):
            with self.assertRaises(ValueError):
                edit_pass(desk=self.bench, worker_id=WORKER,
                          parent_version="base", candidate_version="candidate",
                          accepted_version="next", execute=True)
        self.assertFalse(self.bench._edition(WORKER, "candidate").exists())


if __name__ == "__main__":
    unittest.main()
