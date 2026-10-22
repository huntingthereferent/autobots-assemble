"""Source provenance polling must not overlap or infer unobserved movement."""
from pathlib import Path
import shutil
import subprocess
import unittest

PAGE = Path(__file__).resolve().parents[2] / "docs/live/trace.html"


class TraceRefreshOrderingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node needed for source refresh replay")
    def test_overlapping_poll_or_refresh_does_not_overtake_source_observation(self):
        js=r'''
const fs=require("node:fs"),vm=require("node:vm");
const assert=require("node:assert/strict");
const page=fs.readFileSync(process.argv[1],"utf8");
const start=page.indexOf("  let refreshing=false;\n  async function refresh(){");
const end=page.indexOf('  $("refresh").addEventListener',start);
assert(start>=0&&end>start,"Missing exact source refresh handler");
const nodes={refresh:{disabled:false},freshness:{textContent:""},"status-text":{textContent:""},"research-stamp":{textContent:""}};
const requests=[],notifications=[],rendered=[];
const state={commits:[],runs:[],edges:[],last:0};
const ctx={
  $:id=>nodes[id],
  API:"api",RAW:"research",state,
  json:url=>new Promise((resolve,reject)=>requests.push({url,resolve,reject})),
  parseCommits:input=>input,
  parseRuns:input=>input,
  edges:(c,r)=>c.map(x=>({id:x.id})),
  setRoots:()=>{},renderTrail:()=>rendered.push(state.commits.map(x=>x.id).join(",")),
  setStatus:(kind,msg)=>notifications.push({kind,msg}),
  uiResearch:()=>notifications.push({kind:"research",msg:"source read"}),
  Date,Math,Promise,Set,Error
};
vm.createContext(ctx);
vm.runInContext(page.slice(start,end),ctx);
(async()=>{
 const first=ctx.refresh(),overlap=ctx.refresh();
 assert.equal(requests.length,2,"Only one pair of source reads may run");
 assert.equal(nodes.refresh.disabled,true);
 requests[1].resolve([{id:1,status:"completed"}]);
 requests[0].resolve([{id:"old-source"}]);
 await Promise.resolve();await Promise.resolve();
 assert.equal(requests.length,3,"Research projection request follows source snapshot");
 const blocked=ctx.refresh();
 assert.equal(requests.length,3,"Refresh button must remain guarded through research projection");
 requests[2].resolve({records:[]});
 await Promise.all([first,overlap,blocked]);
 assert.deepEqual(rendered,["old-source"]);
 assert.equal(nodes.refresh.disabled,false);
 const next=ctx.refresh();
 assert.equal(requests.length,5,"Next observation is permitted after completion");
 requests[3].resolve([{id:"latest-source"}]);
 requests[4].resolve([]);
 await Promise.resolve();await Promise.resolve();
 assert.equal(requests.length,6);
 requests[5].resolve({records:[]});
 await next;
 assert.deepEqual(rendered,["old-source","latest-source"]);
 assert.equal(nodes.refresh.disabled,false);
 const failed=ctx.refresh();
 requests[6].reject(new Error("network down"));
 requests[7].resolve([]);
 await Promise.resolve();await Promise.resolve();
 requests[8].resolve({});
 await failed;
 assert.equal(nodes.refresh.disabled,false);
 assert.deepEqual(rendered,["old-source","latest-source"],"No invented commits after an error");
 assert(nodes.freshness.textContent.includes("NO NEW EVIDENCE"));
})().catch(e=>{console.error(e);process.exitCode=1});
'''
        r=subprocess.run(["node","-e",js,str(PAGE)],capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,0,r.stderr)


if __name__=="__main__":
    unittest.main()
