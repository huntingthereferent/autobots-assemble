"""A/B: run actual pinned REA source mutations through the existing workstation.

This is NOT an imitation REA parser or a generic command wrapper: each stage
calls its already-tested repo-native ProcessWorkstation source experiment on
real upstream TypeScript, then executes actual native REA tests and typecheck.

Limited initial operation: JavaScript application matching / observation /
choice / constructed input / restartable checkpoint. No claim to cover every
REA analyzer, and no claim that test parity proves an A/B theorem.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PIN = "f0b9ef34c404c1c65f8167502db972b0bd708403"
STAGES = (
    ("observation", "observation_source_experiment.py"),
    ("choice", "choice_source_experiment.py"),
    ("construct", "construct_source_experiment.py"),
    ("advance", "advance_source_experiment.py"),
    ("checkpoint", "checkpoint_source_experiment.py"),
)
NATIVE_TESTS = (
    "src/domain/javascript/javascriptObservationRefinement.ab-swallow.test.ts",
    "src/domain/javascript/javascriptObservationChoice.ab-swallow.test.ts",
    "src/domain/javascript/javascriptConstructObservation.ab-swallow.test.ts",
    "src/domain/javascript/javascriptInvestigationAdvance.ab-swallow.test.ts",
    "src/domain/javascript/javascriptCheckpoint.ab-swallow.test.ts",
    "src/domain/javascript/javascriptApplicationVersionMatching.test.ts",
    "src/domain/javascript/javascriptApplicationVersionComparison.test.ts",
    "src/domain/javascript/javascriptApplicationVersionRelationshipUncertainty.test.ts",
)
CONTRACT_COPIES = (
    ("observation_refinement_contract.test.ts", "src/domain/javascript/javascriptObservationRefinement.ab-swallow.test.ts"),
    ("choice_contract.test.ts", "src/domain/javascript/javascriptObservationChoice.ab-swallow.test.ts"),
    ("construct_contract.test.ts", "src/domain/javascript/javascriptConstructObservation.ab-swallow.test.ts"),
    ("advance_contract.test.ts", "src/domain/javascript/javascriptInvestigationAdvance.ab-swallow.test.ts"),
    ("checkpoint_cli.ts", "src/domain/javascript/javascriptCheckpointCLI.ab-swallow.ts"),
    ("checkpoint_contract.test.ts", "src/domain/javascript/javascriptCheckpoint.ab-swallow.test.ts"),
)
MAX_OUTPUT = 16_000_000

class ABEvidenceError(RuntimeError):
    pass

def digest(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def _check_repo(repo:Path, rea:Path, out:Path)->None:
    if not repo.is_dir() or not rea.is_dir():
        raise ABEvidenceError("existing repository and actual pinned REA checkout required")
    if not (repo/"systems/workspace/workstation.py").is_file():
        raise ABEvidenceError("the real ProcessWorkstation implementation is missing")
    if not (repo/"experiments/rea-swallow/upstream").is_dir():
        raise ABEvidenceError("source repo lacks pinned upstream REA gitlink")
    if rea.resolve()!= (repo/"experiments/rea-swallow/upstream").resolve():
        raise ABEvidenceError("only the declared pinned REA submodule may be transformed")
    if not (rea/"LICENSE").is_file() or "MIT License" not in (rea/"LICENSE").read_text():
        raise ABEvidenceError("source MIT license is missing; cannot erase REA's original copyright")
    actual=subprocess.run(["git","-C",str(rea),"rev-parse","HEAD"],capture_output=True,text=True,check=True).stdout.strip()
    if actual!=PIN:
        raise ABEvidenceError("wrong REA source revision: "+actual)
    dirty=subprocess.run(["git","-C",str(rea),"status","--porcelain"],capture_output=True,text=True,check=True)
    if dirty.stdout.strip():
        raise ABEvidenceError("REA checkout is not clean; refuse to rewrite an existing source edition")
    if out.resolve().is_relative_to(rea.resolve()):
        raise ABEvidenceError("evidence output must remain outside pinned REA source")
    if (repo/"runtime/data").resolve() not in out.resolve().parents:
        raise ABEvidenceError("evidence output must remain within ignored runtime/data")

def _run(command:list[str], *, cwd:Path, logfile:Path, timeout:int=600,
         env:dict[str,str]|None=None)->dict:
    try:
        execution=subprocess.run(command,cwd=str(cwd),env=env,stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,text=True,timeout=timeout,
                                 encoding="utf-8",errors="replace",check=False)
        output=execution.stdout or ""
        code=execution.returncode
        timed_out=False
    except subprocess.TimeoutExpired as e:
        output=(e.stdout or b"").decode("utf-8","replace") if isinstance(e.stdout,bytes) else (e.stdout or "")
        code=124
        timed_out=True
    if len(output)>MAX_OUTPUT:
        output=output[:MAX_OUTPUT]+"\n[TRUNCATED]\n"
    logfile.parent.mkdir(parents=True,exist_ok=True)
    logfile.write_text(output,encoding="utf-8")
    return {"argv":command,"returncode":code,"timed_out":timed_out,
            "log":str(logfile.name),"sha256":digest(logfile)}

def _unique_output(out:Path):
    if out.exists():
        raise ABEvidenceError("an existing evidence directory cannot be replaced")
    out.mkdir(parents=True)

def _doc(rea:Path, stages:list[dict], upstream_sha:str, *, status:str)->dict:
    src=rea/"src/domain/javascript"
    items=[]
    for filename in ("javascriptApplicationVersionKeys.ts","javascriptInvestigationCheckpoint.ts"):
        p=src/filename
        if p.is_file():
            items.append({"source_path":"src/domain/javascript/"+filename,
                          "sha256":digest(p),"bytes":p.stat().st_size})
    return {"schema_version":1,"kind":"ab-tool/real-rea-source-edition-v1",
            "upstream":"morluto/rea","upstream_commit":upstream_sha,
            "third_party_license":"MIT (morluto); upstream copyright preserved",
            "scope":"native REA JavaScript source relationship investigation",
            "stages":stages,"changed_source_files":items,"result":status,
            "not_proven":"general JavaScript equivalence, general A/B mathematics, all REA providers",
            "original_source_was_edited_in_ephemeral_checkout":True}

def _graph(receipt:dict)->dict:
    """Create original schema-native provenance from actual subprocess receipts."""
    source="REA@"+PIN
    prev=source
    links=[]
    for i,row in enumerate(receipt["stages"]):
        dest="A/B source stage "+str(i+1)+": "+row["name"]
        evidence=["local-log://"+row[k]["log"] for k in ("prepare", "apply", "native", "typecheck")
                  if isinstance(row.get(k), dict) and row[k].get("log")]
        links.append({
          "schema_version":1,
          "provenance_id":"ab-source-"+str(i+1)+"-"+row["name"],
          "from":{"layer":"source-version" if i==0 else "workstation-edition","ref":prev},
          "relation":"source_edition_"+row["name"],
          "to":{"layer":"workstation-edition","ref":dest},
          "evidence_refs":evidence,
          "survived":["original source commit "+PIN,
                      "original REA MIT license"],
          "invalidated":["source stage failed or was interrupted"] if row["result"]=="FAIL" else [],
          "boundaries":["Local subprocess result and source hashes, NOT independent universal semantics.",
                        "Per-stage source preparation is not individually native-tested by this run."
                        if row["result"]!="PASS" else "Native REA tests and typecheck executed."],
          "transformation":"Original REA TypeScript source staged through ProcessWorkstation",
          "observed_at":row["timestamp"]
        })
        prev=dest
    return {"schema_version":1,"provenance_links":links,"traces":[]}

def run(repo:Path,rea:Path,out:Path)->int:
    _check_repo(repo,rea,out)
    _unique_output(out)
    stages=[]
    receipt=_doc(rea,stages,PIN,status="PENDING")
    env=dict(os.environ)
    env["PYTHONPATH"]=str(repo)+ (os.pathsep+env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    try:
        for name,file in STAGES:
            script=repo/"experiments/rea-swallow"/file
            if not script.is_file():
                raise ABEvidenceError("missing actual source edition script: "+file)
            stage={"name":name,"timestamp":datetime.now(timezone.utc).isoformat(),
                   "result":"PENDING"}
            stages.append(stage)
            for action in ("prepare","apply"):
                stage[action]=_run([sys.executable,str(script),action,"--rea",str(rea)],
                                   cwd=repo,logfile=out/(name+"-"+action+".log"),
                                   env=env,timeout=180)
                if stage[action]["returncode"]!=0:
                    stage["result"]="FAIL"
                    raise ABEvidenceError("source stage "+name+" "+action+" failed")
            stage["result"]="PREPARED"
        for source,target in CONTRACT_COPIES:
            original=repo/"experiments/rea-swallow"/source
            destination=rea/target
            if destination.exists() or not original.is_file():
                raise ABEvidenceError("native contract source absent or target already exists: "+target)
            shutil.copyfile(original,destination)
        stage=stages[-1]
        native_cmd=["npx","--no-install","vitest","run",*NATIVE_TESTS]
        stage["native"]=_run(native_cmd,cwd=rea,logfile=out/"native-rea-tests.log",timeout=900)
        if stage["native"]["returncode"]!=0:
            stage["result"]="FAIL"
            raise ABEvidenceError("actual REA native tests failed")
        stage["typecheck"]=_run(["npx","--no-install","tsc","--noEmit","-p","tsconfig.json"],
                                cwd=rea,logfile=out/"rea-typecheck.log",timeout=600)
        if stage["typecheck"]["returncode"]!=0:
            stage["result"]="FAIL"
            raise ABEvidenceError("actual REA source typecheck failed")
        source_diff=_run(["git","-C",str(rea),"diff","--check"],
                          cwd=repo,logfile=out/"source-diff-check.log")
        if source_diff["returncode"]!=0:
            stage["result"]="FAIL"
            raise ABEvidenceError("actual REA source diff has errors")
        stage["source_diff_check"]=source_diff
        stage["result"]="PASS"
        receipt=_doc(rea,stages,PIN,status="PASS")
        return 0
    except (ABEvidenceError,OSError,subprocess.SubprocessError) as err:
        receipt=_doc(rea,stages,PIN,status="FAILED")
        receipt["error"]=str(err)
        return 2
    finally:
        (out/"source-absorption-receipt.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        (out/"source-provenance.json").write_text(
            json.dumps(_graph(receipt),indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"result":receipt["result"],"stage_count":len(stages),
                          "upstream_commit":PIN,"receipt":str(out/"source-absorption-receipt.json")},
                         sort_keys=True))

def main(argv:list[str]|None=None)->int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:2] == ["swallow", "repo"]:
        argv.pop(1)
    if argv and argv[0] == "ship":
        from .ship_cli import main as ship_main
        return ship_main(argv[1:])
    if argv and argv[0] in ("inspect", "ancestors", "render"):
        from .cli import main as provenance
        return provenance(argv)
    parser=argparse.ArgumentParser(prog="ab",description="A/B real-source transformation tool")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("ship",help="Package source-verified A/B wheel, docs, and original evidence")
    sub.add_parser("source",help="Show actual pinned REA source and supported A/B stages")
    p=sub.add_parser("swallow",help="Rebuild and test actual REA source editions (mutates declared checkout)")
    p.add_argument("--repo-root",type=Path,default=Path.cwd())
    p.add_argument("--rea",type=Path,default=None)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--allow-source-edit",action="store_true",
                   help="Explicitly allow modifications to the declared pinned working checkout")
    a=parser.parse_args(argv)
    if a.command=="source":
        print(json.dumps({"upstream":"morluto/rea","pin":PIN,
              "actual_source_editions":[x[0] for x in STAGES],
              "witness_boundary":"Native REA Vitest and TypeScript checks; no general proof",
              "original_LICENSE":"REA MIT notice must be kept in the source distribution"},
              indent=2))
        return 0
    if not a.allow_source_edit:
        parser.error("swallow edits real REA source; supply --allow-source-edit explicitly")
    repo=a.repo_root.resolve()
    rea=(a.rea or (repo/"experiments/rea-swallow/upstream")).resolve()
    try:
        return run(repo,rea,a.out.resolve())
    except (ABEvidenceError, OSError, subprocess.CalledProcessError) as err:
        print("ab: "+str(err),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
