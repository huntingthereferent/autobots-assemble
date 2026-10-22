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


if __name__ == "__main__":
    unittest.main()
