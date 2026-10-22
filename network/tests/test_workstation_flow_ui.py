"""Regression for GitHub-sourced flow counters and the date-scoped run journal."""
from pathlib import Path
import shutil
import subprocess
import unittest

from systems.workspace.research_observatory import ROOT

PAGE = ROOT / "docs/live/work.html"
FLOW = ROOT / "docs/live/workstation-flow.js"
STYLES = ROOT / "docs/live/workstation-flow.css"


class WorkstationFlowTests(unittest.TestCase):
    def test_controls_and_source_provenance(self):
        page = PAGE.read_text(encoding="utf-8")
        flow = FLOW.read_text(encoding="utf-8")
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn('src="workstation-flow.js"', page)
        self.assertIn('href="workstation-flow.css"', page)
        for name in ("queued", "running", "passed", "followups", "failed"):
            self.assertIn(f'data-stat="{name}"', page)
        for period in ("day", "month", "year", "all"):
            self.assertIn(f'data-journal-mode="{period}"', page)
        self.assertIn('id="journal-today"', page)
        self.assertIn("window.WorkstationFlow.matches(r)", page)
        self.assertIn('app.runs.length+" indexed"', page)
        self.assertIn("latestPage", flow)
        self.assertIn("archiveComplete", flow)
        self.assertIn("runs created today", page.lower())
        self.assertIn("not a capacity, speed, or efficiency guarantee", page)
        self.assertIn("prefers-reduced-motion:reduce", css)
        self.assertNotIn("requestAnimationFrame", flow)
        self.assertNotIn("fetch(", flow)

    def test_historical_failures_and_cancellations_are_not_red_kpis(self):
        page=PAGE.read_text(encoding="utf-8")
        flow=FLOW.read_text(encoding="utf-8")
        css=STYLES.read_text(encoding="utf-8")
        self.assertIn("LATER PASSES / INDEX",page)
        self.assertIn("RECORDED OUTCOMES · TODAY",page)
        self.assertNotIn("NOT PASSED / TODAY",page)
        self.assertIn('data-stat="followups"',page)
        self.assertIn('id="cancelled-today"',page)
        self.assertIn('f==="followups"&&app.followups.has(r.id)',page)
        self.assertIn("followingPasses(records)",flow)
        self.assertIn('r.conclusion==="cancelled"',flow)
        self.assertIn(".hist-bar.failed{background:#738b96}",css)
        self.assertIn(".state.later_pass",css)

    @unittest.skipUnless(shutil.which("node"), "Node.js needed to validate journal date handling")
    def test_journal_dates_and_clock_are_not_all_history(self):
        script = r'''
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = {};
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"), {filename:"workstation-flow.js"});
const f = window.WorkstationFlow;
assert.equal(typeof f.matches, "function");
const now = new Date();
const earlier = new Date(now.getFullYear(),now.getMonth(),now.getDate()-1,12);
const today = new Date(now.getFullYear(),now.getMonth(),now.getDate(),12);
assert.equal(f.matches({created: today.toISOString()}), true);
assert.equal(f.matches({created: earlier.toISOString()}), false);
assert.equal(f.matches({created: "not-a-date"}), false);
assert.match(f.scopeLabel(9000,20), /TODAY.*9,000.*20 shown/);
const afternoon = new Date(2026,9,22,17,30);
assert.match(f.clock(afternoon.getTime()), /5:30.*PM/i);
'''
        run = subprocess.run(
            ["node", "-e", script, str(FLOW)],
            text=True, capture_output=True, check=False,
            cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


    @unittest.skipUnless(shutil.which("node"), "Node.js required for matched follow-up source inference")
    def test_later_passes_require_a_newer_same_workflow_and_branch(self):
        script = r'''
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm");
global.window={};vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"));
const f=window.WorkstationFlow.followingPasses;
const at=h=>new Date(2026,9,22,h).toISOString();
const a={id:10,name:"ARC",branch:"main",status:"completed",conclusion:"failure",created:at(9)};
const b={...a,id:11,conclusion:"success",created:at(10)};
const c={...a,id:12,name:"NIH",conclusion:"success",created:at(11)};
const d={...a,id:13,branch:"other",conclusion:"success",created:at(12)};
const e={...a,id:14,conclusion:"cancelled",created:at(8)};
const matched=f([c,a,e,d,b]);
assert.equal(matched.size,1);
assert.equal(matched.get(10).id,11);
assert.equal(matched.has(14),false);
assert.equal(f([a]).size,0);
'''
        run=subprocess.run(["node","-e",script,str(FLOW)],text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js needed for archive/live regression")
    def test_archived_queue_does_not_become_live_and_journal_bins_change(self):
        script = r'''
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
class Element{
 constructor(){this.textContent="";this.children=[];this.style={setProperty(){}};this.className="";this.offsetWidth=1;this.attrs={};this.classList={remove(){},add(){}};this.dataset={};}
 replaceChildren(...xs){this.children=xs;}
 append(...xs){this.children.push(...xs);}
 setAttribute(k,v){this.attrs[k]=v;}
 addEventListener(type,fn){this[type]=fn;}
 closest(){return {querySelector:()=>new Element()};}
}
const byId=new Map(),stats=new Map();
for(const name of ["queued","running","passed","followups","failed"])stats.set(name,new Element());
const modes=["day","month","year","all"].map(mode=>{const e=new Element();e.dataset.journalMode=mode;return e;});
global.document={
 getElementById(id){if(!byId.has(id))byId.set(id,new Element());return byId.get(id);},
 createElement(){return new Element();},
 querySelector(q){return stats.get((q.match(/data-stat="([^"]+)"/)||[])[1]);},
 querySelectorAll(){return modes;}
};
global.window={};
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"));
const flow=window.WorkstationFlow;
const now=Date.now();
const archive={id:1,name:"old still queued",status:"queued",created:new Date(now-4*86400000).toISOString()};
const live={id:2,name:"recent passed",status:"completed",conclusion:"success",created:new Date(now-10000).toISOString()};
flow.render({runs:[archive,live],latestPage:[live],archiveComplete:true,checked:now,liveAvailable:true});
assert.equal(stats.get("queued").textContent,"0"); // archive is historical, not current
assert.equal(byId.get("flow-count-queued").textContent,"0");
flow.render({runs:[archive,live],latestPage:[live],archiveComplete:true,checked:now,liveAvailable:false});
assert.equal(stats.get("queued").textContent,"—"); // refresh failed, fail closed
assert.equal(byId.get("flow-count-queued").textContent,"—");
flow.install(()=>{});
assert.equal(flow.historyBins([live]).bins.length,12); // two-hour day bins
const month=modes.find(x=>x.dataset.journalMode==="month");
month.click();
assert.equal(flow.historyBins([live]).bins.length,new Date(new Date().getFullYear(),new Date().getMonth()+1,0).getDate());
modes.find(x=>x.dataset.journalMode==="year").click();
assert.equal(flow.historyBins([live]).bins.length,12);
modes.find(x=>x.dataset.journalMode==="all").click();
assert.ok(flow.historyBins([live]).bins.length>=1);
'''
        run = subprocess.run(
            ["node", "-e", script, str(FLOW)],
            text=True, capture_output=True, check=False, cwd=ROOT)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
