"""Keep the combined-source execution strip real, scoped, and independent of the old Meta tab."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs/live/work.html"
SOURCE = ROOT / "docs/live/workstation-combined.js"
LANDING = ROOT / "docs/live/index.html"


class CombinedWorkstationViewerTests(unittest.TestCase):
    def test_single_execution_entry_and_verified_source_readers(self):
        html = PAGE.read_text(encoding="utf-8")
        js = SOURCE.read_text(encoding="utf-8")
        landing = LANDING.read_text(encoding="utf-8")
        self.assertNotIn('href="meta.html"', html)
        self.assertFalse((ROOT / "docs/live/meta.html").exists())
        self.assertFalse((ROOT / "docs/live/meta-work-parity.css").exists())
        self.assertIn('"dashboard": "https://huntingthereferent.github.io/autobots-assemble/live/work.html"',
                      (ROOT / "docs/live/meta-registry.json").read_text(encoding="utf-8"))
        self.assertIn('src="workstation-combined.js"', html)
        self.assertIn("window.WorkstationCombined.start()", html)
        for element in ("combined-status", "combined-running", "combined-waiting",
                        "combined-passed", "combined-review", "combined-source-note",
                        "combined-daily-note", "combined-review-note", "combined-routing",
                        "combined-issues"):
            self.assertEqual(html.count('id="' + element + '"'), 1)
        for source in ("meta-registry.json", "history.json", "daily.json",
                       "health.json", "routing.json"):
            self.assertIn(source, js)
        self.assertIn('content="0;url=work.html"', landing)
        self.assertNotIn('content="0;url=meta.html"', landing)
        self.assertIn("unknown is not zero", js)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for the source-validation regression")
    def test_paired_validity_partial_missing_and_stale_are_not_zero(self):
        script = r"""
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
global.window={};
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"),{filename:"workstation-combined.js"});
const summarize=window.WorkstationCombined.summarize;
const now=Date.UTC(2026,9,22,21,0,0);
const checked=new Date(now-300000).toISOString();
const repoA="huntingthereferent/autobots-assemble";
const repoB="aeren-research/continuum-oscillator";
const registry={schema:"meta-workstation/registry-v1",nodes:[{id:"A",repo:repoA},{id:"B",repo:repoB}]};
const sources={
 A:{repo:repoA,observed:true,in_progress:6,queued:2,pending:0,waiting:1},
 B:{repo:repoB,observed:true,in_progress:3,queued:0,pending:1,waiting:0}
};
const history={schema:"ab-meta-observations/v1",samples:[{ts:checked,nodes:sources}]};
const daily={schema:"meta-workstation/daily-runs-v1",all_sources:true,timezone:"America/Chicago",
  local_date:"2026-10-22",observed_at:checked,nodes:sources,totals:{success:135}};
const health={schema:"meta-workstation/current-workflow-health-v1",all_sources:true,
  observed_at:checked,nodes:sources,summary:{open_count:1,open:[
    {repo:repoA,name:"actual failed workflow",run_id:1234}
  ]}};
const routing={schema:"meta-workstation/routing-advice-v1",generated_at:checked,signal:"NO_CLEAR_PRESSURE"};
const good=summarize(registry,history,daily,health,routing,now);
assert.equal(good.running,9);
assert.equal(good.waiting,4);
assert.equal(good.successful,135);
assert.equal(good.review,1);
assert.equal(good.issues[0].run_id,1234);
assert.equal(good.status,"SOURCE OBSERVED");
const stale={...history,samples:[{ts:new Date(now-91*60000).toISOString(),nodes:sources}]};
const partial=summarize(registry,stale,daily,null,null,now);
assert.equal(partial.running,null);
assert.equal(partial.waiting,null);
assert.equal(partial.successful,135);
assert.equal(partial.review,null);
assert.equal(partial.status,"PARTIAL SOURCE");
const incomplete=summarize(registry,history,{...daily,all_sources:false},null,null,now);
assert.equal(incomplete.successful,null);
const changed={...registry,nodes:[registry.nodes[0],{id:"B",repo:"another/repository"}]};
const mismatched=summarize(changed,history,daily,health,routing,now);
assert.equal(mismatched.running,null);
assert.equal(mismatched.successful,null);
assert.equal(mismatched.review,null);
assert.throws(()=>summarize({schema:"wrong",nodes:[]},history,daily,health,routing,now));
"""
        p = subprocess.run(["node", "-e", script, str(SOURCE)], capture_output=True,
                           text=True, cwd=ROOT, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
