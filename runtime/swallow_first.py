"""Swallow-first boundary on the existing durable handoff event stream.

This is an adapter for bounded referent-evidence comparison/admission, not
a definition of the language referent or an autonomous external search tool.
All outward traversal and comparison are supplied by registered actors.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Literal

from .engine import HandoffRuntime
from .handoff import EvidenceRecord, ExecutionResult, Handoff, HandoffEvent, HandoffState


@dataclass(frozen=True)
class NativeWitness:
    """External object remains native; this is its bounded locator."""
    source_kind: str
    locator: str
    native_ref: str
    relation: str


@dataclass(frozen=True)
class SwallowReport:
    searched: tuple[str, ...] = ()
    witnesses: tuple[NativeWitness, ...] = ()
    error: str = ""


@dataclass(frozen=True)
class ReferenceAdmission:
    """Decision returned by the external referent-evidence comparison/admission layer."""
    admitted: bool
    reference_id: str = ""
    evidence: tuple[EvidenceRecord, ...] = ()


SwallowAgent = Callable[[Handoff, HandoffState], SwallowReport]
ReferenceAdmitter = Callable[[Handoff, HandoffState, NativeWitness], ReferenceAdmission]
ResumeWorker = Callable[[Handoff, NativeWitness, ReferenceAdmission], ExecutionResult]
RegroundAgent = Callable[[Handoff, HandoffState, SwallowReport], ExecutionResult | None]


class SwallowFirstBoundary:
    """Resolve UNKNOWN/BLOCKED before considering a human escalation.

    Failed candidates and regrounding are observations on the *same* original
    wall. Only an evidence-valid COMPLETE result may close that same handoff.
    """

    def __init__(
        self,
        runtime: HandoffRuntime,
        *,
        swallow_agent: SwallowAgent,
        admit_reference: ReferenceAdmitter,
        resume_worker: ResumeWorker,
        reground_agents: tuple[RegroundAgent, ...] = (),
    ) -> None:
        self.runtime = runtime
        self.swallow_agent = swallow_agent
        self.admit_reference = admit_reference
        self.resume_worker = resume_worker
        self.reground_agents = reground_agents

    def _terminal_event_id(self, handoff_id: str) -> str:
        for event in reversed(self.runtime.event_store.for_handoff(handoff_id)):
            if event.event_type == "RESULT":
                return event.event_id
        raise ValueError(f"no result event for {handoff_id}")

    def _append(
        self, handoff_id: str, kind: str, terminal_id: str,
        *, data: dict | None = None, evidence: tuple[EvidenceRecord, ...] = (),
    ) -> None:
        last = self.runtime.state(handoff_id).last_event_id
        self.runtime.event_store.append(HandoffEvent.create(
            handoff_id=handoff_id,
            event_type=kind,
            actor_id="swallow-boundary",
            data={"terminal_event_id": terminal_id, **(data or {})},
            evidence=evidence,
            parents=(last,) if last else (),
        ))

    def _recorded(self, handoff_id: str, kind: str, terminal_id: str) -> bool:
        return any(
            event.event_type == kind
            and event.data.get("terminal_event_id") == terminal_id
            for event in self.runtime.event_store.for_handoff(handoff_id)
        )

    def _complete(
        self, handoff: Handoff, result: ExecutionResult,
        *, actor_id: str,
    ) -> HandoffState:
        if result.status != "COMPLETE":
            raise ValueError("only COMPLETE may dissolve this wall")
        if not result.evidence:
            raise ValueError("MOVE requires an evidence witness")
        # One durable RESULT replaces the unresolved projection atomically.
        # No transient READY state exists if execution is interrupted.
        self.runtime._validate_complete_evidence(handoff, result.evidence)
        return self.runtime.return_result(
            handoff.handoff_id, actor_id=actor_id, result=result
        )

    def resolve(self, handoff_id: str) -> HandoffState:
        original = self.runtime.state(handoff_id)
        if original.status not in {"UNKNOWN", "BLOCKED"}:
            return original

        terminal_id = self._terminal_event_id(handoff_id)
        if self._recorded(handoff_id, "SWALLOW_UNRESOLVED", terminal_id):
            return self.runtime.state(handoff_id)
        handoff = self.runtime.get(handoff_id)

        # Reuse the durable outward report after an interrupted resolution;
        # repeated orchestration must not silently search the world again.
        previous = next((
            e for e in self.runtime.event_store.for_handoff(handoff_id)
            if e.event_type == "SWALLOW_ATTEMPT"
            and e.data.get("terminal_event_id") == terminal_id
        ), None)
        if previous is not None:
            report = SwallowReport(
                searched=tuple(previous.data.get("searched", ())),
                witnesses=tuple(NativeWitness(**w)
                                for w in previous.data.get("witnesses", ())),
                error=previous.data.get("error", ""),
            )
        else:
            try:
                report = self.swallow_agent(handoff, original)
                if not isinstance(report, SwallowReport):
                    raise TypeError("swallow agent must return SwallowReport")
            except Exception as exc:
                report = SwallowReport(error=f"{type(exc).__name__}: {exc}")
            # Empty invocation is NOT evidence of outward traversal.
            if not report.searched:
                report = SwallowReport(
                    error=report.error or "no outward source searched"
                )
            self._append(
                handoff_id, "SWALLOW_ATTEMPT", terminal_id,
                data={
                    "searched": list(report.searched),
                    "witnesses": [asdict(w) for w in report.witnesses],
                    "error": report.error,
                    "outward_traversal": bool(report.searched),
                },
            )

        if report.searched:
            for witness in report.witnesses:
                if not all((witness.locator, witness.source_kind,
                            witness.native_ref, witness.relation)):
                    self._append(
                        handoff_id, "REFERENCE_REJECTED", terminal_id,
                        data={"reason": "incomplete native source locator"},
                    )
                    continue
                prior_admission = next((
                    e for e in self.runtime.event_store.for_handoff(handoff_id)
                    if e.event_type == "REFERENCE_ADMITTED"
                    and e.data.get("terminal_event_id") == terminal_id
                    and e.data.get("native_witness") == asdict(witness)
                ), None)
                try:
                    decision = (
                        ReferenceAdmission(
                            admitted=True,
                            reference_id=prior_admission.data["reference_id"],
                            evidence=prior_admission.evidence,
                        )
                        if prior_admission is not None
                        else self.admit_reference(handoff, original, witness)
                    )
                    if not isinstance(decision, ReferenceAdmission):
                        raise TypeError("admitter must return ReferenceAdmission")
                    if not decision.admitted:
                        self._append(
                            handoff_id, "REFERENCE_REJECTED", terminal_id,
                            data={"locator": witness.locator},
                        )
                        continue
                    if not decision.reference_id or not decision.evidence:
                        raise ValueError("admission requires reference id and evidence")
                    resumed = self.resume_worker(handoff, witness, decision)
                    if resumed.status != "COMPLETE":
                        self._append(
                            handoff_id, "WORKER_STILL_BLOCKED", terminal_id,
                            data={"locator": witness.locator, "status": resumed.status},
                        )
                        continue
                    if not resumed.evidence:
                        raise ValueError("worker MOVE requires evidence")
                    self.runtime._validate_complete_evidence(handoff, resumed.evidence)
                except Exception as exc:
                    self._append(
                        handoff_id, "REFERENCE_REJECTED", terminal_id,
                        data={"locator": witness.locator, "reason": str(exc)},
                    )
                    continue

                if prior_admission is None:
                    self._append(
                        handoff_id, "REFERENCE_ADMITTED", terminal_id,
                        data={"reference_id": decision.reference_id,
                              "native_witness": asdict(witness)},
                        evidence=decision.evidence,
                    )
                return self._complete(handoff, resumed, actor_id=handoff.to_actor)

        for index, agent in enumerate(self.reground_agents):
            try:
                candidate = agent(handoff, original, report)
                if candidate is not None and candidate.status == "COMPLETE":
                    if not candidate.evidence:
                        raise ValueError("reground MOVE requires evidence")
                    self.runtime._validate_complete_evidence(handoff, candidate.evidence)
                    self._append(
                        handoff_id, "REGROUND_MOVE", terminal_id,
                        data={"agent_index": index},
                    )
                    return self._complete(handoff, candidate, actor_id=handoff.to_actor)
                status = candidate.status if candidate is not None else "NO_MOVE"
            except Exception as exc:
                status = f"INVALID ({type(exc).__name__}): {exc}"
            self._append(
                handoff_id, "REGROUND_ATTEMPT", terminal_id,
                data={"agent_index": index, "result": status},
            )

        self._append(
            handoff_id, "SWALLOW_UNRESOLVED", terminal_id,
            data={"original_status": original.status,
                  "original_output": original.output,
                  "reground_agents": len(self.reground_agents)},
        )
        return self.runtime.state(handoff_id)

    def ready_for_james(self, handoff_id: str) -> bool:
        """Explicit guard for bridge callers; never escalates by itself."""
        current = self.runtime.state(handoff_id)
        if current.status not in {"UNKNOWN", "BLOCKED"}:
            return False
        terminal_id = self._terminal_event_id(handoff_id)
        events = self.runtime.event_store.for_handoff(handoff_id)
        searched = any(
            e.event_type == "SWALLOW_ATTEMPT"
            and e.data.get("terminal_event_id") == terminal_id
            and e.data.get("outward_traversal") is True
            for e in events
        )
        return searched and self._recorded(handoff_id, "SWALLOW_UNRESOLVED", terminal_id)
