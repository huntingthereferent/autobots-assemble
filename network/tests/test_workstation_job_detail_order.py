"""The most recent selected-run read owns the displayed GitHub job evidence."""
from pathlib import Path
import shutil
import subprocess
import unittest

WORK = Path(__file__).resolve().parents[2] / "docs/live/work.html"


class WorkstationJobDetailOrderTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is needed for source-run detail replay")
    def test_same_run_reselection_cannot_reinsert_old_job_evidence(self):
        js = r'''
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8");
const start=source.indexOf("  let detailRequestSerial=0;");
const end=source.indexOf("  function srcLink(",start);
assert(start>0&&end>start,"Original selectRun source not located");
class Node {
 constructor(tag,txt="",cls=""){
  this.tag=tag;this.textContent=String(txt??"");this.className=cls;
  this.children=[];this.parent=null;this.open=false;
 }
 append(...nodes){for(const node of nodes){if(node instanceof Node){node.parent=this;this.children.push(node)}}}
 replaceChildren(...nodes){for(const node of this.children)node.parent=null;this.children=[];
  this.append(...nodes)}
 remove(){if(this.parent){this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null}}
 scrollIntoView(){}
}
const detail=new Node("div"),panel={open:false};
const nodes={detail,"revision-panel":panel,"revision-scope":new Node("p"),"details-scope":new Node("p")};
const $=key=>{assert(key in nodes,key);return nodes[key]};
const run={id:7,name:"source-run",head:"a".repeat(40),updated:"2026-10-22T19:00:00Z",
 created:"2026-10-22T18:50:00Z",status:"completed",conclusion:"success"};
const app={runs:[run],selection:null,selectedUpdated:null,jobCache:new Map(),
 checked:null,liveAvailable:false,latestPage:[]};
const pending=[];
const ctx={app,$,Date,Number,Set,Math,
 window:{matchMedia:()=>({matches:false})},
 el:(tag,txt,cls)=>new Node(tag,txt,cls),
 pill:text=>new Node("pill",text),statusOf:v=>v.status,
 safeDate:v=>String(v||"none"),plausible:()=>false,
 link:(label)=>new Node("a",label),
 renderRuns:()=>{},loadRevision:()=>{},
 API:"API",
 getJSON:()=>new Promise((resolve,reject)=>pending.push({resolve,reject})),
 jobTimingSummary:()=>null,elapsedBetween:()=>null,
 readableDuration:()=>"",appendStepList:()=>{}
};
vm.createContext(ctx);
vm.runInContext(source.slice(start,end),ctx);
const texts=node=>[node.textContent,...node.children.flatMap(texts)].join(" ");
(async()=>{
 const first=ctx.selectRun(7);
 const current=ctx.selectRun(7);
 assert.equal(pending.length,2);
 pending[1].resolve({jobs:[{id:22,name:"LATEST JOB",status:"completed",steps:[]}]});
 await current;
 pending[0].resolve({jobs:[{id:33,name:"OBSOLETE JOB",status:"completed",steps:[]}]});
 await first;
 assert(texts(detail).includes("LATEST JOB"));
 assert(!texts(detail).includes("OBSOLETE JOB"),"Old selection contaminated current case");
 assert.equal(app.jobCache.get(7).jobs[0].id,22,"Obsolete response poisoned source cache");

 app.jobCache.clear();
 const oldFailure=ctx.selectRun(7);
 const newRead=ctx.selectRun(7);
 pending[3].resolve({jobs:[{id:44,name:"NEW JOB",status:"completed",steps:[]}]});
 await newRead;
 pending[2].reject(new Error("OLD NETWORK FAILURE"));
 await oldFailure;
 assert(!texts(detail).includes("OLD NETWORK FAILURE"));
 assert(texts(detail).includes("NEW JOB"));

 app.jobCache.clear();
 const staleRun=ctx.selectRun(7);
 app.runs=[{...run,updated:"2026-10-22T19:01:00Z"}];
 pending[4].resolve({jobs:[{id:55,name:"OLD REVISION",status:"completed",steps:[]}]});
 await staleRun;
 assert.equal(app.jobCache.has(7),false,"Stale run revision entered current cache");
 assert(!texts(detail).includes("OLD REVISION"));
})().catch(e=>{console.error(e);process.exitCode=1});
'''
        run = subprocess.run(
            ["node", "-e", js, str(WORK)], capture_output=True,
            text=True, timeout=12,
        )
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
