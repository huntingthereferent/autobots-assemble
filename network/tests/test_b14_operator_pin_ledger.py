"""B14 local operator trust lifecycle and actual B3 native signed delivery.

Operator reference strings and ephemeral Ed25519 keys are explicit fixtures,
not authentication of real people or a production source-owner enrollment.
"""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from systems.workspace.b11_native_local_delivery import PROTOCOL
from systems.workspace.b14_operator_pin_ledger import (
    OperatorPinLedger, B14OperatorTrustedDelivery,
)
from systems.workspace.observed_event_journal import LOCAL_PASS, START


NAME = "finite-source-native"
EDITION = "a" * 64


class B14PinLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "trust.jsonl"
        self.ledger = OperatorPinLedger(self.path)
        self.one = sha256(b"public pin 1").hexdigest()
        self.two = sha256(b"public pin 2").hexdigest()
        self.three = sha256(b"public pin 3").hexdigest()

    def enroll(self, pin=None):
        pin = pin or self.one
        return self.ledger.enroll(
            source_name=NAME, source_edition=EDITION, pin_sha256=pin,
            operator_ref="operator-local-01", verification_ref="external-pin-check:case-1",
            confirm_pin_sha256=pin,
        )

    def rotate(self, old=None, new=None):
        old, new = old or self.one, new or self.two
        return self.ledger.rotate(
            source_name=NAME, source_edition=EDITION, prior_sha256=old,
            new_pin_sha256=new, operator_ref="operator-local-01",
            verification_ref="external-pin-check:rotation",
            confirm_prior_sha256=old, confirm_new_sha256=new,
        )

    def revoke(self, pin=None):
        pin = pin or self.one
        return self.ledger.revoke(
            source_name=NAME, source_edition=EDITION, pin_sha256=pin,
            operator_ref="operator-local-01", verification_ref="external-revocation:operator",
            confirm_pin_sha256=pin,
        )

    def test_no_enrollment_defaults_to_untrusted(self):
        self.assertIsNone(self.ledger.current(NAME, EDITION))
        self.assertFalse(self.ledger.is_current(NAME, EDITION, self.one))
        with self.assertRaises(PermissionError):
            self.ledger.require_current(NAME, EDITION, self.one)

    def test_explicit_operator_enrollment_writes_no_private_key(self):
        entry = self.enroll()
        self.assertEqual(entry["kind"], "ENROLL")
        self.assertTrue(self.ledger.is_current(NAME, EDITION, self.one))
        self.assertFalse(self.ledger.is_current(NAME, EDITION, self.two))
        self.assertNotIn("private", self.path.read_text())
        self.assertEqual(len(self.ledger.history()), 1)

    def test_unconfirmed_enrollment_rejected_with_no_history(self):
        with self.assertRaises(PermissionError):
            self.ledger.enroll(
                source_name=NAME, source_edition=EDITION,
                pin_sha256=self.one, operator_ref="operator",
                verification_ref="external", confirm_pin_sha256=self.two,
            )
        self.assertFalse(self.path.exists())

    def test_duplicate_and_historical_pin_reuse_rejected(self):
        self.enroll()
        with self.assertRaises(ValueError):
            self.enroll()
        self.revoke()
        with self.assertRaises(ValueError):
            self.enroll()
        self.assertIsNone(self.ledger.current(NAME, EDITION))

    def test_explicit_rotation_revokes_old_pin_immediately(self):
        self.enroll()
        self.rotate()
        self.assertFalse(self.ledger.is_current(NAME, EDITION, self.one))
        self.assertTrue(self.ledger.is_current(NAME, EDITION, self.two))
        self.assertEqual([x["kind"] for x in self.ledger.history()], ["ENROLL", "ROTATE"])

    def test_rotation_requires_both_exact_confirmations(self):
        self.enroll()
        with self.assertRaises(PermissionError):
            self.ledger.rotate(
                source_name=NAME, source_edition=EDITION,
                prior_sha256=self.one, new_pin_sha256=self.two,
                operator_ref="operator", verification_ref="external",
                confirm_prior_sha256=self.one, confirm_new_sha256=self.three,
            )
        with self.assertRaises(ValueError):
            self.rotate(old=self.three)
        self.assertEqual(self.ledger.current(NAME, EDITION), self.one)

    def test_rotation_cannot_reactivate_previous_public_key(self):
        self.enroll()
        self.rotate()
        with self.assertRaises(ValueError):
            self.rotate(old=self.two, new=self.one)
        self.assertEqual(self.ledger.current(NAME, EDITION), self.two)

    def test_revocation_is_exact_and_idempotence_does_not_reenroll(self):
        self.enroll()
        with self.assertRaises(ValueError):
            self.revoke(self.two)
        self.revoke()
        with self.assertRaises(ValueError):
            self.revoke()
        self.assertIsNone(self.ledger.current(NAME, EDITION))

    def test_new_distinct_pin_after_revocation_needs_new_explicit_enrollment(self):
        self.enroll()
        self.revoke()
        self.enroll(self.two)
        self.assertFalse(self.ledger.is_current(NAME, EDITION, self.one))
        self.assertTrue(self.ledger.is_current(NAME, EDITION, self.two))

    def test_other_source_edition_is_not_implicitly_authorized(self):
        self.enroll()
        self.assertIsNone(self.ledger.current(NAME, "different-edition"))
        self.assertIsNone(self.ledger.current("other-source", EDITION))

    def test_corrupted_hash_or_chain_fails_closed(self):
        self.enroll()
        self.rotate()
        original = self.path.read_text()
        self.path.write_text(original.replace(self.two, self.three), encoding="utf8")
        with self.assertRaises(ValueError):
            self.ledger.current(NAME, EDITION)
        with self.assertRaises(ValueError):
            self.revoke(self.two)

    def test_duplicate_json_key_fails_closed(self):
        self.enroll()
        row = self.path.read_text().splitlines()[0]
        self.path.write_text(row.replace('"kind":', '"kind":"ENROLL","kind":'),
                             encoding="utf8")
        with self.assertRaises(ValueError):
            self.ledger.history()

    def test_truncated_final_line_fails_closed(self):
        self.enroll()
        self.path.write_bytes(self.path.read_bytes()[:-1])
        with self.assertRaises(ValueError):
            self.ledger.current(NAME, EDITION)

    def test_symlinked_ledger_is_rejected(self):
        actual = Path(self.tmp.name) / "real.jsonl"
        self.enroll()
        actual.write_bytes(self.path.read_bytes())
        self.path.unlink()
        self.path.symlink_to(actual)
        with self.assertRaises(ValueError):
            self.ledger.history()
        with self.assertRaises(ValueError):
            self.enroll(self.two)


class B14RealB3TrustTests(unittest.TestCase):
    def setUp(self):
        from network.tests.test_b13_offline_owner_delivery import B13OfflineSourceTests
        self.fixture = B13OfflineSourceTests(
            "test_cross_process_prepare_external_sign_deliver_native"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fx = self.fixture.fx
        self.fixture.execute_b3()
        self.edition = self.fixture.fx.edition
        self.pin_path = self.fixture.pin_file
        self.digest = self.fixture.pin_digest
        self.trust_path = self.fx.root / "operator-trust.jsonl"
        self.trust = OperatorPinLedger(self.trust_path)

    def enroll(self):
        return self.trust.enroll(
            source_name=NAME, source_edition=self.edition, pin_sha256=self.digest,
            operator_ref="ephemeral-test-operator",
            verification_ref="fixture-out-of-band-key-confirmation",
            confirm_pin_sha256=self.digest,
        )

    def revoke(self):
        return self.trust.revoke(
            source_name=NAME, source_edition=self.edition, pin_sha256=self.digest,
            operator_ref="ephemeral-test-operator",
            verification_ref="fixture-operator-revocation",
            confirm_pin_sha256=self.digest,
        )

    def host(self, *, pin_path=None, trust_path=None, observed_path=None):
        return B14OperatorTrustedDelivery(
            trust_ledger_path=trust_path or self.trust_path,
            public_key_path=pin_path or self.pin_path,
            expected_public_key_sha256=self.digest,
            construction_dir=self.fx.graph.data_dir,
            native_data_dir=self.fx.native.data,
            observed_journal_path=observed_path or (self.fx.root / "observed.jsonl"),
            lane_handoff_id=self.fx.source.lane_id,
            opening_id=self.fx.source.opening_id,
            job_id=self.fx.source.job_id,
            confirm_source_job=self.fx.source.job_id,
        )

    def prepare(self, host):
        return host.prepare(
            goal_id=self.fx.goal, candidate_id=self.fx.candidate,
            route=self.fx.route,
        )

    def envelope(self, request):
        return {
            "protocol": PROTOCOL, "receipt": request["receipt"],
            "signature": self.fx.signer.sign(
                bytes.fromhex(request["canonical_bytes_hex"])
            ).hex(),
        }

    def test_unprovisioned_source_fails_before_new_delivery(self):
        with self.assertRaises(PermissionError):
            self.host()

    def test_enrolled_real_b3_result_crosses_without_reexecution(self):
        self.enroll()
        host = self.host()
        req = self.prepare(host)
        original = (self.fx.native.data / "runtime.jsonl").read_bytes()
        payload = self.envelope(host.signing_request(req))
        event = host.deliver(
            request_id=req, confirm_request=req,
            approved=True, signed_envelope=payload,
        )
        self.assertEqual(event.handoff_id, req)
        self.assertEqual(host.host.b12.bridge.projection(req)["state"], "CROSSED")
        self.assertEqual(original, (self.fx.native.data / "runtime.jsonl").read_bytes())
        self.assertFalse(host.host.b12.bridge.projection(req)["whole_route_verified"])
        events = host.host.b12.delivery.journal.for_handoff(req)
        self.assertEqual(sum(e.event_type == START for e in events), 1)

    def test_revocation_after_prepare_blocks_signing_request_and_delivery(self):
        self.enroll()
        host = self.host()
        req = self.prepare(host)
        signed = self.envelope(host.signing_request(req))
        self.revoke()
        with self.assertRaises(PermissionError):
            host.signing_request(req)
        with self.assertRaises(PermissionError):
            host.deliver(
                request_id=req, confirm_request=req,
                approved=True, signed_envelope=signed,
            )
        self.assertEqual(host.host.b12.bridge.projection(req)["state"], "OPEN")
        self.assertFalse(any(x.event_type == LOCAL_PASS for x in
                             host.host.b12.delivery.journal.for_handoff(req)))

    def test_revoked_key_rejects_new_host_even_if_public_bytes_still_exist(self):
        self.enroll()
        self.revoke()
        with self.assertRaises(PermissionError):
            self.host()

    def test_rotation_blocks_prior_host_and_requires_new_pinned_bytes(self):
        self.enroll()
        old = self.host()
        req = self.prepare(old)
        signed = self.envelope(old.signing_request(req))
        other = Ed25519PrivateKey.generate()
        other_public = other.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw,
        )
        other_digest = sha256(other_public).hexdigest()
        self.trust.rotate(
            source_name=NAME, source_edition=self.edition,
            prior_sha256=self.digest, new_pin_sha256=other_digest,
            operator_ref="ephemeral-test-operator",
            verification_ref="fixture-key-change",
            confirm_prior_sha256=self.digest, confirm_new_sha256=other_digest,
        )
        with self.assertRaises(PermissionError):
            old.deliver(request_id=req, confirm_request=req,
                        approved=True, signed_envelope=signed)
        with self.assertRaises(PermissionError):
            self.host()
        self.assertFalse(any(x.event_type == START for x in
                             old.host.b12.delivery.journal.for_handoff(req)))

    def test_corrupted_trust_chain_blocks_existing_host_before_local_delivery(self):
        self.enroll()
        host = self.host()
        req = self.prepare(host)
        signed = self.envelope(host.signing_request(req))
        self.trust_path.write_text(self.trust_path.read_text().replace(
            '"ENROLL"', '"REVOKE"'), encoding="utf8")
        with self.assertRaises(ValueError):
            host.deliver(request_id=req, confirm_request=req,
                         approved=True, signed_envelope=signed)
        self.assertFalse(any(x.event_type == START for x in
                             host.host.b12.delivery.journal.for_handoff(req)))

    def test_trust_ledger_cannot_share_a_source_or_delivery_journal(self):
        self.enroll()
        with self.assertRaisesRegex(ValueError, "must be separate"):
            self.host(trust_path=self.fx.native.data / "runtime.jsonl")
        with self.assertRaisesRegex(ValueError, "must be separate"):
            self.host(trust_path=self.fx.root / "observed.jsonl")

    def test_new_native_source_edition_requires_new_exact_trust_pin(self):
        self.enroll()
        self.assertFalse(self.trust.is_current(NAME, "b" * 64, self.digest))


if __name__ == "__main__":
    unittest.main()
