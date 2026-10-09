"""Opt-in inverse-category construction for the EXISTING A/B agent.

Forward A/B (runtime.ab_information) is untouched. This module uses its
witnessed continuation partition as a source-addressed inverse fiber,
projects bounded candidate structures, then returns those proposals in
the existing ABFrame shape for independent evaluation.

No candidate here is an observed movement. No new agent, evidence
admission, live source connector, or autonomous scheduler is created.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Iterable, Iterator, Literal, Mapping

from .ab_information import (
    ABOccurrence,
    ABInformationState,
    information_closure,
)
from .ab_loop import ABFrame


@dataclass(frozen=True)
class InverseFiber:
    """All witnessed source occurrences in one continuation class."""

    referent: Any
    category: int
    source_indices: tuple[int, ...]
    source_locators: tuple[str, ...]
    continuation: Any
    witness_contract: str
    horizon: int


@dataclass(frozen=True)
class ConstructionProposal:
    """A suggested realization, explicitly NOT a native observation."""

    proposal_id: str
    referent: Any
    category: int | None
    structure: dict[str, Any]
    source_indices: tuple[int, ...]
    source_locators: tuple[str, ...]
    witness_contract: str
    horizon: int
    status: Literal["PROPOSED"] = "PROPOSED"


@dataclass(frozen=True)
class WorldEdge:
    """A caller-provided transition; source trust is external."""

    before: Any
    action: Any
    after: Any
    source_locator: str = ""


@dataclass(frozen=True)
class CompositionCheck:
    """Structural math check; cannot admit native A/B movement."""

    status: Literal["MODEL_COMMUTES", "MODEL_SPLIT", "UNKNOWN"]
    edge: WorldEdge
    parent_before: Any = None
    projected_after: Any = None
    parent_after: Any = None
    reason: str = ""


def inverse_fibers(
    occurrences: Iterable[ABOccurrence],
    state: ABInformationState,
    *,
    source_locators: Iterable[str],
    witness_contract: str,
    horizon: int,
) -> tuple[InverseFiber, ...]:
    """Reverse the witnessed quotient without inventing source occurrences.

    The *caller* supplies independently verifiable source locators.
    Those strings are preserved, not validated or promoted by this
    mathematical function. A new continuation horizon needs new A/B.
    """
    group = tuple(occurrences)
    locators = tuple(source_locators)
    if not group or len(locators) != len(group):
        raise ValueError("one source locator is required for each witnessed occurrence")
    if not all(isinstance(s, str) and s.strip() for s in locators):
        raise ValueError("empty or invalid source locator")
    if not witness_contract.strip() or horizon < 1:
        raise ValueError("nonempty witness contract and positive horizon required")
    if information_closure(group) != state:
        raise ValueError("A/B state does not match the current witnessed occurrences")
    if len({i for b in state.continuation_partition for i in b}) != len(group):
        raise ValueError("continuation partition does not cover all witnesses")

    return tuple(
        InverseFiber(
            referent=state.referent,
            category=category,
            source_indices=tuple(indices),
            source_locators=tuple(locators[i] for i in indices),
            continuation=group[indices[0]].continuation,
            witness_contract=witness_contract,
            horizon=horizon,
        )
        for category, indices in enumerate(state.continuation_partition)
    )


Generator = Callable[[InverseFiber], Iterable[Mapping[str, Any]]]


def project_candidates(
    fibers: Iterable[InverseFiber],
    generator: Generator,
    *,
    intent: Literal["construct", "synthesize", "simulate", "alternatives"],
    max_candidates: int = 32,
) -> tuple[ConstructionProposal, ...]:
    """Round-robin bounded projection; output is always PROPOSED.

    Construction must be explicitly requested. Generator output is
    user/agent-supplied hypothetical structure, not witnessed evidence.
    A budget limits both return size and generator iteration.
    """
    if intent not in {"construct", "synthesize", "simulate", "alternatives"}:
        raise ValueError("inverse construction requires explicit construction intent")
    if not 1 <= max_candidates <= 1000:
        raise ValueError("max_candidates must be from 1 to 1000")
    sources = tuple(fibers)
    if not sources:
        return ()
    if len({(f.referent, f.category) for f in sources}) != len(sources):
        raise ValueError("duplicate source category")
    if not all(f.source_locators and f.witness_contract and f.horizon > 0 for f in sources):
        raise ValueError("unwitnessed inverse fiber")

    iters: tuple[Iterator[Mapping[str, Any]], ...] = tuple(iter(generator(f)) for f in sources)
    active = [True] * len(iters)
    out: list[ConstructionProposal] = []
    known: set[str] = set()
    # Also bound iteration when a generator endlessly repeats one candidate.
    attempts = 0
    max_attempts = max_candidates * max(4, len(sources) * 4)
    while any(active) and len(out) < max_candidates and attempts < max_attempts:
        for i, (fiber, proposals) in enumerate(zip(sources, iters)):
            if not active[i] or len(out) == max_candidates or attempts >= max_attempts:
                continue
            try:
                raw = next(proposals)
                attempts += 1
            except StopIteration:
                active[i] = False
                continue
            if not isinstance(raw, Mapping):
                raise TypeError("construction generator must yield mappings")
            structure = dict(raw)
            payload = {
                "referent": fiber.referent,
                "category": fiber.category,
                "source_indices": fiber.source_indices,
                "source_locators": fiber.source_locators,
                "witness_contract": fiber.witness_contract,
                "horizon": fiber.horizon,
                "structure": structure,
            }
            # Reject unportable objects rather than silently asserting a
            # stable witness/proposal identity using repr or default=str.
            serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            identity = sha256(serialized.encode("utf-8")).hexdigest()
            if identity in known:
                continue
            known.add(identity)
            out.append(ConstructionProposal(
                proposal_id=identity,
                referent=fiber.referent,
                category=fiber.category,
                structure=structure,
                source_indices=fiber.source_indices,
                source_locators=fiber.source_locators,
                witness_contract=fiber.witness_contract,
                horizon=fiber.horizon,
            ))
    return tuple(out)


def frame_for_candidate(proposal: ConstructionProposal) -> ABFrame:
    """Hand back to the ordinary A/B traversal WITHOUT claiming MOVE."""
    return ABFrame(
        referent=str(proposal.referent),
        direction="compare proposed construction against a native witness",
        current={
            "construction_status": "PROPOSED",
            "proposal_id": proposal.proposal_id,
            "category": proposal.category,
            "structure": dict(proposal.structure),
            "witness_contract": proposal.witness_contract,
            "prediction_horizon": proposal.horizon,
            "source_indices": list(proposal.source_indices),
            "source_locators": list(proposal.source_locators),
        },
        survives=("current referent", "source provenance", "witness contract"),
        edge=f"verify construction {proposal.proposal_id[:12]}",
        provenance=tuple(proposal.source_locators),
    )



def proposal_from_frame(frame: ABFrame) -> ConstructionProposal:
    """Rebuild and integrity-check an existing proposed ABFrame.

    This is *not* witness validation; it only prevents accidentally
    changing a candidate while retaining its deterministic proposal ID.
    """
    current = frame.current
    if current.get("category") is None and current.get("structure", {}).get("kind") != "cross-category-recombination":
        raise ValueError("unassigned category requires an exploratory proposal")
    if current.get("construction_status") != "PROPOSED":
        raise ValueError("ordinary A/B movements are not construction proposals")
    indices = tuple(current["source_indices"])
    locators = tuple(current["source_locators"])
    if not indices or not locators or len(indices) != len(locators):
        raise ValueError("construction source addresses are incomplete")
    payload = {
        "referent": frame.referent,
        "category": current["category"],
        "source_indices": indices,
        "source_locators": locators,
        "witness_contract": current["witness_contract"],
        "horizon": current["prediction_horizon"],
        "structure": current["structure"],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected_id = sha256(encoded.encode("utf-8")).hexdigest()
    if current.get("proposal_id") != expected_id:
        raise ValueError("construction proposal identity or provenance changed")
    if not str(payload["witness_contract"]).strip() or payload["horizon"] < 1:
        raise ValueError("construction proposal witness contract unavailable")
    return ConstructionProposal(
        proposal_id=expected_id,
        referent=frame.referent,
        category=current["category"],
        structure=dict(current["structure"]),
        source_indices=indices,
        source_locators=locators,
        witness_contract=current["witness_contract"],
        horizon=current["prediction_horizon"],
    )


def check_composition(
    edges: Iterable[WorldEdge],
    *,
    project: Callable[[Any], Any],
    parent_step: Callable[[Any, Any], Any],
    translate_action: Callable[[Any], Any],
) -> tuple[CompositionCheck, ...]:
    """Check q(T_child(s,a)) = T_parent(q(s),alpha(a)) per supplied edge.

    This is a MODELED commuting-square check. Even if the edge has a
    source locator, the caller must still supply valid native evidence to
    the existing evaluator before anything can become MOVE.
    """
    results = []
    for edge in edges:
        if not edge.source_locator:
            results.append(CompositionCheck(
                status="UNKNOWN", edge=edge, reason="no source locator",
            ))
            continue
        try:
            before = project(edge.before)
            expected = project(edge.after)
            actual = parent_step(before, translate_action(edge.action))
        except (KeyError, LookupError, NotImplementedError) as exc:
            results.append(CompositionCheck(
                status="UNKNOWN", edge=edge, reason=f"model relation unavailable: {exc}",
            ))
            continue
        results.append(CompositionCheck(
            status="MODEL_COMMUTES" if expected == actual else "MODEL_SPLIT",
            edge=edge,
            parent_before=before,
            projected_after=expected,
            parent_after=actual,
            reason="modeled relation agrees" if expected == actual
                   else "projection loses a necessary distinction",
        ))
    return tuple(results)
