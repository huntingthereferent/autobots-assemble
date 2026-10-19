"""Agent-neutral access to existing source-owned workstation workers.

A model harness (Harness², ChatGPT, or another client) can ask for bounded
work and collect native returns. The caller's model/executor never becomes
the workstation's executor. This is an API adapter, not a scheduler.
"""
from __future__ import annotations

from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from .branch_help import help_status, open_and_staff_known, verify_return
from .controls import run_job
from .workstation import _safe_id

_CLIENT_EVENT = "WORKSTATION_CLIENT_REQUEST"


class WorkstationClient:
    """Thin client to the SAME coordinator, native workers, and RuntimeJournal.

    client_id is a provenance label, not authentication or execution authority.
    All real execution still requires the exact native job ID, an affirmative
    request, and the existing worker-specific controls.
    """

    def __init__(self, data_dir: str | Path, *, client_id: str):
        self.data_dir = Path(data_dir)
        self.client_id = _safe_id(client_id)

    def _runtime(self) -> HandoffRuntime:
        return HandoffRuntime(event_store=RuntimeJournal(self.data_dir / "runtime.jsonl"))

    def request_worker(
        self, *, lane: str, slot: str, capability: str, opening_key: str,
        reason: str, parent_version: str | None = None,
        inputs_file: str | Path | None = None,
        admit_registered: bool = False,
    ) -> dict:
        """Open exact help, optionally admit a registered worker; do not run it.

        Generic/unregistered capabilities stay OPEN_UNSTAFFED, never claim
        a worker exists. Existing source-pinned admissions are replay-safe.
        """
        status = open_and_staff_known(
            data_dir=self.data_dir, lane=lane, slot=slot,
            capability=capability, opening_key=opening_key, reason=reason,
            parent_version=parent_version, inputs_file=inputs_file,
            allow_native_admission=admit_registered,
        )
        runtime = self._runtime()
        opening_id = status["opening_id"]
        events = runtime.event_store.for_handoff(opening_id)
        expected = {"client_id": self.client_id, "capability": capability}
        recorded = [e for e in events if e.event_type == _CLIENT_EVENT
                    and e.data.get("client_id") == self.client_id]
        if recorded and any(e.data != expected for e in recorded):
            raise ValueError("client request provenance conflict")
        if not recorded:
            prior = runtime.state(opening_id).last_event_id
            runtime.event_store.append(HandoffEvent.create(
                handoff_id=opening_id, event_type=_CLIENT_EVENT,
                actor_id=self.client_id, data=expected,
                parents=(prior,) if prior else (),
            ))
        return {**status, "client_id": self.client_id, "executed": False}

    def execute_worker(
        self, *, opening_id: str, expected_job_id: str,
        allow_native_execution: bool = False,
    ) -> dict:
        """Execute precisely one already-admitted native job, then reverify it."""
        _safe_id(opening_id)
        _safe_id(expected_job_id)
        status = help_status(self._runtime(), opening_id)
        child = status.get("child")
        if not child:
            raise ValueError("requested capability has no admitted native worker")
        if child["job_id"] != expected_job_id:
            raise PermissionError("expected job ID differs from admitted native job")
        if allow_native_execution is not True:
            raise PermissionError("explicit native execution approval required")
        execution = run_job(
            data_dir=self.data_dir, job_id=expected_job_id,
            confirm_execute=expected_job_id,
        )
        # Native verifier is independently consulted again before returning.
        returned = verify_return(data_dir=self.data_dir, opening_id=opening_id)
        return {
            "opening_id": opening_id, "job_id": expected_job_id,
            "execution": execution, "return": returned,
        }

    def reverify_return(self, *, opening_id: str) -> dict:
        """Read and independently reverify existing worker evidence, no execution."""
        _safe_id(opening_id)
        return verify_return(data_dir=self.data_dir, opening_id=opening_id)
