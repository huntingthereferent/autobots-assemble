"""Complete day-window GitHub workflow outcome counts for the shared Meta viewer.

A workflow run is not a test case. GitHub's `created` filter covers *runs
created during the local day*, not necessarily work finished during the day.
Historical failure and cancellation totals do not represent open problems.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

try:
    from .meta_collect import api, repositories
except ImportError:  # Running meta_daily.py directly inside the Actions workspace.
    from meta_collect import api, repositories

TZ = ZoneInfo("America/Chicago")
CONCLUSIONS = ("success", "failure", "cancelled", "skipped", "timed_out", "action_required")


def day_window(now):
    if now.tzinfo is None:
        raise ValueError("UTC-aware clock required")
    local_day = now.astimezone(TZ).date()
    start_local = dt.datetime.combine(local_day, dt.time.min, tzinfo=TZ)
    end_local = dt.datetime.combine(local_day + dt.timedelta(days=1), dt.time.min, tzinfo=TZ)
    def utc(value):
        return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return local_day.isoformat(), utc(start_local), utc(end_local - dt.timedelta(seconds=1))


def github_count(repo, date_query, status=None, getter=api):
    path = f"/repos/{repo}/actions/runs?created={quote(date_query, safe='')}&per_page=1"
    if status:
        path += "&status=" + status
    response = getter(path)
    count = response.get("total_count")
    if type(count) is not int or count < 0:
        raise ValueError("Missing actual GitHub total_count")
    return count


def collect(repos, now=None, getter=api):
    now = now or dt.datetime.now(dt.timezone.utc)
    local_date, start, end = day_window(now)
    period = start + ".." + end
    result = {
        "schema": "meta-workstation/daily-runs-v1",
        "timezone": "America/Chicago",
        "local_date": local_date,
        "start_utc": start,
        "end_utc": end,
        "observed_at": now.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "basis": "GitHub Actions workflow runs created during today's America/Chicago calendar day; all-matching-source total_count, not last-100 samples.",
        "limitations": "Failed and cancelled runs are historical outcomes, NOT unresolved tests. Later runs can pass the same workflow. A run is not a single test.",
        "nodes": {},
    }
    for node, repo in repos.items():
        counts = {"repo": repo, "observed": False}
        try:
            counts["created"] = github_count(repo, period, getter=getter)
            for status in CONCLUSIONS:
                counts[status] = github_count(repo, period, status=status, getter=getter)
            if sum(counts[s] for s in CONCLUSIONS) > counts["created"]:
                raise ValueError("Inconsistent GitHub date-filtered total_count")
            counts["other"] = counts["created"] - sum(counts[s] for s in CONCLUSIONS)
            counts["observed"] = True
        except Exception as error:
            counts = {"repo": repo, "observed": False, "error": type(error).__name__ + ": " + str(error)}
        result["nodes"][node] = counts
    result["all_sources"] = set(result["nodes"]) == {"A", "B"} and all(
        x["observed"] for x in result["nodes"].values()
    )
    if result["all_sources"]:
        result["totals"] = {
            field: sum(node[field] for node in result["nodes"].values())
            for field in ("created", *CONCLUSIONS, "other")
        }
    else:
        result["totals"] = None
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = collect(repositories(args.registry))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": report["local_date"], "observed_at": report["observed_at"],
                      "all_sources": report["all_sources"], "totals": report["totals"]}))
