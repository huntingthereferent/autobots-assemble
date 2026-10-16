"""B1: deterministic continuation proposals for existing workstation lanes.

The policy neither runs a process nor certifies its own evidence. Native
verifiers belong to the host and must independently validate every observation
and every cross-lane relation before a proposed movement is admitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from typing import Callable, Literal, Mapping, Sequence


@dataclass(frozen=True)
class Lane:
    id: str
    referent: str
    parents: tuple[str, ...] = ()
    status: Literal["READY", "ACTIVE", "COMPLETE", "UNKNOWN", "BLOCKED"] = "READY"


@dataclass(frozen=True)
class Observation:
    id: str
    lane_id: str
    kind: Literal["BRANCH", "RELATION"]
    relation: str
    witness_ref: str
    capability: str = ""
    sequence: int = 0  # native journal ordering, NOT elapsed time


@dataclass(frozen=True)
class Proposal:
    id: str
    kind: Literal["BIRTH", "CONNECTION", "OPEN_UNSTAFFED"]
    parents: tuple[str, ...]
    observation_ids: tuple[str, ...]
    capability: str
    worker_edition: str | None
    relation: str
    reason: str


EvidenceVerifier = Callable[[Observation], bool]
ConnectionVerifier = Callable[[Observation, Observation], bool]


def _identifier(*parts: str) -> str:
    return sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:24]


def propose_movements(
    *,
    lanes: Sequence[Lane],
    observations: Sequence[Observation],
    worker_editions: Mapping[str, str],
    verify_observation: EvidenceVerifier,
    verify_connection: ConnectionVerifier,
    admitted_proposal_ids: frozenset[str] = frozenset(),
    max_new_lanes: int = 4,
    max_total_lanes: int = 32,
) -> tuple[Proposal, ...]:
    """Review all witnessed openings without claiming execution or checkpoint PASS."""
    if max_new_lanes < 0 or max_total_lanes < 0:
        raise ValueError("lane bounds must be nonnegative")
    known_lanes = {lane.id: lane for lane in lanes}
    if len(known_lanes) != len(lanes) or any(
        not x.id.strip() or not x.referent.strip() for x in lanes
    ):
        raise ValueError("duplicate or malformed lane")
    if len(known_lanes) > max_total_lanes:
        raise ValueError("existing lanes already exceed declared capacity")
    seen_obs: set[str] = set()
    validated: list[Observation] = []
    for o in sorted(observations, key=lambda e: (e.sequence, e.id)):
        if (not o.id.strip() or o.id in seen_obs or o.lane_id not in known_lanes
                or not o.relation.strip() or not o.witness_ref.strip()
                or o.sequence < 0 or o.kind not in ("BRANCH", "RELATION")):
            raise ValueError("duplicate, unsupported, or malformed observation")
        seen_obs.add(o.id)
        if o.kind == "BRANCH" and not o.capability.strip():
            raise ValueError("branch requires explicit capability")
        # Source-backed verifier is supplied by the caller. Fail closed.
        if verify_observation(o):
            validated.append(o)

    proposals: list[Proposal] = []
    births = 0
    free_capacity = max(0, min(max_new_lanes, max_total_lanes - len(lanes)))

    def offer(kind: Literal["BIRTH", "CONNECTION"], parents: tuple[str, ...],
              sources: tuple[Observation, ...], capability: str, relation: str) -> None:
        nonlocal births
        ids = tuple(o.id for o in sources)
        key = _identifier(kind, *parents, *ids, capability, relation)
        if key in admitted_proposal_ids:
            return
        worker = worker_editions.get(capability)
        if not worker:
            proposals.append(Proposal(
                key, "OPEN_UNSTAFFED", parents, ids, capability, None, relation,
                "No registered source-pinned capable worker; preserve opening."
            ))
            return
        if births >= free_capacity:
            return
        births += 1
        proposals.append(Proposal(
            key, kind, parents, ids, capability, worker, relation,
            "Native admission required; this proposal is not executed or witnessed."
        ))

    for obs in validated:
        if obs.kind == "BRANCH":
            offer("BIRTH", (obs.lane_id,), (obs,), obs.capability, obs.relation)

    relations = [o for o in validated if o.kind == "RELATION"]
    for a, b in combinations(relations, 2):
        if a.lane_id == b.lane_id or a.relation != b.relation:
            continue
        left, right = sorted((a, b), key=lambda o: (o.lane_id, o.id))
        # Text equality is NOT a join witness.
        if not verify_connection(left, right):
            continue
        offer("CONNECTION", (left.lane_id, right.lane_id), (left, right),
              "relation-connector", left.relation)

    return tuple(proposals)
