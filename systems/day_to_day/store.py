from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
import json

from .model import Reminder, utc_now


class DayToDayStore:
    """Explicit recurring attention state, separated from tasks and notes."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._events: list[dict[str, Any]] = []
        self._reminders: dict[str, Reminder] = {}
        self._acknowledged: set[tuple[str, str]] = set()
        if self.path and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    event = json.loads(line)
                    self._events.append(event)
                    self._replay(event)

    def _append(self, event: dict[str, Any]) -> None:
        self._events.append(event)
        self._replay(event)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _replay(self, event: dict[str, Any]) -> None:
        payload = event["payload"]
        if event["event_type"] == "REMINDER_ADDED":
            self._reminders[payload["reminder_id"]] = Reminder(
                **{
                    **payload,
                    "weekdays": tuple(payload.get("weekdays", ())),
                    "provenance": tuple(payload.get("provenance", ())),
                }
            )
        elif event["event_type"] == "REMINDER_ACKNOWLEDGED":
            self._acknowledged.add((payload["reminder_id"], payload["local_date"]))

    def add_reminder(self, reminder: Reminder) -> Reminder:
        self._append({"event_type": "REMINDER_ADDED", "occurred_at": utc_now(), "payload": asdict(reminder)})
        return reminder

    def acknowledge(self, reminder_id: str, *, local_date: str) -> None:
        if reminder_id not in self._reminders:
            raise KeyError(reminder_id)
        self._append({
            "event_type": "REMINDER_ACKNOWLEDGED",
            "occurred_at": utc_now(),
            "payload": {"reminder_id": reminder_id, "local_date": local_date},
        })

    def due_reminders(self, actor_id: str, *, now: datetime) -> tuple[Reminder, ...]:
        local_date = now.date().isoformat()
        due = [
            reminder for reminder in self._reminders.values()
            if reminder.actor_id == actor_id
            and reminder.is_due(now)
            and (reminder.reminder_id, local_date) not in self._acknowledged
        ]
        return tuple(sorted(due, key=lambda item: (item.local_time or "00:00", item.text.casefold())))

    def reminders(self) -> tuple[Reminder, ...]:
        return tuple(self._reminders.values())

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)
