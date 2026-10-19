"""Source-pinned GAME-WORKER-READY CP in the original nine-job workstation.

Readiness: separately reverify real W13, its independent native witness, and
the live game-to-temporal source; then validate the actual exact-ID controls
route (including a rejected wrong confirmation). A source-owned subprocess
constructs the receipt; the native host independently reconstructs it.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess,sys

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff,EvidenceRecord,ExecutionResult
from .workstation import ProcessWorkstation
from .game_w13_temporal_join import JOB as W13_JOB
from .game_native_verifier_bridge import JOB_ID as WITNESS_JOB
from .game_temporal_bridge import JOB_ID as LIVE_JOB

CP_ID="GAME-WORKER-READY"
WORKER_ROLE="game-adapter"
VERIFIER="cp-checker:GAME-WORKER-READY"
WORKER_ID="game-worker-ready"
VERSION="adapter-v1"
JOB_ID="game-worker-ready-joined-001"
SOURCE_FILE="ready_worker.py"
SOURCE_DIRECTORY=Path(__file__).resolve().parent/"game_worker_ready_source"
LOCATOR="repo:systems/workspace/game_worker_ready_source/ready_worker.py"
RELATION="verify original source-pinned game worker controls adapter readiness"
WITNESS="independent original source and exact native adapter permission checks"
SOURCE="game-adapter-source-owned-readiness/v1"
KIND="game-adapter-readiness-result/v1"

REQUIRED={
    W13_JOB:("game-worlds-w13","GAME-W13-WORLDS","cp-checker:GAME-W13-WORLDS"),
    WITNESS_JOB:("game-native-independent-verifier","GAME-NATIVE-VERIFIER",
                 "cp-checker:GAME-NATIVE-VERIFIER"),
    LIVE_JOB:("game-temporal-live-join","LIVE-GAME-TEMPORAL",
              "game-temporal-live-source-witness/v1"),
}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def digest(x):
    return sha256(canonical(x).encode()).hexdigest()

def copy_ready_source(data_dir,*,version_id,allow_copy=False):
    if not allow_copy:
        raise PermissionError("explicit readiness source copy required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,source_locator=LOCATOR)

def expected_receipt(inp):
    if type(inp) is not dict or set(inp)!={"kind","parents","adapter","synthetic"}:
        raise ValueError("readiness input envelope changed")
    if inp["kind"]!="game-adapter-readiness/v1" or inp["synthetic"] is not True:
        raise ValueError("readiness inputs outside scope")
    parents=inp["parents"]; a=inp["adapter"]
    if set(parents)!=set(REQUIRED):
        raise ValueError("readiness parent set differs")
    for j,(wid,cp,ver) in REQUIRED.items():
        p=parents[j]
        if (p["worker_id"]!=wid or p["contract"]!=cp or p["verifier"]!=ver
                or p["status"]!="COMPLETE"):
            raise ValueError("source-owned adapter parent contract lost")
    if a!={"route":"controls.run_job","w13_worker":"game-worlds-w13",
           "verifier_worker":"game-native-independent-verifier",
           "exact_confirmation":W13_JOB,"wrong_confirmation_rejected":True}:
        raise ValueError("original exact controls route changed")
    manifest={j:{k:parents[j][k] for k in (
        "worker_id","version_id","fingerprint","evidence_digest")}
        for j in REQUIRED}
    return {"kind":"game-adapter-ready-receipt/v1",
            "parent_manifest_digest":digest(manifest),
            "worker_count":3,
            "game_cp_contracts":["GAME-W13-WORLDS","GAME-NATIVE-VERIFIER"],
            "adapter_route":"controls.run_job",
            "wrong_confirmation_rejected":True,
            "live_temporal_parent_present":True,
            "game_worker_edition":parents[W13_JOB]["fingerprint"],
            "witness_edition":parents[WITNESS_JOB]["fingerprint"],
            "scope":"source-owned-synthetic-readiness-only"}

class GameReadyBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _original_parents(self):
        # These rechecks run through the *existing* native controls. No
        # separately invented verifier or synthetic CP claims.
        from .controls import reverify_job,run_job,prepare
        root=self.workstation.root.parent
        parents={}
        for job,(worker,contract,verifier) in REQUIRED.items():
            handoff=self.runtime.get(job)
            state=self.runtime.state(job)
            md=handoff.metadata
            if (state.status!="COMPLETE" or md.get("worker_id")!=worker
                    or md.get("source_system")!="process-workstation"
                    or md.get("native_evidence_verifier")!=verifier
                    or (job!=LIVE_JOB and md.get("checkpoint_contract")!=contract)):
                raise ValueError("native adapter parent identity or evidence is not authoritative")
            if reverify_job(data_dir=root,job_id=job)["status"]!="COMPLETE":
                raise ValueError("source-owned parent failed independent native replay")
            edition=self.workstation.inspect(worker_id=worker,version_id=md["worker_version"])
            if (edition["current_fingerprint"]!=md["edition_fingerprint"]
                    or edition["added"] or edition["deleted"] or edition["modified"]):
                raise ValueError("parent game source edition changed from admission")
            parents[job]={"worker_id":worker,"version_id":md["worker_version"],
                          "fingerprint":edition["current_fingerprint"],
                          "status":state.status,"verifier":verifier,"contract":contract,
                          "evidence_digest":digest(state.output)}
        # The wrong job confirmation must be *rejected*, with no journal append
        # and never any worker execution. This is a native negative, not a flag.
        before=(root/"runtime.jsonl").read_bytes()
        try:
            run_job(data_dir=root,job_id=W13_JOB,confirm_execute="not-"+W13_JOB)
        except PermissionError:
            rejected=True
        else:
            rejected=False
        if not rejected or before!=(root/"runtime.jsonl").read_bytes():
            raise ValueError("game native controls accepted a wrong source confirmation")
        # Positive read-only prepare proves the W13 source edition can be
        # selected in the same native route without permission to reexecute.
        input_file=Path(__file__).resolve().parents[2]/"network/tests/fixtures/game_w13_native_cp_example.json"
        prepare(data_dir=root,worker_id=REQUIRED[W13_JOB][0],
                version_id=parents[W13_JOB]["version_id"],inputs_file=input_file)
        return {"kind":"game-adapter-readiness/v1","synthetic":True,
                "parents":parents,"adapter":{"route":"controls.run_job",
                  "w13_worker":"game-worlds-w13",
                  "verifier_worker":"game-native-independent-verifier",
                  "exact_confirmation":W13_JOB,"wrong_confirmation_rejected":True}}

    def _pinned(self,handoff):
        md=handoff.metadata
        if (md.get("source_system")!="process-workstation"
                or md.get("worker_id")!=WORKER_ID
                or md.get("checkpoint_contract")!=CP_ID
                or md.get("native_evidence_verifier")!=VERIFIER):
            raise ValueError("not source-owned game worker readiness")
        folder,rec=self.workstation._read(WORKER_ID,md["worker_version"])
        now=self.workstation.inspect(worker_id=WORKER_ID,version_id=md["worker_version"])
        if (rec.get("source_locator")!=LOCATOR
                or now["current_fingerprint"]!=md["edition_fingerprint"]
                or set(self.workstation._inventory_edition(folder))!={SOURCE_FILE}):
            raise ValueError("game readiness source edition changed")
        if (handoff.dependencies!=(W13_JOB,WITNESS_JOB,LIVE_JOB)
                or handoff.inputs!=self._original_parents()
                or handoff.expected_output!={"kind":KIND,"official_NIH_test":False}):
            raise ValueError("readiness didn't preserve actual source-owned adapter ancestry")
        return folder

    def admit(self,*,version_id,inputs,from_actor,job_id=JOB_ID):
        if inputs!={"verify_game_adapter":True} or not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("exact game adapter readiness request needed")
        parent=self._original_parents()
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)["current_fingerprint"]
        handoff=Handoff(
            handoff_id=job_id,
            referent="GAME-WORKER-READY source-pinned original W13 native adapter",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,inputs=parent,
            expected_output={"kind":KIND,"official_NIH_test":False},
            dependencies=(W13_JOB,WITNESS_JOB,LIVE_JOB),
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            boundaries=("Original W13 and independent verifier must retain source identity.",
                        "Wrong native controls.run_job authorization must be rejected.",
                        "Ready is finite game adapter verification, not independent NIH-P2-TEST.",
                        "Copied worker is not an OS sandbox or an AI agent."),
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",
                        f"source-fingerprint:{fp}",
                        f"original-game:{W13_JOB}",f"game-witness:{WITNESS_JOB}",
                        f"live-prototype:{LIVE_JOB}"),
            metadata={"source_system":"process-workstation","worker_id":WORKER_ID,
                      "worker_version":version_id,"edition_fingerprint":fp,
                      "checkpoint_contract":CP_ID,"native_evidence_verifier":VERIFIER,
                      "title":"Source-pinned native game worker ready verification"},
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self,handoff,result):
        if handoff.handoff_id == "game-worker-ready-owner-001":
            from .owner_game_ready_bridge import OwnerGameReadyBridge
            return OwnerGameReadyBridge(runtime=self.runtime,workstation=self.workstation,
                register=False)._verify(handoff,result)
        self._pinned(handoff)
        fp=handoff.metadata["edition_fingerprint"]
        ev=(EvidenceRecord(condition=WITNESS,kind="computation",source=SOURCE,
                           ref=fp,depth="exact-controls-route-and-native-source-reverify"),)
        if result.status!="COMPLETE" or result.evidence!=ev:
            raise ValueError("game adapter result lacks real native witness")
        out=result.output
        keys={"kind","checkpoint_contract","checkpoint_verdict","checkpoint_worker_role",
              "native_verifier","report","worker_version","edition_fingerprint","pid"}
        if (type(out) is not dict or set(out)!=keys
                or out["kind"]!=KIND
                or (out["checkpoint_contract"],out["checkpoint_verdict"],
                    out["checkpoint_worker_role"],out["native_verifier"])!=(
                      CP_ID,"PASS",WORKER_ROLE,VERIFIER)
                or out["worker_version"]!=handoff.metadata["worker_version"]
                or out["edition_fingerprint"]!=fp
                or type(out["pid"]) is not int or out["pid"]<=0
                or out["report"]!=expected_receipt(handoff.inputs)):
            raise ValueError("game readiness result didn't pass independent host source reconstruction")

    def execute(self,job_id,*,allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("exact original game-ready native job confirmation required")
        if job_id == "game-worker-ready-owner-001":
            from .owner_game_ready_bridge import OwnerGameReadyBridge
            return OwnerGameReadyBridge(runtime=self.runtime,workstation=self.workstation,register=False).execute(
                job_id,allow_local_execution=True)
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,ReadyWorker(self,job_id))

    def reverify(self,job_id):
        if job_id == "game-worker-ready-owner-001":
            from .owner_game_ready_bridge import OwnerGameReadyBridge
            return OwnerGameReadyBridge(runtime=self.runtime,workstation=self.workstation,register=False).reverify(job_id)
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("game worker is not source-owned ready")
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True

@dataclass(frozen=True)
class ReadyWorker:
    bridge:GameReadyBridge
    job_id:str
    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor
    def can_execute(self,handoff):
        return (handoff.handoff_id==self.job_id
                and handoff.to_actor==self.actor_id and handoff.required_relation==RELATION)
    def execute(self,handoff):
        if not self.can_execute(handoff):
            raise ValueError("wrong source-owned game ready handoff")
        folder=self.bridge._pinned(handoff)
        try:
            p=subprocess.run([sys.executable,"-I",str(folder/SOURCE_FILE)],
                             input=json.dumps(handoff.inputs,sort_keys=True),
                             capture_output=True,text=True,cwd=folder,timeout=8,check=False)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("game adapter readiness worker timeout") from e
        if p.returncode or len(p.stdout)>8000 or len(p.stderr)>4096:
            raise ValueError("source-owned adapter worker failed")
        try:reported=json.loads(p.stdout)
        except ValueError as e:raise ValueError("adapter returned invalid JSON") from e
        if (type(reported) is not dict or set(reported)!={"receipt","pid"}
                or type(reported["pid"]) is not int or reported["pid"]<=0):
            raise ValueError("game adapter worker produced invalid process evidence")
        fp=handoff.metadata["edition_fingerprint"]
        return ExecutionResult(status="COMPLETE",
            output={"kind":KIND,"checkpoint_contract":CP_ID,
                    "checkpoint_verdict":"PASS","checkpoint_worker_role":WORKER_ROLE,
                    "native_verifier":VERIFIER,"report":reported["receipt"],
                    "worker_version":handoff.metadata["worker_version"],
                    "edition_fingerprint":fp,"pid":reported["pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                      source=SOURCE,ref=fp,depth="exact-controls-route-and-native-source-reverify"),))

