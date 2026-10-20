"""Regression: work means source execution plus research, not an animation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from html.parser import HTMLParser
import shutil
import subprocess
import unittest

from systems.workspace.research_observatory import ROOT
from views.traces.research_live import projection
from systems.workspace.research_observatory import research_snapshot

WORK=ROOT/"docs/live/work.html"
ENTRY=ROOT/"docs/live/index.html"
TRACE=ROOT/"docs/live/trace.html"


class Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts=[]
        self.body=""
        self.open_script=False
    def handle_starttag(self,tag,attrs):
        if tag=="script":
            self.open_script=True
            self.body=""
    def handle_data(self,data):
        if self.open_script:
            self.body+=data
    def handle_endtag(self,tag):
        if tag=="script" and self.open_script:
            self.scripts.append(self.body)
            self.open_script=False


class WorkInvestigationPageTests(unittest.TestCase):
    def test_actual_work_is_public_entry_no_decorative_canvas(self):
        entry=ENTRY.read_text(encoding="utf-8")
        work=WORK.read_text(encoding="utf-8")
        self.assertIn('href="work.html"',entry)
        self.assertIn('url=work.html',entry)
        self.assertIn('<title>Workstation · Hunting the Referent</title>',work)
        self.assertIn('<h1 id="title">Research workstation</h1>',work)
        self.assertIn('<h2>Workflow executions</h2>',work)
        self.assertIn('<h2 id="research-title">Research records</h2>',work)
        self.assertNotIn("What started, what passed, what stopped",work)
        self.assertNotIn('<canvas',work)
        self.assertNotIn("<svg",work)
        self.assertNotIn("particles",work.lower())
        self.assertNotIn("work_state.json",work)
        self.assertIn('href="trace.html"',work)
        self.assertIn("const API=",TRACE.read_text(encoding="utf-8"))

    def test_workflow_status_and_native_steps_need_real_api(self):
        p=WORK.read_text(encoding="utf-8")
        self.assertIn('API+"/actions/runs?per_page=100&page=1"',p)
        self.assertIn('API+"/actions/runs/"+id+"/jobs?per_page=100"',p)
        self.assertIn("Array.isArray(j.workflow_runs)",p)
        self.assertIn("Array.isArray(json.jobs)",p)
        self.assertIn("Array.isArray(j.steps)",p)
        self.assertIn("r.head_sha",p)
        self.assertIn("r.conclusion||null",p)
        self.assertIn("no current status inferred",p.lower())
        self.assertIn("if(!document.hidden&&Date.now()>=app.rateLimitUntil",p)
        self.assertIn("Select an observed workflow",p)

    def test_commit_revision_comparison_requires_exact_source_path(self):
        page=WORK.read_text(encoding="utf-8")
        self.assertIn('API+"/commits/"+r.head+"?per_page=100"',page)
        self.assertIn("doc.sha!==r.head",page)
        self.assertIn("sourceRevisionMatches(files,movements,records)",page)
        self.assertIn('id="revision-evidence"',page)
        self.assertIn("not that the workflow executed the research",page)
        self.assertIn("No research-execution link established",page)

    @unittest.skipUnless(shutil.which("node"),"Node.js needed for exact-path verifier")
    def test_revision_match_rejects_noncausal_and_lookalike_sources(self):
        import re
        page=WORK.read_text(encoding="utf-8")
        fn=re.search(r"  function sourceRevisionMatches\(files,movements,records\)\{.*?\n  \}",page,re.S)
        self.assertIsNotNone(fn,"exact-source-match function must remain separately testable")
        script=fn.group(0)+"""
const assert=require("node:assert/strict");
const files=[
  {filename:"research/dives/ARC3-TRACE-001/dive.json",status:"modified"},
  {filename:"research/dives/ARC3-TRACE-001/dive.json.old",status:"modified"},
  {filename:"research/other.md",status:"removed"},
  {filename:"research/spoof.md",status:"not-an-actual-change"},
  {filename:"README.md",status:"added"},
  {filename:"research/movement.md",status:"renamed"}
];
const movements=[
  {path:"research/movement.md",evidence:"documented-heading-only"},
  {path:"research/dives/ARC3-TRACE-001/dive.json",evidence:"structured-source-state"},
  {path:"research/spoof.md",evidence:"structured-source-state"},
  {path:"research/unrelated.md",evidence:"structured-source-state"}
];
const records=[{path:"research/dives/ARC3-TRACE-001/dive.json"}];
assert.deepEqual(sourceRevisionMatches(files,movements,records),
  ["research/dives/ARC3-TRACE-001/dive.json","research/movement.md"]);
assert.deepEqual(sourceRevisionMatches([{filename:"x",status:"modified"}],movements,records),[]);
assert.deepEqual(sourceRevisionMatches([],movements,records),[]);
"""
        with TemporaryDirectory() as d:
            source=Path(d)/"revision-match.js"
            source.write_text(script,encoding="utf-8")
            proc=subprocess.run(["node",str(source)],capture_output=True,text=True,timeout=15)
        self.assertEqual(proc.returncode,0,proc.stderr)

    @unittest.skipUnless(shutil.which("node"),"Node.js needed for immutable source URL check")
    def test_revision_links_accept_real_research_paths_only(self):
        import re
        page=WORK.read_text(encoding="utf-8")
        fn=re.search(r"  function revisionLink\(path,sha\)\{.*?\n  \}",page,re.S)
        self.assertIsNotNone(fn)
        script=fn.group(0)+"""
const assert=require("node:assert/strict");
const REPO="huntingthereferent/autobots-assemble";
const sha="a".repeat(40);
const isSHA=v=>typeof v==="string"&&/^[0-9a-f]{40}$/.test(v);
const link=(text,href)=>({text,href});
const good=revisionLink("research/dives/ARC3-TRACE-001/dive.json",sha);
assert.equal(good.href,"https://github.com/"+REPO+"/blob/"+sha+"/research/dives/ARC3-TRACE-001/dive.json");
assert.equal(revisionLink("../secret",sha),null);
assert.equal(revisionLink("/absolute",sha),null);
assert.equal(revisionLink("research//bad",sha),null);
assert.equal(revisionLink("research/foo", "invalid-sha"),null);
"""
        with TemporaryDirectory() as d:
            source=Path(d)/"revision-url.js"
            source.write_text(script,encoding="utf-8")
            proc=subprocess.run(["node",str(source)],capture_output=True,text=True,timeout=15)
        self.assertEqual(proc.returncode,0,proc.stderr)

    def test_research_retains_original_boundary_and_next(self):
        v=projection(research_snapshot())
        arc=next(x for x in v["records"] if x["source_type"]=="RESEARCH_DIVE")
        self.assertEqual(arc["state"],"MOVE_WITH_WALL")
        self.assertIn("next",arc)
        self.assertIn("boundary",arc)
        cp=next(x for x in v["records"] if "CP-0030" in x["path"])
        self.assertTrue(cp["next"])
        self.assertTrue(cp["boundary"])
        self.assertTrue(any(x["kind"]=="source-recorded-wall" for x in v["walls"]))
        self.assertGreater(len(v["movements"]),0)
        self.assertTrue(any(x["evidence"]=="documented-heading-only" for x in v["movements"]))


    def test_workflow_catalog_and_paginated_history_are_observed_not_fabricated(self):
        p=WORK.read_text(encoding="utf-8")
        self.assertIn('id="workflow-catalog"',p)
        self.assertIn('id="workflow-filter"',p)
        self.assertIn('id="history-chart"',p)
        self.assertIn('id="load-older"',p)
        self.assertIn('API+"/actions/workflows?per_page=100"',p)
        self.assertIn('API+"/actions/runs?per_page=100&page="+page',p)
        self.assertIn("if(runs.length<100||!runs.length)app.olderExhausted=true",p)
        self.assertIn("app.runs=[...previous.values()].sort",p)
        self.assertIn("Bars summarize the currently retrieved pages only",p)
        self.assertIn("not automatically an active worker",p)
        self.assertNotIn('API+"/actions/runs?per_page=50"',p)

    def test_tickstream_only_triggers_original_source_refresh(self):
        p=WORK.read_text(encoding="utf-8")
        self.assertIn('id="tick-form"',p)
        self.assertIn('id="tick-status"',p)
        self.assertIn("new EventSource(safe,{withCredentials:false})",p)
        self.assertIn('connection.addEventListener("tick",onServerTick)',p)
        self.assertIn("app.streamTicks++",p)
        self.assertIn("if(parsed.protocol!==\"https:\"",p)
        self.assertIn("parsed.username||parsed.password||parsed.search||parsed.hash",p)
        self.assertIn("TICK_REFRESH_GAP",p)
        self.assertIn("app.rateLimitUntil=Date.now()+15*60*1000",p)
        self.assertIn("app.lastAttempt=Date.now()",p)
        self.assertIn("A server event is a prompt to recheck original evidence, never a worker result.",p)
        self.assertIn("GitHub auto-check continues",p)
        self.assertIn("no current status inferred",p.lower())


    def test_research_workbench_limits_dom_and_preserves_complete_source_index(self):
        page=WORK.read_text(encoding="utf-8")
        self.assertIn('id="run-search"',page)
        self.assertIn('id="show-more-runs"',page)
        self.assertIn('id="workflow-search"',page)
        self.assertIn('id="show-more-workflows"',page)
        self.assertIn('id="load-more-workflows"',page)
        self.assertIn('id="show-more-records"',page)
        self.assertIn('id="show-more-movements"',page)
        self.assertIn('id="show-more-walls"',page)
        self.assertIn('id="history-panel"',page)
        self.assertIn('id="revision-panel"',page)
        self.assertIn("subset.slice(0,app.runVisible)",page)
        self.assertIn("sorted.slice(0,app.catalogVisible)",page)
        self.assertIn("items.slice(0,app.recordVisible)",page)
        self.assertIn("matching.slice(0,app.movementVisible)",page)
        self.assertIn("walls.slice(0,app.wallVisible)",page)
        self.assertIn("app.catalogNextPage++",page)
        self.assertIn('API+"/actions/workflows?per_page=100&page="+app.catalogNextPage',page)
        self.assertNotIn('id="workflow-registry" open',page)
        self.assertNotIn('class="pane movement-panel" open',page)
        self.assertIn("document heading",page.lower())

    def test_selection_retains_verified_jobs_and_defers_expensive_commit_reads(self):
        page=WORK.read_text(encoding="utf-8")
        self.assertIn('if($("revision-panel").open)loadRevision(r)',page)
        self.assertIn('app.selectedUpdated=r.updated',page)
        self.assertIn('app.selectedUpdated!==selected.updated',page)
        self.assertIn('id="detail"',page)
        self.assertIn('details",undefined,"job-section"',page)
        self.assertIn("Array.isArray(json.jobs)",page)
        self.assertIn("No research-execution link established",page)

    @unittest.skipUnless(shutil.which("node"),"Node.js needed for syntax check")
    def test_inline_program_valid_javascript(self):
        p=Extract()
        p.feed(WORK.read_text(encoding="utf-8"))
        self.assertEqual(len(p.scripts),1)
        with TemporaryDirectory() as d:
            file=Path(d)/"work.js"
            file.write_text(p.scripts[0],encoding="utf-8")
            result=subprocess.run(["node","--check",str(file)],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
