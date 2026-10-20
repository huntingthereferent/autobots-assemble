"""A/B bipolar key-approach relationship, checked on real signed native ingress.

A failed approach must not alter the protected trajectory or read/use private
key exchange merely because it supplied an envelope-shaped request. This is
observational noninterference for this API, not protection from host compromise.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from security.continuation import EnvelopeError, ReplayLedger
from security.finite_motion import BipolarBoundary
from security.key_approach import KeyApproachBoundary
from security.runtime_ingress import (
    AuthenticatedHandoffIngress, IngressAuthority, seal_handoff)
from security.sealed_journal import SealedRuntimeJournal


class KeyApproachHarnessTests(unittest.TestCase):
    def test_external_approach_does_not_move_protected_trajectory(self):
        protected = KeyApproachBoundary()
        before = protected.snapshot()
        for _ in range(2000):
            observation = protected.approach()
            self.assertEqual(observation.view, "bounded-probe")
        after = protected.snapshot()
        self.assertEqual(before.protected_orientation, after.protected_orientation)
        self.assertEqual(after.protected_movements, 0)
        self.assertEqual(after.approach_movements, 2000)
        self.assertEqual(after.admitted_movements, 0)

    def test_trusted_admission_motion_independent_of_interleaved_approach(self):
        isolated = KeyApproachBoundary()
        exposed = KeyApproachBoundary()
        for step in range(99):
            isolated.admitted()
            for _ in range(step % 9):
                exposed.approach()
            exposed.admitted()
            self.assertEqual(
                isolated.snapshot().protected_orientation,
                exposed.snapshot().protected_orientation)
            self.assertEqual(isolated.snapshot().protected_movements,
                             exposed.snapshot().protected_movements)

    def test_motion_records_have_no_key_material_or_identity(self):
        harness = KeyApproachBoundary()
        self.assertEqual(
            set(harness.snapshot().__dict__),
            {"protected_orientation", "protected_movements",
             "approach_movements", "admitted_movements"})
        self.assertNotIn("secret", repr(harness.snapshot()).lower())


class RealKeyUseIngressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sender = Ed25519PrivateKey.generate()
        self.recipient = X25519PrivateKey.generate()
        self.runtime = HandoffRuntime(
            event_store=SealedRuntimeJournal(
                self.root / "native.sealed.sqlite", key=os.urandom(32)))
        self.ledger = ReplayLedger(self.root / "legacy-replay.sqlite")
        self.ingress = AuthenticatedHandoffIngress(
            self.runtime, self.ledger,
            IngressAuthority("key-approach", "owner", "worker",
                             self.sender.public_key(), self.recipient))

    def handoff(self, name):
        return Handoff(handoff_id=name, referent="protected-observation",
                       from_actor="owner", to_actor="worker",
                       required_relation="observe", inputs={"private": "DO-NOT-ECHO"})

    def envelope(self, name):
        return seal_handoff(
            self.handoff(name), lane="key-approach", parent_sha256=None,
            sender_private_key=self.sender,
            recipient_public_key=self.recipient.public_key())

    def test_invalid_approaches_do_not_advance_key_protected_movement(self):
        accepted = self.envelope("first")
        self.assertEqual(self.ingress.submit(accepted).status, "READY")
        after_first = self.ingress.key_approach.snapshot()
        self.assertEqual(after_first.protected_movements, 1)
        for _ in range(250):
            invalid = deepcopy(self.envelope("invalid"))
            invalid["signature"] = "A" * 88
            with self.assertRaises(EnvelopeError):
                self.ingress.submit(invalid)
        after_failures = self.ingress.key_approach.snapshot()
        self.assertEqual(after_failures.protected_movements, 1)
        self.assertEqual(after_failures.protected_orientation,
                         after_first.protected_orientation)
        self.assertEqual(after_failures.approach_movements, 251)
        self.assertEqual(after_failures.admitted_movements, 1)
        self.assertEqual(len(self.runtime.event_store.all()), 1)

        # New authorized movement continues the protected trajectory.
        self.assertEqual(self.ingress.submit(self.envelope("second")).status, "READY")
        after_second = self.ingress.key_approach.snapshot()
        self.assertEqual(after_second.protected_movements, 2)
        self.assertEqual(after_second.admitted_movements, 2)
        self.assertEqual(len(self.runtime.event_store.all()), 2)

    def test_invalid_signature_never_reaches_private_key_derive(self):
        valid = self.envelope("private-use-test")
        forged = deepcopy(valid)
        forged["signature"] = "A" * 88
        # _key is the HKDF input derived from private X25519 exchange.
        # Invalid signatures fail before that derivation is invoked.
        with patch("security.continuation._key",
                   side_effect=AssertionError("private key derivation reached")):
            with self.assertRaises(EnvelopeError):
                self.ingress.submit(forged)
        snap = self.ingress.key_approach.snapshot()
        self.assertEqual(snap.approach_movements, 1)
        self.assertEqual(snap.protected_movements, 0)
        self.assertEqual(self.runtime.snapshot(), {})

    def test_bad_actor_or_replay_cannot_advance_protected_movement(self):
        wrong = Handoff(handoff_id="wrong-owner", referent="x",
                        from_actor="stranger", to_actor="worker",
                        required_relation="observe")
        sealed = seal_handoff(
            wrong, lane="key-approach", parent_sha256=None,
            sender_private_key=self.sender,
            recipient_public_key=self.recipient.public_key())
        with self.assertRaises(EnvelopeError):
            self.ingress.submit(sealed)
        self.assertEqual(self.ingress.key_approach.snapshot().protected_movements, 0)
        good = self.envelope("first")
        self.ingress.submit(good)
        before = self.ingress.key_approach.snapshot()
        with self.assertRaises(EnvelopeError):
            self.ingress.submit(good)
        after = self.ingress.key_approach.snapshot()
        self.assertEqual(before.protected_movements, after.protected_movements)
        self.assertEqual(after.approach_movements, before.approach_movements + 1)

    def test_key_identity_unchanged_by_approaches_and_admission(self):
        from cryptography.hazmat.primitives import serialization
        sender_before = self.sender.private_bytes(
            serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
            serialization.NoEncryption())
        recipient_before = self.recipient.private_bytes(
            serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
            serialization.NoEncryption())
        invalid = deepcopy(self.envelope("invalid"))
        invalid["signature"] = "A" * 88
        with self.assertRaises(EnvelopeError):
            self.ingress.submit(invalid)
        self.ingress.submit(self.envelope("good"))
        self.assertEqual(sender_before, self.sender.private_bytes(
            serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
            serialization.NoEncryption()))
        self.assertEqual(recipient_before, self.recipient.private_bytes(
            serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
            serialization.NoEncryption()))
        self.assertNotIn(b"DO-NOT-ECHO",
                         (self.root / "native.sealed.sqlite").read_bytes())


if __name__ == "__main__":
    unittest.main()
