from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


@dataclass(frozen=True)
class Reminder:
    reminder_id: str
    actor_id: str
    text: str
    referent: str
    cadence: str = "daily"
    weekdays: tuple[int, ...] = ()
    local_time: str = ""
    provenance: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        text: str,
        *,
        actor_id: str,
        referent: str,
        cadence: str = "daily",
        weekdays: tuple[int, ...] = (),
        local_time: str = "",
        provenance: tuple[str, ...] = (),
    ) -> "Reminder":
        cadence = cadence.strip().lower()
        if cadence not in {"daily", "weekdays", "weekly"}:
            raise ValueError("cadence must be daily, weekdays, or weekly")
        if cadence == "weekly" and not weekdays:
            raise ValueError("weekly reminder requires weekdays")
        if any(day < 0 or day > 6 for day in weekdays):
            raise ValueError("weekdays use Monday=0 through Sunday=6")
        if local_time:
            try:
                hour, minute = (int(x) for x in local_time.split(":", 1))
            except Exception as exc:
                raise ValueError("local_time must be HH:MM") from exc
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("local_time must be HH:MM")
        for name, value in (("text", text), ("actor_id", actor_id), ("referent", referent)):
            if not value.strip():
                raise ValueError(f"{name} is required")
        return cls(
            reminder_id=new_id("rem"),
            actor_id=actor_id.strip(),
            text=text.strip(),
            referent=referent.strip(),
            cadence=cadence,
            weekdays=tuple(weekdays),
            local_time=local_time.strip(),
            provenance=tuple(x.strip() for x in provenance if x.strip()),
        )

    def is_due(self, now: datetime) -> bool:
        weekday = now.weekday()
        if self.cadence == "weekdays" and weekday > 4:
            return False
        if self.cadence == "weekly" and weekday not in self.weekdays:
            return False
        if self.local_time:
            hour, minute = (int(x) for x in self.local_time.split(":", 1))
            if (now.hour, now.minute) < (hour, minute):
                return False
        return True
