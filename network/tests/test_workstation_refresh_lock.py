"""Replay source reads through the workstation refresh handler, not mock implementation."""
import shutil
import subprocess
import unittest
from pathlib import Path

WORK = Path(__file__).resolve().parents[2] / "docs/live/work.html"


class WorkstationRefreshLockTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required for workstation JS replay")
    def test_run_and_research_reads_share_a_single_refresh_lock(self):
        js = r'''
const fs=require("node:fs"), vm=require("node:vm"), assert=require("node:assert/strict");
const src=fs.readFileSync(process.argv[1],"utf8");
const start=src.indexOf("  async function refresh(){");
const end=src.indexOf('  $("check-now").addEventListener',start);
assert(start>=0 && end>start,"Source refresh handler missing");
const nodes=Object.fromEntries([
 "workstation-main","check-now","live-dot","feed-state","last-read","feed-error","runs"
].map(n=>[n,{hidden:false,disabled:false,className:"",textContent:"",replaceChildren(){}}]));
const $=id=>nodes[id]||{hidden:false,textContent:""};
const app={reading:false,runs:[],selection:null,selectedUpdated:null,
 checked:null,latestPage:[],liveAvailable:false,rateLimitUntil:0,
 lastAttempt:0,nextPage:2,archiveComplete:true,reportedTotal:null};
const sample={id:12,name:"fixture",updated:"2026-10-22T16:00:00Z"};
let runCalls=0, projected=[],errors=[];
const ctx={
 app,$,
 API:"https://example.invalid", Date, Number, Error,
 getJSON:async()=>{runCalls++;return {total_count:1,workflow_runs:[sample]};},
 readRuns:d=>d.workflow_runs,
 mergeRuns:r=>{app.runs=r},
 renderHistory:()=>{},renderRuns:()=>{},updateNextCheck:()=>{},
 selectRun:async()=>{},
 loadResearch:()=>new Promise((resolve,reject)=>projected.push({resolve,reject})),
 renderMetrics:()=>{},
 el:()=>({}),
};
vm.createContext(ctx);
vm.runInContext(src.slice(start,end),ctx);
const turn=()=>new Promise(resolve=>setImmediate(resolve));
async function until(count){
 for(let i=0;i<20&&projected.length<count;i++)await turn();
 assert.equal(projected.length,count,"Awaiting research source read");
}
(async()=>{
 const first=ctx.refresh();
 await until(1);
 assert.equal(runCalls,1);
 assert.equal(app.reading,true,"Source lock must include pending research read");
 assert.equal(nodes["check-now"].disabled,true);
 await ctx.refresh();
 assert.equal(runCalls,1,"Overlapping source fetch must not start");
 projected[0].resolve();
 await first;
 assert.equal(app.reading,false);
 assert.equal(nodes["check-now"].disabled,false);

 const second=ctx.refresh();
 await until(2);
 assert.equal(runCalls,2,"A later completed source read is allowed");
 assert.equal(app.reading,true);
 projected[1].resolve();
 await second;
 assert.equal(app.reading,false);

 const failedResearch=ctx.refresh();
 await until(3);
 projected[2].reject(new Error("Unexpected research rejection"));
 await assert.rejects(failedResearch,/Unexpected research rejection/);
 assert.equal(app.reading,false,"Finally releases source lock on errors");
 assert.equal(nodes["check-now"].disabled,false);
})().catch(err=>{console.error(err);process.exitCode=1});
'''
        done = subprocess.run(["node", "-e", js, str(WORK)],
                              text=True, capture_output=True, timeout=12)
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
