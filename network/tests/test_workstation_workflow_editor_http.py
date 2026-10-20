"""Local workflow editor HTTP tests: controlled proposals, no worker execution."""
from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from systems.workspace.workflow_editor_server import ROOT, handler_for


class WorkflowEditorHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            handler_for(ROOT, Path(self.tmp.name), "test-only-not-a-public-token"),
        )
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.tmp.cleanup()

    def fetch(self, method, route, payload=None, *, authorized=False, origin=None):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=4)
        headers = {}
        if method == "POST":
            headers["Content-Type"] = "application/json"
            if authorized:
                headers["X-Workstation-Token"] = "test-only-not-a-public-token"
                headers["Origin"] = "http://127.0.0.1:" + str(self.port)
            if origin is not None:
                headers["Origin"] = origin
        conn.request(method, route, body=json.dumps(payload) if payload is not None else None,
                     headers=headers)
        response = conn.getresponse()
        data = response.read()
        status = response.status
        conn.close()
        if route == "/" and status == 200:
            return status, data.decode("utf-8")
        return status, json.loads(data.decode("utf-8"))

    def test_editor_page_exists_and_no_execute_route(self):
        status, html = self.fetch("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Workflow Branches", html)
        self.assertIn("test-only-not-a-public-token", html)
        status, _ = self.fetch("POST", "/api/execute", {"draft": {}}, authorized=True)
        self.assertEqual(status, 404)

    def test_needs_origin_and_token_for_mutation(self):
        _, draft = self.fetch("GET", "/api/example")
        status, data = self.fetch("POST", "/api/pin",
                                  {"draft": draft, "reason": "Keep"}, authorized=False)
        self.assertEqual(status, 403)
        self.assertIn("authorization", data["error"])
        status, _ = self.fetch("POST", "/api/pin",
                               {"draft": draft, "reason": "Keep"},
                               authorized=True, origin="https://malicious.example")
        self.assertEqual(status, 403)
        self.assertFalse((Path(self.tmp.name) / "workflow_pins.jsonl").exists())

    def test_actual_graph_preview_and_pin_roundtrip(self):
        _, draft = self.fetch("GET", "/api/example")
        status, report = self.fetch("POST", "/api/preview",
                                    {"draft": draft}, authorized=True)
        self.assertEqual(status, 200)
        self.assertFalse(report["execution_authorized"])
        self.assertEqual(report["contract_check"], "STRUCTURAL_ONLY")
        self.assertFalse((Path(self.tmp.name) / "runtime.jsonl").exists())

        status, saved = self.fetch("POST", "/api/pin",
                                   {"draft": draft, "reason": "First local workflow"},
                                   authorized=True)
        self.assertEqual(status, 200)
        self.assertEqual(saved["revision"], report["revision"])
        self.assertEqual(saved["status"], "CANDIDATE")
        status, pins = self.fetch("GET", "/api/pins")
        self.assertEqual(status, 200)
        self.assertEqual(len(pins), 1)
        self.assertFalse(pins[0]["whole_workflow_verified"])
        self.assertFalse((Path(self.tmp.name) / "runtime.jsonl").exists())

    def test_idea_checklist_only_native_active_tasks_and_scoped_worker_proposals(self):
        from runtime.repository_tasks import read_active_work
        tasks = read_active_work(ROOT / "TASKS.md")
        status, ideas = self.fetch("GET", "/api/ideas")
        self.assertEqual(status, 200)
        self.assertEqual([x["idea_id"] for x in ideas], [x.source_id for x in tasks])
        self.assertTrue(all(x["status"] == "SOURCE_RECORDED_NOT_COMPLETED" for x in ideas))
        _, draft = self.fetch("GET", "/api/example")
        _, pinned = self.fetch("POST", "/api/pin",
                               {"draft": draft, "reason": "Known original workflow"},
                               authorized=True)
        idea_id = ideas[0]["idea_id"]
        payload = {"idea_id": idea_id, "revision": pinned["revision"],
                   "worker": "native-worker-A", "reason": "Explicit source association"}
        status, blocked = self.fetch("POST", "/api/idea-bind", payload, authorized=False)
        self.assertEqual(status, 403)
        status, recorded = self.fetch("POST", "/api/idea-bind", payload, authorized=True)
        self.assertEqual(status, 200)
        self.assertTrue(recorded["recorded"])
        status, branches = self.fetch("POST", "/api/idea-branches",
                                      {"idea_id": idea_id}, authorized=True)
        self.assertEqual(status, 200)
        self.assertEqual(len(branches), 1)
        status, view = self.fetch("POST", "/api/idea-frontier", {
            "idea_id": idea_id, "revision": pinned["revision"],
            "worker": "native-worker-A", "step_id": "count",
        }, authorized=True)
        self.assertEqual(status, 200)
        self.assertEqual(view["idea"]["idea_id"], idea_id)
        self.assertEqual(view["visible_branches"], [])
        self.assertFalse(view["claimed_global_worker_visibility"])
        self.assertFalse(view["native_relationships_verified"])
        status, error = self.fetch("POST", "/api/idea-propose", {
            "kind": "HELP", "idea_id": idea_id, "revision": pinned["revision"],
            "worker": "native-worker-A", "step_id": "count",
            "target_revision": "0"*64, "reason": "Unsupported imaginary peer",
        }, authorized=True)
        self.assertEqual(status, 400)
        self.assertIn("not visible", error["error"])
        self.assertFalse((Path(self.tmp.name) / "runtime.jsonl").exists())

    def test_real_handoff_frontier_uses_native_task_owner_and_sources(self):
        from runtime.engine import HandoffRuntime
        from runtime.journal import RuntimeJournal
        from runtime.repository_tasks import admit_active_work, read_active_work
        runtime = HandoffRuntime(event_store=RuntimeJournal(
            Path(self.tmp.name) / "runtime.jsonl"))
        work = read_active_work(ROOT / "TASKS.md")
        admit_active_work(runtime, ROOT / "TASKS.md", actor_id="james")
        status, example = self.fetch("GET", "/api/example")
        self.assertEqual(status, 200)
        status, pinned = self.fetch("POST", "/api/pin",
                                    {"draft": example, "reason": "Native source-bound task"},
                                    authorized=True)
        self.assertEqual(status, 200)
        self.fetch("POST", "/api/idea-bind", {
            "idea_id": work[0].source_id,
            "revision": pinned["revision"],
            "worker": "james",
            "reason": "Explicit source association",
        }, authorized=True)
        before = (Path(self.tmp.name) / "runtime.jsonl").read_bytes()
        req = {"handoff_id": "repo-work-" + work[0].source_id,
               "revision": pinned["revision"], "step_id": "count"}
        status, scoped = self.fetch("POST", "/api/idea-native-frontier",
                                    req, authorized=True)
        self.assertEqual(status, 200)
        self.assertEqual(scoped["native_handoff"]["to_actor"], "james")
        self.assertEqual(scoped["idea"]["idea_id"], work[0].source_id)
        self.assertFalse(scoped["native_handoff"]["actor_identity_authenticated"])
        status, denied = self.fetch("POST", "/api/idea-native-frontier",
                                    req, authorized=False)
        self.assertEqual(status, 403)
        self.assertEqual((Path(self.tmp.name) / "runtime.jsonl").read_bytes(), before)
        status, denial = self.fetch("POST", "/api/idea-native-propose", {
            **req, "kind": "HELP", "target_revision": "0"*64,
            "reason": "Not actually related",
        }, authorized=True)
        self.assertEqual(status, 400)
        self.assertIn("not visible", denial["error"])

    def test_native_peer_help_review_only_local_recipient_and_no_adoption(self):
        from runtime.engine import HandoffRuntime
        from runtime.journal import RuntimeJournal
        from runtime.repository_tasks import admit_active_work, read_active_work
        store = Path(self.tmp.name)
        runtime = HandoffRuntime(event_store=RuntimeJournal(store / "runtime.jsonl"))
        idea = read_active_work(ROOT / "TASKS.md")[0]
        admit_active_work(runtime, ROOT / "TASKS.md", actor_id="james")
        _, original = self.fetch("GET", "/api/example")
        _, root_pin = self.fetch("POST", "/api/pin",
                                 {"draft": original, "reason": "Source root"},
                                 authorized=True)
        one = json.loads(json.dumps(original))
        one["parent_revision"] = root_pin["revision"]
        one["steps"][0]["label"] = "Branch alpha source"
        two = json.loads(json.dumps(original))
        two["parent_revision"] = root_pin["revision"]
        two["steps"][0]["label"] = "Branch beta source"
        _, alpha = self.fetch("POST", "/api/pin",
                              {"draft": one, "reason": "Source alpha"},
                              authorized=True)
        _, beta = self.fetch("POST", "/api/pin",
                             {"draft": two, "reason": "Source beta"},
                             authorized=True)
        for record, worker in ((root_pin, "james"), (alpha, "james"),
                               (beta, "worker-B")):
            code, data = self.fetch("POST", "/api/idea-bind", {
                "idea_id": idea.source_id, "revision": record["revision"],
                "worker": worker, "reason": "Explicit source witness association",
            }, authorized=True)
            self.assertEqual(code, 200, data)
        request = {"idea_id": idea.source_id, "revision": beta["revision"],
                   "step_id": "count", "worker": "worker-B",
                   "target_revision": alpha["revision"], "kind": "HELP",
                   "reason": "Current declared source step differs"}
        code, proposed = self.fetch("POST", "/api/idea-propose", request,
                                    authorized=True)
        self.assertEqual(code, 200, proposed)
        native = {"handoff_id": "repo-work-" + idea.source_id,
                  "revision": alpha["revision"], "step_id": "count"}
        code, view = self.fetch("POST", "/api/idea-native-frontier", native,
                               authorized=True)
        self.assertEqual(code, 200, view)
        self.assertEqual(len(view["incoming_peer_help"]), 1)
        ref = view["incoming_peer_help"][0]["proposal_ref"]
        blocked_request = {**native, "proposal_ref": ref,
                           "decision": "INSPECT", "reason": "Scoped review"}
        code, _ = self.fetch("POST", "/api/idea-native-review",
                             blocked_request, authorized=False)
        self.assertEqual(code, 403)
        code, _ = self.fetch("POST", "/api/idea-native-review",
                             {**blocked_request, "proposal_ref": "0"*64},
                             authorized=True)
        self.assertEqual(code, 400)
        before = (store / "runtime.jsonl").read_bytes()
        code, accepted = self.fetch("POST", "/api/idea-native-review",
                                    blocked_request, authorized=True)
        self.assertEqual(code, 200, accepted)
        self.assertTrue(accepted["recorded"])
        self.assertFalse(accepted["event"]["branch_adopted"])
        self.assertEqual(before, (store / "runtime.jsonl").read_bytes())
        code, again = self.fetch("POST", "/api/idea-native-review",
                                 {**blocked_request, "decision": "DECLINE"},
                                 authorized=True)
        self.assertEqual(code, 400)
        self.assertIn("already reviewed", again["error"])
        code, peer = self.fetch("POST", "/api/idea-frontier", {
            "idea_id": idea.source_id, "revision": beta["revision"],
            "step_id": "count", "worker": "worker-B",
        }, authorized=True)
        self.assertEqual(code, 200, peer)
        self.assertEqual(peer["outgoing_help_reviews"][0]["review"], "INSPECT")
        self.assertFalse(peer["outgoing_help_reviews"][0]["branch_adopted"])

    def test_ui_can_edit_branch_diff_without_running_workers(self):
        _, draft = self.fetch("GET", "/api/example")
        _, parent = self.fetch("POST", "/api/pin",
                               {"draft": draft, "reason": "Baseline"}, authorized=True)
        changed = json.loads(json.dumps(draft))
        changed["parent_revision"] = parent["revision"]
        changed["steps"][0]["label"] = "Alternative original implementation"
        status, report = self.fetch("POST", "/api/diff",
                                    {"draft": changed}, authorized=True)
        self.assertEqual(status, 200)
        self.assertEqual(report["changed_steps"], ["count"])
        self.assertFalse(report["native_verified"])


if __name__ == "__main__":
    unittest.main()
