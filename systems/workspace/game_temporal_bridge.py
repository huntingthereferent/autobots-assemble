"""Bounded source-owned live game/temporal BUILD; original workstation journal."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess, sys

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, EvidenceRecord, ExecutionResult
from .workstation import ProcessWorkstation
from .game_build_bridge import GameBuildBridge, WORKER_ID as GAME_ID
from .nih_prototype_bridge import NIHPrototypeBridge, WORKER_ID as PROTO_ID

WORKER_ID="game-temporal-live-join"
SOURCE_FILE="live_join_worker.py"
SOURCE_DIRECTORY=Path(__file__).resolve().parent/"game_temporal_worker_source"
LOCATOR="repo:systems/workspace/game_temporal_worker_source/live_join_worker.py"
RELATION="BUILD live playable game that calls original source-owned temporal prototype"
WITNESS="independent host verified original game and executable temporal sources in produced live join"
EVIDENCE_SOURCE="native-source-owned-game-temporal-relation/v1"
VERIFIER="game-temporal-live-source-witness/v1"
VERSION="game-temporal-live-bundle/v1"
JOB_ID="live-game-temporal-001"

def copy_join_source(data_dir,*,version_id,allow_copy=False):
    if not allow_copy:
        raise PermissionError("explicit native source copy required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,source_locator=LOCATOR)

def validate_request(req):
    if type(req) is not dict or set(req)!={
        "kind","synthetic","cutover_turn","known_at_before","known_at_after","target_at"}:
        raise ValueError("exact live join request needed")
    if req["kind"]!="synthetic-live-game-temporal-join/v1" or req["synthetic"] is not True:
        raise ValueError("only original synthetic game-time experiment")
    from datetime import date
    for key in ("known_at_before","known_at_after","target_at"):
        v=req[key]
        if type(v) is not str or len(v)!=10 or date.fromisoformat(v).isoformat()!=v:
            raise ValueError("invalid source time cutoffs")
    if req["known_at_before"]>=req["known_at_after"]:
        raise ValueError("time must advance in the bounded game")
    if type(req["cutover_turn"]) is not int or not 1<=req["cutover_turn"]<=20:
        raise ValueError("cutover turn invalid")
    return dict(req)

def _sha(s):
    return sha256(s.encode("utf8")).hexdigest()

class LiveJoinBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        self.game=GameBuildBridge(runtime=runtime,workstation=workstation)
        self.proto=NIHPrototypeBridge(runtime=runtime,workstation=workstation)
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _inputs(self,request):
        req=validate_request(request)
        game=self.runtime.get("build-game-room-v1")
        proto=self.runtime.get("nih-prototype-001")
        if (game.metadata.get("worker_id")!=GAME_ID or
                proto.metadata.get("worker_id")!=PROTO_ID or
                self.runtime.state(game.handoff_id).status!="COMPLETE" or
                self.runtime.state(proto.handoff_id).status!="COMPLETE"):
            raise ValueError("original playable BUILD and temporal prototype required")
        self.game.reverify(game.handoff_id)
        self.proto.reverify(proto.handoff_id)
        built=self.runtime.state(game.handoff_id).output["build"]
        program=self.runtime.state(proto.handoff_id).output["prototype"]
        return {"request":req,"world":game.inputs,
                "game_html":built["html"],
                "game_html_sha256":_sha(built["html"]),
                "plan":built["plan"],
                "temporal_source":program["python_source"],
                "temporal_dataset":program["dataset_json"],
                "prototype_source_sha256":_sha(program["python_source"])}

    def _pinned(self,handoff):
        md=handoff.metadata
        if (md.get("source_system")!="process-workstation"
                or md.get("worker_id")!=WORKER_ID
                or md.get("native_evidence_verifier")!=VERIFIER):
            raise ValueError("not source-owned live temporal game")
        edition,record=self.workstation._read(WORKER_ID,md["worker_version"])
        current=self.workstation.inspect(worker_id=WORKER_ID,version_id=md["worker_version"])
        if (record["source_locator"]!=LOCATOR
                or current["current_fingerprint"]!=md["edition_fingerprint"]
                or set(self.workstation._inventory_edition(edition))!={SOURCE_FILE}):
            raise ValueError("source worker edition not intact")
        if (handoff.inputs!=self._inputs(handoff.inputs["request"])
                or handoff.dependencies!=("build-game-room-v1","nih-prototype-001")
                or handoff.expected_output!={"kind":VERSION,"formal_cp":"NOT_CLAIMED"}):
            raise ValueError("game and temporal sources changed")
        return edition

    def admit(self,*,version_id,inputs,from_actor,job_id=JOB_ID):
        payload=self._inputs(inputs)
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)["current_fingerprint"]
        handoff=Handoff(
            handoff_id=job_id,
            referent="live game actions call source-owned bitemporal query program",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,inputs=payload,
            expected_output={"kind":VERSION,"formal_cp":"NOT_CLAIMED"},
            dependencies=("build-game-room-v1","nih-prototype-001"),
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            boundaries=(
                "BUILD is a bounded source subprocess, not an AI autonomous agent.",
                "No NIH Phase 2 test CP before GAME-WORKER-READY is independently witnessed.",
                "Synthetic temporal evidence only; no clinical or official NIH claims.",
                "Local HTTP server restricted to loopback; native workers not OS-sandboxed.",
                "Browser WITNESS must execute separately on actual generated program.",
            ),
            provenance=(f"source-edition:{WORKER_ID}:{version_id}",
                        "parent:build-game-room-v1","parent:nih-prototype-001"),
            metadata={"source_system":"process-workstation","worker_id":WORKER_ID,
                      "worker_version":version_id,"edition_fingerprint":fp,
                      "native_evidence_verifier":VERIFIER,
                      "title":"Live game temporal experimentation BUILD"},
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self,handoff,result):
        self._pinned(handoff)
        fp=handoff.metadata["edition_fingerprint"]
        expect=(EvidenceRecord(condition=WITNESS,kind="computation",
                source=EVIDENCE_SOURCE,ref=fp,depth="fresh-original-source-content-comparison"),)
        if result.status!="COMPLETE" or result.evidence!=expect:
            raise ValueError("live join lacks original native witness")
        out=result.output
        if type(out) is not dict or set(out)!={"kind","formal_cp","bundle","worker_version","edition_fingerprint","pid"}:
            raise ValueError("native join response shape changed")
        if (out["kind"]!=VERSION or out["formal_cp"]!="NOT_CLAIMED"
                or out["worker_version"]!=handoff.metadata["worker_version"]
                or out["edition_fingerprint"]!=fp
                or type(out["pid"]) is not int or out["pid"]<=0):
            raise ValueError("native live join response authority changed")
        b=out["bundle"]; source=handoff.inputs
        if type(b) is not dict or set(b)!={
            "kind","html","server_source","temporal_source","temporal_dataset",
            "config","source_game_sha256","source_temporal_sha256"}:
            raise ValueError("native live game bundle incomplete")
        if b["kind"]!=VERSION or b["source_game_sha256"]!=source["game_html_sha256"] or b["source_temporal_sha256"]!=source["prototype_source_sha256"]:
            raise ValueError("original input source hash mismatch")
        if b["temporal_source"]!=source["temporal_source"] or b["temporal_dataset"]!=source["temporal_dataset"]:
            raise ValueError("live join replaced genuine native query program or dataset")
        if b["config"]!={**source["request"],"kind":source["request"]["kind"]}:
            expected={k:v for k,v in source["request"].items() if k!="kind"}
            if b["config"]!=expected:
                raise ValueError("source times changed during live join")
        original=source["game_html"]
        if (type(b["html"]) is not str or not b["html"].startswith(original.split("</body>")[0])
                or b["html"].count("</body>")!=1
                or 'id="native-temporal-client"' not in b["html"]):
            raise ValueError("live game no longer contains exact original playable room")
        if (type(b["server_source"]) is not str or
                not 2000<len(b["server_source"])<15000
                or 'ThreadingHTTPServer(("127.0.0.1",port),Handler)' not in b["server_source"]
                or 'sys.executable,"-I",str(source),str(dataset)' not in b["server_source"]):
            raise ValueError("local server must query the real prototype on loopback")

    def execute(self,job_id,*,allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("exact local workstation execution must be authorized")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,LiveJoinWorker(self,job_id))

    def reverify(self,job_id):
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("new live join not completed")
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True

@dataclass(frozen=True)
class LiveJoinWorker:
    bridge:LiveJoinBridge
    job_id:str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self,handoff):
        return handoff.handoff_id==self.job_id and handoff.to_actor==self.actor_id and handoff.required_relation==RELATION

    def execute(self,handoff):
        if not self.can_execute(handoff):
            raise ValueError("native source not admitted to exact build")
        folder=self.bridge._pinned(handoff)
        try:
            p=subprocess.run([sys.executable,"-I",str(folder/SOURCE_FILE)],
                             input=json.dumps(handoff.inputs,sort_keys=True),
                             text=True,capture_output=True,cwd=folder,timeout=10,check=False)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("bounded game temporal BUILD timed out") from e
        if p.returncode!=0 or len(p.stdout)>80000 or len(p.stderr)>4096:
            raise ValueError("bounded game temporal BUILD failed")
        try: obj=json.loads(p.stdout)
        except ValueError as e: raise ValueError("builder didn't return JSON") from e
        if type(obj) is not dict or set(obj)!={"bundle","pid"}:
            raise ValueError("missing bounded worker output")
        fp=handoff.metadata["edition_fingerprint"]
        return ExecutionResult(
            status="COMPLETE",
            output={"kind":VERSION,"formal_cp":"NOT_CLAIMED","bundle":obj["bundle"],
                    "worker_version":handoff.metadata["worker_version"],
                    "edition_fingerprint":fp,"pid":obj["pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                      source=EVIDENCE_SOURCE,ref=fp,depth="fresh-original-source-content-comparison"),),
        )
