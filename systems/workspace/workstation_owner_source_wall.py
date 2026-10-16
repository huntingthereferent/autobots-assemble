"""B6: preserve the missing independent owner/candidate relation, not a bot.

A real CP30 native-local audit is NOT proof that a finite-prefilter candidate
belongs to the same external owner or establishes a cross-lane join.
"""
from __future__ import annotations

from runtime.handoff import HandoffEvent
from .workstation_owner_native_observer import _RESULT_EVENT

WALL = "WORKSTATION_OWNER_CANDIDATE_BINDING_WALL"
MISSING = "INDEPENDENT_OWNER_CANDIDATE_BINDING_UNAVAILABLE"


class OwnerCandidateWall:
    def __init__(self, owner_observer):
        self.owner = owner_observer
        self.harness = owner_observer.harness

    def inspect(self, lane_handoff_id: str, task_name: str) -> dict:
        # Calls the actual CP30 two-pass source audit and B2/B3/B4 re-verifiers.
        view, _, index, report, _ = self.owner._fresh_source(
            lane_handoff_id, task_name)
        records = [e.data for e in
                   self.harness._runtime().event_store.for_handoff(lane_handoff_id)
                   if e.event_type == _RESULT_EVENT
                   and e.data.get("job_id") == view.job_id
                   and e.data.get("candidate_index") == index]
        if len(records) > 1:
            raise ValueError("ambiguous historical native owner audit")
        if records:
            old = records[0]
            if (old.get("task_name") != task_name
                    or old.get("native_route") != report["route"]
                    or old.get("route_fingerprint") != report["route_fingerprint"]
                    or old.get("local_evidence_sha256") != report["local_evidence_sha256"]
                    or old.get("output_sha256") != view.output_sha256
                    or old.get("source_fingerprint") != view.source_fingerprint):
                raise ValueError("native owner task changed since historical return")
        return {
            "lane_handoff_id": lane_handoff_id, "job_id": view.job_id,
            "candidate_index": index, "task_name": task_name,
            "native_local_audit_current": True,
            "status": MISSING, "external_owner_authenticated": False,
            "candidate_edge_proved": False, "join_witnessed": False,
            "worker_admitted": False
        }

    def preserve(self, lane_handoff_id: str, task_name: str) -> dict:
        view = self.inspect(lane_handoff_id, task_name)
        runtime = self.harness._runtime()
        recorded = [e.data for e in runtime.event_store.for_handoff(lane_handoff_id)
                    if e.event_type == _RESULT_EVENT
                    and e.data.get("job_id") == view["job_id"]
                    and e.data.get("candidate_index") == view["candidate_index"]]
        if len(recorded) != 1:
            raise ValueError("native-local B5 audit must first be recorded")
        payload = {
            "job_id": view["job_id"], "candidate_index": view["candidate_index"],
            "task_name": task_name,
            "native_audit_sha256": recorded[0]["native_report_sha256"],
            "missing_relation": MISSING,
            "new_lane_admitted": False, "join_witnessed": False,
            "external_owner_authenticated": False
        }
        old = [e for e in runtime.event_store.for_handoff(lane_handoff_id)
               if e.event_type == WALL and e.data.get("job_id") == view["job_id"]]
        if old:
            if len(old) != 1 or old[0].data != payload:
                raise ValueError("historic unresolved wall cannot be rewritten")
            return {**view, "recorded_new_event": False}
        latest = runtime.state(lane_handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=lane_handoff_id, event_type=WALL,
            actor_id="workstation-native-owner-continuation",
            data=payload,
            parents=(latest.last_event_id,) if latest.last_event_id else (),
        ))
        return {**view, "recorded_new_event": True}
