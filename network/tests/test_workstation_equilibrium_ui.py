"""The Workstation equilibrium watch must use successful source observations only."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

from systems.workspace.research_observatory import ROOT

WORK = ROOT / "docs/live/work.html"
SCRIPT = ROOT / "docs/live/workstation-equilibrium.js"
STYLE = ROOT / "docs/live/workstation-equilibrium.css"


class EquilibriumObserverTests(unittest.TestCase):
    def test_page_wires_observer_without_dispatch(self):
        html = WORK.read_text(encoding="utf-8")
        js = SCRIPT.read_text(encoding="utf-8")
        css = STYLE.read_text(encoding="utf-8")
        self.assertIn('src="workstation-equilibrium.js"', html)
        self.assertIn('href="workstation-equilibrium.css"', html)
        self.assertIn('window.WorkstationEquilibrium?.sample(', html)
        for field in ("eq-state", "eq-avg-running", "eq-peak-running",
                      "eq-avg-waiting", "eq-queue-drift", "eq-in", "eq-out"):
            self.assertIn(f'id="{field}"', html)
        self.assertIn("snapshot.latestPage", js)
        self.assertIn("snapshot.checked", js)
        self.assertIn("previous=known", js)
        self.assertIn("STEADY CANDIDATE", js)
        self.assertIn("No confirmed concurrency cap", js)
        self.assertIn("prefers-reduced-motion:reduce", css)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("setInterval(", js)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_observer_counts_transitions_not_page_refreshes(self):
        runner = r'''
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
class Node {
  constructor(){this.textContent="";this.children=[];this.style={};this.className="";this.title="";}
  append(...x){this.children.push(...x);}
  replaceChildren(...x){this.children=x;}
}
const nodes=new Map();
global.document={
 getElementById(id){if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);},
 createElement(){return new Node();}
};
global.window={};
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"));
const a=window.WorkstationEquilibrium;
const start=Date.now()-14*60000;
const when=n=>new Date(start+n*60000).toISOString();
const queued={id:1,name:"A",status:"queued",created:when(0)};
a.sample({checked:start,latestPage:[queued]});
a.sample({checked:start,latestPage:[queued]}); // duplicate must not count
assert.equal(nodes.get("eq-samples").textContent.startsWith("1 checks"),true);
const running={...queued,status:"in_progress"};
a.sample({checked:start+120000,latestPage:[running]});
a.sample({checked:start+240000,latestPage:[{...running,status:"completed",conclusion:"success"}]});
assert.equal(nodes.get("eq-peak-running").textContent,"1");
assert.equal(nodes.get("eq-queue-drift").textContent,"-1");
assert.equal(nodes.get("eq-samples").textContent.startsWith("3 checks"),true);
assert.ok(nodes.get("eq-out").textContent.includes("/h"));
assert.equal(nodes.get("equilibrium-graph").children.length,3);
'''
        result = subprocess.run(
            ["node", "-e", runner, str(SCRIPT)], cwd=ROOT,
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_zero_flow_with_waiting_jobs_is_not_steady(self):
        runner = r'''
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
class Element {
 constructor(){this.textContent="";this.children=[];this.style={};this.className="";this.title="";}
 append(...xs){this.children.push(...xs);}
 replaceChildren(...xs){this.children=xs;}
}
const elements=new Map();
global.document={
 getElementById(id){if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},
 createElement(){return new Element();}
};
global.window={};
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"));
const begin=Date.now()-12*60000;
const waiting=[{id:1,name:"stalled A",status:"queued",created:new Date(begin-3600000).toISOString()},
               {id:2,name:"stalled B",status:"queued",created:new Date(begin-3600000).toISOString()}];
for(let i=0;i<6;i++)
  window.WorkstationEquilibrium.sample({checked:begin+i*120000,latestPage:waiting});
assert.equal(elements.get("eq-state").textContent,"STALLED BACKLOG");
assert.equal(elements.get("eq-in").textContent,"0/h");
assert.equal(elements.get("eq-out").textContent,"0/h");
assert.equal(elements.get("eq-queue-drift").textContent,"0");
assert.ok(!/steady/i.test(elements.get("eq-state").textContent));
'''
        result = subprocess.run(
            ["node", "-e", runner, str(SCRIPT)], cwd=ROOT,
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
