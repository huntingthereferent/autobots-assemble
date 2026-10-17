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
        self.assertIn('Work · Original investigation',work)
        self.assertIn("What's happening in work?",work)
        self.assertNotIn('<canvas',work)
        self.assertNotIn("<svg",work)
        self.assertNotIn("particles",work.lower())
        self.assertNotIn("work_state.json",work)
        self.assertIn('href="trace.html"',work)
        self.assertIn("const API=",TRACE.read_text(encoding="utf-8"))

    def test_workflow_status_and_native_steps_need_real_api(self):
        p=WORK.read_text(encoding="utf-8")
        self.assertIn('API+"/actions/runs?per_page=50"',p)
        self.assertIn('API+"/actions/runs/"+id+"/jobs?per_page=100"',p)
        self.assertIn("Array.isArray(j.workflow_runs)",p)
        self.assertIn("Array.isArray(json.jobs)",p)
        self.assertIn("Array.isArray(j.steps)",p)
        self.assertIn("r.head_sha",p)
        self.assertIn("r.conclusion||null",p)
        self.assertIn("no current status inferred",p.lower())
        self.assertIn("if(!document.hidden)refresh()",p)
        self.assertIn("Select an observed workflow",p)

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
