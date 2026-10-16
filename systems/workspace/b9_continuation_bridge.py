"""B10: bounded, opt-in B9 candidate -> event-driven native observation.

Construction remains proposal-only. A bridge handoff is a separate request for
ONE route-scoped candidate relation and ONE explicitly authorized source edition.
Preparing it cannot start a worker. Only a source-verified LOCAL_PASS event can
ask the existing ObservedEventJournal to attempt the native adapter.

The journal must have a separate file from B9's construction journal. Neither
journal supplies process locks, owner authentication, or a production scheduler.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Callable

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from systems.workspace.observed_event_journal import LOCAL_PASS, ObservedEventJournal
from systems.workspace.workstation_construction import (
    WorkstationConstruction, _digest,
)

BRIDGE_SOURCE = "b9-route-scoped-native-attempt/v1"
BOUNDARIES = (
    "B9 construction is a proposal, not authorization or source evidence.",
    "Only a trusted external LOCAL_PASS verifier may trigger a native attempt.",
    "Native observation is scoped to the chosen candidate, never the entire route.",
    "B2/B3/B7/B8 admission and native source-owner checks remain independent.",
)


def _validate_scope(graph: WorkstationConstruction, handoff: Handoff) -> bool:
    """Compare an immutable bridge contract to the CURRENT B9 construction.

    Route IDs include intermediate nodes. Source hints are never treated as
    permission. This does not recheck source ownership; that belongs to the
    explicit native adapter and independent local-result verifier.
    """
    meta = handoff.metadata
    if meta.get("source_system") != BRIDGE_SOURCE:
        return False
    route = meta.get("construction_route")
    bound = meta.get("continuation_source_binding")
    if (not isinstance(route, list) or len(route) < 2
            or any(not isinstance(node_id, str) or not node_id for node_id in route)
            or len(set(route)) != len(route)
            or not isinstance(bound, dict) or set(bound) != {"name", "edition"}
            or any(not isinstance(bound[k], str) or not bound[k] for k in bound)):
        return False
    goal_id = meta.get("construction_goal_id")
    candidate_id = meta.get("construction_candidate_id")
    source_locator = meta.get("source_locator")
    if (not isinstance(goal_id, str) or not isinstance(candidate_id, str)
            or not isinstance(source_locator, str) or not source_locator
            or candidate_id not in route[:-1] or route[-1] != goal_id):
        return False
    try:
        native = graph._node(graph._runtime(), candidate_id)
        if (native.metadata.get("node_kind") != "CANDIDATE"
                or native.metadata.get("goal_id") != goal_id
                or meta.get("candidate_spec_sha256") != _digest(asdict(native))
                or handoff.required_relation != native.referent):
            return False
        frontier = graph.next_construction_handoffs(goal_id)
    except (KeyError, ValueError, TypeError):
        return False
    for leaf in frontier["construction_handoffs"]:
        for scoped in leaf["routes_with_observational_context"]:
            if tuple(route) != scoped["candidate_ids"]:
                continue
            if scoped["whole_route_verified"] or scoped["execution_authorized"]:
                return False
            for step in scoped["steps"]:
                if step["upstream_id"] != candidate_id:
                    continue
                return any(
                    hint["worker_id"] == bound["name"]
                    and hint["edition_ref"] == bound["edition"]
                    and hint["source_locator"] == source_locator
                    and hint["execution_authorized"] is False
                    for hint in step["suggested_sources"]
                )
    return False


def scoped_local_verifier(
    construction: WorkstationConstruction,
    verify_native_local_result: Callable[[Handoff, HandoffEvent], bool],
) -> Callable[[Handoff, HandoffEvent], bool]:
    """Wrap the caller's independent local-result verifier with B9 scope checks.

    Do not accept an actor label, local test result, saved receipt, or B9 source
    suggestion as proof. The caller must independently verify the LOCAL_PASS.
    """
    if not isinstance(construction, WorkstationConstruction):
        raise TypeError("a B9 construction source is required")
    if not callable(verify_native_local_result):
        raise TypeError("independent local-result verifier is required")

    def verify(handoff: Handoff, event: HandoffEvent) -> bool:
        if event.handoff_id != handoff.handoff_id or event.event_type != LOCAL_PASS:
            return False
        if not _validate_scope(construction, handoff):
            return False
        try:
            return verify_native_local_result(handoff, event) is True
        except Exception:
            return False

    # Scope identity is a guard against accidentally wiring a generic local
    # result verifier into a B9 attempt journal. It is not an owner signature.
    verify._b9_construction_path = construction.data_dir.resolve()
    return verify


class B9ContinuationBridge:
    """Create an inert, source-bound attempt request for one exact B9 route step."""

    def __init__(self, construction: WorkstationConstruction,
                 journal: ObservedEventJournal):
        if not isinstance(construction, WorkstationConstruction):
            raise TypeError("a B9 construction source is required")
        if not isinstance(journal, ObservedEventJournal):
            raise TypeError("the real observed event journal is required")
        if journal.path.resolve() == (construction.data_dir / "runtime.jsonl").resolve():
            raise ValueError("construction and attempt journals must be separate")
        if (getattr(journal.verify_local_pass, "_b9_construction_path", None)
                != construction.data_dir.resolve()):
            raise ValueError("B9-scoped independent local-result verifier is required")
        self.construction = construction
        self.journal = journal

    def prepare(self, goal_id: str, candidate_id: str, *,
                route: tuple[str, ...], worker_id: str,
                edition_ref: str, source_locator: str) -> str:
        """Explicitly request observation; NEVER emit LOCAL_PASS or execute.

        The worker/edition must be both a B9 source hint AND a separately
        authorized adapter whose claims include the exact candidate relation.
        A shared candidate in two routes produces two different requests.
        """
        if (not isinstance(route, tuple) or len(route) < 2
                or any(not isinstance(x, str) or not x for x in route)
                or not all(isinstance(x, str) and x for x in
                           (goal_id, candidate_id, worker_id, edition_ref, source_locator))):
            raise ValueError("complete route and exact source identity are required")
        if not any(
            adapter.capability.name == worker_id
            and adapter.capability.edition == edition_ref
            and adapter.capability.authorized is True
            for adapter in self.journal.adapters
        ):
            raise ValueError("B9 source hint does not authorize a native adapter")
        native = self.construction._node(self.construction._runtime(), candidate_id)
        if (native.metadata.get("node_kind") != "CANDIDATE"
                or native.metadata.get("goal_id") != goal_id):
            raise ValueError("bridge requires a candidate belonging to this goal")
        if not any(
            adapter.capability.name == worker_id
            and adapter.capability.edition == edition_ref
            and native.referent in adapter.capability.claims
            and adapter.capability.authorized is True
            for adapter in self.journal.adapters
        ):
            raise ValueError("authorized source does not claim the candidate relation")
        digest = _digest(asdict(native))
        identity = _digest((goal_id, candidate_id, route, digest,
                            worker_id, edition_ref, source_locator))
        handoff = Handoff(
            handoff_id="b9attempt-" + identity[:32],
            referent=native.referent,
            from_actor="b9-observation-request",
            to_actor="source-owned-native-adapter",
            required_relation=native.referent,
            inputs={"candidate_spec_sha256": digest, "source_locator": source_locator},
            expected_output={"scope": "one candidate-local observation, not route proof"},
            provenance=tuple(native.provenance) + ("b9-route:" + _digest(route),),
            boundaries=BOUNDARIES,
            metadata={
                "source_system": BRIDGE_SOURCE,
                "construction_goal_id": goal_id,
                "construction_candidate_id": candidate_id,
                "construction_route": list(route),
                "candidate_spec_sha256": digest,
                "source_locator": source_locator,
                "continuation_source_binding": {"name": worker_id, "edition": edition_ref},
                "whole_route_verified": False,
                "execution_approved_by_construction": False,
            },
        )
        if not _validate_scope(self.construction, handoff):
            raise ValueError("B9 route step or exact source hint is not present")
        runtime = HandoffRuntime(event_store=self.journal)
        if handoff.handoff_id in runtime._handoffs:
            if runtime.get(handoff.handoff_id) != handoff:
                raise ValueError("bridge request identity collision")
            return handoff.handoff_id
        runtime.submit(handoff)
        return handoff.handoff_id

    def projection(self, handoff_id: str) -> dict:
        handoff = HandoffRuntime(event_store=self.journal).get(handoff_id)
        if handoff.metadata.get("source_system") != BRIDGE_SOURCE:
            raise ValueError("not a B9 continuation request")
        result = dict(self.journal.projection(handoff_id))
        result.update({
            "candidate_id": handoff.metadata["construction_candidate_id"],
            "route": tuple(handoff.metadata["construction_route"]),
            "whole_route_verified": False,
            "join_observed": False,
            "handoff_complete": False,
        })
        return result
