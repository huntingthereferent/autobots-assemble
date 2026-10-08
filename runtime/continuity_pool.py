"""The original Continuity agent queue, on the existing durable runtime.

No new task semantics are created: canonical seed records remain the source.
The recovered ABLoop compares the native source of each admitted task, without
claiming that a source comparison completes site-building or visual work.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from systems.personal_operations.continuity_tasks import ensure_continuity_agent_tasks

ACTOR = "continuity-agent-pool"
SEED_KIND = "continuity_pool"
REFERENT = "Continuity / original autonomous build queue"

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
            "assignee": ACTOR, "evaluator_run": result["status"],
            "model_backed_worker_running": False}


def run_pool_ab(service: Any, repository: Path) -> dict[str, Any]:
    """Execute only through the registered AgentLineage evaluator.

    Never run a parallel source A/B implementation alongside the agent.
    """
    if service.agent_lineage.evaluate is None:
        return {"status": "NOT_REGISTERED"}
    roots = service.agent_lineage.roots_for_actor(ACTOR)
    if not roots:
        return {"status": "NO_AGENT"}
    observations = sum(
        1 for root in roots
        for event in service.runtime.event_store.for_handoff(root)
        if event.event_type == "AGENT_AB_OBSERVED"
    )
    # The evaluator is the same callback installed on the original agent,
    # with a durable idempotency check inside AgentLineage.
    for root in roots:
        service.agent_lineage.run_until_idle(root, max_steps=3)
    newer = sum(
        1 for root in roots
        for event in service.runtime.event_store.for_handoff(root)
        if event.event_type == "AGENT_AB_OBSERVED"
    )
    return {"status": "EVALUATED" if newer > observations else "REUSED"}

def pool_snapshot(service: Any) -> dict[str, Any]:
    """Read-only, truthful live status of the original pool."""
    roots = service.agent_lineage.roots_for_actor(ACTOR)
    tasks = _pool_items(service)
    observations = [
        e for root in roots for e in service.runtime.event_store.for_handoff(root)
        if e.event_type == "AGENT_AB_OBSERVED"
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
        "evaluator_registered": any(
            service.agent_lineage.can_evaluate(service.runtime.get(root))
            for root in roots
        ),
        "evaluator_observations": len(observations),
        "last_evaluation": observations[-1].data["output"] if observations else None,
        "model_backed_worker_running": False,
        "autonomous_site_build_complete": False,
    }
