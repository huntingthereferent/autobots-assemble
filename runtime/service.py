from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from runtime.activation import ActivationRegistry, run_activation
from runtime.agent_bridge import AgentBridge
from runtime.agent_lineage import AgentLineage, Evaluator, ClosureAdmitter
from runtime.observed_evaluator import NativeReferentEvaluator, Observer
from runtime.repository_tasks import admit_active_work, read_active_work
from runtime.daily_checklist import DailyChecklist
from runtime.engine import HandoffRuntime
from runtime.external_feed import LiveFeed
from runtime.handoff import EvidenceRecord, ExecutionResult, SimulatedActor
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator, SystemBinding
from runtime.trace import TraceStore, TraversalTouch
from systems.bindings import personal_operations_binding
from systems.calendar import CalendarEvent, CalendarStore
from systems.day_to_day import DayToDayStore, Reminder, attention_projection
from systems.personal_operations import (
    Note,
    PersonalOperationsStore,
    Plan,
    TaskRecord,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVATIONS = ROOT / "activations" / "registry.json"


class EcosystemService:
    """Persistent application service over the shared runtime.

    The service owns no new work model. It coordinates the existing
    Personal Operations system, activation registry, durable HandoffRuntime,
    and Orchestrator.
    """

    def __init__(
        self,
        *,
        data_dir: str | Path,
        activation_registry: str | Path = DEFAULT_ACTIVATIONS,
        system_bindings: Iterable[SystemBinding] = (),
        actors: Iterable[SimulatedActor] = (),
        referent_evaluator: Evaluator | None = None,
        ab_evaluator: Evaluator | None = None,  # compatibility alias
        native_observer: Observer | None = None,
        closure_admitter: ClosureAdmitter | None = None,
        repository_work_file: str | Path | None = None,
        protected_runtime_key: bytes | None = None,
        trusted_runtime_checkpoint: dict[str, Any] | None = None,
        trusted_checkpoint_public_key: Any | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Explicit trusted-host configuration only. Never enroll keys from HTTP.
        self._security_ingresses = {}
        self.repository_work_file = (Path(repository_work_file).resolve()
                                     if repository_work_file is not None else None)
        if self.repository_work_file is not None and not self.repository_work_file.is_file():
            raise FileNotFoundError(f"repository work source unavailable: {self.repository_work_file}")

        self.daily_checklist = DailyChecklist(self.data_dir / "daily_checklist.jsonl")
        self.personal = PersonalOperationsStore(
            self.data_dir / "personal_operations.jsonl"
        )
        self.day_to_day = DayToDayStore(
            self.data_dir / "day_to_day.jsonl"
        )
        self.calendar = CalendarStore(
            self.data_dir / "calendar.jsonl"
        )
        # Explicit opt-in to native encrypted records. Never silently mix
        # the legacy plaintext journal with a new encrypted history.
        legacy = self.data_dir / "runtime.jsonl"
        sealed = self.data_dir / "runtime.sealed.sqlite"
        if (trusted_runtime_checkpoint is None) != (trusted_checkpoint_public_key is None):
            raise ValueError("both signed checkpoint and pinned public key must be supplied")
        if trusted_runtime_checkpoint is not None and protected_runtime_key is None:
            raise ValueError("checkpoint needs the encrypted runtime key")
        if trusted_runtime_checkpoint is not None and not sealed.is_file():
            raise ValueError("cannot recover missing sealed history from a checkpoint")
        if protected_runtime_key is None:
            if sealed.exists() or sealed.is_symlink():
                raise ValueError("sealed runtime exists; provide its trusted key")
            event_store = RuntimeJournal(legacy)
        else:
            if legacy.exists() or legacy.is_symlink():
                raise ValueError("plaintext runtime exists; explicit migration required")
            from security.sealed_journal import SealedRuntimeJournal
            event_store = SealedRuntimeJournal(sealed, key=protected_runtime_key)
            if trusted_runtime_checkpoint is not None:
                from security.journal_checkpoint import verify_checkpoint
                verify_checkpoint(event_store, trusted_runtime_checkpoint,
                                  trusted_checkpoint_public_key)
        self.runtime = HandoffRuntime(event_store=event_store)
        self.trace = TraceStore(
            self.data_dir / "traversal.jsonl"
        )
        self.live_feed = LiveFeed()
        self.orchestrator = Orchestrator(self.runtime)
        self.orchestrator.register_system(
            personal_operations_binding(self.personal)
        )
        for binding in system_bindings:
            self.orchestrator.register_system(binding)
        for actor in actors:
            self.orchestrator.register_actor(actor)
        self.activations = ActivationRegistry.from_json(
            activation_registry
        )
        if referent_evaluator is not None and ab_evaluator is not None and referent_evaluator is not ab_evaluator:
            raise ValueError("conflicting evaluator bindings")
        selected_evaluator = referent_evaluator if referent_evaluator is not None else ab_evaluator
        native = NativeReferentEvaluator(native_observer) if native_observer is not None else None
        if native is not None and selected_evaluator is not None:
            from runtime.evaluator_router import RoutedEvaluator
            evaluator = RoutedEvaluator(self.runtime, selected_evaluator, native)
        else:
            evaluator = selected_evaluator or native
        self.agent_lineage = AgentLineage(
            self.runtime, self.activations,
            evaluate=evaluator, admit_closure=closure_admitter,
            allow_simulation=False,
        )
        self.agent_bridge = AgentBridge(self.agent_lineage)
        # Resume only already-recorded results. Never run a new comparator at startup.
        self.agent_lineage.reconcile_completed()

        # Re-bind origins and submit any admitted local tasks that predate
        # runtime persistence. Human tasks remain READY without an actor.
        self.orchestrator.step()

    def status(self) -> dict[str, Any]:
        snapshot = self.runtime.snapshot()
        by_status: dict[str, int] = {}
        for state in snapshot.values():
            by_status[state.status] = by_status.get(state.status, 0) + 1

        return {
            "registered_systems": list(self.orchestrator._systems),
            "systems": {
                "personal-operations": {
                    "notes": len(self.personal.notes()),
                    "plans": len(self.personal.plans()),
                    "tasks": len(self.personal.tasks()),
                    "reconciled_results": sum(
                        1
                        for task in self.personal.tasks()
                        if self.personal.task_result(task.task_id) is not None
                    ),
                },
                "day-to-day": {
                    "reminders": len(self.day_to_day.reminders()),
                },
                "calendar": {
                    "events": len(self.calendar.events()),
                }
            },
            "runtime": {
                "handoffs": len(snapshot),
                "by_status": by_status,
                "events": len(self.runtime.event_store.all()),
                "touches": len(self.trace.touches()),
            },
        }

    def connections(self) -> dict[str, Any]:
        """Evidence-grounded source and runtime connectivity, not a live-agent claim."""
        source = self.repository_work_file
        available = source is not None and source.is_file()
        candidates = read_active_work(source) if available else ()
        snapshot = self.runtime.snapshot()
        return {
            "repository_work": {
                "configured": source is not None,
                "available": available,
                "source": source.name if source is not None else None,
                "eligible_active_rows": len(candidates),
                "admitted_handoffs": sum(
                    h.metadata.get("source_system") == "repository"
                    for h in self.runtime._handoffs.values()
                ),
                "mode": "explicit_ohayo_admission_only",
            },
            "handoff_runtime": {
                "durable": isinstance(self.runtime.event_store, RuntimeJournal),
                "recorded_handoffs": len(snapshot),
            },
            "agents": {
                "recorded": sum(h.metadata.get("agent_lineage") is True
                                for h in self.runtime._handoffs.values()),
                "referent_evaluator_connected": self.agent_lineage.evaluate is not None,
                "ab_evaluator_connected": self.agent_lineage.evaluate is not None,  # legacy API
                "evaluator_actors": sorted(getattr(
                    self.agent_lineage.evaluate, "supported_actors", ()) or ()),
                "closure_admitter_connected": self.agent_lineage.admit_closure is not None,
                "autonomous_worker_running": False,
            },
            "continuity_pool": {
                "original_task_owner": "continuity-agent-pool",
                "original_tasks_admitted": sum(
                    t.assignee == "continuity-agent-pool"
                    and self.personal.admitted_handoff_id(t.task_id) is not None
                    for t in self.personal.tasks()
                    if any(p.startswith("seed:continuity-agent:") for p in t.provenance)
                ),
                "registered_evaluator": any(
                    self.agent_lineage.can_evaluate(self.runtime.get(root))
                    for root in self.agent_lineage.roots_for_actor("continuity-agent-pool")
                ),
                "model_backed_worker_running": False,
            },
            "systems": {
                "registered": list(self.orchestrator._systems),
                "online_school_registered": "online-school" in self.orchestrator._systems,
                "factory_registered": "factory" in self.orchestrator._systems,
            },
            "warning": (
                "A referent evaluator can inspect native evidence, but software editing, "
                "independent closure and model-backed autonomous execution need "
                "separately registered capable actors."
            ),
        }

    def step(self):
        """Advance one orchestration pass across every registered system."""
        return self.orchestrator.step()

    def run_until_idle(self, *, max_steps: int = 100):
        """Advance executable work while leaving unavailable actors READY."""
        return self.orchestrator.run_until_idle(max_steps=max_steps)

    def add_note(self, payload: dict[str, Any]) -> dict[str, Any]:
        note = self.personal.add_note(
            Note.create(
                str(payload.get("body") or ""),
                referent=str(payload.get("referent") or ""),
                actor_id=str(payload.get("actor_id") or ""),
                tags=tuple(str(x) for x in payload.get("tags") or ()),
                provenance=tuple(
                    str(x) for x in payload.get("provenance") or ()
                ),
            )
        )
        return asdict(note)

    def add_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = self.personal.add_plan(
            Plan.create(
                str(payload.get("title") or ""),
                referent=str(payload.get("referent") or ""),
                actor_id=str(payload.get("actor_id") or ""),
                steps=tuple(str(x) for x in payload.get("steps") or ()),
                notes=str(payload.get("notes") or ""),
                provenance=tuple(
                    str(x) for x in payload.get("provenance") or ()
                ),
            )
        )
        return asdict(plan)

    def add_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        task = self.personal.add_task(
            TaskRecord.create(
                str(payload.get("title") or ""),
                referent=str(payload.get("referent") or ""),
                assignee=str(payload.get("assignee") or ""),
                required_relation=str(
                    payload.get("required_relation")
                    or "move current task"
                ),
                inputs=dict(payload.get("inputs") or {}),
                expected_output=dict(
                    payload.get("expected_output") or {}
                ),
                boundaries=tuple(
                    str(x) for x in payload.get("boundaries") or ()
                ),
                provenance=tuple(
                    str(x) for x in payload.get("provenance") or ()
                ),
                notes=str(payload.get("notes") or ""),
            )
        )
        return {
            **asdict(task),
            "admitted_handoff_id": None,
            "result": None,
        }

    def admit_task(self, task_id: str) -> dict[str, Any]:
        handoff = self.personal.admit_task(task_id)
        self.orchestrator.step()
        state = self.runtime.state(handoff.handoff_id)
        return self._handoff_view(handoff.handoff_id, state)

    def list_notes(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.personal.notes()]

    def list_plans(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.personal.plans()]

    def list_tasks(self) -> list[dict[str, Any]]:
        rows = []
        for task in self.personal.tasks():
            rows.append(
                {
                    **asdict(task),
                    "admitted_handoff_id": self.personal.admitted_handoff_id(
                        task.task_id
                    ),
                    "result": self.personal.task_result(task.task_id),
                }
            )
        return rows

    def daily_checklist_snapshot(self, *, now: datetime | None = None) -> dict[str, Any]:
        return self.daily_checklist.snapshot(now=now)

    def add_daily_checklist_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.daily_checklist.create(str(payload.get("title") or ""))

    def set_daily_checklist_checked(self, item_id: str, *, checked: bool) -> dict[str, Any]:
        return self.daily_checklist.check(item_id, checked)

    def add_reminder(self, payload: dict[str, Any]) -> dict[str, Any]:
        reminder = self.day_to_day.add_reminder(
            Reminder.create(
                str(payload.get("text") or ""),
                actor_id=str(payload.get("actor_id") or ""),
                referent=str(payload.get("referent") or ""),
                cadence=str(payload.get("cadence") or "daily"),
                weekdays=tuple(int(x) for x in payload.get("weekdays") or ()),
                local_time=str(payload.get("local_time") or ""),
                provenance=tuple(str(x) for x in payload.get("provenance") or ()),
            )
        )
        return asdict(reminder)

    def list_reminders(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.day_to_day.reminders()]

    def acknowledge_reminder(self, reminder_id: str, *, local_date: str) -> None:
        self.day_to_day.acknowledge(reminder_id, local_date=local_date)

    def add_calendar_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = self.calendar.add(
            CalendarEvent.create(
                str(payload.get("title") or ""),
                referent=str(payload.get("referent") or ""),
                participants=tuple(str(x) for x in payload.get("participants") or ()),
                kind=str(payload.get("kind") or "event"),
                movement_anchor=str(payload.get("movement_anchor") or ""),
                starts_at=str(payload.get("starts_at") or ""),
                ends_at=str(payload.get("ends_at") or ""),
                due_at=str(payload.get("due_at") or ""),
                recurrence=str(payload.get("recurrence") or "none"),
                weekdays=tuple(int(x) for x in payload.get("weekdays") or ()),
                notes=str(payload.get("notes") or ""),
                provenance=tuple(str(x) for x in payload.get("provenance") or ()),
            )
        )
        return asdict(event)

    def list_calendar_events(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.calendar.events()]

    def add_touch(self, payload: dict[str, Any]) -> dict[str, Any]:
        touch = self.trace.add(TraversalTouch.create(payload))
        return asdict(touch)

    def list_touches(self, *, session_id: str | None = None) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.trace.touches(session_id=session_id)]

    def trace_ancestry(self, trace_id: str) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.trace.ancestry(trace_id)]

    def live_feed_snapshot(self, *, force: bool = False) -> dict[str, Any]:
        return self.live_feed.snapshot(force=force)

    def attention(self, *, actor_id: str, now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now().astimezone()
        pairs = [
            (self.runtime.get(handoff_id), state)
            for handoff_id, state in self.runtime.snapshot().items()
        ]
        return attention_projection(
            actor_id=actor_id,
            now=now,
            handoffs=pairs,
            reminders=self.day_to_day.due_reminders(actor_id, now=now),
            calendar_events=self.calendar.events_for(actor_id, now=now),
        )

    def _handoff_view(self, handoff_id: str, state=None) -> dict[str, Any]:
        handoff = self.runtime.get(handoff_id)
        state = state or self.runtime.state(handoff_id)
        return {
            "handoff_id": handoff.handoff_id,
            "referent": handoff.referent,
            "from_actor": handoff.from_actor,
            "to_actor": handoff.to_actor,
            "required_relation": handoff.required_relation,
            "status": state.status,
            "inputs": handoff.inputs,
            "expected_output": handoff.expected_output,
            "required_witnesses": list(handoff.required_witnesses),
            "blocked_by": list(state.blocked_by),
            "missing_witnesses": list(state.missing_witnesses),
            "output": state.output,
            "evidence": [asdict(item) for item in state.evidence],
            "boundaries": list(handoff.boundaries),
            "provenance": list(handoff.provenance),
            "metadata": handoff.metadata,
        }

    def list_handoffs(
        self,
        *,
        actor_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = []
        for handoff_id, state in self.runtime.snapshot().items():
            handoff = self.runtime.get(handoff_id)
            if actor_id and handoff.to_actor != actor_id:
                continue
            if status and state.status != status:
                continue
            rows.append(self._handoff_view(handoff_id, state))
        rows.sort(
            key=lambda row: (
                row["status"],
                str(row["metadata"].get("title") or row["required_relation"]),
            )
        )
        return rows

    def activate_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "result" in self._security_ingresses:
            raise PermissionError("unsigned agent activation disabled under signed worker policy")
        activated = self.agent_bridge.activate(payload)
        if self.agent_lineage.evaluate is not None:
            self.agent_lineage.run_until_idle(activated["root"])
            return self.agent_bridge.snapshot(activated["root"])
        return activated

    def agent_result(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if "result" in self._security_ingresses:
            raise PermissionError("unsigned agent result disabled under signed worker policy")
        returned = self.agent_bridge.result(agent_id, payload)
        if self.agent_lineage.evaluate is not None:
            root = returned["lineage"]["root"]
            later = self.agent_lineage.run_until_idle(root)
            returned["continued_steps"] = [asdict(step) for step in later]
            returned["lineage"] = self.agent_bridge.snapshot(root)
        return returned

    def agent_snapshot(self, root: str) -> dict[str, Any]:
        return self.agent_bridge.snapshot(root)

    def monitor(self, *, actor_id: str, limit: int = 40) -> dict[str, Any]:
        """Read-only operational observation. Never invoke Ohayo POST."""
        from runtime.monitor import observe
        return observe(self, actor_id=actor_id, limit=limit)

    def agent_brief(self, *, actor_id: str) -> dict[str, Any]:
        """Read existing agent lineages with no side effects."""
        roots = self.agent_lineage.roots_for_actor(actor_id)
        lineages = [self.agent_bridge.snapshot(root) for root in roots]
        members = [item for lineage in lineages for item in lineage["agents"]]
        ids = {item["agent_id"] for item in members}
        activity = [
            {
                "agent_id": event.handoff_id,
                "event": event.event_type,
                "at": event.occurred_at,
                "actor_id": event.actor_id,
                "evidence_refs": [w.ref for w in event.evidence if w.ref],
            }
            for event in self.runtime.event_store.all()
            if event.handoff_id in ids
            and event.event_type in {"CREATED", "STARTED", "RESULT", "REOPENED",
                                     "AGENT_LOOP_CLOSED", "SWALLOW_ATTEMPT",
                                     "SWALLOW_UNRESOLVED", "REFERENCE_ADMITTED",
                                     "REFERENCE_REJECTED"}
        ]
        return {
            "agents": members,
            "agent_roots": list(roots),
            "agent_summary": {
                "total": len(members),
                "ready": sum(item["status"] == "READY" for item in members),
                "active": sum(item["status"] == "ACTIVE" for item in members),
                "complete": sum(item["status"] == "COMPLETE" for item in members),
                "blocked_or_unknown": sum(
                    item["status"] in {"BLOCKED", "UNKNOWN", "PARTIAL", "FAILED"}
                    for item in members
                ),
                "closed_loops": sum(item["loop_status"] == "CLOSED" for item in members),
            },
            "agent_activity": activity[-15:],
            "agent_evaluator_connected": self.agent_lineage.evaluate is not None,
        }

    def ohayo(self, *, actor_id: str) -> dict[str, Any]:
        """Report-first activation; seed exactly one task agent only if none exists.

        Do not admit personal notes/tasks, alter existing task ownership, or
        treat an available handoff as an executed referent comparison.
        """
        route = self.activations.resolve("ohayo", actor_id=actor_id)
        if route is None or route.projection != "day_attention":
            raise KeyError("ohayo day attention not registered for actor")
        spawned: list[str] = []
        repository_handoffs: tuple[str, ...] = ()
        if not self.agent_lineage.roots_for_actor(actor_id):
            if self.repository_work_file is not None:
                repository_handoffs = admit_active_work(
                    self.runtime, self.repository_work_file, actor_id=actor_id
                )
            snapshot = self.runtime.snapshot()
            tasks = tuple(
                self.runtime.get(hid) for hid, state in snapshot.items()
                if self.runtime.get(hid).to_actor.strip().casefold()
                == actor_id.strip().casefold()
                and state.status in {"ACTIVE", "READY", "PARTIAL", "BLOCKED", "WAITING"}
            )
            if tasks:
                root = self.agent_lineage.seed_for_tasks(
                    actor_id=actor_id, tasks=tasks,
                    route_id=route.activation_id, referent=route.referent,
                    boundaries=route.boundaries, provenance=route.provenance,
                )
                if root is not None:
                    spawned.append(root)
                    if self.agent_lineage.evaluate is not None:
                        self.agent_lineage.run_until_idle(root)
        report = self.activate("ohayo", actor_id=actor_id)
        report["agent_spawned"] = spawned
        report["repository_handoffs_admitted"] = list(repository_handoffs)
        report["repository_work"] = self.connections()["repository_work"]
        if spawned:
            report["agent_note"] = (
                "One task-lineage agent seeded from existing admitted handoffs; "
                "no task execution is implied."
            )
        elif not report["agent_roots"]:
            report["agent_note"] = "No recorded agents or admitted tasks; idle."
        else:
            report["agent_note"] = "Existing agents reported; no new agent spawned."
        return report

    def activate(
        self,
        surface: str,
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        route = self.activations.resolve(
            surface,
            actor_id=actor_id,
        )
        if route is None:
            raise KeyError(
                f"no activation for {surface!r} and actor {actor_id!r}"
            )

        if route.projection == "agent_lineage":
            raise ValueError("agent lineage requires POST /api/agents/activate")
        result = run_activation(
            route,
            surface=surface,
            handoffs=[
                (self.runtime.get(handoff_id), state)
                for handoff_id, state in self.runtime.snapshot().items()
            ],
        )
        payload = {
            "activation_id": route.activation_id,
            "referent": route.referent,
            "projection": route.projection,
            "items": list(result.items),
            "note": result.note,
        }
        if route.projection == "day_attention":
            attention = self.attention(actor_id=actor_id)
            payload["items"] = attention["tasks"]
            payload["tasks"] = attention["tasks"]
            payload["reminders"] = attention["reminders"]
            payload["calendar"] = attention["calendar"]
            payload["local_date"] = attention["local_date"]
            payload.update(self.agent_brief(actor_id=actor_id))
            payload["agent_spawned"] = []
            payload["agent_note"] = "Read-only report; activation uses POST /api/ohayo."
            payload["repository_work"] = self.connections()["repository_work"]
        return payload

    @property
    def signed_http_only(self) -> bool:
        """True as soon as a trusted host begins enrolling HTTP signer roles.

        Partial setup fails closed. Local native Python callers and legacy
        service methods are separate, explicitly trusted interfaces.
        """
        return bool(self._security_ingresses)

    def register_authenticated_ingress(self, role: str, ingress) -> None:
        """Install trusted local key policy; HTTP has no enrollment endpoint."""
        from security.runtime_ingress import AuthenticatedHandoffIngress
        if role not in {"submit", "result"} or role in self._security_ingresses:
            raise ValueError("ingress role must be a unique submit or result")
        if not isinstance(ingress, AuthenticatedHandoffIngress) or ingress.runtime is not self.runtime:
            raise ValueError("security ingress must use this exact native runtime")
        if ingress.authority.operator_pin_ledger is None:
            raise PermissionError("HTTP ingress requires the active B14 operator key policy")
        ingress.authority.require_current_operator_pin()
        self._security_ingresses[role] = ingress

    def authenticated_submit(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Only operator-installed, authenticated external handoffs are admitted."""
        ingress = self._security_ingresses.get("submit")
        if ingress is None:
            raise PermissionError("authenticated handoff ingress is not configured")
        if type(payload) is not dict or set(payload) != {"envelope"}:
            raise ValueError("one sealed envelope required")
        # A caller-supplied expected-parent digest must never establish ancestry.
        # Root events only until a trusted parent registry is attached.
        envelope = payload["envelope"]
        if type(envelope) is not dict:
            raise ValueError("sealed envelope must be an object")
        state = ingress.submit(envelope, expected_parent_sha256=None)
        return self._handoff_view(state.handoff_id, state)

    def authenticated_return_result(self, handoff_id: str,
                                    payload: dict[str, Any]) -> dict[str, Any]:
        """Admit a signed worker result without trusting HTTP actor_id."""
        ingress = self._security_ingresses.get("result")
        if ingress is None:
            raise PermissionError("authenticated result ingress is not configured")
        if type(payload) is not dict or set(payload) != {"envelope"}:
            raise ValueError("one sealed envelope required")
        envelope = payload["envelope"]
        if type(envelope) is not dict:
            raise ValueError("sealed envelope must be an object")
        if self.runtime.get(handoff_id).metadata.get("agent_lineage") is True:
            raise ValueError("agent lineage requires its own authenticated contract")
        state = ingress.return_result(envelope, handoff_id=handoff_id,
                                      expected_parent_sha256=None)
        return self._handoff_view(handoff_id, state)

    def return_result(
        self,
        handoff_id: str,
        payload: dict[str, Any],
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        if "result" in self._security_ingresses:
            raise PermissionError("unsigned handoff result disabled under signed worker policy")
        if self.runtime.get(handoff_id).metadata.get("agent_lineage") is True:
            raise ValueError("agent lineage results require POST /api/agents/{id}/result")
        evidence = tuple(
            EvidenceRecord(
                condition=str(item.get("condition") or ""),
                kind=str(item.get("kind") or ""),
                source=str(item.get("source") or actor_id),
                ref=str(item.get("ref") or ""),
                note=str(item.get("note") or ""),
                depth=str(item.get("depth") or "reported"),
            )
            for item in payload.get("evidence") or ()
        )
        status = str(payload.get("status") or "UNKNOWN").upper()
        if status not in {
            "COMPLETE",
            "PARTIAL",
            "BLOCKED",
            "FAILED",
            "UNKNOWN",
        }:
            raise ValueError(f"invalid result status: {status}")

        result = ExecutionResult(
            status=status,
            output=dict(payload.get("output") or {}),
            evidence=evidence,
            note=str(payload.get("note") or ""),
        )
        state = self.orchestrator.return_result(
            handoff_id,
            actor_id=actor_id,
            result=result,
        )
        return self._handoff_view(handoff_id, state)
