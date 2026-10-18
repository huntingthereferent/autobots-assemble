"""NIH-P2-TEST: source-owned browser-to-actual-Python game test in one workstation.

Consumes original live Chromium result event, original actual browser query
records, and completed Phase 1 packet, Phase 2 prototype and game-ready CP.
Host independently replays the emitted temporal_query.py on each recorded
request PLUS negative and alternative-time inputs before admitting PASS.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess,sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff,EvidenceRecord,ExecutionResult
from .workstation import ProcessWorkstation
from .game_temporal_browser import EVENT as BROWSER_EVENT
from .game_temporal_bridge import JOB_ID as LIVE_JOB
from .game_worker_ready_bridge import JOB_ID as READY_JOB
from .nih_prototype_bridge import WORKER_ID as PROTO_WORKER

CP_ID="NIH-P2-TEST"
WORKER_ROLE="temporal-test"
VERIFIER="cp-checker:NIH-P2-TEST"
WORKER_ID="nih-temporal-game-test"
VERSION="temporal-test-v1"
JOB_ID="nih-p2-game-test-001"
SOURCE_FILE="test_worker.py"
SOURCE_DIRECTORY=Path(__file__).resolve().parent/"nih_game_test_source"
LOCATOR="repo:systems/workspace/nih_game_test_source/test_worker.py"
RELATION="test real temporal Python results through actual playable game browser"
WITNESS="original live Chromium result and independent actual native Python query replay"
EVIDENCE_SOURCE="native-game-backed-temporal-queries-replayed/v1"
KIND="nih-synthetic-p2-game-test/v1"
PARENTS=("nih-packet-001","nih-prototype-001",READY_JOB,LIVE_JOB)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def digest(x):
    return sha256(canonical(x).encode()).hexdigest()

def copy_test_source(data_dir,*,version_id,allow_copy=False):
    if not allow_copy:
        raise PermissionError("exact source-copy permission required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,
        source_locator=LOCATOR)

def validate_request(request):
    if type(request) is not dict or set(request)!={"kind","synthetic"}:
        raise ValueError("exact synthetic P2 test request required")
    if request["kind"]!="native-game-backed-temporal-test/v1" or request["synthetic"] is not True:
        raise ValueError("only source-owned local synthetic temporal tests")
    return dict(request)

class NIHGameTestBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parents(self):
        from .controls import reverify_job
        root=self.workstation.root.parent
        req={
            "nih-packet-001":("nih-phase1-packet","NIH-P1-PACKET"),
            "nih-prototype-001":(PROTO_WORKER,"NIH-P2-PROTOTYPE"),
            READY_JOB:("game-worker-ready","GAME-WORKER-READY"),
            LIVE_JOB:("game-temporal-live-join",None),
        }
        for job,(worker,contract) in req.items():
            handoff=self.runtime.get(job)
            if (handoff.metadata.get("worker_id")!=worker or
                    handoff.metadata.get("source_system")!="process-workstation" or
                    (contract is not None and handoff.metadata.get("checkpoint_contract")!=contract) or
                    self.runtime.state(job).status!="COMPLETE" or
                    reverify_job(data_dir=root,job_id=job)["status"]!="COMPLETE"):
                raise ValueError("original source-owned game or temporal parent changed")
        events=[x for x in self.runtime.event_store.for_handoff(LIVE_JOB)
                if x.event_type==BROWSER_EVENT]
        if len(events)!=1 or events[0].actor_id!="independent-live-chromium-witness":
            raise ValueError("actual original game browser WITNESS not returned to journal")
        proof=events[0].data
        live=self.runtime.state(LIVE_JOB).output["bundle"]
        code=self.runtime.state("nih-prototype-001").output["prototype"]["python_source"]
        dataset=self.runtime.state("nih-prototype-001").output["prototype"]["dataset_json"]
        config=live["config"]
        game=self.runtime.state("build-game-room-v1").output["build"]
        source_sha=sha256(code.encode()).hexdigest()
        if (proof.get("job_id")!=LIVE_JOB or
                proof.get("kind")!="game-temporal-live-browser-witness/v1" or
                proof.get("game_solved") is not True or
                proof.get("temporal_cli_sha256")!=source_sha or
                proof.get("game_actions")!=len(game["plan"]) or
                proof.get("future_became_knowable_after_turn")!=config["cutover_turn"] or
                live["temporal_source"]!=code or live["temporal_dataset"]!=dataset):
            raise ValueError("independent original browser and original temporal source mismatch")
        return proof,config,code,dataset

    def _inputs(self,request,rows):
        req=validate_request(request)
        proof,config,code,_=self._parents()
        if type(rows) is not list or not 4<=len(rows)<=60:
            raise ValueError("actual browser event log is missing")
        return {
            "kind":req["kind"],"synthetic":True,"parent_jobs":list(PARENTS),
            "browser":proof,"events":rows,
            "cutover_turn":config["cutover_turn"],
            "target_at":config["target_at"],
            "known_at_before":config["known_at_before"],
            "known_at_after":config["known_at_after"],
            "prototype_sha256":sha256(code.encode()).hexdigest(),
        }

    def _pinned(self,handoff):
        meta=handoff.metadata
        if (meta.get("source_system")!="process-workstation"
                or meta.get("worker_id")!=WORKER_ID
                or meta.get("checkpoint_contract")!=CP_ID
                or meta.get("native_evidence_verifier")!=VERIFIER):
            raise ValueError("not original Phase 2 source-owned temporal game test")
        folder,rec=self.workstation._read(WORKER_ID,meta["worker_version"])
        current=self.workstation.inspect(worker_id=WORKER_ID,version_id=meta["worker_version"])
        if (rec.get("source_locator")!=LOCATOR or
                current["current_fingerprint"]!=meta["edition_fingerprint"] or
                set(self.workstation._inventory_edition(folder))!={SOURCE_FILE}):
            raise ValueError("Phase 2 test source edition no longer pinned")
        inp=handoff.inputs
        req={"kind":inp["kind"],"synthetic":inp["synthetic"]}
        if (inp!=self._inputs(req,inp["events"]) or
                handoff.dependencies!=PARENTS or
                handoff.expected_output!={"kind":KIND,"official_nih_submission":False}):
            raise ValueError("Phase 2 test lost browser or source-owned ancestry")
        return folder

    def admit(self,*,version_id,inputs,from_actor,job_id=JOB_ID):
        if type(inputs) is not dict or set(inputs)!={"request","events"}:
            raise ValueError("actual source-owned browser query history must be supplied")
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("explicit temporal test coordinator needed")
        data=self._inputs(inputs["request"],inputs["events"])
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)["current_fingerprint"]
        handoff=Handoff(
            handoff_id=job_id,referent="NIH-P2-TEST synthetic point-in-time query via game",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,inputs=data,
            expected_output={"kind":KIND,"official_nih_submission":False},
            dependencies=PARENTS,
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            boundaries=("Must consume actual native Chromium game-to-Python log, not invented events.",
                        "Host replays each query against emitted original temporal Python source.",
                        "Synthetic game-backed test only; no NIH submission or clinical validation.",
                        "No general benchmark; separate NIH-P2-BENCHMARK remains uncompleted.",
                        "Source-owned bounded subprocess not OS-sandboxed."),
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",f"source-fingerprint:{fp}",
                        f"original-live-browser:{LIVE_JOB}",
                        f"source-game-adapter:{READY_JOB}"),
            metadata={"source_system":"process-workstation","worker_id":WORKER_ID,
                      "worker_version":version_id,"edition_fingerprint":fp,
                      "checkpoint_contract":CP_ID,"native_evidence_verifier":VERIFIER,
                      "title":"Actual game-backed synthetic temporal Phase 2 test"},
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self,handoff,result):
        self._pinned(handoff)
        fp=handoff.metadata["edition_fingerprint"]
        expected_ev=(EvidenceRecord(condition=WITNESS,kind="computation",
                     source=EVIDENCE_SOURCE,ref=fp,
                     depth="actual-original-Python-replay-and-browser-evidence"),)
        if result.status!="COMPLETE" or result.evidence!=expected_ev:
            raise ValueError("Phase2 game-backed test does not have independent native evidence")
        out=result.output
        keys={"kind","checkpoint_contract","checkpoint_verdict","checkpoint_worker_role",
              "native_verifier","report","worker_version","edition_fingerprint","pid"}
        if (type(out) is not dict or set(out)!=keys or out["kind"]!=KIND
                or (out["checkpoint_contract"],out["checkpoint_verdict"],
                    out["checkpoint_worker_role"],out["native_verifier"])!=(
                    CP_ID,"PASS",WORKER_ROLE,VERIFIER)
                or out["worker_version"]!=handoff.metadata["worker_version"] or
                out["edition_fingerprint"]!=fp or type(out["pid"]) is not int or out["pid"]<=0):
            raise ValueError("source-owned Phase2 test verdict contract differs")
        proof,config,code,dataset=self._parents()
        rows=handoff.inputs["events"]
        report=out["report"]
        if (type(report) is not dict or set(report)!={
            "kind","query_history_sha256","query_count","before_cutover_queries",
            "after_cutover_queries","cutover_turn","original_temporal_source_sha256",
            "actual_browser_source","static_snapshot_leakage_detected",
            "independent_python_replay_required","verified_synthetic_timing_only",
            "clinical_verdict","official_nih_submission"}
                or report["kind"]!="native-temporal-game-test-result/v1"
                or report["query_history_sha256"]!=digest(rows)
                or report["query_count"]!=len(rows)
                or report["before_cutover_queries"]!=sum(r["turn"]<config["cutover_turn"] for r in rows)
                or report["after_cutover_queries"]!=sum(r["turn"]>=config["cutover_turn"] for r in rows)
                or report["before_cutover_queries"]<1 or report["after_cutover_queries"]<1
                or report["cutover_turn"]!=config["cutover_turn"]
                or report["original_temporal_source_sha256"]!=sha256(code.encode()).hexdigest()
                or report["actual_browser_source"]!=BROWSER_EVENT
                or report["static_snapshot_leakage_detected"] is not True
                or report["independent_python_replay_required"] is not True
                or report["verified_synthetic_timing_only"] is not True
                or report["clinical_verdict"]!="NOT_EVALUATED"
                or report["official_nih_submission"] is not False):
            raise ValueError("game test worker claims not reproducible from original history")
        # Original source-owned Python program, not a JavaScript or in-memory
        # reimplementation of the query result, independently runs every
        # browser input and two new validity-side cutoffs.
        with TemporaryDirectory() as folder:
            path=Path(folder)
            script=path/"temporal_query.py"
            datafile=path/"temporal_dataset.json"
            script.write_text(code,encoding="utf8")
            datafile.write_text(dataset,encoding="utf8")
            def run(req,valid=True):
                r=subprocess.run([sys.executable,"-I",str(script),str(datafile)],
                    input=json.dumps(req),capture_output=True,text=True,cwd=path,
                    timeout=5,check=False)
                if (r.returncode==0)!=valid or len(r.stdout)>16000:
                    raise ValueError("actual original temporal Python failed source replay")
                return json.loads(r.stdout) if valid else None
            for row in rows:
                output=run(row["request"])
                observed=dict(row["result"])
                if observed.pop("prototype_sha256",None)!=sha256(code.encode()).hexdigest():
                    raise ValueError("actual browser origin Python digest changed")
                if output!=observed:
                    raise ValueError("browser game result contradicted actual source-owned Python")
            from datetime import date,timedelta
            target=date.fromisoformat(config["target_at"])
            for offset in (-1,+1):
                query={"known_at":config["known_at_after"],
                       "target_at":(target+timedelta(days=offset)).isoformat()}
                result2=run(query)
                if result2["known_at"]!=config["known_at_after"] or result2["target_at"]!=query["target_at"]:
                    raise ValueError("new native time query wasn't evaluated")
            run({"known_at":"2026-99-99","target_at":config["target_at"]},valid=False)
        if not any("delayed-result" in r["result"]["future_leakage_ids"]
                   for r in rows if r["turn"]<config["cutover_turn"]):
            raise ValueError("no withheld future case was tested before game turn")
        if not any("delayed-result" in r["result"]["temporal_ids"]
                   for r in rows if r["turn"]>=config["cutover_turn"]):
            raise ValueError("no returned evidence after actual game turn")

    def execute(self,job_id,*,allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("exact native Phase2 test authorization required")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,GameTestWorker(self,job_id))

    def reverify(self,job_id):
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("actual Phase2 temporal game test not completed")
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True

@dataclass(frozen=True)
class GameTestWorker:
    bridge:NIHGameTestBridge
    job_id:str
    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor
    def can_execute(self,handoff):
        return (handoff.handoff_id==self.job_id and handoff.to_actor==self.actor_id
                and handoff.required_relation==RELATION)
    def execute(self,handoff):
        if not self.can_execute(handoff):
            raise ValueError("native temporal game test not addressed to bounded worker")
        folder=self.bridge._pinned(handoff)
        try:
            p=subprocess.run([sys.executable,"-I",str(folder/SOURCE_FILE)],
                input=json.dumps(handoff.inputs,sort_keys=True),text=True,
                capture_output=True,cwd=folder,timeout=12,check=False)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("bounded Phase2 native game test timed out") from e
        if p.returncode or len(p.stdout)>8000 or len(p.stderr)>4096:
            raise ValueError("bounded native game temporal test failed")
        try:report=json.loads(p.stdout)
        except ValueError as e:raise ValueError("game temporal test reported malformed JSON") from e
        if (type(report) is not dict or set(report)!={"report","pid"}
                or type(report["pid"]) is not int or report["pid"]<=0):
            raise ValueError("game test source subprocess receipt invalid")
        fp=handoff.metadata["edition_fingerprint"]
        return ExecutionResult(status="COMPLETE",
            output={"kind":KIND,"checkpoint_contract":CP_ID,
                    "checkpoint_verdict":"PASS","checkpoint_worker_role":WORKER_ROLE,
                    "native_verifier":VERIFIER,"report":report["report"],
                    "worker_version":handoff.metadata["worker_version"],
                    "edition_fingerprint":fp,"pid":report["pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                      source=EVIDENCE_SOURCE,ref=fp,
                      depth="actual-original-Python-replay-and-browser-evidence"),))
