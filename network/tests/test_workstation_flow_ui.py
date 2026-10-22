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
        for name in ("queued", "running", "passed", "failed"):
            self.assertIn(f'data-stat="{name}"', page)
        for period in ("day", "month", "year", "all"):
            self.assertIn(f'data-journal-mode="{period}"', page)
        self.assertIn('id="journal-today"', page)
        self.assertIn("window.WorkstationFlow.matches(r)", page)
        self.assertIn('app.runs.length+" indexed"', page)
        self.assertIn("latestPage", flow)
        self.assertIn("liveTotals", flow)
        self.assertIn("status=in_progress&per_page=100", page)
        self.assertIn("status=queued&per_page=100", page)
        self.assertIn("archiveComplete", flow)
        self.assertIn("runs created today", page.lower())
        self.assertIn("not a capacity, speed, or efficiency guarantee", page)
        self.assertIn("prefers-reduced-motion:reduce", css)
        self.assertNotIn("requestAnimationFrame", flow)
        self.assertNotIn("fetch(", flow)

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
for(const name of ["queued","running","passed","failed"])stats.set(name,new Element());
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
flow.render({runs:[archive,live],latestPage:[live],liveActive:[],
             liveTotals:{running:0,queued:0},archiveComplete:true,checked:now,liveAvailable:true});
assert.equal(stats.get("queued").textContent,"0"); // archive is historical, not current
assert.equal(byId.get("flow-count-queued").textContent,"0");
const active={id:3,name:"older active PR",status:"in_progress",created:new Date(now-86400000).toISOString()};
flow.render({runs:[archive,live],latestPage:[live],liveActive:[active],
             liveTotals:{running:20,queued:31},archiveComplete:true,checked:now,liveAvailable:true});
assert.equal(stats.get("queued").textContent,"31"); // server total, no queued ID in latest page
assert.equal(stats.get("running").textContent,"20"); // server total, not one visible active ID
assert.equal(byId.get("flow-count-queued").textContent,"31");
assert.equal(byId.get("flow-count-running").textContent,"20");
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
