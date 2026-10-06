from __future__ import annotations

from copy import deepcopy

from runtime import Handoff, HandoffState


def school_task_actor(task: dict) -> str:
    """Resolve the execution actor without changing the school's learner model."""
    meta = task.get("meta") if isinstance(task.get("meta"), dict) else {}
    responsible = str(meta.get("responsible_actor") or "").strip()
    if responsible:
        return responsible

    learners = [str(x) for x in task.get("learner_ids", [])]
    if len(learners) == 1:
        return learners[0]
    if learners:
        return "online-school:shared"
    return "online-school:operator"


def task_to_handoff(task: dict) -> Handoff:
    task_id = str(task.get("id") or "").strip()
    title = str(task.get("title") or "").strip()
    if not task_id:
        raise ValueError("school task id is required")
    if not title:
        raise ValueError("school task title is required")

    referent = f"Online School / {task.get('date', 'undated')} / {title}"
    actor = school_task_actor(task)
    return Handoff(
        handoff_id=f"school-{task_id}",
        referent=referent,
        from_actor="online-school",
        to_actor=actor,
        required_relation="complete school task",
        inputs={
            "date": task.get("date"),
            "category": task.get("category"),
            "kind": task.get("kind"),
            "scope": task.get("scope"),
            "learner_ids": list(task.get("learner_ids") or []),
            "planned_minutes": task.get("planned_minutes"),
            "notes": task.get("notes") or "",
            "meta": deepcopy(task.get("meta") or {}),
        },
        expected_output={
            "task_status": "done / partial / blocked / skipped",
            "activity_evidence": "when available",
        },
        required_witnesses=("school task disposition reported",),
        admissible_evidence={
            "school task disposition reported": (
                "human_report",
                "work_artifact",
                "automated_record",
            ),
        },
        boundaries=(
            "Task completion does not by itself establish mastery or learning outcome.",
            "Preserve learner privacy boundaries from the Online School source.",
        ),
        provenance=(
            f"online-school-task:{task_id}",
            f"online-school-source:{task.get('source', 'unknown')}",
        ),
        metadata={
            "title": title,
            "source_system": "online-school",
            "source_task_id": task_id,
            "school_date": task.get("date"),
        },
    )


def task_patch_from_handoff_state(state: HandoffState) -> dict:
    """Translate shared handoff state back into the school's local task state.

    The adapter returns a patch; the Online School system remains responsible
    for applying/persisting it.
    """
    if state.status == "COMPLETE":
        return {"status": "done"}
    if state.status in {"ACTIVE", "PARTIAL"}:
        return {"status": "in_progress"}
    if state.status in {"BLOCKED", "FAILED", "UNKNOWN"}:
        return {"status": "blocked"}
    return {"status": "todo"}
