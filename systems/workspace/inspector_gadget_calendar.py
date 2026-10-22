"""Calendar-driven Inspector Gadget activation from the persistent meta health wall.

The calendar is GitHub Actions; the conditional source is the existing
meta-observations/health.json. Reopen *each unresolved workflow* as its own
read-only source handoff on every scheduled cycle, including older incidents
outside the scanner's 2-hour window. A later conclusive PASS in the health
ledger removes the workflow from this recurring source-observation set.

This schedules Inspector investigations, NOT unauthorized native research
runs, external source downloads or unbounded repair retries.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.request

from systems.workspace.inspector_gadget_adapter import plan
from systems.workspace.inspector_gadget_scan import classify

SCHEMA = "meta-workstation/current-workflow-health-v1"
SCAN = "inspector-gadget/workflow-scan/v1"
_MAX_AGE = dt.timedelta(hours=3)


def load_health(repo, token, *, getter=None):
    """Read the existing durable health record, never overwrite/reset it."""
    if not repo or "/" not in repo or not token:
        raise ValueError("repository and read token required")
    if getter is None:
        def getter():
            req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/contents/health.json?ref=meta-observations",
                headers={"Authorization": f"Bearer {token}",
                         "Accept": "application/vnd.github+json",
                         "X-GitHub-Api-Version": "2022-11-28",
                         "User-Agent": "inspector-gadget-calendar"})
            with urllib.request.urlopen(req, timeout=25) as response:
                return json.load(response)
    wrapper = getter()
    if (not isinstance(wrapper, dict) or wrapper.get("encoding") != "base64"
            or not isinstance(wrapper.get("content"), str)):
        raise ValueError("persistent health source unavailable or malformed")
    data = json.loads(base64.b64decode(wrapper["content"], validate=False))
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("persistent health source schema mismatch")
    return data


def _time(value):
    if not isinstance(value, str):
        raise ValueError("health observation has no timestamp")
    t = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("health timestamp must be timezone-aware")
    return t.astimezone(dt.timezone.utc)


def combine(scan, health, *, repo, now=None):
    """Add all durable open source-owned walls to fresh scanner findings.

    Do not treat an unavailable health source as zero open lanes.
    """
    if not isinstance(scan, dict) or scan.get("schema") != SCAN or not isinstance(scan.get("findings"), list):
        raise ValueError("invalid recent workflow observation")
    if not isinstance(health, dict) or health.get("schema") != SCHEMA:
        raise ValueError("invalid persistent health observation")
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("current time must be timezone-aware")
    age = now.astimezone(dt.timezone.utc) - _time(health.get("observed_at"))
    if age > _MAX_AGE or age < -dt.timedelta(minutes=5):
        raise ValueError("persistent health source is stale or future dated")
    node = health.get("nodes", {}).get("A")
    if (not isinstance(node, dict) or node.get("repo") != repo
            or node.get("observed") is not True or not isinstance(node.get("open"), list)):
        raise ValueError("current workstation health is not source-observed")
    findings = list(scan["findings"])
    seen = {rid for finding in findings if isinstance(finding, dict)
            for rid in finding.get("run_ids", []) if type(rid) is int}
    appended, open_ids = [], set()
    for entry in node["open"]:
        if not isinstance(entry, dict) or entry.get("state") != "needs_attention":
            raise ValueError("persistent open item is not source-owned attention")
        wid, rid = entry.get("workflow_id"), entry.get("run_id")
        event = entry.get("conclusion")
        name = entry.get("name")
        url = entry.get("run_url")
        if (type(wid) is not int or wid <= 0 or type(rid) is not int or rid <= 0
                or not isinstance(name, str) or not name.strip()
                or classify({"conclusion": event}) is None
                or url != f"https://github.com/{repo}/actions/runs/{rid}"
                or wid in open_ids):
            raise ValueError("malformed or repeated persistent workflow wall")
        open_ids.add(wid)
        if rid in seen:
            continue
        findings.append({
            "id": f"inspector-{wid}-{event}-{rid}",
            "lane": name, "kind": "candidate", "event": event,
            "count": 1, "run_ids": [rid], "sources": [url],
            "head_shas": [], "owner": "persistent workflow health / " + name,
            "dispatch_state": "awaiting_source_verification",
            "observation": "Persistent source-owned workflow wall still needs attention",
            "state": "awaiting_verification",
        })
        appended.append(wid)
        seen.add(rid)
    return {
        "schema": SCAN,
        "since": scan.get("since"),
        "scanned": scan.get("scanned"),
        "findings": findings,
        "calendar": {
            "schema": "inspector-gadget/calendar/v1",
            "health_observed_at": health["observed_at"],
            "current_source_open": len(node["open"]),
            "open_workflow_ids": sorted(open_ids),
            "persisted_walls_added": len(appended),
            "condition": "start_inspection_lanes" if findings else "no_incidents",
            "dispatch_scope": "source-observation-only",
            "resolution_rule": "a later conclusive source run clears the persistent health wall",
        },
    }


def calendar_plan(scan, health, *, repo, now=None, max_movements=200):
    """All currently open lanes are eligible; keep overflow explicit."""
    merged = combine(scan, health, repo=repo, now=now)
    movement = plan(merged, max_movements=max_movements)
    movement["calendar"] = merged["calendar"]
    return movement


def main(argv):
    if len(argv) != 4 or argv[1] != "plan":
        raise SystemExit("usage: inspector_gadget_calendar.py plan SCAN_JSON OUTPUT_JSON")
    scan = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    health = load_health(repo, os.environ.get("GITHUB_TOKEN", ""))
    result = calendar_plan(scan, health, repo=repo)
    Path(argv[3]).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["calendar"], sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
