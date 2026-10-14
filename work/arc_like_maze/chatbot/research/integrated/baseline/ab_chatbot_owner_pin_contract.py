"""Explicit exact-source-owner pins on the existing provenance-aware chatbot.

A pin is an in-process, registry-issued referent to a live locally verified
owner and *that exact snapshot object*. It is NOT cryptographic identity or
proof of source continuity. Re-pinning creates another referent/session.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import secrets
from typing import Any

from ab_chatbot_provenance_contract import ProvenanceTaskSession, LOCAL
from ab_chatbot_rule_change import _version
from ab_chatbot_language_bridge import ObservationWall


@dataclass(frozen=True)
class PinDescription:
    token: str
    claimed_source: str
    revision: int
    digest: str
    predecessor: str | None


@dataclass
class _StoredPin:
    description: PinDescription
    bridge: object
    owner: object
    snapshot: object
    active: bool = True


@dataclass(frozen=True)
class OwnerPinResult:
    status: str
    pins: tuple[tuple[str, PinDescription, bool], ...]
    base_outcome: object | None
    detail: str


class OwnerPinRegistry:
    """Local registry; registration demands the underlying live owner proof."""
    def __init__(self):
        self._records: dict[str, _StoredPin] = {}

    def issue(self, bridge, *, predecessor: str | None = None) -> PinDescription:
        if predecessor is not None and predecessor not in self._records:
            raise ValueError('unknown predecessor referent')
        if getattr(bridge, 'owner', None) is None or bridge._scope(bridge.snapshot) != LOCAL:
            raise ValueError('cannot issue owner pin from remote/unverified evidence')
        if getattr(bridge, 'origin_scope', None) != LOCAL:
            raise ValueError('owner was not locally verified at initial capture')
        source, revision, digest = _version(bridge)
        token = secrets.token_hex(24)
        description = PinDescription(token, source, revision, digest, predecessor)
        self._records[token] = _StoredPin(description, bridge, bridge.owner, bridge.snapshot)
        return description

    def revoke(self, token: str) -> None:
        if token not in self._records:
            raise ValueError('unknown owner pin')
        self._records[token].active = False

    def verify(self, token: str, bridge) -> bool:
        record = self._records.get(token)
        if record is None or not record.active:
            return False
        descriptor = record.description
        if (record.bridge is not bridge or record.owner is not bridge.owner or
                record.snapshot is not bridge.snapshot or
                _version(bridge) != (descriptor.claimed_source, descriptor.revision, descriptor.digest)):
            record.active = False
            return False
        try:
            current = bridge._scope(bridge.snapshot)
        except (ObservationWall, ValueError, AttributeError, KeyError):
            record.active = False
            return False
        if current != LOCAL:
            record.active = False
            return False
        return True

    def description(self, token: str) -> PinDescription | None:
        record = self._records.get(token)
        return record.description if record else None


class ExactOwnerTaskSession:
    """Opt-in owner-pin gate around unchanged ProvenanceTaskSession.

    Unknown, revoked, wrong-owner, changed-version or changed-snapshot pins
    stop before the underlying mathematical task can request new edges.
    """
    def __init__(self, old, new, task_input: Any, *, registry: OwnerPinRegistry, **kwargs):
        self.registry, self.old, self.new = registry, old, new
        self.requested: tuple[tuple[str, str], ...] = ()
        self.base = None
        self.fingerprint = None
        self.status = 'UNKNOWN_TASK'
        self.detail = 'Exact pin task must use a structured declaration.'
        if type(task_input) is not dict or 'required_owner_pins' not in task_input:
            self.status = 'NOT_PIN_TASK'
            self.detail = 'No exact-owner-pin task declared.'
            return
        pins = task_input['required_owner_pins']
        if (type(pins) is not dict or not pins or set(pins) - {'old', 'new'} or
                any(type(value) is not str or len(value) != 48 or
                    any(char not in '0123456789abcdef' for char in value)
                    for value in pins.values())):
            self.status = 'INVALID_TASK'
            self.detail = 'A pin must name a locally issued 48-character token per side.'
            return
        self.requested = tuple((side, pins[side]) for side in ('old','new') if side in pins)
        remaining = {k: v for k, v in task_input.items() if k != 'required_owner_pins'}
        existing = remaining.get('required_provenance', {})
        if (type(existing) is not dict or set(existing) - {'old','new'} or
                any(value != LOCAL for value in existing.values())):
            self.status = 'INVALID_TASK'
            self.detail = 'Conflicting or invalid source scope.'
            return
        remaining['required_provenance'] = {**existing, **{side: LOCAL for side, _ in self.requested}}
        for side, token in self.requested:
            if self.registry.description(token) is None:
                self.status = 'UNKNOWN_OWNER_PIN'
                self.detail = 'The declared pin was not issued by this in-process registry.'
                return
        base = ProvenanceTaskSession(old, new, remaining, **kwargs)
        if base.intake.status != 'TASK_ACCEPTED':
            self.status = base.intake.status
            self.detail = base.intake.detail
            return
        self.base = base
        self.status = 'TASK_ACCEPTED'
        descriptor = {'base': base.intake.contract.fingerprint, 'required_owner_pins':
                      [(side, token) for side, token in self.requested]}
        self.fingerprint = hashlib.sha256(json.dumps(descriptor, sort_keys=True,
                                 separators=(',', ':')).encode()).hexdigest()
        self.detail = 'Pin requirements admitted as declarations, not source proofs.'

    def advance(self, *, max_new_edges=108) -> OwnerPinResult:
        if self.base is None:
            return OwnerPinResult(self.status, (), None, self.detail)
        checked = []
        for side, token in self.requested:
            bridge = self.old if side == 'old' else self.new
            valid = self.registry.verify(token, bridge)
            checked.append((side, self.registry.description(token), valid))
        if not all(row[2] for row in checked):
            return OwnerPinResult('OWNER_PIN_UNPROVED', tuple(checked), None,
                'Exact pinned owner or snapshot is not live. Re-pin explicitly and start a new task; do not inherit prior success.')
        result = self.base.advance(max_new_edges=max_new_edges)
        # Re-evaluate in case the underlying step was concurrent with withdrawal.
        after = tuple((side, self.registry.description(token),
                       self.registry.verify(token, self.old if side=='old' else self.new))
                      for side,token in self.requested)
        if not all(row[2] for row in after):
            return OwnerPinResult('OWNER_PIN_UNPROVED', after, None,
                                  'Owner binding changed during task continuation.')
        return OwnerPinResult(result.status, after, result,
                              'Task result scoped to the exact currently pinned owners.')
