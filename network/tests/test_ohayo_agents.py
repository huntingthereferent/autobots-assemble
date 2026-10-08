"""Ohayo reports agent lineage and seeds one task agent only when none exists."""
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import urlopen, Request
import json
import threading
import unittest

from runtime.handoff import Handoff, EvidenceRecord
from runtime.service import EcosystemService


class OhayoAgentTests(unittest.TestCase):
    def make_service(self, tmp, **kwargs):
        return EcosystemService(data_dir=Path(tmp) / "data", **kwargs)

    def task(self, svc, *, title="Review existing report"):
        row = svc.add_task({
            "title": title,
            "assignee": "james",
            "referent": "Continuity / current work",
            "required_relation": "review admitted work",
        })
        return svc.admit_task(row["task_id"])

    def test_empty_stays_idle_and_unadmitted_work_is_not_invented(self):
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            svc.add_note({"body": "Possible note", "actor_id": "james"})
            svc.add_plan({"title": "Possible plan", "actor_id": "james",
                          "referent": "planning"})
            svc.add_task({"title": "Not admitted", "referent": "later",
                          "assignee": "james"})
            original = len(svc.runtime.event_store.all())
            for _ in range(3):
                report = svc.ohayo(actor_id="james")
                self.assertEqual(report["agent_spawned"], [])
                self.assertEqual(report["agents"], [])
                self.assertEqual(report["tasks"], [])
                self.assertEqual(report["agent_summary"]["total"], 0)
            self.assertEqual(len(svc.runtime.event_store.all()), original)

    def test_one_seed_for_admitted_tasks_then_only_report(self):
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            first = self.task(svc, title="First task")
            second = self.task(svc, title="Second task")
            report = svc.ohayo(actor_id="james")
            self.assertEqual(len(report["agent_spawned"]), 1)
            root = report["agent_spawned"][0]
            agent = svc.runtime.get(root)
            self.assertEqual(agent.metadata["birth_reason"], "ohayo_task_seed")
            self.assertEqual(agent.from_actor, "james")
            self.assertEqual(agent.to_actor, "agent-ab")
            self.assertEqual([t["handoff_id"] for t in agent.inputs["task_handoffs"]],
                             [first["handoff_id"], second["handoff_id"]])
            self.assertEqual(report["agent_summary"]["ready"], 1)
            self.assertEqual(len(report["tasks"]), 2)
            self.assertFalse(report["agent_evaluator_connected"])
            events = len(svc.runtime.event_store.all())
            again = svc.ohayo(actor_id="james")
            self.assertEqual(again["agent_spawned"], [])
            self.assertEqual(again["agent_roots"], [root])
            self.assertEqual(len(svc.runtime.event_store.all()), events)
            third = self.task(svc, title="Admitted later")
            later = svc.ohayo(actor_id="james")
            self.assertEqual(later["agent_spawned"], [])
            self.assertEqual(len(later["tasks"]), 3)
            # The original snapshot is provenance, not magically mutable inputs.
            self.assertNotIn(third["handoff_id"],
                             [x["handoff_id"] for x in agent.inputs["task_handoffs"]])

    def test_restart_retains_seed_and_never_seeds_twice(self):
        with TemporaryDirectory() as tmp:
            first = self.make_service(tmp)
            self.task(first)
            root = first.ohayo(actor_id="james")["agent_spawned"][0]
            second = self.make_service(tmp)
            before = len(second.runtime.event_store.all())
            report = second.ohayo(actor_id="james")
            self.assertEqual(report["agent_roots"], [root])
            self.assertEqual(report["agent_spawned"], [])
            self.assertEqual(len(second.runtime.event_store.all()), before)

    def test_existing_lineage_from_comparison_is_reported_not_replaced(self):
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            self.task(svc)
            root = svc.activate_agent({
                "surface": "begin comparison",
                "actor_id": "james", "instance_id": "already-live",
                "referent": "ARC relation",
            })["root"]
            count = len(svc.runtime.event_store.all())
            report = svc.ohayo(actor_id="james")
            self.assertEqual(report["agent_spawned"], [])
            self.assertEqual(report["agent_roots"], [root])
            self.assertEqual(report["agents"][0]["referent"], "ARC relation")
            self.assertEqual(len(svc.runtime.event_store.all()), count)

    def test_agent_children_and_events_appear_in_report(self):
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            self.task(svc)
            root = svc.ohayo(actor_id="james")["agent_spawned"][0]
            outcome = svc.agent_result(root, {
                "actor_id": "external-ab-provider",
                "status": "COMPLETE",
                "output": {"relation": "native comparison recorded"},
                "evidence": [{"condition": "movement witness", "kind": "source",
                              "source": "external comparison", "ref": "native:fixture",
                              "depth": "reported"}],
                "next_referent": "New comparison",
            })
            child = outcome["step"]["born"][0]
            report = svc.ohayo(actor_id="james")
            self.assertEqual(report["agent_spawned"], [])
            self.assertEqual(report["agent_summary"]["total"], 2)
            self.assertEqual(report["agent_summary"]["ready"], 1)
            self.assertEqual(report["agent_summary"]["complete"], 1)
            self.assertIn(child, [x["agent_id"] for x in report["agents"]])
            self.assertTrue(any(x["event"] == "RESULT" and x["agent_id"] == root
                                for x in report["agent_activity"]))
            self.assertEqual(report["agent_summary"]["closed_loops"], 0)

    def test_multiple_system_handoffs_not_only_personal_tasks(self):
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            admitted = Handoff(
                handoff_id="school-james-assignment",
                referent="Online School", from_actor="school",
                to_actor="james", required_relation="review learner map",
                metadata={"title": "Inspect school placement"},
            )
            svc.runtime.submit(admitted)
            report = svc.ohayo(actor_id="james")
            self.assertEqual(len(report["agent_spawned"]), 1)
            root = report["agent_spawned"][0]
            self.assertEqual(svc.runtime.get(root).inputs["task_handoffs"][0]["handoff_id"],
                             "school-james-assignment")

    def test_wrong_actor_cannot_run_james_ohayo(self):
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            with self.assertRaises(KeyError):
                svc.ohayo(actor_id="dessy")
            self.assertEqual(svc.agent_lineage.roots_for_actor("dessy"), ())

    def test_get_is_read_only_and_post_is_idempotent(self):
        import runtime.http_server as http
        with TemporaryDirectory() as tmp:
            svc = self.make_service(tmp)
            self.task(svc)
            with patch.object(http, "SERVICE", svc):
                server = ThreadingHTTPServer(("127.0.0.1", 0), http.Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                url = f"http://127.0.0.1:{server.server_port}"
                def get(path):
                    with urlopen(url + path, timeout=4) as response:
                        return json.load(response)
                def post(path, payload):
                    req = Request(url + path, data=json.dumps(payload).encode(),
                                  headers={"Content-Type": "application/json"})
                    with urlopen(req, timeout=4) as response:
                        return json.load(response)
                try:
                    read_only = get("/api/activate?surface=ohayo&actor=james")
                    self.assertEqual(read_only["agents"], [])
                    self.assertEqual(read_only["agent_spawned"], [])
                    self.assertEqual(len(svc.agent_lineage.roots_for_actor("james")), 0)
                    first = post("/api/ohayo", {"actor_id": "james"})
                    self.assertEqual(len(first["agent_spawned"]), 1)
                    second = post("/api/ohayo", {"actor_id": "james"})
                    self.assertEqual(second["agent_spawned"], [])
                    self.assertEqual(second["agent_roots"], first["agent_roots"])
                    observed = get("/api/activate?surface=ohayo&actor=james")
                    self.assertEqual(observed["agent_roots"], first["agent_roots"])
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=4)


if __name__ == "__main__":
    unittest.main()
