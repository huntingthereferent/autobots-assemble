"""The original Continuity agent queue, on the existing durable runtime.

No new task semantics are created: canonical seed records remain the source.
The recovered ABLoop compares the native source of each admitted task, without
claiming that a source comparison completes site-building or visual work.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .ab_loop import ABAgent, ABFrame, ABLoop, ABMove
from .handoff import EvidenceRecord, HandoffEvent
from systems.personal_operations.continuity_tasks import ensure_continuity_agent_tasks

ACTOR = "continuity-agent-pool"
SEED_KIND = "continuity_pool"
REFERENT = "Continuity / original autonomous build queue"

# Native entry points grounded in existing task seeds, NOT an industry checklist.
NATIVE_ENTRY = {
    "finish-continuity-site": ("COMPLETE_STACK.md", "runtime/http/index.html"),
    "find-things-to-swallow": ("runtime/swallow_first.py", "runtime/external_feed.py"),
    "visual-provenance-min-max": (
        "runtime/http/index.html", "design/visual-provenance/registry.json",
    ),
}


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             default=str).encode("utf-8")).hexdigest()


def _pool_items(service: Any) -> tuple[Any, ...]:
    result = []
    for task in service.personal.tasks():
        if task.assignee.strip().casefold() != ACTOR:
            continue
        if not any(p.startswith("seed:continuity-agent:") for p in task.provenance):
            continue
        result.append(task)
    return tuple(result)


def connect_pool(service: Any, repository: Path) -> dict[str, Any]:
    """Connect original three tasks to their *own* pool, not James's Ohayo.

    Does not run a model. Task and lineage birth are idempotent and durable.
    """
    repo = Path(repository).resolve()
    tasks = ensure_continuity_agent_tasks(service.personal)
    if len(tasks) != 3 or any(t.assignee != ACTOR for t in tasks):
        raise ValueError("original continuity agent queue contract changed")
    admitted = []
    for task in tasks:
        existing = service.personal.admitted_handoff_id(task.task_id)
        handoff = (service.personal.admitted_handoff(task.task_id)
                   if existing is not None else service.personal.admit_task(task.task_id))
        admitted.append(handoff)
    service.orchestrator.step()
    if any(h.handoff_id not in service.runtime.snapshot() for h in admitted):
        raise RuntimeError("task handoffs did not reach the durable shared runtime")
    root = service.agent_lineage.seed_for_tasks(
        actor_id=ACTOR,
        tasks=tuple(admitted),
        route_id="original-continuity-build-tasks",
        referent=REFERENT,
        boundaries=(
            "A/B source comparison is not task completion.",
            "Model-backed implementation and tests require their own witnesses.",
            "Swallow before James escalation; James does not own these tasks.",
        ),
        provenance=(
            "repository:systems/personal_operations/task_seeds/continuity_agent_tasks.json",
            "continuity-agent-pool:original-three",
        ),
        seed_kind=SEED_KIND,
    )
    if root is None:
        raise RuntimeError("original continuity pool not seeded")
    result = run_pool_ab(service, repo)
    return {"root": root, "tasks": [t.title for t in tasks],
            "assignee": ACTOR, "native_ab": result["status"],
            "model_backed_worker_running": False}


def run_pool_ab(service: Any, repository: Path) -> dict[str, Any]:
    """Run an actual bounded A/B pass over the pool's original native sources.

    MOVE means the native entry/source was recovered, not that its task
    was done. No model actor / code editor is installed by this function.
    """
    repo = Path(repository).resolve()
    roots = service.agent_lineage.roots_for_actor(ACTOR)
    if not roots:
        return {"status": "NO_AGENT", "agent_roots": [], "checked": []}
    original_tasks = {t.task_id: t for t in _pool_items(service)}
    results, reused = [], []
    for root in roots:
        agent = service.runtime.get(root)
        if service.runtime.state(root).status != "READY":
            continue
        linked = agent.inputs.get("task_handoffs", ())
        if len(linked) != 3:
            raise ValueError("continuity pool no longer carries its three original tasks")
        task_items = []
        for link in linked:
            handoff = service.runtime.get(link["handoff_id"])
            token = next((p.removeprefix("personal-task:") for p in handoff.provenance
                          if p.startswith("personal-task:")), None)
            # Resolve by the admitted handoff rather than guessed task IDs.
            task = next((t for t in original_tasks.values()
                         if service.personal.admitted_handoff_id(t.task_id) ==
                         handoff.handoff_id), None)
            if task is None or task.assignee != ACTOR:
                raise ValueError("pool contains a non-native task handoff")
            seed = next((p.removeprefix("seed:continuity-agent:") for p in task.provenance
                         if p.startswith("seed:continuity-agent:")), None)
            if seed not in NATIVE_ENTRY:
                raise ValueError("unknown original task native reference")
            task_items.append((task, seed))

        def compare(frame: ABFrame) -> ABMove:
            if frame.current.get("reground"):
                return ABMove(
                    "WALL", dict(frame.current), frame.survives, (), frame.edge,
                    note="Implementation cannot be invented from source location.",
                )
            i = int(frame.current.get("index", 0))
            inspected = list(frame.current.get("inspected", ()))
            if i >= len(task_items):
                return ABMove(
                    "UNKNOWN", {"inspected": inspected}, frame.survives, (),
                    "actual implementation and independent results still required",
                    note="A/B source relations checked; open-ended tasks not executed.",
                )
            task, seed = task_items[i]
            sources = []
            for rel in NATIVE_ENTRY[seed]:
                path = (repo / rel).resolve()
                if not path.is_relative_to(repo) or not path.is_file():
                    return ABMove(
                        "WALL", {"inspected": inspected, "missing": rel,
                                 "task": task.title},
                        frame.survives, (), "native source missing",
                        note="Swallow/reference research required before proceeding.",
                    )
                sources.append({"path": rel, "sha256": sha256(path.read_bytes()).hexdigest()})
            inspected.append({"title": task.title, "task_id": task.task_id,
                              "sources": sources, "task_completed": False})
            return ABMove(
                "MOVE", {"index": i+1, "inspected": inspected},
                frame.survives, (f"native entry recovered: {task.title}",),
                "compare next original task's native source",
                evidence=tuple(f"repository:{x['path']}@sha256:{x['sha256']}"
                               for x in sources),
            )

        initial = ABFrame(
            referent=agent.referent,
            direction="A/B original task source references, then stop at actual work",
            current={"index": 0, "inspected": []},
            survives=("task owner", "native reference", "task contract", "provenance"),
            edge="compare next original task's native source",
            provenance=tuple(agent.provenance),
        )
        trace = ABLoop((ABAgent("continuity-native-ab", compare),),
                       max_steps=12).run(initial)
        inspected = [
            entry for step in trace.steps if step.move.state == "MOVE"
            for entry in [step.move.reached["inspected"][-1]]
        ]
        payload = {
            "original_task_count": len(task_items),
            "native_reference_moves": trace.move_count,
            "inspected": inspected,
            "ab_states": [step.move.state for step in trace.steps],
            "last_edge": trace.final_frame.edge,
            "actual_tasks_completed": 0,
            "model_backed_worker_running": False,
        }
        fingerprint = _hash(payload)
        prior = next((
            e for e in service.runtime.event_store.for_handoff(root)
            if e.event_type == "CONTINUITY_POOL_AB"
            and e.data.get("fingerprint") == fingerprint
        ), None)
        if prior is not None:
            reused.append(prior.event_id)
            continue
        witnesses = tuple(
            EvidenceRecord(
                condition="native reference inspected", kind="source",
                source="continuity-original-pool",
                ref=f"repository:{source['path']}@sha256:{source['sha256']}",
                depth="observed", note="Source evidence only, no task completion",
            )
            for task in inspected for source in task["sources"]
        )
        previous = service.runtime.state(root)
        event = HandoffEvent.create(
            handoff_id=root, event_type="CONTINUITY_POOL_AB",
            actor_id="continuity-native-ab",
            data={"fingerprint": fingerprint, **payload},
            evidence=witnesses,
            parents=(previous.last_event_id,) if previous.last_event_id else (),
        )
        service.runtime.event_store.append(event)
        current = service.runtime.state(root)
        if current.status != "READY" or "movement witness" not in current.missing_witnesses:
            raise AssertionError("native source A/B cannot replace task-execution witness")
        results.append({"event_id": event.event_id, **payload})
    return {
        "status": "EVALUATED" if results else ("REUSED" if reused else "NO_READY_AGENT"),
        "agent_roots": list(roots), "evaluations": results, "reused_events": reused,
    }


def pool_snapshot(service: Any) -> dict[str, Any]:
    """Read-only, truthful live status of the original pool."""
    roots = service.agent_lineage.roots_for_actor(ACTOR)
    tasks = _pool_items(service)
    observations = [
        e for root in roots for e in service.runtime.event_store.for_handoff(root)
        if e.event_type == "CONTINUITY_POOL_AB"
    ]
    return {
        "assignee": ACTOR,
        "original_tasks": [
            {"task_id": task.task_id, "title": task.title,
             "admitted_handoff_id": service.personal.admitted_handoff_id(task.task_id),
             "status": service.runtime.state(
                 service.personal.admitted_handoff_id(task.task_id)).status
             if service.personal.admitted_handoff_id(task.task_id) else "NOT_ADMITTED",
             "result": service.personal.task_result(task.task_id)}
            for task in tasks
        ],
        "agent_roots": [
            {"id": root, "status": service.runtime.state(root).status,
             "missing_witnesses": list(service.runtime.state(root).missing_witnesses)}
            for root in roots
        ],
        "native_ab_connected": True,
        "native_ab_observations": len(observations),
        "last_native_ab": observations[-1].data if observations else None,
        "model_backed_worker_running": False,
        "autonomous_site_build_complete": False,
    }
