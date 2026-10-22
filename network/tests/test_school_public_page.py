"""The public Online School page is a functioning static browser surface with explicit storage boundaries."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
LIVE=ROOT/"docs"/"live"

class PublicSchoolPageTests(unittest.TestCase):
    def test_school_page_is_linked_and_served_from_pages_root(self):
        kids=(LIVE/"kids.html").read_text(encoding="utf-8")
        html=(LIVE/"school.html").read_text(encoding="utf-8")
        css=LIVE/"school.css"
        js=LIVE/"school.js"
        self.assertIn('href="school.html"',kids)
        self.assertIn('href="school.css"',html)
        self.assertIn('src="school.js"',html)
        self.assertTrue(css.is_file())
        self.assertTrue(js.is_file())
        for panel in ("today","practice","reading","science","family"):
            with self.subTest(panel=panel):
                self.assertIn('id="panel-'+panel+'"',html)
                self.assertIn('data-page="'+panel+'"',html)

    def test_browser_app_has_real_actions_and_does_not_claim_server_sync(self):
        html=(LIVE/"school.html").read_text(encoding="utf-8")
        js=(LIVE/"school.js").read_text(encoding="utf-8")
        for contract in ('localStorage.setItem','localStorage.getItem','practice-answer',
                         'reading-note','science-note','actual','export-data','import-data'):
            with self.subTest(contract=contract):
                self.assertIn(contract,js)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('XMLHttpRequest',js)
        self.assertIn('Browser storage is device-specific',html)
        self.assertIn('do not sync with the Python school app',html)
        self.assertIn('Planned minutes (optional)',html)
        self.assertIn('Actual minutes are logged separately',html)

    @unittest.skipUnless(shutil.which("node"),"Node is required for JavaScript syntax verification")
    def test_browser_script_parses(self):
        result=subprocess.run(["node","--check",str(LIVE/"school.js")],
                              capture_output=True,text=True,timeout=12)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=="__main__":
    unittest.main()
