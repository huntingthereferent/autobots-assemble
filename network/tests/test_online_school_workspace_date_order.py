"""Date-scoped school workspace reads must not overwrite the latest selection."""
from pathlib import Path
import shutil
import subprocess
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "companies/online-school/app/app.js"


class SchoolWorkspaceDateOrderingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required for actual school loader replay")
    def test_latest_day_wins_under_out_of_order_fetches_and_json(self):
        js = r'''
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8");
const begin=source.indexOf("async function load() {");
const end=source.indexOf("async function patchTask(",begin);
assert(begin>=0&&end>begin,"Original loader not found");
const dayInput={value:"2026-10-21"},requests=[],renders=[],modes=[];
const tick=()=>new Promise(resolve=>setImmediate(resolve));
async function expectRequests(n){
 for(let i=0;i<20&&requests.length<n;i++)await tick();
 assert.equal(requests.length,n,"Timed out waiting for request "+n);
}
function deferred(){let resolve,reject;const promise=new Promise((r,j)=>{resolve=r;reject=j});return{promise,resolve,reject}}
function response(body){
 return{ok:true,json:()=>Promise.resolve(body)}
}
const ctx={dayInput,encodeURIComponent,
 fetch:path=>{const d=deferred();requests.push({...d,path});return d.promise;},
 setMode:yes=>modes.push(yes),
 render:()=>{const s=vm.runInContext("({school,state})",ctx);
   renders.push({day:s.school.day,loaded:s.state.day});}
};
vm.createContext(ctx);
vm.runInContext("let school=null,state=null,selectedLearnerId=null,workspaceReadSerial=0;\n"+
 source.slice(begin,end),ctx);
const school=day=>({day,learners:[{id:"student",display_name:"Student"}]});
const state=day=>({day});
(async()=>{
 const old=ctx.load();
 dayInput.value="2026-10-22";
 const latest=ctx.load();
 await expectRequests(2);
 assert(requests[0].path.includes("2026-10-21"));
 assert(requests[1].path.includes("2026-10-22"));
 requests[1].resolve(response(school("2026-10-22")));
 await expectRequests(3);
 requests[2].resolve(response(state("2026-10-22")));
 await latest;
 requests[0].resolve(response(school("2026-10-21")));
 await expectRequests(4);
 requests[3].resolve(response(state("2026-10-21")));
 await old;
 assert.deepEqual(renders,[{day:"2026-10-22",loaded:"2026-10-22"}]);
 assert.equal(vm.runInContext("school.day",ctx),"2026-10-22");

 dayInput.value="2026-10-22";
 const sameDayOld=ctx.load();
 const sameDayNew=ctx.load();
 await expectRequests(6);
 requests[5].resolve(response(school("new same day")));
 await expectRequests(7);
 requests[6].resolve(response(state("new same day")));
 await sameDayNew;
 requests[4].resolve(response(school("old same day")));
 await expectRequests(8);
 requests[7].resolve(response(state("old same day")));
 await sameDayOld;
 assert.equal(renders.at(-1).day,"new same day");
 assert.equal(renders.length,2,"Older same-day request must not re-render");
})().catch(err=>{console.error(err);process.exitCode=1});
'''
        res=subprocess.run(["node","-e",js,str(SOURCE)],
                           capture_output=True,text=True,timeout=12)
        self.assertEqual(res.returncode,0,res.stderr)


if __name__=="__main__":
    unittest.main()
