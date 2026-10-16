"""B13 offline native owner delivery with actual B3 subprocess source.

All signatures below come from one ephemeral *external* test signer. The B13
host process never sees its private key; source ownership beyond this test
fixture and operator-approved public pin is NOT established.
"""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import unittest

from systems.workspace.b11_native_local_delivery import PROTOCOL
from systems.workspace.b13_offline_owner_delivery import (
    B13OfflineOwnerDelivery, load_operator_pin, load_signed_envelope,
)
from systems.workspace.observed_event_journal import LOCAL_PASS, START
from systems.workspace.workstation_construction import WorkstationConstruction


class B13OfflineSourceTests(unittest.TestCase):
    def setUp(self):
        # Keep the B12 TestCase type out of this module's unittest discovery.
        from network.tests.test_b12_b3_native_delivery import B12NativeB3SourceTests
        self.native_fixture = B12NativeB3SourceTests(
            "test_end_to_end_native_B3_signed_delivery_crosses_only_candidate"
        )
        self.native_fixture.setUp()
        self.addCleanup(self.native_fixture.doCleanups)
        self.fx = self.native_fixture
        self.pin_file = self.fx.root / "owner-public.raw"
        self.pin_file.write_bytes(self.fx.public)
        self.pin_digest = sha256(self.fx.public).hexdigest()
        self.envelope_path = self.fx.root / "signed-envelope.json"
        self.cli_base = [
            sys.executable, "-m", "systems.workspace.b13_offline_owner_delivery",
            "--construction-dir", str(self.fx.graph.data_dir),
            "--native-data-dir", str(self.fx.native.data),
            "--observed-journal", str(self.fx.root / "observed.jsonl"),
            "--lane-id", self.fx.source.lane_id,
            "--opening-id", self.fx.source.opening_id,
            "--job-id", self.fx.source.job_id,
            "--confirm-source-job", self.fx.source.job_id,
            "--pinned-public-key", str(self.pin_file),
            "--expected-public-key-sha256", self.pin_digest,
        ]

    def execute_b3(self):
        return self.fx.complete_native()

    def host(self, *, digest=None):
        return B13OfflineOwnerDelivery(
            construction_dir=self.fx.graph.data_dir,
            native_data_dir=self.fx.native.data,
            observed_journal_path=self.fx.root / "observed.jsonl",
            lane_handoff_id=self.fx.source.lane_id,
            opening_id=self.fx.source.opening_id,
            job_id=self.fx.source.job_id,
            public_key=self.fx.public,
            expected_public_key_sha256=self.pin_digest if digest is None else digest,
            confirm_source_job=self.fx.source.job_id,
        )

    def request(self, host):
        return host.prepare(
            goal_id=self.fx.goal, candidate_id=self.fx.candidate,
            route=self.fx.route,
        )

    def sign(self, req):
        return self.fx.signer.sign(bytes.fromhex(req["canonical_bytes_hex"])).hex()

    def envelope(self, req):
        return {"protocol": PROTOCOL, "receipt": req["receipt"],
                "signature": self.sign(req)}

    def cli(self, *args, ok=True):
        completed = subprocess.run(
            [*self.cli_base, *args], capture_output=True, text=True,
            timeout=20, cwd=Path(__file__).resolve().parents[2],
        )
        if ok:
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            return json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        return completed.stderr

    def test_no_native_result_refuses_host_before_signing(self):
        with self.assertRaises(ValueError):
            self.host()

    def test_operator_pin_requires_out_of_band_digest(self):
        self.execute_b3()
        self.assertEqual(load_operator_pin(self.pin_file, expected_sha256=self.pin_digest),
                         self.fx.public)
        with self.assertRaisesRegex(ValueError, "does not match"):
            load_operator_pin(self.pin_file, expected_sha256="0" * 64)
        with self.assertRaises(ValueError):
            self.host(digest="0" * 64)

    def test_delivery_journal_cannot_be_original_b3_source_journal(self):
        self.execute_b3()
        original = self.fx.native.data / "runtime.jsonl"
        before = original.read_bytes()
        with self.assertRaisesRegex(ValueError, "separate from native B3"):
            B13OfflineOwnerDelivery(
                construction_dir=self.fx.graph.data_dir,
                native_data_dir=self.fx.native.data,
                observed_journal_path=original,
                lane_handoff_id=self.fx.source.lane_id,
                opening_id=self.fx.source.opening_id,
                job_id=self.fx.source.job_id,
                public_key=self.fx.public,
                expected_public_key_sha256=self.pin_digest,
                confirm_source_job=self.fx.source.job_id,
            )
        self.assertEqual(original.read_bytes(), before)

    def test_public_pin_cannot_be_supplied_as_symlink(self):
        self.execute_b3()
        symlink = self.fx.root / "symlink-key"
        symlink.symlink_to(self.pin_file)
        with self.assertRaisesRegex(ValueError, "pinned"):
            load_operator_pin(symlink, expected_sha256=self.pin_digest)

    def test_prepare_is_inert_and_is_idempotent_across_processes(self):
        self.execute_b3()
        before = (self.fx.native.data / "runtime.jsonl").read_bytes()
        one = self.cli(
            "prepare", "--goal-id", self.fx.goal,
            "--candidate-id", self.fx.candidate,
            "--route-node", self.fx.candidate, "--route-node", self.fx.goal,
        )
        two = self.cli(
            "prepare", "--goal-id", self.fx.goal,
            "--candidate-id", self.fx.candidate,
            "--route-node", self.fx.candidate, "--route-node", self.fx.goal,
        )
        self.assertEqual(one["request_id"], two["request_id"])
        self.assertFalse(one["local_pass_emitted"])
        self.assertFalse(one["private_key_loaded"])
        self.assertEqual(before, (self.fx.native.data / "runtime.jsonl").read_bytes())
        self.assertEqual(self.host().b12.bridge.projection(one["request_id"])["state"], "OPEN")

    def test_signing_request_emits_canonical_b11_bytes_without_private_key(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        output = self.cli("signing-request", "--request-id", identity)
        self.assertEqual(output["protocol"], PROTOCOL)
        self.assertTrue(output["signing_required_externally"])
        self.assertFalse(output["signature_provided"])
        raw = bytes.fromhex(output["canonical_bytes_hex"])
        self.assertEqual(sha256(raw).hexdigest(), output["canonical_sha256"])
        self.assertEqual(json.loads(raw)["receipt"], output["receipt"])
        self.assertEqual(host.b12.bridge.projection(identity)["state"], "OPEN")

    def test_cross_process_prepare_external_sign_deliver_native(self):
        self.execute_b3()
        prepared = self.cli(
            "prepare", "--goal-id", self.fx.goal,
            "--candidate-id", self.fx.candidate,
            "--route-node", self.fx.candidate, "--route-node", self.fx.goal,
        )
        req = prepared["request_id"]
        unsigned = self.cli("signing-request", "--request-id", req)
        self.envelope_path.write_text(json.dumps(self.envelope(unsigned)), encoding="utf8")
        original = (self.fx.native.data / "runtime.jsonl").read_bytes()
        delivered = self.cli(
            "deliver", "--request-id", req, "--confirm-request", req,
            "--approve-native-delivery", "--signed-envelope", str(self.envelope_path),
        )
        self.assertEqual(delivered["state"], "CROSSED")
        self.assertFalse(delivered["whole_route_verified"])
        self.assertFalse(delivered["native_b3_worker_executed_now"])
        self.assertEqual(original, (self.fx.native.data / "runtime.jsonl").read_bytes())
        events = self.host().b12.delivery.journal.for_handoff(req)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in events), 1)
        self.assertEqual(sum(e.event_type == START for e in events), 1)
        self.assertFalse(self.fx.graph.next_construction_handoffs(self.fx.goal)
                         ["whole_chain_verified"])

    def test_offline_delivery_requires_explicit_approval(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        with self.assertRaises(PermissionError):
            host.deliver(request_id=identity, confirm_request=identity,
                         approved=False, signed_envelope=signed)
        with self.assertRaises(PermissionError):
            host.deliver(request_id=identity, confirm_request="wrong",
                         approved=True, signed_envelope=signed)
        self.assertEqual(host.b12.bridge.projection(identity)["state"], "OPEN")

    def test_signature_cannot_be_forged_with_another_ephemeral_key(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        unsigned = host.signing_request(identity)
        wrong = self.envelope(unsigned)
        wrong["signature"] = Ed25519PrivateKey.generate().sign(
            bytes.fromhex(unsigned["canonical_bytes_hex"])
        ).hex()
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            host.deliver(request_id=identity, confirm_request=identity,
                         approved=True, signed_envelope=wrong)
        self.assertEqual(host.b12.bridge.projection(identity)["state"], "OPEN")

    def test_other_source_owner_key_does_not_override_pin(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        signed["public_key"] = self.fx.public.hex()
        with self.assertRaises(ValueError):
            host.deliver(request_id=identity, confirm_request=identity,
                         approved=True, signed_envelope=signed)

    def test_stale_native_edition_rejected_after_offline_signature(self):
        from systems.workspace.process_handoff import WORKER_ID
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        job = self.fx.native.runtime().get(self.fx.native.job_id)
        folder, _ = self.fx.native.desk._read(
            WORKER_ID, job.metadata["worker_version"],
        )
        f = folder / "finite_required_edge_guard.py"
        f.write_text(f.read_text(encoding="utf8") + "\n# externally modified\n",
                     encoding="utf8")
        with self.assertRaises(ValueError):
            host.deliver(request_id=identity, confirm_request=identity,
                         approved=True, signed_envelope=signed)
        self.assertEqual(host.b12.bridge.projection(identity)["state"], "OPEN")

    def test_signed_old_native_digest_not_accepted_for_changed_result(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        altered = {**signed, "receipt": {
            **signed["receipt"], "native_receipt_sha256": "0" * 64,
        }}
        with self.assertRaisesRegex(ValueError, "differs"):
            host.deliver(request_id=identity, confirm_request=identity,
                         approved=True, signed_envelope=altered)

    def test_stale_construction_route_fails_after_external_signature(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        self.fx.graph.candidate(
            self.fx.candidate, "new upstream unmet condition",
            provenance="proposal:new-upstream",
        )
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            host.deliver(request_id=identity, confirm_request=identity,
                         approved=True, signed_envelope=signed)
        self.assertEqual(host.b12.bridge.projection(identity)["state"], "OPEN")

    def test_duplicate_signed_delivery_across_instances_is_idempotent(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        first = host.deliver(
            request_id=identity, confirm_request=identity,
            approved=True, signed_envelope=signed,
        )
        second = self.host().deliver(
            request_id=identity, confirm_request=identity,
            approved=True, signed_envelope=signed,
        )
        self.assertEqual(first.event_id, second.event_id)
        events = self.host().b12.delivery.journal.for_handoff(identity)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in events), 1)
        self.assertEqual(sum(e.event_type == START for e in events), 1)

    def test_invalid_signed_response_schema_is_rejected_before_delivery(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        signed = self.envelope(host.signing_request(identity))
        signed["signature"] = "not-hex"
        self.envelope_path.write_text(json.dumps(signed), encoding="utf8")
        with self.assertRaisesRegex(ValueError, "exact B11 protocol"):
            load_signed_envelope(self.envelope_path)
        signed["signature"] = self.sign(host.signing_request(identity))
        signed["unrecognized"] = "not allowed"
        self.envelope_path.write_text(json.dumps(signed), encoding="utf8")
        with self.assertRaises(ValueError):
            load_signed_envelope(self.envelope_path)

    def test_invalid_response_file_is_rejected(self):
        self.execute_b3()
        self.envelope_path.write_text("{broken", encoding="utf8")
        with self.assertRaises(ValueError):
            load_signed_envelope(self.envelope_path)
        self.envelope_path.write_text("x" * 5000, encoding="utf8")
        with self.assertRaisesRegex(ValueError, "bounded"):
            load_signed_envelope(self.envelope_path)

    def test_no_external_signature_means_no_local_event(self):
        self.execute_b3()
        host = self.host()
        identity = self.request(host)
        request = host.signing_request(identity)
        self.assertNotIn("signature", request)
        self.assertEqual(host.b12.bridge.projection(identity)["state"], "OPEN")
        self.assertFalse(any(
            e.event_type == LOCAL_PASS
            for e in host.b12.delivery.journal.for_handoff(identity)
        ))


if __name__ == "__main__":
    unittest.main()
