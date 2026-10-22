"""Inspector Gadget -> native HandoffRuntime source-observation adapter.

Activation is movement: each selected CI signal is admitted as an actual handoff,
runs an independent read of its GitHub Actions source, and records a result.
A completed inspection is NOT a repaired workflow or verified research finding.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from systems.workspace.audit_to_action import process
from systems.workspace.inspector_gadget_wall import chase as chase_wall

VERIFIER = "inspector-gadget-github-run-v1"
RELATION = "verify source-owned workflow incident"
WITNESS = "GitHub Actions run matches the pinned incident"
EVENTS = {"cancelled", "failure", "timed_out", "action_required", "startup_failure"}
_MAX_MOVEMENTS = 200
_ID = re.compile(r"inspector-(\d+)-(cancelled|failure|timed_out|action_required|startup_failure)-(\d+)\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def _selection(entry):
    """Translate one scan group into one stable owning-workflow follow-up."""
    match = _ID.fullmatch(str(entry.get("id", "")))
    if match is None or entry.get("kind") != "candidate" or entry.get("event") != match.group(2):
        raise ValueError("invalid Inspector Gadget candidate")
    ids, sources = entry.get("run_ids"), entry.get("sources")
    if not isinstance(ids, list) or not ids or not all(type(i) is int and i > 0 for i in ids):
        raise ValueError("missing incident run ids")
    if not isinstance(sources, list) or len(sources) != len(ids):
        raise ValueError("incident source cardinality mismatch")
    run_id = ids[-1]
    source = sources[-1]
    if not isinstance(source, str) or not source.startswith("https://github.com/") or not source.endswith("/actions/runs/" + str(run_id)):
        raise ValueError("incident source must identify its exact run")
    name = entry.get("lane")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("missing source workflow owner")
    sha_list = entry.get("head_shas", [])
    pinned_sha = sha_list[0] if len(sha_list) == 1 else ""
    if pinned_sha and (not isinstance(pinned_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", pinned_sha)):
        raise ValueError("invalid pinned source revision")
    return {"finding_id": entry["id"], "lane": name, "event": entry["event"],
            "workflow_id": int(match.group(1)), "run_id": run_id,
            "source": source, "head_sha": pinned_sha, "count": len(ids)}


def plan(report, max_movements=_MAX_MOVEMENTS):
    """Create a bounded matrix; visibly retain the overflow rather than lose it."""
    if not isinstance(report, dict) or report.get("schema") != "inspector-gadget/workflow-scan/v1":
        raise ValueError("unsupported Inspector Gadget scan")
    if not isinstance(max_movements, int) or not 1 <= max_movements <= 256:
        raise ValueError("invalid GitHub Actions matrix limit")
    findings = report.get("findings")
    if not isinstance(findings, list):
        raise ValueError("missing findings")
    selected = []
    seen = set()
    withheld = []
    for entry in findings:
        row = _selection(entry)
        if row["finding_id"] in seen:
            raise ValueError("duplicate Inspector Gadget incident")
        seen.add(row["finding_id"])
        # Do not recursively activate the scanner's own transient failures.
        if row["lane"].startswith("Inspector Gadget"):
            withheld.append(row["finding_id"])
        else:
            selected.append(row)
    selected.sort(key=lambda x: (x["run_id"], x["finding_id"]))
    return {"schema": "inspector-gadget/activation-plan/v1",
            "matrix": {"include": selected[:max_movements]},
            "selected": min(len(selected), max_movements),
            "overflow_count": max(0, len(selected) - max_movements),
            "self_observation_withheld": withheld,
            "observed_findings": len(findings)}


def from_cancel_event(event):
    """Direct, source-owned cancellation trigger for the existing four workflows."""
    run = event.get("workflow_run", {})
    if event.get("action") != "completed" or run.get("conclusion") != "cancelled":
        raise ValueError("only a completed cancellation activates this adapter")
    run_id = run.get("id")
    workflow_id = run.get("workflow_id")
    if type(run_id) is not int or type(workflow_id) is not int:
        raise ValueError("source event must pin its run and workflow identities")
    return _selection({
        "id": f"inspector-{workflow_id}-cancelled-{run_id}",
        "kind": "candidate", "event": "cancelled",
        "lane": run.get("name"), "run_ids": [run_id],
        "sources": [run.get("html_url")],
        "head_shas": [run["head_sha"]] if run.get("head_sha") else [],
    })


def fetch_run(repo, run_id, token):
    """Native independent source read; never reruns or edits a workflow."""
    if not _REPO.fullmatch(repo) or not token:
        raise ValueError("GitHub repository and read token are required")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/runs/{run_id}",
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "inspector-gadget-adapter"})
    with urllib.request.urlopen(req, timeout=25) as result:
        return json.load(result)


class SourceObservationWorker:
    def __init__(self, handoff_id, repo, token, fetcher, wall_chaser=None):
        self.handoff_id, self.repo, self.token, self.fetcher = handoff_id, repo, token, fetcher
        self.wall_chaser = wall_chaser
        self.actor_id = "inspector-gadget:source-observer"

    def can_execute(self, handoff):
        return handoff.handoff_id == self.handoff_id and handoff.to_actor == self.actor_id and handoff.required_relation == RELATION

    def execute(self, handoff):
        if not self.can_execute(handoff):
            raise ValueError("wrong Inspector Gadget handoff")
        expected = handoff.inputs
        run = self.fetcher(self.repo, expected["run_id"], self.token)
        if not isinstance(run, dict):
            raise ValueError("GitHub source returned invalid run payload")
        matching = (
            type(run.get("id")) is int and run["id"] == expected["run_id"]
            and type(run.get("workflow_id")) is int and run["workflow_id"] == expected["workflow_id"]
            and run.get("name") == expected["lane"]
            and run.get("conclusion") == expected["event"]
            and run.get("html_url") == expected["source"]
            and (not expected["head_sha"] or run.get("head_sha") == expected["head_sha"])
        )
        output = {
            "source_verified": matching, "observed_conclusion": run.get("conclusion"),
            "observed_head_sha": run.get("head_sha"),
            "owner_lane": expected["lane"], "repair_dispatched": False,
            "diagnosis": "not established",
            "next": "Owning lane should inspect cause, supersession and subsequent successful runs" if matching
                    else "Source boundary changed or mismatched; request owner verification",
        }
        if not matching:
            return ExecutionResult(status="PARTIAL", output=output,
                                   note="source record does not match the pinned scan")
        # Work backwards from the desired same-step success. The chase reads
        # concrete failed jobs and later workflow evidence; it never repairs.
        output["wall"] = (self.wall_chaser(run, repo=self.repo, token=self.token)
                          if self.wall_chaser is not None else
                          {"schema": "inspector-gadget/wall/v1", "wall_state": "not_checked",
                           "next_movement": "chase_live_workflow_evidence",
                           "owner_validation_required": True})
        evidence = (EvidenceRecord(condition=WITNESS, kind="source-api-comparison",
                                   source="GitHub Actions", ref=expected["source"],
                                   depth="live-source-read"),)
        return ExecutionResult(status="COMPLETE", output=output, evidence=evidence,
                               note="source observation verified; no repair was attempted")


def _verify_result(handoff, result):
    if result.status != "COMPLETE":
        return
    if (result.output.get("source_verified") is not True
        or result.output.get("repair_dispatched") is not False
        or result.output.get("owner_lane") != handoff.inputs["lane"]
        or result.evidence != (EvidenceRecord(
            condition=WITNESS, kind="source-api-comparison", source="GitHub Actions",
            ref=handoff.inputs["source"], depth="live-source-read"),)):
        raise ValueError("Inspector Gadget source observation evidence rejected")


def activate(selection, *, repo, token, fetcher=fetch_run, journal_path=None, wall_chaser=None):
    """Execute one REAL source-observation worker in the owning workflow context."""
    # Reapply the exact scanner validation to untrusted matrix/event inputs.
    row = _selection({"id": selection.get("finding_id"), "kind": "candidate",
                      "event": selection.get("event"), "lane": selection.get("lane"),
                      "run_ids": [selection.get("run_id")],
                      "sources": [selection.get("source")],
                      "head_shas": [selection["head_sha"]] if selection.get("head_sha") else []})
    if (row["workflow_id"] != selection.get("workflow_id")
        or row["lane"].startswith("Inspector Gadget")
        or not _REPO.fullmatch(repo)
        or not row["source"].startswith("https://github.com/" + repo + "/")):
        raise ValueError("handoff is outside the owning repository or source workflow")
    finding = process({"findings": [{
        "id": row["finding_id"], "kind": "candidate", "lane": row["lane"],
        "observation": f"{row['event']} GitHub workflow run; root cause unverified",
        "source": row["source"],
        "proposed_action": "Inspect source-owned run without modifying research",
        "verification": "Read exact GitHub run ID, workflow identity, conclusion and pinned SHA",
    }]})["findings"][0]
    if finding["action"] != "verify" or finding["state"] != "awaiting_verification":
        raise ValueError("audit-to-action rejected source verification")
    job_id = "inspector-gadget-" + str(row["run_id"])
    handoff = Handoff(
        handoff_id=job_id, referent=f"Inspector Gadget / {row['lane']} / {row['run_id']}",
        from_actor="inspector-gadget:scan", to_actor="inspector-gadget:source-observer",
        required_relation=RELATION, inputs=row,
        expected_output={"source_verified": "boolean", "repair_dispatched": False},
        required_witnesses=(WITNESS,),
        admissible_evidence={WITNESS: ("source-api-comparison",)},
        provenance=(row["source"], "workspace-lane:" + row["lane"]),
        boundaries=("Source observation is not a defect diagnosis.",
                    "Inspector completion does not imply an owning-lane fix.",
                    "Expected cancellations must not automatically trigger a repair."),
        metadata={"native_evidence_verifier": VERIFIER, "title": "Inspector Gadget source observation",
                  "source_system": "inspector-gadget", "worker_id": "inspector-gadget",
                  "worker_version": "github-source-v1", "workstation_worker": True,
                  "source_run_id": row["run_id"]})
    runtime = HandoffRuntime(event_store=RuntimeJournal(journal_path) if journal_path else None)
    runtime.register_evidence_verifier(VERIFIER, _verify_result)
    runtime.submit(handoff)
    # The real GitHub worker always chases the source wall. Fixture readers
    # deliberately do not turn a mocked run into a claimed live investigation.
    observer = wall_chaser if wall_chaser is not None else (chase_wall if fetcher is fetch_run else None)
    state = runtime.run(job_id, SourceObservationWorker(job_id, repo, token, fetcher, observer))
    return {"schema": "inspector-gadget/handoff-result/v1",
            "audit": finding, "handoff": asdict(handoff),
            "state": asdict(state),
            "events": [asdict(e) for e in runtime.event_store.for_handoff(job_id)]}


def _write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv):
    if len(argv) != 4 or argv[1] not in {"matrix", "inspect", "event"}:
        raise SystemExit("usage: inspector_gadget_adapter.py matrix|inspect|event INPUT OUTPUT")
    command, source, output = argv[1:]
    if command == "matrix":
        _write(output, plan(json.loads(Path(source).read_text(encoding="utf-8"))))
        return
    if command == "event":
        selection = from_cancel_event(json.loads(Path(source).read_text(encoding="utf-8")))
    else:
        selection = json.loads(Path(source).read_text(encoding="utf-8"))
    _write(output, activate(selection, repo=os.environ.get("GITHUB_REPOSITORY", ""),
                            token=os.environ.get("GITHUB_TOKEN", ""),
                            journal_path=Path(output).with_name("inspector-gadget-runtime.jsonl")))


if __name__ == "__main__":
    main(sys.argv)
