"""Original SP80 level4 middle versus lower L finite source geometry admitted to workstation (opt-in)."""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, ExecutionResult, EvidenceRecord, SimulatedActor
from runtime.journal import RuntimeJournal
from systems.workspace import ProcessWorkstation, WorkspaceStore
from .arc4_l_junction_height_gate import context, inspect as verify_result

SOURCE = Path("work/arc3/native_sp80_stage4_l_junction_height.py")
LANE = "arc4-sp80-l-junction-height-native"
JOB = "arc4-sp80-l-junction-height-20261025"
RELATION = "test genuine lower L UP1/HOLD/DOWN1 at native x20 to x14 lower branch fork under both baseline and compensated four-cup arrangements"
VERIFIER = "arc4-L-junction-native-source-verifier-v1"

def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()

def execute(data_dir: Path, out: Path):
    contract = context()
    if not SOURCE.is_file():
        raise ValueError("original ARC source absent")
    data_dir.mkdir(parents=True, exist_ok=True)
    staged = data_dir / "selected"
    staged.mkdir(exist_ok=True)
    selected = staged / SOURCE.name
    if not selected.exists():
        shutil.copyfile(SOURCE, selected)
    if sha(selected) != sha(SOURCE):
        raise ValueError("staged native source differs from checkout")
    desk = ProcessWorkstation(data_dir / "workstation")
    version = "frozen-" + sha(SOURCE)[:16]
    try:
        edition = desk.inspect(worker_id="arc4-original-sdk", version_id=version)
    except KeyError:
        desk.copy_source(staged, worker_id="arc4-original-sdk", version_id=version,
                         source_locator=str(SOURCE)+"@"+os.getenv("GITHUB_SHA","unversioned"))
        edition = desk.inspect(worker_id="arc4-original-sdk", version_id=version)
    fingerprint = edition["baseline_fingerprint"]
    native_file = Path(edition["path"]) / SOURCE.name
    if edition["current_fingerprint"] != fingerprint or sha(native_file) != sha(SOURCE):
        raise ValueError("native workstation edition drift")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
    handoff = Handoff(
        handoff_id=JOB, referent=contract["referent"],
        from_actor="workstation", to_actor="arc4-original-sdk", required_relation=RELATION,
        inputs={"source_sha256":sha(SOURCE),"frozen_controls":contract["factors"],
                "resets":contract["expected_genuine_sdk_resets"]},
        expected_output={"original_sdk": "official status, frames and comparison"},
        required_witnesses=("pinned source", "SDK frame record", "native return audit"),
        admissible_evidence={"pinned source":("source",),
                             "SDK frame record":("native_sdk",),
                             "native return audit":("derived",)},
        boundaries=tuple(contract["walls"]),
        provenance=("workspace-lane:"+LANE,str(SOURCE),
                    "work/arc3/arc4_l_junction_height_contract.json","source-run:40172934437"),
        metadata={"source_system":"process-workstation","workstation_worker":True,
                  "worker_id":"arc4-original-sdk","worker_version":version,
                  "edition_fingerprint":fingerprint,
                  "native_evidence_verifier":VERIFIER,
                  "title":"ARC4 original SDK finite lower junction L vertical"},
    )
    if JOB not in runtime.snapshot():
        runtime.submit(handoff)
    elif runtime.get(JOB) != handoff:
        raise ValueError("existing workstation handoff changed")

    def verify(h, result):
        if h != handoff or result.status != "PARTIAL":
            raise ValueError("ARC4 handoff witness drift")
        checked = verify_result(contract, out)
        if (result.output["official_progress"] != checked["official_sdk_level5_or_WIN"]
                or result.output["json_sha256"] != sha(out)
                or result.output["npz_sha256"] != sha(out.with_suffix(".npz"))
                or desk.inspect(worker_id="arc4-original-sdk",
                                version_id=version)["current_fingerprint"] != fingerprint):
            raise ValueError("native result or source edition changed")
    runtime.register_evidence_verifier(VERIFIER, verify)

    def native(h):
        if h != handoff:
            raise ValueError("incorrect native ARC work")
        spec = importlib.util.spec_from_file_location(
            "work.arc3.native_sp80_stage4_l_junction_height", native_file)
        if spec is None or spec.loader is None:
            raise ValueError("native edition loader missing")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        old = sys.argv
        try:
            sys.argv = [str(native_file),"--out",str(out)]
            module.main()
        finally:
            sys.argv = old
        result = verify_result(contract,out)
        return ExecutionResult(status="PARTIAL", output={
            "official_progress":result["official_sdk_level5_or_WIN"],
            "resets":result["real_sdk_resets"],
            "json_sha256":sha(out),"npz_sha256":sha(out.with_suffix(".npz")),
            "offcup_events":result["finite_native_L_junction_relations"],
            "next_movement":result["next_movement"]},
            evidence=(
                EvidenceRecord("pinned source","source","workstation-edition",sha(native_file)),
                EvidenceRecord("SDK frame record","native_sdk","original-arc-sdk",str(out.with_suffix(".npz"))),
                EvidenceRecord("native return audit","derived","arc4-drift-gate",sha(out)),
            ),
            note="The trial executed; no complete game claim.")
    if runtime.state(JOB).status == "READY":
        state = runtime.run(JOB,SimulatedActor("arc4-original-sdk",(RELATION,),native))
    elif runtime.state(JOB).status == "PARTIAL":
        state = runtime.state(JOB)
        verify(handoff,ExecutionResult(status="PARTIAL",output=state.output,evidence=state.evidence))
    else:
        raise ValueError("workstation native job is not READY/PARTIAL")

    ws = WorkspaceStore(data_dir/"workspace.jsonl")
    if LANE not in {lane.lane_id for lane in ws.lanes()}:
        ws.open_lane(LANE,label="ARC4 original native SDK",
                     referent=contract["referent"],actor_id="james",
                     sources=(str(SOURCE),"work/arc3/arc4_l_junction_height_contract.json"))
    evidence="native-json-sha256:"+state.output["json_sha256"]
    if not any(evidence in e.get("data",{}).get("evidence_refs",())
               for e in ws.history(LANE)):
        ws.record_movement(LANE,
            changes="Native workstation edition executed "+str(state.output["resets"])
                    +" original SDK resets; "+str(state.output["official_progress"])
                    +" official level5/WIN.",
            preserved="Earlier ARC stages and independent finite mathematics remain distinct.",
            next_movement=state.output["next_movement"],walls=tuple(contract["walls"]),
            evidence_refs=(evidence,"native-npz-sha256:"+state.output["npz_sha256"],
                           "source-edition:"+fingerprint,"handoff:"+JOB,
                           "github-run:"+os.getenv("GITHUB_RUN_ID","local")))
    return {"job":JOB,"state":state.status,
            "native_resets":state.output["resets"],
            "official_level5_or_WIN":state.output["official_progress"],
            "source_fingerprint":fingerprint,
            "json_sha256":state.output["json_sha256"],
            "npz_sha256":state.output["npz_sha256"],
            "workstation_journal":str(data_dir/"runtime.jsonl"),
            "workspace_lane":LANE}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--execute",action="store_true")
    p.add_argument("--data-dir",type=Path,default=Path("runtime/data/arc4/l-junction/workstation"))
    p.add_argument("--out",type=Path,default=Path("runtime/data/arc4/l-junction/original-l-junction.json"))
    args=p.parse_args()
    if not args.execute:
        p.error("explicit --execute required")
    record=execute(args.data_dir,args.out)
    (args.data_dir/"arc4-workstation-return.json").write_text(json.dumps(record,indent=2)+"\n")
    print("WORKSTATION_ARC4_L_JUNCTION_RETURN "+json.dumps(record,sort_keys=True),flush=True)
if __name__=="__main__":
    main()
