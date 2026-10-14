"""Independent read-only *viewer*, sharing the existing workstation and journal.

This is not a new job runtime, scheduler, or execution endpoint. Only local GET
requests are supported. The original ecosystem HTTP entrance is unchanged.
"""
from __future__ import annotations

from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .monitor import workstation_snapshot

ROOT = Path(__file__).resolve().parents[2]
FRONT = ROOT / "runtime" / "http"
DEFAULT_DATA = ROOT / "runtime" / "data"
ASSETS = {"/workstation.html": ("workstation.html", "text/html; charset=utf-8"),
          "/workstation.css": ("workstation.css", "text/css; charset=utf-8"),
          "/workstation.js": ("workstation.js", "text/javascript; charset=utf-8")}


def make_handler(data_dir: str | Path):
    """Construct an explicitly local observer; reading never creates runtime jobs."""
    data = Path(data_dir)

    class WorkstationViewer(BaseHTTPRequestHandler):
        def _send(self, code: int, content: bytes, content_type: str):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(content)

        def _json(self, code: int, value: dict):
            self._send(code, json.dumps(value, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8")

        def do_GET(self):
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                self._json(403, {"error": "local-only viewer"})
                return
            path = urlsplit(self.path).path
            if path == "/api/workstation":
                try:
                    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
                    self._json(200, workstation_snapshot(root=data / "workstation", runtime=runtime,
                                                         workspace_journal=data / "workspace.jsonl"))
                except (OSError, ValueError, TypeError, KeyError):
                    # A changing or unreadable journal is an explicit error, not an empty station.
                    self._json(503, {"error": "workstation state unavailable; no result was inferred"})
                return
            if path == "/":
                path = "/workstation.html"
            if path in ASSETS:
                filename, mime = ASSETS[path]
                p = FRONT / filename
                try:
                    self._send(200, p.read_bytes(), mime)
                except OSError:
                    self._json(503, {"error": "viewer asset unavailable"})
                return
            self._json(404, {"error": "not found"})

        def do_POST(self):
            self._json(405, {"error": "workstation viewer accepts GET only"})

        def log_message(self, fmt, *args):
            pass

    return WorkstationViewer


def main():
    parser = ArgumentParser(description="Local read-only process workstation viewer")
    parser.add_argument("--port", type=int, default=8051)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    print(f"Read-only process workstation: http://127.0.0.1:{args.port}/workstation.html")
    with ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(args.data_dir)) as host:
        host.serve_forever()


if __name__ == "__main__":
    main()
