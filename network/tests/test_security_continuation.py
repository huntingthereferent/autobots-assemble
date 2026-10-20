"""Real crypto round trips, fail-closed checks and finite motion invariants."""
from __future__ import annotations

import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from security.continuation import (
    EnvelopeError, MAX_PLAINTEXT, ReplayLedger, envelope_digest, open_record, seal_record,
)
from security.finite_motion import BipolarBoundary


class AuthenticatedContinuationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.sender = Ed25519PrivateKey.generate()
        self.recipient = X25519PrivateKey.generate()
        self.ledger = ReplayLedger(Path(self.tmp.name) / "admission.sqlite3")
        self.kw = {"expected_lane": "nih-phase2", "expected_parent_sha256": None,
                   "sender_public_key": self.sender.public_key(),
                   "recipient_private_key": self.recipient,
                   "replay_ledger": self.ledger}

    def sealed(self, payload=b"finite evidence", event_id="event-1", parent=None):
        return seal_record(payload, lane="nih-phase2", event_id=event_id,
                           parent_sha256=parent, sender_private_key=self.sender,
                           recipient_public_key=self.recipient.public_key())

    def test_real_roundtrip_and_no_plaintext_in_envelope(self):
        record = self.sealed(b"private longitudinal observation")
        self.assertNotIn("private longitudinal observation", str(record))
        self.assertEqual(open_record(record, **self.kw), b"private longitudinal observation")

    def test_replay_refused_after_restart(self):
        record = self.sealed()
        open_record(record, **self.kw)
        self.kw["replay_ledger"] = ReplayLedger(Path(self.tmp.name) / "admission.sqlite3")
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            open_record(record, **self.kw)

    def test_duplicate_identifier_even_with_new_ciphertext(self):
        open_record(self.sealed(b"first"), **self.kw)
        with self.assertRaisesRegex(EnvelopeError, "replayed"):
            open_record(self.sealed(b"second"), **self.kw)

    def test_wrong_sender_and_recipient_are_refused(self):
        record = self.sealed()
        with self.assertRaisesRegex(EnvelopeError, "not pinned"):
            open_record(record, **{**self.kw, "sender_public_key": Ed25519PrivateKey.generate().public_key()})
        with self.assertRaisesRegex(EnvelopeError, "wrong recipient"):
            open_record(record, **{**self.kw, "recipient_private_key": X25519PrivateKey.generate()})
        self.assertEqual(open_record(record, **self.kw), b"finite evidence")

    def test_lane_parent_and_ciphertext_mutations_refused(self):
        original = self.sealed()
        for field, other in (("lane", "elsewhere"), ("parent_sha256", "0" * 64),
                             ("ciphertext", "AAAA"), ("event_id", "event-2"),
                             ("recipient_key_sha256", "0" * 64)):
            with self.subTest(field=field):
                bad = copy.deepcopy(original)
                bad[field] = other
                with self.assertRaises(EnvelopeError):
                    open_record(bad, **self.kw)
        # Rejected envelopes never consume the good event identifier.
        self.assertEqual(open_record(original, **self.kw), b"finite evidence")

    def test_signature_tamper_and_unrecognized_fields_refused(self):
        original = self.sealed()
        bad = dict(original, signature="A" * 88)
        with self.assertRaises(EnvelopeError):
            open_record(bad, **self.kw)
        bad = dict(original, is_owner=True)
        with self.assertRaisesRegex(EnvelopeError, "shape"):
            open_record(bad, **self.kw)

    def test_real_parent_continuation(self):
        parent = self.sealed(event_id="root")
        parent_digest = envelope_digest(parent)
        open_record(parent, **self.kw)
        child = self.sealed(b"child", event_id="child", parent=parent_digest)
        with self.assertRaisesRegex(EnvelopeError, "parent"):
            open_record(child, **self.kw)
        self.assertEqual(open_record(child, **{**self.kw, "expected_parent_sha256": parent_digest}), b"child")

    def test_bounds_and_invalid_names(self):
        with self.assertRaisesRegex(EnvelopeError, "bounded bytes"):
            self.sealed(b"x" * (MAX_PLAINTEXT + 1))
        with self.assertRaisesRegex(EnvelopeError, "bounded identifier"):
            seal_record(b"x", lane="../bad", event_id="e", parent_sha256=None,
                        sender_private_key=self.sender,
                        recipient_public_key=self.recipient.public_key())
        bad = self.sealed()
        bad["ciphertext"] = "X" * 1_500_001
        with self.assertRaises(EnvelopeError):
            open_record(bad, **self.kw)

    def test_ledger_symlink_refused(self):
        link = Path(self.tmp.name) / "alias"
        link.symlink_to(Path(self.tmp.name) / "admission.sqlite3")
        with self.assertRaisesRegex(EnvelopeError, "symlink"):
            ReplayLedger(link)

    def test_distinct_seals_are_not_identical(self):
        a, b = self.sealed(), self.sealed()
        self.assertNotEqual(a["ciphertext"], b["ciphertext"])
        self.assertNotEqual(a["ephemeral_public"], b["ephemeral_public"])


class BipolarMovementTests(unittest.TestCase):
    def test_observed_oscillation_no_privileged_write(self):
        model = BipolarBoundary()
        original = model.protected_snapshot()
        observed = [model.move(admitted=False) for _ in range(1000)]
        self.assertEqual(model.protected_snapshot(), original)
        self.assertEqual({e.orientation for e in observed}, {-1, 1})
        self.assertEqual(observed[-1].step, 1000)
        self.assertTrue(all(e.view == "bounded-probe" for e in observed))

    def test_interleaving_does_not_change_authorized_trajectory(self):
        expected = BipolarBoundary()
        mixed = BipolarBoundary()
        for i in range(200):
            for _ in range(i % 7):
                mixed.move(admitted=False)
            self.assertEqual(expected.move(admitted=True), mixed.move(admitted=True))
        self.assertEqual(expected.protected_snapshot(), mixed.protected_snapshot())

    def test_admission_is_external_not_inferred_from_oscillation(self):
        model = BipolarBoundary()
        with self.assertRaises(TypeError):
            model.move(admitted="oscillating")
        self.assertEqual(model.protected_snapshot(), (1, 0))


if __name__ == "__main__":
    unittest.main()
