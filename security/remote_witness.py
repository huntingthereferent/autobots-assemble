"""Offline, source-bound sealed-journal witness exchange between independent hosts.

This is observation only: verification of a signed checkpoint and contiguous
ciphertext record hashes. The observer DOES NOT decrypt the source's journal,
admit source work, establish remote operator identity or implement consensus.
"""
from __future__ import annotations

import base64
import binascii
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .continuation import TOKEN
from .journal_checkpoint import verify_checkpoint, verify_checkpoint_signature, _fingerprint
from .sealed_journal import MAX_RECORD, SCHEMA, SealedJournalError, SealedRuntimeJournal

VERSION = "ab-remote-journal-witness/v1"
MAX_FRAMES = 64
FRAME_FIELDS = frozenset({"seq", "prev", "nonce", "cipher", "digest"})
BUNDLE_FIELDS = frozenset({"version", "tip_checkpoint", "frames"})
HEX_DIGITS = frozenset("0123456789abcdef")


def _hex_digest(value: object) -> bool:
    return type(value) is str and len(value) == 64 and set(value) <= HEX_DIGITS


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _read64(value: object, *, expected: int | None = None) -> bytes:
    if type(value) is not str or len(value) > (MAX_RECORD + 16) * 2:
        raise SealedJournalError("invalid remote witness field size")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise SealedJournalError("invalid remote witness base64") from exc
    if base64.b64encode(raw).decode("ascii") != value:
        raise SealedJournalError("noncanonical remote witness field")
    if expected is not None and len(raw) != expected:
        raise SealedJournalError("unexpected remote witness field length")
    return raw


def export_witness_span(journal: SealedRuntimeJournal, *,
                        base_checkpoint: dict, tip_checkpoint: dict,
                        source_public_key: Ed25519PublicKey) -> dict:
    """Export at most 64 encrypted rows connecting two signed checkpoints.

    Both checkpoints must describe this actual locally verified journal.
    No local decryption key or plaintext record leaves this function.
    """
    verify_checkpoint(journal, base_checkpoint, source_public_key)
    verify_checkpoint(journal, tip_checkpoint, source_public_key)
    first, last = base_checkpoint["sequence"], tip_checkpoint["sequence"]
    if (base_checkpoint["journal_identity"] != tip_checkpoint["journal_identity"]
            or not 0 < last - first <= MAX_FRAMES):
        raise SealedJournalError("witness export needs bounded forward movement")
    frames = []
    with closing(journal._connect()) as db:
        db.execute("BEGIN")
        rows = db.execute(
            "SELECT seq, prev, nonce, cipher, digest FROM records "
            "WHERE seq > ? AND seq <= ? ORDER BY seq", (first, last)).fetchall()
        if len(rows) != last - first:
            raise SealedJournalError("source witness rows missing")
        previous = bytes.fromhex(base_checkpoint["head_digest"])
        for seq, back, nonce, cipher, digest in rows:
            if (seq != first + len(frames) + 1 or back != previous
                    or digest != journal._digest(seq, previous, nonce, cipher)):
                raise SealedJournalError("source witness history diverged")
            frames.append({
                "seq": seq,
                "prev": back.hex(),
                "nonce": base64.b64encode(nonce).decode("ascii"),
                "cipher": base64.b64encode(cipher).decode("ascii"),
                "digest": digest.hex(),
            })
            previous = digest
        if previous.hex() != tip_checkpoint["head_digest"]:
            raise SealedJournalError("source witness tip changed")
    return {"version": VERSION, "tip_checkpoint": tip_checkpoint, "frames": frames}


def verify_witness_span(bundle: dict, *, base_checkpoint: dict,
                        source_public_key: Ed25519PublicKey) -> dict:
    """Verify a forward extension of a trusted source prefix, without the key.

    This proves a signed cipher-hash continuation, not its plaintext content.
    """
    verify_checkpoint_signature(base_checkpoint, source_public_key)
    if type(bundle) is not dict or set(bundle) != BUNDLE_FIELDS:
        raise SealedJournalError("invalid remote witness bundle")
    if bundle["version"] != VERSION:
        raise SealedJournalError("wrong remote witness protocol version")
    tip = bundle["tip_checkpoint"]
    verify_checkpoint_signature(tip, source_public_key)
    if tip["journal_identity"] != base_checkpoint["journal_identity"]:
        raise SealedJournalError("remote witness journal identity mismatch")
    first, last = base_checkpoint["sequence"], tip["sequence"]
    frames = bundle["frames"]
    if (type(frames) is not list or not 0 < last - first <= MAX_FRAMES
            or len(frames) != last - first):
        raise SealedJournalError("remote witness has missing, replayed or unbounded frames")
    previous = bytes.fromhex(base_checkpoint["head_digest"])
    for index, frame in enumerate(frames, start=first + 1):
        if type(frame) is not dict or set(frame) != FRAME_FIELDS:
            raise SealedJournalError("remote witness frame shape mismatch")
        if (type(frame["seq"]) is not int or frame["seq"] != index
                or not _hex_digest(frame["prev"]) or not _hex_digest(frame["digest"])
                or frame["prev"] != previous.hex()):
            raise SealedJournalError("remote witness sequence or parent mismatch")
        nonce = _read64(frame["nonce"], expected=12)
        cipher = _read64(frame["cipher"])
        if not 16 < len(cipher) <= MAX_RECORD + 16:
            raise SealedJournalError("remote witness ciphertext size invalid")
        expected = sha256(SCHEMA + b"|" + index.to_bytes(8, "big") +
                          b"|" + previous + nonce + cipher).hexdigest()
        if expected != frame["digest"]:
            raise SealedJournalError("remote witness record digest mismatch")
        previous = bytes.fromhex(expected)
    if previous.hex() != tip["head_digest"]:
        raise SealedJournalError("remote witness does not reach signed tip")
    return tip


class RemoteWitnessLedger:
    """Observer-owned SQLite prefix; no remote host can self-enroll.

    Initial checkpoint and source public key must be independently retained
    and verified by the receiver's operator. A source can sign contradictory
    histories; this detects a fork *from the observer's pinned prefix* but
    does not prove source honesty or a global canonical order.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if (self.path.is_symlink() or not self.path.parent.is_dir()
                or self.path.is_dir()):
            raise SealedJournalError("unsafe observer witness ledger path")
        with closing(self._connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS sources ("
                       "source_id TEXT PRIMARY KEY, signer TEXT NOT NULL, "
                       "journal TEXT NOT NULL, checkpoint TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS movements ("
                       "source_id TEXT NOT NULL, first_seq INTEGER NOT NULL, "
                       "last_seq INTEGER NOT NULL, tip TEXT NOT NULL, "
                       "PRIMARY KEY (source_id, last_seq))")

    def _connect(self):
        if self.path.is_symlink():
            raise SealedJournalError("observer ledger path became symlink")
        return sqlite3.connect(self.path, timeout=10)

    @staticmethod
    def _name(source_id: str):
        if type(source_id) is not str or not TOKEN.fullmatch(source_id):
            raise SealedJournalError("operator source label must be bounded")

    def enroll(self, source_id: str, *,
               signed_base_checkpoint: dict,
               trusted_source_public_key: Ed25519PublicKey) -> None:
        """Trusted *local* enrollment, never called by received network data."""
        self._name(source_id)
        verify_checkpoint_signature(signed_base_checkpoint, trusted_source_public_key)
        with closing(self._connect()) as db, db:
            try:
                db.execute("INSERT INTO sources VALUES (?, ?, ?, ?)", (
                    source_id, _fingerprint(trusted_source_public_key),
                    signed_base_checkpoint["journal_identity"],
                    _canonical(signed_base_checkpoint)))
            except sqlite3.IntegrityError as exc:
                raise SealedJournalError("source already operator-enrolled") from exc

    def current(self, source_id: str, *,
                trusted_source_public_key: Ed25519PublicKey) -> dict:
        self._name(source_id)
        with closing(self._connect()) as db:
            row = db.execute("SELECT signer, journal, checkpoint FROM sources "
                             "WHERE source_id=?", (source_id,)).fetchone()
        if row is None or row[0] != _fingerprint(trusted_source_public_key):
            raise SealedJournalError("source not independently pinned")
        checkpoint = json.loads(row[2])
        verify_checkpoint_signature(checkpoint, trusted_source_public_key)
        if row[1] != checkpoint["journal_identity"]:
            raise SealedJournalError("observer source identity altered")
        return checkpoint

    def observe(self, source_id: str, bundle: dict, *,
                trusted_source_public_key: Ed25519PublicKey) -> dict:
        """Atomically advance the observer's source-specific witnessed prefix."""
        self._name(source_id)
        # Validate against the presently stored baseline *inside* the writer
        # transaction, not against an earlier optimistic snapshot.
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT signer, journal, checkpoint FROM sources "
                             "WHERE source_id=?", (source_id,)).fetchone()
            if row is None or row[0] != _fingerprint(trusted_source_public_key):
                raise SealedJournalError("source not independently pinned")
            base = json.loads(row[2])
            verify_checkpoint_signature(base, trusted_source_public_key)
            if base["journal_identity"] != row[1]:
                raise SealedJournalError("observer source identity altered")
            tip = verify_witness_span(bundle, base_checkpoint=base,
                                      source_public_key=trusted_source_public_key)
            db.execute("INSERT INTO movements VALUES (?, ?, ?, ?)", (
                source_id, base["sequence"], tip["sequence"], _canonical(tip)))
            db.execute("UPDATE sources SET checkpoint=? WHERE source_id=?",
                       (_canonical(tip), source_id))
            db.commit()
            return tip
