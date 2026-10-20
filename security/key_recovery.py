"""Bounded offline recovery envelope for the existing sealed journal key.

The recovery recipient's private key must remain outside the running
workstation. Signing this package does not by itself authorize a restore.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from .continuation import EnvelopeError, ReplayLedger, open_record, seal_record
from .journal_checkpoint import verify_checkpoint
from .sealed_journal import SealedRuntimeJournal

LANE = "ab-journal-key-recovery-v1"
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _anchor(checkpoint: dict) -> str:
    """Canonical signed checkpoint identity, not an unauthenticated claim."""
    try:
        raw = json.dumps(checkpoint, sort_keys=True, ensure_ascii=True,
                         separators=(",", ":"), allow_nan=False).encode("ascii")
    except (ValueError, TypeError) as exc:
        raise EnvelopeError("invalid checkpoint") from exc
    return sha256(raw).hexdigest()


def issue_recovery_envelope(
    journal: SealedRuntimeJournal, journal_key: bytes, *,
    signed_checkpoint: dict,
    trusted_checkpoint_public_key: Ed25519PublicKey,
    operator_signing_private_key: Ed25519PrivateKey,
    offline_recovery_public_key: X25519PublicKey,
) -> dict:
    """Wrap the verified journal key to an independently held recovery recipient."""
    if type(journal_key) is not bytes or len(journal_key) != 32:
        raise EnvelopeError("32-byte journal key required")
    verify_checkpoint(journal, signed_checkpoint, trusted_checkpoint_public_key)
    # The caller-supplied key must really unlock these records, not merely be
    # a plausible looking random 32-byte string.
    SealedRuntimeJournal(journal.path, key=journal_key)
    identity = signed_checkpoint["journal_identity"]
    return seal_record(
        journal_key, lane=LANE, event_id=identity,
        parent_sha256=_anchor(signed_checkpoint),
        sender_private_key=operator_signing_private_key,
        recipient_public_key=offline_recovery_public_key,
    )


def recover_journal_key(
    envelope: dict, *, trusted_journal_identity: str,
    signed_checkpoint: dict,
    trusted_operator_public_key: Ed25519PublicKey,
    offline_recovery_private_key: X25519PrivateKey,
    recovery_ledger: ReplayLedger,
) -> bytes:
    """Decrypt one operator-issued key; caller must separately validate restore."""
    if (not isinstance(trusted_journal_identity, str)
            or not HEX.fullmatch(trusted_journal_identity)
            or not isinstance(signed_checkpoint, dict)
            or signed_checkpoint.get("journal_identity") != trusted_journal_identity
            or not isinstance(envelope, dict)
            or envelope.get("event_id") != trusted_journal_identity):
        raise EnvelopeError("recovery identity mismatch")
    recovered = open_record(
        envelope, expected_lane=LANE,
        expected_parent_sha256=_anchor(signed_checkpoint),
        sender_public_key=trusted_operator_public_key,
        recipient_private_key=offline_recovery_private_key,
        replay_ledger=recovery_ledger)
    if len(recovered) != 32:
        raise EnvelopeError("invalid recovered journal key")
    return recovered
