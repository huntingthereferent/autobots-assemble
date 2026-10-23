"""Finite, domain-neutral packaging admission and verification contracts.

A plan is not a package; a claimed witness is not independent verification.
Unknown formats remain discoverable without an invented default adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Mapping


@dataclass(frozen=True)
class PackagingReferent:
    identity: str
    inputs: tuple[str, ...]
    required_relations: tuple[str, ...]
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class PackagingPlan:
    referent: PackagingReferent
    representation: str
    operations: tuple[str, ...]
    outputs: tuple[str, ...]
    witnesses: tuple[str, ...]
    unresolved: tuple[str, ...] = ()


@dataclass(frozen=True)
class PackagingResult:
    status: str
    plan: PackagingPlan
    evidence: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


def admit(referent: PackagingReferent, *,
          inspect: Callable[[PackagingReferent], Mapping[str, object]]) -> PackagingPlan:
    """Domain adapter observes the object; the core does not select its shape."""
    if not referent.identity.strip() or not referent.inputs or not referent.required_relations:
        raise ValueError("referent identity, inputs and required relations are necessary")
    observed = inspect(referent)
    if not isinstance(observed, Mapping):
        raise TypeError("inspection must return a mapping")
    def strings(name: str) -> tuple[str, ...]:
        value = observed.get(name, ())
        if not isinstance(value, (tuple, list)) or any(not isinstance(v, str) or not v.strip() for v in value):
            raise ValueError("invalid inspection field: " + name)
        return tuple(value)
    representation = observed.get("representation", "")
    if not isinstance(representation, str):
        raise ValueError("invalid representation")
    operations, outputs, witnesses = (strings(k) for k in ("operations", "outputs", "witnesses"))
    unresolved = strings("unresolved")
    if not representation.strip():
        unresolved += ("representation",)
    if not operations:
        unresolved += ("operations",)
    if not outputs:
        unresolved += ("outputs",)
    if not witnesses:
        unresolved += ("witnesses",)
    return PackagingPlan(referent, representation, operations, outputs, witnesses,
                         tuple(dict.fromkeys(unresolved)))


def verify(plan: PackagingPlan, *,
           evidence: Mapping[str, bytes],
           independent_witness: Callable[[str, bytes, PackagingPlan], bool]) -> PackagingResult:
    """Verify each required witness against actual bytes using a supplied native checker."""
    if plan.unresolved:
        return PackagingResult("DISCOVERY_REQUIRED", plan, missing=plan.unresolved)
    if not callable(independent_witness):
        raise ValueError("independent verifier required")
    accepted = []
    missing = []
    for witness in plan.witnesses:
        blob = evidence.get(witness)
        if not isinstance(blob, bytes) or not independent_witness(witness, blob, plan):
            missing.append(witness)
        else:
            accepted.append(witness + ":sha256:" + sha256(blob).hexdigest())
    return PackagingResult("VERIFIED" if not missing else "UNVERIFIED",
                           plan, tuple(accepted), tuple(missing))
