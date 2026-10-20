"""Crash/restart witnesses for the exact native sealed SQLite admission."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
import sqlite3
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from security.continuation import EnvelopeError, ReplayLedger
from security.runtime_ingress import (
    AuthenticatedHandoffIngress, IngressAuthority, seal_handoff, seal_result)
from security.sealed_journal import SealedRuntimeJournal, SealedJournalError


class AtomicSealedAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.file = self.base / "runtime.sealed.sqlite"
        self.key = os.urandom(32)
        self.owner = Ed25519PrivateKey.generate()
        self.worker = Ed25519PrivateKey.generate()
        self.recipient = X25519PrivateKey.generate()
        # Kept for backward-compatible constructor; NOT the sealed replay
        # authority. Replay and native events now share the sealed SQLite DB.
        self.legacy_ledger = ReplayLedger(self.base / "legacy-replay.sqlite")
        self.restart()

    def restart(self):
        self.store = SealedRuntimeJournal(self.file, key=self.key)
        self.runtime = HandoffRuntime(event_store=self.store)
        self.ingress = AuthenticatedHandoffIngress(
            self.runtime, self.legacy_ledger,
            IngressAuthority("research", "owner", "worker",
                             self.owner.public_key(), self.recipient))
        self.returns = AuthenticatedHandoffIngress(
            self.runtime, self.legacy_ledger,
            IngressAuthority("research", "worker", "owner",
                             self.worker.public_key(), self.recipient))

    def task(self, ident="task-1"):
        return Handoff(
            handoff_id=ident, referent="finite movement",
            from_actor="owner", to_actor="worker",
            required_relation="observe", inputs={"secret": "private-native-record"},
            required_witnesses=("native",),
            admissible_evidence={"native": ("measured",)})

    def signed(self, task=None):
        return seal_handoff(
            task or self.task(), lane="research", parent_sha256=None,
            sender_private_key=self.owner,
            recipient_public_key=self.recipient.public_key())

    def result(self, event="return-1"):
        assert self.runtime.get("task-1")
        outcome = ExecutionResult(status="COMPLETE",
            output={"measurement": 9},
            evidence=(EvidenceRecord(condition="native", kind="measured",
                source="verified-test"),))
        return seal_result("task-1", self.runtime.state("task-1").last_event_id,
            outcome, event_id=event, lane="research", parent_sha256=None,
            sender_private_key=self.worker,
            recipient_public_key=self.recipient.public_key())

    def counts(self):
        with sqlite3.connect(self.file) as db:
            records = db.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            replay = db.execute("SELECT COUNT(*) FROM admitted").fetchone()[0]
        return (records, replay)

    def test_signed_submit_and_return_share_single_store(self):
        ticket = self.signed()
        self.assertEqual(self.ingress.submit(ticket).status, "READY")
        self.assertEqual(self.counts(), (1, 1))
        signed_return = self.result()
        self.assertEqual(self.returns.return_result(signed_return, handoff_id="task-1").status,
                         "COMPLETE")
        self.assertEqual(self.counts(), (2, 2))
        disk = self.file.read_bytes()
        self.assertNotIn(b"private-native-record", disk)
        self.assertNotIn(b"task-1", disk)
        # Separate ledger was NOT used for native encrypted admission.
        with sqlite3.connect(self.legacy_ledger.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM admitted").fetchone()[0], 0)
        self.restart()
        self.assertEqual(self.runtime.get("task-1"), self.task())
        self.assertEqual(self.runtime.state("task-1").output["measurement"], 9)
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.ingress.submit(ticket)
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.returns.return_result(signed_return, handoff_id="task-1")

    def test_fault_after_replay_insert_rolls_back_both_writes(self):
        ticket = self.signed()
        with patch.object(self.store, "_after_replay_insert",
                          side_effect=RuntimeError("power cut before event")):
            with self.assertRaisesRegex(RuntimeError, "power cut"):
                self.ingress.submit(ticket)
        self.assertEqual(self.counts(), (0, 0))
        self.restart()
        self.assertEqual(self.ingress.submit(ticket).status, "READY")
        self.assertEqual(self.counts(), (1, 1))

    def test_fault_after_event_insert_rolls_back_both_writes(self):
        ticket = self.signed()
        with patch.object(self.store, "_after_record_insert",
                          side_effect=RuntimeError("power cut before commit")):
            with self.assertRaisesRegex(RuntimeError, "power cut"):
                self.ingress.submit(ticket)
        self.assertEqual(self.counts(), (0, 0))
        self.restart()
        self.assertEqual(self.ingress.submit(ticket).status, "READY")
        self.assertEqual(self.counts(), (1, 1))

    def test_post_commit_lost_response_is_replay_not_second_handoff(self):
        ticket = self.signed()
        def network_disconnected_after_commit():
            self.ingress.submit(ticket)
            raise ConnectionError("connection closed before ACK")
        with self.assertRaises(ConnectionError):
            network_disconnected_after_commit()
        self.restart()
        self.assertEqual(self.runtime.state("task-1").status, "READY")
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.ingress.submit(ticket)
        self.assertEqual(self.counts(), (1, 1))

    def test_result_fault_rollback_keeps_native_state_ready(self):
        self.ingress.submit(self.signed())
        ticket = self.result()
        with patch.object(self.store, "_after_record_insert",
                          side_effect=RuntimeError("cut during result")):
            with self.assertRaisesRegex(RuntimeError, "cut during"):
                self.returns.return_result(ticket, handoff_id="task-1")
        self.assertEqual(self.counts(), (1, 1))
        self.restart()
        self.assertEqual(self.runtime.state("task-1").status, "READY")
        self.assertEqual(self.returns.return_result(ticket, handoff_id="task-1").status,
                         "COMPLETE")
        self.assertEqual(self.counts(), (2, 2))

    def test_result_commit_before_ack_cannot_apply_twice(self):
        self.ingress.submit(self.signed())
        ticket = self.result()
        self.returns.return_result(ticket, handoff_id="task-1")
        self.restart()
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.returns.return_result(ticket, handoff_id="task-1")
        self.assertEqual(self.counts(), (2, 2))

    def test_untrusted_native_fields_fail_before_consuming_admission(self):
        ticket = self.signed(replace(self.task(), from_actor="pretend-owner"))
        with self.assertRaisesRegex(EnvelopeError, "not authorized"):
            self.ingress.submit(ticket)
        self.assertEqual(self.counts(), (0, 0))

    def test_duplicate_identifier_with_new_ciphertext_cannot_apply_again(self):
        self.ingress.submit(self.signed())
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.ingress.submit(self.signed())
        self.assertEqual(self.counts(), (1, 1))

    def test_stale_writer_rolls_back_replay_admission(self):
        old_store = SealedRuntimeJournal(self.file, key=self.key)
        old = HandoffRuntime(event_store=old_store)
        self.ingress.submit(self.signed())
        old_ingress = AuthenticatedHandoffIngress(
            old, self.legacy_ledger,
            IngressAuthority("research", "owner", "worker",
                             self.owner.public_key(), self.recipient))
        second = self.signed(self.task("second"))
        with self.assertRaisesRegex(SealedJournalError, "concurrent"):
            old_ingress.submit(second)
        self.assertEqual(self.counts(), (1, 1))
        self.restart()
        self.assertEqual(self.ingress.submit(second).status, "READY")
        self.assertEqual(self.counts(), (2, 2))

    def test_historical_sealed_database_without_atomic_table_refused(self):
        self.runtime.submit(self.task())
        with sqlite3.connect(self.file) as db:
            db.execute("DROP TABLE admitted")
        with self.assertRaisesRegex(SealedJournalError, "migration"):
            self.restart()


if __name__ == "__main__":
    unittest.main()
