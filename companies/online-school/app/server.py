from __future__ import annotations

from dataclasses import asdict
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import sys
import mimetypes
import os
import threading

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from systems.education import EducationKernel, Observation
from schedule_engine import generate_tasks, load_schedule, load_themes, merge_generated, validate_task
from school_view import build_school_view
from worksheet_engine import generate_worksheet, validate_saved_worksheet


DATA_DIR = Path(
    os.environ.get("ONLINE_SCHOOL_DATA_DIR", str(ROOT / "data"))
)
STATE_PATH = DATA_DIR / "state.json"
EDUCATION_PATH = DATA_DIR / "education.jsonl"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8030"))
LOCK = threading.Lock()


def default_state():
    return {
        "schema_version": 1,
        "tasks": [],
        "worksheets": [],
        "learners": [
            {"id": "track_a", "display_name": "Learner A", "grade_context": "3"},
            {"id": "track_b", "display_name": "Learner B", "grade_context": "1"},
        ],
        "settings": {"school_name": "Online School"},
    }


def load_state():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        state = default_state()
        save_state(state)
        return state
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(STATE_PATH)


def education_kernel():
    return EducationKernel(EDUCATION_PATH)


def json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def api_error(self, message, status=400):
        self.send_json({"error": message}, status)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/state":
            with LOCK:
                state = load_state()
            self.send_json({
                **state,
                "schedule": load_schedule(),
                "themes": load_themes(),
            })
            return

        if parsed.path == "/api/school":
            day = parse_qs(parsed.query).get("date", [date.today().isoformat()])[0]
            try:
                generated = generate_tasks(day, day)
            except ValueError as exc:
                self.api_error(str(exc))
                return
            with LOCK:
                state = load_state()
                state["tasks"], _added = merge_generated(
                    state.get("tasks", []),
                    generated,
                )
                save_state(state)
                view = build_school_view(
                    state=state,
                    day=day,
                    kernel=education_kernel(),
                )
            self.send_json(view)
            return

        if parsed.path == "/api/worksheets":
            with LOCK:
                worksheets = list(load_state().get("worksheets", []))
            worksheets.sort(key=lambda item: str(item.get("title") or "").lower())
            self.send_json({"worksheets": worksheets})
            return

        if parsed.path.startswith("/api/worksheets/"):
            worksheet_id = parsed.path.removeprefix("/api/worksheets/")
            with LOCK:
                worksheets = list(load_state().get("worksheets", []))
            worksheet = next(
                (item for item in worksheets if item.get("worksheet_id") == worksheet_id),
                None,
            )
            if worksheet is None:
                self.api_error("worksheet not found", 404)
            else:
                self.send_json(worksheet)
            return

        if parsed.path == "/api/tasks":
            params = parse_qs(parsed.query)
            with LOCK:
                tasks = list(load_state().get("tasks", []))
            for key in ("date", "status", "kind", "scope"):
                if params.get(key):
                    value = params[key][0]
                    tasks = [t for t in tasks if str(t.get(key, "")) == value]
            if params.get("learner"):
                learner = params["learner"][0]
                tasks = [t for t in tasks if learner in t.get("learner_ids", [])]
            tasks.sort(key=lambda t: (t.get("date", ""), t.get("title", "")))
            self.send_json({"tasks": tasks})
            return

        if parsed.path == "/api/today":
            day = parse_qs(parsed.query).get("date", [date.today().isoformat()])[0]
            try:
                generated = generate_tasks(day, day)
            except ValueError as exc:
                self.api_error(str(exc))
                return
            with LOCK:
                state = load_state()
                state["tasks"], added = merge_generated(state.get("tasks", []), generated)
                save_state(state)
                tasks = [t for t in state["tasks"] if t.get("date") == day]
            self.send_json({"date": day, "added": added, "tasks": tasks})
            return

        if parsed.path.startswith("/api/"):
            self.api_error("not found", 404)
            return

        requested = "index.html" if parsed.path in {"", "/"} else parsed.path.lstrip("/")
        file_path = (ROOT / requested).resolve()
        if ROOT not in file_path.parents and file_path != ROOT:
            self.send_error(403)
            return
        if not file_path.is_file():
            self.send_error(404)
            return
        content = file_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", (mime or "application/octet-stream") + ("; charset=utf-8" if (mime or "").startswith("text/") or file_path.suffix in {".js", ".mjs"} else ""))
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/observations":
            try:
                payload = json_body(self)
                learner_id = str(payload.get("learner_id") or "").strip()
                referent = str(payload.get("referent") or "").strip()
                observed = str(payload.get("observed") or "").strip()
                if not learner_id:
                    raise ValueError("learner_id is required")
                with LOCK:
                    state = load_state()
                    known = {
                        str(item.get("id") or "")
                        for item in state.get("learners", [])
                    }
                    if learner_id not in known:
                        raise ValueError("unknown learner")
                    kernel = education_kernel()
                    relation = kernel.observe(
                        Observation.create(
                            person_ref=learner_id,
                            referent=referent,
                            observed=observed,
                            supports=tuple(
                                str(x) for x in payload.get("supports") or ()
                            ),
                            contradicts=tuple(
                                str(x) for x in payload.get("contradicts") or ()
                            ),
                            support_conditions=tuple(
                                str(x)
                                for x in payload.get("support_conditions") or ()
                            ),
                            evidence_refs=tuple(
                                str(x) for x in payload.get("evidence_refs") or ()
                            ),
                            provenance=tuple(
                                str(x) for x in payload.get("provenance") or ()
                            ),
                        )
                    )
                self.send_json(asdict(relation), 201)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

        if parsed.path == "/api/generate":
            try:
                payload = json_body(self)
                start = str(payload.get("start") or date.today().isoformat())
                end = str(payload.get("end") or start)
                generated = generate_tasks(start, end)
                with LOCK:
                    state = load_state()
                    state["tasks"], added = merge_generated(state.get("tasks", []), generated)
                    save_state(state)
                self.send_json({"added": added, "generated": len(generated), "start": start, "end": end}, 201)
            except (ValueError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

        if parsed.path == "/api/worksheets/generate":
            try:
                self.send_json(generate_worksheet(json_body(self)), 201)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

        if parsed.path == "/api/worksheets":
            try:
                worksheet = validate_saved_worksheet(json_body(self))
                with LOCK:
                    state = load_state()
                    current = list(state.get("worksheets", []))
                    current = [item for item in current if item.get("worksheet_id") != worksheet["worksheet_id"]]
                    current.append(worksheet)
                    state["worksheets"] = current
                    save_state(state)
                self.send_json(worksheet, 201)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

        if parsed.path == "/api/tasks":
            try:
                task = validate_task(json_body(self))
                with LOCK:
                    state = load_state()
                    state.setdefault("tasks", []).append(task)
                    save_state(state)
                self.send_json(task, 201)
            except (ValueError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

        if parsed.path.startswith("/api/"):
            self.api_error("not found", 404)
            return

        self.send_error(404)

    def do_PATCH(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/tasks/"):
            self.api_error("not found", 404)
            return

        task_id = parsed.path.removeprefix("/api/tasks/")
        try:
            patch = json_body(self)
        except json.JSONDecodeError as exc:
            self.api_error(str(exc))
            return

        allowed = {"title", "category", "kind", "scope", "learner_ids", "planned_minutes", "status", "notes", "meta", "date"}
        patch = {k: v for k, v in patch.items() if k in allowed}

        with LOCK:
            state = load_state()
            for i, current in enumerate(state.get("tasks", [])):
                if current.get("id") != task_id:
                    continue
                candidate = {**current, **patch, "id": task_id}
                try:
                    state["tasks"][i] = validate_task(candidate)
                except ValueError as exc:
                    self.api_error(str(exc))
                    return
                save_state(state)
                self.send_json(state["tasks"][i])
                return

        self.api_error("task not found", 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/worksheets/"):
            worksheet_id = parsed.path.removeprefix("/api/worksheets/")
            with LOCK:
                state = load_state()
                before = len(state.get("worksheets", []))
                state["worksheets"] = [
                    item for item in state.get("worksheets", [])
                    if item.get("worksheet_id") != worksheet_id
                ]
                if len(state["worksheets"]) == before:
                    self.api_error("worksheet not found", 404)
                    return
                save_state(state)
            self.send_json({"deleted": worksheet_id})
            return

        if not parsed.path.startswith("/api/tasks/"):
            self.api_error("not found", 404)
            return
        task_id = parsed.path.removeprefix("/api/tasks/")
        with LOCK:
            state = load_state()
            before = len(state.get("tasks", []))
            state["tasks"] = [t for t in state.get("tasks", []) if t.get("id") != task_id]
            if len(state["tasks"]) == before:
                self.api_error("task not found", 404)
                return
            save_state(state)
        self.send_json({"deleted": task_id})

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    print(f"Online School running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
