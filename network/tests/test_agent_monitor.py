"""Read-only monitor behavior and local HTTP dashboard checks."""
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import urlopen
import json
import threading
import unittest

from runtime.service import EcosystemService


class MonitorTests(unittest.TestCase):
    def test_idle_snapshot_is_read_only(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=tmp)
            before = tuple(svc.runtime.event_store.all())
            snapshot = svc.monitor(actor_id="james")
            self.assertTrue(snapshot["read_only"])
            self.assertEqual(snapshot["monitor"]["mode"], "idle")
            self.assertEqual(snapshot["counts"]["tasks_open"], 0)
            self.assertEqual(snapshot["counts"]["agents_total"], 0)
            self.assertEqual(snapshot["events"], [])
            self.assertEqual(tuple(svc.runtime.event_store.all()), before)

    def test_task_agent_report_is_not_execution(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=tmp)
            task = svc.add_task({"title": "Audit ARC report",
                                 "referent": "ARC", "assignee": "james"})
            svc.admit_task(task["task_id"])
            activation = svc.ohayo(actor_id="james")
            root = activation["agent_spawned"][0]
            before = tuple(svc.runtime.event_store.all())
            view = svc.monitor(actor_id="james")
            self.assertEqual(view["counts"]["tasks_total"], 1)
            self.assertEqual(view["counts"]["agents_total"], 1)
            self.assertEqual(view["counts"]["agents_ready"], 1)
            self.assertEqual(view["counts"]["agents_active_recorded"], 0)
            self.assertEqual(view["monitor"]["mode"], "waiting_for_evaluator")
            self.assertFalse(view["connections"]["agents"]["ab_evaluator_connected"])
            self.assertEqual(view["agents"][0]["agent_id"], root)
            self.assertEqual(view["agents"][0]["status"], "READY")
            self.assertEqual(len(view["events"]), 2)
            self.assertEqual(tuple(svc.runtime.event_store.all()), before)
            self.assertEqual(svc.monitor(actor_id="james")["counts"], view["counts"])

    def test_event_log_follows_real_reported_result_and_new_birth(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=tmp)
            root = svc.activate_agent({"surface": "begin comparison",
                  "actor_id": "james", "instance_id": "monitor-fixture",
                  "referent": "Observed comparison"})["root"]
            answer = svc.agent_result(root, {
                "actor_id": "external-provider",
                "status": "COMPLETE",
                "output": {"native_result": "recorded"},
                "evidence": [{"condition": "movement witness", "kind": "source",
                              "source": "native-fixture",
                              "ref": "test:native-witness", "depth": "reported"}],
                "next_referent": "Follow-up observation",
            })
            child = answer["step"]["born"][0]
            v = svc.monitor(actor_id="james")
            self.assertEqual(v["counts"]["agents_total"], 2)
            self.assertEqual(v["counts"]["agents_ready"], 1)
            self.assertIn(root, [x["agent_id"] for x in v["agents"]])
            self.assertIn(child, [x["agent_id"] for x in v["agents"]])
            events = [x for x in v["events"] if x["event_type"] == "RESULT"]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["status"], "COMPLETE")
            self.assertIn("test:native-witness", events[0]["evidence_refs"])
            self.assertEqual(v["counts"]["loops_closed"], 0)

    def test_actor_scoping_excludes_other_assignees(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=tmp)
            for actor in ("james", "learner-a"):
                t = svc.add_task({"title": "Task for " + actor,
                                  "referent": "subject", "assignee": actor})
                svc.admit_task(t["task_id"])
            svc.ohayo(actor_id="james")
            james = svc.monitor(actor_id="james")
            other = svc.monitor(actor_id="learner-a")
            self.assertEqual(james["counts"]["tasks_total"], 1)
            self.assertEqual(other["counts"]["tasks_total"], 1)
            self.assertEqual(other["counts"]["agents_total"], 0)
            self.assertTrue(all("learner-a" not in x["label"]
                    for x in james["events"]))
            self.assertTrue(all(x["subject"] == "task" for x in other["events"]))

    def test_limit_and_validation(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=tmp)
            with self.assertRaisesRegex(ValueError, "actor_id"):
                svc.monitor(actor_id=" ")
            for bad in (-1, 0, 101):
                with self.assertRaisesRegex(ValueError, "limit"):
                    svc.monitor(actor_id="james", limit=bad)
            svc.ohayo(actor_id="james")
            self.assertEqual(svc.monitor(actor_id="james", limit=1)["events"], [])

    def test_restart_recovers_unchanged_task_and_agent_counts(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=tmp)
            t = svc.add_task({"title": "Retained",
                              "referent": "Continuity", "assignee": "james"})
            svc.admit_task(t["task_id"])
            svc.ohayo(actor_id="james")
            before = svc.monitor(actor_id="james")
            restarted = EcosystemService(data_dir=tmp)
            after = restarted.monitor(actor_id="james")
            self.assertEqual(after["counts"], before["counts"])
            self.assertEqual([e["event_type"] for e in after["events"]],
                             [e["event_type"] for e in before["events"]])

    def test_real_local_http_snapshot_and_static_assets(self):
        import runtime.http_server as http
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=Path(tmp) / "state")
            task = service.add_task({"title": "Audit",
                "referent": "Continuity", "assignee": "james"})
            service.admit_task(task["task_id"])
            with patch.object(http, "SERVICE", service):
                server = ThreadingHTTPServer(("127.0.0.1", 0), http.Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base = f"http://127.0.0.1:{server.server_port}"
                try:
                    events_before = tuple(service.runtime.event_store.all())
                    with urlopen(base + "/api/monitor?actor=james", timeout=4) as resp:
                        self.assertEqual(resp.status, 200)
                        snapshot = json.load(resp)
                    self.assertEqual(snapshot["counts"]["tasks_open"], 1)
                    self.assertEqual(snapshot["counts"]["agents_total"], 0)
                    self.assertEqual(tuple(service.runtime.event_store.all()),
                                     events_before)
                    for path, fragment in [
                        ("/monitor.html", b"Agent monitor"),
                        ("/monitor.js", b"/api/monitor?actor=james"),
                        ("/monitor.css", b".metrics"),
                    ]:
                        with urlopen(base + path, timeout=4) as resp:
                            self.assertEqual(resp.status, 200)
                            self.assertIn(fragment, resp.read())
                    with urlopen(base + "/api/activate?surface=ohayo&actor=james",
                                 timeout=4) as resp:
                        self.assertEqual(json.load(resp)["agents"], [])
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=4)


if __name__ == "__main__":
    unittest.main()
