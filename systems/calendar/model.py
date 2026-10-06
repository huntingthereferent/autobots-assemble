from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

@dataclass(frozen=True)
class CalendarEvent:
    event_id: str
    title: str
    referent: str
    participants: tuple[str, ...] = ()
    kind: str = "event"
    movement_anchor: str = ""
    starts_at: str = ""
    ends_at: str = ""
    due_at: str = ""
    recurrence: str = "none"
    weekdays: tuple[int, ...] = ()
    notes: str = ""
    provenance: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def create(cls, title: str, *, referent: str, participants: tuple[str,...]=(),
               kind: str="event", movement_anchor: str="", starts_at: str="", ends_at: str="", due_at: str="",
               recurrence: str="none", weekdays: tuple[int,...]=(), notes: str="",
               provenance: tuple[str,...]=()) -> "CalendarEvent":
        if not title.strip() or not referent.strip():
            raise ValueError("title and referent are required")
        recurrence=recurrence.strip().lower() or "none"
        if recurrence not in {"none","daily","weekdays","weekly"}:
            raise ValueError("unsupported recurrence")
        if recurrence=="weekly" and not weekdays:
            raise ValueError("weekly recurrence requires weekdays")
        if any(d<0 or d>6 for d in weekdays):
            raise ValueError("weekdays use Monday=0 through Sunday=6")
        for value in (starts_at, ends_at, due_at):
            if value:
                datetime.fromisoformat(value)
        return cls(new_id("cal"), title.strip(), referent.strip(),
                   tuple(x.strip() for x in participants if x.strip()), kind.strip() or "event",
                   movement_anchor.strip().upper(), starts_at.strip(), ends_at.strip(), due_at.strip(), recurrence,
                   tuple(weekdays), notes.strip(),
                   tuple(x.strip() for x in provenance if x.strip()))

    def applies_on(self, now: datetime) -> bool:
        if self.recurrence=="daily": return True
        if self.recurrence=="weekdays": return now.weekday() < 5
        if self.recurrence=="weekly": return now.weekday() in self.weekdays
        dates=[]
        for raw in (self.starts_at,self.due_at):
            if raw: dates.append(datetime.fromisoformat(raw).date())
        return now.date() in dates if dates else False
