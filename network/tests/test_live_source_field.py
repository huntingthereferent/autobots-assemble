"""Original evidence and browser program checks for the source-root trace surface."""
from pathlib import Path
from tempfile import TemporaryDirectory
import html.parser
import json
import shutil
import subprocess
import unittest

from views.traces.research_live import ROOT, projection, generate, SCHEMA
from systems.workspace.research_observatory import research_snapshot

PAGE=ROOT/"docs/live/trace.html"


class ScriptParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts=[]
        self.active=False
        self.buf=""
    def handle_starttag(self,tag,attrs):
        if tag=="script":
            self.active=True
            self.buf=""
    def handle_data(self,data):
        if self.active:self.buf+=data
    def handle_endtag(self,tag):
        if tag=="script" and self.active:
            self.scripts.append(self.buf)
            self.active=False


class LiveTraceSourceTests(unittest.TestCase):
    def test_real_workstation_projection_not_fake_execs(self):
        data=projection(research_snapshot())
        self.assertEqual(data["schema"],SCHEMA)
        self.assertGreater(len(data["records"]),5)
        self.assertGreater(len(data["walls"]),1)
        self.assertGreater(len(data["movements"]),1)
        self.assertTrue(any(x["evidence"]=="structured-source-state" for x in data["movements"]))
        self.assertTrue(any(x["evidence"]=="documented-heading-only" for x in data["movements"]))
        self.assertTrue(any(x["path"]=="research/dives/ARC3-TRACE-001/dive.json"
                            and x["state"]=="MOVE_WITH_WALL" for x in data["records"]))
        self.assertTrue(any(x["source_type"]=="CHECKPOINT" and "CP-0030" in x["path"]
                            for x in data["records"]))
        self.assertTrue(any(x["kind"]=="source-recorded-wall" for x in data["walls"]))
        self.assertFalse(any(x["source_type"]=="SYNTHETIC" for x in data["records"]))
        # A source-authored limitation may legitimately say "synthetic" (CP30 key evidence).
        self.assertTrue(any("synthetic" in x["boundary"].lower() for x in data["records"]))

    def test_bad_record_source_rejected(self):
        with self.assertRaises(ValueError):
            projection({"schema":"invented","source_records":[]})

    def test_generation_keeps_original_records(self):
        f=ROOT/"research/dives/ARC3-TRACE-001/dive.json"
        before=f.read_bytes()
        with TemporaryDirectory() as d:
            out=Path(d)/"projection.json"
            actual=generate(out)
            self.assertEqual(json.loads(out.read_text(encoding="utf8")),actual)
        self.assertEqual(before,f.read_bytes())

    def test_owner_ready_cross_run_is_separate_from_historical_w13_wall(self):
        original=ROOT/"research/dives/W13-OWNER-NATIVE-VERIFIER-001/dive.json"
        restored=ROOT/"research/dives/W13-OWNER-READY-CROSS-RUN-001/dive.json"
        old=json.loads(original.read_text(encoding="utf8"))
        new=json.loads(restored.read_text(encoding="utf8"))
        self.assertFalse(old["original_readiness"]["game_worker_ready_owner_run_executed"])
        self.assertTrue(new["native_ready_source"]["game_worker_ready_witnessed"])
        self.assertEqual(new["native_ready_source"]["run_id"],39183388852)
        self.assertEqual(new["separate_run_restoration"]["run_id"],39183832462)
        self.assertTrue(new["separate_run_restoration"]["journal_hashes_unchanged"])
        self.assertEqual(new["separate_run_restoration"]["new_workers_executed"],0)
        self.assertFalse(new["native_ready_source"]["nih_p2_test_witnessed"])
        self.assertFalse(new["encrypted_continuation"]["plaintext_journal_published"])
        index=projection(research_snapshot())
        paths={r["path"] for r in index["records"]}
        self.assertIn("research/dives/W13-OWNER-NATIVE-VERIFIER-001/dive.json",paths)
        self.assertIn("research/dives/W13-OWNER-READY-CROSS-RUN-001/dive.json",paths)

    def test_browser_traces_real_public_git_parent_and_ci_identity(self):
        source=PAGE.read_text(encoding="utf8")
        self.assertIn("GitHub lists the first SHA as an ancestor",source)
        self.assertIn('e.type==="commit-parent"',source)
        self.assertIn('e.type==="ci-head-sha"',source)
        self.assertIn("c.parents.map(p=>p.sha)",source)
        self.assertIn("x.head_sha",source)
        self.assertIn("inSet.has(e.from)",source)
        self.assertIn("requestAnimationFrame",source)
        self.assertIn("refresh()",source)
        self.assertIn('setInterval(()=>{if(!document.hidden)refresh()},FETCH_EVERY)',source)
        self.assertIn("No event assumed",source)
        self.assertIn("SOURCE UNAVAILABLE",source)
        self.assertNotIn("work_state.json",source)
        self.assertNotIn("10 DOMAINS",source)
        self.assertNotIn("15 recorded jobs",source)

    def test_provenance_uses_bounded_source_diagram(self):
        source=PAGE.read_text(encoding="utf8")
        self.assertIn("<h1>Source provenance</h1>",source)
        self.assertIn('<figure class="plot" aria-labelledby="plot-title">',source)
        self.assertIn('<canvas id="field" role="img"',source)
        self.assertIn("Earlier → Later · displayed positions are schematic",source)
        self.assertIn('const drawnRuns=trace.runs.filter(r=>positions.has(r.sha)).slice(0,10)',source)
        self.assertIn('const visible=new Set(points.map(p=>p.id))',source)
        self.assertIn('ctx.setLineDash(ci?[4,4]:[])',source)
        self.assertNotIn("FOLLOW<br>",source)
        self.assertNotIn("position:fixed",source)
        self.assertNotIn("shadowBlur",source)

    @unittest.skipUnless(shutil.which("node"),"Node.js needed for browser syntax lint")
    def test_browser_javascript_is_syntactically_valid(self):
        page=PAGE.read_text(encoding="utf8")
        parser=ScriptParser()
        parser.feed(page)
        self.assertEqual(len(parser.scripts),1)
        with TemporaryDirectory() as d:
            script=Path(d)/"trace-page.js"
            script.write_text(parser.scripts[0],encoding="utf8")
            result=subprocess.run(["node","--check",str(script)],capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
