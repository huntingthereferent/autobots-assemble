"""External checkpoint tests: rollback, fork and signature failures."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import shutil
import sqlite3
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from runtime.service import EcosystemService
from security.journal_checkpoint import issue_checkpoint, verify_checkpoint
from security.sealed_journal import SealedRuntimeJournal, SealedJournalError


class AnchoredJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.key = os.urandom(32)
        self.signer = Ed25519PrivateKey.generate()
        self.file = self.root / "native.sealed.sqlite"

    def runtime(self, path=None):
        return HandoffRuntime(event_store=SealedRuntimeJournal(
            path or self.file, key=self.key))

    def task(self, ident):
        return Handoff(handoff_id=ident, referent="observed-"+ident,
                       from_actor="owner", to_actor="worker",
                       required_relation="observe")

    def test_signed_checkpoint_allows_same_or_extended_history(self):
        r = self.runtime()
        r.submit(self.task("one"))
        checkpoint = issue_checkpoint(r.event_store, self.signer)
        self.assertEqual(checkpoint["sequence"], 1)
        verify_checkpoint(r.event_store, checkpoint, self.signer.public_key())
        r.submit(self.task("two"))
        verify_checkpoint(r.event_store, checkpoint, self.signer.public_key())
        verify_checkpoint(self.runtime().event_store, checkpoint, self.signer.public_key())

    def test_database_rollback_below_anchor_refused(self):
        r = self.runtime()
        r.submit(self.task("one"))
        backup = self.root / "old.sqlite"
        with sqlite3.connect(self.file) as src, sqlite3.connect(backup) as dest:
            src.backup(dest)
        r.submit(self.task("two"))
        checkpoint = issue_checkpoint(r.event_store, self.signer)
        shutil.copyfile(backup, self.file)
        with self.assertRaisesRegex(SealedJournalError, "rolled back"):
            verify_checkpoint(self.runtime().event_store,
                              checkpoint, self.signer.public_key())

    def test_different_valid_fork_with_same_key_is_refused(self):
        r = self.runtime()
        r.submit(self.task("one"))
        other = self.root / "fork.sqlite"
        with sqlite3.connect(self.file) as src, sqlite3.connect(other) as dest:
            src.backup(dest)
        r.submit(self.task("original"))
        checkpoint = issue_checkpoint(r.event_store, self.signer)
        fork = self.runtime(other)
        fork.submit(self.task("alternate"))
        with self.assertRaisesRegex(SealedJournalError, "differs"):
            verify_checkpoint(fork.event_store, checkpoint, self.signer.public_key())

    def test_other_journal_keyed_same_way_is_refused(self):
        r = self.runtime()
        checkpoint = issue_checkpoint(r.event_store, self.signer)
        other = self.root / "other.sqlite"
        with self.assertRaisesRegex(SealedJournalError, "different journal"):
            verify_checkpoint(self.runtime(other).event_store,
                              checkpoint, self.signer.public_key())

    def test_wrong_signer_or_modified_checkpoint_is_refused(self):
        r = self.runtime()
        r.submit(self.task("one"))
        checkpoint = issue_checkpoint(r.event_store, self.signer)
        with self.assertRaises(SealedJournalError):
            verify_checkpoint(r.event_store, checkpoint,
                              Ed25519PrivateKey.generate().public_key())
        for name, value in (("sequence", 0),
                            ("journal_identity", "f"*64),
                            ("head_digest", "0"*64),
                            ("signature", "0"*128)):
            changed = {**checkpoint, name: value}
            with self.subTest(field=name), self.assertRaises(SealedJournalError):
                verify_checkpoint(r.event_store, changed, self.signer.public_key())

    def test_checkpoint_cannot_be_signed_over_unobserved_concurrent_advance(self):
        a = self.runtime()
        b = self.runtime()
        b.submit(self.task("external"))
        with self.assertRaisesRegex(SealedJournalError, "changed outside runtime"):
            issue_checkpoint(a.event_store, self.signer)

    def test_checkpoint_cannot_sign_a_corrupted_atomic_replay_table(self):
        native = self.runtime()
        native.submit(self.task("protected"), admission=("research", "event-one", "b"*64))
        self.assertEqual(issue_checkpoint(native.event_store, self.signer)["sequence"], 1)
        with sqlite3.connect(self.file) as db:
            db.execute("DELETE FROM admitted")
        with self.assertRaisesRegex(SealedJournalError, "replay table differs"):
            issue_checkpoint(native.event_store, self.signer)

    def test_service_only_admits_trusted_anchor_on_restart(self):
        root = self.root / "service"
        service = EcosystemService(data_dir=root, protected_runtime_key=self.key)
        service.runtime.submit(self.task("one"))
        checkpoint = issue_checkpoint(service.runtime.event_store, self.signer)
        service2 = EcosystemService(data_dir=root, protected_runtime_key=self.key,
                     trusted_runtime_checkpoint=checkpoint,
                     trusted_checkpoint_public_key=self.signer.public_key())
        self.assertEqual(service2.runtime.get("one"), self.task("one"))
        with self.assertRaises(ValueError):
            EcosystemService(data_dir=root, protected_runtime_key=self.key,
                             trusted_runtime_checkpoint=checkpoint)
        with self.assertRaises(SealedJournalError):
            EcosystemService(data_dir=root, protected_runtime_key=self.key,
                             trusted_runtime_checkpoint=checkpoint,
                             trusted_checkpoint_public_key=Ed25519PrivateKey.generate().public_key())

    def test_missing_sealed_history_not_recreated_behind_checkpoint(self):
        root = self.root / "missing"
        root.mkdir()
        journal = self.runtime()
        journal.submit(self.task("one"))
        checkpoint = issue_checkpoint(journal.event_store, self.signer)
        with self.assertRaisesRegex(ValueError, "missing sealed history"):
            EcosystemService(data_dir=root, protected_runtime_key=self.key,
                             trusted_runtime_checkpoint=checkpoint,
                             trusted_checkpoint_public_key=self.signer.public_key())
        self.assertFalse((root / "runtime.sealed.sqlite").exists())


if __name__ == "__main__":
    unittest.main()
