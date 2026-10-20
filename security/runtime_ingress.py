"""Opt-in authenticated ingress for native HandoffRuntime movements.

Existing scheduler and journal retain their source ownership. Trust comes from
operator-pinned actor keys, never from self-described envelope contents.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from runtime.journal import handoff_from_dict, handoff_to_dict
from .continuation import EnvelopeError, ReplayLedger, open_record, seal_record

HANDOFF_VERSION = "ab-runtime-handoff/v1"
RESULT_VERSION = "ab-runtime-result/v1"
VALID_RESULTS = frozenset({"COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"})


def _json_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _load_document(raw: bytes, version: str) -> dict[str, Any]:
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise EnvelopeError("duplicate protected field")
            out[key] = value
        return out

    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              EnvelopeError("nonfinite protected value")))
    except (ValueError, UnicodeError, TypeError) as exc:
        raise EnvelopeError("invalid protected runtime document") from exc
    if (type(data) is not dict or set(data) != {"version", "body"}
            or data["version"] != version or type(data["body"]) is not dict):
        raise EnvelopeError("wrong protected runtime document")
    if raw != _json_bytes(data):
        raise EnvelopeError("noncanonical protected runtime document")
    return data["body"]


def _handoff_bytes(handoff: Handoff) -> bytes:
    if not isinstance(handoff, Handoff):
        raise TypeError("native runtime Handoff required")
    return _json_bytes({"version": HANDOFF_VERSION, "body": handoff_to_dict(handoff)})


def _result_bytes(handoff_id: str, prior_event_id: str, result: ExecutionResult) -> bytes:
    if not isinstance(result, ExecutionResult):
        raise TypeError("native runtime ExecutionResult required")
    if result.status not in VALID_RESULTS:
        raise EnvelopeError("invalid result status")
    return _json_bytes({"version": RESULT_VERSION,
                        "body": {"handoff_id": handoff_id,
                                 "prior_event_id": prior_event_id,
                                 "result": asdict(result)}})


def seal_handoff(handoff: Handoff, *, lane: str,
                 parent_sha256: str | None,
                 sender_private_key: Ed25519PrivateKey,
                 recipient_public_key: X25519PublicKey) -> dict:
    """Encrypt and sign the native handoff without creating a second task type."""
    return seal_record(_handoff_bytes(handoff), lane=lane,
                       event_id=handoff.handoff_id,
                       parent_sha256=parent_sha256,
                       sender_private_key=sender_private_key,
                       recipient_public_key=recipient_public_key)


def seal_result(handoff_id: str, prior_event_id: str,
                result: ExecutionResult, *, event_id: str, lane: str,
                parent_sha256: str | None,
                sender_private_key: Ed25519PrivateKey,
                recipient_public_key: X25519PublicKey) -> dict:
    """Bind a returned result to the last observed native runtime event."""
    return seal_record(_result_bytes(handoff_id, prior_event_id, result),
                       lane=lane, event_id=event_id, parent_sha256=parent_sha256,
                       sender_private_key=sender_private_key,
                       recipient_public_key=recipient_public_key)


@dataclass(frozen=True)
class IngressAuthority:
    """Separately established scope, never read from an untrusted envelope."""
    lane: str
    signer_actor: str
    receiver_actor: str
    signer_public_key: Ed25519PublicKey
    receiver_private_key: X25519PrivateKey
    operator_pin_ledger: object | None = None

    def source_key(self) -> tuple[str, str, str]:
        """Fixed operator key scope, independent of the incoming envelope."""
        from cryptography.hazmat.primitives import serialization
        raw = self.signer_public_key.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return (
            f"ab-ingress:{self.lane}:{self.signer_actor}:{self.receiver_actor}",
            "ab-security-ingress-v1",
            sha256(raw).hexdigest(),
        )

    def require_current_operator_pin(self) -> None:
        """Re-read B14 current trust on EVERY native ingress movement."""
        if self.operator_pin_ledger is None:
            return  # direct API is an explicitly trusted local/test integration
        from systems.workspace.b14_operator_pin_ledger import OperatorPinLedger
        if not isinstance(self.operator_pin_ledger, OperatorPinLedger):
            raise PermissionError("B14 operator trust ledger required")
        source, edition, pin = self.source_key()
        self.operator_pin_ledger.require_current(source, edition, pin)

    def __post_init__(self):
        if (not isinstance(self.lane, str) or not self.lane.strip()
                or not isinstance(self.signer_actor, str) or not self.signer_actor.strip()
                or not isinstance(self.receiver_actor, str) or not self.receiver_actor.strip()
                or not isinstance(self.signer_public_key, Ed25519PublicKey)
                or not isinstance(self.receiver_private_key, X25519PrivateKey)):
            raise ValueError("explicit trusted actors and keys required")


class AuthenticatedHandoffIngress:
    """Verify a sealed movement before delegating to the existing runtime.

    Direct runtime methods remain trusted application APIs. Replay admission
    and the runtime journal are separate stores, so a journal failure consumes
    the event ID and fails closed instead of automatically retrying.
    """

    def __init__(self, runtime: HandoffRuntime, ledger: ReplayLedger,
                 authority: IngressAuthority):
        if not isinstance(runtime, HandoffRuntime) or not isinstance(ledger, ReplayLedger):
            raise TypeError("native runtime and replay ledger required")
        if not isinstance(authority, IngressAuthority):
            raise TypeError("pinned ingress authority required")
        self.runtime = runtime
        self.ledger = ledger
        self.authority = authority

    def _open(self, envelope: dict, expected_parent_sha256: str | None) -> bytes:
        self.authority.require_current_operator_pin()
        return open_record(envelope, expected_lane=self.authority.lane,
                           expected_parent_sha256=expected_parent_sha256,
                           sender_public_key=self.authority.signer_public_key,
                           recipient_private_key=self.authority.receiver_private_key,
                           replay_ledger=self.ledger)

    def submit(self, envelope: dict, *, expected_parent_sha256: str | None = None):
        """Admit one authenticated native handoff without executing a worker."""
        raw = self._open(envelope, expected_parent_sha256)
        body = _load_document(raw, HANDOFF_VERSION)
        try:
            handoff = handoff_from_dict(body)
            normalized = _handoff_bytes(handoff)
        except (TypeError, ValueError, KeyError, AttributeError) as exc:
            raise EnvelopeError("invalid native handoff specification") from exc
        if normalized != raw:
            raise EnvelopeError("noncanonical native handoff fields")
        if (handoff.handoff_id != envelope["event_id"]
                or handoff.from_actor != self.authority.signer_actor
                or handoff.to_actor != self.authority.receiver_actor):
            raise EnvelopeError("handoff actor or event identity not authorized")
        return self.runtime.submit(handoff)

    def return_result(self, envelope: dict, *, handoff_id: str,
                      expected_parent_sha256: str | None = None):
        """Admit an authenticated, state-bound result from the assigned worker."""
        handoff = self.runtime.get(handoff_id)
        if handoff.to_actor != self.authority.signer_actor:
            raise EnvelopeError("result actor not authorized for handoff")
        prior = self.runtime.state(handoff_id).last_event_id
        raw = self._open(envelope, expected_parent_sha256)
        body = _load_document(raw, RESULT_VERSION)
        if set(body) != {"handoff_id", "prior_event_id", "result"}:
            raise EnvelopeError("invalid native result fields")
        if body["handoff_id"] != handoff_id or body["prior_event_id"] != prior:
            raise EnvelopeError("stale or wrong native result relationship")
        row = body["result"]
        if (type(row) is not dict or set(row) != {"status", "output", "evidence", "note"}
                or row["status"] not in VALID_RESULTS
                or type(row["output"]) is not dict
                or type(row["evidence"]) is not list
                or not isinstance(row["note"], str)):
            raise EnvelopeError("invalid native result")
        try:
            result = ExecutionResult(status=row["status"], output=row["output"],
                                     evidence=tuple(EvidenceRecord(**e) for e in row["evidence"]),
                                     note=row["note"])
            normalized = _result_bytes(handoff_id, prior, result)
        except (TypeError, ValueError, KeyError) as exc:
            raise EnvelopeError("invalid native result evidence") from exc
        if raw != normalized:
            raise EnvelopeError("noncanonical native result evidence")
        return self.runtime.return_result(handoff_id,
                                          actor_id=self.authority.signer_actor,
                                          result=result)
