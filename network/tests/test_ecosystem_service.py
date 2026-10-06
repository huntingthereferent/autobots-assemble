from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.service import EcosystemService


class EcosystemServiceTests(unittest.TestCase):
    def make_service(self, root):
        return EcosystemService(data_dir=Path(root) / "data")

    def test_note_does_not_create_task_or_handoff(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            before = service.status()

            note = service.add_note({
                "body": "School printer paper is getting low.",
                "referent": "household supplies",
                "actor_id": "james",
            })
            after = service.status()

            self.assertTrue(note["note_id"].startswith("note_"))
            self.assertEqual(after["systems"]["personal-operations"]["notes"], 1)
            self.assertEqual(after["systems"]["personal-operations"]["tasks"], 0)
            self.assertEqual(after["runtime"]["handoffs"], before["runtime"]["handoffs"])

    def test_task_stays_local_until_explicit_admission(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            task = service.add_task({
                "title": "Review current repo movement",
                "referent": "Language Network",
                "assignee": "james",
            })

            self.assertIsNone(task["admitted_handoff_id"])
            self.assertEqual(service.status()["runtime"]["handoffs"], 0)
            self.assertEqual(
                service.activate("ohayo", actor_id="james")["items"],
                [],
            )

            handoff = service.admit_task(task["task_id"])

            self.assertEqual(handoff["status"], "READY")
            self.assertEqual(handoff["to_actor"], "james")
            self.assertEqual(service.status()["runtime"]["handoffs"], 1)
            self.assertEqual(
                [x["title"] for x in service.activate("ohayo", actor_id="james")["items"]],
                ["Review current repo movement"],
            )

    def test_complete_requires_admissible_evidence(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            task = service.add_task({
                "title": "Evidence task",
                "referent": "test",
                "assignee": "james",
            })
            handoff = service.admit_task(task["task_id"])

            with self.assertRaisesRegex(ValueError, "COMPLETE requires evidence"):
                service.return_result(
                    handoff["handoff_id"],
                    {"status": "COMPLETE", "output": {"done": True}},
                    actor_id="james",
                )

            self.assertEqual(
                service.list_handoffs()[0]["status"],
                "READY",
            )

    def test_valid_result_reconciles_and_removes_from_ohayo(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            task = service.add_task({
                "title": "Finish this",
                "referent": "test",
                "assignee": "james",
            })
            handoff = service.admit_task(task["task_id"])

            returned = service.return_result(
                handoff["handoff_id"],
                {
                    "status": "COMPLETE",
                    "output": {"done": True},
                    "evidence": [{
                        "condition": "task disposition reported",
                        "kind": "human_report",
                        "source": "james",
                        "depth": "reported",
                    }],
                },
                actor_id="james",
            )

            self.assertEqual(returned["status"], "COMPLETE")
            self.assertEqual(
                service.activate("ohayo", actor_id="james")["items"],
                [],
            )
            stored = service.list_tasks()[0]
            self.assertEqual(stored["result"]["status"], "COMPLETE")

    def test_service_restart_recovers_task_runtime_and_activation(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            task = service.add_task({
                "title": "Survive restart",
                "referent": "James / current day",
                "assignee": "james",
            })
            admitted = service.admit_task(task["task_id"])

            service2 = self.make_service(tmp)

            self.assertEqual(
                service2.list_tasks()[0]["admitted_handoff_id"],
                admitted["handoff_id"],
            )
            self.assertEqual(
                service2.list_handoffs()[0]["status"],
                "READY",
            )
            self.assertEqual(
                [x["title"] for x in service2.activate("ohayo", actor_id="james")["items"]],
                ["Survive restart"],
            )

    def test_plan_stays_plan(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            plan = service.add_plan({
                "title": "Possible morning",
                "referent": "James / current day",
                "actor_id": "james",
                "steps": ["school", "repo", "outside task"],
            })

            self.assertEqual(plan["steps"], ("school", "repo", "outside task"))
            self.assertEqual(len(service.list_plans()), 1)
            self.assertEqual(len(service.list_tasks()), 0)
            self.assertEqual(len(service.list_handoffs()), 0)

    def test_calendar_and_reminders_change_attention_without_creating_work(self):
        from datetime import datetime
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            service.add_reminder({
                "text": "Check the day",
                "actor_id": "james",
                "referent": "James / current day",
                "cadence": "daily",
            })
            service.add_calendar_event({
                "title": "School block",
                "referent": "school / current day",
                "participants": ["james"],
                "starts_at": "2026-10-05T09:30:00-05:00",
            })

            self.assertEqual(service.status()["runtime"]["handoffs"], 0)
            attention = service.attention(
                actor_id="james",
                now=datetime.fromisoformat("2026-10-05T10:00:00-05:00"),
            )
            self.assertEqual([x["text"] for x in attention["reminders"]], ["Check the day"])
            self.assertEqual([x["title"] for x in attention["calendar"]], ["School block"])
            self.assertEqual(attention["tasks"], [])

    def test_unknown_activation_is_not_guessed(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            with self.assertRaises(KeyError):
                service.activate("good morning", actor_id="james")

    def test_invalid_result_state_is_rejected(self):
        with TemporaryDirectory() as tmp:
            service = self.make_service(tmp)
            task = service.add_task({
                "title": "State test",
                "referent": "test",
                "assignee": "james",
            })
            handoff = service.admit_task(task["task_id"])

            with self.assertRaisesRegex(ValueError, "invalid result status"):
                service.return_result(
                    handoff["handoff_id"],
                    {"status": "done"},
                    actor_id="james",
                )


if __name__ == "__main__":
    unittest.main()
