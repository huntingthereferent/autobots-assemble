"""B3: native worker execution and verified return feedback to the same journal.

No new scheduler, no model-backed worker claims, and no checkpoint promotion.
A retained result is a historical observation, not a new branch admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable
import json

_RETURN_EVENT = "WORKSTATION_NATIVE_RESULT_VERIFIED"
_ASSIGN_EVENT = "WORKSTATION_NATIVE_HELP_ASSIGNED"


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(raw.encode("utf8")).hexdigest()


@dataclass(frozen=True)
class NativeReturn:
    coordination_handoff_id: str
    opening_id: str
    job_id: str
    output_sha256: str
    evidence_sha256: str
    recorded_new_event: bool
    checkpoint_pass: bool = False


class WorkstationNativeFeedback:
    """One explicitly invoked native job and independently verified feedback.

    The caller must pass the repository's actual controls.run_job and
    branch_help.verify_return for a native integration claim. Injection permits
    isolated unit tests but does not establish native source authority.
    """

    def __init__(self, harness, *, run_job: Callable[..., dict],
                 verify_return: Callable[..., dict]):
        if not callable(run_job) or not callable(verify_return):
            raise TypeError("native run and independent return verifier are required")
        self.harness = harness
        self.run_job = run_job
        self.verify_return = verify_return

    def advance(self, coordination_handoff_id: str, *, confirm_execute: str,
                allow_local_execution: bool = False) -> NativeReturn:
        admission = self.harness.admit_native_help(
            coordination_handoff_id, allow_native_admission=False)
        native = admission["native_help"]
        assigned = native.get("child")
        if not assigned or native.get("state") == "OPEN_UNSTAFFED":
            raise ValueError("no registered source-owned native worker admitted")
        job_id = assigned["job_id"]
        opening_id = native["opening_id"]
        if not allow_local_execution:
            raise PermissionError("explicit local native execution approval required")
        if confirm_execute != job_id:
            raise PermissionError("exact native job ID confirmation required")
        runtime = self.harness._runtime()
        handoff = runtime.get(coordination_handoff_id)
        if handoff.metadata.get("source_system") != "workstation-continuation-lane/v1":
            raise ValueError("not a B2 coordination lane")
        if len(handoff.metadata.get("parents", ())) != 1:
            raise ValueError("this native helper is not a single-parent branch")
        assigned_events = [e for e in runtime.event_store.for_handoff(coordination_handoff_id)
                           if e.event_type == _ASSIGN_EVENT]
        if len(assigned_events) != 1 or assigned_events[0].data != {
                "opening_id": opening_id, "job_id": job_id}:
            raise ValueError("missing or ambiguous native assignment evidence")
        if runtime.state(job_id).status not in ("READY", "COMPLETE"):
            raise ValueError("native job is not in an executable or completed state")

        run = self.run_job(data_dir=self.harness.data_dir, job_id=job_id,
                           confirm_execute=confirm_execute)
        if (run.get("job_id") != job_id or run.get("status") != "COMPLETE"
                or run.get("reverified") is not True):
            raise ValueError("native execution did not return verified completion")
        confirmed = self.verify_return(data_dir=self.harness.data_dir,
                                       opening_id=opening_id)
        if (confirmed.get("state") != "RETURN_RECORDED_REVERIFY_BEFORE_USE"
                or confirmed.get("parent_cp_witnessed") is not False
                or confirmed.get("child", {}).get("job_id") != job_id):
            raise ValueError("source-owned helper return not independently verified")

        runtime = self.harness._runtime()
        state = runtime.state(job_id)
        native_job = runtime.get(job_id)
        if state.status != "COMPLETE":
            raise ValueError("verified native job state is not COMPLETE")
        output_sha256 = canonical_digest(state.output)
        evidence_sha256 = canonical_digest([getattr(e, "__dict__", {}) for e in state.evidence])
        source_fp = native_job.metadata.get("edition_fingerprint")
        if not isinstance(source_fp, str) or not source_fp:
            raise ValueError("native job missing source edition fingerprint")
        payload = {"opening_id": opening_id, "job_id": job_id,
                   "output_sha256": output_sha256, "evidence_sha256": evidence_sha256,
                   "source_fingerprint": source_fp,
                   "claim_scope": ("exact WORLD W13 two-room native helper return only"
                                   if assigned.get("worker_id") == "game-worlds-w13"
                                   else "source-owned native finite helper return only"),
                   "parent_cp_witnessed": False}
        prior = [e for e in runtime.event_store.for_handoff(coordination_handoff_id)
                 if e.event_type == _RETURN_EVENT]
        for record in prior:
            if record.data.get("job_id") == job_id:
                if record.data != payload:
                    raise ValueError("native job feedback conflict; keep historical event")
                return NativeReturn(coordination_handoff_id, opening_id, job_id,
                                    output_sha256, evidence_sha256, False)
        from runtime.handoff import HandoffEvent
        latest = runtime.state(coordination_handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=coordination_handoff_id,
            event_type=_RETURN_EVENT,
            actor_id="workstation-native-feedback",
            data=payload,
            parents=(latest.last_event_id,) if latest.last_event_id else (),
        ))
        return NativeReturn(coordination_handoff_id, opening_id, job_id,
                            output_sha256, evidence_sha256, True)

    def historical_returns(self, coordination_handoff_id: str) -> tuple[dict, ...]:
        """Read-only projection of past results, not an independent reverify."""
        events = self.harness._runtime().event_store.for_handoff(coordination_handoff_id)
        return tuple(dict(e.data) for e in events if e.event_type == _RETURN_EVENT)
