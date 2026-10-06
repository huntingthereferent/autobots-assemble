from __future__ import annotations

from datetime import date, timedelta
import uuid


def _week_start(day: str) -> date:
    d = date.fromisoformat(day)
    return d - timedelta(days=d.weekday())


def _placement_result(learner: dict, subject: str) -> dict:
    placement = learner.get("placement") or {}
    return (placement.get("results") or {}).get(subject) or {}


def _math_focus(learner: dict) -> str:
    result = _placement_result(learner, "mathematics")
    band = str(result.get("start_band") or "foundations")
    return {
        "foundations": "foundation mathematics",
        "secondary": "functions and algebra bridge",
        "advanced": "advanced mathematics",
        "higher": "higher mathematics",
    }.get(band, "foundation mathematics")


def _reading_focus(learner: dict) -> str:
    return "reading comprehension and evidence"


def _writing_focus(learner: dict) -> str:
    return "clear writing with reasons and evidence"


def _research_focus(learner: dict) -> str:
    return "question, claim, evidence, and next investigation"


def _task(*, learner_id: str, day: date, title: str, minutes: int, subject: str,
          week_id: str, phase: str, focus: str, order: int) -> dict:
    key = f"{week_id}:{learner_id}:{day.isoformat()}:{subject}:{phase}:{order}"
    task_uuid = uuid.uuid5(uuid.NAMESPACE_URL, "online-school-week:" + key)
    material_seed = int(task_uuid.hex[:8], 16)
    return {
        "id": str(task_uuid),
        "date": day.isoformat(),
        "title": title,
        "category": subject,
        "kind": "assessment" if phase == "retest" else "instruction",
        "scope": "individual",
        "learner_ids": [learner_id],
        "planned_minutes": minutes,
        "status": "todo",
        "source": "placement" if phase == "retest" else "weekly-itinerary",
        "notes": focus,
        "meta": {
            "required": True,
            "week_id": week_id,
            "week_phase": phase,
            "subject": subject,
            "focus": focus,
            "material_seed": material_seed,
            "material_request": (
                f"Generate fresh {subject.replace('-', ' ')} material for {focus}. "
                f"Week {week_id}; phase {phase}; seed {material_seed}."
            ),
            "calendar_relation": True,
            "day_to_day": True,
            "placement": phase == "retest",
            "placement_subject": subject if phase == "retest" else None,
        },
    }


def generate_week(learner: dict, anchor_day: str) -> dict:
    placement = learner.get("placement") or {}
    if placement.get("status") != "complete":
        return {"week_id": None, "tasks": [], "calendar": [], "ready": False}

    start = _week_start(anchor_day)
    learner_id = str(learner.get("id") or "")
    week_id = f"{learner_id}:{start.isoformat()}"

    focuses = {
        "mathematics": _math_focus(learner),
        "reading": _reading_focus(learner),
        "writing": _writing_focus(learner),
        "science-research": _research_focus(learner),
    }
    minutes = {
        "mathematics": 40,
        "reading": 30,
        "writing": 30,
        "science-research": 40,
    }

    tasks = []
    for offset in range(5):
        current = start + timedelta(days=offset)
        if offset == 4:
            for order, subject in enumerate(focuses, start=1):
                tasks.append(_task(
                    learner_id=learner_id,
                    day=current,
                    title=f"Weekly retest — {subject.replace('-', ' ').title()}",
                    minutes=15,
                    subject=subject,
                    week_id=week_id,
                    phase="retest",
                    focus=f"Recheck the active boundary around {focuses[subject]}.",
                    order=order,
                ))
            continue

        subjects = (
            ("mathematics", "reading"),
            ("writing", "science-research"),
            ("mathematics", "writing"),
            ("reading", "science-research"),
        )[offset]
        for order, subject in enumerate(subjects, start=1):
            tasks.append(_task(
                learner_id=learner_id,
                day=current,
                title=f"{subject.replace('-', ' ').title()} — {focuses[subject]}",
                minutes=minutes[subject],
                subject=subject,
                week_id=week_id,
                phase="learn",
                focus=focuses[subject],
                order=order,
            ))

    calendar = [
        {
            "date": task["date"],
            "relation": task["title"],
            "learner_id": learner_id,
            "week_id": week_id,
            "source": "weekly-itinerary",
        }
        for task in tasks
    ]
    return {
        "week_id": week_id,
        "week_start": start.isoformat(),
        "week_end": (start + timedelta(days=4)).isoformat(),
        "ready": True,
        "tasks": tasks,
        "calendar": calendar,
        "retest_date": (start + timedelta(days=4)).isoformat(),
    }


def _previous_week_closed(state: dict, learner_id: str, start: date) -> bool:
    previous_start = start - timedelta(days=7)
    previous_id = f"{learner_id}:{previous_start.isoformat()}"
    previous = [
        task
        for task in state.get("tasks", [])
        if (task.get("meta") or {}).get("week_id") == previous_id
    ]
    if not previous:
        any_week = any(
            (task.get("meta") or {}).get("week_id")
            and learner_id in task.get("learner_ids", [])
            for task in state.get("tasks", [])
        )
        return not any_week
    retests = [
        task
        for task in previous
        if (task.get("meta") or {}).get("week_phase") == "retest"
    ]
    return bool(retests) and all(task.get("status") == "done" for task in retests)


def generate_all_weeks(state: dict, anchor_day: str) -> tuple[list[dict], list[dict]]:
    tasks = []
    calendar = []
    start = _week_start(anchor_day)
    for learner in state.get("learners", []):
        learner_id = str(learner.get("id") or "")
        if not _previous_week_closed(state, learner_id, start):
            continue
        week = generate_week(learner, anchor_day)
        tasks.extend(week["tasks"])
        calendar.extend(week["calendar"])
    return tasks, calendar
