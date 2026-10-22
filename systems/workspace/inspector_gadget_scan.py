"""Inspector Gadget: repository-wide workflow incident scanner.

Uses GitHub's REST API with GITHUB_TOKEN. Read-only; no repair dispatch.
Scans recent completed runs, groups related signals by workflow and conclusion,
and emits a source-linked report. Each run ID is stable across scans.
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request


def classify(r):
    conclusion = r.get("conclusion")
    if conclusion in ("cancelled", "failure", "timed_out", "action_required", "startup_failure"):
        return "candidate"
    return None


def build_report(runs, since):
    groups = {}
    for run in runs:
        if not isinstance(run.get("id"), int) or not classify(run):
            continue
        created = run.get("updated_at") or run.get("created_at") or ""
        if created < since:
            continue
        key = (run.get("workflow_id"), run.get("name") or "unnamed", run.get("conclusion"))
        groups.setdefault(key, []).append(run)
    findings = []
    for (workflow_id, name, conclusion), members in sorted(groups.items(), key=lambda x: str(x[0])):
        members.sort(key=lambda r: r["id"])
        findings.append({
            "id": f"inspector-{workflow_id}-{conclusion}-{members[0]['id']}",
            "lane": name,
            "kind": "candidate",
            "event": conclusion,
            "count": len(members),
            "run_ids": [r["id"] for r in members],
            "owner": "source workflow / " + name,
            "dispatch_state": "awaiting_source_verification",
            "verification_gate": "source run conclusion and cause verified before repair",
            "sources": [r.get("html_url") for r in members],
            "head_shas": sorted({r["head_sha"] for r in members if r.get("head_sha")}),
            "observation": f"{len(members)} {conclusion} run(s) observed for {name}; root cause not established",
            "state": "awaiting_verification",
            "next": "Inspect concurrency, source changes, and supersession; retain expected cancellations without repair",
        })
    return {"schema": "inspector-gadget/workflow-scan/v1", "since": since, "scanned": len(runs), "findings": findings}


def fetch_runs(repo, token, pages=10):
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    if "/" not in repo:
        raise ValueError("GITHUB_REPOSITORY owner/repo required")
    runs = []
    for page in range(1, pages + 1):
        query = urllib.parse.urlencode({"per_page": 100, "page": page, "status": "completed"})
        url = f"https://api.github.com/repos/{repo}/actions/runs?{query}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "inspector-gadget",
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            batch = json.load(response).get("workflow_runs", [])
        runs.extend(batch)
        if len(batch) < 100:
            break
    return runs


def main():
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = build_report(fetch_runs(os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_TOKEN", "")), since)
    with open("inspector-gadget-report.json", "w", encoding="utf-8") as out:
        json.dump(report, out, indent=2)
    print(f"Inspector Gadget: {report['scanned']} runs scanned, {len(report['findings'])} incident groups")


if __name__ == "__main__":
    main()
