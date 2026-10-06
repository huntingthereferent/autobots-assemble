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
import uuid

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from systems.education import EducationKernel, Observation
from systems.missouri_curriculum import path_for_grade
from schedule_engine import generate_tasks, load_schedule, load_themes, merge_generated, validate_task
from school_view import build_school_view
from worksheet_engine import generate_worksheet, validate_saved_worksheet
from placement import placement_plan
from weekly_itinerary import generate_all_weeks


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
        "learners": [],
        "settings": {"school_name": "Online School"},
    }


def normalize_state(state):
    placeholders = {"track_a", "track_b"}
    learners = [
        item
        for item in state.get("learners", [])
        if not (
            str(item.get("id") or "") in placeholders
            and str(item.get("display_name") or "") in {"Learner A", "Learner B"}
        )
    ]
    for learner in learners:
        placement = learner.get("placement")
        if not isinstance(placement, dict):
            learner["placement"] = {
                "status": "required",
                "completed_subjects": [],
                "results": {},
            }
    state["learners"] = learners

    normalized_tasks = []
    current_ids = [str(item.get("id") or "") for item in learners]
    for task in state.get("tasks", []):
        ids = [str(x) for x in task.get("learner_ids", [])]
        if (
            task.get("source") == "schedule_template:individualized_tracks"
            and ids
            and set(ids).issubset(placeholders)
        ):
            continue
        if task.get("scope") == "shared":
            task = dict(task)
            task["learner_ids"] = [
                learner_id for learner_id in ids if learner_id not in placeholders
            ] or current_ids
        normalized_tasks.append(task)
    state["tasks"] = normalized_tasks
    return state


def load_state():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        state = default_state()
        save_state(state)
        return state
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    before = json.dumps(state, sort_keys=True)
    normalized = normalize_state(state)
    if json.dumps(normalized, sort_keys=True) != before:
        save_state(normalized)
    return normalized


def save_state(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(STATE_PATH)


def education_kernel():
    return EducationKernel(EDUCATION_PATH)


def adapt_generated_to_learners(generated, state):
    learner_ids = {
        str(item.get("id") or "")
        for item in state.get("learners", [])
        if str(item.get("id") or "")
    }
    adapted = []
    for task in generated:
        task = dict(task)
        ids = [str(x) for x in task.get("learner_ids", [])]
        if task.get("scope") == "individual":
            if not ids or not set(ids).issubset(learner_ids):
                continue
        elif task.get("scope") == "shared":
            task["learner_ids"] = sorted(learner_ids)
        adapted.append(task)
    return adapted


def placement_tasks(day, state):
    rows = []
    for learner in state.get("learners", []):
        placement = learner.get("placement") or {}
        completed = set(placement.get("completed_subjects") or [])
        for section in placement_plan(learner):
            subject = section["subject"]
            if subject in completed:
                continue
            rows.append(
                {
                    "id": str(
                        uuid.uuid5(
                            uuid.NAMESPACE_URL,
                            f"online-school:placement:{day}:{learner.get('id')}:{subject}",
                        )
                    ),
                    "date": day,
                    "title": section["title"],
                    "category": "placement",
                    "kind": "assessment",
                    "scope": "individual",
                    "learner_ids": [str(learner.get("id") or "")],
                    "planned_minutes": section["minutes"],
                    "status": "todo",
                    "source": "placement",
                    "notes": section["description"],
                    "meta": {
                        "placement": True,
                        "placement_subject": subject,
                    },
                }
            )
    return rows


def placement_complete(learner):
    placement = learner.get("placement") or {}
    return placement.get("status") == "complete"


def adult_required_tasks(day, state):
    if date.fromisoformat(day).weekday() > 4:
        return []
    rows = []
    blocks = (
        ("mathematics", 45, "Work through a required mathematics problem set."),
        ("reading", 30, "Read something substantial and preserve what matters."),
        ("writing", 30, "Write an explanation, argument, summary, or analysis."),
        ("science / research", 45, "Investigate a question through evidence and sources."),
    )
    for learner in state.get("learners", []):
        try:
            age = int(learner.get("age")) if learner.get("age") not in (None, "") else None
        except (TypeError, ValueError):
            age = None
        if age is None or age < 18:
            continue
        if not placement_complete(learner):
            continue
        learner_id = str(learner.get("id") or "")
        for title, minutes, notes in blocks:
            rows.append(
                {
                    "id": str(
                        uuid.uuid5(
                            uuid.NAMESPACE_URL,
                            f"online-school:adult-required:{day}:{learner_id}:{title}",
                        )
                    ),
                    "date": day,
                    "title": title,
                    "category": title.replace(" / ", "-").replace(" ", "-"),
                    "kind": "instruction",
                    "scope": "individual",
                    "learner_ids": [learner_id],
                    "planned_minutes": minutes,
                    "status": "todo",
                    "source": "adult-forced-curriculum",
                    "notes": notes,
                    "meta": {
                        "required": True,
                        "adult_curriculum": True,
                        "guardrail": "obligation without age/grade presentation ceiling",
                    },
                }
            )
    return rows


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
                generated = adapt_generated_to_learners(generated, state)
                generated.extend(placement_tasks(day, state))
                weekly_tasks, calendar_rows = generate_all_weeks(state, day)
                generated.extend(weekly_tasks)
                if not weekly_tasks:
                    generated.extend(adult_required_tasks(day, state))
                state["calendar"] = calendar_rows
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

        if parsed.path == "/api/placement":
            learner_id = parse_qs(parsed.query).get("learner", [""])[0]
            with LOCK:
                state = load_state()
                learner = next(
                    (
                        item for item in state.get("learners", [])
                        if str(item.get("id") or "") == learner_id
                    ),
                    None,
                )
            if learner is None:
                self.api_error("learner not found", 404)
                return
            self.send_json(
                {
                    "learner_id": learner_id,
                    "placement": learner.get("placement") or {},
                    "sections": placement_plan(learner),
                }
            )
            return


        if parsed.path == "/api/record":
            learner_id = parse_qs(parsed.query).get("learner", [""])[0]
            with LOCK:
                state = load_state()
                learner = next(
                    (
                        item for item in state.get("learners", [])
                        if str(item.get("id") or "") == learner_id
                    ),
                    None,
                )
                if learner is None:
                    self.api_error("learner not found", 404)
                    return

                grade = str(learner.get("grade_context") or "").strip()
                try:
                    targets = list(path_for_grade(grade)) if grade else []
                except ValueError:
                    targets = []

                progress_records = learner.get("progress_records") or {}
                learner_tasks = [
                    task for task in state.get("tasks", [])
                    if learner_id in task.get("learner_ids", [])
                ]
                learner_worksheets = [
                    item for item in state.get("worksheets", [])
                    if str(item.get("learner") or "") in {
                        learner_id,
                        str(learner.get("display_name") or ""),
                    }
                ]
                kernel = education_kernel()
                observations = [
                    asdict(item)
                    for item in kernel.observations_for_person(learner_id)
                ]
                relations = [
                    asdict(item)
                    for item in kernel.current_for_person(learner_id)
                ]

                standards = []
                for target in targets:
                    record = progress_records.get(target.code) or {}
                    linked_tasks = [
                        task for task in learner_tasks
                        if str((task.get("meta") or {}).get("curriculum_standard") or "") == target.code
                    ]
                    linked_worksheets = []
                    for item in learner_worksheets:
                        source = item.get("source") or {}
                        provenance = source.get("provenance") if isinstance(source, dict) else {}
                        if isinstance(provenance, dict) and str(provenance.get("standard") or "") == target.code:
                            linked_worksheets.append(item)
                    standards.append(
                        {
                            "code": target.code,
                            "unit": target.unit,
                            "title": target.title,
                            "description": target.description,
                            "skill": target.skill,
                            "status": str(record.get("status") or "not-observed"),
                            "note": str(record.get("note") or ""),
                            "updated_at": record.get("updated_at"),
                            "task_evidence": [
                                {
                                    "id": task.get("id"),
                                    "date": task.get("date"),
                                    "title": task.get("title"),
                                    "status": task.get("status"),
                                }
                                for task in linked_tasks
                            ],
                            "worksheet_evidence": [
                                {
                                    "worksheet_id": item.get("worksheet_id"),
                                    "title": item.get("title"),
                                }
                                for item in linked_worksheets
                            ],
                        }
                    )

                completed_tasks = [
                    task for task in learner_tasks
                    if task.get("status") == "done"
                ]
                recorded_minutes = sum(
                    int(task.get("planned_minutes") or 0)
                    for task in completed_tasks
                )
                scheduled_minutes = sum(
                    int(task.get("planned_minutes") or 0)
                    for task in learner_tasks
                )
                by_category = {}
                for task in completed_tasks:
                    category = str(task.get("category") or task.get("title") or "other")
                    by_category[category] = by_category.get(category, 0) + int(task.get("planned_minutes") or 0)

                calendar_rows = [
                    row for row in state.get("calendar", [])
                    if str(row.get("learner_id") or "") == learner_id
                ]

                self.send_json(
                    {
                        "schema_version": 1,
                        "generated_on": date.today().isoformat(),
                        "learner": learner,
                        "grade_context": grade,
                        "standards_source": (
                            "Missouri Learning Standards comparison fixture"
                            if standards
                            else "No Missouri comparison map loaded for this grade yet"
                        ),
                        "standards": standards,
                        "placement": learner.get("placement") or {},
                        "current_relations": relations,
                        "observations": observations,
                        "tasks": learner_tasks,
                        "worksheets": learner_worksheets,
                        "calendar": calendar_rows,
                        "hours": {
                            "recorded_completed_minutes": recorded_minutes,
                            "recorded_completed_hours": round(recorded_minutes / 60, 2),
                            "scheduled_minutes": scheduled_minutes,
                            "scheduled_hours": round(scheduled_minutes / 60, 2),
                            "completed_by_category_minutes": by_category,
                        },
                        "record_boundary": (
                            "Task completion and worksheet completion are evidence records; "
                            "they do not automatically establish mastery."
                        ),
                    }
                )
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
                generated = adapt_generated_to_learners(generated, state)
                generated.extend(placement_tasks(day, state))
                weekly_tasks, calendar_rows = generate_all_weeks(state, day)
                generated.extend(weekly_tasks)
                if not weekly_tasks:
                    generated.extend(adult_required_tasks(day, state))
                state["calendar"] = calendar_rows
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

        if parsed.path == "/api/learners":
            try:
                payload = json_body(self)
                name = str(payload.get("display_name") or "").strip()
                grade = str(payload.get("grade_context") or "").strip()
                age_raw = payload.get("age")
                if not name:
                    raise ValueError("name is required")
                age = None
                if age_raw not in (None, ""):
                    age = int(age_raw)
                    if age < 1 or age > 120:
                        raise ValueError("age must be between 1 and 120")
                learner = {
                    "id": "learner_" + uuid.uuid4().hex[:12],
                    "display_name": name,
                    "grade_context": grade,
                    "age": age,
                    "placement": {
                        "status": "required",
                        "completed_subjects": [],
                        "results": {},
                    },
                }
                with LOCK:
                    state = load_state()
                    state.setdefault("learners", []).append(learner)
                    for task in state.get("tasks", []):
                        if task.get("scope") == "shared":
                            ids = [str(x) for x in task.get("learner_ids", [])]
                            if learner["id"] not in ids:
                                task["learner_ids"] = ids + [learner["id"]]
                    save_state(state)
                self.send_json(learner, 201)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

        if parsed.path == "/api/placement/submit":
            try:
                payload = json_body(self)
                learner_id = str(payload.get("learner_id") or "").strip()
                subject = str(payload.get("subject") or "").strip()
                responses = payload.get("responses") or {}
                if not learner_id or not subject:
                    raise ValueError("learner_id and subject are required")

                with LOCK:
                    state = load_state()
                    learner = next(
                        (
                            item for item in state.get("learners", [])
                            if str(item.get("id") or "") == learner_id
                        ),
                        None,
                    )
                    if learner is None:
                        raise ValueError("unknown learner")

                    section = next(
                        (
                            item for item in placement_plan(learner)
                            if item["subject"] == subject
                        ),
                        None,
                    )
                    if section is None:
                        raise ValueError("unknown placement subject")

                    result = {
                        "subject": subject,
                        "submitted": True,
                        "response_count": len(responses),
                    }

                    if subject == "mathematics":
                        diagnostic = section["diagnostic"]
                        band_totals = {}
                        band_correct = {}
                        correct = 0
                        for item in diagnostic["items"]:
                            band = item["band"]
                            band_totals[band] = band_totals.get(band, 0) + 1
                            given = str(responses.get(item["id"]) or "").strip().lower()
                            expected = str(item["answer"] or "").strip().lower()
                            hit = given == expected
                            if hit:
                                correct += 1
                                band_correct[band] = band_correct.get(band, 0) + 1

                        band_scores = {}
                        start_band = diagnostic["bands"][0]["id"]
                        for band in diagnostic["bands"]:
                            band_id = band["id"]
                            total = band_totals.get(band_id, 0)
                            accuracy = (
                                band_correct.get(band_id, 0) / total
                                if total
                                else 0.0
                            )
                            band_scores[band_id] = {
                                "correct": band_correct.get(band_id, 0),
                                "total": total,
                                "accuracy": accuracy,
                            }
                            if accuracy >= 0.70:
                                start_band = band_id
                            else:
                                break

                        result.update(
                            {
                                "correct": correct,
                                "total": len(diagnostic["items"]),
                                "band_scores": band_scores,
                                "start_band": start_band,
                            }
                        )
                    else:
                        result["responses"] = {
                            str(key): str(value)
                            for key, value in responses.items()
                        }

                    placement = learner.setdefault(
                        "placement",
                        {
                            "status": "required",
                            "completed_subjects": [],
                            "results": {},
                        },
                    )
                    completed = set(placement.get("completed_subjects") or [])
                    completed.add(subject)
                    placement["completed_subjects"] = sorted(completed)
                    placement.setdefault("results", {})[subject] = result
                    required_subjects = {
                        item["subject"] for item in placement_plan(learner)
                    }
                    if required_subjects.issubset(completed):
                        placement["status"] = "complete"

                    for task in state.get("tasks", []):
                        if (
                            task.get("source") == "placement"
                            and learner_id in task.get("learner_ids", [])
                            and (task.get("meta") or {}).get("placement_subject") == subject
                        ):
                            task["status"] = "done"

                    save_state(state)

                    kernel = education_kernel()
                    support = (
                        f"placement start band: {result.get('start_band')}"
                        if subject == "mathematics"
                        else f"{subject} placement response submitted"
                    )
                    relation = kernel.observe(
                        Observation.create(
                            person_ref=learner_id,
                            referent=f"placement:{subject}",
                            observed=f"completed {subject} placement",
                            supports=(support,),
                            evidence_refs=(f"placement:{subject}",),
                            provenance=("online-school:placement",),
                        )
                    )

                self.send_json(
                    {
                        "result": result,
                        "placement": learner["placement"],
                        "relation": asdict(relation),
                    },
                    201,
                )
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return


        if parsed.path == "/api/progress":
            try:
                payload = json_body(self)
                learner_id = str(payload.get("learner_id") or "").strip()
                code = str(payload.get("code") or "").strip()
                status = str(payload.get("status") or "").strip()
                note = str(payload.get("note") or "").strip()
                allowed_status = {
                    "demonstrated",
                    "developing",
                    "introduced",
                    "not-observed",
                }
                if not learner_id or not code:
                    raise ValueError("learner_id and code are required")
                if status not in allowed_status:
                    raise ValueError("invalid progress status")

                with LOCK:
                    state = load_state()
                    learner = next(
                        (
                            item for item in state.get("learners", [])
                            if str(item.get("id") or "") == learner_id
                        ),
                        None,
                    )
                    if learner is None:
                        raise ValueError("unknown learner")
                    learner.setdefault("progress_records", {})[code] = {
                        "status": status,
                        "note": note,
                        "updated_at": date.today().isoformat(),
                    }
                    save_state(state)

                self.send_json(
                    {
                        "learner_id": learner_id,
                        "code": code,
                        "status": status,
                        "note": note,
                    },
                    201,
                )
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.api_error(str(exc))
            return

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
                generated = generate_tasks(start, start)
                with LOCK:
                    state = load_state()
                    generated = adapt_generated_to_learners(generated, state)
                    generated.extend(placement_tasks(start, state))
                    weekly_tasks, calendar_rows = generate_all_weeks(state, start)
                    generated.extend(weekly_tasks)
                    if not weekly_tasks:
                        generated.extend(adult_required_tasks(start, state))
                    state["calendar"] = calendar_rows
                    state["tasks"], added = merge_generated(state.get("tasks", []), generated)
                    save_state(state)
                self.send_json({
                    "added": added,
                    "generated": len(generated),
                    "start": start,
                    "end": start,
                    "bounded_week": True,
                }, 201)
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
