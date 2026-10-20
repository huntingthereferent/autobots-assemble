"""Offline recovery escrow tests: no unverified key substitution."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from security.continuation import EnvelopeError, ReplayLedger
from security.journal_checkpoint import issue_checkpoint, verify_checkpoint
from security.key_recovery import issue_recovery_envelope, recover_journal_key
from security.sealed_journal import SealedRuntimeJournal, SealedJournalError


class OfflineJournalKeyRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.key = os.urandom(32)
        self.checkpoint_signer = Ed25519PrivateKey.generate()
        self.operator = Ed25519PrivateKey.generate()
        self.recovery_recipient = X25519PrivateKey.generate()
        self.file = self.path / "native.sealed.sqlite"
        self.store = SealedRuntimeJournal(self.file, key=self.key)
        self.runtime = HandoffRuntime(event_store=self.store)
        self.runtime.submit(Handoff(handoff_id="a", referent="private secret 1223",
                                    from_actor="owner", to_actor="worker",
                                    required_relation="observe"))
        self.anchor = issue_checkpoint(self.store, self.checkpoint_signer)

    def package(self):
        return issue_recovery_envelope(
            self.store, self.key, signed_checkpoint=self.anchor,
            trusted_checkpoint_public_key=self.checkpoint_signer.public_key(),
            operator_signing_private_key=self.operator,
            offline_recovery_public_key=self.recovery_recipient.public_key())

    def recover(self, envelope=None, **overrides):
        values = dict(
            trusted_journal_identity=self.anchor["journal_identity"],
            signed_checkpoint=self.anchor,
            trusted_operator_public_key=self.operator.public_key(),
            offline_recovery_private_key=self.recovery_recipient,
            recovery_ledger=ReplayLedger(self.path / "recovery.sqlite"))
        values.update(overrides)
        return recover_journal_key(envelope or self.package(), **values)

    def test_offline_recovery_reopens_original_and_checks_anchor(self):
        escrow = self.package()
        self.assertNotIn(self.key.hex().encode(), str(escrow).encode())
        original_key = self.recover(escrow)
        self.assertEqual(original_key, self.key)
        restored = SealedRuntimeJournal(self.file, key=original_key)
        verify_checkpoint(restored, self.anchor, self.checkpoint_signer.public_key())
        self.assertEqual(HandoffRuntime(event_store=restored).get("a").referent,
                         "private secret 1223")

    def test_wrong_recovery_recipient_refused(self):
        with self.assertRaises(EnvelopeError):
            self.recover(offline_recovery_private_key=X25519PrivateKey.generate())

    def test_untrusted_operator_key_refused(self):
        with self.assertRaises(EnvelopeError):
            self.recover(trusted_operator_public_key=Ed25519PrivateKey.generate().public_key())

    def test_wrong_journal_identity_refused(self):
        with self.assertRaisesRegex(EnvelopeError, "identity mismatch"):
            self.recover(trusted_journal_identity="f"*64)

    def test_recovery_package_replay_refused(self):
        envelope = self.package()
        self.recover(envelope)
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            self.recover(envelope)

    def test_wrong_candidate_key_cannot_be_escrowed(self):
        with self.assertRaises(SealedJournalError):
            issue_recovery_envelope(
                self.store, os.urandom(32),
                signed_checkpoint=self.anchor,
                trusted_checkpoint_public_key=self.checkpoint_signer.public_key(),
                operator_signing_private_key=self.operator,
                offline_recovery_public_key=self.recovery_recipient.public_key())

    def test_forged_checkpoint_refused_on_issuance(self):
        forged = {**self.anchor, "head_digest": "0"*64}
        with self.assertRaises(SealedJournalError):
            issue_recovery_envelope(
                self.store, self.key, signed_checkpoint=forged,
                trusted_checkpoint_public_key=self.checkpoint_signer.public_key(),
                operator_signing_private_key=self.operator,
                offline_recovery_public_key=self.recovery_recipient.public_key())


if __name__ == "__main__":
    unittest.main()
