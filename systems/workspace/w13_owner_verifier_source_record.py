"""Authenticate the actual owner-W13 native child GitHub run and its log claim.

A GitHub workflow success + exact redacted log is source evidence, NOT an
independently replayed native journal. No worker is created or run. The
original ephemeral child journal was NOT published or retained as an artifact.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess

RECORD = "research/dives/W13-OWNER-NATIVE-VERIFIER-001/dive.json"
SCHEMA = "owner-w13-child-github-source-witness/v1"
REPO = "huntingthereferent/autobots-assemble"
HEAD = "98d5cb136f531f8dd8e174fbd605f4769ecfad64"
RUN_ID = 39135756852
JOB_ID = 117699812720
AUTH_BLOB = "7599869612b58d5949f3bd2b26616a5ffc262af1"
READY_BLOB = "30749a8d126e4bfa46365d65adaecffa3512fdbe"
_SHA = re.compile("[0-9a-f]{40}\\Z")
_EVENT = re.compile("evt_[0-9a-f]{32}\\Z")
_LOG = re.compile(r'"(?P<key>[a-z_]+)":\s*(?:"(?P<string>[^"]*)"|(?P<atom>true|false|[0-9]+))')


def _blob(path: Path) -> str:
    return subprocess.check_output(["git","hash-object",str(path)],text=True).strip()


def extract_report(log_text: str) -> dict:
    """Extract only the exact redacted reported native RESULT; never log a journal."""
    if type(log_text) is not str or len(log_text) > 4_000_000:
        raise ValueError("job log absent or oversized")
    keys=(
        "schema","original_run_id","owner_authorization_commit",
        "parent_job_id","parent_event_id","child_job_id",
        "child_result_event_id","child_worker_source_fingerprint",
        "game_w13_cp","game_native_verifier_cp","game_worker_ready_cp",
        "source_owner_authorized","new_child_admitted","one_native_child_executed",
        "fresh_native_child_reverified","private_journal_uploaded",
        "official_game_or_scientific_claim"
    )
    report={}
    for line in log_text.splitlines():
        m=_LOG.search(line)
        if not m or m["key"] not in keys:
            continue
        key=m["key"]
        if key in report:
            raise ValueError("ambiguous duplicate log source field: "+key)
        raw=m["string"]
        if raw is not None:
            value=raw
        elif m["atom"] in ("true","false"):
            value=m["atom"]=="true"
        else:
            value=int(m["atom"])
        report[key]=value
    if set(report)!=set(keys):
        raise ValueError("exact original child RESULT fields missing in GitHub log")
    return report


def verify_source(*, repo_root: Path, run: dict, jobs: dict,
                  artifacts: dict, log_text: str) -> dict:
    root=Path(repo_root).resolve()
    rec=json.loads((root/RECORD).read_text(encoding="utf8"))
    source=rec.get("source_run")
    claim=rec.get("reported_native_result")
    readiness=rec.get("original_readiness")
    if rec.get("schema_version")!=1 or rec.get("result_state")!="MOVE_WITH_WALL":
        raise ValueError("new source record has wrong research scope")
    if not all(type(x) is dict for x in (source,claim,readiness)):
        raise ValueError("unstructured source report")
    if (source.get("repository"),source.get("run_id"),source.get("job_id"),
        source.get("head_sha"),source.get("owner_request_git_blob"))!=(
            REPO,RUN_ID,JOB_ID,HEAD,AUTH_BLOB):
        raise ValueError("source report is not the original owner-run witness")
    if (_blob(root/source["owner_request_path"])!=AUTH_BLOB or
            _blob(root/readiness["bridge_path"])!=READY_BLOB):
        raise ValueError("owner authorization or readiness implementation changed")
    if not (type(run) is dict and run.get("id")==RUN_ID
            and run.get("name")==source["workflow"]
            and run.get("head_sha")==HEAD
            and run.get("event")==source["event"]=="push"
            and run.get("head_branch")==source["branch"]=="main"
            and run.get("status")=="completed" and run.get("conclusion")=="success"
            and run.get("run_attempt")==1
            and (run.get("actor") or {}).get("login")==source["actor"]):
        raise ValueError("GitHub execution is not the authorized original owner run")
    listed=jobs.get("jobs") if type(jobs) is dict else None
    owned=[j for j in (listed if type(listed) is list else ()) if j.get("id")==JOB_ID]
    if len(owned)!=1:
        raise ValueError("exact GitHub run job missing or ambiguous")
    job=owned[0]
    if (job.get("run_id")!=RUN_ID or job.get("head_sha")!=HEAD
            or job.get("name")!=source["job_name"]
            or job.get("status")!="completed" or job.get("conclusion")!="success"):
        raise ValueError("GitHub source job is not the successful native witness")
    steps=job.get("steps")
    required=(
        "Authenticate NEW exact owner request before fetching original archive",
        "Authenticate original owner-run and immutable evidence artifact",
        "Download authenticated original W13 artifact with digest validation",
        "Execute exactly ONE separately authorized native verifier child"
    )
    if type(steps) is not list or any(
        len([x for x in steps if x.get("name")==name and x.get("conclusion")=="success"])!=1
        for name in required):
        raise ValueError("GitHub job did not complete all original source gates")
    if extract_report(log_text)!=claim:
        raise ValueError("reported event or worker result does not match exact original job log")
    if not _EVENT.fullmatch(claim["child_result_event_id"]) or not _SHA.fullmatch(source["head_sha"]):
        raise ValueError("reported original event/source is not a bounded ID")
    if claim["owner_authorization_commit"]!=HEAD or claim["original_run_id"]!=39025574748:
        raise ValueError("reported child did not cite the original owner authorization and parent")
    if (claim["game_native_verifier_cp"],claim["game_worker_ready_cp"])!=(
            "WITNESSED","ADMISSIBLE"):
        raise ValueError("reported native verification did not preserve CP frontier")
    # This is a historical observation about a single finished run, not a
    # guarantee no artifacts will ever be published in another system.
    available=artifacts.get("artifacts") if type(artifacts) is dict else None
    if type(available) is not list or available:
        raise ValueError("unexpected child artifacts; re-audit preservation boundary")
    if (readiness["original_owner_child_runtime_artifact_count_at_inspection"]!=0
            or readiness["native_child_replayable_in_later_runner"] is not False
            or readiness["game_worker_ready_owner_run_executed"] is not False
            or readiness["legacy_readiness_contract_directly_compatible_with_owner_job_ids"] is not False
            or readiness["separate_required_live_parent"]!="live-game-temporal-001"
            or set(readiness["original_owner_parent_jobs"])!={
                "game-w13-github-001","game-native-verifier-github-001"}):
        raise ValueError("readiness gap has been silently declared solved")
    return {
        "schema":SCHEMA,
        "state":"GITHUB_OWNER_RESULT_OBSERVED_NO_PORTABLE_CHILD_JOURNAL",
        "original_run_id":RUN_ID,
        "original_job_id":JOB_ID,
        "original_w13_cp":"WITNESSED_REPORTED_AND_PREVIOUSLY_REPLAYED",
        "game_native_verifier_cp":"WITNESSED_IN_ORIGINAL_RUN",
        "game_worker_ready_cp":"ADMISSIBLE_NOT_ADMITTED",
        "redacted_result_log_matched":True,
        "source_run_metadata_authenticated":True,
        "native_child_replayed_from_retained_journal":False,
        "original_live_temporal_parent_reverified_here":False,
        "ready_worker_executed":False,
        "private_journal_published":False,
        "external_scientific_claim":False
    }
