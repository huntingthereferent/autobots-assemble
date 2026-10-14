"""Read-only workstation viewer HTTP behavior; no job-admission routes."""
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json
import unittest

from systems.workspace.view_server import make_handler

ROOT = Path(__file__).resolve().parents[2]


class WorkstationHTTPTests(unittest.TestCase):
    def test_live_local_readonly_endpoint_and_gui(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            host = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(root))
            thread = Thread(target=host.serve_forever, daemon=True)
            thread.start()
            try:
                address = "http://127.0.0.1:" + str(host.server_port)
                with urlopen(address + "/api/workstation", timeout=8) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers["Cache-Control"], "no-store")
                    snapshot = json.loads(response.read().decode("utf-8"))
                self.assertTrue(snapshot["read_only"])
                self.assertEqual(snapshot["counts"]["jobs"], 0)
                self.assertFalse((root / "workstation").exists())
                for path in ("/", "/workstation.html", "/workstation.css", "/workstation.js"):
                    with urlopen(address + path, timeout=8) as response:
                        self.assertEqual(response.status, 200)
                        self.assertTrue(response.read())
                with self.assertRaises(HTTPError) as err:
                    urlopen(Request(address + "/api/workstation", data=b"{}",method="POST",
                                    headers={"Content-Type": "application/json"}), timeout=8)
                self.assertEqual(err.exception.code, 405)
                with self.assertRaises(HTTPError) as err:
                    urlopen(address + "/api/handoffs",timeout=8)
                self.assertEqual(err.exception.code, 404)
                self.assertFalse((root / "runtime.jsonl").exists())
            finally:
                host.shutdown()
                host.server_close()
                thread.join(timeout=3)

    def test_local_gui_contract_and_no_html_injection(self):
        server = (ROOT / "systems/workspace/view_server.py").read_text(encoding="utf-8")
        self.assertIn('"127.0.0.1"', server)
        self.assertIn('workstation viewer accepts GET only', server)
        js = (ROOT / "runtime/http/workstation.js").read_text(encoding="utf-8")
        self.assertIn('fetch("/api/workstation"', js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn('method:"POST"', js)
        self.assertNotIn("eval(", js)
        html = (ROOT / "runtime/http/workstation.html").read_text(encoding="utf-8")
        self.assertIn('id="editions"', html)
        self.assertIn('id="jobs"', html)
        self.assertIn('id="lanes"', html)
        self.assertIn('Read-only observation', html)


if __name__ == "__main__":
    unittest.main()
