"""Source-pinned project audit: inspect individual tests, not live execution telemetry."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
PAGE=ROOT/"docs/live/audit.html"
WORK=ROOT/"docs/live/work.html"
DOC=ROOT/"docs/live/README.md"

class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__();self.scripts=[];self.active=False
    def handle_starttag(self,tag,attrs):
        if tag=="script":self.active=True;self.scripts.append("")
    def handle_data(self,data):
        if self.active:self.scripts[-1]+=data
    def handle_endtag(self,tag):
        if tag=="script":self.active=False

def source_script():
    parser=ScriptCollector();parser.feed(PAGE.read_text(encoding="utf-8"))
    assert len(parser.scripts)==1,"one auditable inline source program expected"
    return parser.scripts[0]

class SourceTestAuditUITests(unittest.TestCase):
    def test_entry_remains_in_workstation(self):
        page=PAGE.read_text(encoding="utf-8")
        host=WORK.read_text(encoding="utf-8")
        self.assertIn("<title>Referent audit · Hunting the Referent</title>",page)
        for element in ('id="referents"','id="test-files"','id="case-source"','id="research"','id="export"'):
            self.assertIn(element,page)
        self.assertIn('data-src="audit.html?embedded=1"',host)
        self.assertIn('href="#audit"',host)
        self.assertIn('event.origin!==location.origin',host)
        self.assertIn('event.source!==auditFrame.contentWindow',host)
        self.assertIn("window.parent.postMessage({type:'referent-audit:resize',height",page)
        self.assertIn('[Referent audit](work.html#audit)',DOC.read_text(encoding="utf-8"))

    def test_not_a_live_monitor_or_counter_dashboard(self):
        js=source_script();page=PAGE.read_text(encoding="utf-8")
        for forbidden in ('/actions/runs','setInterval(','new EventSource','run-count','metric-runs','live monitoring dashboard'):
            self.assertNotIn(forbidden,js)
        self.assertNotIn('id="metric-runs"',page)
        self.assertIn('not live monitoring',page.lower())
        self.assertIn("API+'/git/trees/'+sha+'?recursive=1'",js)
        self.assertIn("API+'/branches/main'",js)
        self.assertIn("state.head+':'+path",js)
        self.assertIn("const r=await fetch(url,{cache:'no-store'})",js)

    def test_no_invented_test_execution(self):
        js=source_script();page=PAGE.read_text(encoding="utf-8")
        for required in ("function parseCases(text)", "function openFile(path)", "function advance(step)",
                         "function renderCase()", "sourceURL(path,c.line)", "line:i+j+1",
                         "not a witnessed pass", "function exportReviews()","source_commit:state.head",
                         "statement:'Human assessments of test source; no test execution"):
            self.assertIn(required,js)
        self.assertIn("Dynamic tests and tests using other naming conventions may be missing.",page)
        self.assertIn("Source declarations are not execution results.",page)
        self.assertIn("state.reviews.set(key",js)
        self.assertNotIn(".innerHTML",js)
        self.assertNotIn("eval(",js)

    @unittest.skipUnless(shutil.which("node"),"Node.js required")
    def test_source_script_parses(self):
        with TemporaryDirectory() as d:
            path=Path(d)/"audit.js";path.write_text(source_script(),encoding="utf-8")
            run=subprocess.run(["node","--check",str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)

    @unittest.skipUnless(shutil.which("node"),"Node.js required")
    def test_test_cases_recover_actual_source_lines(self):
        js=source_script()
        functions=js[js.index("  function projectForPath(path)"):js.index("  const state=")]
        parsing=js[js.index("  function parseCases(text)"):js.index("  function selectedFiles()")]
        fixture=r"""
const assert=require('node:assert/strict');
const src=[
'class Verification(unittest.TestCase):',
'    def test_small(self):',
'        self.assertEqual(2+2,4)',
'    def test_bound(self):',
'        assert 7 > 2',
'',
'def test_external():',
'    with pytest.raises(ValueError):',
'        raise ValueError()',
].join('\n');
const cases=parseCases(src);
assert.equal(cases.length,3);
assert.deepEqual(cases.map(c=>c.name),['Verification.test_small','Verification.test_bound','test_external']);
assert.deepEqual(cases.map(c=>c.line),[2,4,7]);
assert.deepEqual(cases.map(c=>c.checks[0].line),[3,5,8]);
assert.equal(projectForPath('network/tests/test_arc3_sp80_stage3.py'),'arc');
assert.equal(projectForPath('network/tests/test_ab_world_trial16.py'),'world');
assert.equal(projectForPath('network/tests/test_nih_p2_ontology.py'),'nih');
assert.equal(projectForPath('network/tests/test_workstation_http.py'),'workstation');
assert.equal(projectForPath('network/tests/test_ab_information.py'),'ab');
assert.equal(projectForPath('network/tests/test_ambiguous.py'),'other');
assert.equal(isTestPath('network/tests/test_examples.py'),true);
assert.equal(isTestPath('README.md'),false);
"""
        with TemporaryDirectory() as d:
            path=Path(d)/"case-inspection.js";path.write_text(functions+parsing+fixture,encoding="utf-8")
            run=subprocess.run(["node",str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)

if __name__=="__main__":
    unittest.main()
