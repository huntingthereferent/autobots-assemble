"""Fail-closed local staging preflight tests; no worker is launched."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from time import monotonic, sleep

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from runtime.service import EcosystemService
from security.continuation import ReplayLedger
from security.deployment_preflight import check_staged_local_security
from security.journal_checkpoint import issue_checkpoint
from security.runtime_ingress import AuthenticatedHandoffIngress, IngressAuthority
from systems.workspace.b14_operator_pin_ledger import OperatorPinLedger


class StagedLocalSecurityGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.key = os.urandom(32)
        self.checkpoint_signer = Ed25519PrivateKey.generate()
        self.owner = Ed25519PrivateKey.generate()
        self.worker = Ed25519PrivateKey.generate()
        self.recipient = X25519PrivateKey.generate()
        self.service = EcosystemService(data_dir=self.root / "private",
                                        protected_runtime_key=self.key)
        self.trust = OperatorPinLedger(self.root / "policy.jsonl")
        self.ledger = ReplayLedger(self.root / "replay.sqlite")
        self.anchor = issue_checkpoint(self.service.runtime.event_store,
                                        self.checkpoint_signer)
        self.initial = tuple(self.service.runtime.event_store.all())

    def install(self, role):
        signer, receiver, key = (("owner", "worker", self.owner) if role == "submit"
                                  else ("worker", "owner", self.worker))
        a = IngressAuthority("research", signer, receiver,
                             key.public_key(), self.recipient, self.trust)
        source, edition, digest = a.source_key()
        self.trust.enroll(source_name=source, source_edition=edition,
                          pin_sha256=digest, confirm_pin_sha256=digest,
                          operator_ref="test-operator", verification_ref="test-witness")
        self.service.register_authenticated_ingress(role,
             AuthenticatedHandoffIngress(self.service.runtime, self.ledger, a))

    def preflight(self, **kw):
        args = dict(independently_retained_checkpoint=self.anchor,
                    trusted_checkpoint_public_key=self.checkpoint_signer.public_key())
        args.update(kw)
        return check_staged_local_security(self.service, **args)

    def test_no_keys_is_refused_and_read_only(self):
        decision = self.preflight()
        self.assertFalse(decision.ready_for_isolated_local_test)
        self.assertTrue(any("both operator-pinned" in x for x in decision.findings))
        self.assertEqual(tuple(self.service.runtime.event_store.all()), self.initial)

    def test_both_pins_anchor_encrypted_journal_allow_local_pilot(self):
        self.install("submit")
        self.install("result")
        decision = self.preflight()
        self.assertTrue(decision.ready_for_isolated_local_test)
        self.assertEqual(decision.scope, "local_staging_only")
        self.assertTrue(decision.findings[0].startswith("PASS"))
        self.assertEqual(tuple(self.service.runtime.event_store.all()), self.initial)
        with self.assertRaises(TypeError):
            bool(decision)

    def test_service_owned_presence_moves_without_work_or_http_calls(self):
        self.install("submit")
        self.install("result")
        self.assertIs(
            self.service._security_ingresses["submit"].key_approach,
            self.service._security_ingresses["result"].key_approach)
        boundary = self.service._security_ingresses["submit"].key_approach
        self.assertEqual(boundary.snapshot().presence_movements, 0)
        self.service.start_local_key_presence(interval_seconds=0.01)
        try:
            deadline = monotonic() + 2
            while monotonic() < deadline and boundary.snapshot().presence_movements < 5:
                sleep(0.01)
            observed = boundary.snapshot()
            self.assertGreaterEqual(observed.presence_movements, 5)
            self.assertEqual(observed.protected_movements, 0)
            self.assertEqual(observed.approach_movements, 0)
            self.assertEqual(tuple(self.service.runtime.event_store.all()), self.initial)
            with self.assertRaisesRegex(ValueError, "already configured"):
                self.service.start_local_key_presence()
        finally:
            self.service.stop_local_key_presence()
        stopped = boundary.snapshot()
        sleep(0.05)
        self.assertEqual(boundary.snapshot(), stopped)
        self.assertIsNone(self.service._native_security_presence)

    def test_service_presence_refuses_missing_roles_or_revoked_pins(self):
        with self.assertRaises(PermissionError):
            self.service.start_local_key_presence(interval_seconds=0.01)
        self.install("submit")
        with self.assertRaises(PermissionError):
            self.service.start_local_key_presence(interval_seconds=0.01)
        self.install("result")
        authority = self.service._security_ingresses["result"].authority
        source, edition, pin = authority.source_key()
        self.trust.revoke(
            source_name=source, source_edition=edition,
            pin_sha256=pin, confirm_pin_sha256=pin,
            operator_ref="test-operator", verification_ref="test-revoked-presence")
        with self.assertRaises(PermissionError):
            self.service.start_local_key_presence(interval_seconds=0.01)
        self.assertIsNone(self.service._native_security_presence)

    def test_plaintext_runtime_cannot_start_presence(self):
        plain = EcosystemService(data_dir=self.root / "plain-presence")
        with self.assertRaises(PermissionError):
            plain.start_local_key_presence(interval_seconds=0.01)

    def test_remote_host_refused_even_with_valid_pins(self):
        self.install("submit")
        self.install("result")
        decision = self.preflight(listener_host="0.0.0.0")
        self.assertFalse(decision.ready_for_isolated_local_test)
        self.assertTrue(any("loopback" in f for f in decision.findings))

    def test_missing_anchor_and_wrong_checkpoint_signer_are_refused(self):
        self.install("submit")
        self.install("result")
        for kw in (dict(independently_retained_checkpoint=None),
                   dict(trusted_checkpoint_public_key=Ed25519PrivateKey.generate().public_key())):
            with self.subTest(case=kw):
                self.assertFalse(self.preflight(**kw).ready_for_isolated_local_test)

    def test_revoked_pinned_worker_stops_pilot(self):
        self.install("submit")
        self.install("result")
        a = self.service._security_ingresses["result"].authority
        source, edition, digest = a.source_key()
        self.trust.revoke(source_name=source, source_edition=edition,
                          pin_sha256=digest, confirm_pin_sha256=digest,
                          operator_ref="test-operator", verification_ref="test-revocation")
        d = self.preflight()
        self.assertFalse(d.ready_for_isolated_local_test)
        self.assertTrue(any("result signing key" in f for f in d.findings))

    def test_unreciprocated_lanes_refused(self):
        self.install("submit")
        signer = self.worker
        mismatch = IngressAuthority("other-lane", "worker", "owner",
                    signer.public_key(), self.recipient, self.trust)
        source, edition, digest = mismatch.source_key()
        self.trust.enroll(source_name=source, source_edition=edition,
                          pin_sha256=digest, confirm_pin_sha256=digest,
                          operator_ref="test-operator", verification_ref="test-witness")
        self.service.register_authenticated_ingress("result",
                AuthenticatedHandoffIngress(self.service.runtime, self.ledger, mismatch))
        d = self.preflight()
        self.assertFalse(d.ready_for_isolated_local_test)
        self.assertTrue(any("reciprocal" in f for f in d.findings))

    def test_plaintext_service_fails_preflight(self):
        unsealed = EcosystemService(data_dir=self.root / "plain")
        d = check_staged_local_security(unsealed,
              independently_retained_checkpoint=self.anchor,
              trusted_checkpoint_public_key=self.checkpoint_signer.public_key())
        self.assertFalse(d.ready_for_isolated_local_test)
        self.assertTrue(any("not using the sealed journal" in f for f in d.findings))


if __name__ == "__main__":
    unittest.main()
