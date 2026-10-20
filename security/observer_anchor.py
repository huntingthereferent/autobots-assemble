"""Independently retainable observer-owned source checkpoint.

The operator signs an observer prefix OUTSIDE the observer SQLite rollback
domain. Verification checks the *anchored prefix*, while later unanchored
observations may extend it. No automatic off-host publication is claimed.
"""
from __future__ import annotations

from contextlib import closing
from hashlib import sha256
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .journal_checkpoint import verify_checkpoint_signature
from .remote_witness import RemoteWitnessLedger
from .sealed_journal import SealedJournalError

VERSION = "ab-independent-observer-anchor/v1"
FIELDS = frozenset({"version", "source_id", "source_signer", "journal_identity",
                    "checkpoint", "movement_count", "history_sha256",
                    "observer_signer", "signature"})
HEX = frozenset("0123456789abcdef")
CONTEXT = b"ab-observer-anchor-sig/v1|"


def _canon(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def _fp(pub):
    return sha256(pub.public_bytes(serialization.Encoding.Raw,
                                   serialization.PublicFormat.Raw)).hexdigest()


def _digest(value):
    return type(value) is str and len(value) == 64 and set(value) <= HEX


def _history(ledger: RemoteWitnessLedger, source_id: str,
             source_public_key: Ed25519PublicKey):
    ledger._name(source_id)
    if not isinstance(source_public_key, Ed25519PublicKey):
        raise TypeError("independently pinned source public key required")
    with closing(ledger._connect()) as db:
        db.execute("BEGIN")
        src = db.execute("SELECT signer, journal, checkpoint FROM sources WHERE source_id=?",
                         (source_id,)).fetchone()
        if src is None or src[0] != _fp(source_public_key):
            raise SealedJournalError("observer source signer is not pinned")
        rows = db.execute(
            "SELECT first_seq,last_seq,tip FROM movements WHERE source_id=? "
            "ORDER BY last_seq", (source_id,)).fetchall()
        try:
            current = json.loads(src[2])
        except (TypeError, ValueError) as exc:
            raise SealedJournalError("invalid observer source checkpoint") from exc
        verify_checkpoint_signature(current, source_public_key)
        if current["journal_identity"] != src[1]:
            raise SealedJournalError("observer journal identity changed")
        history = []
        prior = None
        for first, last, raw in rows:
            try:
                tip = json.loads(raw)
            except (TypeError, ValueError) as exc:
                raise SealedJournalError("invalid observed tip") from exc
            verify_checkpoint_signature(tip, source_public_key)
            if (tip["journal_identity"] != src[1]
                    or type(first) is not int or type(last) is not int
                    or first < 0 or last <= first or last != tip["sequence"]
                    or (prior is not None and first != prior)):
                raise SealedJournalError("observer movement history not continuous")
            prior = last
            history.append({"first_seq": first, "last_seq": last, "tip": tip})
        if history and history[-1]["tip"] != current:
            raise SealedJournalError("observer current state differs from last movement")
        return src[0], src[1], current, history


def issue_observer_anchor(ledger: RemoteWitnessLedger, source_id: str, *,
                          source_public_key: Ed25519PublicKey,
                          observer_private_key: Ed25519PrivateKey) -> dict:
    """Return a signed observer prefix; calling this does NOT store it safely."""
    if not isinstance(observer_private_key, Ed25519PrivateKey):
        raise TypeError("observer signing key required")
    signer, journal, checkpoint, rows = _history(ledger, source_id, source_public_key)
    body = {"version": VERSION, "source_id": source_id,
            "source_signer": signer, "journal_identity": journal,
            "checkpoint": checkpoint, "movement_count": len(rows),
            "history_sha256": sha256(_canon(rows)).hexdigest(),
            "observer_signer": _fp(observer_private_key.public_key())}
    return {**body, "signature": observer_private_key.sign(CONTEXT + _canon(body)).hex()}


def verify_observer_anchor(ledger: RemoteWitnessLedger, anchor: dict, *,
                           source_public_key: Ed25519PublicKey,
                           observer_public_key: Ed25519PublicKey) -> None:
    """Reject a rolled-back/rewritten observer prefix before admitting work."""
    if (not isinstance(observer_public_key, Ed25519PublicKey)
            or type(anchor) is not dict or set(anchor) != FIELDS
            or anchor["version"] != VERSION or not _digest(anchor["source_signer"])
            or not _digest(anchor["journal_identity"])
            or not _digest(anchor["history_sha256"])
            or anchor["source_signer"] != _fp(source_public_key)
            or anchor["observer_signer"] != _fp(observer_public_key)
            or type(anchor["movement_count"]) is not int
            or anchor["movement_count"] < 0
            or type(anchor["signature"]) is not str or len(anchor["signature"]) != 128):
        raise SealedJournalError("invalid independently signed observer anchor")
    try:
        observer_public_key.verify(bytes.fromhex(anchor["signature"]),
                                   CONTEXT + _canon({k:v for k,v in anchor.items()
                                                    if k != "signature"}))
    except (ValueError, InvalidSignature, TypeError) as exc:
        raise SealedJournalError("observer anchor signature invalid") from exc
    # Source signature independently authenticates the journal tip named by
    # the observer; an observer's signature cannot enroll a source key.
    verify_checkpoint_signature(anchor["checkpoint"], source_public_key)
    signer, journal, current, rows = _history(
        ledger, anchor["source_id"], source_public_key)
    if signer != anchor["source_signer"] or journal != anchor["journal_identity"]:
        raise SealedJournalError("observer anchor refers to another source")
    n = anchor["movement_count"]
    if len(rows) < n:
        raise SealedJournalError("observer history rolled back below signed anchor")
    if sha256(_canon(rows[:n])).hexdigest() != anchor["history_sha256"]:
        raise SealedJournalError("observer history differs from signed prefix")
    if n:
        if rows[n-1]["tip"] != anchor["checkpoint"]:
            raise SealedJournalError("observer anchor checkpoint mismatch")
    elif rows:
        if rows[0]["first_seq"] != anchor["checkpoint"]["sequence"]:
            raise SealedJournalError("observer initial prefix changed")
    elif current != anchor["checkpoint"]:
        raise SealedJournalError("observer current checkpoint changed")
    if len(rows) > n and rows[n]["first_seq"] != anchor["checkpoint"]["sequence"]:
        raise SealedJournalError("observer continuation does not extend anchor")
