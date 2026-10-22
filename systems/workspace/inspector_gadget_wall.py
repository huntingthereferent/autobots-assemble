"""Inspector Gadget's wall: a source-owned obstruction with a falsifiable exit.

Walk backward from a verified completion: identify the workflow, failed job
and failed step, then look for later executions of the same obligation.
Do not equate a green CI run with research correctness or a repaired defect.
Read-only, bounded GitHub API calls; no workflow dispatch, edits or retries.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request


_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_MAX_FOLLOWUPS = 100
_MAX_JOBS = 100


def _get(repo, token, endpoint):
    if not _REPO.fullmatch(repo) or not token:
        raise ValueError("GitHub repository and read token required")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{endpoint}",
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "inspector-gadget-wall"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def fetch_jobs(repo, run_id, token):
    """First 100 jobs of a known run; incompleteness is made explicit."""
    if type(run_id) is not int or run_id <= 0:
        raise ValueError("run id required")
    data = _get(repo, token, f"actions/runs/{run_id}/jobs?per_page={_MAX_JOBS}&page=1")
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ValueError("source jobs response malformed")
    return data


def fetch_followups(repo, workflow_id, token):
    """Newest 100 workflow runs, not a claim of exhaustive history."""
    if type(workflow_id) is not int or workflow_id <= 0:
        raise ValueError("workflow id required")
    data = _get(repo, token, f"actions/workflows/{workflow_id}/runs?per_page={_MAX_FOLLOWUPS}&page=1")
    if not isinstance(data, dict) or not isinstance(data.get("workflow_runs"), list):
        raise ValueError("source workflow history malformed")
    return data


def _steps(job_data):
    rows = job_data.get("jobs", [])
    if not isinstance(rows, list):
        raise ValueError("invalid job collection")
    results = []
    for job in rows:
        if not isinstance(job, dict):
            continue
        job_id = job.get("id")
        if type(job_id) is not int:
            continue
        for step in job.get("steps") or []:
            if not isinstance(step, dict) or not isinstance(step.get("name"), str):
                continue
            results.append({"job_id": job_id, "job": str(job.get("name") or ""),
                            "step": step["name"], "conclusion": step.get("conclusion")})
    return results


def _same_obligation(source, subsequent):
    return (type(subsequent.get("id")) is int
            and subsequent["id"] > source["id"]
            and subsequent.get("workflow_id") == source["workflow_id"]
            and subsequent.get("head_branch") == source.get("head_branch")
            and subsequent.get("event") == source.get("event")
            and (not source.get("created_at") or
                 (isinstance(subsequent.get("created_at"), str)
                  and subsequent["created_at"] > source["created_at"])))


def evaluate_wall(source_run, jobs, later, followup_jobs=None):
    """Return a measurable wall and next movement, never a fabricated fix."""
    if (not isinstance(source_run, dict) or type(source_run.get("id")) is not int
            or type(source_run.get("workflow_id")) is not int
            or source_run.get("conclusion") not in
            {"cancelled", "failure", "timed_out", "startup_failure", "action_required"}):
        raise ValueError("source incident not established")
    if not isinstance(jobs, dict) or not isinstance(later, dict):
        raise ValueError("source evidence missing")
    original = _steps(jobs)
    failures = [x for x in original if x["conclusion"] in ("failure", "timed_out")]
    # The wall is pinned to a concrete step where possible, not generic red UI.
    wall_kind = ("failed_step" if failures else
                 "cancellation_or_supersession" if source_run["conclusion"] == "cancelled"
                 else "incident_without_step_witness")
    witness = failures[0] if failures else None
    if not isinstance(later.get("workflow_runs"), list):
        raise ValueError("missing subsequent workflow history")
    followups = sorted((x for x in later["workflow_runs"]
                       if isinstance(x, dict) and _same_obligation(source_run, x)),
                       key=lambda x: (x.get("created_at") or "", x["id"]))
    successful = [x for x in followups if x.get("conclusion") == "success"]
    # A later green run is relevant only if the original failed step can be
    # matched to a successful step in the same named job in that later run.
    next_run = successful[-1] if successful else None
    wall = {
        "schema": "inspector-gadget/wall/v1",
        "wall_id": f"workflow-{source_run['workflow_id']}-run-{source_run['id']}",
        "owner_workflow_id": source_run["workflow_id"],
        "owner_workflow": source_run.get("name"),
        "source_run_id": source_run["id"],
        "source_conclusion": source_run["conclusion"],
        "kind": wall_kind,
        "source_job_id": witness["job_id"] if witness else None,
        "failed_job": witness["job"] if witness else None,
        "failed_step": witness["step"] if witness else None,
        "goal": ("Subsequent execution of the same owning workflow and failing step "
                 "passes; source-owner verifies that the original obligation is satisfied"),
        "later_same_obligation_runs": len(followups),
        "later_success_run_id": next_run["id"] if next_run else None,
        "checked_step_in_later_success": False,
        "wall_state": "chasing",
        "next_movement": "inspect_original_failure",
        "owner_validation_required": True,
        "history_complete": False,
        "history_limit": _MAX_FOLLOWUPS,
        "jobs_complete": type(jobs.get("total_count")) is int and jobs["total_count"] <= len(jobs.get("jobs", [])),
    }
    if wall_kind == "cancellation_or_supersession":
        wall["wall_state"] = "superseded_candidate" if next_run else "cancellation_unclassified"
        wall["next_movement"] = ("verify_expected_supersession" if next_run
                                  else "inspect_concurrency_and_supersession")
    elif witness is None:
        wall["next_movement"] = "locate_failed_job_or_external_boundary"
    elif next_run and followup_jobs is not None:
        step_results = [x for x in _steps(followup_jobs)
                        if x["job"] == witness["job"] and x["step"] == witness["step"]]
        wall["checked_step_in_later_success"] = True
        if step_results and all(x["conclusion"] == "success" for x in step_results):
            wall["wall_state"] = "obligation_pass_observed"
            wall["next_movement"] = "request_owning_lane_witness"
        else:
            wall["next_movement"] = "reproduce_missing_or_failed_step"
    elif next_run:
        wall["next_movement"] = "check_failed_step_in_later_success"
    elif followups:
        wall["next_movement"] = "recheck_after_new_owner_run"
    # If the source workflow has >100 recent runs, the needed evidence may
    # be outside the window. Never claim that no newer run exists.
    return wall


def chase(source_run, *, repo, token, job_reader=fetch_jobs,
          history_reader=fetch_followups):
    """Perform the next bounded, real investigation from the pinned run."""
    jobs = job_reader(repo, source_run["id"], token)
    history = history_reader(repo, source_run["workflow_id"], token)
    provisional = evaluate_wall(source_run, jobs, history)
    followup_jobs = None
    if provisional["kind"] == "failed_step" and provisional["later_success_run_id"]:
        followup_jobs = job_reader(repo, provisional["later_success_run_id"], token)
    return evaluate_wall(source_run, jobs, history, followup_jobs)
