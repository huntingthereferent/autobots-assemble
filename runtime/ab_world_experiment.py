"""Witness-bounded simulation of proposed worlds for the SAME A/B mathematics.

The simulator actually executes caller-supplied transitions, then lets
runtime.ab_information discover categories from their returned traces.
These are SIMULATED observations; they are NEVER native EvidenceRecords
and can never become a live agent MOVE via this module.

This module is deliberately independent of an ARC game or maze renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Iterable, Literal, Mapping

from .ab_information import (
    ABOccurrence, ABInformationState, SynthesizedRelation,
    information_closure, synthesize_continuation_relation,
)
from .ab_construction import ConstructionProposal


@dataclass(frozen=True)
class SimulationWorld:
    """Explicitly *simulated* mechanics, never a native witness adapter."""

    source: str
    initial: Callable[[Mapping[str, Any]], Any]
    step: Callable[[Any, Any], Any]
    observe: Callable[[Any], Any]
    relations: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    kind: Literal["simulation"] = "simulation"


@dataclass(frozen=True)
class SimulatedTrial:
    proposal_id: str
    original_category: int
    source_locators: tuple[str, ...]
    action_path: tuple[Any, ...]
    before: Any
    observed: tuple[Any, ...]
    predicted: tuple[Any, ...] | None
    trace_locator: str
    status: Literal[
        "SIMULATED_MATCH", "SIMULATED_COUNTEREXAMPLE",
        "SIMULATED_UNPREDICTED", "UNKNOWN",
    ]
    reason: str = ""


@dataclass(frozen=True)
class WorldExperiment:
    """Complete trace plus A/B quotient if EVERY candidate returned a trace."""

    referent: Any
    source: str
    action_path: tuple[Any, ...]
    witness_contract: str
    trials: tuple[SimulatedTrial, ...]
    information: ABInformationState | None
    synthesized: SynthesizedRelation | None
    complete: bool
    # Only a FULL, repeatable trial set may return the next A/B input.
    observed_occurrences: tuple[ABOccurrence, ...] = ()
    observed_locators: tuple[str, ...] = ()
    unresolved_boundary: str = ""
    evidence_kind: Literal["simulation"] = "simulation"


Predictor = Callable[[ConstructionProposal, tuple[Any, ...]], Iterable[Any] | None]


def _portable(value: Any) -> str:
    """Do not silently convert executable/opaque objects into evidence."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def run_simulation_probe(
    proposals: Iterable[ConstructionProposal],
    *,
    world: SimulationWorld,
    action_path: Iterable[Any],
    predict: Predictor | None = None,
    max_candidates: int = 128,
    max_actions: int = 12,
) -> WorldExperiment:
    """Run one action path on distinct proposals using an explicit simulator.

    Two independent initializations/replays must agree exactly; divergent
    replays or unavailable transitions yield UNKNOWN, no constructed
    continuation category. Predictions are optional hypotheses; A/B uses
    actual model returns, even when those hypotheses are contradicted.

    No AgentLineage, evidence admission, storage mutation, or outside
    environment access occurs here. The injected world may execute local
    simulation code; its trust is the caller's responsibility.
    """
    candidates = tuple(proposals)
    actions = tuple(action_path)
    if world.kind != "simulation" or not world.source.strip():
        raise ValueError("world must declare a simulation source")
    if not candidates or not 1 <= len(candidates) <= max_candidates <= 1000:
        raise ValueError("invalid candidate count or cap")
    if not 1 <= len(actions) <= max_actions <= 128:
        raise ValueError("action path must be bounded and nonempty")
    if any(p.status != "PROPOSED" for p in candidates):
        raise ValueError("only unverified construction proposals can be simulated")
    if len({p.proposal_id for p in candidates}) != len(candidates):
        raise ValueError("duplicate proposal identity")
    referent = candidates[0].referent
    contract = candidates[0].witness_contract
    if any(p.referent != referent or p.witness_contract != contract for p in candidates):
        raise ValueError("all candidate experiments require one referent and source contract")
    _portable(actions)

    trial_results: list[SimulatedTrial] = []
    observations: list[ABOccurrence] = []
    complete = True
    for proposal in candidates:
        reason = ""
        before: Any = None
        observed: tuple[Any, ...] = ()
        prediction: tuple[Any, ...] | None = None
        try:
            if predict is not None:
                proposed = predict(proposal, actions)
                if proposed is not None:
                    prediction = tuple(proposed)
                    _portable(prediction)
                    if len(prediction) != len(actions):
                        raise ValueError("prediction must contain one return per action")

            def replay() -> tuple[Any, tuple[Any, ...]]:
                state = world.initial(dict(proposal.structure))
                first = world.observe(state)
                trace = []
                for action in actions:
                    state = world.step(state, action)
                    trace.append(world.observe(state))
                _portable((first, trace))
                return first, tuple(trace)

            before, observed = replay()
            duplicate_before, duplicate_observed = replay()
            if before != duplicate_before or observed != duplicate_observed:
                raise ValueError("simulation repeated differently; no deterministic quotient")
            relations = dict(world.relations(dict(proposal.structure)))
            _portable(relations)
            observations.append(ABOccurrence.create(
                referent=referent, relations=relations, continuation=observed,
            ))
            if prediction is None:
                status = "SIMULATED_UNPREDICTED"
            elif prediction == observed:
                status = "SIMULATED_MATCH"
            else:
                status = "SIMULATED_COUNTEREXAMPLE"
        except Exception as exc:
            # This is deliberately one UNKNOWN trial rather than a fabricated
            # comparison. No subquotient is promoted from incomplete coverage.
            complete = False
            status = "UNKNOWN"
            reason = f"{type(exc).__name__}: {exc}"
            before = None
            observed = ()
        trace_payload = {
            "kind": "simulation",
            "source": world.source,
            "proposal": proposal.proposal_id,
            "actions": actions,
            "before": before,
            "observed": observed,
            "status": status,
        }
        loc = "simulation://sha256/" + sha256(_portable(trace_payload).encode()).hexdigest()
        trial_results.append(SimulatedTrial(
            proposal_id=proposal.proposal_id,
            original_category=proposal.category,
            source_locators=proposal.source_locators,
            action_path=actions,
            before=before,
            observed=observed,
            predicted=prediction,
            trace_locator=loc,
            status=status,
            reason=reason,
        ))

    info = None
    synthetic = None
    boundary = ""
    if complete:
        try:
            info = information_closure(observations)
            synthetic = synthesize_continuation_relation(info)
        except ValueError as exc:
            # Observed futures may diverge while the currently available
            # input relations cannot explain them. That is an explicit
            # vocabulary/contract wall, not permission to invent a relation.
            boundary = f"witnessed continuation requires missing relation: {exc}"
    else:
        boundary = "one or more simulations did not yield repeatable observations"
    return WorldExperiment(
        referent=referent,
        source=world.source,
        action_path=actions,
        witness_contract=contract,
        trials=tuple(trial_results),
        information=info,
        synthesized=synthetic,
        complete=complete,
        observed_occurrences=tuple(observations) if complete and info is not None else (),
        observed_locators=(
            tuple(t.trace_locator for t in trial_results)
            if complete and info is not None else ()
        ),
        unresolved_boundary=boundary,
    )
