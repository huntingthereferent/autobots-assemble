"""Two independent sealed source journals and offline receipt-only observer.

No network access, no shared native journal, and no decryption key moves
between owners. Positive cases and negative evidence are source-bound.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import base64
import os
import sqlite3
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from security.journal_checkpoint import issue_checkpoint
from security.remote_witness import (
    RemoteWitnessLedger, export_witness_span, verify_witness_span,
)
from security.sealed_journal import SealedJournalError, SealedRuntimeJournal


class IndependentRemoteWitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.root_a = self.root / "source-a"
        self.root_b = self.root / "source-b"
        self.root_observer = self.root / "observer"
        for root in (self.root_a, self.root_b, self.root_observer):
            root.mkdir()
        self.signer_a = Ed25519PrivateKey.generate()
        self.signer_b = Ed25519PrivateKey.generate()
        self.key_a, self.key_b = os.urandom(32), os.urandom(32)
        self.file_a = self.root_a / "source.sealed.sqlite"
        self.file_b = self.root_b / "source.sealed.sqlite"
        self.a = HandoffRuntime(event_store=SealedRuntimeJournal(
            self.file_a, key=self.key_a))
        self.b = HandoffRuntime(event_store=SealedRuntimeJournal(
            self.file_b, key=self.key_b))
        self.base_a = issue_checkpoint(self.a.event_store, self.signer_a)
        self.base_b = issue_checkpoint(self.b.event_store, self.signer_b)
        self.observer_path = self.root_observer / "observed.sqlite"
        self.observer = RemoteWitnessLedger(self.observer_path)
        self.observer.enroll(
            "alpha", signed_base_checkpoint=self.base_a,
            trusted_source_public_key=self.signer_a.public_key())
        self.observer.enroll(
            "beta", signed_base_checkpoint=self.base_b,
            trusted_source_public_key=self.signer_b.public_key())

    @staticmethod
    def task(identifier):
        return Handoff(handoff_id=identifier, referent="source-private-"+identifier,
                       from_actor="origin", to_actor="worker",
                       required_relation="observe",
                       inputs={"private_source": identifier + "-hidden"})

    def advance_a(self, identifiers, base=None):
        for identifier in identifiers:
            self.a.submit(self.task(identifier))
        tip = issue_checkpoint(self.a.event_store, self.signer_a)
        return export_witness_span(
            self.a.event_store, base_checkpoint=base or self.base_a,
            tip_checkpoint=tip, source_public_key=self.signer_a.public_key())

    def advance_b(self, identifiers, base=None):
        for identifier in identifiers:
            self.b.submit(self.task(identifier))
        tip = issue_checkpoint(self.b.event_store, self.signer_b)
        return export_witness_span(
            self.b.event_store, base_checkpoint=base or self.base_b,
            tip_checkpoint=tip, source_public_key=self.signer_b.public_key())

    def test_two_owned_histories_advance_independently_without_shared_key(self):
        first_a = self.advance_a(["a-1", "a-2"])
        first_b = self.advance_b(["b-1"])
        # Only public signatures and ciphertext frames leave the sources.
        exported = str(first_a) + str(first_b)
        self.assertNotIn("source-private-", exported)
        self.assertNotIn("hidden", exported)
        self.assertNotIn(self.key_a.hex(), exported)
        self.assertNotIn(self.key_b.hex(), exported)
        result_a = self.observer.observe(
            "alpha", first_a, trusted_source_public_key=self.signer_a.public_key())
        result_b = self.observer.observe(
            "beta", first_b, trusted_source_public_key=self.signer_b.public_key())
        self.assertEqual((result_a["sequence"], result_b["sequence"]), (2, 1))
        previous_a = self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key())
        next_a = self.advance_a(["a-3"], base=previous_a)
        final_a = self.observer.observe(
            "alpha", next_a, trusted_source_public_key=self.signer_a.public_key())
        self.assertEqual(final_a["sequence"], 3)
        # Restart the observer. Source and observer own distinct SQLite files.
        restarted = RemoteWitnessLedger(self.observer_path)
        self.assertEqual(restarted.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key())["sequence"], 3)
        self.assertEqual(restarted.current(
            "beta", trusted_source_public_key=self.signer_b.public_key())["sequence"], 1)
        with sqlite3.connect(self.observer_path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM movements").fetchone()[0], 3)
        self.assertEqual(len(self.a.event_store.all()), 3)
        self.assertEqual(len(self.b.event_store.all()), 1)

    def test_sender_cannot_implicitly_enroll_new_identity(self):
        bundle = self.advance_a(["a-1"])
        with self.assertRaisesRegex(SealedJournalError, "not independently pinned"):
            self.observer.observe(
                "invented-host", bundle,
                trusted_source_public_key=self.signer_a.public_key())
        with self.assertRaisesRegex(SealedJournalError, "already operator-enrolled"):
            self.observer.enroll(
                "alpha", signed_base_checkpoint=self.base_a,
                trusted_source_public_key=self.signer_a.public_key())
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key()), self.base_a)

    def test_wrong_pinned_signer_or_source_refused(self):
        bundle = self.advance_a(["a-1"])
        with self.assertRaises(SealedJournalError):
            self.observer.observe(
                "alpha", bundle, trusted_source_public_key=self.signer_b.public_key())
        with self.assertRaises(SealedJournalError):
            self.observer.observe(
                "beta", bundle, trusted_source_public_key=self.signer_b.public_key())
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key()), self.base_a)

    def test_ciphertext_tampering_and_missing_frame_refused(self):
        bundle = self.advance_a(["a-1", "a-2"])
        attacks = []
        modified = deepcopy(bundle)
        cipher = bytearray(base64.b64decode(modified["frames"][0]["cipher"]))
        cipher[2] ^= 1
        modified["frames"][0]["cipher"] = base64.b64encode(cipher).decode("ascii")
        attacks.append(modified)
        modified = deepcopy(bundle)
        modified["frames"].pop(0)
        attacks.append(modified)
        modified = deepcopy(bundle)
        modified["frames"].reverse()
        attacks.append(modified)
        modified = deepcopy(bundle)
        modified["frames"][0]["nonce"] = "invalid!!"
        attacks.append(modified)
        for attack in attacks:
            with self.subTest(attack=attack["frames"][:1]):
                with self.assertRaises(SealedJournalError):
                    self.observer.observe(
                        "alpha", attack,
                        trusted_source_public_key=self.signer_a.public_key())
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key()), self.base_a)

    def test_signed_tip_without_contiguous_ciphertext_is_not_enough(self):
        bundle = self.advance_a(["a-1", "a-2"])
        fake = {"version": bundle["version"],
                "tip_checkpoint": bundle["tip_checkpoint"], "frames": []}
        with self.assertRaisesRegex(SealedJournalError, "missing"):
            self.observer.observe(
                "alpha", fake, trusted_source_public_key=self.signer_a.public_key())
        # The actual contiguous chain is accepted.
        self.observer.observe(
            "alpha", bundle, trusted_source_public_key=self.signer_a.public_key())

    def test_replay_and_out_of_order_observation_rejected(self):
        first = self.advance_a(["a-1"])
        self.observer.observe(
            "alpha", first, trusted_source_public_key=self.signer_a.public_key())
        with self.assertRaises(SealedJournalError):
            self.observer.observe(
                "alpha", first, trusted_source_public_key=self.signer_a.public_key())
        later = self.advance_a(["a-2"], base=first["tip_checkpoint"])
        self.observer.observe(
            "alpha", later, trusted_source_public_key=self.signer_a.public_key())
        with self.assertRaises(SealedJournalError):
            self.observer.observe(
                "alpha", first, trusted_source_public_key=self.signer_a.public_key())

    def test_other_source_ciphertext_cannot_extend_alpha(self):
        bundle = self.advance_b(["b-1"])
        with self.assertRaises(SealedJournalError):
            verify_witness_span(
                bundle, base_checkpoint=self.base_a,
                source_public_key=self.signer_a.public_key())

    def test_duplicate_concurrent_observations_admit_one(self):
        bundle = self.advance_a(["a-1"])
        observer_two = RemoteWitnessLedger(self.observer_path)
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(
                lambda obs: self._observe_or_refuse(obs, bundle),
                (self.observer, observer_two)))
        self.assertEqual(sorted(outcomes), ["accepted", "refused"])
        with sqlite3.connect(self.observer_path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM movements").fetchone()[0], 1)
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key())["sequence"], 1)

    def _observe_or_refuse(self, observer, bundle):
        try:
            observer.observe(
                "alpha", bundle, trusted_source_public_key=self.signer_a.public_key())
            return "accepted"
        except SealedJournalError:
            return "refused"

    def test_same_signer_two_valid_forks_cannot_be_merged_as_one_history(self):
        # Copy the encrypted database *before* either branch moves. Both
        # branches have the same authentic journal identity and signer.
        other_path = self.root_a / "forked-copy.sqlite"
        with sqlite3.connect(self.file_a) as original, sqlite3.connect(other_path) as copy:
            original.backup(copy)
        forked = HandoffRuntime(event_store=SealedRuntimeJournal(
            other_path, key=self.key_a))
        first = self.advance_a(["a-real"])
        forked.submit(self.task("a-other"))
        forked_tip = issue_checkpoint(forked.event_store, self.signer_a)
        conflicting = export_witness_span(
            forked.event_store, base_checkpoint=self.base_a,
            tip_checkpoint=forked_tip,
            source_public_key=self.signer_a.public_key())
        # Each fork independently verifies from the original pinned baseline.
        self.assertEqual(
            verify_witness_span(conflicting, base_checkpoint=self.base_a,
                                source_public_key=self.signer_a.public_key()),
            forked_tip)
        self.observer.observe(
            "alpha", first, trusted_source_public_key=self.signer_a.public_key())
        with self.assertRaises(SealedJournalError):
            self.observer.observe(
                "alpha", conflicting,
                trusted_source_public_key=self.signer_a.public_key())
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key()),
            first["tip_checkpoint"])

    def test_bounded_span_not_unbounded_transfer(self):
        for i in range(65):
            self.a.submit(self.task("a-"+str(i)))
        tip = issue_checkpoint(self.a.event_store, self.signer_a)
        with self.assertRaisesRegex(SealedJournalError, "bounded"):
            export_witness_span(
                self.a.event_store, base_checkpoint=self.base_a,
                tip_checkpoint=tip, source_public_key=self.signer_a.public_key())
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.signer_a.public_key()), self.base_a)


if __name__ == "__main__":
    unittest.main()
