"""Real localhost HTTP integration for the *opt-in* finite branch maze.

Uses the same native Python clock, consent recorder and branch graph.
No worker or crypto keys constructed by the browser module.
"""
from __future__ import annotations

from http.client import HTTPConnection
from pathlib import Path
import json
import threading
import time
import unittest

from security.branch_browser import BranchBrowserServer
from security.branch_world import audit_graph


class LocalMazeBrowserTests(unittest.TestCase):
    def setUp(self):
        self.server = BranchBrowserServer(("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)
        self.server.start_presence()
        self.thread.start()
        self.addCleanup(self._stop)
        self.token = None

    def _stop(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()
        self.assertFalse(self.server.presence.running)

    def request(self, method, path, payload=None, *,
                headers=None, token=None, origin=True):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        extras = dict(headers or {})
        if origin and method == "POST":
            extras.setdefault("Origin", self.server.local_origin)
        if (token if token is not None else self.token) is not None:
            extras.setdefault("X-AB-Session",
                              token if token is not None else self.token)
        raw = None
        if payload is not None:
            raw = (payload if isinstance(payload, bytes) else
                   json.dumps(payload).encode("utf-8"))
            extras.setdefault("Content-Type", "application/json")
        try:
            conn.request(method, path, body=raw, headers=extras)
            response = conn.getresponse()
            data = response.read()
            mime = response.getheader("Content-Type") or ""
            if "application/json" in mime:
                return response.status, json.loads(data.decode("utf-8")), dict(response.getheaders())
            return response.status, data.decode("utf-8"), dict(response.getheaders())
        finally:
            conn.close()

    def enroll(self):
        status, body, _ = self.request("POST", "/api/consent", {"accepted": True})
        self.assertEqual(status, 200)
        self.token = body["session"]
        self.assertEqual(body["start"], "threshold")
        return self.token

    def test_public_page_and_js_only_without_any_session_or_key_data(self):
        status, html, headers = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Branch", html)
        self.assertIn("I agree", html)
        self.assertIn("local", html.lower())
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(headers["Cache-Control"], "no-store")
        status, js, _ = self.request("GET", "/maze.js")
        self.assertEqual(status, 200)
        self.assertIn('textContent', js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("eval(", js)
        self.assertNotIn("os.system", js)
        self.assertEqual(self.server.recorder.operator_snapshot(), ())

    def test_consent_required_for_all_session_actions(self):
        for method, path, body in (
            ("GET", "/api/state", None),
            ("GET", "/api/transcript", None),
            ("POST", "/api/submit", {"message": "hello", "exit_choice": "along"}),
            ("POST", "/api/erase", {}),
        ):
            with self.subTest(path=path):
                self.assertEqual(self.request(method, path, body)[0], 403)
        self.assertEqual(
            self.request("POST", "/api/consent", {"accepted": False})[0], 403)
        self.assertEqual(
            self.request("POST", "/api/consent", {"accepted": 1})[0], 403)
        self.assertEqual(self.server.recorder.operator_snapshot(), ())

    def test_real_presence_ticks_without_a_single_submitted_message(self):
        self.enroll()
        a = self.request("GET", "/api/state")[1]
        deadline = time.monotonic() + 2
        b = a
        while time.monotonic() < deadline:
            b = self.request("GET", "/api/state")[1]
            if b["presence"] >= a["presence"] + 3:
                break
            time.sleep(0.02)
        self.assertGreaterEqual(b["presence"], a["presence"] + 3)
        self.assertEqual(a["node"], "threshold")
        self.assertEqual(b["node"], "threshold")
        self.assertEqual(self.request("GET", "/api/transcript")[1]["records"], [])
        snap = self.server.boundary.snapshot()
        self.assertEqual(snap.approach_movements, 0)
        self.assertEqual(snap.protected_movements, 0)
        self.assertEqual(snap.admitted_movements, 0)

    def test_browser_submit_along_side_reads_movement_without_moving_it(self):
        self.enroll()
        before = self.server.boundary.snapshot()
        status, body, _ = self.request(
            "POST", "/api/submit", {"message": "hello branch", "exit_choice": "along"})
        self.assertEqual(status, 200)
        branch = body["branch"]
        self.assertIn(branch["branch_node"], {"hallway", "mirror"})
        self.assertEqual(len(branch["exits"]), 2)
        self.assertIn("branch", branch["branch_words"].lower())
        status, body, _ = self.request(
            "POST", "/api/submit", {"message": "python print(1)", "exit_choice": "side"})
        self.assertEqual(status, 200)
        self.assertEqual(body["branch"]["form"], "python")
        self.assertIn("fictional Python branch", body["branch"]["branch_words"])
        trail = self.request("GET", "/api/transcript")[1]["records"]
        self.assertEqual(len(trail), 2)
        self.assertEqual([row["message"] for row in trail],
                         ["hello branch", "python print(1)"])
        after = self.server.boundary.snapshot()
        self.assertGreaterEqual(after.presence_movements, before.presence_movements)
        self.assertEqual(after.approach_movements, 0)
        self.assertEqual(after.protected_movements, 0)
        self.assertEqual(after.admitted_movements, 0)
        self.assertEqual(audit_graph()["terminal_nodes"], 0)

    def test_injection_shaped_text_is_inert_json_not_html_or_execution(self):
        self.enroll()
        attack = '<img src=x onerror=alert(1)> eval("danger")'
        status, body, _ = self.request(
            "POST", "/api/submit",
            {"message": attack, "exit_choice": "along"})
        self.assertEqual(status, 200)
        branch = body["branch"]
        self.assertEqual(branch["message"], attack)
        self.assertEqual(branch["form"], "instruction")
        self.assertNotIn(attack, branch["branch_words"])
        self.assertEqual(self.server.boundary.snapshot().protected_movements, 0)
        self.assertNotIn(attack, self.request("GET", "/")[1])

    def test_same_origin_enforced_on_mutations(self):
        for headers, origin in (
            ({"Origin": "https://attacker.invalid"}, False),
            ({}, False),
            ({"Sec-Fetch-Site": "cross-site"}, True),
            ({"Host": "attacker.invalid"}, True),
            ({"Host": "localhost:8080"}, True),
            ({"Transfer-Encoding": "chunked"}, True),
        ):
            with self.subTest(headers=headers, origin=origin):
                status, _, _ = self.request(
                    "POST", "/api/consent", {"accepted": True},
                    headers=headers, origin=origin)
                self.assertEqual(status, 403)
        self.assertEqual(self.server.recorder.operator_snapshot(), ())

    def test_bad_json_oversized_and_wrong_endpoints_fail_closed(self):
        self.enroll()
        cases = (
            b'{"message":"one","message":"two","exit_choice":"along"}',
            b'{"message":NaN,"exit_choice":"along"}',
            b'{"message":"ok","exit_choice":"../secret"}',
            b'{"message":"ok","exit_choice":"keys"}',
            b'[]', b'x' * 3000,
        )
        for payload in cases:
            with self.subTest(body=payload[:25]):
                self.assertEqual(self.request("POST", "/api/submit", payload)[0], 400)
        self.assertEqual(self.request(
            "POST", "/api/submit",
            {"message": "hello", "exit_choice": "along"},
            headers={"Content-Type": "text/plain"})[0], 400)
        self.assertEqual(self.request("GET", "/api/workers")[0], 404)
        self.assertEqual(self.request("POST", "/api/keys", {})[0], 404)
        self.assertEqual(self.request("POST", "/api/erase", {"other": True})[0], 400)
        self.assertEqual(self.server.recorder.operator_snapshot(), ())
        self.assertEqual(self.server.boundary.snapshot().approach_movements, 0)

    def test_erasure_revokes_session_and_deletes_entire_transcript(self):
        token = self.enroll()
        self.request("POST", "/api/submit", {"message": "first", "exit_choice": "side"})
        self.assertEqual(len(self.server.recorder.operator_snapshot()), 1)
        code, erased, _ = self.request("POST", "/api/erase", {})
        self.assertEqual((code, erased), (200, {"erased": True}))
        self.assertEqual(self.server.recorder.operator_snapshot(), ())
        self.assertEqual(self.request("GET", "/api/state", token=token)[0], 403)
        self.assertEqual(self.request("GET", "/api/transcript", token=token)[0], 403)
        self.assertEqual(self.request("POST", "/api/erase", {}, token=token)[0], 403)

    def test_client_cannot_bind_public_interface(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            BranchBrowserServer(("0.0.0.0", 0))
        with self.assertRaisesRegex(ValueError, "loopback"):
            BranchBrowserServer(("localhost", 0))
        with self.assertRaisesRegex(ValueError, "loopback"):
            BranchBrowserServer(("127.0.0.2", 0))


if __name__ == "__main__":
    unittest.main()
