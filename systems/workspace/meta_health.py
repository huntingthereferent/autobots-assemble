"""Current workflow checks needing attention, not historical failure counts.

A check is keyed by GitHub workflow ID + repository. The latest *conclusive*
completed run (success/failure) determines whether that workflow currently
needs review. Cancelled or skipped attempts neither open nor clear a problem.
This does NOT establish whether a particular scientific claim or test assertion
has been validated. Full event provenance remains in GitHub Actions.

Initial coverage begins 48h before first capture. Subsequent captures examine
the time since the last complete scan plus an overlap for late completions.
If any API page is unavailable, never report a fabricated zero.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import quote

try:
    from .meta_collect import api, repositories
except ImportError:
    from meta_collect import api, repositories

SCHEMA = "meta-workstation/current-workflow-health-v1"
BAD = {"failure", "timed_out", "action_required", "startup_failure"}
OK = {"success"}
NEUTRAL = {"cancelled", "skipped", "neutral", "stale", None}
UTC = dt.timezone.utc


def utcstr(v):
    return v.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).astimezone(UTC)


def windows(start, end):
    current = start
    while current < end:
        stop = min(end, current + dt.timedelta(hours=1))
        yield current, stop
        current = stop


def workflows(repo, getter):
    active = set()
    for page in range(1, 25):
        data = getter(f"/repos/{repo}/actions/workflows?per_page=100&page={page}")
        rows = data.get("workflows")
        if not isinstance(rows, list):
            raise ValueError("GitHub did not return workflow source data")
        for item in rows:
            if item.get("state") == "active" and isinstance(item.get("id"), int):
                active.add(item["id"])
        if len(rows) < 100:
            return active
    raise RuntimeError("Workflow inventory exceeded bounded pagination")


def events(repo, start, end, getter):
    result = []
    for lo, hi in windows(start, end):
        # One-hour partitions keep individual GitHub Actions filtered searches
        # below the 1,000-result search cap for this workstation.
        period = quote(utcstr(lo) + ".." + utcstr(hi - dt.timedelta(seconds=1)), safe="")
        for page in range(1, 12):
            response = getter(f"/repos/{repo}/actions/runs?created={period}&per_page=100&page={page}")
            rows = response.get("workflow_runs")
            total = response.get("total_count")
            if not isinstance(rows, list) or type(total) is not int:
                raise ValueError("Missing Actions pagination")
            if total > 1000:
                raise RuntimeError("Dense hour exceeded safe query limit; no trusted count")
            result.extend(rows)
            if len(rows) < 100:
                break
        else:
            raise RuntimeError("Run window pagination exceeded safe source bound")
    return result


def update_status(previous, run, repo):
    if run.get("status") != "completed" or run.get("conclusion") not in BAD | OK:
        return
    workflow_id = run.get("workflow_id")
    if type(workflow_id) is not int or workflow_id <= 0:
        return
    rid = run.get("id")
    when = run.get("updated_at") or run.get("run_started_at") or run.get("created_at")
    if type(rid) is not int or not when:
        return
    try:
        stamp = utcstr(parse(when))
    except (ValueError, TypeError, OverflowError):
        return
    key = str(workflow_id)
    old = previous.get(key, {})
    marker = (stamp, int(run.get("run_attempt") or 1), rid)
    earlier = (str(old.get("event_at", "")), int(old.get("attempt", 0)), int(old.get("run_id", 0)))
    if marker <= earlier:
        return
    previous[key] = {
        "workflow_id": workflow_id,
        "name": str(run.get("name") or key),
        "state": "needs_attention" if run["conclusion"] in BAD else "clear",
        "conclusion": run["conclusion"],
        "event_at": stamp,
        "attempt": marker[1],
        "run_id": rid,
        "run_url": f"https://github.com/{repo}/actions/runs/{rid}",
        "branch": str(run.get("head_branch") or ""),
    }


def collect(previous, registry, now=None, getter=api):
    now = now or dt.datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("Current time must have timezone")
    if previous and previous.get("schema") != SCHEMA:
        raise ValueError("Wrong journal schema; never silently reset historical state")
    previous = previous or {}
    repos = repositories(registry)
    previous_nodes = previous.get("nodes", {})
    last = previous.get("last_complete_scan")
    # A first verified baseline; old unobserved work is not called fixed.
    start = now - dt.timedelta(hours=48) if not last else parse(last) - dt.timedelta(hours=3)
    start = max(start, now - dt.timedelta(hours=48))
    out = {
        "schema": SCHEMA,
        "observed_at": utcstr(now),
        "coverage_since": previous.get("coverage_since", utcstr(start)),
        "basis": "Latest conclusive completed GitHub Actions run for each active workflow, within the observed history. A later pass clears its earlier failed state.",
        "limits": "Workflow-level health, not individual test-case proof; cancellations/skips do not change state. Initial baseline is the previous 48 hours; earlier failures outside observed coverage are unknown.",
        "nodes": {}, "all_sources": False, "summary": None,
    }
    for label, repo in repos.items():
        old = previous_nodes.get(label) or {}
        current = dict(old.get("workflows") or {}) if old.get("repo") == repo else {}
        try:
            active = workflows(repo, getter)
            feed = events(repo, start, now, getter)
            for run in sorted(feed, key=lambda r: (str(r.get("updated_at") or ""), int(r.get("id") or 0))):
                update_status(current, run, repo)
            # A rerun of an older run ID may finish after its created_at window;
            # refresh the latest previously unresolved runs explicitly.
            old_open = [v.get("run_id") for v in current.values() if v.get("state") == "needs_attention"]
            for rid in old_open[:300]:
                if type(rid) is int:
                    r = getter(f"/repos/{repo}/actions/runs/{rid}")
                    update_status(current, r, repo)
            open_items = sorted(
                (v for k, v in current.items() if int(k) in active and v["state"] == "needs_attention"),
                key=lambda v: v.get("event_at", ""), reverse=True
            )
            out["nodes"][label] = {
                "repo": repo, "observed": True, "active_workflows": len(active),
                "tracked_workflows": len([k for k in current if int(k) in active]),
                "open_count": len(open_items), "open": open_items,
                "workflows": current,
            }
        except Exception as exc:
            # The source is incomplete; do not treat missing data as clear.
            out["nodes"][label] = {
                "repo": repo, "observed": False,
                "error": type(exc).__name__ + ": " + str(exc),
                "workflows": current,
            }
    out["all_sources"] = len(out["nodes"]) == 2 and all(v["observed"] for v in out["nodes"].values())
    if out["all_sources"]:
        out["last_complete_scan"] = utcstr(now)
        out["summary"] = {
            "open_count": sum(v["open_count"] for v in out["nodes"].values()),
            "open": sorted(
                [dict(v, repo=node["repo"]) for node in out["nodes"].values() for v in node["open"]],
                key=lambda v: v["event_at"], reverse=True
            ),
            "tracked_workflows": sum(v["tracked_workflows"] for v in out["nodes"].values()),
        }
    elif last:
        out["last_complete_scan"] = last
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--previous", required=True, type=Path)
    args = parser.parse_args()
    try:
        previous = json.loads(args.previous.read_text())
    except FileNotFoundError:
        previous = None
    report = collect(previous, args.registry)
    args.previous.write_text(json.dumps(report, separators=(",", ":")) + "\n")
    print(json.dumps({
        "all_sources": report["all_sources"],
        "current_open": (report["summary"] or {}).get("open_count"),
        "tracked_workflows": (report["summary"] or {}).get("tracked_workflows"),
        "coverage_since": report["coverage_since"],
    }))
    if not report["all_sources"]:
        raise SystemExit("Incomplete source; health cannot claim zero")


if __name__ == "__main__":
    main()
