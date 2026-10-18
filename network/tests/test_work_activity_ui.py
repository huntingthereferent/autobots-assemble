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
        self.assertIn('<h1 id="title">Workstation</h1>',work)
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
        self.assertIn('API+"/actions/runs?per_page=50"',p)
        self.assertIn('"queued","in_progress","waiting","pending","requested"',p)
        self.assertIn("coverage incomplete",p)
        self.assertIn("[...recent,...active]",p)
        self.assertIn('API+"/actions/runs/"+id+"/jobs?per_page=100"',p)
        self.assertIn("Array.isArray(j.workflow_runs)",p)
        self.assertIn("Array.isArray(json.jobs)",p)
        self.assertIn("Array.isArray(j.steps)",p)
        self.assertIn("r.head_sha",p)
        self.assertIn("r.conclusion||null",p)
        self.assertIn("no current status inferred",p.lower())
        self.assertIn("if(!document.hidden)refresh()",p)
        self.assertIn("Select an observed workflow",p)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_active_run_query_paginates_and_keeps_old_work(self):
        import re
        page=WORK.read_text()
        fn=re.search(r"  async function activeRuns\(\)\{.*?\n  \}",page,re.S).group(0)
        script="""
const assert=require('node:assert/strict');
const API='https://example.test';
let queries=[];
function readRuns(data){return data.workflow_runs;}
async function getJSON(url){
  queries.push(url);
  const u=new URL(url),state=u.searchParams.get('status'),page=u.searchParams.get('page');
  return {workflow_runs:state==='in_progress' ? (page==='1' ?
    Array.from({length:100},(_,i)=>({id:i+1})) : [{id:9999}]) : []};
}
"""+fn+"""
(async()=>{
 const runs=await activeRuns();
 assert(runs.some(r=>r.id===9999));
 assert(queries.some(q=>q.includes('page=2')));
 getJSON=async()=>({workflow_runs:Array.from({length:100},()=>({id:1}))});
 await assert.rejects(activeRuns(),/coverage incomplete/);
})().catch(e=>{console.error(e);process.exit(1)});
"""
        subprocess.run(["node","-e",script],check=True,capture_output=True,text=True)

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
