"""Actual finite Studio source-copy -> HandoffRuntime -> host replay tests."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import json
import math
import struct
import subprocess
import sys
import unittest
import wave

from runtime.handoff import ExecutionResult
from systems.workspace.studio_native import (expected_result, pcm_hash,
                                             read_wav_session, validate_input)
from systems.workspace.studio_bridge import (StudioSwallowBridge, WORKER_ID,
                                            copy_studio_source)
from systems.workspace import WorkspaceStore, ProcessWorkstation


def example():
    pcm=[int(11000*math.sin(2*math.pi*i/52)) for i in range(2048)]
    audio={"kind":"audio","id":"opening","source":"a","start":0,"length":960,
           "offset":0,"rate_num":1,"rate_den":1}
    midi={"kind":"midi","id":"notes","start":0,"length":960,"notes":[
        {"pitch":60,"start":0,"length":480,"velocity":80},
        {"pitch":64,"start":240,"length":480,"velocity":70}]}
    track1={"id":"audio-track","gain":850,"pan":-200,"mute":False,"solo":False,
            "automation":[{"tick":480,"gain":300},{"tick":960,"gain":850}],"clips":[audio]}
    track2={"id":"midi-track","gain":500,"pan":200,"mute":False,"solo":False,
            "automation":[],"clips":[midi]}
    return {"schema":"ab-studio-render/v1","sample_rate":8000,"bpm":120,
            "duration_ticks":960,"sources":[{"id":"a","sha256":pcm_hash(pcm),"pcm":pcm}],
            "tracks":[track1,track2]}

def make_wav(path,pcm):
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000)
        w.writeframes(struct.pack("<"+"h"*len(pcm),*pcm))


class StudioNativeTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.data=self.root/"runtime-data"

    def native(self):
        copy_studio_source(self.data,"v1",allow_copy=True)
        return StudioSwallowBridge(self.data)

    def test_copy_and_execute_are_explicit_and_separate(self):
        with self.assertRaises(PermissionError):
            copy_studio_source(self.data,"v1")
        bridge=self.native()
        request=example()
        handoff=bridge.admit("v1",request,from_actor="owner")
        self.assertEqual(bridge.runtime.state(handoff.handoff_id).status,"READY")
        with self.assertRaises(PermissionError):
            bridge.execute(handoff.handoff_id)
        self.assertEqual(bridge.runtime.state(handoff.handoff_id).status,"READY")
        with self.assertRaises(FileExistsError):
            copy_studio_source(self.data,"v1",allow_copy=True)

    def test_actual_child_and_replay_and_return_and_wav(self):
        bridge=self.native()
        request=example()
        task=bridge.admit("v1",request,from_actor="owner")
        state=bridge.execute(task.handoff_id,allow_local_execution=True)
        self.assertEqual(state.status,"COMPLETE")
        self.assertEqual(state.output["result"],expected_result(request))
        self.assertNotEqual(state.output["pid"],0)
        witness=bridge.reverify(task.handoff_id)
        self.assertEqual(witness["frames"],4000)
        recorded=bridge.record_movement(task.handoff_id)
        self.assertTrue(recorded["movement_recorded"])
        self.assertFalse(bridge.record_movement(task.handoff_id)["movement_recorded"])
        path=self.root/"mix.wav"
        output=bridge.export(task.handoff_id,path)
        with wave.open(str(path),"rb") as sound:
            self.assertEqual(sound.getnchannels(),2)
            self.assertEqual(sound.getsampwidth(),2)
            self.assertEqual(sound.getnframes(),4000)
            self.assertEqual(sound.getframerate(),8000)
            self.assertEqual(sound.readframes(4000)[:4],
                             struct.pack("<hh",state.output["result"]["left"][0],state.output["result"]["right"][0]))
        self.assertEqual(output["pcm_sha256"],witness["pcm_sha256"])
        second=StudioSwallowBridge(self.data)
        self.assertTrue(second.reverify(task.handoff_id)["reverified"])
        journal=WorkspaceStore(self.data/"workspace.jsonl")
        self.assertEqual(journal.get_lane("creative-studio-swallow").movements,1)

    def test_source_edit_and_output_forgery_are_rejected(self):
        bridge=self.native()
        job=bridge.admit("v1",example(),from_actor="owner")
        bridge.execute(job.handoff_id,allow_local_execution=True)
        original=bridge.runtime.state(job.handoff_id)
        out=deepcopy(original.output)
        out["result"]["left"][10]+=1
        with self.assertRaises(ValueError):
            bridge._verify(job,ExecutionResult(status="COMPLETE",output=out,evidence=original.evidence))
        child=self.data/"workstation"/WORKER_ID/"v1"/"studio_worker.py"
        child.write_text(child.read_text()+"\n# changed after pinned admission\n",encoding="utf8")
        with self.assertRaises(ValueError):
            bridge.reverify(job.handoff_id)
        with self.assertRaises(ValueError):
            bridge.export(job.handoff_id,self.root/"bad.wav")

    def test_mutation_and_bounds_fail_closed(self):
        source=example()
        cases=[]
        c=deepcopy(source);c["bpm"]=0;cases.append(c)
        c=deepcopy(source);c["duration_ticks"]=7680;cases.append(c)
        c=deepcopy(source);c["tracks"][0]["pan"]=1001;cases.append(c)
        c=deepcopy(source);c["tracks"][0]["automation"][1]["tick"]=480;cases.append(c)
        c=deepcopy(source);c["tracks"][1]["clips"][0]["notes"][0]["velocity"]=0;cases.append(c)
        c=deepcopy(source);c["sources"][0]["pcm"][0]=999999;cases.append(c)
        c=deepcopy(source);c["sources"][0]["sha256"]="a"*64;cases.append(c)
        c=deepcopy(source);c["tracks"][0]["clips"][0]["source"]="missing";cases.append(c)
        c=deepcopy(source);c["tracks"]+=deepcopy(source["tracks"]);cases.append(c)
        c=deepcopy(source);c["tracks"][1]["clips"][0]["notes"][0]["length"]=10000;cases.append(c)
        c=deepcopy(source);c["tracks"][1]["clips"][0]["notes"][0]["pitch"]=500;cases.append(c)
        for i,candidate in enumerate(cases):
            with self.subTest(i=i),self.assertRaises(ValueError):
                validate_input(candidate)

    def test_gating_muted_solo_and_pan(self):
        request=example()
        ordinary=expected_result(request)
        self.assertNotEqual(ordinary["pcm_sha256"],"0"*64)
        l=sum(abs(v) for v in ordinary["left"])
        r=sum(abs(v) for v in ordinary["right"])
        self.assertNotEqual(l,r)
        muted=deepcopy(request)
        muted["tracks"][0]["mute"]=True
        self.assertNotEqual(expected_result(muted)["pcm_sha256"],ordinary["pcm_sha256"])
        solo=deepcopy(request)
        solo["tracks"][1]["solo"]=True
        solo["tracks"][0]["mute"]=False
        self.assertEqual(expected_result(solo)["pcm_sha256"],expected_result(muted)["pcm_sha256"])

    def test_selected_wav_manifest_path(self):
        request=example()
        file=self.root/"clip.wav"
        make_wav(file,request["sources"][0]["pcm"])
        manifest=self.root/"project.json"
        raw={k:deepcopy(v) for k,v in request.items() if k!="sources"}
        raw["schema"]="ab-studio-wav-intake/v1"
        raw["sources"]=[{"id":"a","path":"clip.wav"}]
        manifest.write_text(json.dumps(raw),encoding="utf8")
        data=read_wav_session(manifest)
        self.assertEqual(data,validate_input(request))
        bad=deepcopy(raw)
        bad["sources"][0]["path"]="../missing.wav"
        manifest.write_text(json.dumps(bad),encoding="utf8")
        with self.assertRaises((OSError,ValueError)):
            read_wav_session(manifest)

    def test_cli_uses_real_source_editions_and_independent_job(self):
        request=example()
        sample=self.root/"clip.wav"
        make_wav(sample,request["sources"][0]["pcm"])
        manifest=self.root/"intake.json"
        request2={k:deepcopy(v) for k,v in request.items() if k!="sources"}
        request2["schema"]="ab-studio-wav-intake/v1"
        request2["sources"]=[{"id":"a","path":"clip.wav"}]
        manifest.write_text(json.dumps(request2),encoding="utf8")
        out=self.root/"cli-mix.wav"
        run=subprocess.run([sys.executable,"-m","systems.workspace.studio_bridge",
               "--manifest",str(manifest),"--data-dir",str(self.data),"--version","fresh-001",
               "--copy-source","--execute","--out",str(out)],
              text=True,capture_output=True,timeout=40)
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout)
        self.assertEqual(result["status"],"COMPLETE")
        self.assertTrue(result["witness"]["reverified"])
        self.assertTrue(out.is_file())
        self.assertEqual(StudioSwallowBridge(self.data).runtime.state(result["job"]).status,"COMPLETE")

if __name__=="__main__":
    unittest.main()
