from __future__ import annotations

from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import mimetypes
import os
import threading
from ipaddress import ip_address
from urllib.parse import urlsplit

from runtime.service import EcosystemService
from runtime.research_board import load_research_board


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "http"
DATA_DIR = Path(
    os.environ.get(
        "ECOSYSTEM_DATA_DIR",
        str(ROOT / "data"),
    )
)
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8040"))
LOCK = threading.RLock()
POOL_ENABLED = os.environ.get("CONTINUITY_AGENT_POOL", "").lower() in {"1", "true", "yes"}
# Existing service endpoints include unsiged mutable records and private state.
# No remote bind is safe until external authentication and storage are audited.
if HOST not in {"127.0.0.1", "::1", "localhost"}:
    raise ValueError("Ecosystem HTTP entrance is loopback-only; external access requires a separate authenticated gateway")
if POOL_ENABLED:
    from runtime.pool_evaluator import ContinuityPoolEvaluator
    POOL_EVALUATOR = ContinuityPoolEvaluator(ROOT.parent)
else:
    POOL_EVALUATOR = None
SERVICE = EcosystemService(
    data_dir=DATA_DIR,
    repository_work_file=os.environ.get('CONTINUITY_REPO_WORK_FILE') or None,
    referent_evaluator=POOL_EVALUATOR,
)
if POOL_EVALUATOR is not None:
    from runtime.continuity_pool import connect_pool
    POOL_EVALUATOR.bind(SERVICE)
    POOL_BOOT = connect_pool(SERVICE, ROOT.parent)


MAX_HTTP_JSON = 1_500_000


def _loopback(value):
    try:
        return ip_address(value).is_loopback
    except ValueError:
        return value == "localhost"


def trusted_http_request(handler, *, write=False):
    """Fail closed for browser-origin, DNS rebinding and off-host requests.

    Loopback access is a transport boundary, NOT a local-user authentication
    claim. Dedicated signed API operations require their own enrolled keys.
    """
    if not _loopback(handler.client_address[0]):
        return False
    port = handler.server.server_port
    host = handler.headers.get("Host", "")
    try:
        target = urlsplit("http://" + host)
        if (not _loopback(target.hostname or "") or target.port != port
                or target.username is not None or target.password is not None
                or target.path or target.query or target.fragment):
            return False
        origin = handler.headers.get("Origin")
        if origin is not None:
            o = urlsplit(origin)
            if (o.scheme != "http" or o.hostname != target.hostname
                    or o.port != port or o.username is not None
                    or o.password is not None or o.path or o.query or o.fragment):
                return False
    except ValueError:
        return False
    if handler.headers.get("Sec-Fetch-Site", "").casefold() in {"cross-site", "same-site"}:
        return False
    if write:
        if handler.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            return False
        try:
            size = int(handler.headers.get("Content-Length", "0"))
        except ValueError:
            return False
        if not 0 < size <= MAX_HTTP_JSON or handler.headers.get("Transfer-Encoding"):
            return False
    return True


def read_json(handler):
    size = int(handler.headers.get("Content-Length", "0"))
    if not 0 < size <= MAX_HTTP_JSON:
        raise ValueError("bounded JSON body required")
    obj = json.loads(handler.rfile.read(size).decode("utf-8"))
    if type(obj) is not dict:
        raise ValueError("JSON object required")
    return obj


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        raw = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def fail(self, exc, status=400):
        self.send_json(
            {
                "error": str(exc),
                "type": exc.__class__.__name__,
            },
            status,
        )

    def do_GET(self):
        if not trusted_http_request(self):
            self.send_json({"error": "loopback host and same-origin request required"}, 403)
            return
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        try:
            with LOCK:
                if parsed.path == "/api/monitor":
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "monitor API is loopback-only"}, 403)
                        return
                    actor = query.get("actor", [""])[0]
                    if not actor:
                        raise ValueError("actor is required")
                    limit = int(query.get("limit", ["40"])[0])
                    self.send_json(SERVICE.monitor(actor_id=actor, limit=limit))
                    return

                if parsed.path == "/api/agent-pool":
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "agent pool API is loopback-only"}, 403)
                        return
                    from runtime.continuity_pool import pool_snapshot
                    self.send_json({"enabled": POOL_ENABLED,
                                    **pool_snapshot(SERVICE)})
                    return

                if parsed.path == "/api/research-board":
                    checkpoint = query.get("checkpoint", [None])[0]
                    self.send_json(load_research_board(checkpoint=checkpoint))
                    return

                if parsed.path == "/api/connections":
                    self.send_json(SERVICE.connections())
                    return

                if parsed.path == "/api/status":
                    self.send_json(SERVICE.status())
                    return

                if parsed.path == "/api/notes":
                    self.send_json({"notes": SERVICE.list_notes()})
                    return

                if parsed.path == "/api/plans":
                    self.send_json({"plans": SERVICE.list_plans()})
                    return

                if parsed.path == "/api/daily-checklist":
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "private checklist is loopback-only"}, 403)
                        return
                    self.send_json(SERVICE.daily_checklist_snapshot())
                    return

                if parsed.path == "/api/tasks":
                    self.send_json({"tasks": SERVICE.list_tasks()})
                    return

                if parsed.path == "/api/reminders":
                    self.send_json({"reminders": SERVICE.list_reminders()})
                    return

                if parsed.path == "/api/calendar":
                    self.send_json({"events": SERVICE.list_calendar_events()})
                    return

                if parsed.path == "/api/traces":
                    session_id = query.get("session_id", [None])[0]
                    self.send_json({
                        "touches": SERVICE.list_touches(session_id=session_id)
                    })
                    return

                if parsed.path == "/api/live-feed":
                    force = query.get("force", ["0"])[0] in {"1", "true", "yes"}
                    self.send_json(SERVICE.live_feed_snapshot(force=force))
                    return

                if parsed.path.startswith("/api/traces/") and parsed.path.endswith("/ancestry"):
                    trace_id = parsed.path.removeprefix(
                        "/api/traces/"
                    ).removesuffix("/ancestry").strip("/")
                    self.send_json({
                        "touches": SERVICE.trace_ancestry(trace_id)
                    })
                    return

                if parsed.path == "/api/attention":
                    actor = query.get("actor", [""])[0]
                    if not actor:
                        raise ValueError("actor is required")
                    at = query.get("at", [""])[0]
                    now = datetime.fromisoformat(at) if at else None
                    self.send_json(SERVICE.attention(actor_id=actor, now=now))
                    return

                if parsed.path == "/api/handoffs":
                    actor = query.get("actor", [None])[0]
                    status = query.get("status", [None])[0]
                    self.send_json(
                        {
                            "handoffs": SERVICE.list_handoffs(
                                actor_id=actor,
                                status=status,
                            )
                        }
                    )
                    return

                if parsed.path == "/api/agents":
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "agent API is loopback-only"}, 403)
                        return
                    root = query.get("root", [""])[0]
                    if not root:
                        raise ValueError("root is required")
                    self.send_json(SERVICE.agent_snapshot(root))
                    return

                if parsed.path == "/api/activate":
                    surface = query.get("surface", [""])[0]
                    actor = query.get("actor", [""])[0]
                    self.send_json(
                        SERVICE.activate(
                            surface,
                            actor_id=actor,
                        )
                    )
                    return
        except KeyError as exc:
            self.fail(exc, 404)
            return
        except (ValueError, TypeError) as exc:
            self.fail(exc)
            return

        if parsed.path.startswith("/api/"):
            self.send_json({"error": "not found"}, 404)
            return

        if parsed.path in {"/monitor.html", "/monitor.js", "/monitor.css"} and (
            self.client_address[0] not in {"127.0.0.1", "::1"}
        ):
            self.send_error(403)
            return

        requested = (
            "index.html"
            if parsed.path in {"", "/"}
            else parsed.path.lstrip("/")
        )
        target = (STATIC / requested).resolve()
        if STATIC not in target.parents and target != STATIC:
            self.send_error(403)
            return
        if not target.is_file():
            self.send_error(404)
            return

        raw = target.read_bytes()
        mime, _ = mimetypes.guess_type(str(target))
        self.send_response(200)
        self.send_header(
            "Content-Type",
            (mime or "application/octet-stream")
            + (
                "; charset=utf-8"
                if (mime or "").startswith("text/")
                or target.suffix in {".js", ".mjs"}
                else ""
            ),
        )
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        if not trusted_http_request(self, write=True):
            self.send_json({"error": "bounded same-origin JSON request on loopback required"}, 403)
            return
        parsed = urlparse(self.path)
        try:
            payload = read_json(self)
            with LOCK:
                if parsed.path == "/api/ohayo":
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "ohayo mutation is loopback-only"}, 403)
                        return
                    actor = str(payload.get("actor_id") or "").strip()
                    if not actor:
                        raise ValueError("actor_id is required")
                    self.send_json(SERVICE.ohayo(actor_id=actor))
                    return

                if parsed.path == "/api/agents/activate" or (
                    parsed.path.startswith("/api/agents/") and parsed.path.endswith("/result")
                ):
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "agent API is loopback-only"}, 403)
                        return
                    if parsed.path == "/api/agents/activate":
                        self.send_json(SERVICE.activate_agent(payload), 201)
                        return
                    agent_id = parsed.path.removeprefix("/api/agents/").removesuffix("/result").strip("/")
                    if not agent_id:
                        raise ValueError("agent identifier is required")
                    self.send_json(SERVICE.agent_result(agent_id, payload))
                    return

                if parsed.path == "/api/notes":
                    self.send_json(
                        SERVICE.add_note(payload),
                        201,
                    )
                    return

                if parsed.path == "/api/plans":
                    self.send_json(
                        SERVICE.add_plan(payload),
                        201,
                    )
                    return

                if parsed.path == "/api/daily-checklist" or (
                    parsed.path.startswith("/api/daily-checklist/")
                    and parsed.path.endswith("/check")
                ):
                    if self.client_address[0] not in {"127.0.0.1", "::1"}:
                        self.send_json({"error": "private checklist writes are loopback-only"}, 403)
                        return
                    if parsed.path == "/api/daily-checklist":
                        self.send_json(SERVICE.add_daily_checklist_item(payload), 201)
                        return
                    item_id = parsed.path.removeprefix(
                        "/api/daily-checklist/"
                    ).removesuffix("/check").strip("/")
                    if not item_id:
                        raise ValueError("checklist ID required")
                    if not isinstance(payload.get("checked"), bool):
                        raise ValueError("checked must be boolean")
                    self.send_json(SERVICE.set_daily_checklist_checked(
                        item_id, checked=payload["checked"]
                    ))
                    return

                if parsed.path == "/api/tasks":
                    self.send_json(
                        SERVICE.add_task(payload),
                        201,
                    )
                    return

                if parsed.path == "/api/reminders":
                    self.send_json(
                        SERVICE.add_reminder(payload),
                        201,
                    )
                    return

                if parsed.path == "/api/calendar":
                    self.send_json(
                        SERVICE.add_calendar_event(payload),
                        201,
                    )
                    return

                if parsed.path == "/api/traces":
                    self.send_json(
                        SERVICE.add_touch(payload),
                        201,
                    )
                    return

                if (
                    parsed.path.startswith("/api/reminders/")
                    and parsed.path.endswith("/ack")
                ):
                    reminder_id = parsed.path.removeprefix(
                        "/api/reminders/"
                    ).removesuffix("/ack").strip("/")
                    local_date = str(payload.get("local_date") or "").strip()
                    if not local_date:
                        raise ValueError("local_date is required")
                    SERVICE.acknowledge_reminder(
                        reminder_id,
                        local_date=local_date,
                    )
                    self.send_json({"acknowledged": reminder_id})
                    return

                if (
                    parsed.path.startswith("/api/tasks/")
                    and parsed.path.endswith("/admit")
                ):
                    task_id = parsed.path.removeprefix(
                        "/api/tasks/"
                    ).removesuffix("/admit").strip("/")
                    self.send_json(
                        SERVICE.admit_task(task_id),
                        201,
                    )
                    return

                if (
                    parsed.path.startswith("/api/handoffs/")
                    and parsed.path.endswith("/result")
                ):
                    handoff_id = parsed.path.removeprefix(
                        "/api/handoffs/"
                    ).removesuffix("/result").strip("/")
                    actor = str(
                        payload.get("actor_id") or ""
                    ).strip()
                    if not actor:
                        raise ValueError("actor_id is required")
                    self.send_json(
                        SERVICE.return_result(
                            handoff_id,
                            payload,
                            actor_id=actor,
                        )
                    )
                    return
        except KeyError as exc:
            self.fail(exc, 404)
            return
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.fail(exc)
            return

        self.send_json({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    print(
        f"Ecosystem HTTP entrance running at "
        f"http://{HOST}:{PORT}"
    )
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
