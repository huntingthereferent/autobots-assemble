"""B5: source-owned CP30 live-observation adapter to B4's unstaffed need.

This adapter does not fabricate live task objects or promote a finite prefilter
to a correspondence theorem. Trusted owner-supplied callbacks are required.
It adds no scheduler, repository network access, or generic coding agent.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Callable, Mapping, Any
import json
import re

from runtime.handoff import HandoffEvent
from .workstation_native_feedback import canonical_digest
from .workstation_return_continuation import _DERIVED

_RESULT_EVENT = "WORKSTATION_OWNER_NATIVE_LOCAL_TASK_AUDITED"
_BOUND_CAP = "owner-native-correspondence-witness"
_CANDIDATE = re.compile(
    r"Acquire owner-native evidence for unresolved candidate ([0-9]+) of job (.+)\\Z"
)


@dataclass(frozen=True)
class OwnerNativeAuditReturn:
    lane_handoff_id: str
    job_id: str
    task_name: str
    candidate_index: int
    source_evidence_sha256: str
    recorded_new_event: bool
    status: str = "NATIVE_LOCAL_TASK_AUDITED_NOT_EXTERNAL_PROOF"


class WorkstationOwnerNativeObserver:
    """Owner-provided live task callback and candidate-to-task binding.

    The separate verify_candidate_binding callback must be implemented by an
    authorized, trusted source controller and must inspect the *exact* native
    task/candidate relation. A callback returning True in a fixture only proves
    the integration route; it is not externally authenticated ownership.
    """

    def __init__(self, b4, *, native_source_root: str | Path,
                 source_capture: Callable[[], Mapping[str, Any]],
                 verify_candidate_binding: Callable[[Any, str, Mapping[str, Any]], bool]):
        if not callable(source_capture) or not callable(verify_candidate_binding):
            raise ValueError("live owner source and independent candidate binding callbacks required")
        self.b4 = b4
        self.harness = b4.harness
        self.native_source_root = Path(native_source_root)
        self.source_capture = source_capture
        self.verify_candidate_binding = verify_candidate_binding

    def _fresh_source(self, lane_handoff_id: str, task_name: str):
        from .native_owner_observation import observe_native_owners

        # B4 reopens B3, validates the exact native finite worker, source
        # fingerprint, original witnessed branch, and domain relation policy.
        view = self.b4._view(lane_handoff_id)
        move = self.b4._candidate(view)
        if move is None or move.kind != "BRANCH" or move.capability != _BOUND_CAP:
            raise ValueError("no admitted owner-native observation need")
        match = _CANDIDATE.fullmatch(move.relation)
        if match is None or match.group(2) != view.job_id:
            raise ValueError("owner-native request is not bound to one native job")
        candidate_index = int(match.group(1))
        verdicts = view.result.get("verdicts")
        if (type(verdicts) is not list or candidate_index >= len(verdicts)
                or verdicts[candidate_index] not in ("NOT_CONTRADICTED", "UNDECIDED")):
            raise ValueError("candidate is contradicted, absent or out of bounds")

        runtime = self.harness._runtime()
        lane = runtime.get(lane_handoff_id)
        events = runtime.event_store.for_handoff(lane_handoff_id)
        derived = [e for e in events if e.event_type == _DERIVED]
        if len(derived) != 1:
            raise ValueError("B4 relation not admitted into the journal")
        row = derived[0].data
        originals = [o for o in self.harness._snapshot()[3]
                     if o.id == row.get("observation_id")]
        if len(originals) != 1 or not self.b4.verify_observation(originals[0]):
            raise ValueError("B4 source-derived relation no longer freshly witnessed")
        openings = [e for e in events
                    if e.event_type == "WORKSTATION_HELP_OPEN"
                    and e.data.get("capability") == _BOUND_CAP]
        if len(openings) != 1:
            raise ValueError("the native observation need is not recorded as unstaffed")

        # This is the actual source-native CP30 observer, not a JSON mock.
        report = observe_native_owners(
            native_source_root=self.native_source_root,
            source_capture=self.source_capture,
            allow_native_audit=True,
        )
        if (report.get("status") != "NATIVE_LOCAL_ROUTE_FRESHLY_REAUDITED"
                or report.get("local_owner_pins_verified") is not True
                or report.get("same_live_native_objects_recaptured") is not True
                or report.get("fresh_native_two_pass_route_audit") is not True
                or report.get("external_owner_identity_authenticated") is not False
                or report.get("external_signed_observation_mapped_to_native") is not False
                or report.get("cp30_independent_process_attestation_verified") is not False
                or report.get("new_transition_observations") is not False
                or report.get("runtime_handoff_admitted") is not False):
            raise ValueError("native owner audit lacks the required bounded source proof")
        answers = [x for x in report.get("task_results", ())
                   if x.get("name") == task_name]
        if (len(answers) != 1
                or answers[0].get("status") != "TASK_COMPLETED_ON_SELECTED_ROUTE"
                or answers[0].get("all_obligations_admitted") is not True
                or task_name not in report.get("tasks", ())):
            raise ValueError("selected native owner task is not witnessed complete")
        if self.verify_candidate_binding(view, task_name, report) is not True:
            raise ValueError("finite candidate has no separately bound native owner task")

        return view, move, candidate_index, report, lane

    def inspect(self, lane_handoff_id: str, *, task_name: str) -> dict:
        """No journal writes; actual native CP30 double-capture and audit."""
        view, move, index, report, _ = self._fresh_source(lane_handoff_id, task_name)
        return {"job_id": view.job_id, "task_name": task_name,
                "candidate_index": index,
                "local_evidence_sha256": report["local_evidence_sha256"],
                "route": report["route"], "route_fingerprint": report["route_fingerprint"],
                "native_task_completed": True, "external_identity_proven": False,
                "finite_candidate_edge_proven": False,
                "runtime_job_started": False, "journal_modified": False}

    def record(self, lane_handoff_id: str, *, task_name: str,
               allow_native_record: bool = False) -> OwnerNativeAuditReturn:
        """Explicitly record a locally witnessed source-owner task, not an edge."""
        if not allow_native_record:
            raise PermissionError("explicit native-local observation record approval required")
        view, move, index, report, lane = self._fresh_source(lane_handoff_id, task_name)
        payload = {
            "job_id": view.job_id,
            "output_sha256": view.output_sha256,
            "source_fingerprint": view.source_fingerprint,
            "candidate_index": index,
            "task_name": task_name,
            "native_route": report["route"],
            "route_fingerprint": report["route_fingerprint"],
            "local_evidence_sha256": report["local_evidence_sha256"],
            "native_report_sha256": canonical_digest(report),
            "claim_scope": "native-local CP30 selected task audited, owner-provided candidate binding",
            "external_owner_identity_authenticated": False,
            "finite_prefilter_edge_proven": False,
            "parent_cp_witnessed": False,
        }
        runtime = self.harness._runtime()
        prior = [e for e in runtime.event_store.for_handoff(lane_handoff_id)
                 if e.event_type == _RESULT_EVENT]
        for e in prior:
            if e.data.get("job_id") == view.job_id and e.data.get("candidate_index") == index:
                if e.data != payload:
                    raise ValueError("live native evidence changed; historical receipt preserved")
                return OwnerNativeAuditReturn(
                    lane_handoff_id, view.job_id, task_name, index,
                    report["local_evidence_sha256"], False)
        state = runtime.state(lane_handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=lane_handoff_id, event_type=_RESULT_EVENT,
            actor_id="workstation-native-owner-local-observer",
            data=payload,
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        return OwnerNativeAuditReturn(
            lane_handoff_id, view.job_id, task_name, index,
            report["local_evidence_sha256"], True)

    def recorded(self, lane_handoff_id: str) -> tuple[dict, ...]:
        """Historical claims only. For freshness, call inspect() again."""
        return tuple(dict(e.data) for e in
                     self.harness._runtime().event_store.for_handoff(lane_handoff_id)
                     if e.event_type == _RESULT_EVENT)
