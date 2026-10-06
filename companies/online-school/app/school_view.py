from __future__ import annotations

from dataclasses import asdict
from typing import Any

from systems.education import EducationKernel
from systems.missouri_curriculum import path_for_grade


DEFAULT_GRADE_CONTEXT = {
    "track_a": "3",
    "track_b": "1",
}


def learner_grade_context(learner: dict[str, Any]) -> str:
    explicit = str(learner.get("grade_context") or "").strip()
    if explicit:
        return explicit
    return DEFAULT_GRADE_CONTEXT.get(str(learner.get("id") or ""), "")


def build_school_view(
    *,
    state: dict[str, Any],
    day: str,
    kernel: EducationKernel,
) -> dict[str, Any]:
    tasks = [task for task in state.get("tasks", []) if task.get("date") == day]
    worksheets = list(state.get("worksheets", []))
    shared_tasks = [
        task for task in tasks
        if task.get("scope") == "shared" or not task.get("learner_ids")
    ]

    learners = []
    for learner in state.get("learners", []):
        learner_id = str(learner.get("id") or "")
        grade = learner_grade_context(learner)
        relations = [asdict(item) for item in kernel.current_for_person(learner_id)]
        observations = [
            asdict(item) for item in kernel.observations_for_person(learner_id)
        ]

        obligations = []
        if grade:
            try:
                obligations = [
                    {
                        "code": target.code,
                        "unit": target.unit,
                        "title": target.title,
                        "description": target.description,
                        "skill": target.skill,
                        "grade_context": target.grade,
                    }
                    for target in path_for_grade(grade)
                ]
            except ValueError:
                obligations = []

        learner_tasks = [
            task for task in tasks
            if learner_id in task.get("learner_ids", [])
            and task.get("scope") != "shared"
        ]
        learner_worksheets = [
            worksheet
            for worksheet in worksheets
            if str(worksheet.get("learner") or "") in {
                learner_id,
                str(learner.get("display_name") or ""),
            }
        ]

        current_relation = max(
            relations,
            key=lambda item: str(item.get("formed_at") or ""),
            default=None,
        )
        recent_observation = observations[-1] if observations else None
        unfinished = [
            task for task in learner_tasks
            if task.get("status") != "done"
        ]
        unfinished.sort(
            key=lambda task: (
                0 if task.get("source") == "placement" else 1,
                str(task.get("title") or ""),
            )
        )
        shared_unfinished = [
            task for task in shared_tasks
            if task.get("status") != "done"
            and (
                not task.get("learner_ids")
                or learner_id in task.get("learner_ids", [])
            )
        ]
        next_task = (unfinished or shared_unfinished or [None])[0]

        age_raw = learner.get("age")
        try:
            age = int(age_raw) if age_raw not in (None, "") else None
        except (TypeError, ValueError):
            age = None
        adult = age is not None and age >= 18

        learners.append(
            {
                "id": learner_id,
                "display_name": learner.get("display_name") or learner_id,
                "grade_context": grade,
                "age": age,
                "adult": adult,
                "presentation_guardrails": {
                    "age_bounded": not adult,
                    "grade_bounded": not adult,
                },
                "placement": learner.get("placement") or {
                    "status": "required",
                    "completed_subjects": [],
                    "results": {},
                },
                "academic_tools": (
                    [
                        "research",
                        "reading",
                        "notes",
                        "writing",
                        "problem-sets",
                        "projects",
                        "experiments",
                        "sources-citations",
                        "print-worksheets",
                        "artifacts",
                    ]
                    if adult
                    else []
                ),
                "current_relations": relations,
                "observation_count": len(observations),
                "recent_observations": observations[-5:],
                "curriculum_obligations": obligations,
                "today_tasks": learner_tasks,
                "artifacts": learner_worksheets,
                "front": {
                    "learning_now": current_relation,
                    "do_next": next_task,
                    "what_changed": recent_observation,
                },
            }
        )

    return {
        "schema_version": 1,
        "date": day,
        "learners": learners,
        "shared_today": shared_tasks,
        "worksheet_count": len(worksheets),
        "boundaries": [
            "Learner relations come from current evidence, not grade placement.",
            "Grade context constrains obligations/reporting; it does not define current learner state.",
            "Curriculum order is a planning projection, not the learner-path engine.",
            "Tasks and worksheets are educational actuators/artifacts, not proof of mastery.",
        ],
    }
