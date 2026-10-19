"""Read-only separate-run restoration of the exact retained owner readiness."""
from __future__ import annotations
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

REPO = "huntingthereferent/autobots-assemble"
REPO_ID = 1403664339
OWNER_ID = 331854748
RUN = 39183388852
ARTIFACT = 12156672990
COMMIT = "b939f577962f737cc60a977977d5ca9adc0731d6"
DIGEST = "sha256:34ee7433aee5882c71cdb38410e812d6db4a46ab7a21b7589835ac6ae1c834a5"
SEALED_SHA = "18cba8f958a9f3654362eb00a249d244e9bc77b65afd9a6b655045a9cc047e88"
READY_JOB = "game-worker-ready-owner-001"
READY_EVENT = "evt_74329dc7684b487abfe7bf7ad3538897"
READY_FINGERPRINT = "b6ed010d128d713af995945ced90d8094b884a2c3b96cdf9a2c80c8d3618d289"
CHILD_EVENT = "evt_a9ba637571d04967ab777c71a2945a64"


def validate_origin(run, artifact):
    if (run.get("id") != RUN or run.get("name") != "owner W13 native adapter readiness"
            or run.get("head_sha") != COMMIT or run.get("run_attempt") != 1
            or run.get("event") != "push" or run.get("head_branch") != "main"
            or run.get("status") != "completed" or run.get("conclusion") != "success"
            or run.get("actor",{}).get("id") != OWNER_ID
            or run.get("actor",{}).get("login") != "huntingthereferent"
            or run.get("repository",{}).get("id") != REPO_ID
            or run.get("head_repository",{}).get("id") != REPO_ID
            or run.get("head_repository",{}).get("full_name") != REPO):
        raise ValueError("exact successful owner readiness producer required")
    origin = artifact.get("workflow_run",{})
    if (artifact.get("id") != ARTIFACT or artifact.get("name") != f"owner-ready-encrypted-{RUN}"
            or artifact.get("digest") != DIGEST or artifact.get("expired") is not False
            or origin.get("id") != RUN or origin.get("head_sha") != COMMIT
            or origin.get("repository_id") != REPO_ID):
        raise ValueError("retained readiness artifact expired or source identity differs")


def validate_receipt(receipt, sealed_bytes):
    sealed = receipt.get("encrypted_retention",{})
    if (receipt.get("schema") != "owner-W13-native-ready-result/v1"
            or receipt.get("owner_merge") != COMMIT or receipt.get("job_id") != READY_JOB
            or receipt.get("ready_result_event") != READY_EVENT
            or receipt.get("ready_source_fingerprint") != READY_FINGERPRINT
            or receipt.get("game_worker_ready_witnessed") is not True
            or receipt.get("external_temporal_input_reverified") is not True
            or receipt.get("temporal_history_imported") is not False
            or receipt.get("native_job_count_added") != 1
            or receipt.get("nih_p2_test_witnessed") is not False
            or receipt.get("private_journal_published") is not False
            or sealed.get("owner_execution_commit") != COMMIT
            or sealed.get("child_event") != CHILD_EVENT
            or sealed.get("sealed_sha256") != SEALED_SHA
            or sha256(sealed_bytes).hexdigest() != SEALED_SHA):
        raise ValueError("exact retained readiness RESULT or capsule binding differs")


def validate_native(receipt):
    results = [e for e in receipt.get("events",()) if e.get("type") == "RESULT"]
    if (receipt.get("job_id") != READY_JOB
            or receipt.get("worker_id") != "game-worker-ready"
            or receipt.get("worker_version") != "owner-adapter-v1"
            or receipt.get("source_fingerprint") != READY_FINGERPRINT
            or receipt.get("recorded_status") != "COMPLETE"
            or receipt.get("verification") != "FRESH_NATIVE_REVERIFICATION_LOCAL"
            or len(results) != 1 or results[0].get("event_id") != READY_EVENT
            or results[0].get("result_status") != "COMPLETE"):
        raise ValueError("restored readiness lacks exact fresh native RESULT")


def main():
    producer = Path(os.environ["PRODUCER_SOURCE"]).resolve()
    commit = subprocess.run(["git","-C",str(producer),"rev-parse","HEAD"],
        capture_output=True,text=True,check=True,timeout=10).stdout.strip()
    if commit != COMMIT:
        raise ValueError("native verifier checkout differs from producer source")
    # Import the original producer's native host and controls, not a newer
    # implementation that might reinterpret the historical readiness result.
    sys.path.insert(0,str(producer))
    from systems.workspace.owner_temporal_handoff import _get, unpack_zip
    from systems.workspace.owner_native_evidence_vault import restore_verified
    from systems.workspace.native_receipt_projection import reverify_local
    from systems.workspace.coordinator_window import CoordinatorIndex, freshly_reverify_linked_jobs
    from systems.workspace.cp_motion import workstation_cp_view, one_cp_handoff
    from systems.workspace.controls import reverify_job
    token = os.environ["GH_TOKEN"]
    run = _get(f"actions/runs/{RUN}",token)
    artifact = _get(f"actions/artifacts/{ARTIFACT}",token)
    validate_origin(run,artifact)
    with TemporaryDirectory(prefix="owner-ready-cross-run-") as tmp:
        root = Path(tmp)
        raw = _get(f"actions/artifacts/{ARTIFACT}/zip",token,binary=True)
        unpack_zip(raw,root/"artifact",DIGEST)
        capsule = root/"artifact"/"continuation.enc"
        validate_receipt(json.loads((root/"artifact"/"receipt.json").read_text()),capsule.read_bytes())
        private = base64.b64decode(os.environ["PRIVATE_KEY_B64"],validate=True)
        restore_verified(encrypted=capsule,private_key_raw=private,destination=root/"native",
            expected_owner_execution_commit=COMMIT,expected_child_event=CHILD_EVENT)
        data = root/"native"
        before = {name:sha256((data/name).read_bytes()).hexdigest()
                  for name in ("runtime.jsonl","coordinator-windows.jsonl")}
        ready = reverify_local(data,READY_JOB)
        validate_native(ready)
        index = CoordinatorIndex(data/"coordinator-windows.jsonl")
        checked = freshly_reverify_linked_jobs(index,"complete-stack",workstation_cp_view(data),
            lambda job:reverify_job(data_dir=data,job_id=job))
        frontier = one_cp_handoff(index,"complete-stack",checked,reverified=True)["cp_automation"]
        if "GAME-WORKER-READY" not in frontier["witnessed"] or "NIH-P2-TEST" in frontier["witnessed"]:
            raise ValueError("restored coordinator readiness frontier differs")
        if before != {name:sha256((data/name).read_bytes()).hexdigest() for name in before}:
            raise ValueError("read-only restoration witness changed native journals")
        print(json.dumps({"schema":"owner-ready-separate-run-restoration/v1",
            "state":"EXACT_READY_RESULT_RESTORED_AND_FRESHLY_REVERIFIED",
            "source_run":RUN,"source_artifact":ARTIFACT,"source_commit":COMMIT,
            "ready_job":READY_JOB,"ready_result_event":READY_EVENT,
            "game_worker_ready_witnessed":True,"separate_run_ready_restore_witnessed":True,
            "journal_hashes_unchanged":True,"new_workers_executed":0,
            "nih_p2_test_witnessed":False,"private_journal_published":False},sort_keys=True))


if __name__ == "__main__":
    main()
