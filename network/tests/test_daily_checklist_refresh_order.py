"""A delayed checklist poll must not replace a newer observed task state."""
from pathlib import Path
import shutil
import subprocess
import unittest

PAGE = Path(__file__).resolve().parents[2] / "runtime/http/daily-checklist.html"


class DailyChecklistRefreshTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node needed for live refresh-function replay")
    def test_newest_success_and_mutation_boundary_take_precedence(self):
        js = r'''
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const html=fs.readFileSync(process.argv[1],"utf8");
const start=html.indexOf("async function refresh(){");
const end=html.indexOf('$("#daily-form").addEventListener',start);
assert(start>=0 && end>start);
const stats={textContent:""},form={hidden:false},error={hidden:false};
const list={children:[],replaceChildren(...items){this.children=items},append(x){this.children.push(x)}};
const controls={"#daily-stats":stats,"#daily-list":list,"#daily-form":form,"#daily-error":error};
const pending=[];
const context={
  $:id=>controls[id],
  api:()=>new Promise((resolve,reject)=>pending.push({resolve,reject})),
  row:task=>({id:task.id}),
  document:{createElement:tag=>({tag,textContent:""})},
  alertError:err=>{error.hidden=false;error.textContent=err.message}
};
vm.createContext(context);
vm.runInContext("let refreshSerial=0,pendingMutations=0;\n"+html.slice(start,end),context);
const state=(id)=>({pending:1,checked_today:0,local_date:"2026-10-22",items:[{id}]});
(async()=>{
 const first=context.refresh();
 const latest=context.refresh();
 assert.equal(pending.length,2);
 pending[1].resolve(state("new"));
 await latest;
 pending[0].resolve(state("old"));
 await first;
 assert.equal(list.children[0].id,"new");

 vm.runInContext("pendingMutations++",context);
 const quiet=context.refresh();
 await quiet;
 assert.equal(pending.length,2,"No poll should start during a mutation");
 vm.runInContext("pendingMutations--; refreshSerial++",context);

 const beforeWrite=context.refresh();
 assert.equal(pending.length,3);
 vm.runInContext("pendingMutations++; refreshSerial++",context);
 pending[2].resolve(state("older-than-write"));
 await beforeWrite;
 assert.equal(list.children[0].id,"new","A read started before the write must be ignored");
 vm.runInContext("pendingMutations--",context);
 const afterWrite=context.refresh();
 pending[3].resolve(state("after-write"));
 await afterWrite;
 assert.equal(list.children[0].id,"after-write");

 const oldFailure=context.refresh();
 const current=context.refresh();
 pending[5].resolve(state("latest-ok"));
 await current;
 pending[4].reject(new Error("late network error"));
 await oldFailure;
 assert.equal(list.children[0].id,"latest-ok");
 assert.equal(form.hidden,false);
 assert.equal(error.hidden,true);
})().catch(err=>{console.error(err);process.exitCode=1});
'''
        run = subprocess.run(["node", "-e", js, str(PAGE)],
                             capture_output=True, text=True, timeout=12)
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_mutation_guards_are_present_on_add_and_check(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn("pendingMutations++;refreshSerial++;", html)
        self.assertEqual(html.count("pendingMutations++;refreshSerial++;"), 2)
        self.assertEqual(html.count("if(!pendingMutations)await refresh();"), 2)


if __name__ == "__main__":
    unittest.main()
