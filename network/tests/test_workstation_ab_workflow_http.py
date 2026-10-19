"""Local HTTP bridge from existing native A/B source records to pinned branches."""
from __future__ import annotations

from hashlib import sha256
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/ab-provenance/src"))
from systems.workspace.workflow_editor_server import handler_for


class ABWorkflowHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            handler_for(ROOT, Path(self.temp.name), "local-test-token"))
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def request(self, route, payload=None, auth=True):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        headers = {}
        if payload is not None:
            headers["Content-Type"] = "application/json"
            if auth:
                headers["Origin"] = f"http://127.0.0.1:{self.server.server_port}"
                headers["X-Workstation-Token"] = "local-test-token"
        conn.request("POST" if payload is not None else "GET", route,
                     json.dumps(payload) if payload is not None else None, headers)
        result = conn.getresponse()
        obj = json.loads(result.read())
        code = result.status
        conn.close()
        return code, obj

    @staticmethod
    def native_records():
        f = "runtime/pool_evaluator.py"
        return [{"task_id": "native-pool", "native_sources": [
            {"source": f, "sha256": sha256((ROOT/f).read_bytes()).hexdigest()}
        ]}]

    def test_opt_in_evidence_inspection_and_immutable_pin_association(self):
        status, draft = self.request("/api/example")
        self.assertEqual(status, 200)
        payload = {"draft": draft, "source_records": self.native_records(),
                   "step_bindings": {"count": "native-pool"}}
        status, report = self.request("/api/ab-preview", payload)
        self.assertEqual(status, 200)
        self.assertEqual(report["record"]["unbound_steps"], ["alternative", "describe"])
        self.assertEqual(report["record"]["relation_scope"], "SOURCE_REFERENCES_ONLY")
        self.assertFalse(report["record"]["native_result_verified"])
        status, failed = self.request("/api/ab-record", payload)
        self.assertEqual(status, 400)
        self.assertIn("pinned", failed["error"])
        status, pin = self.request("/api/pin", {"draft": draft, "reason": "Original"})
        self.assertEqual(status, 200)
        status, saved = self.request("/api/ab-record", payload)
        self.assertEqual(status, 200)
        self.assertTrue(saved["recorded"])
        self.assertEqual(saved["record"]["draft_revision"], pin["revision"])
        status, links = self.request("/api/ab-links")
        self.assertEqual(status, 200)
        self.assertEqual(len(links), 1)
        status, again = self.request("/api/ab-record", payload)
        self.assertEqual(status, 200)
        self.assertTrue(again["already_present"])

    def test_unverified_and_cross_origin_cannot_claim_or_write(self):
        _, draft = self.request("/api/example")
        payload = {"draft": draft, "source_records": self.native_records(),
                   "step_bindings": {"count": "native-pool"}}
        code, _ = self.request("/api/ab-preview", payload, auth=False)
        self.assertEqual(code, 403)
        payload["source_records"][0]["native_sources"][0]["sha256"] = "0"*64
        code, result = self.request("/api/ab-preview", payload)
        self.assertEqual(code, 400)
        self.assertIn("fingerprint", result["error"])
        self.assertFalse((Path(self.temp.name)/"workflow_ab_source_links.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
