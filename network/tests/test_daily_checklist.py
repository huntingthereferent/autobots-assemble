"""Claim checklist is never native handoff completion; deadlines never close tasks."""
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from runtime.daily_checklist import DailyChecklist
from runtime.service import EcosystemService


TZ = ZoneInfo("America/Chicago")


class DailyChecklistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "daily.jsonl"

    def at(self, date):
        return datetime.fromisoformat(date).replace(tzinfo=TZ)

    def test_seed_is_an_evidence_todo_not_a_claim_result(self):
        tasks = DailyChecklist(self.path)
        today = tasks.snapshot(now=self.at("2026-10-09T10:00:00"))
        self.assertEqual(len(today["items"]), 8)
        self.assertEqual(today["pending"], 8)
        self.assertEqual(today["checked_today"], 0)
        self.assertEqual({x["claim_id"] for x in today["items"] if x["claim_id"]},
                         {"ARC-01","ARC-02","ARC-03","AGENT-01","SYS-01","STACK-01","MATH-01"})

    def test_completed_stays_today_disappears_next_day_unfinished_never_expires(self):
        tasks = DailyChecklist(self.path)
        day = self.at("2026-10-09T23:50:00")
        tasks.check("claim-arc-01", True, now=day)
        visible = tasks.snapshot(now=day)
        self.assertEqual(visible["checked_today"], 1)
        self.assertTrue(next(x for x in visible["items"] if x["id"] == "claim-arc-01")["checked"])
        tomorrow = tasks.snapshot(now=self.at("2026-10-10T00:02:00"))
        self.assertFalse(any(x["id"] == "claim-arc-01" for x in tomorrow["items"]))
        self.assertEqual(tomorrow["pending"], 7)
        distant = tasks.snapshot(now=self.at("2032-01-01T12:00:00"))
        self.assertEqual(distant["pending"], 7)
        self.assertEqual(distant["archived_count"], 1)
        reloaded = DailyChecklist(self.path)
        self.assertEqual(reloaded.snapshot(now=self.at("2032-01-01T12:00:00"))["pending"], 7)
        self.assertEqual(reloaded.snapshot(now=day)["checked_today"], 1)

    def test_uncheck_today_and_idempotent_checks(self):
        tasks = DailyChecklist(self.path)
        now = self.at("2026-10-09T10:00:00")
        original_events = tasks.snapshot(now=now)["history_events"]
        tasks.check("claim-arc-02", True, now=now)
        tasks.check("claim-arc-02", True, now=now)
        self.assertEqual(tasks.snapshot(now=now)["history_events"], original_events + 1)
        tasks.check("claim-arc-02", False, now=now)
        self.assertEqual(tasks.snapshot(now=now)["pending"], 8)
        with self.assertRaisesRegex(KeyError, "missing"):
            tasks.check("missing", True, now=now)

    def test_checklist_does_not_admit_agent_handoffs(self):
        svc = EcosystemService(data_dir=Path(self.tmp.name) / "service")
        self.assertEqual(svc.status()["runtime"]["handoffs"], 0)
        self.assertEqual(svc.daily_checklist_snapshot()["pending"], 8)
        svc.set_daily_checklist_checked("claim-agent-01", checked=True)
        self.assertEqual(svc.status()["runtime"]["handoffs"], 0)
        svc.add_daily_checklist_item({"title": "Investigate a new error"})
        self.assertEqual(svc.status()["runtime"]["handoffs"], 0)

    def test_input_rejection_and_checklist_log_survives(self):
        tasks = DailyChecklist(self.path)
        with self.assertRaises(ValueError):
            tasks.create(" ")
        with self.assertRaises(ValueError):
            tasks.create("x" * 281)
        day = self.at("2026-10-09T23:00:00")
        tasks.check("claim-math-01", True, now=day)
        with self.assertRaisesRegex(ValueError, "past-day"):
            tasks.check("claim-math-01", False, now=self.at("2026-10-10T01:00:00"))
        events = [json.loads(x) for x in self.path.read_text().splitlines()]
        self.assertEqual(events[-1]["event"], "CHECK")
        self.assertEqual(DailyChecklist(self.path).snapshot(now=day)["checked_today"], 1)


if __name__ == "__main__":
    unittest.main()
