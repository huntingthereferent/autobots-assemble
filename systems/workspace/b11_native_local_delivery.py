"""B11: source-owned LOCAL_PASS delivery into the existing B10 event journal.

The trust anchor is a caller-pinned Ed25519 public key per native source edition,
PLUS an independent, current native-result verifier. Neither a B9 proposal nor
an actor string can supply either trust anchor. The source owner signs a
canonical, exact-handoff receipt outside this module.

This is a bounded single-writer library, not a scheduler, source owner, or
external credential issuer. The original journal handles durable event replay.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from runtime.handoff import Handoff, HandoffEvent, utc_now
from runtime.engine import HandoffRuntime
from systems.workspace.b9_continuation_bridge import (
    BRIDGE_SOURCE, B9ContinuationBridge, scoped_local_verifier,
)
from systems.workspace.observed_event_journal import (
    LOCAL_PASS, ObservedEventJournal, SourceAdapter,
)
from systems.workspace.workstation_construction import WorkstationConstruction

PROTOCOL = "b11-pinned-native-local-result/v1"
ACTOR = "b11-source-owned-local-delivery"


@dataclass(frozen=True)
class NativeLocalProof:
    """A source-signed claim, NOT proof without a pinned key and native recheck."""

    handoff_id: str
    source_name: str
    source_edition: str
    required_relation: str
    candidate_spec_sha256: str
    source_locator: str
    native_receipt_ref: str
    native_receipt_sha256: str


def canonical_proof_bytes(proof: NativeLocalProof) -> bytes:
    """Stable bytes a native source owner signs with its own Ed25519 key."""
    if not isinstance(proof, NativeLocalProof):
        raise TypeError("B11 requires a typed native local proof")
    return json.dumps(
        {"protocol": PROTOCOL, "receipt": asdict(proof)},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _bounded(value: object, max_length: int = 400) -> bool:
    return isinstance(value, str) and 0 < len(value) <= max_length and value.strip() == value


def _sha256(value: object) -> bool:
    return (_bounded(value, 64) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


class SourceOwnedAdmission:
    """Verify signed source identity, exact B10 request, and fresh native state.

    Public-key registration is an EXTERNAL trust decision. A valid signature
    alone never establishes a still-current local result or a complete route.
    """

    def __init__(self, *, pinned_public_keys: Mapping[tuple[str, str], bytes],
                 verify_native_current: Callable[[NativeLocalProof], bool]):
        if not callable(verify_native_current):
            raise TypeError("independent current native-result verification is required")
        if not isinstance(pinned_public_keys, Mapping) or not pinned_public_keys:
            raise ValueError("one or more explicitly pinned native edition keys are required")
        verified_keys: dict[tuple[str, str], Ed25519PublicKey] = {}
        for identity, public in pinned_public_keys.items():
            if (not isinstance(identity, tuple) or len(identity) != 2
                    or not all(_bounded(i, 200) for i in identity)
                    or not isinstance(public, bytes) or len(public) != 32):
                raise ValueError("invalid native source edition pin")
            try:
                verified_keys[identity] = Ed25519PublicKey.from_public_bytes(public)
            except ValueError as exc:
                raise ValueError("invalid pinned Ed25519 public key") from exc
        self._keys = verified_keys
        self._verify_native_current = verify_native_current

    def verify(self, handoff: Handoff, event: HandoffEvent) -> bool:
        if (not isinstance(handoff, Handoff)
                or handoff.metadata.get("source_system") != BRIDGE_SOURCE
                or not isinstance(event, HandoffEvent)
                or event.event_type != LOCAL_PASS
                or event.actor_id != ACTOR
                or event.handoff_id != handoff.handoff_id):
            return False
        data = event.data
        if not isinstance(data, dict) or set(data) != {"protocol", "receipt", "signature"}:
            return False
        if data["protocol"] != PROTOCOL or not isinstance(data["receipt"], dict):
            return False
        if set(data["receipt"]) != set(NativeLocalProof.__dataclass_fields__):
            return False
        try:
            proof = NativeLocalProof(**data["receipt"])
        except (TypeError, ValueError):
            return False
        if (not all(_bounded(value) for value in asdict(proof).values())
                or not _sha256(proof.candidate_spec_sha256)
                or not _sha256(proof.native_receipt_sha256)):
            return False
        binding = handoff.metadata.get("continuation_source_binding")
        if not isinstance(binding, dict):
            return False
        if (proof.handoff_id != handoff.handoff_id
                or proof.required_relation != handoff.required_relation
                or proof.source_name != binding.get("name")
                or proof.source_edition != binding.get("edition")
                or proof.candidate_spec_sha256 != handoff.metadata.get("candidate_spec_sha256")
                or proof.source_locator != handoff.metadata.get("source_locator")):
            return False
        signature = data["signature"]
        if (not isinstance(signature, str) or len(signature) != 128
                or any(c not in "0123456789abcdef" for c in signature)):
            return False
        key = self._keys.get((proof.source_name, proof.source_edition))
        if key is None:
            return False
        try:
            key.verify(bytes.fromhex(signature), canonical_proof_bytes(proof))
        except (InvalidSignature, ValueError, TypeError):
            return False
        try:
            # The source owner must check its live native state against BOTH
            # the exact receipt reference AND its content digest. An old or
            # independently revoked local PASS is not a trigger.
            return self._verify_native_current(proof) is True
        except Exception:
            return False


class SourceOwnedLocalDelivery:
    """Admit and append one verified B11 LOCAL_PASS event for a B10 request."""

    def __init__(self, *, construction: WorkstationConstruction,
                 journal_path: str | Path,
                 adapters: tuple[SourceAdapter, ...],
                 pinned_public_keys: Mapping[tuple[str, str], bytes],
                 verify_native_current: Callable[[NativeLocalProof], bool],
                 max_attempts: int = 8):
        if not isinstance(construction, WorkstationConstruction):
            raise TypeError("B9 construction is required")
        self.admission = SourceOwnedAdmission(
            pinned_public_keys=pinned_public_keys,
            verify_native_current=verify_native_current,
        )
        self.journal = ObservedEventJournal(
            journal_path, adapters=adapters, max_attempts=max_attempts,
            verify_local_pass=scoped_local_verifier(construction, self.admission.verify),
        )
        self.bridge = B9ContinuationBridge(construction, self.journal)

    def deliver(self, proof: NativeLocalProof, *, signature_hex: str) -> HandoffEvent:
        """Native source delivery; idempotent for an identical signed proof.

        A rejected proof is NEVER appended. A durable, admitted proof is
        recoverable by ObservedEventJournal if the process dies before its
        native attempt starts. A started attempt still needs reconciliation.
        """
        payload = {
            "protocol": PROTOCOL,
            "receipt": asdict(proof) if isinstance(proof, NativeLocalProof) else {},
            "signature": signature_hex,
        }
        event_id = "evt_b11_" + sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest()
        event = HandoffEvent(
            event_id=event_id, handoff_id=proof.handoff_id,
            event_type=LOCAL_PASS, actor_id=ACTOR, occurred_at=utc_now(),
            data=payload,
        )
        try:
            handoff = HandoffRuntime(event_store=self.journal).get(proof.handoff_id)
        except KeyError as exc:
            raise ValueError("B11 proof targets an unregistered handoff") from exc
        if not self.journal.verify_local_pass(handoff, event):
            raise ValueError("source-owned local proof was not independently admitted")
        existing = [e for e in self.journal.for_handoff(proof.handoff_id)
                    if e.event_id == event_id]
        if existing:
            if (len(existing) != 1 or existing[0].event_type != LOCAL_PASS
                    or existing[0].actor_id != ACTOR or existing[0].data != payload):
                raise ValueError("conflicting durable local proof identity")
            return existing[0]
        return self.journal.append(event)
