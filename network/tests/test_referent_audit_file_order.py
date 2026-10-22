"""Source-pinned audit: only the latest selected-file read may update the case view."""
from pathlib import Path
import shutil
import subprocess
import unittest

PAGE = Path(__file__).resolve().parents[2] / "docs/live/audit.html"


class SourceFileSelectionOrderTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required to replay file selection")
    def test_latest_file_read_wins_even_if_paths_match(self):
        js = r'''
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const html=fs.readFileSync(process.argv[1],"utf8");
const start=html.indexOf("  async function openFile(path){");
const end=html.indexOf("  function advance(step)",start);
assert(start>0 && end>start);
const state={
 selected:"",cases:[],source:"",position:0,head:"a".repeat(40),mode:"tests"
};
const pending=[],renders=[];
const sourcePanel={
 children:[], replaceChildren(...items){this.children=items}
};
const position={textContent:""};
const ctx={
 state,
 $:id=>id==="case-source"?sourcePanel:position,
 elem:(tag,value)=>({tag,value}),
 renderFiles:()=>{},
 sourceText:()=>new Promise((resolve,reject)=>pending.push({resolve,reject})),
 parseCases:text=>[{name:text}],
 parseData:text=>[{name:text}],
 renderCase:()=>renders.push(state.source)
};
vm.createContext(ctx);
vm.runInContext("let fileReadSerial=0;\n"+html.slice(start,end),ctx);
(async()=>{
 const path="network/tests/test_observations.py";
 const first=ctx.openFile(path);
 const latest=ctx.openFile(path);
 assert.equal(pending.length,2);
 pending[1].resolve("LATEST TEST DEFINITION");
 await latest;
 pending[0].resolve("OUTDATED TEST DEFINITION");
 await first;
 assert.equal(state.source,"LATEST TEST DEFINITION");
 assert.deepEqual(renders,["LATEST TEST DEFINITION"]);

 const obsoleteError=ctx.openFile(path);
 const valid=ctx.openFile(path);
 pending[3].resolve("LATEST SOURCE AFTER FAILURE");
 await valid;
 pending[2].reject(new Error("Old fetch failed"));
 await obsoleteError;
 assert.equal(state.source,"LATEST SOURCE AFTER FAILURE");
 assert.deepEqual(renders,["LATEST TEST DEFINITION","LATEST SOURCE AFTER FAILURE"]);
 assert.equal(sourcePanel.children[0]?.value,"Reading exact source at aaaaaaaaaaaa…");

 const wrongMode=ctx.openFile(path);
 state.mode="data";
 pending[4].resolve("OLDER MODE");
 await wrongMode;
 assert.equal(state.source,"");
})().catch(err=>{console.error(err);process.exitCode=1});
'''
        result = subprocess.run(
            ["node", "-e", js, str(PAGE)],
            capture_output=True, text=True, timeout=12
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
