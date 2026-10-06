from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Any
import json
from .model import CalendarEvent, utc_now

class CalendarStore:
    def __init__(self,path: str|Path|None=None):
        self.path=Path(path) if path else None
        self._events=[]
        self._calendar={}
        if self.path and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    e=json.loads(line); self._events.append(e); self._replay(e)

    def _replay(self,event):
        p=event["payload"]
        if event["event_type"]=="CALENDAR_EVENT_ADDED":
            self._calendar[p["event_id"]]=CalendarEvent(**{**p,
                "participants":tuple(p.get("participants",())),
                "weekdays":tuple(p.get("weekdays",())),
                "provenance":tuple(p.get("provenance",()))})

    def _append(self,event):
        self._events.append(event); self._replay(event)
        if self.path:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open("a",encoding="utf-8") as h: h.write(json.dumps(event,ensure_ascii=False)+"\n")

    def add(self,event: CalendarEvent)->CalendarEvent:
        self._append({"event_type":"CALENDAR_EVENT_ADDED","occurred_at":utc_now(),"payload":asdict(event)})
        return event

    def events_for(self, actor_id: str, *, now):
        return tuple(e for e in self._calendar.values()
                     if (not e.participants or actor_id in e.participants) and e.applies_on(now))

    def events(self): return tuple(self._calendar.values())
