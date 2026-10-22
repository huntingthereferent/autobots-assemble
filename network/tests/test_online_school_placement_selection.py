"""A learner's placement questions cannot be displayed or submitted as another learner."""
from pathlib import Path
import shutil
import subprocess
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "companies/online-school/app/app.js"


class SchoolPlacementSelectionTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required for actual placement loader replay")
    def test_learner_and_request_identity_survive_out_of_order_responses(self):
        js = r'''
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8");
const begin=source.indexOf("async function openPlacement(subject) {");
const end=source.indexOf('$("#focus-start-test").onclick',begin);
assert(begin>0&&end>begin,"Exact placement loader unavailable");
const submitBegin=source.indexOf('placementForm.addEventListener("submit"',end);
const submitEnd=source.indexOf("function openObservation()",submitBegin);
assert(submitBegin>end&&submitEnd>submitBegin,"Placement submit handler unavailable");
const pending=[],titles={title:{},intro:{}},items={children:[],replaceChildren(...a){this.children=a},append(x){this.children.push(x)}};
let selected="A",shown=0,submitted=0;
class Element {
 constructor(){this.nodes={};this.className="";this.name="";this.textContent="";}
 set innerHTML(v){this.html=v;}
 querySelector(q){return this.nodes[q]??(this.nodes[q]=new Element());}
}
const placementForm={dataset:{},handlers:{},addEventListener(k,fn){this.handlers[k]=fn}};
const placementDialog={showModal(){shown++},close(){}};
const placementError={hidden:true,textContent:""};
const ctx={
  person:()=>({id:selected}), placementForm,placementDialog,placementError,
  $:id=>id==="#placement-title"?titles.title:id==="#placement-intro"?titles.intro:id==="#placement-items"?items:null,
  document:{createElement:()=>new Element()},
  fetch:url=>{const row={url};pending.push(row);return new Promise(resolve=>{row.resolve=resolve})},
  alert:msg=>{throw new Error("Unexpected user-visible alert: "+msg)},
  encodeURIComponent,FormData:()=>{throw Error("Should never reach FormData after learner mismatch")},
  load:async()=>{}, console,Promise,JSON
};
vm.createContext(ctx);
vm.runInContext("let placementReadSerial=0;\n"+source.slice(begin,end),ctx);
vm.runInContext(source.slice(submitBegin,submitEnd),ctx);
const response=(id,subject,title)=>({ok:true,json:async()=>({sections:[{subject,title,prompts:[id+" question"]}]})});
(async()=>{
 const older=ctx.openPlacement("reading");
 assert.equal(pending.length,1);
 assert(pending[0].url.endsWith("learner=A"));
 selected="B";
 vm.runInContext("placementReadSerial++",ctx);
 pending[0].resolve(response("A","reading","A QUESTIONS"));
 await older;
 assert.equal(shown,0,"Prior learner must not open a new dialog");

 const oldB=ctx.openPlacement("reading");
 const latestB=ctx.openPlacement("science");
 assert.equal(pending.length,3);
 pending[2].resolve(response("B","science","LATEST B QUESTIONS"));
 await latestB;
 pending[1].resolve(response("B","reading","OLD B QUESTIONS"));
 await oldB;
 assert.equal(shown,1);
 assert.equal(titles.title.textContent,"LATEST B QUESTIONS");
 assert.equal(placementForm.dataset.subject,"science");
 assert.equal(placementForm.dataset.learnerId,"B");

 const canceled=ctx.openPlacement("science");
 vm.runInContext("placementReadSerial++",ctx);
 pending[3].resolve(response("B","science","CANCELLED QUESTIONS"));
 await canceled;
 assert.equal(shown,1,"Closed dialog must not reopen after stale response");

 selected="A";
 await placementForm.handlers.submit({preventDefault(){}});
 assert.equal(submitted,0);
 assert.equal(placementError.hidden,false);
 assert(placementError.textContent.includes("Reopen the questions"));
 assert.equal(placementForm.dataset.learnerId,"B",
   "A different selected learner must not change the form's source identity");
})().catch(e=>{console.error(e);process.exitCode=1});
'''
        p = subprocess.run(["node", "-e", js, str(SOURCE)],
                           capture_output=True, text=True, timeout=12)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_selection_and_close_handlers_invalidate_pending_placement(self):
        s = SOURCE.read_text(encoding="utf-8")
        self.assertIn('selectedLearnerId = item.id;\n      placementReadSerial++;', s)
        self.assertEqual(s.count('selectedLearnerId = item.id;\n      placementReadSerial++;'), 2)
        self.assertIn('$("#close-placement").onclick = () => {\n  placementReadSerial++;', s)


if __name__ == "__main__":
    unittest.main()
