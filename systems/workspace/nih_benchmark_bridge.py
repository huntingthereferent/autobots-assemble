"""Original workstation's bounded NIH-P2-BENCHMARK source owner and host WITNESS.

Synthetic data only. Uses real browser events as parent provenance, benchmarks
new known-time and valid-time boundary queries through the actual generated
temporal_query.py executable, and checks results against the original source
observation oracle. Neither an NIH result nor clinical validation.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date,timedelta
from hashlib import sha256
import json,subprocess,sys
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff,EvidenceRecord,ExecutionResult
from .workstation import ProcessWorkstation
from .nih_prototype_native import oracle
from .nih_game_test_bridge import JOB_ID as TEST_JOB, digest
from .nih_prototype_bridge import JOB_ID as PROTOTYPE_JOB

CP_ID="NIH-P2-BENCHMARK"
WORKER_ROLE="temporal-benchmark"
VERIFIER="cp-checker:NIH-P2-BENCHMARK"
WORKER_ID="nih-temporal-benchmark"
VERSION="temporal-benchmark-v1"
JOB_ID="nih-p2-benchmark-001"
SOURCE_FILE="benchmark_worker.py"
SOURCE_DIRECTORY=Path(__file__).resolve().parent/"nih_benchmark_worker_source"
LOCATOR="repo:systems/workspace/nih_benchmark_worker_source/benchmark_worker.py"
WITNESS="independent original temporal Python benchmark replay versus source observation oracle"
EVIDENCE_SOURCE="native-synthetic-temporal-static-benchmark/v1"
KIND="nih-synthetic-temporal-static-benchmark/v1"
PARENTS=(TEST_JOB,PROTOTYPE_JOB)
REQUEST={"kind":"native-synthetic-temporal-static-benchmark/v1","synthetic":True}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def copy_benchmark_source(data_dir,*,version_id,allow_copy=False):
    if not allow_copy:
        raise PermissionError("exact source-copy permission required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,
        source_locator=LOCATOR)

def validate_request(x):
    if type(x) is not dict or x!=REQUEST:
        raise ValueError("exact synthetic benchmark request required")
    return dict(x)

def _days(v):
    d=date.fromisoformat(v)
    if d.isoformat()!=v:
        raise ValueError("noncanonical source time")
    return {(d+timedelta(days=k)).isoformat() for k in (-1,0,1)}

def _select(pool,must):
    ordered=sorted(pool)
    if len(ordered)<=9:
        return ordered
    pinned=set(must)|{ordered[0],ordered[-1]}
    if len(pinned)>9:
        raise ValueError("benchmark source boundary grid exceeds pinned axes")
    for i in range(17):
        if len(pinned)>=9:
            break
        pinned.add(ordered[round(i*(len(ordered)-1)/16)])
    return sorted(pinned)

def _grid(observations,rows):
    first=rows[0]["request"];last=rows[-1]["request"]
    before=first["known_at"];after=last["known_at"];target=first["target_at"]
    if before>=after or target!=last["target_at"]:
        raise ValueError("actual source browser history lacks knowledge transition")
    known=set(_days(before)|_days(after))
    valid=set(_days(target))
    for o in observations:
        known|=_days(o["known_at"])
        valid|=_days(o["valid_from"])|_days(o["valid_to"])
    known_axis=_select(known,{before,after})
    target_axis=_select(valid,{target})
    queries=[{"known_at":k,"target_at":t} for k in known_axis for t in target_axis]
    if not 20<=len(queries)<=96:
        raise ValueError("insufficient independent source temporal boundary cases")
    return queries

class NIHBenchmarkBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parents(self):
        from .controls import reverify_job
        root=self.workstation.root.parent
        for job,worker,cp in ((TEST_JOB,"nih-temporal-game-test","NIH-P2-TEST"),
                              (PROTOTYPE_JOB,"nih-temporal-prototype","NIH-P2-PROTOTYPE")):
            h=self.runtime.get(job)
            if (h.metadata.get("worker_id")!=worker or
                h.metadata.get("checkpoint_contract")!=cp or
                h.metadata.get("source_system")!="process-workstation" or
                self.runtime.state(job).status!="COMPLETE" or
                reverify_job(data_dir=root,job_id=job)["status"]!="COMPLETE"):
                raise ValueError("original independently verified synthetic source parent changed")
        test=self.runtime.state(TEST_JOB).output["report"]
        rows=self.runtime.get(TEST_JOB).inputs["events"]
        if (test["query_history_sha256"]!=digest(rows) or
            test["query_count"]!=len(rows)):
            raise ValueError("actual source Chromium query history digest differs")
        prototype=self.runtime.state(PROTOTYPE_JOB).output["prototype"]
        inp=self.runtime.get(PROTOTYPE_JOB).inputs
        source=prototype["python_source"]
        dataset=prototype["dataset_json"]
        if (sha256(source.encode()).hexdigest()!=test["original_temporal_source_sha256"]
            or json.loads(dataset)["observations"]!=inp["scope"]["observations"]):
            raise ValueError("benchmark prototype not from original observed source")
        return test,rows,inp,source,dataset

    def _inputs(self,request):
        validate_request(request)
        test,rows,inp,source,dataset=self._parents()
        observations=inp["scope"]["observations"]
        return {"kind":REQUEST["kind"],"synthetic":True,
                "queries":_grid(observations,rows),
                "observations":observations,
                "prototype_sha256":sha256(source.encode()).hexdigest(),
                "query_history_sha256":test["query_history_sha256"]}

    def _pinned(self,h):
        md=h.metadata
        if (md.get("source_system")!="process-workstation" or
            md.get("worker_id")!=WORKER_ID or
            md.get("checkpoint_contract")!=CP_ID or
            md.get("native_evidence_verifier")!=VERIFIER):
            raise ValueError("wrong benchmark native identity")
        folder,rec=self.workstation._read(WORKER_ID,md["worker_version"])
        info=self.workstation.inspect(worker_id=WORKER_ID,version_id=md["worker_version"])
        if (rec.get("source_locator")!=LOCATOR or
            info["current_fingerprint"]!=md["edition_fingerprint"] or
            set(self.workstation._inventory_edition(folder))!={SOURCE_FILE}):
            raise ValueError("source-owned benchmark worker edition changed")
        if (h.inputs!=self._inputs(REQUEST) or h.dependencies!=PARENTS or
            h.expected_output!={"kind":KIND,"official_nih_submission":False}):
            raise ValueError("benchmark lost original source or history")
        return folder

    def admit(self,*,version_id,inputs,from_actor,job_id=JOB_ID):
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("benchmark requires original coordinator")
        expected=self._inputs(inputs)
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)["current_fingerprint"]
        h=Handoff(
            handoff_id=job_id,referent="NIH-P2-BENCHMARK original synthetic temporal versus static experiment",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{version_id}",
            required_relation="benchmark source-observed temporal and static future leakage",
            inputs=expected,expected_output={"kind":KIND,"official_nih_submission":False},
            dependencies=PARENTS,required_witnesses=(WITNESS,),
            admissible_evidence={WITNESS:("computation",)},
            boundaries=("No patient data or clinical correctness result.",
                        "Only exact browser-tested native prototype and native test parent.",
                        "Independent verifier must run original generated Python on each case.",
                        "Static comparison is a single synthetic-snapshot baseline, not a general KG benchmark.",
                        "No NIH award or submission. Bounded subprocess is not OS-sandboxed."),
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",f"source-fingerprint:{fp}",
                        f"native-game-test:{TEST_JOB}",f"native-prototype:{PROTOTYPE_JOB}"),
            metadata={"source_system":"process-workstation","worker_id":WORKER_ID,
                      "worker_version":version_id,"edition_fingerprint":fp,
                      "checkpoint_contract":CP_ID,"native_evidence_verifier":VERIFIER,
                      "title":"Source-owned synthetic temporal versus static benchmark"}
        )
        self._pinned(h)
        self.runtime.submit(h)
        return h

    def _verify(self,h,result):
        folder=self._pinned(h)
        fp=h.metadata["edition_fingerprint"]
        evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                    source=EVIDENCE_SOURCE,ref=fp,
                    depth="independent-original-Python-and-source-oracle-grid-replay"),)
        if result.status!="COMPLETE" or result.evidence!=evidence:
            raise ValueError("synthetic benchmark lacks native independently checked evidence")
        out=result.output
        if (type(out) is not dict or set(out)!={"kind","checkpoint_contract","checkpoint_verdict",
                "checkpoint_worker_role","native_verifier","report","worker_version",
                "edition_fingerprint","pid"} or
            (out["kind"],out["checkpoint_contract"],out["checkpoint_verdict"],
             out["checkpoint_worker_role"],out["native_verifier"])!=
            (KIND,CP_ID,"PASS",WORKER_ROLE,VERIFIER) or
            out["worker_version"]!=h.metadata["worker_version"] or
            out["edition_fingerprint"]!=fp or type(out["pid"]) is not int or out["pid"]<=0):
            raise ValueError("benchmark checkpoint output identity differs")
        test,rows,inp,code,dataset=self._parents()
        report=out["report"]
        queries=h.inputs["queries"]
        if (type(report) is not dict or set(report)!={"kind","query_history_sha256",
              "prototype_sha256","grid_sha256","query_count","static_future_leakage_cases",
              "static_future_leakage_ids_total","temporal_leakage_ids_total","cases",
              "synthetic_only","clinical_verdict","official_nih_submission"} or
            report["kind"]!="native-synthetic-temporal-static-benchmark-result/v1" or
            report["query_history_sha256"]!=test["query_history_sha256"] or
            report["prototype_sha256"]!=sha256(code.encode()).hexdigest() or
            report["grid_sha256"]!=sha256(canonical(queries).encode()).hexdigest() or
            report["query_count"]!=len(queries) or report["temporal_leakage_ids_total"]!=0 or
            report["synthetic_only"] is not True or
            report["clinical_verdict"]!="NOT_EVALUATED" or
            report["official_nih_submission"] is not False or
            type(report["cases"]) is not list or len(report["cases"])!=len(queries)):
            raise ValueError("benchmark claimed unsupported metrics")
        expected_cases=[]
        with TemporaryDirectory() as temp:
            work=Path(temp)
            script=work/"temporal_query.py";data=work/"temporal_dataset.json"
            script.write_text(code,encoding="utf8");data.write_text(dataset,encoding="utf8")
            for query in queries:
                native=oracle(inp["scope"],inp["reasoning_request"]["functional_predicates"],
                              known=query["known_at"],target=query["target_at"])
                returned=subprocess.run([sys.executable,"-I",str(script),str(data)],
                    input=json.dumps(query),capture_output=True,text=True,cwd=work,timeout=5)
                if returned.returncode or len(returned.stdout)>16000 or json.loads(returned.stdout)!=native:
                    raise ValueError("actual generated native Python diverged from source observation oracle")
                expected_cases.append({"request":query,"temporal_ids":native["temporal_ids"],
                    "static_snapshot_ids":native["static_snapshot_ids"],
                    "future_leakage_ids":native["future_leakage_ids"]})
            for invalid in ({"known_at":"2026-99-99","target_at":queries[0]["target_at"]},
                            {"known_at":queries[0]["known_at"]},
                            {"known_at":queries[0]["known_at"],"target_at":queries[0]["target_at"],"extra":True}):
                p=subprocess.run([sys.executable,"-I",str(script),str(data)],
                    input=json.dumps(invalid),capture_output=True,text=True,cwd=work,timeout=5)
                if p.returncode==0:
                    raise ValueError("native Python improperly accepted invalid benchmark request")
        if report["cases"]!=expected_cases:
            raise ValueError("source-owned benchmark cases contradicted native oracle")
        leak=sum(bool(x["future_leakage_ids"]) for x in expected_cases)
        total=sum(len(x["future_leakage_ids"]) for x in expected_cases)
        if (not 0<leak<len(queries) or
            report["static_future_leakage_cases"]!=leak or
            report["static_future_leakage_ids_total"]!=total):
            raise ValueError("benchmark comparison cannot be independently reproduced")

    def execute(self,job_id,*,allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("exact native benchmark authorization required")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,BenchmarkWorker(self,job_id))

    def reverify(self,job_id):
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("source-owned benchmark not COMPLETE")
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True

@dataclass(frozen=True)
class BenchmarkWorker:
    bridge:NIHBenchmarkBridge
    job_id:str
    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor
    def can_execute(self,h):
        return (h.handoff_id==self.job_id and h.to_actor==self.actor_id
                and h.required_relation=="benchmark source-observed temporal and static future leakage")
    def execute(self,h):
        if not self.can_execute(h):
            raise ValueError("benchmark addressed to another native worker")
        folder=self.bridge._pinned(h)
        try:
            result=subprocess.run([sys.executable,"-I",str(folder/SOURCE_FILE)],
                input=json.dumps(h.inputs,sort_keys=True),text=True,capture_output=True,
                cwd=folder,timeout=15,check=False)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("bounded benchmark worker timed out") from e
        if result.returncode or len(result.stdout)>60000 or len(result.stderr)>4096:
            raise ValueError("source-owned benchmark subprocess failed")
        value=json.loads(result.stdout)
        if type(value) is not dict or set(value)!={"pid","report"} or type(value["pid"]) is not int:
            raise ValueError("source-owned benchmark receipt invalid")
        fp=h.metadata["edition_fingerprint"]
        return ExecutionResult(status="COMPLETE",
            output={"kind":KIND,"checkpoint_contract":CP_ID,"checkpoint_verdict":"PASS",
                    "checkpoint_worker_role":WORKER_ROLE,"native_verifier":VERIFIER,
                    "report":value["report"],"worker_version":h.metadata["worker_version"],
                    "edition_fingerprint":fp,"pid":value["pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                      source=EVIDENCE_SOURCE,ref=fp,
                      depth="independent-original-Python-and-source-oracle-grid-replay"),))
