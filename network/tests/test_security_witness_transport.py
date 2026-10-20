"""Ephemeral local TLS 1.3 witness-only transport, pinned on BOTH ends.

Certificates and keys are generated inside each temporary test directory;
nothing is deployed, enrolled remotely, or checked in.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from http.client import HTTPSConnection
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import ssl
import threading
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from security.journal_checkpoint import issue_checkpoint
from security.observer_anchor import issue_observer_anchor
from security.remote_witness import RemoteWitnessLedger, export_witness_span
from security.witness_transport import WitnessOnlyHTTPServer


class MutuallyAuthenticatedWitnessTransportTests(unittest.TestCase):
    def _cert(self, common_name, *, issuer_cert=None, issuer_key=None, key=None,
              ca=False, usage=None):
        key = key or rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
        now = datetime.now(timezone.utc)
        issuer = issuer_cert.subject if issuer_cert is not None else name
        signing_key = issuer_key or key
        builder = (x509.CertificateBuilder()
                   .subject_name(name).issuer_name(issuer)
                   .public_key(key.public_key())
                   .serial_number(x509.random_serial_number())
                   .not_valid_before(now-timedelta(minutes=1))
                   .not_valid_after(now+timedelta(days=1))
                   .add_extension(x509.BasicConstraints(ca=ca, path_length=None),
                                  critical=True))
        if usage is not None:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([usage]), critical=False)
        if common_name == "127.0.0.1":
            import ipaddress
            builder = builder.add_extension(
                x509.SubjectAlternativeName([x509.IPAddress(
                    ipaddress.ip_address("127.0.0.1"))]), critical=False)
        return key, builder.sign(signing_key, hashes.SHA256())

    def _pem(self, label, key, cert):
        path = self.root / (label + ".pem")
        path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        secret = self.root / (label + ".key")
        secret.write_bytes(key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()))
        return path, secret

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ca_key, ca = self._cert("Test witness CA", ca=True)
        self.ca_path, _ = self._pem("ca", self.ca_key, ca)
        server_key, server_cert = self._cert("127.0.0.1", issuer_cert=ca,
            issuer_key=self.ca_key, usage=ExtendedKeyUsageOID.SERVER_AUTH)
        client_key, client_cert = self._cert("observer-source-A", issuer_cert=ca,
            issuer_key=self.ca_key, usage=ExtendedKeyUsageOID.CLIENT_AUTH)
        wrong_key, wrong_cert = self._cert("unregistered-source-B", issuer_cert=ca,
            issuer_key=self.ca_key, usage=ExtendedKeyUsageOID.CLIENT_AUTH)
        self.server_cert, self.server_key = self._pem("server", server_key, server_cert)
        self.client_cert, self.client_key = self._pem("source-a", client_key, client_cert)
        self.wrong_cert, self.wrong_key = self._pem("other", wrong_key, wrong_cert)
        self.client_pin = sha256(
            client_cert.public_bytes(serialization.Encoding.DER)).hexdigest()
        self.source_key = ed25519.Ed25519PrivateKey.generate()
        self.observer_key = ed25519.Ed25519PrivateKey.generate()
        self.native = HandoffRuntime(event_store=__import__(
            "security.sealed_journal", fromlist=["SealedRuntimeJournal"]
        ).SealedRuntimeJournal(self.root / "source.db", key=os.urandom(32)))
        self.initial_checkpoint = issue_checkpoint(
            self.native.event_store, self.source_key)
        self.observer = RemoteWitnessLedger(self.root / "observer.db")
        self.observer.enroll(
            "alpha", signed_base_checkpoint=self.initial_checkpoint,
            trusted_source_public_key=self.source_key.public_key())
        self.anchor = issue_observer_anchor(
            self.observer, "alpha", source_public_key=self.source_key.public_key(),
            observer_private_key=self.observer_key)
        self.server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.server_context.minimum_version = ssl.TLSVersion.TLSv1_3
        self.server_context.verify_mode = ssl.CERT_REQUIRED
        self.server_context.load_cert_chain(
            str(self.server_cert), str(self.server_key))
        self.server_context.load_verify_locations(cafile=str(self.ca_path))
        self.client_context = self._client_context(self.client_cert, self.client_key)
        self.wrong_context = self._client_context(self.wrong_cert, self.wrong_key)
        self.no_cert_context = self._client_context(None, None)
        self.server = WitnessOnlyHTTPServer(
            ("127.0.0.1", 0), tls_context=self.server_context,
            observer=self.observer,
            client_pins={self.client_pin: ("alpha", self.source_key.public_key())},
            independently_retained_anchors={
                "alpha": (self.anchor, self.observer_key.public_key())})
        self.addCleanup(self.server.server_close)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self._stop)

    def _client_context(self, cert, key):
        context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile=str(self.ca_path))
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        if cert is not None:
            context.load_cert_chain(str(cert), str(key))
        return context

    def _stop(self):
        self.server.shutdown()
        self.thread.join(timeout=4)

    def next_bundle(self, identifier, base=None):
        previous = base or self.observer.current(
            "alpha", trusted_source_public_key=self.source_key.public_key())
        self.native.submit(Handoff(
            handoff_id=identifier, referent="private-source-"+identifier,
            from_actor="owner", to_actor="worker",
            required_relation="observe", inputs={"secret": "fixture-only"}))
        tip = issue_checkpoint(self.native.event_store, self.source_key)
        return export_witness_span(
            self.native.event_store, base_checkpoint=previous,
            tip_checkpoint=tip, source_public_key=self.source_key.public_key())

    def request(self, body, *, context=None, method="POST", path="/v1/witness",
                content_type="application/json"):
        conn = HTTPSConnection(
            "127.0.0.1", self.server.server_port, timeout=5,
            context=context or self.client_context)
        try:
            raw = json.dumps(body).encode("utf-8")
            conn.request(method, path, body=raw,
                         headers={"Content-Type": content_type})
            response = conn.getresponse()
            return response.status, json.loads(response.read().decode("utf-8"))
        finally:
            conn.close()

    def test_mutual_tls_pinned_source_and_observer_anchor_accept_continuation(self):
        first = self.next_bundle("one")
        status, receipt = self.request({"source_id": "alpha", "bundle": first})
        self.assertEqual((status, receipt),
                         (200, {"source_id": "alpha", "observed_sequence": 1}))
        self.assertEqual(self.request({"source_id": "alpha", "bundle": first})[0], 400)
        second = self.next_bundle("two")
        self.assertEqual(self.request({"source_id": "alpha", "bundle": second})[0], 200)
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.source_key.public_key())["sequence"], 2)
        self.assertEqual(len(self.native.event_store.all()), 2)

    def test_unpinned_certificate_and_self_claimed_source_refused(self):
        bundle = self.next_bundle("first")
        self.assertEqual(self.request(
            {"source_id": "alpha", "bundle": bundle},
            context=self.wrong_context)[0], 403)
        self.assertEqual(self.request(
            {"source_id": "imagined", "bundle": bundle})[0], 403)
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.source_key.public_key())["sequence"], 0)

    def test_no_client_certificate_cannot_complete_tls_request(self):
        bundle = self.next_bundle("first")
        with self.assertRaises((ssl.SSLError, OSError)):
            self.request({"source_id": "alpha", "bundle": bundle},
                         context=self.no_cert_context)

    def test_endpoint_never_accepts_worker_commands_or_reads(self):
        self.assertEqual(self.request({}, method="GET")[0], 405)
        self.assertEqual(self.request({"actor_id": "owner"},
                                      path="/api/handoffs")[0], 404)
        self.assertEqual(self.request({"source_id": "alpha"},
                                      path="/v1/witness", content_type="text/plain")[0], 415)
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.source_key.public_key())["sequence"], 0)

    def test_receiver_rechecks_independent_anchor_before_each_admission(self):
        bundle = self.next_bundle("first")
        # Operator-retained anchor is not a writable field in SQLite.
        forged = {**self.anchor, "movement_count": 13}
        self.server.independent_anchors["alpha"] = (
            forged, self.observer_key.public_key())
        self.assertEqual(self.request({"source_id": "alpha", "bundle": bundle})[0], 400)
        self.assertEqual(self.observer.current(
            "alpha", trusted_source_public_key=self.source_key.public_key())["sequence"], 0)


if __name__ == "__main__":
    unittest.main()
