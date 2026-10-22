"""Native Studio component through ProcessWorkstation, HandoffRuntime and host replay.

Unlike a site view, this path actually copies executable source, admits a job,
runs a child process when allowed, and independently witnesses PCM before
recording a WorkspaceStore movement. No Suno account or hidden API is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff, SimulatedActor
from runtime.journal import RuntimeJournal

from .studio_native import (SOURCE_LOCATOR, VERIFIER, WITNESS, expected_result,
                            read_wav_session, validate_input, write_verified_wav)
from .store import WorkspaceStore
from .workstation import ProcessWorkstation

WORKER_ID="studio-render"
SOURCE_FILE="studio_worker.py"
SOURCE_DIRECTORY=Path(__file__).parent/"studio_worker_source"
RELATION="finite audio and MIDI timeline movement to independently witnessed stereo PCM"
LANE_ID="creative-studio-swallow"

def copy_studio_source(data_dir:str|Path,version:str,*,allow_copy:bool=False)->dict:
    if not allow_copy:
        raise PermissionError("explicit allow_copy required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version,source_locator=SOURCE_LOCATOR)

def _run_worker(edition:Path,request:dict)->dict:
    try:
        child=subprocess.run([sys.executable,"-I",str(edition/SOURCE_FILE)],cwd=edition,
                             input=json.dumps(request,separators=(",",":")),text=True,
                             capture_output=True,timeout=15,check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Studio worker timeout") from exc
    if child.returncode or len(child.stdout)>500000 or len(child.stderr)>4096:
        raise RuntimeError("Studio child failed or exceeded output budget")
    try:result=json.loads(child.stdout)
    except json.JSONDecodeError as exc:raise ValueError("worker did not produce JSON") from exc
    if type(result)!=dict or set(result)!={"result","pid"} or type(result["pid"])!=int or result["pid"]<=0:
        raise ValueError("worker output contract")
    return result

class StudioSwallowBridge:
    def __init__(self,data_dir:str|Path):
        self.data_dir=Path(data_dir)
        self.workstation=ProcessWorkstation(self.data_dir/"workstation")
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data_dir/"runtime.jsonl"))
        self.runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _pinned(self,job:Handoff)->Path:
        m=job.metadata
        if (m.get("source_system")!="process-workstation" or
            m.get("worker_id")!=WORKER_ID or
            m.get("native_evidence_verifier")!=VERIFIER or
            job.required_relation!=RELATION):
            raise ValueError("wrong workstation handoff")
        version=m.get("worker_version")
        folder,edition=self.workstation._read(WORKER_ID,version)
        current=self.workstation.inspect(worker_id=WORKER_ID,version_id=version)
        if (edition["source_locator"]!=SOURCE_LOCATOR or
                current["current_fingerprint"]!=m.get("edition_fingerprint") or
                SOURCE_FILE not in self.workstation._inventory_edition(folder)):
            raise ValueError("source edition changed after admission")
        return folder

    def admit(self,version:str,inputs:dict,*,from_actor:str,job_id:str|None=None)->Handoff:
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("caller required")
        canonical=validate_input(inputs)
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version)["current_fingerprint"]
        job=Handoff(
            handoff_id=job_id or "studio-"+uuid4().hex,
            referent="explicit selected audio/MIDI clips under a finite timeline",
            from_actor=from_actor,to_actor="studio-render:"+version,
            required_relation=RELATION,inputs=canonical,
            expected_output={"schema":"ab-studio-render-result/v1"},
            required_witnesses=(WITNESS,),
            admissible_evidence={WITNESS:("computation",)},
            boundaries=("Only declared finite input clips; no Suno accounts, AI generation or stem extraction.",
                        "Local child is trusted code, not an operating-system security sandbox.",
                        "PCM hashes establish content identity only, not ownership or copyright.",
                        "This is a finite render, not a complete live DAW."),
            provenance=("workspace-lane:"+LANE_ID,"worker-edition:"+WORKER_ID+":"+version,
                        "source-fingerprint:"+fp,*("pcm-source:"+s["sha256"] for s in canonical["sources"])),
            metadata={"title":"Studio component PCM render",
                      "source_system":"process-workstation","worker_id":WORKER_ID,
                      "worker_version":version,"edition_fingerprint":fp,
                      "native_evidence_verifier":VERIFIER})
        self._pinned(job)
        self.runtime.submit(job)
        return job

    def _verify(self,job:Handoff,returned:ExecutionResult)->None:
        self._pinned(job)
        if returned.status!="COMPLETE":raise ValueError("not a completed Studio render")
        fp=job.metadata["edition_fingerprint"]
        expected_evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                            source="independent host Studio PCM frame replay",
                            ref=fp,depth="independent-host-replay"),)
        if returned.evidence!=expected_evidence:
            raise ValueError("wrong Studio witness evidence")
        out=returned.output
        if (type(out)!=dict or set(out)!={"result","pid","worker_version","edition_fingerprint"} or
            type(out["pid"])!=int or out["pid"]<=0 or
            out["worker_version"]!=job.metadata["worker_version"] or
            out["edition_fingerprint"]!=fp or
            type(out["result"])!=dict or
            out["result"]!=expected_result(job.inputs)):
            raise ValueError("independent Studio PCM replay disagrees")

    def execute(self,job_id:str,*,allow_local_execution:bool=False):
        if not allow_local_execution:raise PermissionError("execution requires explicit approval")
        job=self.runtime.get(job_id)
        folder=self._pinned(job)
        def run(h:Handoff)->ExecutionResult:
            observed=_run_worker(folder,h.inputs)
            return ExecutionResult(status="COMPLETE",
                                   output={**observed,"worker_version":h.metadata["worker_version"],
                                           "edition_fingerprint":h.metadata["edition_fingerprint"]},
                                   evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                                       source="independent host Studio PCM frame replay",
                                       ref=h.metadata["edition_fingerprint"],
                                       depth="independent-host-replay"),))
        return self.runtime.run(job_id,SimulatedActor(actor_id=job.to_actor,capabilities=(RELATION,),handler=run))

    def reverify(self,job_id:str)->dict:
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":raise ValueError("Studio result incomplete")
        self._verify(self.runtime.get(job_id),ExecutionResult(status="COMPLETE",output=state.output,evidence=state.evidence))
        r=state.output["result"]
        return {"job_id":job_id,"reverified":True,"worker_version":state.output["worker_version"],
                "pcm_sha256":r["pcm_sha256"],"frames":r["frames"],"sample_rate":r["sample_rate"]}

    def record_movement(self,job_id:str)->dict:
        result=self.reverify(job_id)
        journal=WorkspaceStore(self.data_dir/"workspace.jsonl")
        try:lane=journal.get_lane(LANE_ID)
        except KeyError:
            lane=journal.open_lane(LANE_ID,label="Studio source swallow / finite native render",
                                   referent="source-owned composition-to-PCM relationship",
                                   actor_id="workstation-operator",
                                   sources=(SOURCE_LOCATOR,"work/projects/ab-studio-native/README.md"))
        if any("job:"+job_id in event["data"].get("evidence_refs",[]) for event in journal.history(LANE_ID)):
            return {**result,"movement_recorded":False,"return_event":lane.latest_event_id}
        next_lane=journal.record_movement(
            LANE_ID,
            changes="independently replayed stereo render of "+str(result["frames"])+" frames",
            preserved="source-pinned native worker and exact output PCM identity",
            next_movement="compare arrangement/mixer input against the retained PCM output before extending the component",
            evidence_refs=("job:"+job_id,"pcm-sha256:"+result["pcm_sha256"]))
        return {**result,"movement_recorded":True,"return_event":next_lane.latest_event_id}

    def export(self,job_id:str,path:str|Path)->dict:
        self.reverify(job_id)
        return write_verified_wav(path,self.runtime.state(job_id).output["result"])

def main():
    ap=argparse.ArgumentParser(description="Run native finite A/B Studio component in the source-pinned workstation")
    ap.add_argument("--manifest",required=True,help="User-selected ab-studio-wav-intake/v1 JSON")
    ap.add_argument("--data-dir",default="runtime/data")
    ap.add_argument("--version",default="studio-v1")
    ap.add_argument("--out",required=True)
    ap.add_argument("--copy-source",action="store_true")
    ap.add_argument("--execute",action="store_true")
    args=ap.parse_args()
    if not args.copy_source or not args.execute:
        ap.error("explicit --copy-source and --execute are both required")
    request=read_wav_session(args.manifest)
    source=copy_studio_source(args.data_dir,args.version,allow_copy=True)
    bridge=StudioSwallowBridge(args.data_dir)
    job=bridge.admit(args.version,request,from_actor="workstation-operator")
    state=bridge.execute(job.handoff_id,allow_local_execution=True)
    report=bridge.record_movement(job.handoff_id)
    exported=bridge.export(job.handoff_id,args.out)
    print(json.dumps({"edition":source["source_fingerprint"],"job":job.handoff_id,
                      "status":state.status,"witness":report,"export":exported},sort_keys=True))

if __name__=="__main__":main()
