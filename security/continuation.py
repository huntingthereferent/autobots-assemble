"""Authenticated, encrypted, scope-bound evidence envelopes.

Uses established cryptography primitives. The envelope authenticates bytes and
an enrolled public key; it does not establish that the observation is true.
Private keys and trust enrollment are owned by the calling application.
"""
from __future__ import annotations

import base64
import binascii
import hmac
import json
import os
from hashlib import sha256
from contextlib import closing
from pathlib import Path
import re
import sqlite3

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

VERSION = "ab-evidence-envelope/v1"
DOMAIN = b"ab-evidence-envelope/v1:encryption"
MAX_PLAINTEXT = 1_048_576
MAX_ENVELOPE = 1_500_000
TOKEN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,127}\Z")
DIGEST = re.compile(r"[a-f0-9]{64}\Z")
FIELDS = frozenset({"version", "lane", "event_id", "parent_sha256",
                    "sender_key_sha256", "recipient_key_sha256", "ephemeral_public",
                    "salt", "nonce", "ciphertext", "signature"})


class EnvelopeError(ValueError):
    """Invalid envelope, wrong scope, failed authentication or refused replay."""


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _raw_public(key: Ed25519PublicKey | X25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _decode(value: str, expected_size: int | None = None) -> bytes:
    if not isinstance(value, str) or len(value) > MAX_ENVELOPE:
        raise EnvelopeError("invalid encoded field")
    try:
        result = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise EnvelopeError("invalid base64 field") from exc
    if expected_size is not None and len(result) != expected_size:
        raise EnvelopeError("invalid field size")
    return result


def _name(value: str) -> str:
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        raise EnvelopeError("lane or event id must be a bounded identifier")
    return value


def _parent(value: str | None) -> str | None:
    if value is not None and (not isinstance(value, str) or not DIGEST.fullmatch(value)):
        raise EnvelopeError("parent digest must be SHA-256 hex or null")
    return value


def _key(secret: bytes, salt: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32,
                salt=salt, info=DOMAIN).derive(secret)


def seal_record(
    plaintext: bytes, *, lane: str, event_id: str, parent_sha256: str | None,
    sender_private_key: Ed25519PrivateKey, recipient_public_key: X25519PublicKey,
) -> dict:
    """Seal one bounded record to a recipient and sign all envelope fields."""
    if type(plaintext) is not bytes or not 0 < len(plaintext) <= MAX_PLAINTEXT:
        raise EnvelopeError("plaintext must be nonempty bounded bytes")
    _name(lane)
    _name(event_id)
    _parent(parent_sha256)
    if not isinstance(sender_private_key, Ed25519PrivateKey) or not isinstance(
        recipient_public_key, X25519PublicKey
    ):
        raise TypeError("actual Ed25519 signing and X25519 recipient keys required")
    ephemeral = X25519PrivateKey.generate()
    salt, nonce = os.urandom(16), os.urandom(12)
    body = {
        "version": VERSION,
        "lane": lane,
        "event_id": event_id,
        "parent_sha256": parent_sha256,
        "sender_key_sha256": sha256(_raw_public(sender_private_key.public_key())).hexdigest(),
        "recipient_key_sha256": sha256(_raw_public(recipient_public_key)).hexdigest(),
        "ephemeral_public": _b64(_raw_public(ephemeral.public_key())),
        "salt": _b64(salt),
        "nonce": _b64(nonce),
    }
    # Authenticate the scope, ancestry and identities as AEAD associated data.
    ciphertext = AESGCM(_key(ephemeral.exchange(recipient_public_key), salt)).encrypt(
        nonce, plaintext, _canonical(body)
    )
    body["ciphertext"] = _b64(ciphertext)
    body["signature"] = _b64(sender_private_key.sign(_canonical(body)))
    return body


def envelope_digest(envelope: dict) -> str:
    """Content identity for a stored signed envelope (not a trust decision)."""
    _structure(envelope)
    return sha256(_canonical(envelope)).hexdigest()


def _structure(envelope: dict) -> None:
    if type(envelope) is not dict or set(envelope) != FIELDS:
        raise EnvelopeError("unexpected envelope shape")
    try:
        size = len(_canonical(envelope))
    except (TypeError, ValueError) as exc:
        raise EnvelopeError("invalid envelope serialization") from exc
    if size > MAX_ENVELOPE or envelope["version"] != VERSION:
        raise EnvelopeError("unsupported or oversized envelope")
    _name(envelope["lane"])
    _name(envelope["event_id"])
    _parent(envelope["parent_sha256"])
    for digest in ("sender_key_sha256", "recipient_key_sha256"):
        v = envelope[digest]
        if not isinstance(v, str) or not DIGEST.fullmatch(v):
            raise EnvelopeError("invalid key fingerprint")
    for field, n in (("ephemeral_public", 32), ("salt", 16), ("nonce", 12),
                     ("signature", 64)):
        _decode(envelope[field], n)
    raw = _decode(envelope["ciphertext"])
    if not 17 <= len(raw) <= MAX_PLAINTEXT + 16:
        raise EnvelopeError("invalid ciphertext length")


class ReplayLedger:
    """Local persistent, atomic first-admission ledger; not a remote trust root.

    Use a private, access-controlled path. A hostile host may replace or roll
    back the database, and distributed callers require a shared admission store.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if self.path.is_symlink():
            raise EnvelopeError("replay ledger cannot be a symlink")
        if not self.path.parent.is_dir():
            raise EnvelopeError("replay ledger directory must already exist")
        if not self.path.exists():
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        with closing(self._connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS admitted (lane TEXT NOT NULL, "
                       "event_id TEXT NOT NULL, digest TEXT NOT NULL, "
                       "PRIMARY KEY (lane, event_id))")

    def _connect(self) -> sqlite3.Connection:
        if self.path.is_symlink():
            raise EnvelopeError("replay ledger cannot be a symlink")
        return sqlite3.connect(self.path, timeout=10)

    def admit(self, lane: str, event_id: str, digest: str) -> None:
        _name(lane)
        _name(event_id)
        if not DIGEST.fullmatch(digest):
            raise EnvelopeError("invalid replay digest")
        try:
            with closing(self._connect()) as db, db:
                db.execute("INSERT INTO admitted VALUES (?, ?, ?)",
                           (lane, event_id, digest))
        except sqlite3.IntegrityError as exc:
            raise EnvelopeError("replayed or reused event identifier") from exc


def verify_record(
    envelope: dict, *, expected_lane: str, expected_parent_sha256: str | None,
    sender_public_key: Ed25519PublicKey, recipient_private_key: X25519PrivateKey,
) -> bytes:
    """Verify/decrypt WITHOUT admission; caller MUST commit replay with movement.

    Only the sealed native SQLite journal can make those two writes atomic.
    This function is not a usable admission API by itself.
    """
    _structure(envelope)
    _name(expected_lane)
    _parent(expected_parent_sha256)
    if not isinstance(sender_public_key, Ed25519PublicKey) or not isinstance(
        recipient_private_key, X25519PrivateKey
    ):
        raise TypeError("pinned sender and private recipient keys required")
    if envelope["lane"] != expected_lane or envelope["parent_sha256"] != expected_parent_sha256:
        raise EnvelopeError("wrong lane or parent relationship")
    if not hmac.compare_digest(envelope["sender_key_sha256"],
                               sha256(_raw_public(sender_public_key)).hexdigest()):
        raise EnvelopeError("sender key not pinned")
    if not hmac.compare_digest(envelope["recipient_key_sha256"],
                               sha256(_raw_public(recipient_private_key.public_key())).hexdigest()):
        raise EnvelopeError("wrong recipient")
    signed = {k: v for k, v in envelope.items() if k != "signature"}
    try:
        sender_public_key.verify(_decode(envelope["signature"], 64), _canonical(signed))
    except Exception as exc:
        raise EnvelopeError("signature verification failed") from exc
    aad = {k: v for k, v in signed.items() if k != "ciphertext"}
    try:
        peer = X25519PublicKey.from_public_bytes(_decode(envelope["ephemeral_public"], 32))
        plain = AESGCM(_key(recipient_private_key.exchange(peer),
                            _decode(envelope["salt"], 16))).decrypt(
            _decode(envelope["nonce"], 12), _decode(envelope["ciphertext"]),
            _canonical(aad)
        )
    except Exception as exc:
        raise EnvelopeError("ciphertext authentication failed") from exc
    return plain


def open_record(
    envelope: dict, *, expected_lane: str, expected_parent_sha256: str | None,
    sender_public_key: Ed25519PublicKey, recipient_private_key: X25519PrivateKey,
    replay_ledger: ReplayLedger,
) -> bytes:
    """Legacy separate-ledger API: verify then persist replay admission.

    Sealed native runtime ingress instead uses verify_record() followed by a
    single SQLite transaction joining replay admission to the journal event.
    """
    if not isinstance(replay_ledger, ReplayLedger):
        raise TypeError("replay ledger required")
    plain = verify_record(
        envelope, expected_lane=expected_lane,
        expected_parent_sha256=expected_parent_sha256,
        sender_public_key=sender_public_key,
        recipient_private_key=recipient_private_key)
    replay_ledger.admit(expected_lane, envelope["event_id"], envelope_digest(envelope))
    return plain
