"""Opt-in *witness-only* mutually authenticated TLS HTTP entrance.

No worker dispatch, runtime key, trust enrollment or general-purpose API.
The constructor never binds an external interface, and importing this
module never starts a listener. A separate operator must provide an mTLS
server SSLContext and out-of-band client certificate/source public-key pins.
"""
from __future__ import annotations

from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import ssl

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .remote_witness import RemoteWitnessLedger
from .observer_anchor import verify_observer_anchor
from .sealed_journal import SealedJournalError

MAX_REQUEST = 1_048_576
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _unique_json_fields(pairs):
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("duplicate witness JSON field")
        fields[key] = value
    return fields


def _reject_constant(_):
    raise ValueError("nonfinite witness JSON")


class WitnessOnlyHTTPServer(ThreadingHTTPServer):
    """Loopback-only mTLS test/staging endpoint; no deployment entrypoint."""

    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, address, *, tls_context: ssl.SSLContext,
                 observer: RemoteWitnessLedger, client_pins: dict,
                 independently_retained_anchors: dict):
        host, port = address
        if host not in ("127.0.0.1", "::1") or not isinstance(port, int):
            raise ValueError("witness listener must be loopback-only")
        if (not isinstance(tls_context, ssl.SSLContext)
                or tls_context.protocol != ssl.PROTOCOL_TLS_SERVER
                or tls_context.verify_mode != ssl.CERT_REQUIRED
                or tls_context.minimum_version != ssl.TLSVersion.TLSv1_3):
            raise ValueError("operator-provided TLS 1.3 mutual authentication required")
        if not isinstance(observer, RemoteWitnessLedger) or not client_pins:
            raise ValueError("trusted observer and client certificate pins required")
        if (type(independently_retained_anchors) is not dict
                or not independently_retained_anchors):
            raise ValueError("independently retained observer anchors required")
        normalized = {}
        for digest, item in client_pins.items():
            if (type(digest) is not str or not HEX.fullmatch(digest)
                    or type(item) is not tuple or len(item) != 2
                    or not isinstance(item[1], Ed25519PublicKey)):
                raise ValueError("client certificate must map to pinned source identity and key")
            observer._name(item[0])
            if item[0] not in independently_retained_anchors:
                raise ValueError("source requires separately retained observer anchor")
            anchor, observer_public = independently_retained_anchors[item[0]]
            verify_observer_anchor(
                observer, anchor, source_public_key=item[1],
                observer_public_key=observer_public)
            normalized[digest] = item
        self.observer = observer
        self.client_pins = normalized
        self.independent_anchors = dict(independently_retained_anchors)
        super().__init__((host, port), WitnessOnlyHandler, bind_and_activate=False)
        self.socket = tls_context.wrap_socket(self.socket, server_side=True,
                                              do_handshake_on_connect=False)
        self.server_bind()
        self.server_activate()


class WitnessOnlyHandler(BaseHTTPRequestHandler):
    server: WitnessOnlyHTTPServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Avoid logging research contents or even the authenticated source ID.
        return

    def _reply(self, status, message):
        data = json.dumps(message, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)
        self.close_connection = True

    def do_GET(self):
        self._reply(405, {"error": "witness endpoint does not support reads"})

    def do_POST(self):
        # The only accepted operation advances an observer-owned proof
        # ledger; never call the worker service or runtime from this handler.
        if self.path != "/v1/witness":
            self._reply(404, {"error": "unknown witness operation"})
            return
        try:
            peer = self.connection.getpeercert(binary_form=True)
            digest = sha256(peer or b"").hexdigest()
            authorized = self.server.client_pins.get(digest)
            if authorized is None:
                self._reply(403, {"error": "unrecognized witness transport identity"})
                return
            lengths = self.headers.get_all("Content-Length", [])
            content_types = self.headers.get_all("Content-Type", [])
            if (self.headers.get_all("Transfer-Encoding", [])
                    or len(lengths) != 1 or len(content_types) != 1
                    or content_types[0].split(";", 1)[0].strip().lower()
                    != "application/json"):
                self._reply(415, {"error": "bounded JSON required"})
                return
            length = int(lengths[0])
            if not 0 < length <= MAX_REQUEST:
                self._reply(413, {"error": "invalid witness frame size"})
                return
            document = json.loads(
                self.rfile.read(length).decode("utf-8"),
                object_pairs_hook=_unique_json_fields, parse_constant=_reject_constant)
            if (type(document) is not dict
                    or set(document) != {"source_id", "bundle"}
                    or document["source_id"] != authorized[0]):
                self._reply(403, {"error": "witness source not authorized by mTLS pin"})
                return
            anchor, observer_public_key = self.server.independent_anchors[authorized[0]]
            verify_observer_anchor(
                self.server.observer, anchor, source_public_key=authorized[1],
                observer_public_key=observer_public_key)
            checkpoint = self.server.observer.observe(
                authorized[0], document["bundle"],
                trusted_source_public_key=authorized[1])
            self._reply(200, {"source_id": authorized[0],
                              "observed_sequence": checkpoint["sequence"]})
        except (SealedJournalError, ValueError, UnicodeError, TypeError):
            self._reply(400, {"error": "witness refused"})
