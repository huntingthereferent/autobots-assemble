"""Native runtime ingress tests: real journals, enrolled actors and replay."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from runtime.journal import RuntimeJournal
from security.continuation import EnvelopeError, ReplayLedger, envelope_digest
from security.runtime_ingress import (
    AuthenticatedHandoffIngress, IngressAuthority, seal_handoff, seal_result,
)


class NativeIngressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.runtime_file = self.root / "runtime.jsonl"
        self.ledger_file = self.root / "replay.sqlite3"
        self.owner = Ed25519PrivateKey.generate()
        self.worker = Ed25519PrivateKey.generate()
        self.receiver = X25519PrivateKey.generate()
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.runtime_file))
        self.ledger = ReplayLedger(self.ledger_file)
        self.ingress = self._ingress("owner", self.owner.public_key(), "worker")
        self.result_ingress = self._ingress("worker", self.worker.public_key(), "owner")

    def _ingress(self, sender, key, recipient):
        return AuthenticatedHandoffIngress(self.runtime, self.ledger,
                IngressAuthority("research", sender, recipient, key, self.receiver))

    def task(self, ident="job-1"):
        return Handoff(handoff_id=ident, referent="finite-trial", from_actor="owner",
                       to_actor="worker", required_relation="observe",
                       inputs={"source": "edition-1"},
                       required_witnesses=("native",),
                       admissible_evidence={"native": ("measured",)})

    def envelope(self, task=None, parent=None, signer=None):
        return seal_handoff(task or self.task(), lane="research", parent_sha256=parent,
                            sender_private_key=signer or self.owner,
                            recipient_public_key=self.receiver.public_key())

    def result(self, status="COMPLETE", kind="measured"):
        return ExecutionResult(status=status, output={"value": 3},
                evidence=(EvidenceRecord(condition="native", kind=kind,
                                         source="native-source", ref="receipt-1"),))

    def signed_result(self, *, prior=None, result=None, event="result-1"):
        return seal_result("job-1", prior or self.runtime.state("job-1").last_event_id,
                           result or self.result(), event_id=event,
                           lane="research", parent_sha256=None,
                           sender_private_key=self.worker,
                           recipient_public_key=self.receiver.public_key())

    def test_real_runtime_durable_submission_without_execution(self):
        ticket = self.envelope()
        state = self.ingress.submit(ticket)
        self.assertEqual(state.status, "READY")
        self.assertEqual(self.runtime.get("job-1"), self.task())
        self.assertFalse(any(x.event_type == "STARTED" for x in
                             self.runtime.event_store.for_handoff("job-1")))
        self.assertEqual(HandoffRuntime(event_store=RuntimeJournal(self.runtime_file)).get("job-1"),
                         self.task())

    def test_replay_after_restarting_both_runtime_and_ledger(self):
        ticket = self.envelope()
        self.ingress.submit(ticket)
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.runtime_file))
        self.ledger = ReplayLedger(self.ledger_file)
        self.ingress = self._ingress("owner", self.owner.public_key(), "worker")
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.ingress.submit(ticket)
        self.assertEqual(len(self.runtime.event_store.for_handoff("job-1")), 1)

    def test_identical_id_with_fresh_encryption_is_not_readmitted(self):
        self.ingress.submit(self.envelope())
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.ingress.submit(self.envelope())

    def test_claimed_actor_and_destination_are_not_authority(self):
        for impostor in (replace(self.task(), from_actor="impostor"),
                         replace(self.task("job-2"), to_actor="another-worker")):
            with self.subTest(actor=impostor.from_actor, destination=impostor.to_actor):
                with self.assertRaisesRegex(EnvelopeError, "not authorized"):
                    self.ingress.submit(self.envelope(impostor))
        self.assertEqual(self.runtime.snapshot(), {})

    def test_wrong_signature_or_scope_does_not_enter_runtime(self):
        with self.assertRaises(EnvelopeError):
            self.ingress.submit(self.envelope(signer=self.worker))
        with self.assertRaises(EnvelopeError):
            self.ingress.submit(self.envelope(), expected_parent_sha256="a" * 64)
        self.assertEqual(self.runtime.snapshot(), {})
        self.assertEqual(self.ingress.submit(self.envelope()).status, "READY")

    def test_parent_envelope_binding_enforced(self):
        root = self.envelope()
        root_hash = envelope_digest(root)
        self.ingress.submit(root)
        child = self.envelope(self.task("job-2"), parent=root_hash)
        with self.assertRaisesRegex(EnvelopeError, "parent"):
            self.ingress.submit(child)
        self.assertEqual(self.ingress.submit(child, expected_parent_sha256=root_hash).status,
                         "READY")

    def test_event_identity_cannot_differ_from_handoff(self):
        ticket = self.envelope()
        ticket["event_id"] = "different"
        with self.assertRaises(EnvelopeError):
            self.ingress.submit(ticket)
        self.assertEqual(self.runtime.snapshot(), {})

    def test_signed_worker_result_returns_to_native_runtime(self):
        self.ingress.submit(self.envelope())
        output = self.result_ingress.return_result(self.signed_result(), handoff_id="job-1")
        self.assertEqual(output.status, "COMPLETE")
        self.assertEqual(output.output["value"], 3)
        self.assertEqual(len(self.runtime.event_store.for_handoff("job-1")), 2)

    def test_wrong_worker_cannot_report_completion(self):
        self.ingress.submit(self.envelope())
        ticket = seal_result("job-1", self.runtime.state("job-1").last_event_id,
                             self.result(), event_id="result-1", lane="research",
                             parent_sha256=None, sender_private_key=self.owner,
                             recipient_public_key=self.receiver.public_key())
        with self.assertRaises(EnvelopeError):
            self.result_ingress.return_result(ticket, handoff_id="job-1")
        with self.assertRaisesRegex(EnvelopeError, "result actor"):
            self.ingress.return_result(self.signed_result(), handoff_id="job-1")
        self.assertEqual(self.runtime.state("job-1").status, "READY")

    def test_stale_result_cannot_overwrite_changed_runtime_state(self):
        self.ingress.submit(self.envelope())
        ticket = self.signed_result()
        self.runtime.reopen("job-1", actor_id="owner", reason="new source")
        with self.assertRaisesRegex(EnvelopeError, "stale"):
            self.result_ingress.return_result(ticket, handoff_id="job-1")
        self.assertEqual(self.runtime.state("job-1").status, "READY")

    def test_unsupported_witness_is_not_admitted(self):
        self.ingress.submit(self.envelope())
        ticket = self.signed_result(result=self.result(kind="reported"))
        with self.assertRaisesRegex(ValueError, "witness"):
            self.result_ingress.return_result(ticket, handoff_id="job-1")
        self.assertEqual(self.runtime.state("job-1").status, "READY")

    def test_result_replay_refused(self):
        self.ingress.submit(self.envelope())
        ticket = self.signed_result()
        self.result_ingress.return_result(ticket, handoff_id="job-1")
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.result_ingress.return_result(ticket, handoff_id="job-1")


if __name__ == "__main__":
    unittest.main()
