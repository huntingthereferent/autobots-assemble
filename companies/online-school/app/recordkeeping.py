from __future__ import annotations

from dataclasses import asdict
from typing import Any


def build_record_packet(*, state: dict[str, Any], learner: dict[str, Any], kernel) -> dict[str, Any]:
    learner_id = str(learner.get("id") or "")
    tasks = [t for t in state.get("tasks", []) if learner_id in t.get("learner_ids", [])]
    works = [
        w for w in state.get("worksheets", [])
        if str(w.get("learner") or "") in {learner_id, str(learner.get("display_name") or "")}
    ]
    observations = [asdict(x) for x in kernel.observations_for_person(learner_id)]
    relations = [asdict(x) for x in kernel.current_for_person(learner_id)]
    completed = [t for t in tasks if t.get("status") == "done"]
    # Completion and planned minutes alone never establish actual instructional time.
    def actual_time(task):
        value = task.get("actual_minutes")
        return int(value) if value is not None else None

    actual_tasks = [t for t in tasks if actual_time(t) is not None]
    logged_actual_minutes = sum(actual_time(t) for t in actual_tasks)
    completed_actual = [t for t in completed if actual_time(t) is not None]
    completed_actual_minutes = sum(actual_time(t) for t in completed_actual)
    scheduled_minutes = sum(int(t.get("planned_minutes") or 0) for t in tasks)
    estimated_completed_minutes = sum(
        int(t.get("planned_minutes") or 0) for t in completed
    )
    by_category = {}
    for task in actual_tasks:
        category = str(task.get("category") or task.get("title") or "other")
        by_category[category] = by_category.get(category, 0) + actual_time(task)

    return {
        "learner": learner,
        "placement": learner.get("placement") or {},
        "current_relations": relations,
        "observations": observations,
        "human_notes": learner.get("human_notes") or [],
        "tasks": tasks,
        "worksheets": works,
        "calendar": [
            row for row in state.get("calendar", [])
            if str(row.get("learner_id") or "") == learner_id
        ],
        "hours": {
            "recorded_completed_minutes": completed_actual_minutes,
            "recorded_completed_hours": round(completed_actual_minutes / 60, 2),
            "logged_actual_minutes": logged_actual_minutes,
            "logged_actual_hours": round(logged_actual_minutes / 60, 2),
            "actual_time_entries": len(actual_tasks),
            "completed_without_actual_time": len(completed) - len(completed_actual),
            "completed_estimated_minutes": estimated_completed_minutes,
            "scheduled_minutes": scheduled_minutes,
            "scheduled_hours": round(scheduled_minutes / 60, 2),
            "completed_by_category_minutes": {
                category: sum(
                    actual_time(t) for t in completed_actual
                    if str(t.get("category") or t.get("title") or "other") == category
                )
                for category in by_category
            },
            "actual_by_category_minutes": by_category,
        },
        "boundary": (
            "Logged actual minutes are entered separately from planned time. "
            "Task completion alone does not establish instruction hours or mastery. "
            "Recordkeeping preserves what was reported; it does not choose future learning."
        ),
    }
