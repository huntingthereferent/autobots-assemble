"""Student home v2 uses real learner/task data for the progress meter."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2] / "companies/online-school/app"


class StudentHomeUpgradeTests(unittest.TestCase):
    def test_connected_tools_and_accessible_progress(self):
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        js=(ROOT/"app.js").read_text(encoding="utf-8")
        css=(ROOT/"school-refresh.css").read_text(encoding="utf-8")
        for path in ("practice.html","family.html","reading.html","science.html"):
            self.assertIn(path,html)
        self.assertIn("school-refresh.css",html)
        self.assertIn('id="reading-link"',html)
        self.assertIn('$("#reading-link").href',js)
        self.assertIn('id="science-link"',html)
        self.assertIn('$("#science-link").href',js)
        self.assertIn('role="progressbar"',html)
        self.assertIn('id="progress-fill"',html)
        self.assertIn('id="progress-value"',html)
        self.assertIn('own.filter(x => x.status !== "done")',js)
        self.assertIn('$("#progress-fill").style.width = percentage + "%"',js)
        self.assertIn('$("#progress-bar").setAttribute("aria-valuenow"',js)
        self.assertIn("prefers-reduced-motion",css)
        self.assertNotIn("Math.floor(Math.random()",js)

    @unittest.skipUnless(shutil.which("node"),"Node required for browser script syntax checks")
    def test_all_student_javascript_parses(self):
        for name in ("app.js", "practice.js", "family.js"):
            # Other lanes publish companion files before Home is integrated;
            # validate this branch's existing app.js without assuming their merge order.
            if not (ROOT/name).is_file():
                continue
            result=subprocess.run(["node","--check",str(ROOT/name)],
                                  capture_output=True,text=True,timeout=12)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__ == "__main__":
    unittest.main()
