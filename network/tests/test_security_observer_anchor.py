"""Independent observer checkpoint survives a separately restored database."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sqlite3
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from security.journal_checkpoint import issue_checkpoint
from security.observer_anchor import issue_observer_anchor, verify_observer_anchor
from security.remote_witness import RemoteWitnessLedger, export_witness_span
from security.sealed_journal import SealedRuntimeJournal, SealedJournalError


class ObserverAnchorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.key = os.urandom(32)
        self.source = Ed25519PrivateKey.generate()
        self.observer_signer = Ed25519PrivateKey.generate()
        self.runtime = HandoffRuntime(event_store=SealedRuntimeJournal(
            self.root / "source.sqlite", key=self.key))
        self.base = issue_checkpoint(self.runtime.event_store, self.source)
        self.ledger_file = self.root / "observer.sqlite"
        self.observer = RemoteWitnessLedger(self.ledger_file)
        self.observer.enroll("source-a", signed_base_checkpoint=self.base,
                             trusted_source_public_key=self.source.public_key())

    def add(self, name):
        base = self.observer.current(
            "source-a", trusted_source_public_key=self.source.public_key())
        self.runtime.submit(Handoff(handoff_id=name, referent="observation",
                                    from_actor="origin", to_actor="worker",
                                    required_relation="observe"))
        tip = issue_checkpoint(self.runtime.event_store, self.source)
        bundle = export_witness_span(
            self.runtime.event_store, base_checkpoint=base,
            tip_checkpoint=tip, source_public_key=self.source.public_key())
        self.observer.observe("source-a", bundle,
                              trusted_source_public_key=self.source.public_key())

    def anchor(self):
        return issue_observer_anchor(
            self.observer, "source-a",
            source_public_key=self.source.public_key(),
            observer_private_key=self.observer_signer)

    def verify(self, anchor):
        return verify_observer_anchor(
            self.observer, anchor,
            source_public_key=self.source.public_key(),
            observer_public_key=self.observer_signer.public_key())

    def test_initial_signed_observer_prefix_can_be_extended(self):
        anchor = self.anchor()
        self.verify(anchor)
        self.add("first")
        self.verify(anchor)
        self.add("second")
        self.verify(anchor)
        reloaded = RemoteWitnessLedger(self.ledger_file)
        verify_observer_anchor(
            reloaded, anchor,
            source_public_key=self.source.public_key(),
            observer_public_key=self.observer_signer.public_key())

    def test_later_signed_prefix_catches_full_observer_db_rollback(self):
        self.add("one")
        old_snapshot = self.root / "observer-old.sqlite"
        with sqlite3.connect(self.ledger_file) as source, sqlite3.connect(old_snapshot) as copy:
            source.backup(copy)
        self.add("two")
        anchor = self.anchor()
        self.verify(anchor)
        with sqlite3.connect(old_snapshot) as source, sqlite3.connect(self.ledger_file) as target:
            source.backup(target)
        self.observer = RemoteWitnessLedger(self.ledger_file)
        with self.assertRaisesRegex(SealedJournalError, "rolled back"):
            self.verify(anchor)

    def test_changed_or_removed_observation_refused(self):
        self.add("first")
        self.add("second")
        anchor = self.anchor()
        self.verify(anchor)
        with sqlite3.connect(self.ledger_file) as db:
            db.execute("DELETE FROM movements WHERE source_id=? AND last_seq=?",
                       ("source-a", 1))
        with self.assertRaises(SealedJournalError):
            self.verify(anchor)

    def test_older_signed_anchor_allows_later_unanchored_extension(self):
        self.add("first")
        anchor = self.anchor()
        self.add("second")
        self.verify(anchor)
        self.assertEqual(self.observer.current(
            "source-a", trusted_source_public_key=self.source.public_key())["sequence"], 2)

    def test_forged_anchor_and_untrusted_observer_key_refused(self):
        self.add("first")
        anchor = self.anchor()
        with self.assertRaises(SealedJournalError):
            self.verify({**anchor, "movement_count": 0})
        with self.assertRaises(SealedJournalError):
            verify_observer_anchor(
                self.observer, anchor,
                source_public_key=self.source.public_key(),
                observer_public_key=Ed25519PrivateKey.generate().public_key())
        with self.assertRaises(SealedJournalError):
            verify_observer_anchor(
                self.observer, anchor,
                source_public_key=Ed25519PrivateKey.generate().public_key(),
                observer_public_key=self.observer_signer.public_key())

    def test_corrupted_current_tip_refused_before_issuing_new_anchor(self):
        self.add("first")
        with sqlite3.connect(self.ledger_file) as db:
            db.execute("UPDATE sources SET checkpoint=? WHERE source_id=?",
                       ('{"invalid":true}', "source-a"))
        with self.assertRaises(SealedJournalError):
            self.anchor()


if __name__ == "__main__":
    unittest.main()
