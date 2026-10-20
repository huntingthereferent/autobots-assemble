"""Referent audit regression: no inferred execution or globally flattened source states."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs/live/audit.html"
WORK = ROOT / "docs/live/work.html"
TRACE = ROOT / "docs/live/trace.html"
DOC = ROOT / "docs/live/README.md"


class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.scripts = []

    def handle_starttag(self, name, attrs):
        if name == "script":
            self.in_script = True
            self.scripts.append("")

    def handle_data(self, value):
        if self.in_script:
            self.scripts[-1] += value

    def handle_endtag(self, name):
        if name == "script":
            self.in_script = False


def source_script():
    collector = ScriptCollector()
    collector.feed(PAGE.read_text(encoding="utf-8"))
    assert len(collector.scripts) == 1, "one auditable inline program expected"
    return collector.scripts[0]


class ReferentAuditUITests(unittest.TestCase):
    def test_project_referent_is_the_root_and_workstation_links_to_it(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("<title>Referent audit · Hunting the Referent</title>", page)
        self.assertIn('id="referents"', page)
        self.assertIn('id="runs"', page)
        self.assertIn('id="next"', page)
        self.assertIn('id="research"', page)
        self.assertIn('href="audit.html"', WORK.read_text(encoding="utf-8"))
        self.assertIn('href="audit.html"', TRACE.read_text(encoding="utf-8"))
        self.assertIn('[Referent audit](audit.html)', DOC.read_text(encoding="utf-8"))

    def test_live_evidence_and_historical_research_are_separate(self):
        js = source_script()
        self.assertIn("API+'/actions/runs?per_page=100&page=1'", js)
        self.assertIn("API+'/actions/runs/'+run.id+'/jobs?per_page=100'", js)
        self.assertIn("API+'/commits/'+run.head_sha+'?per_page=100'", js)
        self.assertIn("API+'/pulls?state=open&per_page=100'", js)
        self.assertIn("views/traces/research-live.json", js)
        self.assertIn("Array.isArray(data.jobs)", js)
        self.assertIn("Array.isArray(results[2].value.records)", js)
        self.assertIn("app.jobs.delete(r.id)", js)
        self.assertIn("app.rateLimitUntil", js)
        self.assertIn("x.path", js)
        self.assertIn("r.next", js)
        self.assertIn("m.line", js)
        self.assertIn("w.line", js)
        self.assertIn("no matching runs in the fetched history window".lower(),
                      PAGE.read_text(encoding="utf-8").lower())
        self.assertIn("not a claim the workflow executed", js.lower())
        self.assertNotIn("Math.random(", js)
        self.assertNotIn("canvas", PAGE.read_text(encoding="utf-8").lower())

    @unittest.skipUnless(shutil.which("node"), "Node.js required for browser script parsing")
    def test_browser_js_parses(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "audit.js"
            f.write_text(source_script(), encoding="utf-8")
            run = subprocess.run(["node", "--check", str(f)],
                                 text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for namespace ownership test")
    def test_referent_path_and_branch_rules_do_not_conflate_world48_and_arc(self):
        script = source_script()
        section = script[script.index("  const RULES=["):script.index("  function family(")]
        assertions = r"""
const assert = require('node:assert/strict');
assert.equal(referent('.github/workflows/arc3-window48-native-composites.yml'), 'world48');
assert.equal(referent('.github/workflows/arc3-sp80-action4-saturation.yml'), 'arc-run');
assert.equal(referent('research/dives/ARC3-TRACE-001/dive.json'), 'arc-run');
assert.equal(referent('research/dives/W13-NATIVE-RECEIPT-001/dive.json'), 'w13');
assert.equal(referent('.github/workflows/nih-p2-source-variation.yml'), 'nih');
assert.equal(referent('.github/workflows/ab-relational-cluster.yml'), 'ab');
assert.equal(referent('.github/workflows/tests.yml'), 'unassigned');
assert.equal(referent('', 'experiment/arc-sp80-stage2'), 'arc-run');
assert.equal(prReferent({title:'WORLD Trial 13: controlled evidence',head:{ref:'misc/unlisted'}}), 'world');
assert.equal(prReferent({title:'A surprising turn',head:{ref:'misc/unlisted'}}), 'unassigned');
"""
        with TemporaryDirectory() as d:
            f = Path(d) / "namespaces.js"
            f.write_text(section + assertions, encoding="utf-8")
            run = subprocess.run(["node", str(f)], text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
