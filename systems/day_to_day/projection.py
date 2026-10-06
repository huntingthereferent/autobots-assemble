from __future__ import annotations

from datetime import datetime
from typing import Iterable

from runtime.handoff import Handoff, HandoffState
from runtime.projections import task_projection
from .model import Reminder


VISIBLE_STATUSES = {"ACTIVE", "READY", "PARTIAL", "BLOCKED", "WAITING"}


def attention_projection(
    *,
    actor_id: str,
    now: datetime,
    handoffs: Iterable[tuple[Handoff, HandoffState]],
    reminders: Iterable[Reminder] = (),
    calendar_events: Iterable[object] = (),
) -> dict:
    tasks = [
        task_projection(handoff, state)
        for handoff, state in handoffs
        if handoff.to_actor == actor_id and state.status in VISIBLE_STATUSES
    ]
    status_order = {
        "ACTIVE": 0,
        "READY": 1,
        "PARTIAL": 2,
        "BLOCKED": 3,
        "WAITING": 4,
    }
    tasks.sort(
        key=lambda item: (
            status_order.get(item["status"], 99),
            str(item["title"]).casefold(),
        )
    )
    reminder_rows = [
        {
            "id": reminder.reminder_id,
            "text": reminder.text,
            "referent": reminder.referent,
            "local_time": reminder.local_time,
            "cadence": reminder.cadence,
        }
        for reminder in reminders
        if reminder.actor_id == actor_id and reminder.is_due(now)
    ]
    calendar_rows = [
        {
            "id": getattr(event, "event_id", ""),
            "title": getattr(event, "title", ""),
            "referent": getattr(event, "referent", ""),
            "kind": getattr(event, "kind", "event"),
            "starts_at": getattr(event, "starts_at", ""),
            "ends_at": getattr(event, "ends_at", ""),
            "due_at": getattr(event, "due_at", ""),
            "recurrence": getattr(event, "recurrence", "none"),
        }
        for event in calendar_events
    ]
    calendar_rows.sort(
        key=lambda item: (
            item["starts_at"] or item["due_at"] or "9999",
            item["title"].casefold(),
        )
    )
    return {
        "actor_id": actor_id,
        "local_date": now.date().isoformat(),
        "tasks": tasks,
        "reminders": reminder_rows,
        "calendar": calendar_rows,
    }
