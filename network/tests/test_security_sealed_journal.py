"""Encrypted native runtime journal: real append/replay and failure witnesses."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sqlite3
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from security.sealed_journal import SealedJournalError, SealedRuntimeJournal


class SealedJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "journal.sealed.sqlite"
        self.key = os.urandom(32)

    def runtime(self, key=None):
        return HandoffRuntime(event_store=SealedRuntimeJournal(self.file, key=key or self.key))

    def handoff(self):
        return Handoff(handoff_id="sealed-1", referent="private native referent",
                       from_actor="owner", to_actor="worker",
                       required_relation="measure", inputs={"secret": "PRIVATE-PROBE-STRING-12345"},
                       required_witnesses=("native",),
                       admissible_evidence={"native": ("measured",)})

    def test_encrypted_real_native_submission_result_and_restart(self):
        r = self.runtime()
        r.submit(self.handoff())
        self.assertEqual(r.state("sealed-1").status, "READY")
        r.return_result("sealed-1", actor_id="worker",
            result=ExecutionResult(status="COMPLETE", output={"result": 12},
                evidence=(EvidenceRecord(condition="native", kind="measured", source="test"),)))
        self.assertEqual(r.state("sealed-1").status, "COMPLETE")
        self.assertEqual(len(r.event_store.all()), 2)
        disk = self.file.read_bytes()
        self.assertNotIn(b"PRIVATE-PROBE-STRING-12345", disk)
        self.assertNotIn(b"private native referent", disk)
        self.assertNotIn(b"sealed-1", disk)
        restored = self.runtime()
        self.assertEqual(restored.get("sealed-1"), self.handoff())
        self.assertEqual(restored.state("sealed-1").status, "COMPLETE")
        self.assertEqual(restored.state("sealed-1").output["result"], 12)
        self.assertEqual(len(restored.event_store.all()), 2)

    def test_wrong_key_refused_even_on_empty_journal(self):
        self.runtime()
        with self.assertRaisesRegex(SealedJournalError, "wrong key"):
            self.runtime(os.urandom(32))

    def test_missing_key_or_bad_key_length_fails(self):
        for value in (None, b"", b"0"*31, "not bytes"):
            with self.subTest(key=value):
                with self.assertRaises(SealedJournalError):
                    SealedRuntimeJournal(self.file, key=value)

    def test_mutated_ciphertext_fails_restore(self):
        r = self.runtime()
        r.submit(self.handoff())
        with sqlite3.connect(self.file) as db:
            cipher = bytearray(db.execute("SELECT cipher FROM records WHERE seq=1").fetchone()[0])
            cipher[-1] ^= 1
            db.execute("UPDATE records SET cipher=? WHERE seq=1", (bytes(cipher),))
        with self.assertRaisesRegex(SealedJournalError, "altered"):
            self.runtime()

    def test_corrupted_nonce_refused(self):
        r = self.runtime()
        r.submit(self.handoff())
        with sqlite3.connect(self.file) as db:
            db.execute("UPDATE records SET nonce=? WHERE seq=1", (b"bad",))
        with self.assertRaises(SealedJournalError):
            self.runtime()

    def test_missing_middle_record_fails_closed(self):
        r = self.runtime()
        r.submit(self.handoff())
        r.reopen("sealed-1", actor_id="owner", reason="continued movement")
        r.reopen("sealed-1", actor_id="owner", reason="continued again")
        with sqlite3.connect(self.file) as db:
            db.execute("DELETE FROM records WHERE seq=2")
        with self.assertRaisesRegex(SealedJournalError, "interrupted"):
            self.runtime()

    def test_second_writer_cannot_extend_stale_runtime(self):
        a = self.runtime()
        b = self.runtime()
        a.submit(self.handoff())
        with self.assertRaisesRegex(SealedJournalError, "concurrent"):
            b.submit(Handoff(handoff_id="other", referent="x", from_actor="owner",
                             to_actor="worker", required_relation="observe"))
        self.assertEqual(len(self.runtime().event_store.all()), 1)

    def test_reject_file_symlink(self):
        target = Path(self.temp.name) / "other"
        target.write_bytes(b"bad")
        self.file.symlink_to(target)
        with self.assertRaisesRegex(SealedJournalError, "unsafe"):
            self.runtime()


class ServiceSwitchTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.key = os.urandom(32)

    def service(self, key=None):
        from runtime.service import EcosystemService
        return EcosystemService(data_dir=self.root, protected_runtime_key=key)

    def test_opt_in_uses_native_encrypted_journal(self):
        s = self.service(self.key)
        self.assertIsInstance(s.runtime.event_store, SealedRuntimeJournal)
        s.runtime.submit(Handoff(handoff_id="private", referent="SECRET-PROTECTED",
                                 from_actor="owner", to_actor="worker", required_relation="observe"))
        self.assertFalse((self.root / "runtime.jsonl").exists())
        self.assertNotIn(b"SECRET-PROTECTED", (self.root / "runtime.sealed.sqlite").read_bytes())
        again = self.service(self.key)
        self.assertEqual(again.runtime.get("private").referent, "SECRET-PROTECTED")

    def test_opening_sealed_dir_without_key_refused(self):
        self.service(self.key)
        with self.assertRaisesRegex(ValueError, "sealed runtime exists"):
            self.service()

    def test_plaintext_history_must_not_be_silently_ignored(self):
        (self.root / "runtime.jsonl").write_text("existing journal")
        with self.assertRaisesRegex(ValueError, "plaintext runtime"):
            self.service(self.key)


if __name__ == "__main__":
    unittest.main()
