"""Opt-in browser entrance for the *fictional* A/B story graph.

Dedicated loopback-only HTTP service. NO workstation service, key material,
filesystem browser, remote deployment, shell, or worker execution. A session
begins only when the participant explicitly accepts the research notice.
The native monotonic presence clock is independently owned by the host.
"""
from __future__ import annotations

from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
from ipaddress import ip_address

from .approach_dialogue import ConsentApproachRecorder, NOTICE
from .branch_world import START, branch_view
from .key_approach import KeyApproachBoundary, NativePresenceRunner

ROOT = Path(__file__).resolve().parent
MAX_JSON = 2048
JSON_TYPE = "application/json"


def _unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate input field")
        result[key] = value
    return result


def _reject_nonfinite(_):
    raise ValueError("nonfinite JSON")


class BranchBrowserServer(HTTPServer):
    """Inert construction; external binds rejected before any listen."""

    allow_reuse_address = False

    def __init__(self, address=("127.0.0.1", 0)):
        host, port = address
        if host != "127.0.0.1" or type(port) is not int or not 0 <= port <= 65535:
            raise ValueError("fictional maze browser binds only IPv4 loopback")
        self.boundary = KeyApproachBoundary()
        self.recorder = ConsentApproachRecorder(self.boundary)
        self.presence = NativePresenceRunner(self.boundary, interval_seconds=0.04)
        super().__init__(address, BranchBrowserHandler)

    @property
    def local_origin(self):
        return f"http://127.0.0.1:{self.server_port}"

    def start_presence(self):
        self.presence.start()

    def stop_presence(self):
        self.presence.stop()

    def server_close(self):
        # Explicitly clear consented text in memory, and stop only our own
        # research thread; no lifecycle contact with the workstation.
        try:
            self.stop_presence()
        finally:
            self.recorder.clear_all()
            super().server_close()


class BranchBrowserHandler(BaseHTTPRequestHandler):
    server: BranchBrowserServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Do not log submitted messages, cookies, addresses or session tokens.
        return

    def _safe_origin(self, *, writing):
        try:
            addr = ip_address(self.client_address[0])
        except ValueError:
            return False
        if not addr.is_loopback:
            return False
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1 or hosts[0] != f"127.0.0.1:{self.server.server_port}":
            return False
        if self.headers.get_all("Transfer-Encoding", []):
            return False
        origin = self.headers.get_all("Origin", [])
        if origin and (len(origin) != 1 or origin[0] != self.server.local_origin):
            return False
        site = self.headers.get("Sec-Fetch-Site", "")
        if site not in ("", "same-origin", "none"):
            return False
        return not writing or origin == [self.server.local_origin]

    def _write(self, status, raw, *, kind=JSON_TYPE):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'self'; "
                         "style-src 'unsafe-inline'; connect-src 'self'; "
                         "img-src 'none'; object-src 'none'; "
                         "base-uri 'none'; form-action 'none'; "
                         "frame-ancestors 'none'")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(raw)
        self.close_connection = True

    def _json(self, code, document):
        self._write(code, json.dumps(document, ensure_ascii=True,
                                     separators=(",", ":"),
                                     allow_nan=False).encode("ascii"))

    def _read_json(self):
        sizes = self.headers.get_all("Content-Length", [])
        content_types = self.headers.get_all("Content-Type", [])
        if (len(sizes) != 1 or len(content_types) != 1
                or content_types[0] != JSON_TYPE
                or not sizes[0].isdigit()):
            raise ValueError("one explicit JSON Content-Length required")
        size = int(sizes[0])
        if not 0 < size <= MAX_JSON:
            raise ValueError("message exceeds bounded JSON size")
        raw = self.rfile.read(size)
        if len(raw) != size:
            raise ValueError("incomplete JSON")
        data = json.loads(raw.decode("utf-8"),
                          object_pairs_hook=_unique_fields,
                          parse_constant=_reject_nonfinite)
        if type(data) is not dict:
            raise ValueError("one JSON object required")
        return data

    def _session(self):
        token = self.headers.get_all("X-AB-Session", [])
        if len(token) != 1 or not 20 <= len(token[0]) <= 64:
            raise PermissionError("consented maze session required")
        return token[0]

    def do_GET(self):
        if not self._safe_origin(writing=False):
            self._json(403, {"error": "loopback same-origin only"})
            return
        if self.path == "/":
            raw = (ROOT / "branch_browser.html").read_bytes()
            self._write(200, raw, kind="text/html; charset=utf-8")
        elif self.path == "/maze.js":
            raw = (ROOT / "branch_browser.js").read_bytes()
            self._write(200, raw, kind="text/javascript; charset=utf-8")
        elif self.path == "/api/state":
            try:
                token = self._session()
                node = self.server.recorder.session_position(token)
                motion = self.server.boundary.snapshot()
                view = branch_view(node, movement_orientation=motion.presence_orientation)
                self._json(200, {"node": node,
                                 "along": view.along, "side": view.side,
                                 "orientation": motion.presence_orientation,
                                 "presence": motion.presence_movements})
            except PermissionError:
                self._json(403, {"error": "session not active"})
        elif self.path == "/api/transcript":
            try:
                rows = self.server.recorder.session_transcript(self._session())
                self._json(200, {"records": [asdict(x) for x in rows]})
            except PermissionError:
                self._json(403, {"error": "session not active"})
        else:
            self._json(404, {"error": "unknown fictional route"})

    def do_POST(self):
        if not self._safe_origin(writing=True):
            self._json(403, {"error": "loopback same-origin only"})
            return
        if self.path not in {"/api/consent", "/api/submit", "/api/erase"}:
            self._json(404, {"error": "unknown fictional route"})
            return
        try:
            body = self._read_json()
            if self.path == "/api/consent":
                if set(body) != {"accepted"} or body["accepted"] is not True:
                    raise PermissionError("explicit notice acceptance required")
                session = self.server.recorder.open_session(accepted_notice=True)
                self._json(200, {"session": session, "start": START})
            elif self.path == "/api/submit":
                if set(body) != {"message", "exit_choice"}:
                    raise ValueError("only maze words and fictional exit accepted")
                entry = self.server.recorder.submit(
                    self._session(), body["message"],
                    exit_choice=body["exit_choice"])
                self._json(200, {"branch": asdict(entry)})
            else:
                if body:
                    raise ValueError("erase accepts no submitted data")
                self.server.recorder.erase_session(self._session())
                self._json(200, {"erased": True})
        except PermissionError:
            self._json(403, {"error": "consent or session required"})
        except (ValueError, TypeError, UnicodeError):
            self._json(400, {"error": "invalid bounded maze submission"})

    def do_OPTIONS(self):
        self._json(405, {"error": "cross-origin access disabled"})


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local-only A/B fictional branch browser")
    parser.add_argument("--port", type=int, default=0, help="loopback port; 0 uses a free port")
    args = parser.parse_args(argv)
    with BranchBrowserServer(("127.0.0.1", args.port)) as server:
        print(f"A/B fictional maze: {server.local_origin}", flush=True)
        print(NOTICE, flush=True)
        print("Stop with Ctrl+C. No real keys or workers are exposed.", flush=True)
        server.start_presence()
        try:
            server.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            pass
        finally:
            server.stop_presence()


if __name__ == "__main__":
    raise SystemExit(main())
