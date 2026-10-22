"""Replay out-of-order board responses through the actual Continuity loader."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "runtime/http/research-board.js"


class ResearchBoardRequestOrderTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is required to replay the async loader")
    def test_old_response_or_error_never_replaces_latest_checkpoint(self):
        js = r'''
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const raw=fs.readFileSync(process.argv[1],"utf8");
const start=raw.indexOf('async function loadBoard(checkpoint = "") {');
const end=raw.indexOf('el("research-checkpoint").addEventListener',start);
assert(start>=0 && end>start);
const renders=[],errors={hidden:true,textContent:""},requests=[];
let clears=0;
const ctx={
  el:id=>{assert.equal(id,"research-error");return errors},
  fetch:path=>new Promise((resolve,reject)=>requests.push({path,resolve,reject})),
  renderBoard:data=>renders.push(data.checkpoint.id),
  clearLanes:()=>{clears++},
  encodeURIComponent
};
vm.createContext(ctx);
vm.runInContext("let boardRequestSerial = 0;\n"+raw.slice(start,end),ctx);
const packet=id=>({ok:true,json:async()=>({available:true,checkpoint:{id}})});
(async()=>{
  const old=ctx.loadBoard("old");
  const latest=ctx.loadBoard("new");
  assert.equal(requests.length,2);
  requests[1].resolve(packet("new"));
  await latest;
  requests[0].resolve(packet("old"));
  await old;
  assert.deepEqual(renders,["new"]);
  assert.equal(clears,0);
  assert.equal(errors.hidden,true);

  const staleError=ctx.loadBoard("old-failing");
  const current=ctx.loadBoard("current");
  requests[3].resolve(packet("current"));
  await current;
  requests[2].reject(new Error("old request failed"));
  await staleError;
  assert.deepEqual(renders,["new","current"]);
  assert.equal(clears,0);
  assert.equal(errors.hidden,true);

  const newestFailure=ctx.loadBoard("latest-failing");
  requests[4].reject(new Error("current source unavailable"));
  await newestFailure;
  assert.equal(clears,1);
  assert.equal(errors.hidden,false);
  assert.equal(errors.textContent,"current source unavailable");
})().catch(error=>{console.error(error);process.exitCode=1});
'''
        result = subprocess.run(
            ["node", "-e", js, str(BOARD)],
            capture_output=True, text=True, timeout=12
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
