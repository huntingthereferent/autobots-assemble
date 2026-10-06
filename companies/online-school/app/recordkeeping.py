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
    done_minutes = sum(int(t.get("planned_minutes") or 0) for t in completed)
    scheduled_minutes = sum(int(t.get("planned_minutes") or 0) for t in tasks)
    by_category = {}
    for task in completed:
        category = str(task.get("category") or task.get("title") or "other")
        by_category[category] = by_category.get(category, 0) + int(task.get("planned_minutes") or 0)

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
            "recorded_completed_minutes": done_minutes,
            "recorded_completed_hours": round(done_minutes / 60, 2),
            "scheduled_minutes": scheduled_minutes,
            "scheduled_hours": round(scheduled_minutes / 60, 2),
            "completed_by_category_minutes": by_category,
        },
        "boundary": "Recordkeeping preserves what happened; it does not choose future learning.",
    }
