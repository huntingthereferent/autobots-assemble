from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
import json
import re
import uuid


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE_PATH = ROOT / "operations" / "schedule_template.json"
THEMES_PATH = ROOT / "operations" / "theme_weeks.json"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_schedule():
    return load_json(SCHEDULE_PATH, {})


def load_themes():
    return load_json(THEMES_PATH, {"weeks": []})


def iso_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "task"


def task_id(day: str, scope: str, activity: str, learner_ids: list[str]) -> str:
    key = f"{day}|{scope}|{activity}|{','.join(sorted(learner_ids))}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "online-school:" + key))


def theme_for_day(day: str, themes: dict) -> dict:
    for week in themes.get("weeks", []):
        for item in week.get("days", []):
            if item.get("date") == day:
                return {
                    "theme": item.get("theme"),
                    "math": item.get("math"),
                    "math_mode": item.get("math_mode"),
                    "week": week.get("label"),
                }
    return {}


def make_task(
    *,
    day: str,
    activity: str,
    minutes: int | None,
    scope: str,
    learner_ids: list[str],
    source: str,
    theme: dict,
    notes: str | None = None,
    kind: str = "instruction",
    metadata: dict | None = None,
):
    task = {
        "id": task_id(day, scope, activity, learner_ids),
        "date": day,
        "title": activity,
        "category": slug(activity),
        "kind": kind,
        "scope": scope,
        "learner_ids": learner_ids,
        "planned_minutes": minutes,
        "status": "todo",
        "source": source,
        "notes": notes or "",
        "meta": dict(metadata or {}),
    }
    if theme.get("theme"):
        task["meta"]["theme"] = theme["theme"]
    if activity == "mathematics":
        if theme.get("math"):
            task["notes"] = theme["math"]
        if theme.get("math_mode"):
            task["meta"]["math_mode"] = theme["math_mode"]
    return task


def generate_tasks_for_day(day: str, schedule: dict | None = None, themes: dict | None = None):
    schedule = schedule or load_schedule()
    themes = themes or load_themes()
    current = iso_day(day)
    weekday = current.weekday()
    if weekday > 4:
        return []

    tracks = schedule.get("individualized_tracks", [])
    learner_ids = [track["id"] for track in tracks]
    theme = theme_for_day(day, themes)
    tasks = []

    for track in tracks:
        track_id = track["id"]
        for block in track.get("weekday_blocks", []):
            tasks.append(
                make_task(
                    day=day,
                    activity=block["activity"],
                    minutes=block.get("minutes"),
                    scope="individual",
                    learner_ids=[track_id],
                    source="schedule_template:individualized_tracks",
                    theme=theme,
                    metadata={
                        key: value
                        for key, value in block.items()
                        if key not in {"activity", "minutes"}
                    },
                )
            )

    for block in schedule.get("shared_weekday_blocks", []):
        tasks.append(
            make_task(
                day=day,
                activity=block["activity"],
                minutes=block.get("minutes"),
                scope="shared",
                learner_ids=learner_ids,
                source="schedule_template:shared_weekday_blocks",
                theme=theme,
                metadata={
                    key: value
                    for key, value in block.items()
                    if key not in {"activity", "minutes"}
                },
            )
        )

    if weekday in {0, 2, 4}:
        for block in schedule.get("mwf_blocks", []):
            tasks.append(
                make_task(
                    day=day,
                    activity=block["activity"],
                    minutes=block.get("minutes"),
                    scope="shared",
                    learner_ids=learner_ids,
                    source="schedule_template:mwf_blocks",
                    theme=theme,
                    metadata={
                        key: value
                        for key, value in block.items()
                        if key not in {"activity", "minutes"}
                    },
                )
            )

    if weekday == 2:
        for block in schedule.get("wednesday_blocks", []):
            tasks.append(
                make_task(
                    day=day,
                    activity=block["activity"],
                    minutes=block.get("minutes"),
                    scope="shared",
                    learner_ids=learner_ids,
                    source="schedule_template:wednesday_blocks",
                    theme=theme,
                    metadata={
                        key: value
                        for key, value in block.items()
                        if key not in {"activity", "minutes"}
                    },
                )
            )

    return tasks


def generate_tasks(start: str, end: str):
    start_day = iso_day(start)
    end_day = iso_day(end)
    if end_day < start_day:
        raise ValueError("end must be on or after start")
    if (end_day - start_day).days > 90:
        raise ValueError("generation range is limited to 90 days")

    schedule = load_schedule()
    themes = load_themes()
    rows = []
    cursor = start_day
    while cursor <= end_day:
        rows.extend(generate_tasks_for_day(cursor.isoformat(), schedule, themes))
        cursor += timedelta(days=1)
    return rows


def merge_generated(existing: list[dict], generated: list[dict]):
    by_id = {item["id"]: item for item in existing}
    added = 0
    for task in generated:
        if task["id"] not in by_id:
            by_id[task["id"]] = task
            added += 1
    return list(by_id.values()), added


def validate_task(payload: dict):
    title = str(payload.get("title", "")).strip()
    day = str(payload.get("date", "")).strip()
    if not title:
        raise ValueError("title is required")
    iso_day(day)

    minutes = payload.get("planned_minutes")
    if minutes is not None:
        minutes = int(minutes)
        if minutes < 0 or minutes > 24 * 60:
            raise ValueError("planned_minutes must be between 0 and 1440")

    learners = payload.get("learner_ids", [])
    if not isinstance(learners, list):
        raise ValueError("learner_ids must be a list")

    return {
        "id": str(payload.get("id") or uuid.uuid4()),
        "date": day,
        "title": title,
        "category": str(payload.get("category") or slug(title)),
        "kind": str(payload.get("kind") or "instruction"),
        "scope": str(payload.get("scope") or "custom"),
        "learner_ids": [str(x) for x in learners],
        "planned_minutes": minutes,
        "status": str(payload.get("status") or "todo"),
        "source": str(payload.get("source") or "manual"),
        "notes": str(payload.get("notes") or ""),
        "meta": payload.get("meta") if isinstance(payload.get("meta"), dict) else {},
    }
