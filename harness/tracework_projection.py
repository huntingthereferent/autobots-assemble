"""Read-only mathematical projection over existing Tracework handoffs and events.

No worker execution, journal writes, probabilistic-model or stability claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine import HandoffRuntime


@dataclass(frozen=True)
class Transition:
    event_id: str
    handoff_id: str
    event_type: str
    actor: str
    occurred_at: str
    parents: tuple[str, ...]
    status_after: str


@dataclass(frozen=True)
class Mismatch:
    handoff_id: str
    expected: dict[str, Any]
    observed: dict[str, Any]
    missing_keys: tuple[str, ...]
    differing_keys: tuple[str, ...]
    missing_witnesses: tuple[str, ...]
    blocked_by: tuple[str, ...]
    status: str


def compare_handoff(runtime: HandoffRuntime, handoff_id: str) -> Mismatch:
    """Compare only declared expected-output keys; no inferred semantics.

    Nonterminal states have no final observation and must not be called a
    successful match. Witness requirements remain separate from output match.
    """
    handoff = runtime.get(handoff_id)
    state = runtime.state(handoff_id)
    expected = dict(handoff.expected_output)
    observed = dict(state.output)
    terminal = state.status in {"COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"}
    missing = tuple(k for k in expected if terminal and k not in observed)
    differing = tuple(
        k for k in expected if terminal and k in observed and expected[k] != observed[k]
    )
    return Mismatch(
        handoff_id=handoff_id,
        expected=expected,
        observed=observed,
        missing_keys=missing,
        differing_keys=differing,
        missing_witnesses=state.missing_witnesses,
        blocked_by=state.blocked_by,
        status=state.status,
    )


def project(runtime: HandoffRuntime) -> dict[str, Any]:
    """Snapshot native handoffs, event transitions, relations and comparisons."""
    handoffs = runtime.snapshot()
    events = runtime.event_store.all()
    known_events = {event.event_id for event in events}
    # Project event-local movement without modifying the journal.
    # Historical dependency resolution cannot be recovered from event order
    # alone; mark such states rather than inventing them.
    last_status: dict[str, str] = {}
    transitions_list = []
    for e in events:
        if e.event_type == "CREATED":
            status = "DEPENDENCY_DEPENDENT" if runtime.get(e.handoff_id).dependencies else "READY"
        elif e.event_type == "STARTED":
            status = "ACTIVE"
        elif e.event_type == "RESULT":
            status = str(e.data["status"])
        elif e.event_type == "REOPENED":
            status = "DEPENDENCY_DEPENDENT" if runtime.get(e.handoff_id).dependencies else "READY"
        else:
            status = last_status.get(e.handoff_id, "UNSPECIFIED")
        last_status[e.handoff_id] = status
        transitions_list.append(Transition(
            event_id=e.event_id,
            handoff_id=e.handoff_id,
            event_type=e.event_type,
            actor=e.actor_id,
            occurred_at=e.occurred_at,
            parents=e.parents,
            status_after=status,
        ))
    transitions = tuple(transitions_list)
    return {
        "states": {hid: handoffs[hid].status for hid in handoffs},
        "transitions": transitions,
        "relations": {
            hid: {
                "dependencies": runtime.get(hid).dependencies,
                "required_relation": runtime.get(hid).required_relation,
                "boundaries": runtime.get(hid).boundaries,
            }
            for hid in handoffs
        },
        "mismatches": {hid: compare_handoff(runtime, hid) for hid in handoffs},
        "unresolved_parent_ids": tuple(
            (e.event_id, parent)
            for e in events for parent in e.parents if parent not in known_events
        ),
    }
