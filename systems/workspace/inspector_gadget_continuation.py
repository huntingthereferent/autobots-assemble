"""Calendar-driven continuation controller for existing GitHub worker lanes.

The native worker is its source workflow; this module only selects eligible
registered workers and dispatches their existing entry points. It cannot
send prompts to ChatGPT windows, invent the next research experiment, or
bypass private workstation admission. Records every dispatch attempt.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
ROSTER = Path(__file__).with_name("inspector_gadget_workers.json")
SCHEMA = "inspector-gadget/native-worker-calendar/v1"
_ALLOWED = re.compile(r"[a-z0-9][a-z0-9-]{1,79}\Z")
_FILE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]+\.yml\Z")
_BAD = {"failure", "timed_out", "action_required", "startup_failure"}
_ACTIVE = {"queued", "in_progress", "pending", "waiting", "requested"}


def _timestamp(value):
    if not isinstance(value, str) or not value:
        raise ValueError("run is missing created_at")
    date = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ValueError("run timestamp must have a timezone")
    return date.astimezone(dt.timezone.utc)


def validate(roster, root=ROOT):
    if not isinstance(roster, dict) or roster.get("schema") != SCHEMA or roster.get("ref") != "main":
        raise ValueError("unsupported native worker calendar")
    max_jobs = roster.get("max_dispatch_per_tick")
    if type(max_jobs) is not int or not 1 <= max_jobs <= 16:
        raise ValueError("invalid per-tick dispatch cap")
    entries = roster.get("workers")
    if not isinstance(entries, list) or not entries:
        raise ValueError("native workers missing")
    seen_ids, seen_paths = set(), set()
    for row in entries:
        if not isinstance(row, dict):
            raise ValueError("invalid worker")
        identity, filename, interval = row.get("id"), row.get("filename"), row.get("min_interval_minutes")
        if (not isinstance(identity, str) or not _ALLOWED.fullmatch(identity)
                or identity in seen_ids or not isinstance(filename, str)
                or not _FILE.fullmatch(filename) or filename in seen_paths
                or type(interval) is not int or not 0 <= interval <= 10080
                or type(row.get("enabled")) is not bool):
            raise ValueError("invalid/duplicate native worker identity, cadence or switch")
        seen_ids.add(identity)
        seen_paths.add(filename)
        wf = root / ".github" / "workflows" / filename
        if not wf.is_file():
            raise ValueError("unavailable native workflow: " + filename)
        # A real workflow-dispatch entry point is mandatory. Do not add
        # synthetic command wrappers to substitute for owning workers.
        if not re.search(r"(?m)^[ \t]{2}workflow_dispatch[ \t]*:", wf.read_text(encoding="utf8")):
            raise ValueError("native worker has no workflow_dispatch entry point: " + filename)
    return entries


def _api(repo, token, method, endpoint, payload=None):
    if (not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not token
            or method not in {"GET", "POST"}):
        raise ValueError("authorized GitHub source required")
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "inspector-gadget-native-lane-continuation"}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/{endpoint}",
                                 data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        if method == "POST":
            if response.status != 204:
                raise ValueError("GitHub did not accept native worker dispatch")
            return {"accepted": True}
        return json.load(response)


def read_runs(repo, filename, token):
    wf = urllib.parse.quote(filename, safe="")
    body = _api(repo, token, "GET", f"actions/workflows/{wf}/runs?per_page=100&page=1")
    if not isinstance(body, dict) or not isinstance(body.get("workflow_runs"), list):
        raise ValueError("native worker history missing")
    # An incomplete page is safe for cooldown and active-run screening only
    # because the latest created run dominates older records. If empty and
    # total_count nonzero, refuse to assume this worker is idle.
    if body.get("total_count", 0) and not body["workflow_runs"]:
        raise ValueError("native worker run history incomplete")
    return body["workflow_runs"]


def assess(roster, histories, *, repo, now=None, root=ROOT):
    """Select existing independently owned workers, never synthesize tasks."""
    entries = validate(roster, root=root)
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("scheduler clock missing timezone")
    now = now.astimezone(dt.timezone.utc)
    # Per-worker GitHub Actions source histories now gate dispatch directly.
    # No cross-account observation ledger or Meta scheduler participates.
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("owning GitHub repository required")
    ready, outcomes = [], []
    for worker in entries:
        key = worker["id"]
        runs = histories.get(key)
        if not isinstance(runs, list):
            raise ValueError("native worker history missing: " + key)
        for run in runs:
            if not isinstance(run, dict):
                raise ValueError("invalid native run record")
        filename = worker["filename"]
        lane = {"id": key, "workflow": filename}
        if not worker["enabled"]:
            outcomes.append({**lane, "state": "DISABLED"})
            continue
        if any(r.get("status") in _ACTIVE for r in runs):
            outcomes.append({**lane, "state": "ALREADY_RUNNING"})
            continue
        dates = [_timestamp(r["created_at"]) for r in runs if r.get("created_at")]
        last = max(dates) if dates else None
        # Cadence describes observation/revalidation, not permission to launch.
        # Only an active owner run prevents duplicate dispatch.
        # Replaying a green fixture is an existing-worker *recheck*, never a
        # claim that a new hypothesis or native research experiment was born.
        due = {**lane, "state": "ELIGIBLE", "last_run_at": last.isoformat() if last else None,
               "min_interval_minutes": worker["min_interval_minutes"]}
        ready.append(due)
    # Oldest work first, stable ties; avoid prioritizing one project by name.
    ready.sort(key=lambda r: (r["last_run_at"] is not None, r["last_run_at"] or "", r["id"]))
    cap = len(ready)  # No calendar quota on independently runnable lanes.
    dispatched = ready[:cap]
    outcomes.extend([{**r, "state": "SELECTED"} for r in dispatched])
    outcomes.extend([{**r, "state": "CAPACITY_WAIT"} for r in ready[cap:]])
    return {"schema": "inspector-gadget/native-worker-plan/v1",
            "calendar_source": "owning GitHub Actions workflow history",
            "observed_at": now.isoformat(),
            "eligible_count": len(ready),
            "selected_count": len(dispatched),
            "capacity_wait": max(0, len(ready) - cap),
            "selected": dispatched, "workers": sorted(outcomes, key=lambda x: x["id"]),
            "boundary": "Dispatches existing source-owned workflows only; not ChatGPT turns, research novelty or external authorization"}


def run(roster, *, repo, token, reader=read_runs, sender=None, root=ROOT):
    entries = validate(roster, root=root)
    histories = {w["id"]: reader(repo, w["filename"], token) for w in entries if w["enabled"]}
    histories.update({w["id"]: [] for w in entries if not w["enabled"]})
    plan = assess(roster, histories, repo=repo, root=root)
    dispatch = sender or (lambda filename: _api(
        repo, token, "POST",
        "actions/workflows/" + urllib.parse.quote(filename, safe="") + "/dispatches",
        {"ref": "main"}))
    receipts = []
    failures = []
    for worker in plan["selected"]:
        try:
            result = dispatch(worker["workflow"])
            if result.get("accepted") is not True:
                raise ValueError("source-owned workflow did not accept dispatch")
            receipts.append({**worker, "result": "DISPATCH_ACCEPTED"})
        except Exception as exc:
            failures.append(worker["id"])
            receipts.append({**worker, "result": "DISPATCH_FAILED",
                             "error": type(exc).__name__ + ": " + str(exc)})
    plan["receipts"] = receipts
    plan["dispatch_failures"] = failures
    return plan


def main(argv):
    if len(argv) != 2 or argv[1] != "dispatch":
        raise SystemExit("usage: python -m systems.workspace.inspector_gadget_continuation dispatch")
    roster = json.loads(ROSTER.read_text(encoding="utf8"))
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    report = None
    try:
        report = run(roster, repo=repo, token=token)
    finally:
        if report is not None:
            Path("inspector-gadget-native-continuation.json").write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    if report["dispatch_failures"]:
        raise RuntimeError("native workflow dispatch failed for: " + ", ".join(report["dispatch_failures"]))
    print(json.dumps({"selected": report["selected_count"],
                      "accepted": len(report["receipts"]),
                      "capacity_wait": report["capacity_wait"]}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
