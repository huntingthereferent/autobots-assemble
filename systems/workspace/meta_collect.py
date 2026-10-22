"""Observe GitHub Actions for A and B without scheduling or running research jobs.

Only real status counts from both public repository Actions APIs are recorded.
Writes are deliberately isolated to the meta-observations Git branch.
"""
import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOS = {
    "A": "huntingthereferent/autobots-assemble",
    "B": "aeren-research/continuum-oscillator",
}
STATUSES = ("in_progress", "queued", "pending", "waiting")


def repositories(registry_file):
    """Resolve current node repositories by identity, not old GitHub slugs."""
    doc = json.loads(registry_file.read_text(encoding="utf-8"))
    if doc.get("schema") != "meta-workstation/registry-v1":
        raise ValueError("Invalid meta registry")
    nodes = {n.get("id"): n.get("repo") for n in doc.get("nodes", [])}
    if set(nodes) != {"A", "B"}:
        raise ValueError("Expected exactly two admitted workstations")
    if any(not isinstance(v, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", v)
           for v in nodes.values()):
        raise ValueError("Invalid repository identifier")
    return nodes


def api(path):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "a-b-meta-workstation-observer"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request("https://api.github.com" + path, headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def observe(repo):
    result = {"repo": repo, "observed": False}
    try:
        for status in STATUSES:
            data = api(f"/repos/{repo}/actions/runs?status={status}&per_page=1")
            if not isinstance(data.get("total_count"), int):
                raise ValueError("Missing real GitHub total_count")
            result[status] = data["total_count"]
        latest = api(f"/repos/{repo}/actions/runs?per_page=1")
        run = (latest.get("workflow_runs") or [None])[0]
        result["latest_run_id"] = run["id"] if run else None
        result["observed"] = True
    except (HTTPError, URLError, ValueError, KeyError, TimeoutError) as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    return result


def update(path, now=None, repos=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    previous = json.loads(path.read_text(encoding="utf-8"))
    if previous.get("schema") != "ab-meta-observations/v1":
        raise ValueError("Unexpected meta-observation schema")
    sample = {
        "ts": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "nodes": {key: observe(repo) for key, repo in (repos or REPOS).items()},
    }
    if not any(node["observed"] for node in sample["nodes"].values()):
        raise RuntimeError("No valid GitHub observations; do not insert fabricated data")
    samples = previous.get("samples", [])
    if not isinstance(samples, list):
        raise ValueError("Invalid samples shape")
    if samples and samples[-1].get("ts") == sample["ts"]:
        samples[-1] = sample
    else:
        samples.append(sample)
    # An explicit retention window; readings outside this window are not implied.
    cutoff = (now - dt.timedelta(days=365)).isoformat().replace("+00:00", "Z")
    samples = [s for s in samples if isinstance(s, dict) and str(s.get("ts", "")) >= cutoff]
    previous["samples"] = samples
    previous["last_updated"] = sample["ts"]
    path.write_text(json.dumps(previous, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"ts": sample["ts"], "nodes": sample["nodes"], "retained_samples": len(samples)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-path", required=True, type=Path)
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    update(args.history_path, repos=repositories(args.registry) if args.registry else REPOS)
