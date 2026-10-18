"""Genuine owner W13 parent compatibility in existing native GAME-NATIVE-VERIFIER.

These are fresh, isolated finite-workstation experiments. They DO NOT consume
the archived real owner journal or claim the owner checkpoint has been staffed.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import replace
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.controls import reverify_job
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.game_w13_native_bridge import copy_game_source
from systems.workspace.game_native_verifier_bridge import (
    NativeGameVerifierBridge,copy_verifier_source,WORKER_ID,
    OWNER_W13_JOB,OWNER_VERSION,OWNER_JOB_ID,VERSION,W13_JOB)

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/"network/tests/fixtures/game_w13_native_cp_example.json"


class OwnerW13NativeVerifierParentTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.desk=ProcessWorkstation(self.root/"workstation")
        self.rt=HandoffRuntime(event_store=RuntimeJournal(self.root/"runtime.jsonl"))
        self.inputs=json.loads(FIXTURE.read_text(encoding="utf8"))
        copy_game_source(self.root,version_id="w13-github-v1",allow_copy=True)
        copy_verifier_source(self.root,version_id=OWNER_VERSION,allow_copy=True)
        self.bridge=NativeGameVerifierBridge(runtime=self.rt,workstation=self.desk)
        # The existing bridge already registers its own original W13 verifier.
        # Registering a second instance would violate runtime verifier ownership.
        self.parent=self.bridge.parent_bridge
        self.parent.admit(version_id="w13-github-v1",inputs=self.inputs,
                          from_actor="isolated-test",job_id=OWNER_W13_JOB)

    def _admit(self):
        return self.bridge.admit(version_id=OWNER_VERSION,
                                 inputs={"w13_job_id":OWNER_W13_JOB},
                                 from_actor="isolated-source-test",job_id=OWNER_JOB_ID)

    def _parent_complete(self):
        self.parent.execute(OWNER_W13_JOB,allow_local_execution=True)
        self.assertTrue(self.parent.reverify(OWNER_W13_JOB))

    def test_uncompleted_original_parent_cannot_admit_child(self):
        with self.assertRaises(ValueError):
            self._admit()
        self.assertNotIn(OWNER_JOB_ID,self.rt.snapshot())

    def test_owner_path_is_distinct_from_legacy_source_parent(self):
        self._parent_complete()
        with self.assertRaisesRegex(ValueError,"separate source-pinned"):
            self.bridge.admit(version_id=VERSION,
                              inputs={"w13_job_id":OWNER_W13_JOB},
                              from_actor="isolated-source-test",job_id=OWNER_JOB_ID)
        with self.assertRaisesRegex(ValueError,"separate source-pinned"):
            self.bridge.admit(version_id=OWNER_VERSION,
                              inputs={"w13_job_id":OWNER_W13_JOB},
                              from_actor="isolated-source-test",job_id="game-native-verifier-joined-001")
        with self.assertRaises(ValueError):
            self.bridge.admit(version_id=OWNER_VERSION,
                              inputs={"w13_job_id":"another-job"},
                              from_actor="isolated-source-test",job_id=OWNER_JOB_ID)
        self.assertNotIn(OWNER_JOB_ID,self.rt.snapshot())

    def test_synthetic_reuse_of_original_job_name_cannot_impersonate_real_result(self):
        self._parent_complete()
        with self.assertRaisesRegex(ValueError,"original owner W13 RESULT/source identity not authenticated"):
            self._admit()
        self.assertNotIn(OWNER_JOB_ID,self.rt.snapshot())

    def test_finite_owner_parent_algorithm_with_explicitly_mocked_historical_id(self):
        """Exercises the real native subprocess but NOT the original owner archive.

        Only this synthetic fixture substitutes historical identity admission;
        the independent parent W12 replay and native witness still run for real.
        """
        self._parent_complete()
        with patch.object(NativeGameVerifierBridge,"_check_original_owner",return_value=None):
            original=self._admit()
            self.assertEqual(original.dependencies,(OWNER_W13_JOB,))
            self.assertEqual(original.inputs["parent_job_id"],OWNER_W13_JOB)
            self.assertEqual(self.rt.state(OWNER_JOB_ID).status,"READY")
            self.assertEqual(original.metadata["checkpoint_contract"],"GAME-NATIVE-VERIFIER")
            self.assertEqual(original.metadata["worker_version"],OWNER_VERSION)
            with self.assertRaises(PermissionError):
                self.bridge.execute(OWNER_JOB_ID)
            self.bridge.execute(OWNER_JOB_ID,allow_local_execution=True)
            self.assertEqual(self.rt.state(OWNER_JOB_ID).status,"COMPLETE")
            self.assertTrue(self.bridge.reverify(OWNER_JOB_ID))
            self.assertEqual(reverify_job(data_dir=self.root,job_id=OWNER_JOB_ID)["status"],"COMPLETE")
            self.assertEqual(self.rt.get(OWNER_W13_JOB).handoff_id,OWNER_W13_JOB)
            self.assertEqual(len(self.rt.snapshot()),2)

    def test_spoofed_parent_dependency_is_rejected_before_execution(self):
        self._parent_complete()
        with patch.object(NativeGameVerifierBridge,"_check_original_owner",return_value=None):
            original=self._admit()
        self.rt._handoffs[OWNER_JOB_ID]=replace(original,dependencies=(W13_JOB,))
        with self.assertRaises(ValueError):
            self.bridge.execute(OWNER_JOB_ID,allow_local_execution=True)
        self.assertEqual(self.rt.state(OWNER_JOB_ID).status,"READY")

    def test_tampered_child_worker_edition_fails_closed(self):
        self._parent_complete()
        with patch.object(NativeGameVerifierBridge,"_check_original_owner",return_value=None):
            self._admit()
        edition=self.desk._edition(WORKER_ID,OWNER_VERSION)/"native_verifier.py"
        edition.write_text(edition.read_text(encoding="utf8")+"\n# changed after admission\n",encoding="utf8")
        with self.assertRaises(ValueError):
            self.bridge.execute(OWNER_JOB_ID,allow_local_execution=True)
        self.assertEqual(self.rt.state(OWNER_JOB_ID).status,"READY")

    def test_parent_result_must_still_reverify_after_child_admission(self):
        self._parent_complete()
        with patch.object(NativeGameVerifierBridge,"_check_original_owner",return_value=None):
            self._admit()
        source=self.desk._edition("game-worlds-w13","w13-github-v1")/"game_worlds_worker.py"
        source.write_text(source.read_text(encoding="utf8")+"\n# changed parent\n",encoding="utf8")
        with self.assertRaises(ValueError):
            self.bridge.execute(OWNER_JOB_ID,allow_local_execution=True)
        self.assertEqual(self.rt.state(OWNER_JOB_ID).status,"READY")


if __name__=="__main__":
    unittest.main()
