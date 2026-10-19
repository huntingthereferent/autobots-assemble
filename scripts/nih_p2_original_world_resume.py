"""Re-enter the retained 12-job W13 NIH-P2 game world; do not start another lineage.

Download via GitHub Actions download-artifact from the exact successful original
owner source run, restore its native journal, and execute the existing world
publication-uncertainty browser experiment on THAT journal. Never modify the
native event history, import outside workers, or declare new NIH checkpoints.
"""
from __future__ import annotations
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
from urllib.request import Request, urlopen

REPO="huntingthereferent/autobots-assemble"
RUN=39160329599
ARTIFACT=12147754403
SOURCE="34652b7b788fe21cc470273c953ae0ea1799b1e9"
ARTIFACT_DIGEST="sha256:5bad19007c2dd69e6c221a43ed3d3547dede01696559edd5a89918869ff48c30"
ARTIFACT_NAME="nih-phase1-world-publication-uncertainty-39160329599-1"
MAX_TAR=16*1024*1024
MAX_FILES=2500
MAX_EXTRACTED=55*1024*1024

def api(route,token):
    req=Request(f"https://api.github.com/repos/{REPO}/{route}",headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"NIH-original-W13-journal-resume"})
    with urlopen(req,timeout=20) as resp:
        raw=resp.read(1_000_001)
    if len(raw)>1_000_000: raise ValueError("source API response exceeded bound")
    return json.loads(raw)

def check_run(run,artifact):
    if (run.get("id")!=RUN or run.get("head_sha")!=SOURCE
        or run.get("event")!="push" or run.get("head_branch")!="main"
        or run.get("run_attempt")!=1 or run.get("status")!="completed"
        or run.get("conclusion")!="success"
        or run.get("name")!="NIH Phase 1 original world uncertain-publication witness"
        or run.get("actor",{}).get("login")!="huntingthereferent"
        or run.get("head_repository",{}).get("full_name")!=REPO):
        raise ValueError("original twelve-job world run is not independently authenticated")
    if (artifact.get("id")!=ARTIFACT or artifact.get("name")!=ARTIFACT_NAME
        or artifact.get("expired") is not False
        or artifact.get("digest")!=ARTIFACT_DIGEST
        or artifact.get("workflow_run",{}).get("id")!=RUN):
        raise ValueError("retained owner game-world artifact unavailable or changed")

def unpack_native(archive,dest):
    if not archive.is_file() or archive.is_symlink() or archive.stat().st_size>MAX_TAR:
        raise ValueError("original native journal tar unavailable or excessive")
    allowed={"runtime.jsonl","coordinator-windows.jsonl","workstation"}
    with tarfile.open(archive,"r:gz") as tar:
        seen=set()
        total=0
        for n,entry in enumerate(tar,1):
            name=entry.name[2:] if entry.name.startswith("./") else entry.name
            rel=PurePosixPath(name)
            if (n>MAX_FILES or not name or rel.is_absolute() or ".." in rel.parts
                or rel.parts[0] not in allowed
                or (rel.parts[0]!="workstation" and len(rel.parts)!=1)
                or not (entry.isfile() or entry.isdir()) or name in seen
                or len(name)>280):
                raise ValueError("unsafe or unexpected original native tar entry")
            seen.add(name)
            total+=entry.size
            if total>MAX_EXTRACTED: raise ValueError("original journal expanded too large")
            target=dest.joinpath(*rel.parts)
            if entry.isdir():
                target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(tar.extractfile(entry).read())
                target.chmod(0o600)
    for name in ("runtime.jsonl","coordinator-windows.jsonl"):
        if not (dest/name).is_file(): raise ValueError("missing original journal source")
    if not (dest/"workstation").is_dir(): raise ValueError("missing copied source-owned worker editions")

def main():
    root=Path(os.environ["RUNNER_TEMP"])
    evidence=root/"source-world"
    native=root/"restored-original-w13"
    output=root/"continued-original-w13"
    if native.exists() or output.exists():
        raise ValueError("refuse overwritten native reconstruction")
    source=Path(os.environ["ORIGINAL_SOURCE_DIR"]).resolve()
    actual=subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
    if actual!=SOURCE: raise ValueError("must execute the historical source implementation")
    token=os.environ["GH_TOKEN"]
    check_run(api(f"actions/runs/{RUN}",token),api(f"actions/artifacts/{ARTIFACT}",token))
    original=json.loads((evidence/"nih-phase1-world-publication-uncertainty.json").read_text())
    if (original.get("schema")!="nih-phase1-original-world-publication-uncertainty/v1"
        or original.get("original_native_jobs")!=12
        or original.get("independent_three_state_policy_verified") is not True
        or original.get("original_native_journals_preserved") is not True
        or original.get("real_historical_publication_authenticated") is not False):
        raise ValueError("last retained original world observations differ")
    native.mkdir(mode=0o700)
    unpack_native(evidence/"original-native-journal.tgz",native)
    output.mkdir(mode=0o700)
    for child in evidence.iterdir():
        if child.is_file() and child.name!="original-native-journal.tgz":
            shutil.copy2(child,output/child.name)
    before={name:sha256((native/name).read_bytes()).hexdigest()
            for name in ("runtime.jsonl","coordinator-windows.jsonl")}
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from systems.workspace.controls import reverify_job
    from systems.workspace.nih_phase1_world_publication_uncertainty import run_world
    original_jobs=HandoffRuntime(event_store=RuntimeJournal(native/"runtime.jsonl")).snapshot()
    if len(original_jobs)!=12 or "nih-p2-benchmark-001" not in original_jobs:
        raise ValueError("retained source isn't the original witnessed 12-job Phase 2 game world")
    verified=reverify_job(data_dir=native,job_id="nih-p2-benchmark-001")
    if (verified.get("status")!="COMPLETE" or verified.get("reverified") is not True
        or verified.get("executed") is not False):
        raise ValueError("original Phase 2 benchmark is not freshly reverified")
    report=run_world(data_dir=native,output_dir=output)
    after={name:sha256((native/name).read_bytes()).hexdigest() for name in before}
    new_jobs=HandoffRuntime(event_store=RuntimeJournal(native/"runtime.jsonl")).snapshot()
    if before!=after or set(original_jobs)!=set(new_jobs):
        raise ValueError("continued world changed original source-owned journal or jobs")
    if (report.get("original_native_jobs")!=12
        or report.get("played_original_game_solved") is not True
        or report.get("independent_three_state_policy_verified") is not True
        or report.get("new_native_job") is not False
        or report.get("new_NIH_checkpoint") is not False
        or report.get("real_historical_publication_authenticated") is not False):
        raise ValueError("continued original world evidence unsupported")
    receipt={
        "schema":"nih-p2-retained-original-w13-world-reentry/v1",
        "source_run":RUN,"source_artifact":ARTIFACT,"source_commit":SOURCE,
        "original_native_jobs":len(original_jobs),"source_journals_sha256":before,
        "journals_unchanged":True,"native_p2_benchmark_freshly_reverified":True,
        "original_game_played_again":True,"native_jobs_added":0,
        "world_actions":report["world_actions"],
        "browser_frames":len(report["observed_browser_frames"]),
        "original_python_calls":len(report["actual_original_python_calls"]),
        "actual_historical_version_fields_authenticated":False,
        "new_checkpoint_claimed":False,"official_NIH_submission":False,
        "retained_original_journal_republished":False,
    }
    (output/"retained-world-reentry-receipt.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    sys.path.insert(0,str(Path(os.environ["ORIGINAL_SOURCE_DIR"]).resolve()))
    main()
