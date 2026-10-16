"""B15: the older B13 API and CLI must obey B14 operator trust.

Ephemeral test key and native B3 execution are controlled CI fixtures, not
a real-world authenticated source owner or unattended deployment.
"""
from pathlib import Path
import json
import subprocess
import sys
import unittest

from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.b11_native_local_delivery import ACTOR, PROTOCOL
from systems.workspace.b13_offline_owner_delivery import B13OfflineOwnerDelivery
from systems.workspace.b14_operator_pin_ledger import OperatorPinLedger
from systems.workspace.observed_event_journal import LOCAL_PASS, START, ObservedEventJournal


class B15MandatoryTrustTests(unittest.TestCase):
    def setUp(self):
        from network.tests.test_b13_offline_owner_delivery import B13OfflineSourceTests
        self.fixture = B13OfflineSourceTests(
            "test_cross_process_prepare_external_sign_deliver_native"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fx = self.fixture.fx

    def complete(self):
        self.fixture.execute_b3()

    def prepared(self):
        host = self.fixture.host()
        request = self.fixture.request(host)
        sign_req = host.signing_request(request)
        signed = self.fixture.envelope(sign_req)
        return host, request, signed

    def revoke(self):
        self.fixture.trust.revoke(
            source_name="finite-source-native",
            source_edition=self.fx.edition,
            pin_sha256=self.fixture.pin_digest,
            operator_ref="ephemeral-test-operator",
            verification_ref="B15-negative-revocation",
            confirm_pin_sha256=self.fixture.pin_digest,
        )

    def test_legacy_class_refuses_missing_trust_ledger(self):
        self.complete()
        with self.assertRaises(TypeError):
            B13OfflineOwnerDelivery(
                construction_dir=self.fx.graph.data_dir,
                native_data_dir=self.fx.native.data,
                observed_journal_path=self.fx.root / "observed.jsonl",
                lane_handoff_id=self.fx.source.lane_id,
                opening_id=self.fx.source.opening_id,
                job_id=self.fx.source.job_id,
                public_key=self.fx.public,
                expected_public_key_sha256=self.fixture.pin_digest,
                confirm_source_job=self.fx.source.job_id,
            )

    def test_legacy_class_rejects_absent_enrollment_even_with_valid_key(self):
        self.complete()
        self.fixture.trust_path.unlink()
        with self.assertRaises(PermissionError):
            self.fixture.host()

    def test_b13_cli_requires_trust_ledger_argument(self):
        self.complete()
        base = self.fixture.cli_base
        idx = base.index("--trust-ledger")
        old = base[:idx] + base[idx + 2:]
        cp = subprocess.run(
            [*old, "inspect"], capture_output=True, text=True,
            cwd=Path(__file__).resolve().parents[2], timeout=20,
        )
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("--trust-ledger", cp.stderr)

    def test_b13_cli_rejects_unenrolled_key(self):
        self.complete()
        self.fixture.trust_path.unlink()
        self.fixture.cli("inspect", ok=False)
        self.assertFalse(self.fixture.trust_path.exists())

    def test_b13_cli_rejects_revoked_key_after_restart(self):
        self.complete()
        self.revoke()
        err = self.fixture.cli("inspect", ok=False)
        self.assertIn("revoked", err)

    def test_b13_cli_rejects_rotated_key(self):
        from hashlib import sha256
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        self.complete()
        k = Ed25519PrivateKey.generate()
        new_key = k.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw,
        )
        new = sha256(new_key).hexdigest()
        self.fixture.trust.rotate(
            source_name="finite-source-native", source_edition=self.fx.edition,
            prior_sha256=self.fixture.pin_digest, new_pin_sha256=new,
            operator_ref="ephemeral-test-operator",
            verification_ref="B15-rotation",
            confirm_prior_sha256=self.fixture.pin_digest,
            confirm_new_sha256=new,
        )
        self.fixture.cli("inspect", ok=False)
        with self.assertRaises(PermissionError):
            self.fixture.host()

    def test_b13_class_does_not_accept_explicit_none_ledger(self):
        self.complete()
        with self.assertRaises(PermissionError):
            B13OfflineOwnerDelivery(
                construction_dir=self.fx.graph.data_dir,
                native_data_dir=self.fx.native.data,
                observed_journal_path=self.fx.root / "observed.jsonl",
                lane_handoff_id=self.fx.source.lane_id,
                opening_id=self.fx.source.opening_id,
                job_id=self.fx.source.job_id,
                public_key=self.fx.public,
                expected_public_key_sha256=self.fixture.pin_digest,
                confirm_source_job=self.fx.source.job_id,
                operator_trust_ledger_path=None,
            )

    def test_legacy_class_prepares_inert_after_valid_operator_enrollment(self):
        self.complete()
        host, request, signed = self.prepared()
        self.assertEqual(host.b12.bridge.projection(request)["state"], "OPEN")
        self.assertFalse(any(
            event.event_type == LOCAL_PASS
            for event in host.b12.delivery.journal.for_handoff(request)
        ))

    def test_revocation_blocks_existing_b13_host_prepare(self):
        self.complete()
        host = self.fixture.host()
        self.revoke()
        with self.assertRaises(PermissionError):
            self.fixture.request(host)

    def test_revocation_blocks_existing_b13_host_signing_request(self):
        self.complete()
        host, request, signed = self.prepared()
        self.revoke()
        with self.assertRaises(PermissionError):
            host.signing_request(request)

    def test_revocation_blocks_existing_b13_host_signed_delivery(self):
        self.complete()
        host, request, signed = self.prepared()
        self.revoke()
        with self.assertRaises(PermissionError):
            host.deliver(request_id=request, confirm_request=request,
                         approved=True, signed_envelope=signed)
        self.assertFalse(any(x.event_type == START for x in
                             host.b12.delivery.journal.for_handoff(request)))

    def test_revocation_blocks_saved_signed_pass_during_recovery(self):
        self.complete()
        host, request, signed = self.prepared()
        journal = host.b12.delivery.journal
        event = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR,
            data=signed,
        )
        RuntimeJournal.append(journal, event)
        self.revoke()
        reopened = ObservedEventJournal(
            journal.path, adapters=journal.adapters,
            verify_local_pass=journal.verify_local_pass,
        )
        self.assertEqual(reopened.projection(request)["state"], "OPEN")
        self.assertFalse(any(x.event_type == START for x in reopened.for_handoff(request)))

    def test_policy_journal_symlink_does_not_bypass_current_policy(self):
        self.complete()
        alias = self.fx.root / "operator-policy-alias.jsonl"
        alias.symlink_to(self.fixture.trust_path)
        with self.assertRaisesRegex(ValueError, "must not be a symlink"):
            B13OfflineOwnerDelivery(
                construction_dir=self.fx.graph.data_dir,
                native_data_dir=self.fx.native.data,
                observed_journal_path=self.fx.root / "observed.jsonl",
                lane_handoff_id=self.fx.source.lane_id,
                opening_id=self.fx.source.opening_id,
                job_id=self.fx.source.job_id,
                public_key=self.fx.public,
                expected_public_key_sha256=self.fixture.pin_digest,
                confirm_source_job=self.fx.source.job_id,
                operator_trust_ledger_path=alias,
            )

    def test_separate_operator_and_delivery_journals_remain_required(self):
        self.complete()
        self.fixture.trust_path.unlink()
        self.fixture.trust_path.symlink_to(self.fx.native.data / "runtime.jsonl")
        with self.assertRaises(ValueError):
            self.fixture.host()

    def test_valid_b13_cli_uses_existing_b3_return_with_enrolled_pin(self):
        self.complete()
        prepared = self.fixture.cli(
            "prepare", "--goal-id", self.fx.goal, "--candidate-id", self.fx.candidate,
            "--route-node", self.fx.candidate, "--route-node", self.fx.goal,
        )
        req = prepared["request_id"]
        unsigned = self.fixture.cli("signing-request", "--request-id", req)
        signed = self.fixture.envelope(unsigned)
        self.fixture.envelope_path.write_text(json.dumps(signed), encoding="utf8")
        done = self.fixture.cli(
            "deliver", "--request-id", req, "--confirm-request", req,
            "--approve-native-delivery", "--signed-envelope",
            str(self.fixture.envelope_path),
        )
        self.assertEqual(done["state"], "CROSSED")
        self.assertFalse(done["whole_route_verified"])
        self.assertFalse(done["native_b3_worker_executed_now"])


if __name__ == "__main__":
    unittest.main()
