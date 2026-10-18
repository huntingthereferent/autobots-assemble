"""Real source-owned GAME-NATIVE-VERIFIER worker in ORIGINAL ProcessWorkstation.

Consumes exact W13 CP parent and independently replays game rules inside a
separately copied witness subprocess. Host also re-runs original W12 verifier.
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
from .game_w13_native_bridge import GameW13NativeBridge,WORKER_ID as W13_WORKER
from .game_w13_native import (CP_ID as W13_CP,VERIFIER as W13_VERIFIER,
                              verify_native_report)
from .game_w13_temporal_join import JOB as W13_JOB

CP_ID="GAME-NATIVE-VERIFIER"
WORKER_ROLE="game-witness"
VERIFIER="cp-checker:GAME-NATIVE-VERIFIER"
WORKER_ID="game-native-independent-verifier"
VERSION="witness-v1"
SOURCE_FILE="native_verifier.py"
SOURCE_DIRECTORY=Path(__file__).resolve().parent/"game_native_verifier_worker_source"
LOCATOR="repo:systems/workspace/game_native_verifier_worker_source/native_verifier.py"
RELATION="independently verify the exact source-owned W13 receipt with cross-world negatives"
WITNESS="host original W12 replay and independent copied game witness agree"
SOURCE="game-native-independent-two-world-witness/v1"
RESULT_KIND="game-native-verifier-result/v1"
JOB_ID="game-native-verifier-joined-001"
# A second, independently authorized path to the existing genuine owner W13 journal.
OWNER_W13_JOB="game-w13-github-001"
OWNER_VERSION="witness-owner-v1"
OWNER_JOB_ID="game-native-verifier-github-001"
PARENTS=(W13_JOB,OWNER_W13_JOB)

def copy_verifier_source(data_dir,*,version_id,allow_copy=False):
    if not allow_copy:
        raise PermissionError("exact source copy confirmation required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,
        version_id=version_id,source_locator=LOCATOR)

def _digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

class NativeGameVerifierBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        self.parent_bridge=GameW13NativeBridge(runtime=runtime,workstation=workstation)
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parent_inputs(self,parent_job_id=W13_JOB):
        if parent_job_id not in PARENTS:
            raise ValueError("unknown original W13 parent identity")
        original=self.runtime.get(parent_job_id)
        metadata=original.metadata
        if (metadata.get("worker_id")!=W13_WORKER
                or metadata.get("checkpoint_contract")!=W13_CP
                or metadata.get("native_evidence_verifier")!=W13_VERIFIER
                or self.runtime.state(parent_job_id).status!="COMPLETE"):
            raise ValueError("original W13 native game CP must be complete")
        self.parent_bridge.reverify(parent_job_id)
        original_result=self.runtime.state(parent_job_id).output["report"]
        verify_native_report(original.inputs,original_result)
        return {"request":original.inputs,"receipt":original_result["receipt"],
                "parent_job_id":parent_job_id}

    def _pinned(self,handoff):
        md=handoff.metadata
        if (md.get("worker_id")!=WORKER_ID
                or md.get("source_system")!="process-workstation"
                or md.get("checkpoint_contract")!=CP_ID
                or md.get("native_evidence_verifier")!=VERIFIER):
            raise ValueError("not independently admitted GAME-NATIVE-VERIFIER")
        edition,record=self.workstation._read(WORKER_ID,md["worker_version"])
        observed=self.workstation.inspect(worker_id=WORKER_ID,version_id=md["worker_version"])
        if (record["source_locator"]!=LOCATOR
                or observed["current_fingerprint"]!=md["edition_fingerprint"]
                or set(self.workstation._inventory_edition(edition))!={SOURCE_FILE}):
            raise ValueError("source-owned W13 verifier edition lost its integrity")
        parent_id=handoff.dependencies[0] if len(handoff.dependencies)==1 else None
        if parent_id not in PARENTS:
            raise ValueError("W13 verifier has no admitted exact parent")
        if parent_id==OWNER_W13_JOB and (
                md["worker_version"]!=OWNER_VERSION
                or handoff.handoff_id!=OWNER_JOB_ID):
            raise ValueError("owner W13 source can only use its separate exact edition/job")
        if (handoff.inputs!=self._parent_inputs(parent_id)
                or handoff.dependencies!=(parent_id,)
                or handoff.expected_output!={"kind":RESULT_KIND,
                                             "independent_native_game_replay":True}):
            raise ValueError("W13 parent witness ancestry or output contract altered")
        return edition

    def admit(self,*,version_id,inputs,from_actor,job_id=JOB_ID):
        if type(inputs) is not dict or set(inputs)!={"w13_job_id"} or inputs["w13_job_id"] not in PARENTS:
            raise ValueError("only exact source-owned W13 parent may be witnessed")
        parent_id=inputs["w13_job_id"]
        if parent_id==OWNER_W13_JOB and (version_id!=OWNER_VERSION or job_id!=OWNER_JOB_ID):
            raise ValueError("owner W13 requires separate source-pinned native worker edition and job")
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("native witness requires explicit coordinator actor")
        payload=self._parent_inputs(parent_id)
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)["current_fingerprint"]
        handoff=Handoff(
            handoff_id=job_id,referent="GAME-NATIVE-VERIFIER independently replays original W13",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,inputs=payload,
            expected_output={"kind":RESULT_KIND,"independent_native_game_replay":True},
            dependencies=(parent_id,),
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            boundaries=("Only exact admitted W13 source-owned native result.",
                        "Independent witness source must replay both worlds and reject early advance.",
                        "Host separately checks byte-pinned original W12 oracle.",
                        "Does not confer GAME-WORKER-READY or NIH-P2-TEST by itself.",
                        "Copied native worker has no OS-level sandbox guarantee."),
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",
                        f"source-fingerprint:{fp}",f"parent-game:{parent_id}"),
            metadata={"source_system":"process-workstation",
                      "worker_id":WORKER_ID,"worker_version":version_id,
                      "edition_fingerprint":fp,"checkpoint_contract":CP_ID,
                      "native_evidence_verifier":VERIFIER,
                      "title":"Independent bounded original W13 game verification"},
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self,handoff,result):
        folder=self._pinned(handoff)
        fp=handoff.metadata["edition_fingerprint"]
        evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                  source=SOURCE,ref=fp,depth="two-independent-replays-and-native-negative"),)
        if result.status!="COMPLETE" or result.evidence!=evidence:
            raise ValueError("native game WITNESS has no verified evidence")
        out=result.output
        expected={"kind","checkpoint_contract","checkpoint_verdict",
                  "checkpoint_worker_role","native_verifier","report",
                  "worker_version","edition_fingerprint","pid"}
        if (type(out) is not dict or set(out)!=expected
                or out["kind"]!=RESULT_KIND
                or (out["checkpoint_contract"],out["checkpoint_verdict"],
                    out["checkpoint_worker_role"],out["native_verifier"])!=(
                    CP_ID,"PASS",WORKER_ROLE,VERIFIER)
                or out["worker_version"]!=handoff.metadata["worker_version"]
                or out["edition_fingerprint"]!=fp
                or type(out["pid"]) is not int or out["pid"]<=0):
            raise ValueError("GAME-NATIVE-VERIFIER output contract mutated")
        parent=self._parent_inputs(handoff.dependencies[0])
        result_w12=verify_native_report(parent["request"],
                                        {"receipt":parent["receipt"],"pid":1})
        rr=out["report"]
        if (type(rr) is not dict
                or set(rr)!={"kind","worlds_completed","cross_world_boundaries",
                              "per_world_turns","negative_early_advance_rejected",
                              "receipt_sha256","w12_sha256"}
                or rr["kind"]!="w13-independent-native-game-verdict/v1"
                or rr["worlds_completed"]!=result_w12["worlds_completed"]
                or rr["cross_world_boundaries"]!=1
                or rr["per_world_turns"]!=[2,2]
                or rr["negative_early_advance_rejected"] is not True
                or rr["receipt_sha256"]!=_digest(parent["receipt"])
                or rr["w12_sha256"]!=parent["request"]["w12_sha256"]):
            raise ValueError("independent game native witness contradicts original W12")

    def execute(self,job_id,*,allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("exact native source witness run must be authorized")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,GameNativeVerifierWorker(self,job_id))

    def reverify(self,job_id):
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("game independent witness worker has not completed")
        self._verify(self.runtime.get(job_id),
                     ExecutionResult(status="COMPLETE",
                                     output=state.output,evidence=state.evidence))
        return True

@dataclass(frozen=True)
class GameNativeVerifierWorker:
    bridge:NativeGameVerifierBridge
    job_id:str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self,handoff):
        return (handoff.handoff_id==self.job_id and
                handoff.to_actor==self.actor_id and
                handoff.required_relation==RELATION)

    def execute(self,handoff):
        if not self.can_execute(handoff):
            raise ValueError("independent witness has wrong actor identity")
        edition=self.bridge._pinned(handoff)
        try:
            p=subprocess.run([sys.executable,"-I",str(edition/SOURCE_FILE)],
                             input=json.dumps(handoff.inputs,sort_keys=True),
                             text=True,capture_output=True,cwd=edition,
                             timeout=8,check=False)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("copied independent witness exceeded bound") from e
        if p.returncode or len(p.stdout)>8000 or len(p.stderr)>4096:
            raise ValueError("independent source game WITNESS execution failed")
        try:report=json.loads(p.stdout)
        except ValueError as e:raise ValueError("game witness returned malformed JSON") from e
        if (type(report) is not dict or set(report)!={"result","pid"} or
                type(report["pid"]) is not int or report["pid"]<=0):
            raise ValueError("witness wasn't a real bounded subprocess")
        fp=handoff.metadata["edition_fingerprint"]
        return ExecutionResult(
            status="COMPLETE",
            output={"kind":RESULT_KIND,"checkpoint_contract":CP_ID,
                    "checkpoint_verdict":"PASS","checkpoint_worker_role":WORKER_ROLE,
                    "native_verifier":VERIFIER,"report":report["result"],
                    "worker_version":handoff.metadata["worker_version"],
                    "edition_fingerprint":fp,"pid":report["pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                      source=SOURCE,ref=fp,
                      depth="two-independent-replays-and-native-negative"),),
        )
