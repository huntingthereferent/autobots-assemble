"""Negative-boundary tests for local, redacted, exact workstation receipts."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent, EvidenceRecord, ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.native_receipt_projection import (
    inspect_local, recorded_receipt, reverify_local,
)


class NativeReceiptProjectionTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.path = self.dir / "runtime.jsonl"
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.path))
        self.job = "native-local-job"
        self.runtime.submit(Handoff(
            handoff_id=self.job, referent="private-referent", from_actor="operator",
            to_actor="private-worker", required_relation="private-operation",
            inputs={"private_token": "do-not-expose"}, metadata={
                "source_system": "process-workstation",
                "worker_id": "finite-original",
                "worker_version": "version-a",
                "edition_fingerprint": "a" * 64,
                "native_evidence_verifier": "independent-original-verifier",
                "private_context": "keep-secret",
            },
        ))

    def complete(self):
        parent = self.runtime.state(self.job).last_event_id
        self.runtime.event_store.append(HandoffEvent.create(
            handoff_id=self.job, event_type="STARTED",
            actor_id="private-worker", parents=(parent,),
        ))
        self.runtime.register_evidence_verifier(
            "independent-original-verifier", lambda _h, _result: None,
        )
        self.runtime.return_result(
            self.job, actor_id="private-worker",
            result=ExecutionResult(status="COMPLETE",
                                   output={"secret": "private-result"},
                                   evidence=(EvidenceRecord(
                                       condition="test-record-only", kind="source",
                                       source="test-private", ref="private-evidence-ref",
                                   ),)),
        )

    def test_missing_journal_does_not_create_file(self):
        with self.assertRaises(ValueError):
            inspect_local(self.dir / "missing", self.job)
        self.assertFalse((self.dir / "missing").exists())

    def test_open_job_not_called_executed_or_verified(self):
        row = inspect_local(self.dir, self.job)
        self.assertEqual(row["recorded_status"], "READY")
        self.assertEqual(row["verification"], "RECORDED_NOT_REVERIFIED")
        self.assertEqual(len(row["events"]), 1)
        self.assertIsNone(row["causal_research_link"])

    def test_complete_is_recorded_not_reverified_and_private_fields_omitted(self):
        self.complete()
        receipt = inspect_local(self.dir, self.job)
        self.assertEqual([x["type"] for x in receipt["events"]],
                         ["CREATED", "STARTED", "RESULT"])
        self.assertEqual(receipt["events"][1]["parents"],
                         [receipt["events"][0]["event_id"]])
        self.assertEqual(receipt["events"][2]["parents"],
                         [receipt["events"][1]["event_id"]])
        self.assertEqual(receipt["verification"], "RECORDED_NOT_REVERIFIED")
        self.assertEqual(receipt["recorded_status"], "COMPLETE")
        rendered = json.dumps(receipt)
        for secret in ("private-token", "do-not-expose", "private-result",
                       "private-evidence-ref", "private-referent", "private-worker"):
            self.assertNotIn(secret, rendered)
        self.assertFalse(receipt["publicly_published"])

    def test_wrong_source_not_permitted(self):
        h = self.runtime.get(self.job)
        self.runtime._handoffs[self.job] = replace(
            h, metadata={**h.metadata, "source_system": "external"})
        with self.assertRaises(ValueError):
            recorded_receipt(self.runtime, self.job)

    def test_source_fingerprint_must_be_exact(self):
        h = self.runtime.get(self.job)
        self.runtime._handoffs[self.job] = replace(
            h, metadata={**h.metadata, "edition_fingerprint": "not-a-sha"})
        with self.assertRaises(ValueError):
            recorded_receipt(self.runtime, self.job)

    def test_forged_parent_or_duplicate_event_fails_closed(self):
        self.runtime.event_store.append(HandoffEvent.create(
            handoff_id=self.job, event_type="STARTED",
            actor_id="private-worker", parents=("evt_not_in_same_journal",),
        ))
        with self.assertRaises(ValueError):
            inspect_local(self.dir, self.job)

    def test_other_handoff_parent_cannot_masquerade_as_local_ancestry(self):
        self.runtime.submit(Handoff(
            handoff_id="unrelated-job", referent="another source",
            from_actor="operator", to_actor="worker", required_relation="separate",
        ))
        foreign=self.runtime.state("unrelated-job").last_event_id
        self.runtime.event_store.append(HandoffEvent.create(
            handoff_id=self.job, event_type="STARTED",
            actor_id="private-worker", parents=(foreign,),
        ))
        with self.assertRaisesRegex(ValueError,"unresolved or forward"):
            inspect_local(self.dir,self.job)

    def test_duplicate_event_id_rejected_without_promoting_result(self):
        first=self.runtime.event_store.for_handoff(self.job)[0]
        self.runtime.event_store.append(replace(first,event_type="STARTED"))
        with self.assertRaisesRegex(ValueError,"duplicate or invalid"):
            inspect_local(self.dir,self.job)

    def test_reverification_rejects_changed_journal_during_native_check(self):
        self.complete()
        def changed(*,data_dir,job_id):
            runtime=HandoffRuntime(event_store=RuntimeJournal(self.path))
            prior=runtime.state(self.job).last_event_id
            runtime.event_store.append(HandoffEvent.create(
                handoff_id=self.job,event_type="NOTE",
                actor_id="private-worker",parents=(prior,),
            ))
            return {"job_id":job_id,"status":"COMPLETE",
                    "reverified":True,"executed":False}
        with patch("systems.workspace.controls.reverify_job",side_effect=changed):
            with self.assertRaisesRegex(ValueError,"changed during native re-verification"):
                reverify_local(self.dir,self.job)

    def test_noncomplete_cannot_invoke_native_reverifier(self):
        with patch("systems.workspace.controls.reverify_job") as invoke:
            with self.assertRaises(ValueError):
                reverify_local(self.dir, self.job)
            invoke.assert_not_called()

    def test_reverify_requires_exact_native_pass(self):
        self.complete()
        with patch("systems.workspace.controls.reverify_job",
                   return_value={"job_id": self.job, "status": "COMPLETE",
                                 "reverified": False, "executed": False}) as invoke:
            with self.assertRaises(ValueError):
                reverify_local(self.dir, self.job)
            invoke.assert_called_once()

    def test_reverification_path_only_promotes_after_exact_native_check(self):
        """Mocked routing test; does NOT prove actual native semantics."""
        self.complete()
        with patch("systems.workspace.controls.reverify_job",
                   return_value={"job_id": self.job, "status": "COMPLETE",
                                 "reverified": True, "executed": False}):
            row = reverify_local(self.dir, self.job)
        self.assertEqual(row["verification"], "FRESH_NATIVE_REVERIFICATION_LOCAL")
        self.assertIsNone(row["causal_research_link"])
        self.assertFalse(row["publicly_published"])


if __name__ == "__main__":
    unittest.main()
