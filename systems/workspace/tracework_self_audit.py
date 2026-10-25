"""Tracework self-audit: close only when required current-head checks pass.

No repairs, dispatches, or fabricated success. The GitHub Actions source is authoritative.
"""
import json
import os
import sys
import urllib.request

REQUIRED = (
    "protocol-tests",
    "Publish source-bound research for the live trace surface",
)
MARKER = "<!-- tracework-self-audit/v1 -->"


def evaluate(head, runs):
    verdict = {}
    for name in REQUIRED:
        matches = [r for r in runs if r.get("name") == name and r.get("head_sha") == head]
        matches.sort(key=lambda r: (r.get("created_at", ""), r.get("id", 0)), reverse=True)
        latest = matches[0] if matches else None
        verdict[name] = {
            "state": ("PASS" if latest and latest.get("status") == "completed"
                      and latest.get("conclusion") == "success" else "OPEN"),
            "run_id": latest.get("id") if latest else None,
            "conclusion": latest.get("conclusion") if latest else None,
            "url": latest.get("html_url") if latest else None,
        }
    return {"schema": "tracework-self-audit/v1", "head_sha": head,
            "checks": verdict, "closed": all(v["state"] == "PASS" for v in verdict.values())}


def api(method, endpoint, payload=None):
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    url = "https://api.github.com/repos/" + repo + endpoint
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tracework-self-audit",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def main():
    head = api("GET", "/git/ref/heads/main")["object"]["sha"]
    runs = []
    for page in range(1, 5):
        batch = api("GET", "/actions/runs?branch=main&per_page=100&page=" + str(page))["workflow_runs"]
        runs.extend(batch)
        if len(batch) < 100:
            break
    result = evaluate(head, runs)
    with open("tracework-self-audit.json", "w", encoding="utf-8") as out:
        json.dump(result, out, indent=2)
    print(json.dumps(result, indent=2))
    body = (MARKER + "\nTracework audit loop, opened from the October 25 failures.\n\n"
            "This closes only when both independent GitHub workflows have completed "
            "successfully on the same current main commit. No historical pass or skipped job counts.\n\n"
            + "\n".join("- **" + name + "**: " + v["state"] +
                        (" ([source](" + v["url"] + "))" if v["url"] else " (no current-head run)")
                        for name, v in result["checks"].items())
            + "\n\nCurrent main: `" + head + "`\n")
    issues = api("GET", "/issues?state=all&per_page=100")
    issue = next((i for i in issues if MARKER in (i.get("body") or "") and "pull_request" not in i), None)
    if issue:
        number = issue["number"]
        api("PATCH", "/issues/" + str(number), {"body": body, "state": "closed" if result["closed"] else "open"})
    elif not result["closed"]:
        api("POST", "/issues", {"title": "Tracework self audit — open until all checks pass", "body": body,
                                 "labels": []})
    if not result["closed"]:
        sys.exit("Audit remains open: current main has not passed every required check")


if __name__ == "__main__":
    main()
