"""Operator-signed checkpoint of a native encrypted journal's observed prefix.

The operator must publish/preserve the returned signed checkpoint OUTSIDE the
journal's rollback domain. Local hash chains cannot supply that anchor.
"""
from __future__ import annotations

from contextlib import closing
from hashlib import sha256
import json
import sqlite3

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature, InvalidTag

from .sealed_journal import SealedRuntimeJournal, SealedJournalError, SCHEMA, ZERO

VERSION = "ab-native-journal-checkpoint/v1"
FIELDS = frozenset({"version", "journal_identity", "sequence", "head_digest", "signer_fingerprint", "signature"})


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def _fingerprint(key: Ed25519PublicKey) -> str:
    return sha256(key.public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).hexdigest()


def _snapshot(journal: SealedRuntimeJournal):
    """Read and authenticate the journal's complete current chain, once."""
    if not isinstance(journal, SealedRuntimeJournal):
        raise TypeError("native sealed journal required")
    with closing(journal._connect()) as db:
        db.execute("BEGIN")
        header = db.execute("SELECT version, nonce, proof FROM seal").fetchall()
        if len(header) != 1 or header[0][0] != SCHEMA.decode("ascii"):
            raise SealedJournalError("invalid journal identity")
        _, seal_nonce, seal_proof = header[0]
        if not isinstance(seal_nonce, bytes) or not isinstance(seal_proof, bytes):
            raise SealedJournalError("invalid journal header")
        identity = sha256(SCHEMA + b"|" + seal_nonce + b"|" + seal_proof).hexdigest()
        prev = ZERO
        count = 0
        digests = {0: ZERO.hex()}
        protected_admissions = {}
        for seq, back, nonce, cipher, digest in db.execute(
                "SELECT seq, prev, nonce, cipher, digest FROM records ORDER BY seq"):
            if (type(seq) is not int or seq != count + 1 or back != prev
                    or not isinstance(nonce, bytes) or len(nonce) != 12
                    or digest != journal._digest(seq, prev, nonce, cipher)):
                raise SealedJournalError("checkpoint journal ancestry invalid")
            try:
                plaintext = journal._crypto.decrypt(nonce, cipher, journal._aad(seq, prev))
                record = json.loads(plaintext.decode("utf-8"))
                if type(record) is not dict:
                    raise SealedJournalError("invalid checkpoint native record")
                protected = record.get("_sealed_admission")
                if protected is not None:
                    if (type(protected) is not dict
                            or set(protected) != {"token", "digest"}
                            or type(protected["token"]) is not str
                            or len(protected["token"]) != 64
                            or type(protected["digest"]) is not str
                            or len(protected["digest"]) != 64):
                        raise SealedJournalError("invalid checkpoint replay binding")
                    token, envelope_hash = bytes.fromhex(protected["token"]), bytes.fromhex(protected["digest"])
                    if token in protected_admissions:
                        raise SealedJournalError("duplicate checkpoint replay binding")
                    protected_admissions[token] = envelope_hash
            except (InvalidTag, ValueError, UnicodeError, TypeError) as exc:
                raise SealedJournalError("checkpoint journal authentication failed") from exc
            count = seq
            prev = digest
            digests[seq] = digest.hex()
        if count != journal._committed_records:
            raise SealedJournalError("checkpoint source changed outside runtime")
        if dict(db.execute("SELECT token, digest FROM admitted")) != protected_admissions:
            raise SealedJournalError("checkpoint replay table differs from encrypted history")
        return identity, count, digests


def issue_checkpoint(journal: SealedRuntimeJournal,
                     signer_private_key: Ed25519PrivateKey) -> dict:
    """Return signed bytes for independently anchored storage; never save here."""
    if not isinstance(signer_private_key, Ed25519PrivateKey):
        raise TypeError("operator checkpoint signing key required")
    identity, count, digests = _snapshot(journal)
    body = {"version": VERSION, "journal_identity": identity,
            "sequence": count, "head_digest": digests[count],
            "signer_fingerprint": _fingerprint(signer_private_key.public_key())}
    return {**body, "signature": signer_private_key.sign(
        b"ab-journal-checkpoint-signature/v1|" + _canonical(body)).hex()}


def verify_checkpoint_signature(checkpoint: dict,
                                trusted_public_key: Ed25519PublicKey) -> None:
    """Authenticate checkpoint bytes without needing the sealed journal.

    Used for offline recovery; the recovered journal MUST be verified again
    against this independently pinned checkpoint before execution resumes.
    """
    if not isinstance(trusted_public_key, Ed25519PublicKey):
        raise TypeError("independently pinned checkpoint public key required")
    if type(checkpoint) is not dict or set(checkpoint) != FIELDS:
        raise SealedJournalError("invalid checkpoint structure")
    body = {k: v for k, v in checkpoint.items() if k != "signature"}
    digest = lambda x: type(x) is str and len(x) == 64 and all(c in "0123456789abcdef" for c in x)
    if (checkpoint["version"] != VERSION
            or not digest(checkpoint["journal_identity"])
            or not digest(checkpoint["head_digest"])
            or checkpoint["signer_fingerprint"] != _fingerprint(trusted_public_key)
            or type(checkpoint["sequence"]) is not int or checkpoint["sequence"] < 0
            or not isinstance(checkpoint["signature"], str)
            or len(checkpoint["signature"]) != 128):
        raise SealedJournalError("invalid or untrusted checkpoint")
    try:
        trusted_public_key.verify(bytes.fromhex(checkpoint["signature"]),
            b"ab-journal-checkpoint-signature/v1|" + _canonical(body))
    except (ValueError, InvalidSignature) as exc:
        raise SealedJournalError("checkpoint signature invalid") from exc
def verify_checkpoint(journal: SealedRuntimeJournal, checkpoint: dict,
                      trusted_public_key: Ed25519PublicKey) -> None:
    """Reject a current history that cannot include an independently signed prefix."""
    verify_checkpoint_signature(checkpoint, trusted_public_key)
    identity, count, digests = _snapshot(journal)
    if checkpoint["journal_identity"] != identity:
        raise SealedJournalError("checkpoint belongs to different journal")
    seq = checkpoint["sequence"]
    if seq > count:
        raise SealedJournalError("journal rolled back below independently anchored checkpoint")
    if digests[seq] != checkpoint["head_digest"]:
        raise SealedJournalError("journal history differs from independently anchored checkpoint")
