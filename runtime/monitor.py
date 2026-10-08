"""Read-only operational snapshot over the existing durable runtime.

A snapshot is observation, not execution, and never submits/reopens work.
Only events from the actor's handoffs and their descendant agents are exposed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .service import EcosystemService

WATCHED_EVENTS = {
    "CREATED", "STARTED", "RESULT", "REOPENED", "AGENT_LOOP_CLOSED",
    "SWALLOW_ATTEMPT", "SWALLOW_UNRESOLVED", "REFERENCE_ADMITTED",
    "REFERENCE_REJECTED", "REGROUND_ATTEMPT",
}
OPEN_TASK_STATUSES = {"WAITING", "READY", "ACTIVE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"}


def observe(service: "EcosystemService", *, actor_id: str, limit: int = 40) -> dict[str, Any]:
    """Generate one bounded actor-scoped snapshot without touching event state."""
    if not actor_id.strip():
        raise ValueError("actor_id required")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be 1..100")
    actor = actor_id.strip().casefold()
    now = datetime.now(timezone.utc)
    connections = service.connections()
    brief = service.agent_brief(actor_id=actor_id)

    states = service.runtime.snapshot()
    tasks = []
    for hid, state in states.items():
        handoff = service.runtime.get(hid)
        if handoff.to_actor.strip().casefold() != actor:
            continue
        tasks.append({
            "handoff_id": hid,
            "title": str(handoff.metadata.get("title") or handoff.referent),
            "referent": handoff.referent,
            "status": state.status,
            "source": str(handoff.metadata.get("source_system") or handoff.from_actor),
            "source_ref": next(iter(handoff.provenance), ""),
            "last_event_at": next(
                (event.occurred_at for event in reversed(
                    service.runtime.event_store.for_handoff(hid))), None),
            "missing_witnesses": list(state.missing_witnesses),
        })
    agents = []
    for item in brief["agents"]:
        hid = item["agent_id"]
        recent = service.runtime.event_store.for_handoff(hid)
        agents.append({
            "agent_id": hid,
            "referent": item["referent"],
            "generation": item["generation"],
            "birth_parent": item["birth_parent"],
            "birth_reason": item["birth_reason"],
            "status": item["status"],
            "loop_status": item["loop_status"],
            "last_event_at": recent[-1].occurred_at if recent else None,
            "last_event_type": recent[-1].event_type if recent else None,
            "witness_count": len(item["evidence"]),
        })

    agent_ids = {a["agent_id"] for a in agents}
    task_ids = {t["handoff_id"] for t in tasks}
    labels = {item["handoff_id"]: item["title"] for item in tasks}
    labels.update({item["agent_id"]: item["referent"] for item in agents})
    events = [
        {
            "event_id": event.event_id,
            "at": event.occurred_at,
            "event_type": event.event_type,
            "handoff_id": event.handoff_id,
            "subject": "agent" if event.handoff_id in agent_ids else "task",
            "label": labels[event.handoff_id],
            "actor_id": event.actor_id,
            "status": (
                str(event.data.get("status") or "")
                if event.event_type == "RESULT" else ""
            ),
            "evidence_refs": [e.ref for e in event.evidence if e.ref][:6],
        }
        for event in service.runtime.event_store.all()
        if event.handoff_id in (agent_ids | task_ids)
        and event.event_type in WATCHED_EVENTS
    ]

    open_tasks = sum(t["status"] in OPEN_TASK_STATUSES for t in tasks)
    working = sum(a["status"] == "ACTIVE" for a in agents)
    ready = sum(a["status"] == "READY" for a in agents)
    unresolved = sum(a["status"] in {"BLOCKED", "FAILED", "UNKNOWN", "PARTIAL"}
                     for a in agents)
    evaluator = connections["agents"]["ab_evaluator_connected"]
    worker = connections["agents"]["autonomous_worker_running"]
    if unresolved:
        mode, detail = "needs_attention", "An agent has an unresolved result; examine the event trail."
    elif ready and not evaluator:
        mode, detail = "waiting_for_evaluator", "Queued agents exist, but no A/B evaluator is registered."
    elif ready and not worker:
        mode, detail = "queued_manual", "Queued agents exist; no autonomous worker is registered."
    elif working:
        mode, detail = "reported_active", "Runtime has a STARTED agent; current execution is not independently verified."
    elif ready:
        mode, detail = "queued", "Agents are ready for execution."
    elif agents:
        mode, detail = "recorded", "Agent history exists; no currently queued or started agents."
    elif open_tasks:
        mode, detail = "tasks_no_agent", "Admitted work exists but no task agent is recorded."
    else:
        mode, detail = "idle", "No active task or agent movement recorded."

    return {
        "generated_at": now.isoformat(),
        "actor_id": actor,
        "read_only": True,
        "monitor": {"mode": mode, "detail": detail},
        "counts": {
            "tasks_total": len(tasks),
            "tasks_open": open_tasks,
            "agents_total": len(agents),
            "agents_ready": ready,
            "agents_active_recorded": working,
            "agents_unresolved": unresolved,
            "loops_closed": sum(a["loop_status"] == "CLOSED" for a in agents),
            "events_observed": len(events),
        },
        "agents": agents,
        "tasks": tasks,
        "events": events[-limit:][::-1],
        "last_event_at": events[-1]["at"] if events else None,
        "connections": connections,
    }
