"""Append-only daily checklist, distinct from evidence-gated handoffs."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4
from zoneinfo import ZoneInfo
import json
import os

SEED = Path(__file__).with_name("claim_checklist.json")


class DailyChecklist:
    """Pending persists forever; checked today remains visible until next day."""

    def __init__(self, path, *, seed_file=SEED, timezone_name="America/Chicago"):
        self.path = Path(path)
        self.zone = ZoneInfo(timezone_name)
        self.lock = RLock()
        self.items = {}
        self.completed = {}
        self.history = []
        if self.path.exists():
            for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    try:
                        event = json.loads(line)
                        self._apply(event)
                        self.history.append(event)
                    except (ValueError, TypeError, KeyError) as error:
                        raise ValueError(f"bad daily checklist journal line {number}") from error
        seed = json.loads(Path(seed_file).read_text(encoding="utf-8"))
        if seed.get("schema_version") != 1:
            raise ValueError("unknown checklist seed format")
        for row in seed["items"]:
            if row["id"] not in self.items:
                self._append({"event": "ADD", "item": self._normalize(row)})

    @staticmethod
    def _normalize(source):
        item_id = str(source.get("id") or "").strip()
        title = str(source.get("title") or "").strip()
        if not item_id or not title or len(item_id) > 120 or len(title) > 280:
            raise ValueError("valid task ID and title required")
        return {
            "id": item_id, "title": title,
            "detail": str(source.get("detail") or "")[:700],
            "kind": str(source.get("kind") or "personal")[:32],
            "claim_id": str(source.get("claim_id") or "")[:40],
            "source": str(source.get("source") or "")[:650],
        }

    def _apply(self, record):
        kind = record["event"]
        if kind == "ADD":
            task = self._normalize(record["item"])
            if task["id"] in self.items:
                raise ValueError("duplicate task ID")
            self.items[task["id"]] = task
            self.completed[task["id"]] = None
        elif kind in {"CHECK", "UNCHECK"}:
            item_id = record["id"]
            if item_id not in self.items:
                raise KeyError(item_id)
            if kind == "CHECK":
                datetime.strptime(record["day"], "%Y-%m-%d")
                self.completed[item_id] = record["day"]
            else:
                self.completed[item_id] = None
        else:
            raise ValueError("unknown daily checklist event")

    def _append(self, record):
        with self.lock:
            prior_items, prior_done = self.items.copy(), self.completed.copy()
            self._apply(record)
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                event = {**record, "timestamp": datetime.now(timezone.utc).isoformat()}
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(event, ensure_ascii=False) + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                self.history.append(event)
            except Exception:
                self.items, self.completed = prior_items, prior_done
                raise

    def local_day(self, now=None):
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("aware time required")
        return now.astimezone(self.zone).date().isoformat()

    def snapshot(self, *, now=None):
        day = self.local_day(now)
        with self.lock:
            rows = [
                {**task, "checked": self.completed[key] == day}
                for key, task in self.items.items()
                if self.completed[key] is None or self.completed[key] == day
            ]
            rows.sort(key=lambda x: (x["checked"], x["kind"] != "claim", x["id"]))
            return {
                "local_date": day, "timezone": str(self.zone), "items": rows,
                "pending": sum(not x["checked"] for x in rows),
                "checked_today": sum(x["checked"] for x in rows),
                "archived_count": len(self.items) - len(rows),
                "history_events": len(self.history),
            }

    def create(self, title):
        task = self._normalize({"id": "todo-" + uuid4().hex, "title": title})
        self._append({"event": "ADD", "item": task})
        return task

    def check(self, item_id, checked, *, now=None):
        day = self.local_day(now)
        with self.lock:
            if item_id not in self.items:
                raise KeyError(item_id)
            old = self.completed[item_id]
            if checked and old is None:
                self._append({"event": "CHECK", "id": item_id, "day": day})
            elif not checked and old == day:
                self._append({"event": "UNCHECK", "id": item_id})
            elif (checked and old == day) or (not checked and old is None):
                pass  # idempotent request
            else:
                raise ValueError("a past-day completion is archived")
            return {**self.items[item_id], "checked": self.completed[item_id] == day}
