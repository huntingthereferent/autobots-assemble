"""Learner profile source selections must remain bound to their own responses."""
from pathlib import Path
import shutil
import subprocess
import unittest

PAGE = Path(__file__).resolve().parents[2] / "companies/online-school/app/profile.js"


class LearnerProfileOrderTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node needed to replay actual learner loader")
    def test_out_of_order_record_response_and_safe_error_message(self):
        js=r'''
const fs=require("node:fs"),vm=require("node:vm");
const assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8");
const begin=source.indexOf("async function loadRecord(learnerId){");
const end=source.indexOf("function renderStandards()",begin);
assert(begin>0 && end>begin);
const select={value:"a"},requests=[],rendered=[];
let ctx;
ctx={
  $:key=>{assert.equal(key,"#learner-select");return select},
  encodeURIComponent,
  fetch:url=>new Promise((resolve,reject)=>requests.push({url,resolve,reject})),
  render:()=>{const data=vm.runInContext("({record,comparison})",ctx);
    rendered.push({person:data.record.learner.id,grade:data.comparison.grade_context})}
};
vm.createContext(ctx);
vm.runInContext("let record=null,comparison=null,recordReadSerial=0;\n"+
 source.slice(begin,end),ctx);
const good=payload=>({ok:true,json:async()=>payload});
(async()=>{
 const old=ctx.loadRecord("a");
 select.value="b";
 const latest=ctx.loadRecord("b");
 assert.equal(requests.length,2);
 requests[1].resolve(good({learner:{id:"b"}}));
 await Promise.resolve();await Promise.resolve();
 assert.equal(requests.length,3);
 requests[2].resolve(good({grade_context:"B grade"}));
 await latest;
 requests[0].resolve(good({learner:{id:"a"}}));
 await Promise.resolve();await Promise.resolve();
 assert.equal(requests.length,4);
 requests[3].resolve(good({grade_context:"A grade"}));
 await old;
 assert.deepEqual(rendered,[{person:"b",grade:"B grade"}]);
 const selection=vm.runInContext("({record,comparison})",ctx);
 assert.equal(selection.record.learner.id,"b");
 assert.equal(selection.comparison.grade_context,"B grade");

 const stale=ctx.loadRecord("old");
 select.value="c";
 const current=ctx.loadRecord("c");
 assert.equal(requests.length,6);
 requests[5].resolve(good({learner:{id:"c"}}));
 await Promise.resolve();await Promise.resolve();
 requests[6].resolve(good({grade_context:"C grade"}));
 await current;
 requests[4].reject(new Error("Late old learner error"));
 await stale;
 assert.equal(rendered.at(-1).person,"c");
 assert.equal(rendered.length,2);

 let message=null;
 const body={set innerHTML(_){throw Error("Unsafe error HTML")},
   replaceChildren(node){message=node}};
 const doc={body,createElement:tag=>({tag,style:{},textContent:""})};
 const errCtx={document:doc,loadLearners:()=>Promise.reject(new Error("<img src=x onerror=alert(1)>"))};
 vm.createContext(errCtx);
 const start=source.lastIndexOf("loadLearners().catch(err=>");
 assert(start>0);
 vm.runInContext(source.slice(start),errCtx);
 await Promise.resolve();await Promise.resolve();
 assert.equal(message.tag,"p");
 assert.equal(message.textContent,"<img src=x onerror=alert(1)>");
 assert.equal(message.style.padding,"24px");
})().catch(err=>{console.error(err);process.exitCode=1});
'''
        result=subprocess.run(["node","-e",js,str(PAGE)],
                              capture_output=True,text=True,timeout=12)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
