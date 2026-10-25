"""Read-only GitHub evidence resolver for finite audit workflow nodes.

A/B: claimed evidence (A) and independent GitHub observation (B).
Mismatch stays open. Never automatically admit a run or mark a node passed.
"""
import json
import os
import urllib.request


def github_run(repo, token, run_id):
    if not isinstance(run_id, int) or run_id <= 0:
        raise ValueError("positive workflow run ID required")
    if not token or not repo or "/" not in repo:
        raise ValueError("authenticated source required")
    req = urllib.request.Request(
        "https://api.github.com/repos/" + repo + "/actions/runs/" + str(run_id),
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "tracework-bounded-audit"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def verify_workflow(node, source):
    """Return an explicit source comparison; no mutation or inferred success."""
    evidence = node.get("evidence") or {}
    expected = {
        "id": evidence.get("run_id"),
        "head_sha": evidence.get("head_sha"),
        "conclusion": "success",
        "status": "completed",
    }
    observed = {key: source.get(key) for key in expected}
    # Bind workflow identity when supplied, rather than accepting a different
    # workflow's successful run.
    workflow = evidence.get("workflow_name")
    identity_ok = isinstance(workflow, str) and bool(workflow) and source.get("name") == workflow
    source_url = source.get("html_url", "")
    expected_url = evidence.get("source")
    url_ok = bool(source_url) and source_url == expected_url
    matches = (all(expected[k] == observed[k] for k in expected)
               and identity_ok and url_ok and evidence.get("verified") is True)
    return {"node": node["id"], "matches": matches,
            "expected": expected, "observed": observed,
            "identity_matches": identity_ok, "url_matches": url_ok}


def verify_audit(audit, fetch):
    """Evaluate all workflow nodes; a single missing source blocks closure."""
    comparisons = {}
    for node in audit["nodes"]:
        if node["kind"] != "workflow":
            continue
        evidence = node.get("evidence") or {}
        try:
            run = fetch(evidence.get("run_id"))
            comparisons[node["id"]] = verify_workflow(node, run)
        except (ValueError, TypeError, KeyError, OSError) as exc:
            comparisons[node["id"]] = {"node": node["id"], "matches": False,
                                       "error": str(exc)}
    return comparisons
