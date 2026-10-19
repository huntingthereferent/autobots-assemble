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
