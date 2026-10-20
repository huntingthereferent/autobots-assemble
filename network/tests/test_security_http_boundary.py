"""Native HTTP boundary tests: no accidental remote or unsigned worker admission."""
from __future__ import annotations

from dataclasses import replace
from email.message import Message
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from hashlib import sha256
from cryptography.hazmat.primitives import serialization
from systems.workspace.b14_operator_pin_ledger import OperatorPinLedger
from tempfile import TemporaryDirectory
import json
import threading
import unittest
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

import runtime.http_server as server_module
from runtime.handoff import Handoff, ExecutionResult, EvidenceRecord
from runtime.service import EcosystemService
from security.continuation import ReplayLedger, seal_record
from security.runtime_ingress import (AuthenticatedHandoffIngress, IngressAuthority,
                                      seal_handoff, seal_result)


def headers(**values):
    h = Message()
    for k, v in values.items():
        h[k.replace("_", "-")] = v
    return h


class HttpBoundaryTests(unittest.TestCase):
    def fake(self, *, ip="127.0.0.1", host="localhost:8040", origin=None,
             kind="application/json", size="20", fetch=None):
        h = headers(Host=host, Content_Type=kind, Content_Length=size)
        if origin is not None:
            h["Origin"] = origin
        if fetch is not None:
            h["Sec-Fetch-Site"] = fetch
        return SimpleNamespace(headers=h, client_address=(ip, 1),
                               server=SimpleNamespace(server_port=8040))

    def test_valid_loopback_json(self):
        self.assertTrue(server_module.trusted_http_request(self.fake(), write=True))

    def test_external_client_refused_even_with_local_host(self):
        self.assertFalse(server_module.trusted_http_request(
            self.fake(ip="203.0.113.10"), write=True))

    def test_remote_host_header_refused(self):
        for host in ("evil.example:8040", "127.0.0.1:4444",
                     "localhost.evil.example:8040", "localhost:8040@evil.example",
                     "localhost", "localhost:8040/x"):
            with self.subTest(host=host):
                self.assertFalse(server_module.trusted_http_request(self.fake(host=host)))

    def test_cross_origin_refused_even_on_loopback(self):
        for origin in ("https://evil.example", "null", "http://localhost:8000",
                       "http://127.0.0.1:8040", "https://localhost:8040"):
            with self.subTest(origin=origin):
                self.assertFalse(server_module.trusted_http_request(
                    self.fake(origin=origin), write=True))

    def test_same_origin_and_fetch_site(self):
        self.assertTrue(server_module.trusted_http_request(
            self.fake(origin="http://localhost:8040", fetch="same-origin"), write=True))
        self.assertFalse(server_module.trusted_http_request(
            self.fake(fetch="cross-site"), write=True))

    def test_non_json_and_unbounded_bodies_refused(self):
        for kind, size in (("text/plain", "20"), ("application/x-www-form-urlencoded", "20"),
                           ("application/json", "0"), ("application/json", "-1"),
                           ("application/json", "1500001"), ("application/json", "abc")):
            with self.subTest(kind=kind, size=size):
                self.assertFalse(server_module.trusted_http_request(
                    self.fake(kind=kind, size=size), write=True))

    def test_read_json_requires_bounded_object(self):
        bad = SimpleNamespace(headers=headers(Content_Length="2"), rfile=BytesIO(b"[]"))
        with self.assertRaises(ValueError):
            server_module.read_json(bad)

    def test_remote_bind_configuration_is_rejected(self):
        # Startup guard exists in the module; external exposure must be
        # rejected before launching ThreadingHTTPServer.
        from inspect import getsource
        source = getsource(server_module)
        self.assertIn('if HOST not in {"127.0.0.1", "::1", "localhost"}:', source)
        self.assertIn("Ecosystem HTTP entrance is loopback-only", source)


class SignedHttpIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.service = EcosystemService(data_dir=Path(self.tmp.name) / "runtime")
        self.owner_key = Ed25519PrivateKey.generate()
        self.worker_key = Ed25519PrivateKey.generate()
        self.recipient = X25519PrivateKey.generate()
        self.ledger = ReplayLedger(Path(self.tmp.name) / "replay.sqlite")
        self.trust = OperatorPinLedger(Path(self.tmp.name) / "operator-trust.jsonl")
        self.original_service = server_module.SERVICE
        server_module.SERVICE = self.service
        self.addCleanup(setattr, server_module, "SERVICE", self.original_service)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
        self.addCleanup(self.httpd.server_close)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.httpd.shutdown()
        self.thread.join(timeout=3)

    def task(self, key="task-1"):
        return Handoff(handoff_id=key, referent="bounded-native-observation",
                       from_actor="owner", to_actor="worker",
                       required_relation="measure",
                       required_witnesses=("native",),
                       admissible_evidence={"native": ("measured",)})

    def ingress(self, role):
        if role == "submit":
            actor, peer, signer = "owner", "worker", self.owner_key
        else:
            actor, peer, signer = "worker", "owner", self.worker_key
        pub = signer.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        digest = sha256(pub).hexdigest()
        source = f"ab-ingress:native:{actor}:{peer}"
        if self.trust.current(source, "ab-security-ingress-v1") is None:
            self.trust.enroll(source_name=source, source_edition="ab-security-ingress-v1",
                              pin_sha256=digest, confirm_pin_sha256=digest,
                              operator_ref="fixture-operator",
                              verification_ref="fixture-out-of-band-check")
        entry = AuthenticatedHandoffIngress(self.service.runtime, self.ledger,
                    IngressAuthority("native", actor, peer,
                                     signer.public_key(), self.recipient, self.trust))
        self.service.register_authenticated_ingress(role, entry)

    def request(self, path, payload, extra=None):
        conn = HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            raw = json.dumps(payload).encode("utf8")
            conn.request("POST", path, body=raw,
                         headers={"Content-Type": "application/json", **(extra or {})})
            r = conn.getresponse()
            return r.status, json.loads(r.read().decode("utf8"))
        finally:
            conn.close()

    def seal(self, h=None, parent=None):
        return seal_handoff(h or self.task(), lane="native", parent_sha256=parent,
                            sender_private_key=self.owner_key,
                            recipient_public_key=self.recipient.public_key())

    def test_disabled_signed_route_is_rejected(self):
        status, doc = self.request("/api/security/handoffs", {"envelope": self.seal()})
        self.assertEqual(status, 403)
        self.assertEqual(self.service.runtime.snapshot(), {})

    def test_signed_handoff_and_worker_result_round_trip(self):
        self.ingress("submit")
        self.ingress("result")
        payload = {"envelope": self.seal()}
        status, doc = self.request("/api/security/handoffs", payload)
        self.assertEqual(status, 201)
        self.assertEqual(doc["status"], "READY")
        self.assertEqual(self.service.runtime.get("task-1"), self.task())
        status, _ = self.request("/api/security/handoffs", payload)
        self.assertEqual(status, 400)

        prior = self.service.runtime.state("task-1").last_event_id
        result = ExecutionResult(status="COMPLETE", output={"measured": True},
                    evidence=(EvidenceRecord(condition="native", kind="measured",
                                             source="native-observer"),))
        sealed = seal_result("task-1", prior, result, event_id="result-1", lane="native",
                             parent_sha256=None, sender_private_key=self.worker_key,
                             recipient_public_key=self.recipient.public_key())
        status, doc = self.request("/api/security/handoffs/task-1/result",
                                    {"envelope": sealed})
        self.assertEqual(status, 200)
        self.assertEqual(doc["status"], "COMPLETE")
        self.assertEqual(doc["output"], {"measured": True})
        self.assertEqual(len(self.service.runtime.event_store.for_handoff("task-1")), 2)

    def test_attacker_chosen_parent_digest_is_not_trusted(self):
        self.ingress("submit")
        envelope = self.seal(parent="1" * 64)
        status, _ = self.request("/api/security/handoffs",
                                  {"envelope": envelope, "expected_parent_sha256": "1" * 64})
        self.assertEqual(status, 400)
        status, _ = self.request("/api/security/handoffs", {"envelope": envelope})
        self.assertEqual(status, 400)
        self.assertEqual(self.service.runtime.snapshot(), {})

    def test_same_origin_rejection_occurs_before_signed_verification(self):
        self.ingress("submit")
        status, _ = self.request("/api/security/handoffs", {"envelope": self.seal()},
                                  {"Origin": "https://unrelated.example"})
        self.assertEqual(status, 403)
        self.assertEqual(self.service.runtime.snapshot(), {})
        status, _ = self.request("/api/security/handoffs", {"envelope": self.seal()})
        self.assertEqual(status, 201)

    def test_unsigned_actor_claim_cannot_enter_signed_route(self):
        self.ingress("submit")
        status, _ = self.request("/api/security/handoffs",
                                  {"actor_id": "owner", "handoff": {}})
        self.assertEqual(status, 400)
        self.assertEqual(self.service.runtime.snapshot(), {})

    def test_operator_cannot_register_same_role_twice(self):
        self.ingress("submit")
        with self.assertRaises(ValueError):
            self.ingress("submit")

    def test_revocation_blocks_existing_registered_ingress(self):
        self.ingress("submit")
        source = "ab-ingress:native:owner:worker"
        old = self.trust.current(source, "ab-security-ingress-v1")
        self.trust.revoke(source_name=source, source_edition="ab-security-ingress-v1",
                          pin_sha256=old, confirm_pin_sha256=old,
                          operator_ref="fixture-operator",
                          verification_ref="fixture-revoke-evidence")
        status, _ = self.request("/api/security/handoffs", {"envelope": self.seal()})
        self.assertEqual(status, 403)
        self.assertEqual(self.service.runtime.snapshot(), {})

    def test_operator_pin_is_mandatory_not_self_enrollment(self):
        other = AuthenticatedHandoffIngress(self.service.runtime, self.ledger,
                    IngressAuthority("native", "owner", "worker",
                                     self.owner_key.public_key(), self.recipient))
        with self.assertRaisesRegex(PermissionError, "operator key policy"):
            self.service.register_authenticated_ingress("submit", other)
        self.assertEqual(self.service.runtime.snapshot(), {})

    def test_revocation_blocks_signed_result_after_preparation(self):
        self.ingress("submit")
        self.ingress("result")
        status, _ = self.request("/api/security/handoffs", {"envelope": self.seal()})
        self.assertEqual(status, 201)
        source = "ab-ingress:native:worker:owner"
        old = self.trust.current(source, "ab-security-ingress-v1")
        result = ExecutionResult(status="UNKNOWN", output={}, evidence=())
        ticket = seal_result("task-1", self.service.runtime.state("task-1").last_event_id,
                             result, event_id="result-revoked", lane="native",
                             parent_sha256=None, sender_private_key=self.worker_key,
                             recipient_public_key=self.recipient.public_key())
        self.trust.revoke(source_name=source, source_edition="ab-security-ingress-v1",
                          pin_sha256=old, confirm_pin_sha256=old,
                          operator_ref="fixture-operator",
                          verification_ref="fixture-result-revoked")
        status, _ = self.request("/api/security/handoffs/task-1/result", {"envelope": ticket})
        self.assertEqual(status, 403)
        self.assertEqual(self.service.runtime.state("task-1").status, "READY")


if __name__ == "__main__":
    unittest.main()
